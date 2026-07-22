<!--
question:
  id: 11.ai-knowledge-ingestion-pipeline
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: RAG 工程
  tags: [11.ai, Knowledge Ingestion, Connectors, PDF, OCR, Deduplication, CDC, Vector Database]
-->

# 知识入库流水线面试深挖（4 大核心）

> ⬅️ [返回 AI 咬文嚼字](../README.md) | [主模块深度专题](../../../11.ai/02-technology-stack/knowledge-ingestion-pipeline/README.md)

> **一句话定位**：**4 大核心知识入库面试深挖**：多源连接 / 复杂文档解析 / 去重与 CDC / 亿级 Chunk 性能。

---

## 🎯 4 大核心题

### Q1：企业知识库接入 10+ 数据源，怎么选连接器？

**陷阱**：
- ❌ 每个数据源都自己写爬虫（重复造轮子）
- ❌ 不区分文档类、协作类、代码类和数据类

**30 秒话术**：
> "3 大连接器生态：**LlamaHub（200+ connector）/ Airbyte（300+ source）/ Unstructured（多格式）**。**原则：能不写就不写，能配置就别写代码**；只有专有认证、复杂 ACL 或特殊版本语义无法由生态覆盖时，才写 Custom Connector。"

**90 秒话术**：
> "先按数据源类型分流，再决定工具，而不是为每个站点复制一份爬虫：
>
> - **文档类**（PDF/DOCX/PPTX/MD/HTML）→ Unstructured.io / Docling，重点保留版面、表格、页码和附件关系。
> - **协作类**（Confluence/Notion/Slack/邮件）→ LlamaHub + Airbyte，重点捕获线程、评论、空间权限、编辑历史和删除语义。
> - **代码类**（GitHub/GitLab Issue/PR/Discussion）→ GitHub REST/GraphQL API + LlamaIndex GithubRepoReader，重点保留仓库、分支、commit 和关联关系。
> - **数据库类**（MySQL/PostgreSQL CDC / S3 / Kafka）→ Debezium CDC / S3 Event Notification / Kafka Consumer，重点处理事务边界、游标、offset 和 schema 演进。
>
> **反模式**：① 写独立爬虫→维护成本 10x；② 所有内容塞同一字段→检索粗、ACL 难过滤；③ 不存 raw + parsed 双版本→失败难复盘、解析器升级无法重放。生产连接器还要统一 `source_uri`、稳定 `object_id`、`source_version`、`updated_at`、ACL 和 checkpoint，并在原始对象落盘后再推进游标。"

---

### Q2：解析 PDF / 复杂文档的 5 个雷区是什么？表格、OCR、图片怎么处理？

**陷阱**：
- ❌ 全部用 PyPDF（表格、公式和阅读顺序可能全丢）
- ❌ 不区分扫描件和文本 PDF

**30 秒话术**：
> "5 大雷区：① 表格 → Docling/Unstructured（PyPDF 容易丢失结构）② 扫描件 → OCR（Tesseract/PaddleOCR）③ 公式/图表 → Mathpix API / 多模态 LLM ④ 嵌套布局 → 用 layout-aware 解析 ⑤ 编码乱码 → chardet/charset-normalizer。**企业级首选 Docling（IBM 开源，layout + table + OCR 全有）**，但要用真实语料抽样验证，而不是只看能否抽出文字。"

**90 秒话术**：
> "5 个雷区要分别治理：
>
> - **表格解析**：PyPDF 把单元格按坐标拼成错位文本，表头和跨列关系会丢；必须用 Docling 或 Unstructured，Excel 则直接用 pandas，并同时保留表格 Markdown 与单元格 JSON。
> - **OCR**：多页扫描件没有文本层，必须走 Tesseract / PaddleOCR（中文场景通常更友好）/ Docling 内置 OCR；记录页级置信度，金额和编号低置信度时进人工复核。
> - **公式与图表**：公式用 Mathpix API 或多模态 LLM 转 LaTeX/MathML，同时保留原图；图表可用 GPT-4V 等视觉模型生成描述，但不能替代原图引用。
> - **嵌套布局**：双栏、页眉页脚、目录和脚注不能靠正则硬拼；使用 layout-aware 解析识别层级，再针对模板清洗页眉页脚。
> - **编码乱码**：先用 chardet + charset-normalizer 探测和修复 UTF-8/GBK 混杂、非法字节与 mojibake，再生成 content hash。
>
> **企业级最佳实践**：① Docling 统一解析并记录 parser version ② 保留 raw + parsed 双版本 ③ 表格/图片单独存（不直接混进普通 Chunk），通过 metadata 引用 ④ OCR 采用异步任务并设置低置信度复核队列。解析产物还应保留 page、坐标、标题层级、阅读顺序和原文映射，便于回放和引用。"

---

### Q3：去重策略与 CDC 增量同步怎么设计？

**陷阱**：
- ❌ 只按 URL 去重（同一文档的不同格式、镜像和附件会重复）
- ❌ 增量同步靠人工触发，没有 checkpoint、版本和删除语义

**30 秒话术**：
> "采用**3 层去重**：URL/稳定 ID 精确去重 → 内容 hash（SHA-256 + MinHash/SimHash）→ 向量近似（embedding 距离 < 0.05，阈值需按语料标定）。**CDC 增量 3 模式**：拉（poll）/ 推（webhook）/ 流（Kafka + Debezium）。**关键**：依据 source 的 `updated_at` 与 `source_version` 触发重 hash；hash 未变就不重做解析和 Embedding，ACL 变化则只更新过滤元数据。"

**90 秒话术**：
> "去重要分层、分粒度，并且不能破坏血缘：
>
> - **第 1 层：URL/稳定 ID 精确去重**（DB 主键）→ 防重复抓取；URL 变化时仍以源系统稳定 object ID 和 source version 为准。
> - **第 2 层：内容 hash 去重**（规范化全文的 SHA-256，近重复再用 SimHash 64-bit/MinHash）→ 识别跨源复制和少量改写。
> - **第 3 层：向量近似去重**（候选集合的 L2 距离 < 0.05）→ 识别改写后的同义段落，成本最高，只做最后确认；法律条款阈值必须谨慎标定。
>
> **CDC 增量 3 模式**：
>
> | 模式 | 适用 | 实现 |
> |------|------|------|
> | 拉（poll） | 文档类 / 内部 wiki | 每天定时拉 `updated_at > last_sync`，时间窗口重叠后幂等去重 |
> | 推（webhook） | Confluence / GitHub | 验签后先落事件表，再实时推送；定期全量对账防漏推 |
> | 流（CDC） | 数据库 / Kafka | Debezium 监听 binlog，Kafka 按 `doc_id` 分区并记录 offset |
>
> **软删除 vs 硬删除**：推荐软删除（`is_deleted = true` 或墓碑），保留审计与恢复能力；硬删除仅在 GDPR 等删除权要求下执行，并清理向量、文本、缓存和对象存储副本。**实战**：① source 保留 `updated_at` + `version` ② 增量请求带 If-Modified-Since/ETag ③ 抽样 5% 对比前后 embedding 是否漂移 ④ 事件含 `event_id` 并按版本比较，避免乱序覆盖。"

---

### Q4：亿级 Chunk 入库，性能瓶颈在哪里，怎么选型？

**陷阱**：
- ❌ 单条 insert 同步循环（慢 100x）
- ❌ 不分批写入（容易 OOM，也无法控制失败重试）

**30 秒话术**：
> "**3 大瓶颈**：① 同步写入 → bulk + async ② 单线程 → 并发 worker ③ Embedding 单点 → 批量 + 异步池。**实战**：百万 Chunk 同步串行 12 小时 → async 批量约 25 分钟；上线前仍要用真实数据校准吞吐、限流和成本。"

**90 秒话术**：
> "优化要把解析、Embedding、写入拆成可背压的流水线：
>
> - **① Bulk Insert**：向量库按 1000–10000 条一批 bulk，吞吐可提升 10–50x；每批有 manifest，失败可幂等重放。
> - **② 异步写入**：Kafka / RabbitMQ 解耦解析、Embedding、写入三阶段，用队列长度控制背压。
> - **③ Embedding 批量**：`batch_size=64`（按模型和显存压测）利用 GPU，单 token 成本可降 5–10x；使用 vLLM/TGI 等推理服务并限制并发。
> - **④ 并发流水线**：Celery/Ray/Dask 多 worker 分布式处理，按 token 数而不是文档数分批，避免大文件拖慢整个批次。
> - **⑤ 重试 + DLQ**：限流和 5xx 使用 exponential backoff + jitter；认证、维度不匹配、内容超限快速失败进入 DLQ。
>
> **亿级 Chunk 实战选型**：
>
> | 数据规模 | 架构 |
> |---------|------|
> | < 100 万 | 单机 + `bulk_insert` |
> | 100 万 - 1000 万 | Celery + 批量 + 月增量 |
> | > 1000 万 | Kafka + Flink + Milvus 集群 / Pinecone Serverless |
>
> **监控指标**：入库 QPS / 失败率 / Embedding 显存 / 队列长度 / 端到端 `trace_id`。同时监控 freshness lag、DLQ 数量和写后读可见性；向量模型升级时用新 collection 或新字段双写，禁止把不同向量空间原地混写。"

---

## 🔗 兄弟章节

- **主模块深度**：[企业级 Knowledge Ingestion Pipeline](../../../11.ai/02-technology-stack/knowledge-ingestion-pipeline/README.md) — 8 阶段全链路：连接、解析、清洗、分块、Embedding、入库与 CDC。
- **兄弟面试题**：[长文档与 PDF 面试深挖](../long-document-pdf/README.md) — 分块、Lost-in-Middle、上下文扩展与长合同 Pipeline。
- **餐厅叙事**：[12.story 36 — RAG 检索增强生成](../../../12.story/36-rag-retrieval-augmented-generation.md) — 用阿明餐厅串起 RAG 的入库、检索与回答全流程。

---

## 📊 4 题难度速查表

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 多源连接器 | ⭐⭐⭐⭐ | 高频 | 3 大生态 / 4 类数据源 / 10+ 源 |
| Q2 复杂文档解析 | ⭐⭐⭐⭐⭐ | 高频 | 5 大雷区 / raw + parsed / OCR |
| Q3 去重与 CDC | ⭐⭐⭐⭐⭐ | 高频 | 3 层去重 / 3 种 CDC / 5% 抽样 |
| Q4 亿级 Chunk 性能 | ⭐⭐⭐⭐⭐ | 高频 | 5 大优化 / 1000–10000 批量 / 10–50x |

---

## 📚 参考来源

1. [LlamaIndex 官方文档：Loading Data](https://docs.llamaindex.ai/en/stable/module_guides/loading/) — LlamaHub、数据加载器与 Ingestion Pipeline。
2. [Unstructured.io 官方文档](https://docs.unstructured.io/) — 多格式文档 partition、表格与 OCR 处理。
3. [阿里云 Lindorm：Pipeline 自动 Embedding](https://help.aliyun.com/document_detail/2873214.html) — 向量写入、查询与 Pipeline 工程实践。
4. [Debezium 官方文档：Change Data Capture](https://debezium.io/documentation/reference/stable/) — binlog CDC、事件、事务边界与增量同步。
5. [Final-State-Press/enterprise-knowledge-base](https://github.com/Final-State-Press/enterprise-knowledge-base) — 企业知识系统的结构化与工程化参考。

---

← 返回 [AI 咬文嚼字](../README.md)