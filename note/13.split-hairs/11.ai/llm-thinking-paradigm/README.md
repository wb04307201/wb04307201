<!--
question:
  id: 11.ai-llm-thinking-paradigm
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 思维范式, Prompt, if-else, Production]
-->

# Prompt 可能不如 if-else —— 大模型思维范式如何养成

> 一句话定位：LLM 不是万能解——能用规则就别用 LLM（5ms if-else 变 500ms + $0.01）。完整深度见 [主模块 · 思维范式](../../../11.ai/08-llmops/production-stability/01-thinking-paradigm.md)。

> **系列定位**：AI 生产工程面试题（字节 / 阿里高频）。考察的不是"Prompt 怎么写"，而是**何时该用 LLM、何时用规则**的思维范式。

---

## 引子：产品同事把"金额校验"都丢给 LLM

```text
场景：某 AI 公司上线 AI 客服——
- 金额校验：if-else 5ms，LLM 500ms + $0.01 + 5% 错误率
- 电话校验：正则 1ms，LLM 500ms + $0.01
- UUID 生成：确定性 0ms，LLM 可能生成无效 UUID
```

普通候选人会答"Prompt 写得更好就行"——踩中"**LLM 万能、忽视成本、缺协同**" 3 大雷区。
高分候选人会答：**4 信号决策（满足 ≥ 3 个才上 LLM）+ 规则优先 / LLM 兜底 + 80/20 协同模式**。

---

## 一、核心原理

### 1.1 LLM 是"柔性 if-else"

LLM 是处理自然语言模糊性专用工具，不是通用计算器。核心判断标准：

```text
用 LLM 的 4 信号（满足 ≥ 3 个才上）：
1. 输入是非结构化（自然语言）
2. 规则难以枚举（> 100 条）
3. 答案容许一定错误（> 5%）
4. ROI 比规则 ≥ 10x
任一不满足 → 规则优先 / LLM 兜底
```

### 1.2 思维范式对比

| 场景 | 方案 | 延迟 | 成本 | 错误率 |
|------|------|------|------|--------|
| 金额校验 | if-else | 5ms | $0 | 0% |
| 金额校验 | LLM | 500ms | $0.01 | 5% |
| 电话校验 | 正则 | 1ms | $0 | 0% |
| 语义理解 | LLM | 500ms | $0.01 | 3% |
| 语义理解 | 规则 | 不可行 | - | - |

---

## 二、面试话术（60 秒版本）

**题目：Prompt 可能不如 if-else……大模型思维工程如何养成？**

**高分答案**（4 层递进，60-90 秒）：

```text
1. 思维转换（15 秒）：
   "LLM 是'柔性 if-else'——处理自然语言模糊性专用工具，
   不是通用计算器。能用规则就别用 LLM（成本 × 5、错误率 × 0）。"

2. 4 信号决策（30 秒）：
   "决定用不用 LLM，看 4 个信号：
   - 输入是非结构化？规则可枚举？错误容许？ROI ≥ 10x？
   满足 ≥ 3 个才上 LLM。任何一项不满足都用规则。"

3. 协同模式（25 秒）：
   "生产实操：80% 规则处理高频场景（5ms），20% LLM 处理长尾（500ms）；
   LLM 生成后规则做合规校验（PII / 违规词 / 长度）。
   工程师必须养成的肌肉记忆。"

4. 反问（10 秒）：
   "贵司 LLM 接 API 还是自部署？通用场景还是专业领域？
   这决定 4 信号的具体阈值。"
```

---

## 三、常见陷阱

### 陷阱：思维错位（LLM 万能）

- **错误**：所有逻辑都用 LLM（金额校验、电话校验、UUID）
- **真相**：结构化校验 if-else 5ms，LLM 500ms + $0.01
- **代价**：成本 × 5，错误率从 0% 涨到 5%

---

## 四、相关章节

- [主模块 · 思维范式](../../../11.ai/08-llmops/production-stability/01-thinking-paradigm.md) —— 深度内容
- [主模块 · llm-production-thinking 总目录](../../../11.ai/08-llmops/production-stability/README.md)
- [主模块 · 成本 5 层路由](../../../11.ai/08-llmops/production-stability/02-cost-control-and-degradation.md)
- [主模块 · 决策树](../../../11.ai/08-llmops/production-stability/06-decision-tree.md)
- [12.story · 05-observability](../../../12.story/05-observability.md) —— 阿明餐厅的 5 问实战

---

> 📅 2026-07-26 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 思维范式 · 含 60 秒话术 + 反模式

← [返回: 咬文嚼字 · 11.ai](../README.md)
