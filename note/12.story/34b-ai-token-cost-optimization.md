<!--
story:
  number: 34b
  type: 续集
  position: 续集十二（下）
  title: 省钱大作战
  audience: AI 工程师 / 架构师
-->

# 34b · 省钱大作战

> 从阿明的"AI 月账单从 5 万涨到 50 万"，看 AI 时代的 FinOps —— Token 经济学**下篇：成本优化与 ROI**

> **系列定位**：本篇是「阿明餐厅」系列的**续集十二（下）**。本篇接续[34a · AI 成本结构（上）](./34a-ai-token-cost-structure.md)，**聚焦"优化成本"**：路由 + 缓存 + 压缩 + 训练优化 + 6 大实战技巧 + ROI 度量 + FinOps 组织。本篇与上篇是一对孪生篇 —— 上篇讲"看见"，下篇讲"赚回"。

> **兄弟篇**：34a · AI 成本结构（[← 点击阅读](./34a-ai-token-cost-structure.md)）

---

## 引言：从"看见成本"到"优化成本"

> **阿明的厨房类比（开篇场景）**：上篇（34a）阿明看清了"调料账单"，发现每月调料花 5 万。这篇阿明要"省调料"—— 但不是省到菜难吃，而是"用同样的调料做出更多菜"。本章阿明的"省调料绝招"包括：按场景选便宜调料（成本感知路由）、重复用同一瓶调料（缓存）、调料批量采购（压缩）、培训厨师自己种菜（微调）…… 5 大策略，省到 30% 但菜更好吃。

[34a · 成本结构（上）](./34a-ai-token-cost-structure.md)讲的是"看见" —— 知道钱花在哪、为什么 AI 成本和云资源成本不同、6 大组件、4 大陷阱、5 大监控指标。

**但"看见"只是开始。**

阿明在看见结构后，问了 3 个问题：

1. **怎么省？** 哪些模型可以降级？哪些调用可以缓存？哪些上下文可以压缩？
2. **怎么赚？** 怎么让 AI 的 ROI 可度量？怎么把低 ROI 场景下线？
3. **怎么组织？** 谁来管 AI FinOps？是 SRE 还是产品？

本篇回答这 3 个问题。本篇分 6 章：

- **第五章**：成本感知路由（按场景选模型）
- **第六章**：缓存与压缩（零成本优化手段）
- **第七章**：训练与微调的成本控制
- **第八章**：Token 优化的 6 大实战技巧
- **第九章**：AI ROI 度量
- **第十章**：AI FinOps 的组织与流程

---

> **阿明的厨房类比（第五章）**：阿明不可能所有菜都用顶级厨师做 —— 凉拌黄瓜用学徒工就行，红烧肉才用主厨。AI 模型也一样：简单任务（凉菜）用便宜模型（GPT-4o-mini / Qwen-turbo），复杂任务（招牌菜）才用顶级模型（GPT-4o / Claude Opus）。这叫"成本感知路由"。

## 第五章：成本感知路由 —— 按场景选模型

**最有效的成本优化：不用贵的模型**。阿明设计了**5 层路由策略**。

### 5.1 模型分级

```text
Tier 1 - 旗舰模型（贵但强）
  GPT-4o / Claude Sonnet 4.6
  适用：复杂推理 / 关键决策 / 长文档分析
  成本：$5-15/M input

Tier 2 - 高性价比（中等）
  GPT-4o-mini / Claude Haiku 4.5
  适用：日常客服 / 简单生成 / RAG 检索
  成本：$0.15-1.25/M input

Tier 3 - 开源小模型（便宜）
  Llama-3.1-8B / Qwen-7B / DeepSeek-V3
  适用：分类 / 提取 / 简单对话
  成本：自建 GPU 约 $0.10/M input

Tier 4 - 专用小模型（极便宜）
  微调的 1B-3B 模型
  适用：意图识别 / 实体提取 / 分类
  成本：自建 CPU/GPU 约 $0.01/M input
```

### 5.2 路由策略

```python
# 成本感知路由
class CostAwareRouter:
    def __init__(self):
        self.models = {
            "critical": "gpt-4o",
            "standard": "gpt-4o-mini",
            "simple": "llama-8b-local",
            "trivial": "tiny-1b-local",
        }

    def route(self, request):
        # 策略 1: 风险等级路由
        if request.risk == "critical":
            return self.models["critical"]

        # 策略 2: 任务类型路由
        if request.task == "classification":
            return self.models["trivial"]  # 1B 模型够用

        # 策略 3: 上下文长度路由
        if request.context_length > 100000:
            # 长上下文用 Claude（cache 便宜）
            return "claude-sonnet-with-cache"

        # 策略 4: 成本上限路由
        if request.user.monthly_cost > 1000:
            # 重度用户降级到便宜模型
            return self.models["standard"]

        # 默认
        return self.models["standard"]
```

### 5.3 路由的"质量回退"机制

```python
# 质量回退：先用便宜模型，不行再升级
def route_with_fallback(request):
    # 第一步：用便宜模型
    response = call_model("gpt-4o-mini", request)

    # 第二步：检查质量
    quality_score = evaluate_quality(response, request)

    # 第三步：质量不行？升级模型
    if quality_score < 0.7:
        response = call_model("gpt-4o", request)
        quality_score = evaluate_quality(response, request)

        if quality_score < 0.7:
            # 还是不行？HITL
            return escalate_to_human(request)

    return response, quality_score
```

**实测效果**：

- 70% 的请求用 Tier 2 模型（成本低）
- 20% 的请求用 Tier 3 模型（更便宜）
- 8% 的请求用 Tier 1 模型（高质量）
- 2% 的请求 HITL

**总体成本下降 60%**，质量只下降 5%。

### 5.4 路由的"用户分级"

```text
用户分级 → 配额 → 模型选型

VIP 用户：GPT-4o 不限次
普通用户：每天 100 次 GPT-4o
试用用户：每天 10 次 GPT-4o-mini
免费用户：只能用 Tier 3-4 模型
```

---

> **阿明的厨房类比（第六章）**：阿明发现 80% 的订单都是"老几样"（红烧肉、麻婆豆腐、回锅肉）。如果每次都让 AI 重新"研制"，浪费调料。本章阿明用"中央厨房 + 半成品配送"（缓存 + 压缩）—— 同一道菜只做一次，半成品分发到 80 家店。

## 第六章：缓存与压缩 —— 成本优化的"零成本"手段

### 6.1 三级缓存策略

```text
Level 1 - 精确匹配缓存
  key: hash(用户问题)
  value: 上次回答
  命中：直接返回
  适用：FAQ / 重复问题
  命中率：5-20%

Level 2 - 语义匹配缓存
  key: 用户问题 embedding
  value: 上次回答
  命中：相似度 > 0.95 才返回
  适用：相似问题（"附近有川菜吗" vs "川菜有吗"）
  命中率：15-30%

Level 3 - Prompt 模板缓存
  key: hash(系统 Prompt)
  value: 缓存的 Prompt
  命中：省 90% 重复 token
  适用：所有 LLM 调用
  命中率：100%（只要 Prompt 稳定）
```

**实测**：三级缓存叠加，**总 token 减少 40-60%**。

### 6.2 上下文压缩

```python
# 上下文压缩 4 策略

# 策略 1: 截断（最简单）
def truncate_context(messages, max_tokens=4000):
    if count_tokens(messages) > max_tokens:
        # 保留 system + 最近 5 轮
        return messages[:1] + messages[-5:]
    return messages

# 策略 2: 摘要（中等）
def summarize_context(messages, max_tokens=2000):
    if count_tokens(messages) > max_tokens:
        # 用 LLM 摘要老消息
        old_messages = messages[1:-5]
        summary = llm_call("gpt-4o-mini",
                            f"请摘要以下对话：{old_messages}",
                            max_tokens=500)
        return [messages[0], {"role": "system", "content": f"历史摘要：{summary}"}] + messages[-5:]

# 策略 3: RAG 替换（推荐）
def rag_replace_context(query, full_docs, top_k=5):
    # 不用全量文档，只用检索到的相关片段
    relevant_docs = vector_db.search(query, top_k=top_k)
    return f"参考资料：{relevant_docs}"

# 策略 4: 结构化提取（高级）
def extract_structured(conversation):
    # 把对话提取成结构化信息
    return {
        "user_intent": "查订单",
        "key_info": {"order_id": "123"},
        "context": "用户对上次回复不满",
    }
```

**实测**：上下文压缩可**减少 50-80% 的 token**，质量只下降 10-15%。

### 6.3 输出压缩

```python
# 输出压缩：让 AI 写"短一点"
output_prompt_v1 = "请回答用户问题"
output_prompt_v2 = "请用最简洁的语言回答（不超过 50 字）"

# 实测：v2 比 v1 节省 60% 输出 token
# 代价：信息密度变高，用户体验略差
# 平衡：核心场景用 v1，闲聊场景用 v2
```

### 6.4 Embedding 缓存

```python
# Embedding 缓存：相同文本不重复 Embedding
embedding_cache = {}

async def get_embedding(text):
    cache_key = hash(text)
    if cache_key in embedding_cache:
        return embedding_cache[cache_key]

    embedding = await embedding_api.embed(text)
    embedding_cache[cache_key] = embedding
    return embedding

# 命中率通常 30-50%（重复查询常见）
# 节省 30-50% Embedding 成本
```

---

> **阿明的厨房类比（第七章）**：阿明花了 50 万请米其林大厨来培训 —— 结果培训出 5 个能做大餐的厨师，但花了 80 万。培训是"长期投资"，但**培训成本不能比长期收益还贵**。本章阿明学会用 LoRA/QLoRA"小培训"—— 用 1/10 的成本培训出 80% 水平的厨师。

## 第七章：训练与微调的成本控制 —— 培训厨师不能把餐厅培训破产

### 7.1 训练的成本结构

```text
训练成本 = GPU 时长 + 数据成本 + 存储成本

GPU 时长 = 数据量 × 模型大小 × 训练轮次 / GPU 算力

例：
  微调 Llama-7B（QLoRA）
  - 数据：5000 样本
  - 轮次：3 epoch
  - GPU：A100 1 卡
  - 时长：约 8 小时
  - 成本：8 × 30 = ¥240
```

### 7.2 5 大训练成本控制

**控制 1：LoRA / QLoRA 替代全参数微调**

```text
全参数微调 7B 模型：
  - 显存：60GB+（A100 80G 勉强）
  - 时长：20 小时
  - 成本：¥600

QLoRA 微调 7B 模型：
  - 显存：24GB（A100 40G / 4090 24G 即可）
  - 时长：8 小时
  - 成本：¥240

节省：60%
```

**控制 2：数据复用**

```text
不要每次微调都重新准备数据：
  - 数据集版本化（Git 管理）
  - 增量训练（基于上次的 checkpoint）
  - 共享 embedding 缓存
```

**控制 3：自动化训练流水线**

```text
手动训练：准备数据 → 跑训练 → 评估 → 调参 → 重训（4-8 小时）
自动化训练：数据变更触发 → 自动训练 → 评估 → 自动部署（30 分钟）

节省：人力成本 10×
```

**控制 4：训练任务调度**

```text
训练任务用 Spot 实例：
  - On-Demand：¥30/小时
  - Spot：¥10/小时（可中断）
  - 训练可恢复 → Spot 完全够用
  - 节省：66%
```

**控制 5：模型蒸馏**

```text
用大模型的输出来训练小模型：
  - 大模型（GPT-4）做"教师"
  - 小模型（Llama-8B）做"学生"
  - 训练数据：大模型的输出
  - 推理时：用小模型，成本降低 10-100×
```

### 7.3 训练 ROI 评估

```python
# 训练 ROI 计算
training_cost = 5000  # 训练花了 5000 元
inference_saving_per_month = 8000  # 训练后每月推理节省 8000
quality_improvement = 0.05  # 质量提升 5%

roi_months = training_cost / inference_saving_per_month
# = 5000 / 8000 = 0.625 个月 → 不到 1 个月回本

# 如果 ROI > 12 个月，建议不训练（用 Prompt Engineering 替代）
```

---

## 第八章：Token 优化的 6 大实战技巧 —— 六个省字绝招，字字用在刀刃上

阿明总结了 6 个**立即可做**的 Token 优化技巧。**剩下的"分块处理长文档 / RAG 替代长上下文 / Function Call Schema 简化 / 僵尸 Prompt 清理"等 4 个技巧**，详见[34a 第三章"4 大隐藏陷阱"](./34a-ai-token-cost-structure.md#第三章token-计费的-4-大隐藏陷阱)和第五章的"5 层路由"，本章聚焦最高频的 6 个。

### 8.1 技巧 1：精简 System Prompt

```text
# 优化前（200 token）
"你是一个专业的、智能的、友善的客服助手，名字叫小美。
 你的职责是帮助用户解答关于阿明餐厅的问题，包括但不限于：
 1. 菜品信息
 2. 订单查询
 3. 退款政策
 4. 配送问题
 你应该保持礼貌、耐心、专业，禁止讨论政治、宗教等敏感话题。
 如果不确定答案，请转人工。"

# 优化后（60 token）
"你是阿明餐厅客服。回答：菜品/订单/退款/配送。
 不确定转人工。"
```

**节省**：70% system prompt token。

### 8.2 技巧 2：避免"Few-shot"过度使用

```text
# 错误：5 个 example（约 1000 token）
example1 = "..."
example2 = "..."
example3 = "..."
example4 = "..."
example5 = "..."

# 正确：1-2 个 example（约 200 token）
example1 = "..."

# 更好：Zero-shot + 清晰指令（0 token example）
"请按以下格式输出：..."
```

**节省**：80% few-shot token。

### 8.3 技巧 3：Tool 定义精简

```python
# 优化前：每个 tool 详细描述
tool_def = {
    "name": "query_order",
    "description": "这是一个用于查询订单状态的工具，参数是订单 ID，返回订单的详细信息，包括但不限于订单状态、订单金额、订单时间等。",
    "parameters": {
        "order_id": {"type": "string", "description": "订单的唯一标识符，通常是一个 8 位数字字符串，例如 12345678"}
    }
}

# 优化后
tool_def = {
    "name": "query_order",
    "description": "查订单",
    "parameters": {
        "order_id": {"type": "string"}
    }
}
```

**节省**：60% tool 定义 token × N 个 tool。

### 8.4 技巧 4：流式输出（用户提前看到响应）

```python
# 流式输出：用户看到第一个字就"知道 AI 在响应"
async def stream_response(prompt):
    async for chunk in llm.stream(prompt):
        yield chunk

# 用户不等最后 token 生成完就能开始看
# 不减少总 token，但用户体验好 → 容忍度更高
```

### 8.5 技巧 5：拒绝处理"无意义"输入

```python
# 简单输入 → 规则引擎兜底
def handle_request(user_input):
    if len(user_input) < 3:
        return "请详细描述您的问题"

    if "你好" in user_input or "hi" in user_input.lower():
        return "你好，我是阿明餐厅客服，有什么可以帮您？"

    # 真的有意义的问题，才调 LLM
    return await llm_call(user_input)
```

**节省**：20% 闲聊 token。

### 8.6 技巧 6：批处理（Batching）

```python
# 优化前：100 个用户请求 = 100 次 API 调用
for user in users:
    response = await llm_call(user.input)

# 优化后：100 个用户请求 = 1 次 API 调用（批量）
batch_prompt = "请依次回答以下 100 个问题：\n"
for i, user in enumerate(users):
    batch_prompt += f"{i+1}. {user.input}\n"
response = await llm_call(batch_prompt, max_tokens=10000)
```

**节省**：API 调用费（按调用次数收费时），但 token 可能略增。

> 进阶技巧 7-10：长文档分块 Map-Reduce、RAG 替代长上下文、Function Call Schema 动态选择、僵尸 Prompt 清理 —— 这些分别在[34a 第三章 4 大陷阱](./34a-ai-token-cost-structure.md#第三章token-计费的-4-大隐藏陷阱)、第五章 5 层路由有详细展开。

---

> **阿明的厨房类比（第九章）**：阿明花 10 万请米其林大厨，到底值不值？要看大厨做的招牌菜让餐厅多赚了多少。如果大厨带来了 50 万新营收，ROI = 5x，值；如果只多赚 5 万，ROI = 0.5x，不值。本章阿明学会用 4 类 ROI 度量"AI 投资回报"。

## 第九章：AI ROI 度量 —— 花了十万请大厨，得算算多赚了多少

**成本不是"花得少"，是"花得值"**。阿明建立了 AI 系统的 ROI 度量框架。

### 9.1 AI 系统的 4 类 ROI

```text
ROI 1 - 替代人力（Cost Reduction）
  AI 替代了多少人 × 工资 = 节省的钱
  例：客服 AI 替代 5 个客服 × 8000 元/月 = 4 万/月

ROI 2 - 增加收入（Revenue Growth）
  AI 带来了多少新客户/订单
  例：AI 推荐让 GMV 提升 10% × 100 万 = 10 万/月

ROI 3 - 提升效率（Productivity）
  AI 让现有员工效率提升
  例：AI 辅助让工程师效率提升 30% × 10 人 × 2 万 = 6 万/月

ROI 4 - 降低风险（Risk Reduction）
  AI 减少了多少事故/损失
  例：AI 监控让故障率下降 50% × 10 万/月潜在损失 = 5 万/月
```

### 9.2 ROI 计算公式

```python
# 单个 AI 场景的 ROI
ai_scenario_roi = {
    "scenario": "客服 AI",
    "monthly_cost": 5000,  # AI 成本
    "monthly_saving": 40000,  # 替代 5 个客服
    "monthly_revenue_gain": 0,  # 没有新收入
    "net_monthly_value": 40000 - 5000,  # 35000
    "roi": 35000 / 5000,  # 7x
    "payback_months": 5000 / 35000,  # 0.14 月
}

# 决策：ROI > 3x 才值得做
```

### 9.3 5 大反 ROI 模式

| 反模式 | 表现 | 正确做法 |
|--------|------|----------|
| **算不清 ROI** | "AI 很好" 但不知道好在哪 | 建立 4 类 ROI 度量 |
| **只算成本** | "AI 烧钱" | 同时算收入和效率 |
| **短期 ROI 思维** | "3 个月不回本就停" | AI 有学习曲线，给 6-12 个月 |
| **平均 ROI 思维** | "整体 ROI 5x 很好" | 拆分场景，可能 1 个场景亏钱 |
| **忽略隐藏成本** | 只算 API 费 | 算全成本（含工程/数据/运维） |

### 9.4 AI 成本 vs 业务增长的健康度

```text
健康：
  - AI 成本增长 < 业务增长（成本占比下降）
  - 边际成本递减（每用户成本下降）

警告：
  - AI 成本增长 = 业务增长（成本占比不变）
  - 边际成本不变

危险：
  - AI 成本增长 > 业务增长（成本占比上升）
  - 边际成本递增 → 必须优化
```

阿明的仪表盘每月给管理层看这个图。

---

> **阿明的厨房类比（第十章）**：省调料不是一个人能干的 —— 需要"调料采购员"（监控账单）、"厨师长"（审批大模型使用）、"采购委员会"（CCB，审批加新菜的成本）。本章阿明建"AI FinOps 团队" —— 5 大成熟度阶段 + 5 大实战流程。

## 第十章：AI FinOps 的组织与流程 —— 谁来管账单，谁来审批"加菜"

### 10.1 AI FinOps 团队配置

```text
小型团队（< 5 个 AI 应用）：
  - 1 个 DevOps 兼 AI FinOps
  - 用第三方工具（Helicone / LangSmith）
  - 月度 review

中型团队（5-20 个 AI 应用）：
  - 1 个 AI 平台工程师
  - 1 个 FinOps 分析师
  - 1 个产品经理（管 ROI）
  - 自建 + 第三方混合

大型团队（> 20 个 AI 应用）：
  - AI 平台团队（3-5 人）
  - FinOps 团队（2-3 人）
  - 产品经理（每场景 1 人）
  - 完整自建平台
```

### 10.2 AI FinOps 的 5 大工作流

```text
工作流 1 - 预算管理
  - 每场景年度 / 季度 / 月度预算
  - 超预算自动告警 + 拦截
  - 预算滚动 review

工作流 2 - 成本归因
  - 按用户 / 场景 / 模型 / 团队归因
  - Showback / Chargeback 报表
  - 谁的钱谁负责

工作流 3 - 优化建议
  - 每月输出"成本优化 Top 5"
  - 推动团队落地
  - 跟踪 ROI

工作流 4 - 异常告警
  - 单次成本异常 → 实时告警
  - 月度预算超支 → 周告警
  - 季度趋势异常 → 月告警

工作流 5 - 战略规划
  - 季度规划：哪些 AI 场景值得做
  - 模型选型：什么时候升级 / 降级
  - 自建 vs API 决策
```

### 10.3 AI FinOps 的成熟度模型

| 等级 | 名称 | 特征 |
|------|------|------|
| L1 | 事后发现 | 月底看账单，"怎么又超了？" |
| L2 | 实时监控 | 有仪表盘，知道"钱花在哪" |
| L3 | 主动优化 | 持续做优化，月环比下降 10% |
| L4 | 智能优化 | AI 自动优化（路由/缓存/压缩） |
| L5 | 战略 FinOps | FinOps 驱动 AI 战略，预算-业务对齐 |

阿明现在在 **L3 → L4** 之间：主动优化已稳定，下一步是**让 AI 自己优化 AI 成本**（自动路由、自动压缩、自动缓存策略调整）。

---

## 核心总结（下篇）：AI 成本优化的全景

```mermaid
graph TB
    subgraph "成本感知"
        A1[实时监控]
        A2[异常告警]
        A3[成本归因]
    end

    subgraph "成本优化"
        B1[模型路由]
        B2[缓存策略]
        B3[压缩技术]
        B4[训练优化]
        B5[部署优化]
    end

    subgraph "ROI 度量"
        C1[替代 ROI]
        C2[收入 ROI]
        C3[效率 ROI]
        C4[风险 ROI]
    end

    subgraph "组织流程"
        D1[预算管理]
        D2[Showback]
        D3[持续优化]
        D4[战略规划]
    end

    A1 & A2 & A3 --> B1 & B2 & B3 & B4 & B5
    B1 & B2 & B3 & B4 & B5 --> C1 & C2 & C3 & C4
    C1 & C2 & C3 & C4 --> D1 & D2 & D3 & D4
    D1 & D2 & D3 & D4 -.->|反馈| A1
```

| 维度 | 核心问题 | 关键工具/方法 | 优化效果 |
|------|----------|---------------|----------|
| 监控 | 钱花在哪？ | Helicone / LangSmith | 看见 |
| 路由 | 用对模型了吗？ | 成本感知路由 | 30-60% |
| 缓存 | 重复算了吗？ | 3 级缓存 | 40-60% |
| 压缩 | 上下文冗余吗？ | 4 策略压缩 | 50-80% |
| 训练 | 训练 ROI？ | LoRA + 蒸馏 | 60% |
| 部署 | 自建 vs API？ | 混合部署 | 30-50% |
| ROI | 赚了吗？ | 4 类 ROI | 决策 |

### 下篇心法

**AI 成本不是"月底看账单"，是"实时监控 + 主动优化 + ROI 度量"的工程体系。** Token 不会撕账单，但月底会 —— 看不见的成本最可怕，看得见的优化最有效。

---

## 延伸阅读

- [34a · AI 成本结构（上篇）](./34a-ai-token-cost-structure.md) —— 成本结构与监控
- [阿明的省钱经](./14-cloud-finops.md) —— 番外二，云资源 FinOps，本篇的"传统版本"
- [Agent Harness](./30-agent-harness.md) —— 续集八，Agent Loop 的成本护栏
- [AI 评测工程（基础篇）](./32a-ai-evaluation-fundamentals.md) / [（流水线篇）](./32b-ai-evaluation-pipeline.md) —— 续集十，评测本身有成本（与本篇成本优化的"分层评测"对应）
- [从厨师到 CEO](./07-from-chef-to-ceo.md) —— 终章，FinOps 是技术管理 ROI 的一部分
- [AI 致命三件套](./31-ai-fatal-trio.md) —— 续集九，攻击者也会利用 Token 成本（拒绝服务 / 资源耗尽）
- [MCP 协议](./33a-mcp-protocol.md) / [A2A 协议](./33b-a2a-protocol.md) —— 续集十一，协议层是成本监控的颗粒度
- [Codebase 认知债](./29-codebase-cognitive-debt.md) —— 续集七，认知债导致"看不懂代码也改不出 Token 优化"
- [AI 的"黑暗料理"](./28-ai-hallucination-safety.md) —— 续集六，AI 幻觉的"重试成本"
- [学徒的困境](./11-ai-learning-paradox.md) —— 续集二，AI 时代的人机协作与 Token 成本的关系
- [会自我进化的厨房](./27-self-evolving-company.md) —— 续集五，自进化组织的"烧 Token 不烧人头"

---

## 跨章节衔接

- 11.ai/02-technology-stack/README.md —— AI 技术栈中的推理/Embedding/向量库 —— 6 大成本组件的技术解构
- 11.ai/03-engineering/ai-platforms/README.md —— AI 平台 —— 平台层成本感知路由与缓存压缩的工程实现

---

## 结语

阿明花了 3 个月，把 AI 月成本从 48 万降到了 18 万（下降 62%），同时业务增长了 2 倍：

```text
优化前（2026/01）：
  - AI 成本：48 万
  - 业务量：100%
  - 单位成本：48 万/100% = 48 万

优化后（2026/06）：
  - AI 成本：18 万
  - 业务量：200%
  - 单位成本：18 万/200% = 9 万

单位成本下降：81%
```

**关键动作**：

1. **实时监控**：知道钱花在哪（Helicone）
2. **成本路由**：70% 请求用便宜模型，30% 用贵的（路由策略）
3. **三级缓存**：FAQ / 语义 / Prompt 缓存，命中率 50%（Redis + Embedding 缓存）
4. **上下文压缩**：RAG 替代长文档，节省 80% token（RAG + 摘要）
5. **训练优化**：LoRA + Spot 实例，节省 70% 训练成本
6. **ROI 度量**：低 ROI 场景下线，资源向高 ROI 场景倾斜

阿明对团队说：

> "**AI 成本和云资源成本是两回事**。云资源看得到，AI 成本看不到 —— Token 进去了不一定出来，出来也不一定有用。**没有 AI FinOps，AI 系统就是'在云上烧钱、在月底哭'**。有了 AI FinOps，AI 才能从'成本中心'变成'价值中心'。"

下次当你的 AI 系统月账单超预算时，不妨问自己：

- 你的 **Token 成本是实时可见**的吗？还是月底才知道？
- 你的 **AI 成本有归因**吗？能算清"哪个用户 / 哪个场景最贵"吗？
- 你的 **模型路由**有"成本感知"吗？还是"无脑用 GPT-4"？
- 你的 **缓存命中率**是多少？< 30% 就是浪费
- 你的 **上下文**有没有过度膨胀？用 RAG 替代了吗？
- 你的 **训练 ROI**算过吗？什么时候回本？
- 你的 **AI 业务 ROI**算过吗？4 类 ROI 各是多少？
- 你的 **组织有 FinOps 职能**吗？还是"开发者凭感觉省钱"？

> 好的成本优化，不是"一刀切换便宜模型"，而是"**该省省、该花花——用缓存减少重复消费，用小模型处理简单任务，用架构思维降低总成本**"。

← [返回系列导读](./index.md) | [上篇：34a 成本结构 →](./34a-ai-token-cost-structure.md)