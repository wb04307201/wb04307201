# 12.interview ↔ 主模块 depth 联动映射（2026-09-01）

> **目的**：把高频面试题（5⭐⭐⭐⭐⭐ + 4⭐⭐⭐⭐）与主模块 depth 对应，建立"面试触发 → 主模块深入"的导航关系
> **方法**：从 169 题（5⭐ 61 + 4⭐ 108）中抽 30 题映射
> **关键指标**：5⭐ 平均对应 depth 4.33/5，4⭐ 平均对应 depth 4.40/5

## 5⭐ 题映射（抽 15 个）

| # | 12.interview 题 | diff | 对应主模块 leaf | depth | 对齐 | 备注 |
|---|----------------|-----|----------------|-------|------|------|
| 1 | 11.ai/rag | 5⭐ | 09.ai-applications/rag (MOC) | L4 | ✓ -1 | children 含 5 个 L5 + 4 个 L3-L4 |
| 2 | 11.ai/prompt-engineering | 5⭐ | 09.ai-applications/prompts/prompt-engineering | L3 | ✗ **-2** | **不匹配** |
| 3 | 11.ai/llm-inference | 5⭐ | 09.ai-applications/llm-inference (MOC) | L4 | ✓ -1 | vllm-vs-ollama / kv-cache L5 |
| 4 | 11.ai/multi-agent-system-design | 5⭐ | 09.ai-applications/agent/production-agent | L4 | ✓ -1 | 轻度低估 |
| 5 | 11.ai/vector-search-at-scale | 5⭐ | 09.ai-applications/rag/vector-search-at-scale | L5 | ✓ | 完全对齐 |
| 6 | 11.ai/function-calling | 5⭐ | 09.ai-applications/agent/agent-spec-tools | L3 | ✗ **-2** | **不匹配** |
| 7 | 03.database/mvcc | 5⭐ | 03.data-stack/01-database/03-transaction | L4 | ✓ -1 | 通用 MVCC，PG 专项 L5 |
| 8 | 03.database/redis-persistence | 5⭐ | 03.data-stack/01-database/07-redis | L5 | ✓ | 完全对齐 |
| 9 | 03.database/sharding-distributed-tx | 5⭐ | 06.distributed-systems/.../db-sharding | L5 | ✓ | 分片在 distributed |
| 10 | 04.system-design/distributed-lock | 5⭐ | 06.distributed-systems/02-distributed/distributed-lock | L4 | ✓ -1 | 轻度低估 |
| 11 | 04.system-design/live-barrage-100k | 5⭐ | 06.distributed-systems/04-high-performance/mq | L5 | ✓ | 完全对齐 |
| 12 | 04.system-design/search-typeahead | 5⭐ | 06.distributed-systems/.../product-search | L4 | ✓ -1 | 轻度低估 |
| 13 | 05.security/oauth2-flow | 5⭐ | 06.distributed-systems/05-security/oauth2-oidc | L5 | ✓ | 完全对齐 |
| 14 | 09.front-end/large-list-perf | 5⭐ | 05.frontend/03-frameworks/vue/large-list-perf | L5 | ✓ | 完全对齐（专属 leaf） |
| 15 | 10.big-data/kafka-exactly-once | 5⭐ | 06.distributed-systems/04-high-performance/mq | L5 | ✓ | 完全对齐 |

## 4⭐ 题映射（抽 15 个）

| # | 12.interview 题 | diff | 对应主模块 leaf | depth | 对齐 | 备注 |
|---|----------------|-----|----------------|-------|------|------|
| 1 | 01.java/concurrent-hashmap | 4⭐ | 01.java-and-jvm/collection/ConcurrentHashMap | L5 | ✓ +1 | 主模块更深入 |
| 2 | 01.java/jvm-memory | 4⭐ | 01.java-and-jvm/02-jvm | L5 | ✓ +1 | 主模块更深入 |
| 3 | 01.java/thread-pool | 4⭐ | 01.java-and-jvm/03-concurrency/thread-pool | L3 | ✓ -1 | 轻度低估 |
| 4 | 01.java/synchronized-lock-upgrade | 4⭐ | 01.java-and-jvm/03-concurrency/synchronized | L4 | ✓ | 完全对齐 |
| 5 | 03.database/bplus-tree | 4⭐ | 03.data-stack/01-database/04-index | L5 | ✓ +1 | 主模块更深入 |
| 6 | 03.database/redis-cluster | 4⭐ | 03.data-stack/01-database/07-redis | L5 | ✓ +1 | 主模块更深入 |
| 7 | 04.system-design/cache-consistency | 4⭐ | 06.distributed-systems/02-distributed/distributed-cache | L5 | ✓ +1 | 主模块更深入 |
| 8 | 04.system-design/circuit-breaker | 4⭐ | 06.distributed-systems/03-high-availability/circuit-break | L5 | ✓ +1 | 主模块更深入 |
| 9 | 06.spring/transactional-propagation | 4⭐ | 04.spring-backend/04-data/transaction/propagation-and-isolation | L3 | ✓ -1 | 无 frontmatter depth |
| 10 | 06.spring/circular-dependency | 4⭐ | 04.spring-backend/01-core/ioc/circular-dependency | L4 | ✓ | 完全对齐 |
| 11 | 06.spring/aop-principle | 4⭐ | 04.spring-backend/01-core/aop | L3 | ✓ -1 | 无 frontmatter depth |
| 12 | 09.front-end/event-loop | 4⭐ | 05.frontend/02-language/runtime | L4 | ✓ | 完全对齐 |
| 13 | 09.front-end/virtual-dom-diff | 4⭐ | 05.frontend/03-frameworks/react | L5 | ✓ +1 | 主模块更深入 |
| 14 | 02.computer-basics/tcp-handshake-teardown | 4⭐ | 02.cs-foundations/03-network/tcp-handshake-teardown | L5 | ✓ +1 | 主模块更深入（同名 leaf） |
| 15 | 05.security/jwt-vs-session | 4⭐ | 06.distributed-systems/05-security/jwt-security | L5 | ✓ +1 | 主模块更深入 |

## 不匹配清单（偏差 ≥2）

| 题 | diff | 主模块 leaf | depth | 偏差 | 修复建议 |
|---|------|-------------|-------|------|----------|
| 12.interview/11.ai/prompt-engineering | 5⭐ | 09.ai-applications/prompts/prompt-engineering | L3 | **-2** | 当前仅 3 段基础 prompt 模板；需补 CoT / ReAct / Self-Consistency / 结构化输出 / 多模态 prompt，至少扩到 L5 |
| 12.interview/11.ai/function-calling | 5⭐ | 09.ai-applications/agent/agent-spec-tools | L3 | **-2** | 当前 3 个 spec 工具；需补 function calling 协议（OpenAI/Anthropic/MCP）、JSON Schema、tool use error handling |

## 关键洞察

### 1. 5⭐ 与 4⭐ 题主模块覆盖度对比

| 指标 | 5⭐ 题 | 4⭐ 题 |
|------|--------|--------|
| 平均对应主模块 depth | 4.33 / 5 | 4.40 / 5 |
| 完全对齐率 | 46.7% | 26.7% |
| 主模块更深入（+1） | 0% | 53.3% |
| 轻度低估（-1） | 40% | 13.3% |
| 不匹配（-2） | 13.3% | 0% |

### 2. 核心问题

**5⭐ AI 题 → 09.ai-applications 主模块深度不足**

5⭐ 面试题是高频热点，但 09.ai-applications 模块平均 6.50 / 10（仅 L3 顶部）。表现为：
- 6 个 -1 的 5⭐ 题中，5 个是 MOC/索引层（rag / llm-inference / multi-agent / mvcc / distributed-lock）
- 主模块需要更细分的子 leaf 才能匹配 5⭐ 颗粒度
- 2 个 -2 的不匹配都集中在 09.ai-applications

### 3. 推荐补强清单（Top 5 高频 + 浅主模块）

| 优先级 | 主模块 leaf | 当前 depth | 5⭐ 面试题 | 修复方向 |
|:------:|------------|:----------:|------------|----------|
| 1 | 09.ai-applications/prompts/prompt-engineering | L3 | prompt-engineering | 扩到 L5，涵盖 CoT/ReAct/structured output |
| 2 | 09.ai-applications/agent/agent-spec-tools | L3 | function-calling | 扩到 L5，涵盖 function calling / MCP / tool use |
| 3 | 09.ai-applications/agent/agent-execution-patterns | L3 | multi-agent-system-design | 4 模式深度对比扩到 L5 |
| 4 | 09.ai-applications/agent/architecture | L3 | multi-agent | 多 Agent 架构扩到 L5 |
| 5 | 01.java-and-jvm/03-concurrency/thread-pool | L3 | thread-pool | 线程池扩到 L4（含拒绝策略矩阵 / Worker 回收） |

### 4. 副洞察

- **04.spring-backend 模块均深仅 5.35**（最低），多个 leaf 缺 frontmatter depth 字段；建议统一补全
- **完全对齐的 5⭐ 题集中在 06.distributed-systems（L4-L5） + 03.data-stack/07-redis + 05.frontend 专属 leaf** —— 这三类是沉淀质量最高的
- **反向链价值**：4⭐ 题主模块 +1 占比 53.3% —— 双层沉淀的"反向链"价值在此体现：面试题触发学习后，主模块已超额覆盖

## 应用场景

1. **学习路径规划**：从 12.interview 5⭐ 题入手，遇到不匹配时跳转主模块对应 L5 leaf 深挖
2. **沉淀缺口识别**：2 个 -2 不匹配项是下一轮主模块深化的最高 ROI 目标
3. **质量标杆**：3 大沉淀质量最高的子类（06.distributed-systems / 03.data-stack / 05.frontend 专属 leaf）应作为其他模块的方法论样板

## 关联文件

- 12.interview 高频题清单：每个 subdir 的 `README.md` + 各 `topic/README.md`
- 主模块 depth 分布：`README.md` 总目录章节 + `skills/note-health/references/main-module-depth.md`
- difficulty ↔ depth 校准流程：`skills/note-health/references/difficulty-calibration.md`
