<!--
module:
  parent: ai/loop-engineering
  slug: ai/loop-engineering/verifier-design
  type: topic
  category: 验证器设计
  summary: Verifier（验证器）5 大设计 —— 测试 / 类型检查 / lint / 编译 / 运行时 5 大客观反馈源 + 评分函数
-->

# Verifier 设计 · 5 大客观验证源

> **一句话**：Auto-Fix Loop 的灵魂是 **Verifier（验证器）**——Agent 改完后必须能"客观判断 pass/fail"。5 大客观源（测试/类型/lint/编译/运行时） + 评分函数设计。

← [返回: Loop Engineering 总目录](../README.md)

---

## 1. 5 大 Verifier 类型

| 类型 | 工具 | 信号 | 客观程度 |
|------|------|------|---------|
| **测试** | Jest / pytest / JUnit / Go test | pass / fail | ⭐⭐⭐⭐⭐ |
| **类型检查** | TypeScript / mypy / Pyright | 类型错误数 = 0 | ⭐⭐⭐⭐⭐ |
| **lint** | ESLint / Pylint / golangci-lint | violation 数 | ⭐⭐⭐⭐ |
| **编译** | tsc / gcc / javac | exit code 0 | ⭐⭐⭐⭐⭐ |
| **运行时** | runtime test / e2e | 输出/异常 | ⭐⭐⭐ |

---

## 2. 测试 Verifier（最重要的客观源）

### 2.1 单元测试用例示例

```python
# tests/test_user_login.py
import pytest
from app.auth import login

def test_login_success():
    user = login("alice", "password123")
    assert user.id == 1

def test_login_invalid_password():
    with pytest.raises(InvalidPassword):
        login("alice", "wrong")
```

### 2.2 测试驱动修复循环

```python
def fix_until_tests_pass(code, tests):
    for attempt in range(5):
        result = run_tests(code, tests)
        if result.passed:
            return code, "success"
        # 给 Agent 详细错误
        prompt = f"""测试 {result.passed}/{result.total}：

失败的测试：
{format_failures(result.failures)}

请修改代码以通过测试：
{code}
"""
        code = agent.invoke(prompt)
    return code, "max_attempts"
```

**关键设计**：失败的测试信息**结构化**（测试名 + 期望 + 实际 + trace），不只传异常文本。

### 2.3 反模式：测试本身有 bug

```python
# 错：测试期望值错误，Agent 永远修不对
def test_login():
    user = login("alice", "password123")
    assert user.id == 999  # 错误的期望！
```

**修复**：Verifying the Verifier（测试本身要正确）—— 用 mutation testing 或已知 good case 测试。

---

## 3. 类型检查 Verifier

### 3.1 TypeScript 实战

```python
def check_types(code):
    result = subprocess.run(
        ['npx', 'tsc', '--noEmit'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return VerifierResult(passed=True)
    # 错误格式化为可读
    errors = parse_tsc_errors(result.stdout)
    return VerifierResult(passed=False, errors=errors)
```

### 3.2 Python 实战

```python
def check_types(code):
    result = subprocess.run(
        ['mypy', '--strict', '.'], capture_output=True
    )
    return result.returncode == 0
```

**优势**：类型检查是**编译期错误**，不需要运行，比测试快。

---

## 4. Lint Verifier（完全自动）

```python
def fix_lint(code):
    """无需 Agent 介入"""
    result = subprocess.run(
        ['eslint', '--fix', 'src/'],
        capture_output=True
    )
    return {'code': read('src/'), 'remaining': parse_lint(result.stdout)}
```

**实战配置**：pre-commit hook + ESLint auto-fix + Prettier——零 Agent 介入。

---

## 5. 编译 Verifier（绝对客观）

```python
def check_compile(code):
    result = subprocess.run(
        ['gcc', '-o', 'main', 'main.c', '-Wall'],
        capture_output=True
    )
    return {
        'passed': result.returncode == 0,
        'stderr': result.stderr.decode()
    }
```

**优势**：二进制成功/失败是最客观的信号。

---

## 6. 运行时 Verifier（最复杂）

```python
def check_runtime(code, test_input):
    """执行代码 + 捕获异常"""
    try:
        result = subprocess.run(
            ['python', '-c', code],
            input=test_input,
            capture_output=True,
            timeout=5,  # 防止 hang
        )
        return {
            'passed': result.returncode == 0,
            'stdout': result.stdout.decode(),
            'stderr': result.stderr.decode(),
        }
    except subprocess.TimeoutExpired:
        return {'passed': False, 'error': 'timeout'}
```

**关键**：超时保护（防止 Agent 死循环卡住整个 Verifier）。

---

## 7. 复合 Verifier 设计

```python
class CompositeVerifier:
    """组合多个 Verifier 形成评分"""
    def __init__(self, verifiers, weights):
        self.verifiers = verifiers  # List[Verifier]
        self.weights = weights      # List[float]
    
    def check(self, code):
        results = []
        for v, w in zip(self.verifiers, self.weights):
            r = v.check(code)
            results.append((r.passed, w))
        score = sum(p * w for p, w in results) / sum(self.weights)
        return score >= 0.8  # 80% 通过算过
```

**实战配置**：
- 测试 (50%) + 类型检查 (30%) + lint (20%)
- 通过 = score >= 0.9（严苛）or >= 0.7（宽松）

---

## 8. 评分函数 vs 通过判定

```python
# 二值（pass/fail）
def check(code):
    return all_tests_pass(code)

# 评分（精细）
def score(code):
    s = 0.0
    s += 0.5 * test_pass_rate(code)        # 50%
    s += 0.3 * (1 - type_error_rate(code)) # 30%
    s += 0.2 * (1 - lint_error_rate(code))  # 20%
    return s
```

**实战**：
- 研发阶段：评分函数（容忍个别失败）
- 上线前：二值（必须全过）

---

## 9. 反模式 · 5 个常见错

### ⚠️ 反模式 1：单 Verifier（仅 1 个）

- 错：只用"测试通过"作为信号
- 对：5 大 Verifier 组合，分数 ≥ 阈值

### ⚠️ 反模式 2：测试本身有 bug

- 错：测试期望写错，Agent 永远修不对
- 对：测试也要被验证（mutation testing）

### ⚠️ 反模式 3：没有超时保护

- 错：Agent 写死循环代码 → Verifier hang
- 对：subprocess timeout + watchdog

### ⚠️ 反模式 4：太严格的阈值

- 错：必须 100% 测试通过
- 对：阈值 70-90%，允许少量失败

### ⚠️ 反模式 5：不给 Agent 详细错误

- 错：只传 "Test failed"
- 对：传测试名 + 期望 + 实际 + stack trace

---

## 10. 一句话总结

> **Verifier = Agent 改完后的客观"判官"——5 大源（测试/类型/lint/编译/运行时）+ 复合评分 + 详细错误反馈。Auto-Fix Loop 没有 Verifier 就是盲改。**

---

← [返回: Loop Engineering 总目录](../README.md) · 上一章：[auto-fix-strategy](auto-fix-strategy.md) · 下一章：[ide-case-studies](ide-case-studies.md)
