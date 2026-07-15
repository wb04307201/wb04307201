<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/03-consistency-and-failure-handling
  type: topic
  category: 一致性与失败处理
  summary: Self-Consistency 投票 + Judge 模型 + 重试预算 + 多结果聚合 + 失败模式（连续 3 次不一致怎么办）
-->

# 不一致与失败处理 · Self-Consistency 投票

> **一句话**：模型本身有随机性，**3 次重试可能都错**。必须用「Self-Consistency 投票 + Judge 模型 + 重试预算」才能挑出最一致的答案——raw 重试是错觉。

← [返回: 大模型思维工程](../README.md)

---

## 1. 为什么"重试"解决不了一致性问题？

```
用户问："北京人口多少？"

模型第 1 次："2000 万"     ← 幻觉
模型第 2 次："3000 万"     ← 幻觉
模型第 3 次："5000 万"     ← 幻觉

重试 3 次，全部错误——不是网络问题，是模型本身在"自由发挥"。
```

**根因**：LLM 是概率模型，temperature > 0 时同样 prompt 不同次给出不同回答。

**重试错觉**：
- 网络层错误（5xx、超时） → 重试有效
- 业务层错误（幻觉、事实错误）→ 重试通常无解

---

## 2. Self-Consistency 投票：3 重机制

### 2.1 机制 1：多次采样

```python
def self_consistency(query, n_samples=5, temperature=0.7):
    samples = [llm.invoke(query, temperature=temperature) for _ in range(n_samples)]
    return samples
```

### 2.2 机制 2：结果聚合

```python
from collections import Counter

def majority_vote(samples):
    # 字符串投票
    counter = Counter(samples)
    most_common, count = counter.most_common(1)[0]
    return most_common, count / len(samples)
```

**问题**：开放式回答（"写一篇文章"）无法字符串投票。

### 2.3 机制 3：Judge 模型（语义投票）

```python
def semantic_vote(samples, judge_llm):
    """用强模型当裁判，从多个回答中选最佳"""
    prompt = f"""以下是对同一问题的 {len(samples)} 个回答，请评估并选出**最准确**的：

回答：
{chr(10).join(f"[{i+1}] {s}" for i, s in enumerate(samples))}

要求：
- 准确性优先
- 引用证据
- 选择最一致的事实

请输出最佳答案编号 + 理由。"""
    
    return judge_llm.invoke(prompt)
```

**优势**：开放式回答也能选最佳

---

## 3. 实战：3 个采样策略

### 3.1 高温度采样（Creative tasks）

```python
# temperature=0.8，多样性高
samples = [llm.invoke(query, temperature=0.8) for _ in range(5)]
best = judge_llm.choose_best(query, samples)
```

**适用**：文案生成、创意写作

### 3.2 低温度采样（Fact tasks）

```python
# temperature=0.2，趋同性强
samples = [llm.invoke(query, temperature=0.2) for _ in range(3)]
best = majority_vote(samples)
```

**适用**：事实问答、分类

### 3.3 混合投票（推荐）

```python
def hybrid_vote(query, judge_llm):
    # 低温度 3 次（事实部分）
    factual = [llm.invoke(query, temperature=0.2) for _ in range(3)]
    # 高温度 3 次（表达部分）
    creative = [llm.invoke(query, temperature=0.8) for _ in range(3)]
    # Judge 综合
    return judge_llm.choose_best(query, factual + creative)
```

---

## 4. Judge 模型设计

### 4.1 选择 Judge 模型

| 场景 | Judge 选择 |
|------|-----------|
| 通用质量 | GPT-4 / Claude 3.5 Sonnet |
| 业务领域 | 微调的 domain-judge 模型 |
| 成本敏感 | 开源 Llama-3-70B / Qwen-72B 自部署 |

### 4.2 Judge Prompt 模板

```
你是 [领域] 资深评审，请评估以下回答：

【问题】
{query}

【候选回答】
{candidates}

【评估维度】(10 分制)
1. 准确性 (40%)：事实是否正确
2. 完整性 (30%)：是否覆盖关键点
3. 一致性 (20%)：逻辑是否自洽
4. 表达 (10%)：是否清晰流畅

【输出格式】
- 每个回答评分 + 理由
- 选出最佳，输出编号 + 1 句话理由
```

### 4.3 Judge 失败兜底

```python
def safe_judge(query, samples, judge_llm, fallback_model):
    try:
        return judge_llm.choose_best(query, samples)
    except (Timeout, RateLimit):
        # Judge 也挂了 → 退而求其次
        return fallback_model.choose_best(query, samples)
```

---

## 5. 重试预算

### 5.1 区分重试类型

```python
class RetryPolicy:
    NETWORK_RETRY = 3      # 网络错误重试 3 次
    RATE_LIMIT_RETRY = 5   # 限流重试 5 次（退避）
    VALIDATION_RETRY = 2   # 校验失败重试 2 次（重新生成）
    CONSISTENCY_RETRY = 3  # 不一致需要 3 样本（不算重试，是聚合）
    
    @classmethod
    def get_retry_budget(cls, error_type):
        policy = {
            "network": 3,
            "timeout": 3,
            "rate_limit": 5,
            "validation": 2,
            "consistency": 3,  # 强制采样数
        }
        return policy.get(error_type, 0)
```

### 5.2 指数退避

```python
import random

def retry_with_backoff(fn, max_retries=3, base_delay=1):
    for i in range(max_retries):
        try:
            return fn()
        except (NetworkError, RateLimitError) as e:
            if i == max_retries - 1:
                raise
            # 指数退避 + 抖动
            delay = base_delay * (2 ** i) + random.uniform(0, 1)
            time.sleep(delay)
```

---

## 6. 5 大失败模式

| 模式 | 触发 | 修复 |
|------|------|------|
| **幻觉** | 模型自由发挥 | Self-Consistency + Judge + RAG 兜底 |
| **格式错误** | 输出不符合 JSON | Output Parser + retry with format hint |
| **上下文溢出** | 输入超 token | truncate + chunking |
| **超时** | 推理慢 | 双 timeout + 降级 |
| **成本爆炸** | 重试/循环无上限 | 3 道 quota 强制硬限 |

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：所有失败都盲目重试

- 错：网络错 + 幻觉都重试 3 次
- 对：网络错重试 + 幻觉**不重试**改用 Self-Consistency

### ⚠️ 反模式 2：Self-Consistency 没用 Judge

- 错：5 次采样后 majority_vote，但回答是开放文本
- 对：开放回答必须用 Judge 模型

### ⚠️ 反模式 3：Judge 模型选错

- 错：用同款小模型当 Judge（自己评自己）
- 对：Judge 用更强 / 不同模型（GPT-4 judge 7B 输出）

### ⚠️ 反模式 4：忽视 Judge 自身失败

- 错：Judge 抛超时 → 系统崩
- 对：Judge 兜底（fallback 模型 + 默认选择）

### ⚠️ 反模式 5：投票数太少

- 错：2 次采样选最常出现
- 对：至少 3 次（最好 5-7 次），统计显著

---

## 8. 一句话总结

> **LLM 一致性 ≠ 重试——raw 重试失败，**Self-Consistency 投票 + Judge 模型**才能挑出最佳。3 次不一致不可怕，可怕的是没有 Judge / 没有重试预算。

---

## 9. Temperature=0 仍可变的 5 大根因 + 3 大防御（高频误区题）

> ⚠️ **常见误区**：很多人以为 Temperature=0 = 完全确定。其实生产中 5 大根因会让输出仍有微小波动。面试速查版见 [13.split-hairs · temperature-zero-myth](../../../13.split-hairs/11.ai/temperature-zero-myth/README.md)。

### 9.1 5 大根因速查表

| # | 根因 | 影响范围 | 实战表现 |
|---|------|---------|---------|
| 1 | **GPU 浮点非结合**（float reduction 顺序） | 所有 GPU 推理 | 同 prompt + 同模型 + 不同 batch size → 1e-7 量级差异 → 偶发 argmax 不同 |
| 2 | **Provider 默认值覆盖**（OpenAI / Anthropic 默认 ≠ 0） | 商业 API | OpenAI gpt-4 / Anthropic Claude 默认都是 1.0；"0" 在某些 SDK 内部被替换成 0.0001 |
| 3 | **Seed 字段失效**（OpenAI seed ≠ 跨调用持久化） | OpenAI API | seed 只保证 `best_of` 内一致；跨调用不一定；重启进程就失效 |
| 4 | **模型版本升级**（API 模型快照漂移） | 商业 API | gpt-4 → gpt-4-0314 → gpt-4-0613 行为不同；gpt-4o 系列每月微调 |
| 5 | **Router / 负载均衡**（不同 backend 实例） | 大厂 API | OpenAI / Anthropic 多实例路由，同 prompt 命中不同实例 → 不同 KV cache 路径 → 不同输出 |

### 9.2 Provider 默认 Temperature 速查表

| Provider | 模型 | 默认 Temperature | 推荐 |
|----------|------|-----------------|------|
| **OpenAI** | gpt-4 / gpt-4o / gpt-3.5 | **1.0** | 显式设 0 + seed 字段 |
| **Anthropic** | Claude 3 / 3.5 | **1.0** | 显式设 0 |
| **Google Gemini** | gemini-1.5-pro | **1.0** | 显式设 0 |
| **Cohere** | command-r-plus | 0.3 | 谨慎 |
| **OpenRouter** | 任意 | 透传上游 | 看具体上游 |
| **Ollama**（自托管） | llama3 | 0.8 | 显式设 0 |

⚠️ **商业 API 默认几乎都是 1.0** — 不显式设 = 高随机性。

### 9.3 3 大防御

#### 9.3.1 防御 A：业务容错（90% 场景）

→ 见上文 **第 2、3 节** 的 Self-Consistency 投票 + Judge 模型。

#### 9.3.2 防御 B：自托管确定性推理（关键场景）

```yaml
# vLLM 部署配置（关键参数）
vllm:
  temperature: 0.0
  seed: 42
  enforce_eager: true           # 禁用 CUDA graph
  max_num_seqs: 1               # 固定 batch size = 1（关键！）
```

```python
import vllm
llm = vllm.LLM(model="...", seed=42, enforce_eager=True)
```

**限制**：
- ⚠️ 不同 GPU 型号（A100 vs H100）仍有微小差异
- ⚠️ 不同 vLLM 版本间行为可能漂移
- ⚠️ batch_size > 1 时浮点非结合问题重现

#### 9.3.3 防御 C：漂移监控（生产必备）

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def drift_monitor(prompt, n_samples=10):
    samples = [llm.invoke(prompt, temperature=0)
               for _ in range(n_samples)]
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = encoder.encode(samples)

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

### 9.4 实战原则（什么时候用什么策略）

| 业务类型 | 策略 | 原因 |
|---------|------|------|
| **QA / 摘要 / 抽取** | Temperature=0 + Self-Consistency | 一致性优先 |
| **聊天 / 客服** | Temperature=0.3-0.7 + 重试 | 自然交互需小幅变化 |
| **创意 / 写作** | Temperature=0.7-1.0 + 多采样 | 多样性是特征 |
| **金融 / 法律 / 审计** | 自托管 vLLM + 固定 batch + 漂移监控 | 真确定性 |
| **Agent 多步决策** | Temperature=0.0 + 业务容错 | Agent 一致性影响动作链 |

---

← [返回: 大模型思维工程](../README.md) · 上一章：[02-cost-control](02-cost-control-and-degradation.md) · 下一章：[04-timeout-and-circuit-breaker](04-timeout-and-circuit-breaker.md)
