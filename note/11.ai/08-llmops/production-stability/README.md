<!--
module:
  parent: ai/08-llmops
  slug: ai/llmops/production-stability
  type: deep-dive
  category: 大模型生产工程
  summary: 大模型思维工程 5 个灵魂拷问——Prompt vs if-else / 成本降级 / 不一致处理 / 超时熔断 / 线上监控与定位
-->

# 大模型思维工程 · 5 个灵魂拷问

> **一句话答案**：LLM 生产稳定性不是"Prompt 写得更好"那么简单——而是**5 大工程问题的协同回答**：①Prompt vs if-else 思维转换 ②成本上限与自动降级 ③连续不一致的多结果投票 ④超时熔断 ⑤线上监控与快速定位。

## 反向链

- [builtin-loop-commands](../../03-engineering/loop-engineering/builtin-loop-commands.md)

← [返回: LLMOps](../README.md) · 同级：[llm-evaluation](../04-llm-evaluation/README.md) · [llmops-stack](../02-llmops-stack/README.md)

---

## 5 个灵魂拷问（程序员学大模型的第一个坎）
```text
Q1：Prompt 可能不如 if-else … 大模型思维工程到底如何养成？
Q2：模型调用的成本上限是多少？超了如何自动降级？
Q3：如果模型连续 3 次给出不一致的结果，你的系统如何反应？
Q4：等不及模型思考，你的系统有没有超时熔断？
Q5：上线后，怎么检测模型的准确率？幻觉率？怎么快速定位问题？
```

这 5 个问题不是"写好 Prompt"能解决的——是 **LLM Production Engineering** 的全部。每一个都对应一个工程章节。

---

## 5 大问题全景
| # | 问题 | 工程领域 | 一行答案 |
|---|------|---------|---------|
| **Q1** | Prompt vs if-else | 思维范式 | **能用规则就别用 LLM**——LLM 是"柔性 if-else"，不是万能解 |
| **Q2** | 成本上限 + 降级 | 成本工程 | **硬上限 + 自动切换模型（小→大→兜底文本）**——5 层路由 |
| **Q3** | 连续 3 次不一致 | 可靠性 | **多结果投票 + Judge 模型 + 重试预算**——Self-Consistency + Self-Reflection |
| **Q4** | 超时熔断 | 可用性 | **双 timeout + Circuit Breaker + Fallback 模型**——Netflix Hystrix 模式 |
| **Q5** | 线上监控 + 定位 | 可观测性 | **Trace（链路追踪）+ 黄金集回归 + 漂移检测**——Langfuse / Helicone |

---

## 子章节导航
| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [思维范式](01-thinking-paradigm.md) | Prompt 可能不如 if-else —— 何时该用 LLM、何时用规则？ |
| 02 | [成本上限与降级](02-cost-control-and-degradation.md) | 单请求成本上限怎么定？超了怎么 5 层降级？ |
| 03 | [不一致与失败处理](03-consistency-and-failure-handling.md) | 连续 3 次不一致怎么办？多结果投票 + 重试预算？ |
| 04 | [超时熔断](04-timeout-and-circuit-breaker.md) | LLM 慢响应 / 不响应如何熔断？Fallback 引擎？ |
| 05 | [线上监控与定位](05-online-monitoring.md) | 准确率 / 幻觉率怎么监控？漂移检测 + Trace 定位？ |
| 06 | [决策树](06-decision-tree.md) | 5 大问题场景化决策树 + checklist |

---

## 反直觉点
- ⚠️ **"Prompt 万能"是错觉** —— 一个 if-else 5ms 完成的事，LLM 调 500ms + $0.01 + 5% 错误率 = **永远不划算**。LLM 是"处理自然语言模糊性"专用工具，不是通用计算器。
- ⚠️ **"重试就能解决一致性"是错觉** —— 模型本身有随机性（temperature > 0），3 次重试可能都是错。必须靠 **Self-Consistency + Judge 模型**才能挑出最佳。
- ⚠️ **"成本监控只算 token 钱"是错觉** —— 单次 LLM 调用的总成本 = token 费 + GPU 时间 + 排队 + 重试 + **风险成本**（幻觉导致客诉）。忽视风险成本是最常见的 OOM 推理。
- ⚠️ **"监控响应时间就够了"是错觉** —— LLM 监控必须是「**质量 + 延迟 + 成本 + 一致性**」4 维。延迟 OK 但答案错误是更严重的事故。

---

## 速查表
| 维度 | 一句话原则 |
|------|----------|
| 思维范式 | **能用 if-else 就别用 LLM**（对比 ROI ≥ 10x 用规则）|
| 成本降级 | **5 层路由**：cheap → small model → big model → SaaS fallback → human handoff |
| 一致性 | **Self-Consistency 投票 + Judge 模型**（拒绝 raw 重试）|
| 超时熔断 | **双 timeout**（5s 软限 + 30s 硬限）+ Circuit Breaker |
| 监控 | **Trace + 黄金集回归 + 漂移检测**（每月回归 + 实时漂移告警）|

---

## 一句话总结
```text
"LLM 生产工程 = 5 大问题协同：
- 思维范式：能用规则就别用 LLM（成本 × 5）
- 成本降级：5 层路由把成本上限限定在预期
- 不一致处理：投票 + Judge + 重试预算
- 超时熔断：双 timeout + 熔断器保系统可用
- 监控定位：Trace 串起来，黄金集回归常态化

任何一项弱，整个系统崩。"
```

---

## 速记卡：split-hairs 视角

> 本节为 split-hairs 迁出内容（2026-08-10），保留面试深挖价值（60 秒话术 + 反模式），避免与上方"Q3 5 大问题"重复。

### 60 秒面试话术（连续 3 次不一致）

> **题目**：如果模型连续 3 次给出不一致的结果，系统如何反应？

> **高分答案**（60 秒）：
>
> ```text
> raw 重试不解决一致性问题——LLM 是概率模型，3 次重试可能都错。
>
> 正解：Self-Consistency 投票 + Judge 模型 + 重试预算。
>
> Self-Consistency：
> - 多采样（5-7 次）
> - 用 Judge 模型（GPT-4 或业务 fine-tune）选最佳
> - 离散答案可字符串投票，开放回答必须语义投票
>
> 重试预算：
> - 网络错误：3 次（指数退避）
> - 限流：5 次（退避）
> - 校验失败：2 次（重新生成）
> - 一致性：3 次（这是采样数，不是重试数）
>
> 失败模式：
> - 幻觉 → Self-Consistency
> - 格式错 → Output Parser + 重试 with format hint
> - 超时 → 双 timeout + 降级
> - 成本爆炸 → 3 道 quota 强制
> ```

### 3 大反直觉陷阱（核心雷区）

| 陷阱 | 直觉以为 | 实际真相 | 代价 |
|------|---------|---------|------|
| **raw 重试幻觉** | "3 次失败重试 3 次会好" | LLM 是概率模型，幻觉重试**还是幻觉** | 浪费 3x 成本，答案还是错 |
| **缺 Judge 模型** | 字符串投票就够 | 离散答案可字符串投票；**开放回答必须语义投票**（用 LLM/LLM-as-Judge 选最佳） | 投票出来的答案质量差 |
| **缺重试预算分级** | 重试越多越好 | 重试必须**按失败类型分级**：网络错误 3 次、限流 5 次、校验失败 2 次、一致性 3 次 | 成本失控 / 雪崩 |

### 失败模式对应方案（一表打尽）

| 失败模式 | 解决手段 | 关键工具 |
|---------|---------|---------|
| **幻觉** | Self-Consistency | 多采样 + Judge 模型 |
| **格式错** | Output Parser + 重试 | Pydantic / Zod + format hint |
| **超时** | 双 timeout + 降级 | 软限 5s / 硬限 30s + Fallback 模型 |
| **成本爆炸** | 3 道 quota 强制 | 用户级 / 接口级 / 全局级 |

### 面试反问模板

```text
Q1：贵司对答案准确性的要求？
    → 金融/医疗用 5 投票；一般用 Self-Consistency 即可
Q2：贵司是否有回归测试流程？
    → 黄金集 + 漂移检测必须有
Q3：Judge 模型用什么？
    → 离线用 GPT-4（强但贵），线上用业务 fine-tune 的小模型（快且省）
```

### 与本目录其他"灵魂拷问"的协同

- **Q1 思维范式**：本节方案仅在"必须用 LLM"时启用——能用规则就别用 LLM（成本 × 5）
- **Q2 成本控制**：Self-Consistency 多采样会让成本翻 5-7 倍，必须配合 5 层路由
- **Q4 超时熔断**：一致性投票的单次超时必须设短（5s），否则总时延爆炸
- **Q5 监控定位**：必须监控"**一致性指标**"（多次回答分歧度），不是只看延迟

---

## 速查 · 关联资源
- **餐厅叙事**：[12.story/05-observability.md](../../../12.story/05-observability.md) —— 阿明餐厅的"AI 思维工程 5 问"实战
- **面试题**：[思维范式](../../../13.split-hairs/11.ai/llm-thinking-paradigm/) · [成本控制](../../../13.split-hairs/11.ai/llm-cost-control/) · 一致性（本节速记卡） · [超时熔断](../../../13.split-hairs/11.ai/llm-timeout-circuit-breaker/) · [监控](../../../13.split-hairs/11.ai/llm-monitoring/) — 拆分为 5 个独立面试题
- **同级兄弟**：[llm-evaluation](../04-llm-evaluation/README.md) · [llmops-stack](../02-llmops-stack/README.md)
- **相关章节**：[production-agent](../../03-engineering/production-agent/README.md) · [harness-engineering](../../03-engineering/harness-engineering/README.md) · [loop-engineering](../../03-engineering/loop-engineering/README.md) · [hallucination](../../../13.split-hairs/11.ai/hallucination/README.md)

---

← [返回: LLMOps](../README.md)
