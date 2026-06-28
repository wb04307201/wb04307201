# Loop Engineering：循环调用的反直觉哲学

> 2026 年 AI 工程第四阶段：当任务复杂到 Agent 一次跑不完，怎么办？Loop Engineering 是"循环调用 Agent 直到任务完成"的工程实践。

## 一、核心结论（TL;DR）

| 阶段 | 关注点 | 主导者 |
|------|--------|--------|
| Prompt Engineering | 怎么写好一句提示 | 人类 |
| Context Engineering | 怎么管理上下文 | Agent |
| Harness Engineering | 怎么约束 Agent 行为 | 规范/流程 |
| **Loop Engineering** | 怎么循环调用 Agent | Agent + Harness |

> 一句话：**Loop Engineering 是"信任 Agent，让它循环重试直到任务完成"——前提是 Harness 兜底防止失控**。

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

详见 [`agent-dag-vs-react`](../agent-dag-vs-react/README.md)。

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

## 八、面试陷阱

### 陷阱 1：以为 Loop 就是"while True"

- **真相**：生产级 Loop 有 Max attempts、超时、Context 管理、Verifier、Harness 兜底

### 陷阱 2：以为 Loop 能解决所有问题

- **真相**：对于确定性流程，DAG 更合适；对于模糊探索性任务，Loop 更合适

### 陷阱 3：以为 LLM-as-Judge 是万能验证器

- **真相**：LLM 评估本身有偏差，关键验证必须用 ground-truth（测试、benchmark）

---

## 九、面试话术模板

> Loop Engineering 是 2026 年 AI 工程第四阶段，演进路径是 Prompt → Context → Harness → Loop。
>
> Loop 是"循环调用 Agent 直到任务完成"的模式，核心 3 大组件：
>
> 1. **任务定义**：可验证、可测试
> 2. **验证函数**：自动化、ground-truth
> 3. **反馈循环**：具体、可操作
>
> 4 大失败模式：无限循环、上下文爆炸、幻觉放大、资源耗尽。防护手段：Max attempts + 超时 + Context 重置 + cheaper 模型验证。
>
> 何时用 Loop vs DAG：模糊探索任务用 Loop，确定性流程用 DAG。复杂业务用 Loop + DAG 混合。
>
> 反直觉：Loop 的"重复"不是低效，是数据收集；信任 Agent 但 Verifier 兜底。

---

## 十、相关章节

- 同栏目：[`prompt-engineering`](../prompt-engineering/README.md) — Prompt Engineering
- 同栏目：[`context-engineering`](../context-engineering/README.md) — Context Engineering
- 同栏目：[`harness-engineering`](../harness-engineering/README.md) — Harness Engineering
- 同栏目：[`agent-dag-vs-react`](../agent-dag-vs-react/README.md) — DAG vs ReAct
- 主模块：[`11.ai/03-engineering`](../../../../11.ai/03-engineering/README.md) — AI 工程实践

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（2026 面试热点）