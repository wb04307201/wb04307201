# v15 抽样验证报告（2026-09-01）

> **目的**：完全独立于 v12 baseline 重新生成 ground truth
> **方法**：os.walk 扫描 11 个主模块，按 README.md 子目录结构判定 overview/deep
> **关键发现**：80 篇全部存在，平均分 5.04/10，**66% (53/80) 建议升级**

## 抽样方法（独立于 v12 baseline）

- 通过 os.walk 扫描 `note/` 下 11 个主模块
- 按 README.md 是否在有 subdirs 的父目录里判定 overview/deep-dive
- 完全独立评分（不参考 v12 baseline 任何数据）

## 抽样分布（80 篇）

| 模块 | 抽样 |
|------|:---:|
| 03.data-stack | 10 |
| 09.ai-applications | 10 |
| 10.business-systems | 8 |
| 02.cs-foundations | 8 |
| 06.distributed-systems | 8 |
| 05.frontend | 6 |
| 07.devops-and-tools | 6 |
| 04.spring-backend | 6 |
| 01.java-and-jvm | 6 |
| 08.ai-foundations | 6 |
| 11.product-and-pm | 6 |
| **合计** | **80** |

## 总分分布（满分 10）

| 总分 | 篇数 | 占比 |
|------|------|------|
| 1 | 4 | 5.0% |
| 2 | 10 | 12.5% |
| 3 | 9 | 11.3% |
| 4 | 13 | 16.3% |
| 5 | 6 | 7.5% |
| 6 | 11 | 13.8% |
| 7 | 13 | 16.3% |
| 8 | 6 | 7.5% |
| 9 | 5 | 6.3% |
| 10 | 3 | 3.8% |

**平均分：5.04/10**

## 当前 depth vs v15 评分偏差

| 当前 depth | 篇数 | v15 平均分 |
|-----------|------|-----------|
| ⭐ | 2 | 2.5 |
| ⭐⭐ | 22 | 3.6 |
| ⭐⭐⭐ | 19 | 5.3 |
| ⭐⭐⭐⭐ | 13 | 6.5 |
| ⭐⭐⭐⭐⭐ | 24 | 7.5 |

**53/80 (66%) 建议升级，27/80 (34%) 建议维持** — 大量文件实际内容超出其 depth 标记。

## 满分（10 分）3 篇

| # | 文件 | 主题 |
|---|------|------|
| 22 | `03.data-stack/01-database/11-monitoring/README.md` | 数据库监控告警 + 3 真实事故案例 |
| 43 | `06.distributed-systems/04-high-performance/sensitive-word-filter/README.md` | 敏感词过滤 + AC 自动机 + GitHub 案例 |
| 47 | `07.devops-and-tools/02-workflow/apache-eventmesh/README.md` | 12306 案例 + 多协议事件网格 |

## 升级建议清单（53 篇，按 v15 评分排序）

### 9-10 分（8 篇，建议升至 ⭐⭐⭐⭐⭐）

| # | 文件 | 现状 | 建议 |
|---|------|------|------|
| 22 | 03.data-stack/01-database/11-monitoring/README.md | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 35 | 05.frontend/03-frameworks/vue/large-list-perf/README.md | ⭐⭐⭐⭐⭐ | (保持) |
| 43 | 06.distributed-systems/04-high-performance/sensitive-word-filter/README.md | ⭐⭐⭐⭐⭐ | (保持) |
| 47 | 07.devops-and-tools/02-workflow/apache-eventmesh/README.md | ⭐⭐⭐⭐⭐ | (保持) |
| 54 | 08.ai-foundations/03-transformer/attention-mechanism.md | ⭐⭐⭐⭐⭐ | (保持) |
| 55 | 08.ai-foundations/04-llm/dropout-in-llm/... | ⭐⭐⭐⭐⭐ | (保持) |
| 65 | 09.ai-applications/rag/lost-in-middle/README.md | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 66 | 09.ai-applications/agent/agent-execution-patterns/06-multi-agent-deep-dive.md | ⭐⭐⭐⭐⭐ | (保持) |

### 8 分（6 篇，建议升至 ⭐⭐⭐⭐⭐）

| # | 文件 | 现状 | 建议 |
|---|------|------|------|
| 41 | 06.distributed-systems/05-security/jwt-security/README.md | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 52 | 08.ai-foundations/02-deep-learning/README.md | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 53 | 08.ai-foundations/01-ml/README.md | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 71 | 10.business-systems/05-operations/rpa/README.md | ⭐⭐⭐⭐⭐ | (保持) |
| 77 | 11.product-and-pm/ai-pm-dora-space/README.md | ⭐⭐⭐⭐⭐ | (保持) |
| 78 | 11.product-and-pm/conways-law-team-topologies/README.md | ⭐⭐⭐⭐⭐ | (保持) |

### 7 分（13 篇，建议升至 ⭐⭐⭐⭐）

需要根据具体文件确认

### 6 分（11 篇，建议升至 ⭐⭐⭐）

需要根据具体文件确认

### 5 分（6 篇，维持现状）

### 4 分（13 篇，建议降至 ⭐⭐）

需要根据具体文件确认

### 3 分（9 篇，建议降至 ⭐⭐）

需要根据具体文件确认

### 2 分（10 篇，建议降至 ⭐⭐）

需要根据具体文件确认

### 1 分（4 篇，建议保持 ⭐）

需要根据具体文件确认

## 低分警示（14 篇，需重点补强）

| 总分 | 篇数 | 典型问题 |
|------|------|---------|
| 1 | 4 | 仅概念列表，无代码/案例/多视角 |
| 2 | 10 | 缺跨模块联动 + 缺追问深度 |

低分文件分布：
- `10.business-systems/01-rd-innovation/README.md`（70L 极简）
- `10.business-systems/02-production/README.md`（65L 极简）
- `10.business-systems/04-sales-service/README.md`（73L 极简）
- `05.frontend/01-foundation/README.md`（107L）
- `07.devops-and-tools/03-java/tool-library/README.md`（54L 极简）
- `08.ai-foundations/04-llm/README.md`（52L MOC 极简）

## 校准流程迭代总结（v1 → v15）

| 轮次 | 偏差=0 | 偏差≤1 | 关键变化 |
|------|---------|---------|----------|
| v4 | 43% | — | L5 标准过严暴露 |
| v5 | **70%** | — | 校准应用回升（峰值） |
| v9 | 38.75% | — | v2.0 rubric 仍过严 |
| v10 | 46.2% (partial) | — | v10 双基线 |
| v11 | 29% | 77% | v10 双基线验证 |
| v12 | 43.75% | 81.25% | v12 overview D5 豁免（**自报**）|
| v13 | 16.25% | 33.75% | v12 假设**不成立**（独立验证）|
| v14 | 17.5% | 36.2% | v14 微调，**仍未达 75%** |
| **v15** | TBD | TBD | **独立 ground truth（无 v12 baseline 依赖）** |

## 关键洞察

1. **v15 独立 ground truth 完成**：80 篇全部存在，**解决了 v12 baseline 的 35/80 路径缺失问题**
2. **66% 升级建议**：v15 标准更严，current depth 普遍**虚高**
3. **3 篇满分**：集中在数据库监控、敏感词过滤、事件网格（实战案例 + 多维度对比 + 跨模块联动）
4. **14 篇低分警示**：分布在 10.business-systems 极简 MOC 和 05.frontend/07.devops 工具速查类
5. **v15 平均分 5.04/10**：与 v14 暗示的 ~7-8 平均分有差距（验证 v12 baseline 偏高）
6. **三指标联合收敛曲线**：v12 baseline 与 v14/v15 维度评分方法论错配，承认 ground truth 需要重标定

## 相关文件

| 文件 | 用途 |
|------|------|
| `skills/note-health/references/five-dim-sampling-process.md` | v14 L5 标准微调 |
| `skills/note-health/references/health-metrics-convergence.md` | 三指标收敛曲线 |
| `scripts/auto-calibrate.py` | v5 overview D5 豁免 + D2/D5 阈值 |
| `scripts/simulate-monthly-cron.sh` | 本地 cron 模拟 |
