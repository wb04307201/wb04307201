<!--
module:
  parent: ai/loop-engineering
  slug: ai/loop-engineering/auto-fix-strategy
  type: topic
  category: 修复策略
  summary: Auto-Fix Loop 5 种修复策略 —— 按错误类型（语法/类型/lint/测试/运行时）选择修复路径 + 重试预算 + 终止条件
-->

# Auto-Fix 修复策略 · 5 种按错误类型

> **一句话**：Auto-Fix 不是"错了就改"——**按错误类型选择策略**（语法 vs 类型 vs 测试 vs 运行时），让 Agent 拿到**针对性 prompt + 特定上下文**，避免在错误方向上循环。

← [返回: Loop Engineering 总目录](../README.md)

---

## 1. 错误分类 → 5 种修复策略

| 错误类型 | 现象 | 修复策略 | Verifier | 终止条件 |
|---------|------|---------|---------|---------|
| **语法错误** | 编译报错 | parse → 修复一行 → 重编译 | 编译器 | 编译通过 |
| **类型错误** | typecheck fail | 重读类型 → 修复 → recheck | TypeScript / mypy | 类型检查过 |
| **lint 错误** | 风格违规 | 自动修复（eslint --fix）| lint | 0 violation |
| **测试失败** | 单测 fail | 重读错误 → 修代码 → rerun | Jest / pytest / JUnit | 全过 |
| **运行时错误** | crash / 异常 | 重读 stack trace → 修 | 日志 + 测试 | 跑通 |

---

## 2. 5 大策略详解

### 2.1 策略 1：语法错误 → 编译反馈循环

```python
def fix_syntax(code):
    for attempt in range(3):
        try:
            compile(code)  # Python
            return code
        except SyntaxError as e:
            # 把错误位置 + 信息返回给 Agent
            fix_prompt = f"代码在第 {e.lineno} 行语法错误：{e.msg}\n请修复：\n{code}"
            code = agent.invoke(fix_prompt)
    raise MaxAttemptsExceededError()
```

**适用**：明显语法错误（括号 / 分号 / 缩进）

### 2.2 策略 2：类型错误 → typecheck 反馈循环

```python
def fix_types(code):
    for attempt in range(3):
        errors = run_typecheck(code)  # tsc / mypy
        if not errors:
            return code
        # 把所有类型错误一次性喂给 Agent
        fix_prompt = f"""代码类型错误：

{format_errors(errors)}

请一次性修复所有错误：
{code}
"""
        code = agent.invoke(fix_prompt)
    raise MaxAttemptsExceededError()
```

**关键**：**一次性给所有错误**，避免 Agent 修复一个引入新错误。

### 2.3 策略 3：lint 错误 → 自动修复循环

```python
def fix_lint(code):
    # 大多数 lint 可自动修复（prettier / eslint --fix）
    fixed = run_auto_fix(code)
    return fixed
```

**关键**：Agent 不必介入，让工具做。

### 2.4 策略 4：测试失败 → 重读错误循环

```python
def fix_tests(code, tests):
    for attempt in range(5):
        result = run_tests(code, tests)
        if result.passed:
            return code
        # 关键：把"失败测试名 + 期望值 + 实际值 + stack trace"都给 Agent
        fix_prompt = f"""测试失败 ({attempt+1}/5):

失败测试：{result.failed_tests}
期望：{result.expected}
实际：{result.actual}
Stack trace：{result.stack_trace}

请分析失败原因，修复代码：
{code}
"""
        code = agent.invoke(fix_prompt)
    raise MaxAttemptsExceededError()
```

**关键**：详细的 error context 让 Agent 能定位问题。

### 2.5 策略 5：运行时错误 → 日志 + 重跑

```python
def fix_runtime(code, test_input):
    for attempt in range(5):
        result = run_with_logging(code, test_input)
        if result.exit_code == 0:
            return code
        # 关键：把崩溃日志（前 200 行 + stack trace）给 Agent
        fix_prompt = f"""运行崩溃：

异常：{result.exception}
Stack：{result.stack[:2000]}
最后 5 条日志：{result.logs[-5:]}

请修复后重试：
{code}
"""
        code = agent.invoke(fix_prompt)
    raise MaxAttemptsExceededError()
```

---

## 3. 5 大策略对比

| 策略 | 自动化程度 | Agent 介入 | 平均修复轮次 |
|------|----------|----------|------------|
| 1 语法 | 部分自动 | 重写一行 | 1-2 轮 |
| 2 类型 | 部分自动 | 重写类型 | 1-3 轮 |
| 3 lint | **完全自动** | ❌ | 0 轮 |
| 4 测试 | Agent 主导 | 重写代码 | 3-5 轮 |
| 5 运行 | Agent 主导 | 重写代码 | 5-10 轮 |

**实战 80%**：策略 1（语法）+ 策略 4（测试）能覆盖 80% 场景。

---

## 4. 重试预算控制

```python
class RetryBudget:
    """防止无限循环"""
    def __init__(self, max_per_strategy=5, max_total=15):
        self.max_per_strategy = max_per_strategy
        self.max_total = max_total
        self.total_attempts = 0
    
    def can_retry(self, strategy):
        if self.total_attempts >= self.max_total:
            return False
        strategy.attempts += 1
        self.total_attempts += 1
        return strategy.attempts <= self.max_per_strategy
```

**实战预算**：
- 单策略 ≤ 5 次
- 总计 ≤ 15 次
- 超限 → 转人工 / 升级

---

## 5. 反模式 · 5 个常见错

### ⚠️ 反模式 1：所有错误用同一 Prompt

- 错：所有错误都用相同 prompt
- 对：按错误类型分类用针对性 prompt

### ⚠️ 反模式 2：不传上下文只传错误消息

- 错：`fix this error: TypeError: x is not a function`
- 对：传代码 + 错误 + 完整 stack + 相关上下文

### ⚠️ 反模式 3：失败立刻转人工

- 错：1 次失败就升级
- 对：累计 3-5 次同类失败才升级

### ⚠️ 反模式 4：忽略终止条件

- 错：Agent 无限循环
- 对：硬上限（5 次 / 策略 / 15 次 / 总）

### ⚠️ 反模式 5：丢失上下文

- 错：第 N 次循环丢掉历史错误
- 对：所有错误历史写入 Context（避免重复失败）

---

## 6. 一句话总结

> **Auto-Fix Loop 5 策略：语法 / 类型 / lint / 测试 / 运行时——按错误类型选针对性 Prompt + Verifier + 重试预算 + 终止条件。80% 场景覆盖在策略 1（语法）+ 策略 4（测试）。**

---

← [返回: Loop Engineering 总目录](../README.md) · 下一章：[verifier-design](verifier-design.md)
