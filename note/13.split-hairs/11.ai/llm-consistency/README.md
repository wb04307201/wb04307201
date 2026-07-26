<!--
question:
  id: 11.ai-llm-consistency
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 一致性, Self-Consistency, 投票, Production]
-->

# 模型连续 3 次给出不一致的结果 —— Self-Consistency 投票

> 一句话定位：raw 重试不解决一致性问题——LLM 是概率模型，3 次重试可能都错。完整深度见 [主模块 · 不一致与失败处理](../../../11.ai/08-llmops/production-stability/03-consistency-and-failure-handling.md)。

> **系列定位**：AI 生产工程面试题（Anthropic / OpenAI 高频）。考察的是**Self-Consistency 投票 + Judge 模型 + 重试预算**的协同方案。

---

## 引子：客服问"北京人口"，3 次返回 2000/3000/5000 万

```text
场景：AI 客服上线 2 周——
- 用户反馈"AI 一问三不知"
- 同一问题 3 次调用，返回 3 个不同答案
- 工程师 A："多试几次就对了"（raw 重试陷阱）
- 工程师 B："需要语义投票，不是字符串匹配"
- CTO：限你 3 天解决一致性问题
```

普通候选人会答"重试 3 次就好"——踩中"**raw 重试幻觉、缺 Judge 模型、缺重试预算分级**" 3 大雷区。
高分候选人会答：**Self-Consistency 多采样 + Judge 语义投票 + 分级重试预算**。

---

## 一、核心原理

### 1.1 Self-Consistency 投票

```python
samples = [llm.invoke(query, temperature=0.7) for _ in range(5)]
# Judge 模型选最佳（不是字符串投票，是语义投票）
best = judge_llm.choose_best(query, samples)
```

### 1.2 重试预算分级

| 失败类型 | 重试次数 | 策略 |
|----------|----------|------|
| 网络错误 | 3 次 | 指数退避 |
| 限流 | 5 次 | 退避 |
| 校验失败 | 2 次 | 重新生成 + format hint |
| 一致性 | 3 次 | 采样数，不是重试数 |

### 1.3 失败模式对应方案

- **幻觉** → Self-Consistency
- **格式错** → Output Parser + 重试 with format hint
- **超时** → 双 timeout + 降级
- **成本爆炸** → 3 道 quota 强制

---

## 二、面试话术（60 秒版本）

**题目：如果模型连续 3 次给出不一致的结果，系统如何反应？**

**高分答案**（60 秒）：

```text
"raw 重试不解决一致性问题——LLM 是概率模型，3 次重试可能都错。

正解：Self-Consistency 投票 + Judge 模型 + 重试预算。

Self-Consistency：
- 多采样（5-7 次）
- 用 Judge 模型（GPT-4 或业务 fine-tune）选最佳
- 离散答案可字符串投票，开放回答必须语义投票

重试预算：
- 网络错误：3 次（指数退避）
- 限流：5 次（退避）
- 校验失败：2 次（重新生成）
- 一致性：3 次（这是采样数，不是重试数）

失败模式：
- 幻觉 → Self-Consistency
- 格式错 → Output Parser + 重试 with format hint
- 超时 → 双 timeout + 降级
- 成本爆炸 → 3 道 quota 强制"
```

---

## 三、常见陷阱

### 陷阱：raw 重试

- **错误**：3 次失败重试 3 次，认为会好
- **真相**：LLM 是概率模型，幻觉重试还是幻觉
- **代价**：浪费 3x 成本，答案还是错

---

## 四、面试反问

```text
Q1：贵司对答案准确性的要求？
    → 金融/医疗用 5 投票；一般用 Self-Consistency 即可
Q2：贵司是否有回归测试流程？
    → 黄金集 + 漂移检测必须有
```

---

## 五、相关章节

- [主模块 · 不一致与失败处理](../../../11.ai/08-llmops/production-stability/03-consistency-and-failure-handling.md) —— 深度内容
- [主模块 · llm-production-thinking 总目录](../../../11.ai/08-llmops/production-stability/README.md)
- [Temperature=0 误区](../temperature-zero-myth/README.md) —— 相关的一致性根因分析

---

> 📅 2026-07-26 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · Self-Consistency 投票 · 含 60 秒话术 + 反模式

← [返回: 咬文嚼字 · 11.ai](../README.md)
