# 10.big-data 中度重构 — 设计 Spec

> 日期：2026-06-26
> 模式：B 中度重构（仿 09.front-end 模式）
> 基础：10.big-data-analysis.md（Explore agent 调研）

---

## 1. 背景与动机

`note/10.big-data/` 当前是「微型版」的 09.front-end 前重构态：

| 指标 | 当前 |
|---|---|
| 总 .md 文件 | 3（顶层 1 + 子 2） |
| 总行数 | 365 |
| 顶层 README | 31 行宏观综述，**无模块导航** |
| 子 README | 2 个，风格截然不同（叙事+图示 vs 百科+表格） |
| PNG | 6 张（命名无语义，无 alt 文本） |
| mermaid | 0 个 |
| `- [ ] 待完善` placeholder | 17 个（占 open-source/ 大量子主题） |

**5 大 gap：**
1. 顶层 README 缺模块导航/速查表（gap 1）
2. open-source/ 17 个 placeholder 空洞（gap 2）
3. 0 个 mermaid（Lambda/Kappa 等天然适合 flowchart）（gap 3）
4. 6 张 PNG 命名无语义（gap 4）
5. 缺统一 emoji 章节模板（gap 5）

**为什么 B 不 A：** A 只精修不解决 gap 1（缺导航）根因。
**为什么 B 不 C：** 10 原始只有 365 行，C 方案 7+ 子 README + 17 placeholder 全填 = 4000+ 行，过度。

---

## 2. 最终目录结构

```
note/10.big-data/
├── README.md                          (顶层 350-400 行，11 节)
├── 01-data-warehouse/                 (现有 offline-or-real-time 改造，80 行索引)
├── 02-hadoop-ecosystem/               (新增子 README 200-300 行)
├── 03-realtime-compute/               (现有 open-source 改造，80 行索引)
├── 04-data-lake/                      (新增 200-300 行)
├── 05-olap/                           (新增 200-300 行)
├── 06-scheduling/                     (新增 200-300 行)
├── 07-data-governance/                (新增 200-300 行)
└── 08-sync-tools/                     (新增 200-300 行，从 open-source/ 拆出)
```

**注：** 删除 09-bigdata-and-ai 模块（避免与 11.ai 重叠；如需可在 future spec 加入）。

**子 README 总数：1 顶层 + 8 子模块 + 6 新子 README = 15 个文件**

---

## 3. 顶层 README 结构（11 节，350-400 行）

### 3.1 11 节结构（仿 09）

| # | 节名 | 行数预算 |
|---|------|---------|
| 1 | 9 模块导航 | 80（表格 + 简介块 + 选型指南） |
| 2 | 知识脉络 | 1 mermaid |
| 3 | 速查地图（12 表） | 160 |
| 4 | 选型决策树 | 4 mermaid |
| 5 | 学习路线 | 30 |
| 6 | 交叉引用 | 20 |
| 7 | 开源参考 | 20 |
| 8 | 数据时效性 | 15 |
| 9 | 章节统计 | 10 |
| 10 | 变更记录 | 5 |
| 11 | 术语表 | 30 |
| 总计 | | 350-400 |

### 3.2 9 模块导航表（章节 1）

```markdown
| 序号 | 主题 | 核心内容 | 子 README | 学习价值 |
|------|------|---------|-----------|---------|
| 01 | 数仓架构 | Lambda/Kappa/湖仓一体/批流融合 | 01-data-warehouse/ | 架构选型根因 |
| 02 | Hadoop 生态 | HDFS/YARN/Hive/Presto | 02-hadoop-ecosystem/ | 离线数仓基石 |
| 03 | 实时计算 | Flink/Spark Streaming/Storm | 03-realtime-compute/ | 毫秒-秒级延迟 |
| 04 | 数据湖 | Iceberg/Hudi/Delta Lake | 04-data-lake/ | 存算分离新范式 |
| 05 | OLAP | Doris/ClickHouse/StarRocks | 05-olap/ | 亚秒级查询 |
| 06 | 调度 | Airflow/DolphinScheduler | 06-scheduling/ | 任务编排 |
| 07 | 数据治理 | Atlas/DataHub/数据血缘 | 07-data-governance/ | 元数据/质量/安全 |
| 08 | 同步工具 | DataX/SeaTunnel/Sqoop | 08-sync-tools/ | 异构数据集成 |
```

### 3.3 12 张速查表（章节 3）

| 表 | 内容 |
|---|------|
| 3.1 | 架构对比（Lambda/Kappa/湖仓一体） |
| 3.2 | 计算引擎对比（Flink/Spark/Storm/Beam） |
| 3.3 | 存储格式对比（Parquet/ORC/Avro） |
| 3.4 | 数据湖对比（Iceberg/Hudi/Delta） |
| 3.5 | OLAP 对比（Doris/ClickHouse/StarRocks/Presto） |
| 3.6 | 调度对比（Airflow/DolphinScheduler/Azkaban） |
| 3.7 | 同步对比（DataX/SeaTunnel/Sqoop/Flume） |
| 3.8 | 治理对比（Atlas/DataHub/Piper） |
| 3.9 | 资源管理对比（YARN/K8s/Mesos） |
| 3.10 | 大数据生态版本（2026 H1） |
| 3.11 | 学习路径（按角色） |
| 3.12 | 工具速查（Hive SQL / Spark SQL / Flink SQL 区别） |

---

## 4. 子模块 README 模板（7 节，50-80 行）

仿 09 子模块索引模板：

```markdown
# 0X 模块名

> 一句话定位

---

## 1. 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| ... | ✓ 已有 | [xxx/] |
| ... | 📝 新增 (T9) | 顶层速查 |

## 2. 速查要点

- ...

## 3. 选型建议

```mermaid
flowchart TD
    ...
```

## 4. 与其他模块的关系

- **上游**：
- **下游**：
- **横向**：

## 5. 学习建议

- ...

## 6. 数据时效性

- ...

## 7. 关键术语

| 术语 | 解释 |
|------|------|
| ... | ... |
```

---

## 5. 6 个新子 README 内容简介（200-300 行）

每个新子 README 用 9 节深读模板（仿 08.deep-dive 模式）：

### 5.1 02-hadoop-ecosystem/

**一句话定位：** Hadoop 三件套（HDFS/YARN/MapReduce）+ 上层引擎（Hive/Presto/Impala）

**核心覆盖：**
- HDFS 架构（NameNode/DataNode/副本机制）
- YARN 资源调度（Capacity/Fair Scheduler）
- Hive 架构与执行引擎（MR/Tez/Spark）
- Presto/Trino 分布式 SQL
- 版本演进（Hadoop 2 → 3 → Ozone/Submarine）

**典型场景：**
- 离线数仓 T+1 报表
- 历史数据归档
- 大规模批量 ETL

### 5.2 04-data-lake/

**一句话定位：** 数据湖三种表格式（Iceberg/Hudi/Delta Lake）+ 存算分离

**核心覆盖：**
- Iceberg / Hudi / Delta Lake 三种表格式对比
- 存算分离架构（MinIO/S3 + 计算引擎）
- ACID / Time Travel / Schema Evolution
- 查询引擎集成（Spark/Flink/Trino）

**典型场景：**
- AI/ML 训练数据湖
- 流批一体数据存储
- 跨云数据共享

### 5.3 05-olap/

**一句话定位：** 实时 OLAP 引擎（Doris/ClickHouse/StarRocks/Presto）

**核心覆盖：**
- Doris 架构（Frontend/Backend/Broker）
- ClickHouse MergeTree 引擎家族
- StarRocks CBO 优化器
- Presto/Trino 联邦查询

**典型场景：**
- 实时大屏
- 交互式分析
- 用户行为分析

### 5.4 06-scheduling/

**一句话定位：** 大数据调度系统（Airflow/DolphinScheduler/Azkaban）

**核心覆盖：**
- DAG 模型 vs 传统 Cron
- Airflow 2.x 架构（Scheduler/Executor/Webserver）
- DolphinScheduler 海豚调度（去中心化）
- 任务依赖、补数、告警

**典型场景：**
- 每日离线报表任务编排
- 实时任务监控
- 跨团队任务协同

### 5.5 07-data-governance/

**一句话定位：** 数据治理三大支柱（元数据/血缘/质量）+ 安全合规

**核心覆盖：**
- 元数据管理（Apache Atlas / DataHub / OpenMetadata）
- 数据血缘（Column-Level Lineage）
- 数据质量（Great Expectations / Deequ）
- 数据安全（脱敏 / 访问控制 / 审计）

**典型场景：**
- 金融数据合规（GDPR / 数据出境）
- 数据资产盘点
- 故障根因定位（血缘反向追溯）

### 5.6 08-sync-tools/

**一句话定位：** 异构数据同步工具（DataX/SeaTunnel/Sqoop/Flume）

**核心覆盖：**
- DataX 阿里开源（离线批量）
- Apache SeaTunnel（实时 + 离线）
- Sqoop（数据库 ↔ Hadoop）
- Flume（日志流式采集）

**典型场景：**
- MySQL → Hive 离线同步
- Kafka → ClickHouse 实时同步
- 日志采集 → HDFS / ES

---

## 6. PNG 替换（6 张 → 3 个 mermaid）

### 6.1 现有 PNG 列表

| PNG | 当前位置 | 替换方案 |
|---|---|---|
| `01-data-warehouse/img.png` | offline-or-real-time 主图 | mermaid flowchart（Lambda 架构） |
| `01-data-warehouse/img_1.png` | ... | mermaid flowchart（Kappa 架构） |
| `01-data-warehouse/img_2.png` | ... | mermaid flowchart（湖仓一体） |
| `01-data-warehouse/img_3.png` | ... | mermaid sequenceDiagram（批流融合） |
| `01-data-warehouse/img_4.png` | ... | 删除（重复或低价值） |
| `03-realtime-compute/img.png` | open-source 全景图 | mermaid flowchart（开源生态全景） |

**结果：** 6 PNG → 5 mermaid 块（删除 1 张）+ 0 PNG

### 6.2 mermaid 块设计原则

- 全部 `flowchart LR/TD` 或 `sequenceDiagram`（不用 `mindmap`/`timeline`）
- 节点文案中文 + 英文缩写
- 颜色一致（subgraph 区分模块）

---

## 7. 13-commit 计划（4 阶段）

### Phase 1: 顶层 README 扩写（3 commits）

- **T1**: 章节 1（9 模块导航）+ 章节 2（知识脉络 mermaid）→ 80 → 180 行
- **T2**: 章节 3（12 张速查表）→ 180 → 320 行
- **T3**: 章节 4-11（选型树 + 学习路线 + 附录）→ 320 → 380 行

### Phase 2: 9 子模块索引化（9 commits）

- **T4**: 01-data-warehouse/（offline-or-real-time 改造，73→80）
- **T5**: 02-hadoop-ecosystem/（新增空壳 80 行）
- **T6**: 03-realtime-compute/（open-source 改造，261→80）
- **T7**: 04-data-lake/（新增空壳 80 行）
- **T8**: 05-olap/（新增空壳 80 行）
- **T9**: 06-scheduling/（新增空壳 80 行）
- **T10**: 07-data-governance/（新增空壳 80 行）
- **T11**: 08-sync-tools/（新增空壳 80 行）
- **T12**: 章节 9 章节统计更新（25 + 6 = 31 ... 等，最终 1 + 8 + 6 = 15 README）

### Phase 3: 6 新子 README（1 batch commit）

- **T13**: 6 × 200-300 行（详见 §5）一次性创建

### Phase 4: PNG 替换（1 commit）

- **T14**: 6 PNG 删除 + 5 mermaid 块插入 + 17 placeholder 清理

**总计：14 commits**

---

## 8. 全局约束（继承 09 spec + 仓库约定）

- **零 PNG**：所有图必须 mermaid；本 spec 完成后 0 张仓库图片
- **零 TODO**：完成后 `grep -rE "TODO|TBD|待完善" note/10.big-data/` 必须 0 行
- **零 PNG 引用**：完成后 `grep -rE "<img|!\[.*\]\(.*\.png" note/10.big-data/` 必须 0 行
- **不写厂商主观对比表**：速查表按事实属性（吞吐/延迟/生态），不分级推荐
- **链接风格**：相对路径（`./xxx`），不使用绝对路径
- **Mermaid 兼容**：只用 `flowchart LR/TD` + `sequenceDiagram`（不用 `mindmap`/`timeline`）
- **顶层 README 行数目标**：350-400 行
- **子模块 README 行数目标**：50-80 行
- **新子 README 行数目标**：200-300 行
- **commit 颗粒度**：14 commits 独立可查、可回滚
- **保持现有 2 个子 README 内容不变**：本重构把它们拆散重组，原 README 内容大部分迁移到新位置（待定）

---

## 9. 不在本 Spec 范围

- 09-bigdata-and-ai/ 模块（避免与 11.ai 重叠）
- 2 个原有子 README 内的具体技术内容深度重构（只移动到合适子 README + 索引化）
- 17 个 placeholder 的内容填充（只删除空的）
- 顶层 README 的 5 章宏观综述内容（保留在 §1 9 模块导航表格中作为简介）

---

## 10. 验收标准

### 10.1 数量验收

| 项 | 目标 |
|---|------|
| 顶层 README 行数 | 350-400 |
| 9 子模块 README 平均行数 | 50-80 |
| 新子 README 数 | 6 |
| 每个新子 README 行数 | 200-300 |
| 仓库 PNG 数 | 0 |
| TODO/placeholder 数 | 0 |
| mermaid 块总数 | ≥ 10（4 决策树 + 5 PNG 替换 + 1 知识脉络） |

### 10.2 链接验收

- 0 死链（所有相对路径解析到存在的文件/锚点）
- 顶层 12 速查表无重复内容（与子 README 不重复定义）

### 10.3 风格验收

- 8 个子模块 README 都用 7 节模板
- 6 个新子 README 都用 9 节深读模板
- 顶层 11 节编号 1-11 完整

### 10.4 提交验收

- 14 commits 独立可查
- 每个 commit 信息结尾含 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- 完成后 push 到 origin/master

---

## 11. 风险与缓解

| 风险 | 缓解 |
|---|------|
| 现有 open-source/ README 261 行，索引化会丢失大量内容 | 关键内容迁到 02/04/05/06/07/08 对应子 README；不能迁的接受删除（已建议） |
| 17 placeholder 删除可能丢失用户原始意图 | 删除前 grep 一次确认都是空行 |
| 顶层 README 9 模块 vs 09 的 9 模块结构是否一致 | 严格对齐 09 模式（11 节 + 12 速查表 + 4 决策树） |
| 新子 README 内容质量难保证 | 仿 09 T13 经验：先写骨架 brief → 实施 → fix 扩到 200-300 行 |
| 14 commits 数量适中，但仍需 14 task × 2 subagent = 28+ 调度 | 接受，沿用 Subagent-Driven 模式 |

---

## 12. 与 09 plan 的差异

| 维度 | 09.front-end | 10.big-data（本 spec） |
|---|---|---|
| 顶层行数目标 | 400-500 | **350-400**（10 规模小） |
| 子模块数 | 9 | **8**（避免与 11.ai 重叠） |
| 现有子 README 数 | 25 | **2**（保留目录结构，索引化） |
| 新子 README 数 | 6 | **6**（同 09） |
| 子 README 模板 | 8 节 | **7 节**（小幅简化） |
| 顶层章节数 | 11 | **11**（同 09） |
| 速查表数 | 12 | **12**（同 09） |
| 决策树数 | 4 | **4**（同 09） |
| 章节命名风格 | 数字 + emoji | **数字 + emoji**（同 09） |
| 章节 9 统计：子 README 总数 | 31 | **15**（1+8+6） |

---

**Spec 完成，待用户批准后进入 writing-plans 阶段。**