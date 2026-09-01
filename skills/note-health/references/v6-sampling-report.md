# v6 抽样验证报告（2026-09-01）

> **目的**：验证 v4+v5 校准应用后准确度提升
> **方法**：30 篇抽样（含 v4+v5 校准过的 14 篇 + 新增未评估文件）
> **关键发现**：准确度 **53.3%**（16/30），比 v5 (70%) **下降 16.7 个百分点**

## 评分明细（30 篇）

### 完全一致（16 篇，53.3%）

| # | 文件 | 当前 | 5-dim |
|---|------|------|------|
| 1 | 03.data-stack/01-database/03-transaction | ⭐⭐⭐⭐ | 7 |
| 2 | 03.data-stack/01-database/04-index/composite-index-filesort | ⭐⭐⭐ | 5 |
| 6 | 09.ai-applications/agent/agent-context/context-engineering | ⭐⭐⭐⭐⭐ | 9 |
| 8 | 09.ai-applications/agent/agent-memory | ⭐⭐⭐⭐⭐ | 9 |
| 11 | 10.business-systems/01-rd-innovation/cms | ⭐⭐ | 4 |
| 12 | 10.business-systems/02-production/aps | ⭐⭐ | 4 |
| 13 | 10.business-systems/02-production/mom | ⭐⭐ | 4 |
| 14 | 10.business-systems/01-rd-innovation/km | ⭐⭐⭐⭐ | 8 |
| 18 | 06.distributed-systems/02-distributed/consensus-algorithms/raft | ⭐⭐⭐⭐ | 7 |
| 19 | 06.distributed-systems/02-distributed/cap-and-base/cap | ⭐⭐⭐⭐⭐ | 9 |
| 23 | 05.frontend/03-frameworks/vue/large-list-perf | ⭐⭐⭐⭐⭐ | 9 |
| 25 | 07.devops-and-tools/01-tools/04-nginx/pingora | ⭐⭐⭐⭐⭐ | 9 |
| 26 | 04.spring-backend/01-core/event.md | ⭐⭐⭐⭐ | 7 |
| 28 | 01.java-and-jvm/03-concurrency/juc-locks | ⭐⭐⭐⭐ | 8 |
| 29 | 08.ai-foundations/04-llm/dropout-in-llm/single-epoch-and-config-evidence | ⭐⭐⭐⭐⭐ | 10 |
| 30 | 11.product-and-pm/risk-register | ⭐⭐⭐⭐ | 8 |

### 高估（14 篇，全部已应用降级）

| # | 文件 | v6 → 建议 | 5-dim |
|---|------|------|------|
| 3 | 03.data-stack/01-database/08-nosql/mongodb | ⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |
| 4 | 03.data-stack/01-database/02-sql | ⭐⭐⭐ → ⭐⭐ | 3 |
| 5 | 03.data-stack/02-big-data/02-hadoop-ecosystem | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 7 |
| 7 | 09.ai-applications/rag/chunking-strategies | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 8 |
| 9 | 09.ai-applications/agent/agent-architecture/llm-control-evolution | ⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |
| 10 | 09.ai-applications/agent/agent-evaluation/08-practical-cases | ⭐⭐⭐ → ⭐⭐ | 4 |
| 15 | 02.cs-foundations/02-os/memory | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 7 |
| 16 | 02.cs-foundations/01-algorithms/string-algorithms/02-kmp-algorithm | ⭐⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |
| 17 | 02.cs-foundations/03-network/04-https-tls | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 7 |
| 20 | 06.distributed-systems/02-distributed/distributed-transaction | ⭐⭐⭐⭐ → ⭐⭐ | 4 |
| 21 | 05.frontend/05-architecture/rendering-modes | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 8 |
| 22 | 05.frontend/02-language/runtime/async-await-error-handling/03-react-vue-production | ⭐⭐⭐⭐ → ⭐⭐ | 3 |
| 24 | 07.devops-and-tools/01-tools/devops/04-pipeline-patterns | ⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |
| 27 | 04.spring-backend/01-core/ioc/circular-dependency | ⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |

### 低估（0 篇）

无低估案例。

### depth 缺失（0 篇）

无 depth 缺失。

## 准确度评分

| 维度 | v4 | v5 | v6 | 趋势 |
|------|----|----|----|------|
| 完全一致 | 43% | 70% | **53.3%** | ⚠ 下降 |
| 低估 | 17% | 13% | 0% | ✅ 下降 |
| 高估 | 40% | 17% | 47% | ⚠ 反弹 |
| depth 缺失 | 3% | 3% | 0% | ✅ 改善 |

**结论**：v6 准确度从 v5 (70%) 下降至 53.3%，全部偏差方向为高估。L5 标准仍需进一步收紧。

## 根因分析

### 1. L5 标准 v4 后收紧但 v6 抽样暴露系统性偏高

14 篇偏差全部方向一致（高估），说明现有评级标准系统性偏高 1 级：
- L5 → L4：缺 D2 跨模块联动（多数仅在同模块内打转）
- L5 → L4：缺 D1 源码深度（仅原理 + API）

### 2. v5 校准未解决 base rate 偏高问题

v5 应用了 10 篇校准，但整体分布仍偏高。说明 depth 字段的初始赋值（v2/v3 抽样时）就需要更严的标准。

### 3. 关键扣分维度

- **D2 跨模块**（80% 高估案例）：仅"主模块内联动"而非真正 5+ 主模块
- **D1 源码深度**（次要）：多为原理 + 公式而非引擎源码

## 已应用校准（commit a8c9b88c）

14 篇降级校准全部应用：
- 11 篇高估 1 级
- 3 篇高估 2 级（kmp / distributed-transaction / async-await-error-handling）

## 校准流程迭代总结（v1 → v6）

| 轮次 | 准确度 | 偏差方向 | 关键变化 |
|------|--------|---------|----------|
| v1 | N/A | 233 误报 | 初始基线 |
| v2 | 70% | 6 → 0 | 修复合并检测 + emoji 兼容 |
| v3 | 100%（小样本）| 0 | 修复重复表误报 |
| v4 | 43% | 17 偏差 | L5 标准过严暴露 |
| **v5** | **70%** | 9 | 校准应用后回升 ✅ |
| **v6** | **53.3%** | 14 | 全部高估，标准仍偏宽松 |

## 推荐下一步

### 1. **L5 标准 2.0（v7 抽样前）**

除 D2 ≥ 5 跨模块外，加：
- D1 必须含"可运行代码片段"或"字节码级分析"
- D4 ≥ 5 层追问需 3+ 反直觉点支撑
- D5 需 5+ 真实公司案例（部分 1-2 案例文件需降级）

### 2. **v7 抽样策略调整**

- 抽 50 篇（vs 30 篇）提升统计可靠性
- 抽样组成：70% 已校准文件 + 30% 未评估文件（验证 base rate）
- 多 agent 共识：每篇 2 agent 评分（取均值）

### 3. **CI 自动化校准**

- 月度 cron 自动跑 v6+ 抽样 + auto-calibrate.py
- 阈值 ≥ 2 自动应用
- 阈值 = 1 标记待人工审核

## 相关文件

| 文件 | 用途 |
|------|------|
| `skills/note-health/references/v4-sampling-report.md` | v4 偏差清单（17 篇） |
| `skills/note-health/references/v5-sampling-report.md` | v5 准确度回升（70%） |
| `skills/note-health/references/five-dim-sampling-process.md` | 流程固化 |
| `scripts/auto-calibrate.py` | 自动化校准脚本 |
