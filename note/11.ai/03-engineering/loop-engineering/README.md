<!--
module:
  parent: ai
  slug: ai/loop-engineering
  type: article
  category: 主模块子文章
  summary: Loop Engineering：循环调用 Agent 直到任务完成的反直觉哲学。
-->

# Loop Engineering — 循环调用的反直觉哲学

← 返回 [工程实践](../README.md)

> 2026 年 AI 工程第四阶段：当任务复杂到 Agent 一次跑不完，怎么办？Loop Engineering 是"循环调用 Agent 直到任务完成"的工程实践 —— 核心是 Harness 兜底防止失控。

---
---

## 一、核心结论（TL;DR）

| 阶段 | 关注点 | 主导者 |
|------|--------|--------|
| [Prompt Engineering](../../02-technology-stack/prompt-engineering/README.md) | 怎么写好一句提示 | 人类 |
| [Context Engineering](../../02-technology-stack/context-engineering/README.md) | 怎么管理上下文 | Agent |
| [Harness Engineering](../harness-engineering/README.md) | 怎么约束 Agent 行为 | 规范/流程 |
| **Loop Engineering** | 怎么循环调用 Agent 直到任务完成 | Agent + Harness |

> 一句话：**Loop Engineering 是"信任 Agent，让它循环重试直到任务完成"——前提是 Harness 兜底防止失控**。

📌 **驾驭演进主线**：[LLM 驾驭演进史（Prompt → Context → Harness → Loop）](../../04-architecture/llm-control-evolution/README.md)

---

## 二、什么是 Loop？

**Loop** 是"循环调用同一个 Agent 直到任务完成"的模式：

```
Task → Agent → 检查结果
  ↑                  │
  └──── 不通过 ←─────┘
              通过
                ↓
              Done
```

例如 AI 写代码 + 自动测试：

```python
for attempt in range(max_attempts):
    code = agent.generate_code(task)
    test_result = run_tests(code)
    
    if test_result.passed:
        return code  # 成功
    else:
        # 把错误反馈给 Agent，重新生成
        agent.feedback(test_result.error)
        
raise Exception("Max attempts reached")
```

---

## 三、Loop 的 3 大核心组件

### 1. 任务定义（Task）

清晰、可验证的 task 定义：

```python
task = """
实现一个 LRU Cache，要求：
1. get(key) 和 put(key, value) 都是 O(1)
2. 容量满时淘汰最久未使用的 key
3. 写单元测试覆盖边界场景
"""
```

### 2. 验证函数（Verifier）

可以自动检查任务是否完成：

```python
def verify(code: str) -> bool:
    """运行测试 + Lint + 类型检查"""
    return (
        run_unit_tests(code) and
        run_lint(code) and
        run_type_check(code)
    )
```

### 3. 反馈循环（Feedback Loop）

把失败原因反馈给 Agent，让它改进：

```python
feedback = """
测试失败：
- test_lru_eviction: 期望 [3, 4] 实际 [4, 3]
- 你的 evict() 函数逻辑有误
"""
agent.regenerate(feedback)
```

---

## 四、Loop vs DAG：什么时候用哪个？

| 场景 | 推荐 | 理由 |
|------|------|------|
| 任务明确、步骤固定 | DAG Workflow | 确定性、可预测 |
| 任务模糊、需要探索 | Loop + Agent | 灵活性高 |
| 一次性脚本 | 一次性 Agent 调用 | 简单 |
| 持续运行的服务 | Loop + 监控 | 自动化 |
| 复杂业务流 | DAG + Loop 混合 | 兼顾确定性与灵活性 |

详见 [Agent 架构](../../04-architecture/agent-architecture/README.md)。

---

## 五、Loop 的 4 大失败模式

### 1. 无限循环（Infinite Loop）

Agent 反复失败但永远不停止。

**防护**：
```python
MAX_ATTEMPTS = 5  # 硬性上限
TIMEOUT = 300  # 5 分钟超时
```

### 2. 上下文爆炸（Context Explosion）

每次循环都把错误堆到 Context 里，最终超出窗口。

**防护**：
```python
# 只保留最近 3 次的错误
def trim_context(context, max_errors=3):
    return context[-max_errors:]
```

### 3. 幻觉放大（Hallucination Amplification）

Agent 在错误反馈基础上"幻觉"出新错误。

**防护**：
- 用 ground-truth 测试（单元测试、集成测试）而非 LLM-as-Judge
- 重置 Context 而非累积

### 4. 资源耗尽（Resource Exhaustion）

循环调用消耗大量 token 和时间。

**防护**：
- 限制每次循环的 token 预算
- 使用 cheaper 模型做"验证"，expensive 模型做"生成"

---

## 六、Loop Engineering 的 5 大最佳实践

### 1. 任务定义要"可验证"

```python
# ❌ 模糊任务
task = "写一个好的代码"

# ✅ 可验证任务
task = "写 LRU Cache，要求 O(1) get/put，通过以下测试用例：..."
```

### 2. 验证函数要"自动化"

- 单元测试
- 集成测试
- Lint / 类型检查
- 性能 benchmark
- 不要用"人类 review"做验证（太慢）

### 3. 反馈要"具体"

```python
# ❌ 模糊反馈
feedback = "你的代码有问题"

# ✅ 具体反馈
feedback = """
Line 23: TypeError: 'NoneType' object is not subscriptable
Expected: get(1) returns 1
Actual: get(1) raises TypeError
请检查 LRU cache miss 时的返回逻辑
"""
```

### 4. Context 要"重置"而非累积

```python
# ❌ 累积 Context
context += error_message  # Context 越来越长

# ✅ 重置 + 关键信息
context = base_context + last_error  # 每次重新开始
```

### 5. 兜底机制要"完善"

- Max attempts 上限
- 超时机制
- 失败时通知人类
- 关键决策点（删除文件、发邮件、转账）必须人工确认

---

## 七、Loop Engineering 的反直觉之处

### 1. "重复"不等于"低效"

让 Agent 循环 5 次（每次 5 分钟）比让人类重写 1 次（1 小时）快 2.4 倍。

### 2. "失败"是"数据"

每次失败都让 Agent 离正确答案更近，关键是"失败模式可被验证"。

### 3. "简单循环 > 复杂 DAG"

对于探索性任务，简单 Loop 比精心设计的 DAG 更有效——因为 Agent 自己会找到路径。

### 4. "信任但验证"（Trust but Verify）

Loop 假设 Agent 能完成任务，但 Verifier 确保它真的完成了。这是 Harness Engineering 的兜底。

---

## 八、面试陷阱速览

> 完整陷阱 + 反直觉 + 30 秒话术见 [13.split-hairs Loop Engineering](../../../13.split-hairs/11.ai/loop-engineering/README.md)

---

## 相关章节

- 同栏目：[Harness Engineering](../harness-engineering/README.md) — Loop 依赖 Harness 兜底
- 上一步：[Context Engineering](../../02-technology-stack/context-engineering/README.md) — Context 重置是 Loop 关键
- 关联：[Agent 架构](../../04-architecture/agent-architecture/README.md) — Loop vs DAG 的取舍
- 实战：[生产级 Agent](../production-agent/README.md) — Loop 在生产环境的实现

← [返回: AI 知识体系 · loop-engineering](README.md)
