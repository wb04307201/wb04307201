<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/01-thinking-paradigm
  type: topic
  category: 思维范式
  summary: Prompt vs if-else —— 何时用 LLM、何时用规则的 4 维决策矩阵 + 反模式
-->

# 思维范式 · Prompt vs if-else

> **一句话**：**能用规则就别用 LLM**——LLM 是"柔性 if-else"，处理自然语言模糊性专用工具，不是通用计算器。决策公式：`ROI(LLM) ≥ 10 × ROI(rule)` 才上 LLM。

← [返回: 大模型思维工程](../README.md)

---

## 1. 决策矩阵：什么时候用 LLM？

| 场景特征 | 用规则 | 用 LLM | 原因 |
|---------|--------|--------|------|
| 输入是结构化数据 | ✅ | ❌ | if-else + 正则就够 |
| 规则可枚举（< 100 条）| ✅ | ❌ | 维护成本指数级 |
| 输入是自然语言（自由文本）| ❌ | ✅ | 规则难以覆盖所有变化 |
| 输出需要"理解语义" | ❌ | ✅ | LLM 唯一方案 |
| 调用频率 > 100 QPS | ✅ | ❌ | LLM 成本 + 延迟太高 |
| 答案需要可解释 | ✅ | ❌ | 黑盒输出难以审计 |
| 答案容许 5%+ 错误 | ❌ | ✅ | 规则只能做到 0% 或 100% |
| 答案需要 100% 准确 | ✅ | ❌ | LLM 幻觉不可消除 |

---

## 2. 4 维决策：何时 LLM 划算？

```text
                用 LLM 的 4 信号（满足 ≥ 3 个才上）：
                ┌─────────────────────────┐
                │ 1. 输入是非结构化（自然语言）│
                │ 2. 规则难以枚举（> 100 条） │
                │ 3. 答案容许一定错误（> 5%）│
                │ 4. ROI 比规则 ≥ 10x      │
                └─────────────────────────┘
                          ↓ 任一不满足
                用规则 + LLM 兜底（如分类先规则后 LLM）
```

### 2.1 信号 1：输入是非结构化

```python
# 规则友好：手机号格式校验
def is_phone(s):
    return re.match(r"^1[3-9]\d{9}$", s) is not None

# LLM 友好：用户意图"我想退款，怎么办？"
def is_refund_intent(query):
    prompt = "判断下面用户问题是否涉及退款意图，只回答 yes/no：[...]"
    return llm.invoke(prompt) == "yes"
```

### 2.2 信号 2：规则难以枚举

```python
# 规则友好：金额精度校验（< 0.01 报错）
amount.is_integer_multiple_of_cents()

# LLM 友好：客服问答（几千种问题类型）
#   "我的订单什么时候到？" ← 物流
#   "能便宜点吗？"     ← 议价
#   "怎么退货？"       ← 售后
#   "发票怎么开？"     ← 财务
#   ... 无法穷举
```

### 2.3 信号 3：答案容许 5%+ 错误

**绝对不能 LLM**的场景：
- 银行转账金额
- 医疗诊断结论
- 密码验证
- API 参数校验

**可以用 LLM**的场景：
- 客服对话
- 内容摘要
- 营销文案生成
- 代码 review（人 review 仍兜底）

### 2.4 信号 4：ROI 比规则 ≥ 10x

```text
LLM 成本：0.01 元/次 × 100 QPS × 86400 秒 = 86,400 元/天
规则成本：开发 1 周 + 0 元/次 = 16,000 元（一次性）

LLM 上限：2 天的开发 ROI 就打平
超过 2 天 → 用规则
```

---

## 3. LLM + 规则协同模式

### 3.1 规则优先 + LLM 兜底

```python
def handle_query(query):
    # Step 1：规则高频场景
    if rule_engine.match(query):
        return rule_engine.execute(query)  # 5ms
    
    # Step 2：LLM 处理长尾
    return llm.invoke(query)  # 500ms
```

**优点**：80% 请求 5ms 完成，20% 走 LLM
**适用**：客服高频 5-10 类意图 + 长尾小众意图

### 3.2 LLM 优先 + 规则校验

```python
def handle_query(query):
    # Step 1：LLM 生成
    answer = llm.invoke(query)
    
    # Step 2：规则校验输出安全
    if contains_pii(answer):  # PII 规则
        answer = mask_pii(answer)
    if is_banned(answer):     # 违规词规则
        return fallback()
    if len(answer) > 2000:    # 长度规则
        answer = summarize(answer)
    
    return answer
```

**适用**：内容生成、文案、报告

### 3.3 规则熔断 + LLM 兜底

```python
def handle_query(query):
    try:
        result = rule_engine.match(query)
        if result.confidence > 0.9:
            return result.answer
    except Exception:
        pass
    
    # 兜底 LLM
    return llm.invoke(query)
```

---

## 4. 反模式 · 5 个常见错

### ⚠️ 反模式 1：所有逻辑都用 LLM

- 错：金额校验、电话校验、UUID 校验全 LLM
- 对：这些是结构化校验，if-else 5ms

### ⚠️ 反模式 2：用户说"我想要退款"都过 LLM

- 错：100% 请求都过 LLM
- 对：高频意图规则处理，长尾才 LLM

### ⚠️ 反模式 3：LLM 当"万能函数"

- 错："用 LLM 算 1+1+...+10000"
- 对：这是数学，用 Python 1ms

### ⚠️ 反模式 4：忽视决定性场景用 LLM

- 错：银行转账 / 医疗诊断用 LLM
- 对：100% 用规则 + 审计

### ⚠️ 反模式 5：用 LLM 做"硬编码的逻辑分支"

- 错："如果用户等级 = VIP，走 A 路径；否则走 B 路径"
- 对：if-elif-else 1ms 完成

---

## 5. 实操决策脚本

```python
def should_use_llm(input_text, expected_qps, accuracy_required):
    # 信号 1：是否自然语言
    is_natural_language = not is_structured(input_text)
    
    # 信号 2：规则复杂度
    rule_complexity = estimate_rules(input_text)
    
    # 信号 3：容错率
    error_tolerance = 1 - accuracy_required
    
    # 信号 4：ROI
    annual_llm_cost = qps_to_annual_cost(expected_qps)
    rule_dev_cost = rule_complexity * dev_days * 1000
    
    if not is_natural_language:
        return False
    if rule_complexity < 50:
        return False
    if error_tolerance < 0.01:
        return False
    if annual_llm_cost > rule_dev_cost * 10:
        return False
    
    return True
```

---

## 6. 一句话总结

> **Prompt vs if-else：能用规则就别用 LLM（成本 × 5、错误率 × 0）。LLM 是处理自然语言模糊性的专业工具，不是 if-else 的替代品。决策公式：4 信号满足 ≥ 3 个才上 LLM。**

---

← [返回: 大模型思维工程](../README.md) · 下一章：[02-cost-control](02-cost-control-and-degradation.md)
