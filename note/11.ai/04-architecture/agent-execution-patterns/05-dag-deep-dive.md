<!--
module:
  parent: ai/agent-architecture/agent-execution-patterns
  slug: ai/agent-architecture/agent-execution-patterns/05-dag
  type: topic
  category: DAG 深度
  summary: DAG（有向无环图）深度剖析 —— 节点 + 边的确定性工作流 + 错误恢复 + Loop 节点 + LangGraph/Temporal 实现 + 5 个反模式
-->

# DAG 深度剖析 · 节点 + 边的确定性工作流

> **一句话**：DAG = 把工作流拆成"节点"和"边"，每个节点做一件事，边定义执行顺序——**可预测性最强、Token 最省、生产最稳**，但灵活性最差。

← [返回: Agent 4 大模式](../README.md)

---

## 1. DAG 的本质

```
┌──────────────────────────────────────────────────────────┐
│ DAG = 节点（Node）+ 边（Edge）                             │
│                                                          │
│  [接收订单] → [校验库存] → [扣减库存] → [生成物流单]        │
│                    ↓ 库存不足                              │
│              [通知缺货] → [推荐替代品]                      │
│                                                          │
│  每个节点：一个函数 / 一个 LLM 调用 / 一个工具调用           │
│  每条边：条件路由（if-else）或顺序执行                      │
└──────────────────────────────────────────────────────────┘
```

**核心特征**：
- **确定性**：同一路径跑多次，结果一致（可复现性 10/10）
- **无环**：不会有无限循环（区别于 ReAct）
- **可视化**：整个工作流可以用图表示，产品经理都能看懂

---

## 2. DAG 的 5 种节点类型

| 节点类型 | 职责 | 示例 |
|---------|------|------|
| **函数节点** | 确定性逻辑（无 LLM） | 校验参数、格式转换、数据库查询 |
| **LLM 节点** | 调用大模型 | 文本生成、分类、摘要 |
| **工具节点** | 调用外部 API | 搜索引擎、支付接口、邮件发送 |
| **路由节点** | 条件分支（if-else） | 根据订单状态走不同路径 |
| **人工节点** | 等待人工审批 | 退款审批、内容审核 |

---

## 3. 错误恢复机制

DAG 最大的生产优势是**错误可恢复**。3 种策略：

### 3.1 重试（Retry）

```text
节点失败 → 等待 N 秒 → 重试（最多 3 次）

适用：网络超时、API 限流
实现：节点配置 retry_count + retry_delay
```

### 3.2 降级（Fallback）

```text
主节点失败 → 执行备选节点

适用：主 LLM 不可用 → 切换到备用 LLM
实现：节点配置 fallback_node_id

示例：
  [GPT-4 生成] → 失败 → [Claude 生成] → 失败 → [模板兜底]
```

### 3.3 补偿（Compensation / Saga）

```text
节点失败 → 反向执行已完成节点的"撤销"操作

适用：跨服务事务（订单创建成功但扣款失败 → 撤销订单）
实现：每个节点配对一个 compensation 节点

示例：
  [创建订单] → [扣减库存] → [扣款失败！]
                                    ↓ 补偿
                            [恢复库存] → [取消订单]
```

---

## 4. Loop 节点：让 DAG 处理动态场景

纯 DAG 无法处理循环，但通过 **Loop 节点** 可以：

```text
Loop 节点 = 子 DAG + 循环条件

[接收用户问题]
      ↓
[Loop: 信息收集]
  ├─ [提问节点] → 向用户追问
  ├─ [解析回答] → 提取信息
  └─ [判断是否足够] → 不足则循环，足够则退出
      ↓
[生成最终回答]
```

**Loop 节点的 3 个安全阀**：
1. **max_iterations** — 最多循环 N 次（防止无限循环）
2. **timeout** — 总超时时间
3. **exit_condition** — 明确的退出条件（如"收集到 3 个必填字段"）

> **反直觉**：DAG + Loop 节点 ≈ Plan-and-Execute 的 RePlan 能力，但可控性更强（循环次数有上限）。

---

## 5. 典型实现框架

| 框架 | 特点 | 适用 |
|------|------|------|
| **LangGraph** | LangChain 生态，Python 原生，节点=函数 | Python Agent 首选 |
| **Temporal** | 持久化工作流，自动重试+补偿，跨语言 | 企业级长事务 |
| **Cursor Composer** | IDE 内置，可视化编辑 | 开发工具链 |
| **Prefect** | 数据管道 + DAG，可观测性强 | 数据工程 |
| **Airflow** | 大数据调度，成熟稳定 | ETL / 批处理 |

### LangGraph 示例

```python
from langgraph.graph import StateGraph, END

# 定义状态
class OrderState(TypedDict):
    order_id: str
    stock_ok: bool
    payment_ok: bool

# 定义节点
def check_stock(state: OrderState) -> OrderState:
    # 检查库存
    state["stock_ok"] = inventory.check(state["order_id"])
    return state

def deduct_stock(state: OrderState) -> OrderState:
    inventory.deduct(state["order_id"])
    return state

def notify_out_of_stock(state: OrderState) -> OrderState:
    notification.send("商品缺货")
    return state

# 定义路由
def route_by_stock(state: OrderState) -> str:
    return "deduct" if state["stock_ok"] else "notify"

# 构建 DAG
graph = StateGraph(OrderState)
graph.add_node("check_stock", check_stock)
graph.add_node("deduct", deduct_stock)
graph.add_node("notify", notify_out_of_stock)

graph.add_conditional_edges("check_stock", route_by_stock, {
    "deduct": "deduct",
    "notify": "notify"
})
graph.add_edge("deduct", END)
graph.add_edge("notify", END)

graph.set_entry_point("check_stock")
app = graph.compile()
```

---

## 6. DAG vs ReAct vs Plan-and-Execute

| 维度 | DAG | ReAct | Plan-and-Execute |
|------|-----|-------|-----------------|
| **灵活性** | ⭐⭐（最低） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **可预测性** | ⭐⭐⭐⭐⭐（最高） | ⭐⭐ | ⭐⭐⭐⭐ |
| **Token 成本** | ⭐（最低，无循环） | ⭐⭐⭐⭐⭐（最高） | ⭐⭐⭐ |
| **错误恢复** | 重试/降级/补偿 | 靠 LLM 自行修复 | Plan Repair |
| **可视化** | ✅ 天然可视化 | ❌ 黑盒 | ⚠️ 部分可视 |
| **适合谁** | DBA / 运维 / PM 都能看懂 | 只有开发者能调试 | 开发者 + PM |

---

## 7. 5 个反模式

### ⚠️ 反模式 1：所有任务都用 DAG

- 错：探索性任务（如"帮我调研 X 技术"）硬塞进 DAG
- 对：探索任务用 ReAct，确定性流程用 DAG

### ⚠️ 反模式 2：节点粒度太细

- 错：一个"查订单"拆成 5 个节点（连接DB → 写SQL → 执行 → 解析 → 返回）
- 对：一个节点 = 一个完整业务动作（"查询订单"）

### ⚠️ 反模式 3：忽略错误恢复

- 错：DAG 节点失败直接终止，没有重试/降级/补偿
- 对：每个关键节点配置 retry + fallback

### ⚠️ 反模式 4：用 DAG 替代所有 LLM 调用

- 错：把"文本生成"也做成确定性节点（模板填充）
- 对：LLM 节点负责需要"理解"的部分，函数节点负责确定性逻辑

### ⚠️ 反模式 5：DAG 不支持动态

- 错：认为 DAG 只能走固定路径
- 对：DAG + Loop 节点 + 条件路由 = 动态且可控

---

## 8. 一句话总结

> **DAG 是生产的基石**：可预测、可复现、可观测、Token 最省。80% 的生产 Agent 应以 DAG 为主流程，辅以 ReAct 子节点处理探索性步骤。

---

## 系列导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [ReAct 深度](01-react-deep-dive.md) | Thought/Action/Observation 循环 + Token 失控 |
| 02 | [Plan-and-Execute 深度](02-plan-and-execute-deep-dive.md) | 规划 + RePlan + Plan Repair |
| 03 | [6 维对比](03-six-dimensions-comparison.md) | 4 模式完整打分 |
| 04 | [选型决策树](04-selection-decision-tree.md) | 场景化选型 + checklist |
| **05** | **DAG 深度（本文）** | 节点设计 + 错误恢复 + Loop 节点 |
| 06 | [Multi-Agent 深度](06-multi-agent-deep-dive.md) | 通信协议 + 协调者 + 循环防护 |

---

← [返回: Agent 4 大模式](../README.md) · 上一章：[04-selection-decision-tree](04-selection-decision-tree.md) · 下一章：[06-multi-agent](06-multi-agent-deep-dive.md)
