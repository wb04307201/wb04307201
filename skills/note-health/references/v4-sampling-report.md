# v4 抽样验证报告（2026-09-01）

> **目的**：验证 Session 3.5 校准后的 depth 字段准确度
> **方法**：从 11 个主模块抽 30 个 leaf 文件（含已有 depth 与新补 depth），用 adapted 5-dim 评分对比
> **关键发现**：准确度 **43%**（13/30 完全一致），低于 95% 阈值——流程仍需打磨

## 抽样分布（30 篇）

按模块均分权重分配：

| 模块 | 抽样数 | 模块均分 |
|------|:----:|:--------:|
| 03.data-stack | 5 | 9.4 |
| 09.ai-applications | 5 | 8.1 |
| 10.business-systems | 4 | 8.4 |
| 02.cs-foundations | 3 | 7.7 |
| 06.distributed-systems | 3 | 7.4 |
| 05.frontend | 3 | 6.9 |
| 07.devops-and-tools | 2 | 6.8 |
| 04.spring-backend | 2 | 6.3 |
| 01.java-and-jvm | 1 | 6.3 |
| 08.ai-foundations | 1 | 8.0 |
| 11.product-and-pm | 1 | 7.3 |

## 评分明细（30 篇）

### 完全一致（13 篇，43%）

| # | 文件 | 当前 | 5-dim |
|---|------|------|------|
| 6 | 09.ai-applications/rag/embedding-models | ⭐⭐⭐⭐⭐ | 9 |
| 7 | 09.ai-applications/llm-inference/paged-attention | ⭐⭐⭐⭐⭐ | 10 |
| 8 | 09.ai-applications/fine-tuning/06-peft-lora | ⭐⭐⭐⭐⭐ | 10 |
| 14 | 10.business-systems/01-rd-innovation/km | ⭐⭐⭐⭐⭐ | 9 |
| 18 | 06.distributed-systems/01-foundation/software-engineering/quality-assurance | ⭐ | 1 |
| 19 | 06.distributed-systems/01-foundation/system-design-basics/api/rest | ⭐ | 1 |
| 20 | 06.distributed-systems/01-foundation/02-evolution/02-serverless-architecture | ⭐⭐⭐ | 5 |
| 22 | 05.frontend/02-language/typescript | ⭐⭐⭐ | 5 |
| 23 | 05.frontend/02-language/angular | ⭐⭐⭐⭐ | 8 |
| 24 | 07.devops-and-tools/01-tools/01-git/branch-naming | ⭐⭐⭐⭐ | 8 |
| 26 | 04.spring-backend/01-core/aop/pointcut-expression | ⭐⭐⭐ | 6 |
| 28 | 01.java-and-jvm/01-language/enum | ⭐⭐ | 3 |

### 低估（5 篇，建议提升）

| # | 文件 | 当前 → 建议 | 5-dim |
|---|------|------|------|
| 9 | 09.ai-applications/agent/agent-context/context-engineering | ⭐⭐⭐ → ⭐⭐⭐⭐⭐ | 9 |
| 10 | 09.ai-applications/agent/agent-memory | ⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐ | 9 |
| 21 | 05.frontend/01-foundation/css-engineering | ⭐⭐ → ⭐⭐⭐ | 5 |
| 29 | 08.ai-foundations/04-llm/dropout-in-llm | ⭐⭐⭐ → ⭐⭐⭐⭐⭐ | 9 |
| 30 | 11.product-and-pm/risk-register | ⭐⭐⭐ → ⭐⭐⭐⭐⭐ | 9 |

### 高估（12 篇，建议下调）

| # | 文件 | 当前 → 建议 | 5-dim |
|---|------|------|------|
| 1 | 03.data-stack/01-database/01-fundamentals | ⭐⭐⭐ → ⭐⭐ | 3 |
| 2 | 03.data-stack/01-database/03-transaction | ⭐⭐⭐⭐ → ⭐⭐⭐ | 6 |
| 3 | 03.data-stack/01-database/04-index/composite-index-filesort | ⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |
| 4 | 03.data-stack/01-database/08-nosql/cassandra | ⭐⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |
| 5 | 03.data-stack/01-database/08-nosql/elasticsearch | ⭐⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |
| 11 | 10.business-systems/01-rd-innovation/cms | ⭐⭐ → ⭐ | 2 |
| 12 | 10.business-systems/02-production/aps | ⭐⭐⭐ → ⭐⭐ | 4 |
| 13 | 10.business-systems/02-production/mom | ⭐⭐⭐⭐ → ⭐⭐ | 4 |
| 15 | 02.cs-foundations/01-algorithms/complexity/time-complexity | ⭐⭐ → ⭐ | 1 |
| 16 | 02.cs-foundations/01-algorithms/clustering/k-means | ⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |
| 17 | 02.cs-foundations/01-algorithms/ensemble | ⭐⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |
| 25 | 07.devops-and-tools/01-tools/04-nginx/pingora | ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐ | 7 |
| 27 | 04.spring-backend/01-core/event.md | ⭐⭐⭐⭐⭐ → ⭐⭐⭐ | 5 |

## 准确度评分

| 维度 | 数据 |
|------|------|
| 完全一致 | **43%**（13/30） |
| 低估 | **17%**（5/30） |
| 高估 | **40%**（12/30） |

**结论**：准确度远低于 95% 阈值（43% < 95%），流程仍需打磨。

## 根因分析

### 1. L5 标准过严

D1 必须"引擎源码 + 字节码"才能 2 分，普通工程文档普遍拿 0-1 分；
D2 要求"5+ 主模块联动"，多数专题只在 1-2 个模块内打转。

**结论**：L5 实际只能容纳极少数文件（paged-attention / peft-lora / km / embedding-models / agent-memory / dropout / risk-register）。

### 2. 当前 depth 倾向乐观

12/30 高估集中在 L4/L5（缺跨模块互链被赋予过高评级）。

**根因**：Session 3.5 升级浪潮中，部分文件仅因主题重要性获评 L5，但实际缺乏跨模块互链（D2=0 或 1）。

### 3. 修复建议

| 类型 | 文件 | 修复方向 |
|------|------|---------|
| 高估 | cassandra / elasticsearch / ensemble / event / pingora | 补主模块间反向链后再上调；或下调 1-2 级 |
| 低估 | context-engineering / agent-memory / dropout / risk-register | 优先上调到 L5（真材实料） |
| L5 标准 | 全体 | 收紧为"源码 + 5 模块 + 5 案例"三件套硬指标 |

## 待修复偏差清单（17 篇）

### 高估（12 篇，建议降级）

1. `03.data-stack/01-database/01-fundamentals/README.md` ⭐⭐⭐ → ⭐⭐
2. `03.data-stack/01-database/03-transaction/README.md` ⭐⭐⭐⭐ → ⭐⭐⭐
3. `03.data-stack/01-database/04-index/composite-index-filesort/README.md` ⭐⭐⭐⭐ → ⭐⭐⭐
4. `03.data-stack/01-database/08-nosql/cassandra/README.md` ⭐⭐⭐⭐⭐ → ⭐⭐⭐
5. `03.data-stack/01-database/08-nosql/elasticsearch/README.md` ⭐⭐⭐⭐⭐ → ⭐⭐⭐
6. `10.business-systems/01-rd-innovation/cms/README.md` ⭐⭐ → ⭐
7. `10.business-systems/02-production/aps/README.md` ⭐⭐⭐ → ⭐⭐
8. `10.business-systems/02-production/mom/README.md` ⭐⭐⭐⭐ → ⭐⭐
9. `02.cs-foundations/01-algorithms/complexity/time-complexity/README.md` ⭐⭐ → ⭐
10. `02.cs-foundations/01-algorithms/clustering/k-means/README.md` ⭐⭐⭐⭐ → ⭐⭐⭐
11. `02.cs-foundations/01-algorithms/ensemble/README.md` ⭐⭐⭐⭐⭐ → ⭐⭐⭐
12. `07.devops-and-tools/01-tools/04-nginx/pingora/README.md` ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐
13. `04.spring-backend/01-core/event.md` ⭐⭐⭐⭐⭐ → ⭐⭐⭐

### 低估（5 篇，建议升级）

14. `09.ai-applications/agent/agent-context/context-engineering/README.md` ⭐⭐⭐ → ⭐⭐⭐⭐⭐
15. `09.ai-applications/agent/agent-memory/README.md` ⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐
16. `05.frontend/01-foundation/css-engineering/README.md` ⭐⭐ → ⭐⭐⭐
17. `08.ai-foundations/04-llm/dropout-in-llm/README.md` ⭐⭐⭐ → ⭐⭐⭐⭐⭐
18. `11.product-and-pm/risk-register/README.md` ⭐⭐⭐ → ⭐⭐⭐⭐⭐

## 推荐行动

1. **下一轮 v5 抽样**：应用上述 17 处校准后，再抽 30 篇验证准确度（目标 ≥80%）
2. **L5 硬指标化**：v1/v2/v3 抽样规则需明确"D2 ≥ 5 跨主模块"作为 L5 强制门槛
3. **CI 自动化**：将 v4 评分规则集成到 difficulty-calibration.yml 自动校验 depth 字段
4. **流程成熟度**：建议用「抽样 30 篇 → 偏差 ≥ 1 应用 → 重复」循环，逐步提升准确度
