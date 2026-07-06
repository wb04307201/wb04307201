<!--
question:
  id: 11.ai-production-thinking-5q
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI Production Engineering
  tags: [11.ai, LLM, 思维范式, 成本控制, 一致性, 超时熔断, 监控, Production]
-->

# 大模型思维工程：5 个灵魂拷问

> 一句话定位：LLM 生产稳定性不是"Prompt 写得更好"那么简单——而是 5 大工程的协同回答：思维范式 + 成本降级 + 一致性处理 + 超时熔断 + 监控定位。完整深度见 [主模块 llm-production-thinking 专题](../../../11.ai/03-engineering/llm-production-thinking/README.md)。

> **系列定位**：经典 AI 生产工程面试题（字节 / 阿里 / 美团 / Anthropic 高频）。考察的不是"Prompt 怎么写"，而是 **5 大工程问题的协同能力** + **5 大反模式** + **何时反选**。

---

## 引子：阿明 CTO 上线 AI 客服的 3 个崩溃现场

```text
场景：2024 Q3 某 AI 公司 CEO 阿明 决定上线"AI 客服"——
- 上线 1 周：成本失控（每日从 $300 飙到 $12,000）
- 上线 2 周：用户反馈"AI 一问三不知"
- 上线 3 周：供应商短暂故障 30 分钟，APP 完全卡死
```

**崩盘现场**（5 个核心问题）：

1. **思维错位**：产品同事把"金额校验"都丢给 LLM（5ms if-else 变 500ms + $0.01）
2. **成本爆炸**：循环 bug 让 Agent 无限调 API，token 无上限
3. **连续不一致**：客服问"北京人口"3 次返回 2000/3000/5000 万
4. **超时熔断缺失**：供应商故障时每个请求卡 60 秒
5. **监控盲区**：上游静默升级，用户狂喷"AI 变笨了"

普通候选人会答"Prompt 写得更好就行"——踩中"**忽视工程、缺反模式、缺协同**" 3 大雷区。
高分候选人会答：**思维范式（4 信号决策）→ 5 层路由（cost control）→ Self-Consistency 投票（一致性）→ 双 timeout + Circuit Breaker（熔断）→ Trace + 黄金集（监控）**。

---

## 一、核心原理（必选）

### 1.1 5 大问题的本质

| # | 问题 | 本质 | 工程方案 |
|---|------|------|---------|
| **Q1** | Prompt 可能不如 if-else | 决策错位 | 4 信号决策 |
| **Q2** | 成本上限 + 降级 | 经济性问题 | 5 层路由 + 3 道 quota |
| **Q3** | 连续 3 次不一致 | 概率模型特性 | Self-Consistency 投票 + Judge |
| **Q4** | 超时熔断 | 可用性问题 | 双 timeout + Circuit Breaker |
| **Q5** | 监控 + 定位 | 可观测性问题 | Trace + 黄金集 + 漂移 |

### 1.2 思维范式 4 信号

```
用 LLM 的 4 信号（满足 ≥ 3 个才上）：
1. 输入是非结构化（自然语言）
2. 规则难以枚举（> 100 条）
3. 答案容许一定错误（> 5%）
4. ROI 比规则 ≥ 10x
任一不满足 → 规则优先 / LLM 兜底
```

完整内容见 [01-thinking-paradigm](../../../11.ai/03-engineering/llm-production-thinking/01-thinking-paradigm.md)。

### 1.3 成本 5 层路由

```
Layer 1：缓存 + 规则（5ms）—— 80% 请求
   ↓ 未命中
Layer 2：Cheap 小模型（200ms，$0.0001）—— 15%
   ↓ 复杂
Layer 3：Big 模型（1s，$0.01）—— 4%
   ↓ 仍失败
Layer 4：SaaS API fallback（3s，$0.05）—— 1%
   ↓ 仍失败
Layer 5：人工兜底 —— 0.X%
```

### 1.4 一致性：Self-Consistency 投票

```python
samples = [llm.invoke(query, temperature=0.7) for _ in range(5)]
# Judge 模型选最佳（不是字符串投票，是语义投票）
best = judge_llm.choose_best(query, samples)
```

### 1.5 熔断 3 道防线

```
[客户端] loading state（5s 用户能看到的）
   ↓
[Edge Timeout] CDN/网关层 5s 截断
   ↓
[服务端双 Timeout] 5s 软限 partial + 30s 硬限 fallback
   ↓
[Circuit Breaker] 错误率 > 50% 熔断 30s
   ↓
[Fallback 模型链] 切换 secondary/tertiary/SaaS
   ↓
[静态兜底] "请稍后重试" + 转人工
```

完整见 [04-timeout-and-circuit-breaker](../../../11.ai/03-engineering/llm-production-thinking/04-timeout-and-circuit-breaker.md)。

### 1.6 监控 4 维 + Trace

```
4 维：延迟 + 成本 + 质量 + 一致性
Trace：5 分钟定位根因（vs 1-3 天经验排查）
黄金集：每月 / 每次模型升级回归
漂移检测：Embedding / Prompt / 召回率
```

---

## 二、面试话术（90 秒版本 / 5 问各一题）

> ⚠️ **模板不是背答案**——面试现场结合题目微调。

### 题目 A：Prompt 可能不如 if-else……大模型思维工程如何养成？

**高分答案**（4 层递进，60-90 秒）：

```
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

### 题目 B：模型调用的成本上限是多少？超了如何自动降级？

**高分答案**（60 秒）：

```
"LLM 成本必须硬上限 + 自动降级，3 道 quota + 5 层路由：

3 道 quota（防爆）：
- 单请求：4000 输入 / 2000 输出 / $0.05
- 单用户：$10/天 / $200/月
- 单租户：$1000/天 / 并发 100

5 层路由（降级）：
- Layer 1 缓存 + 规则：$0, 5ms
- Layer 2 Cheap 小模型：$0.0001, 200ms（80%）
- Layer 3 Big 模型：$0.01, 1s（4%）
- Layer 4 SaaS API fallback：$0.05, 3s（1%）
- Layer 5 人工兜底

实时监控 + Prometheus 告警：95% 阈值时熔断，
P99 单请求 $0.05 触发降级。"

反问：贵司是 B2C 高 QPS 还是 B2B 低 QPS？
前者必须 Layer 2 主导，后者 Layer 3 足够。"
```

### 题目 C：如果模型连续 3 次给出不一致的结果，系统如何反应？

**高分答案**（60 秒）：

```
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

### 题目 D：等不及模型思考，系统有没有超时熔断？

**高分答案**（60 秒）：

```
"必须有三层超时熔断：

1. 双 Timeout：
   - 软 5s：开始响应就 partial 推给前端（流式）
   - 硬 30s：兜底 fallback（直接返回"请稍后重试"）

2. Circuit Breaker（熔断器）：
   - 错误率 > 50% 熔断 30s
   - Half-Open 探针：成功 50% 后恢复
   - 避免雪崩

3. Fallback 模型链：
   - primary（GPT-4o）→ secondary（Claude）→ tertiary（开源）→ static FAQ
   - 多供应商 + SaaS 兜底

反模式：
- 只一个 timeout → 切
- 超时后重试 5 次 → 错（不要重试，fallback）
- 没有熔断 → 一旦故障全挂
- 只有 1 个供应商 → 必须多供应商"
```

### 题目 E：上线后怎么检测准确率 / 幻觉率？怎么快速定位问题？

**高分答案**（60 秒）：

```
"4 维监控体系 + Trace + 黄金集回归。

4 维指标：
- 延迟：P50/P95/P99 latency（实时）
- 成本：单请求 / 日累计（实时）
- 质量：准确率 / 幻觉率（5 分钟 batch）
- 一致性：重复问题答案漂移率（1 小时）

黄金集（50-200 题人工标注）：
- 每月回归
- 每次模型升级跑全量
- 准确率跌破 85% 告警

漂移检测：
- Embedding 分布（KS 检验）
- Prompt 模板响应
- 召回率变化

5 分钟定位实战：
1. 看监控大盘（30s）
2. 查 Trace 抽样 5 个失败请求（1 分钟）
3. 比对黄金集（2 分钟）
4. 定位根因：RAG 召回错 / Prompt 漂移 / 模型升级 / 数据过期（5 分钟）

工具：Langfuse / Helicone / Phoenix

反模式：
- 只监控 HTTP 200 + latency（缺质量 + 成本 + 一致性）
- 上线后没 Trace（定位 3 天 vs 5 分钟）
- 黄金集跑一次（每次升级都应回归）
- 漂移检测从未设置（事故等到才发现）"
```

### 题目 F（综合）：5 个问题优先级如何排？

**高分答案**（45 秒）：

```
"上线前必须全部 4 维：
1. 思维范式（设计阶段）
2. 成本 5 层路由（设计阶段）
3. 一致性投票（设计阶段）
4. 监控 4 维（设计阶段）

上线后必须实时：
5. 熔断（运维阶段）

优先级：
- 监控 > 熔断 > 一致性 > 成本 > 思维范式
- 因为：监控告诉你"哪里出错"，熔断防雪崩
- 一致性 / 成本 / 思维是"问题本身"

实施 checklist：
- 思维决策 1 天
- 5 层路由 + 3 道 quota 1 周
- Self-Consistency + Judge 1 周
- 双 timeout + Circuit Breaker 2 天
- Trace + 黄金集 + 漂移 1 周

总计 ~1 个月（看复杂度）。"
```

---

## 三、常见陷阱（必选，5 个核心反模式）

### 陷阱 1：思维错位（LLM 万能）

- **错误**：所有逻辑都用 LLM（金额校验、电话校验、UUID）
- **真相**：结构化校验 if-else 5ms，LLM 500ms + $0.01
- **代价**：成本 × 5，错误率从 0% 涨到 5%

### 陷阱 2：成本爆炸（无硬上限）

- **错误**：所有调用不加 quota，"看监控再说"
- **真相**：监控是事后，循环 bug 会 1 小时烧 $1000
- **代价**：上线即事故

### 陷阱 3：raw 重试

- **错误**：3 次失败重试 3 次，认为会好
- **真相**：LLM 是概率模型，幻觉重试还是幻觉
- **代价**：浪费 3x 成本，答案还是错

### 陷阱 4：单 timeout

- **错误**：timeout=30s 一刀切
- **真相**：长等待让用户体验崩塌
- **代价**：用户流失，APP 卡死

### 陷阱 5：监控盲区（只盯延迟）

- **错误**：监控 HTTP 200 + latency 就够了
- **真相**：质量掉到 70%，用户耐心用户以为是 AI 进步
- **代价**：3 个月才发现，损失 50% 用户

---

## 四、最佳实践（5 大问题对应方案）

### 方案 A：客服 Agent（高频 B2C）

```
- 思维：80% 规则 + 20% LLM
- 成本：缓存 + Cheap 主导 ($0.001/次)
- 一致性：Self-Consistency + 客服领域 Judge
- 熔断：双 timeout + SaaS 兜底
- 监控：Trace + 黄金集 100 题

效果：客服响应 P99 < 2s，成本 $0.05/次，准确率 92%
```

### 方案 B：金融分析师（高风险 B2B）

```
- 思维：规则优先 + LLM 兜底
- 成本：Big 模型 + 审计（人审）+ 5 层路由
- 一致性：3 供应商投票（GPT-4 / Claude / Gemini）
- 熔断：强熔断 + 转人工（Hystrix strict mode）
- 监控：强监控 + 审计 + 漂移秒级

效果：准确率 95%+，可解释性 100%
```

### 方案 C：代码助手（中等 QPS B2C）

```
- 思维：LLM 主 + Linter 规则
- 成本：Big 模型 + Cache（IDE session 复用）
- 一致性：Self-Reflection（重新生成 if 测试失败）
- 熔断：双 timeout + Cursor 回退
- 监控：Trace + CodeBLEU 评估

效果：IDE 内 P99 < 1.5s，准确率 88%
```

---

## 五、相关章节（强制）

### 主模块深度专题

- [llm-production-thinking 总目录](../../../11.ai/03-engineering/llm-production-thinking/README.md)
- [01-thinking-paradigm](../../../11.ai/03-engineering/llm-production-thinking/01-thinking-paradigm.md) —— Prompt vs if-else 思维范式
- [02-cost-control-and-degradation](../../../11.ai/03-engineering/llm-production-thinking/02-cost-control-and-degradation.md) —— 5 层路由 + 3 道 quota
- [03-consistency-and-failure-handling](../../../11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md) —— Self-Consistency 投票
- [04-timeout-and-circuit-breaker](../../../11.ai/03-engineering/llm-production-thinking/04-timeout-and-circuit-breaker.md) —— 超时熔断
- [05-online-monitoring](../../../11.ai/03-engineering/llm-production-thinking/05-online-monitoring.md) —— Trace + 漂移检测
- [06-decision-tree](../../../11.ai/03-engineering/llm-production-thinking/06-decision-tree.md) —— 决策树 checklist

### 同栏目（11.ai）姐妹篇

- [harness-engineering](../../11.ai/harness-engineering/README.md) —— Agent 行为约束
- [loop-engineering](../../11.ai/loop-engineering/README.md) —— Loop 失败模式
- [production-agent](../../../11.ai/production-agent/README.md) —— 生产 Agent 总览
- [hallucination](../../11.ai/hallucination/README.md) —— 幻觉深度检测

### 主模块兄弟

- [11.ai/07-llmops/04-llm-evaluation](../../../11.ai/07-llmops/04-llm-evaluation/README.md) —— LLM 评估体系 6 维度
- [11.ai/07-llmops/02-llmops-stack](../../../11.ai/07-llmops/02-llmops-stack/README.md) —— LLMOps 全景
- [11.ai/03-engineering/ai-platforms/vllm-vs-ollama](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md) —— 推理引擎选型（成本相关）

### 实战姐妹（12.story）

- [12.story/05-observability](../../../12.story/05-observability.md) —— 阿明餐厅的"AI 思维工程 5 问"实战
- [12.story/04-peak-traffic-defense](../../../12.story/04-peak-traffic-defense.md) —— 高峰流量防御

---

## 六、面试反问（让候选人反客为主）

```
Q1：贵司 LLM 接 API 还是自部署？单供应商还是多？
    → 决定 5 层路由的复杂度
Q2：贵司对延迟的 P99 SLO 是多少？
    → < 500ms 强制 Sliding Window + Cheap 模型
Q3：贵司对答案准确性的要求？
    → 金融/医疗用 5 投票；一般用 Self-Consistency 即可
Q4：贵司是否有回归测试流程？
    → 黄金集 + 漂移检测必须有
Q5：贵司事故复盘时间窗？
    → 5 分钟定位需要 Trace 平台
```

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 6 道精选 Q&A · 含 90 秒话术模板 + 5 大反模式 + 3 工业方案
