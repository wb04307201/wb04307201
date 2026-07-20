<!--
question:
  id: 11.ai-temperature-zero-myth
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: LLM 调参误区
  tags: [11.ai, temperature, sampling, determinism, inference, GPU-floating-point, seed]
-->

# Temperature=0 为什么输出还会不同 —— 5 大根因 + 3 大防御

> 一句话定位：**Temperature=0 ≠ 完全确定**——5 大根因（GPU 浮点 / Provider 默认值 / Seed 失效 / 版本升级 / Router 负载均衡）。完整深度 + 实战修复见 [主模块 · 不一致与失败处理](../../../11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md)。

> **系列定位**：LLM 调参高频误区题（Anthropic / OpenAI / Google 工程师都考过）。考察的不是"Temperature 是什么"，而是 **5 大根因识别 + 3 大实战防御 + Provider 差异**。

---

⭐⭐⭐⭐ 深度级别（高级 LLM 应用工程师级）
📚 前置知识：Transformer 解码 / Sampling / Prompt Engineering 基础

---

## 引子：生产环境 "Temperature=0 怎么还在变？"

```text
场景：2025 Q2 某 AI 产品上线连续 3 天——
- 同一 prompt "法国的首都是？" 调 gpt-4 temperature=0
- 用户报告："昨天回答 'Paris'，今天回答 '巴黎'（中文），明天又是 'Paris, France'"
- 工程师 A：不可能，temperature=0 一定确定性啊
- 工程师 B：可能是 Provider 端的"0 ≠ 0"
- 工程师 C：但每次都有微小变动，是不是浮点问题？
- CTO：限你 3 天把 SLO 提到 99.5% 一致性
```

**三个崩溃现场**：

1. 初级面试：「Temperature 是什么？」
2. 高级面试：「Temperature=0 输出 100% 一样吗？」
3. 架构师面试：「怎么保证 LLM 输出的可重现性？」

普通候选人会答："Temperature=0 就是 greedy decoding，输出应该一致"——踩中"**完全忽略 5 大根因、缺 Provider 差异认知、缺自托管思路**" 3 大雷区。
高分候选人会答：**5 大根因（GPU 浮点非结合 / Provider 默认 / Seed 失效 / 版本升级 / Router 负载均衡）+ 3 大防御（业务容错 / 自托管确定性推理 / 漂移监控）**。

---

## 一、核心原理（必选）

### 1.1 Temperature 快速回顾

```text
标准采样（temperature > 0）：
  P(token_i) = softmax(logits / temperature)   ← 软化分布
  token_i ~ P(token_i)                          ← 概率采样

Greedy decoding（temperature = 0）：
  token_i = argmax(logits)                     ← 永远选最高概率
  → 看似确定性，但实际并不绝对！
```

### 1.2 5 大根因速查表（核心考点）

| # | 根因 | 影响范围 | 实战表现 |
|---|------|---------|---------|
| 1 | **GPU 浮点非结合**（float reduction 顺序） | 所有 GPU 推理 | 同 prompt + 同模型 + 不同 batch size → 1e-7 量级差异 → 偶发 argmax 不同 |
| 2 | **Provider 默认值覆盖**（OpenAI / Anthropic 默认 ≠ 0） | 商业 API | OpenAI gpt-4 / Anthropic Claude 默认都是 1.0；"0" 在某些 SDK 内部被替换成 0.0001 |
| 3 | **Seed 字段失效**（OpenAI seed ≠ 跨调用持久化） | OpenAI API | seed 只保证 `best_of` 内一致；跨调用不一定；重启进程就失效 |
| 4 | **模型版本升级**（API 模型快照漂移） | 商业 API | gpt-4 → gpt-4-0314 → gpt-4-0613 行为不同；gpt-4o 系列每月微调 |
| 5 | **Router / 负载均衡**（不同 backend 实例） | 大厂 API | OpenAI / Anthropic 多实例路由，同 prompt 命中不同实例 → 不同 KV cache 路径 → 不同输出 |

### 1.3 Temperature=0 ≠ 完全确定的直觉图

```text
你设:    temperature = 0
API 收到: temperature = 0.0     ← Provider 内部替换成 1e-6？
       ↓
GPU 计算: argmax(logits * 1e-6 + bias)  ← 浮点 1e-7 差异
       ↓
Backend: 实例 A → 输出 1   |   实例 B → 输出 2   ← 负载均衡
       ↓
版本:    gpt-4-0613 → gpt-4-1106 → 行为漂移

→ 5 大根因叠加 → "看似确定" 实则"小幅波动"
```

### 1.4 Provider 默认 Temperature 速查表

| Provider | 模型 | 默认 Temperature | "0" 实际行为 | 推荐设置 |
|----------|------|-----------------|-------------|---------|
| **OpenAI** | gpt-4 / gpt-4o / gpt-3.5 | **1.0** | 真 0（greedy） | 显式设 0 + seed 字段 |
| **Anthropic** | Claude 3 / 3.5 | **1.0** | 真 0（greedy） | 显式设 0 |
| **Google Gemini** | gemini-1.5-pro | **1.0** | 真 0 | 显式设 0 |
| **Cohere** | command-r-plus | 0.3 | 软替换 | 谨慎 |
| **OpenRouter** | 任意 | **0.0-1.0**（按上游） | 透传上游 | 看具体上游 |
| **Ollama**（自托管） | llama3 | 0.8 | 真 0 | 显式设 0 |

⚠️ **常见误区**：**商业 API 默认几乎都是 1.0**，如果你不显式设 temperature=0，你的"默认调用"实质上是高随机性！

---

## 二、3 大实战防御

### 2.1 防御 A：业务容错（最常用）

适用：90% 业务场景（聊天 / 总结 / 生成）

```python
# 思路：Temperature=0 + 多结果投票 + Judge 模型
def safe_invoke(query, n_samples=3):
    # 多采样投票
    samples = [llm.invoke(query, temperature=0, seed=42)
               for _ in range(n_samples)]

    # 对开放式输出用 Judge
    judge_prompt = f"选出以下 {n_samples} 个回答中最准确的：\n"
                   + "\n".join(f"[{i+1}] {s}" for i, s in enumerate(samples))
    best_idx = judge_llm.invoke(judge_prompt, temperature=0)

    return samples[int(best_idx) - 1]
```

详细方案见 [主模块 · 03-consistency-and-failure-handling](../../../11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md)。

### 2.2 防御 B：自托管确定性推理（关键场景）

适用：金融 / 法律 / 审计 / 可重现实验

```yaml
# vLLM 部署配置
vllm:
  model: meta-llama/Llama-3-70B-Instruct
  temperature: 0.0
  seed: 42
  enforce_eager: true           # 禁用 CUDA graph
  max_num_seqs: 1               # 固定 batch size = 1
  gpu_memory_utilization: 0.9
```

```python
# 调用侧
import vllm
llm = vllm.LLM(model="...", seed=42, enforce_eager=True)
output = llm.generate(["..."], sampling_params=vllm.SamplingParams(
    temperature=0.0,
    seed=42,
    max_tokens=100,
))
# → 在固定 batch=1 + seed=42 下，理论可重现
```

**限制**：
- ⚠️ 不同 GPU 型号（A100 vs H100）仍有微小差异
- ⚠️ 不同 vLLM 版本间行为可能漂移
- ⚠️ batch_size > 1 时浮点非结合问题重现

### 2.3 防御 C：漂移监控（生产必备）

```python
# 每日采样 + cosine embedding 监控
def drift_monitor(prompt, n_samples=10):
    samples = [llm.invoke(prompt, temperature=0)
               for _ in range(n_samples)]

    # 算 pairwise cosine
    from sentence_transformers import SentenceTransformer
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = encoder.encode(samples)

    # 平均相似度
    import numpy as np
    sims = []
    for i in range(len(samples)):
        for j in range(i+1, len(samples)):
            sim = np.dot(embeddings[i], embeddings[j]) / \
                  (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))
            sims.append(sim)

    avg_sim = np.mean(sims)

    # SLO: avg_sim > 0.95 算稳定
    if avg_sim < 0.95:
        alert(f"⚠️ LLM 输出漂移: avg_sim={avg_sim:.3f}, 触发 SLO")
    return avg_sim
```

---

## 三、面试话术（90 秒版本）

### 题目：Temperature=0 输出 100% 一样吗？

**高分答案（4 层递进，60-90 秒）**：

```text
1. 一句话定位（10 秒）：
   "Temperature=0 不等于完全确定。
   这是 LLM 工程最常见的误区之一。"

2. 5 大根因速览（40 秒）：
   "为什么？5 大根因：
   ① GPU 浮点非结合 —— 同 batch size ≠ 同浮点路径，
      1e-7 量级差异偶尔改变 argmax
   ② Provider 端默认值 —— OpenAI/Anthropic 默认都是 1.0，
      即使你设 0，部分 SDK 内部替换成 1e-6
   ③ Seed 字段失效 —— OpenAI seed 只保证 best_of 内一致，
      跨调用、重启进程都可能失效
   ④ 模型版本升级 —— gpt-4 → 4-0314 → 4-1106 → 4o，
      行为漂移；版本号很关键
   ⑤ Router 负载均衡 —— 大厂 API 多实例路由，
      同 prompt 命中不同 backend → 不同 KV cache 路径"

3. 3 大防御 + 权衡（20 秒）：
   "3 大防御：
   ① 业务容错（90% 场景）—— 多采样投票 + Judge 模型
   ② 自托管确定性推理 —— vLLM + 固定 batch=1 + seed，最接近'真 0'
   ③ 漂移监控 —— 每日 cosine embedding 监控，< 0.95 告警
   实战：商业 API 永远要假设'小幅波动'，
   关键场景才上自托管"

4. 权衡视角（20 秒）：
   "但完全确定性也不总是 desired：
   - 创意场景反而要 temperature > 0 增加多样性
   - Self-Consistency 也需要小幅波动才能采样多个答案
   - 反例：把所有 LLM 调用都设 0 → 失去 LLM 多样性优势
   - 实战原则：QA / 摘要类设 0 + 容错；
   创意 / 探索类保持 0.7-1.0 才有惊喜"
```

---

## 四、面试反问（让候选人反客为主）

```text
Q1：贵司目前用哪个 Provider？默认 temperature 是多少？
    → 没显式设：追问"意识到默认是 1.0 吗？" = 面试官加分题
Q2：贵司 LLM 输出有监控吗？用什么指标？
    → 答 embedding cosine 监控 = 高分
Q3：贵司对 LLM 输出的一致性 SLO 是多少？
    → 99% 以上 + 漂移告警 = 高分
Q4：贵司用过 seed 字段吗？理解其限制吗？
    → 答"只保证 best_of 内一致" = 高分
Q5：贵司 LLM 是否自托管？用的哪个推理框架？
    → vLLM + SGLang + TensorRT-LLM = 一线实践
```

---

## 🔗 系列导航表（13.split-hairs · 11.ai 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [agent-dag-vs-react](../agent-dag-vs-react/README.md) | Agent DAG vs ReAct | ⭐⭐⭐⭐ |
| [agent-memory-classification](../agent-memory-classification/README.md) | Agent 记忆 4 类 | ⭐⭐⭐⭐ |
| [agent-performance-evaluation](../agent-performance-evaluation/README.md) | Agent 评估指标 | ⭐⭐⭐⭐ |
| [ai-coding-roi](../ai-coding-roi/README.md) | AI 编程 ROI | ⭐⭐⭐ |
| [claude-code-agentic-search](../claude-code-agentic-search/README.md) | Claude Code 搜索模式 | ⭐⭐⭐⭐ |
| [context-engineering](../context-engineering-interview/README.md) | Context Engineering | ⭐⭐⭐⭐⭐ |
| [dropout-in-llm](../dropout-in-llm/README.md) | LLM Dropout | ⭐⭐⭐ |
| [function-calling](../function-calling/README.md) | Function Calling | ⭐⭐⭐⭐⭐ |
| [hallucination](../hallucination/README.md) | 幻觉治理 | ⭐⭐⭐⭐⭐ |
| [long-context-agent-strategy](../long-context-agent-strategy/README.md) | 长上下文策略 | ⭐⭐⭐⭐ |
| [prompt-engineering](../prompt-engineering/README.md) | 8 种核心技巧 + 注入防御 | ⭐⭐⭐⭐ |
| [rag](../rag/README.md) | RAG 架构 | ⭐⭐⭐⭐⭐ |
| [transformer](../transformer/README.md) | Transformer 原理 | ⭐⭐⭐⭐⭐ |
| [production-thinking-5q](../production-thinking-5q/README.md) | 5 个灵魂拷问 | ⭐⭐⭐⭐⭐ |
| **temperature-zero-myth**（本篇）| Temperature=0 仍变化的 5 大根因 | ⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [11.ai · 03-consistency-and-failure-handling](../../../11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md) — 不一致与失败处理 + 5 大根因 + 实战防御 + Self-Consistency 投票 + Judge 模型

---

## 🔗 相关章节（互链）

- [12.story · 02-system-architecture-evolution](../../../12.story/02-system-architecture-evolution.md) — 餐厅叙事
- [11.ai · 11.ai/02-technology-stack/prompt-engineering](../../../11.ai/02-technology-stack/prompt-engineering/README.md) — 温度参数对 Prompt 影响

---

> 📅 2026-07-13 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐ · 5 大根因 + 3 大防御 + 90 秒话术 + 15 兄弟导航

← [返回: 咬文嚼字 · 11.ai](../README.md)
