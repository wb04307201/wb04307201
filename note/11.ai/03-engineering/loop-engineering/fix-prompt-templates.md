<!--
module:
  parent: ai/loop-engineering
  slug: ai/loop-engineering/fix-prompt-templates
  type: topic
  category: 修复 prompt 模板
  summary: 修复 prompt 模板 4 类（语法/类型/测试/运行时）+ 通用结构 + 实战示例
-->

# 修复 Prompt 模板 · 4 类常用模板

> **一句话**：修复 prompt 不能只传错误信息——必须含 **任务背景 + 当前代码 + 错误详情 + 上次尝试 + 修复建议** 5 要素，让 Agent 一次到位。

← [返回: Loop Engineering 总目录](../README.md)

---

## 1. 修复 prompt 5 大要素

```python
fix_prompt = f"""
[任务背景] {task_description}

[当前代码] {code}

[错误详情]
{error_message}
{stack_trace}
{test_failures}

[上次尝试] {previous_attempt}      # 防止重复失败
[失败原因] {why_failed}

[约束]
- 只能修改必要部分
- 保持原有架构
- 不要破坏现有测试

请输出修复后的完整代码。
"""
```

**5 要素**：任务 + 代码 + 错误 + 历史 + 约束

---

## 2. 4 类常见错误的 prompt 模板

### 2.1 语法错误

```python
SYNTAX_FIX_PROMPT = """
代码位置：第 {lineno} 行
错误信息：{error_msg}

当前代码：
```{lang}
{code}
```text

请修复语法错误，保持代码逻辑不变。

注意：
- 完整保留代码结构和命名
- 只修复 {lineno} 行附近的错误
- 检查括号 / 分号 / 缩进

输出完整代码（不要只输出修复部分）。
"""
```

### 2.2 类型错误

```python
TYPE_FIX_PROMPT = """
类型错误（{lang}）：

错误文件：{file}:{line}
错误信息：{error}

当前代码：
```{lang}
{code}
```text

类型签名：
{type_signature}

请修复类型错误：
- 保证类型正确（TypeScript strict mode）
- 不要用 any / unknown 绕过
- 必要时添加类型守卫

输出完整修复后的代码。
"""
```

### 2.3 测试失败

```python
TEST_FIX_PROMPT = """
测试失败：

失败测试：{test_name}
期望值：{expected}
实际值：{actual}
Stack trace：
{stack}

被测试的函数：
```{lang}
{function_code}
```text

测试代码：
```{lang}
{test_code}
```text

请：
1. 分析失败原因（不是机械改，而是理解）
2. 修改函数 / 测试（优先改函数）
3. 不要只让测试通过——保持语义正确

输出修改后的代码。
"""
```

### 2.4 运行时崩溃

```python
RUNTIME_FIX_PROMPT = """
运行崩溃：

输入：{input}
异常类型：{exception}
Stack trace：
{stack[:2000]}

最后 10 条日志：
{logs[-10:]}

当前代码：
```{lang}
{code}
```text

环境信息：{env_info}

请：
1. 分析崩溃根因
2. 修复代码（处理边界情况）
3. 加 unit test 覆盖此次崩溃场景

输出完整修复代码 + 测试代码。
"""
```

---

## 3. 通用结构模板

```python
GENERIC_FIX_TEMPLATE = """
## 任务
{task}

## 当前状态
{current_state}

## 错误信息
{error}

## 历史尝试
{previous_attempts}

## 约束
- 不能修改测试
- 保持向后兼容
- 性能不能下降

## 输出格式
请输出：
1. 分析（20 行内）
2. 修改后的完整代码
3. 验证方法（如何测）
"""
```

---

## 4. 实战示例：Python 修复 prompt

```python
# Agent 失败的 python 修复任务
fix_prompt = """
## 任务
实现 calculate_discount 函数，根据订单金额和会员等级返回折扣价。

## 当前代码
```python
def calculate_discount(amount, member_level):
    if amount > 1000:
        return amount * 0.9
    return amount * 0.95
```text

## 测试失败

test_calculate_discount_silver_member：
  期望：amount=2000, level='silver' → 1900
  实际：1900 ✅

test_calculate_discount_gold_member：
  期望：amount=2000, level='gold' → 1800  
  实际：1900 ❌  # ← 测试失败

## 分析
会员等级 'gold' 应该享受更高的折扣（90%），目前代码没考虑等级。

## 修复要求
- 'gold' 等级享受 80% 折扣
- 'silver' 保持 90%
- 'normal' 保持 95%
- < 1000 元的订单不享受折扣

输出完整修复后的代码。
"""
```

---

## 5. 5 大设计原则

### 5.1 原则 1：具体 > 抽象

```text
❌ "请修复代码"
✅ "第 13 行的 TypeError: x is not a function，请改用 .call()"
```

### 5.2 原则 2：完整 > 部分

```text
❌ 只传错误信息
✅ 错误 + 代码 + 测试 + 历史尝试 + 约束
```

### 5.3 原则 3：结构化 > 自由文本

```text
❌ "测试失败了"
✅ "test_calculate_discount 失败：expected 1900, actual 1800, at line 42"
```

### 5.4 原则 4：上下文 > 凭空

```text
❌ 让 Agent 凭空修复
✅ 提供代码 + 错误 + 上次尝试 + 历史
```

### 5.5 原则 5：反馈 > 命令

```text
❌ "修复这个 bug"
✅ "分析失败原因 + 修改代码 + 验证通过"
```

---

## 6. 实战技巧

### 6.1 技巧 1：失败历史

```python
PREVIOUS_ATTEMPTS_PROMPT = """
之前的尝试：
{chr(10).join([
  f'尝试 {i+1}：{attempt["code_diff"]}, 错误：{attempt["error"]}'
  for i, attempt in enumerate(history)
])}

请不要重复同样的失败模式。
"""
```

### 6.2 技巧 2：错误归类

```python
ERROR_CATEGORIZATION_PROMPT = """
请先分析错误类型：
- 语法错误 → 参考语法修复模板
- 类型错误 → 参考类型修复模板
- 测试失败 → 参考测试修复模板
- 运行时错误 → 参考运行时修复模板

然后选择对应的修复策略。
"""
```

### 6.3 技巧 3：限定范围

```python
SCOPED_FIX_PROMPT = """
【严格约束】
- 只能修改 {file} 文件
- 不能修改测试
- 不能 import 新包
- 不能修改公共 API
- 不能添加新依赖
"""
```

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：只传错误信息

```text
❌ "fix this: TypeError: x is not a function"
✅ 完整 prompt（任务+代码+错误+上下文）
```

### ⚠️ 反模式 2：让 Agent 凭空修复

```text
❌ "请修复登录 bug"
✅ "测试 test_login 失败，错误信息... 代码..."
```

### ⚠️ 反模式 3：不传上次尝试

```text
❌ Agent 第 5 次还尝试同样错误的方法
✅ 传 previous_attempts 让 Agent 不要重复
```

### ⚠️ 反模式 4：不限定范围

```text
❌ Agent 修改了测试代码蒙混过关
✅ 限制"不能修改测试"
```

### ⚠️ 反模式 5：缺口化修复

```text
❌ 只让测试通过（不管代码质量）
✅ 要求"语义正确，不只是为了过测"
```

---

## 8. 一句话总结

> **修复 prompt 模板 5 要素：任务 + 当前代码 + 错误详情 + 历史尝试 + 约束。4 类模板（语法/类型/测试/运行时）+ 5 大原则（具体/完整/结构化/上下文/反馈）= Agent 一次到位修复率 +50%。**

---

← [返回: Loop Engineering 总目录](../README.md) · 上一章：[ide-case-studies](ide-case-studies.md) · 专题结束
