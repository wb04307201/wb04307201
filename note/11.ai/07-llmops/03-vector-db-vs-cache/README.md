# LLM 缓存策略：向量数据库 vs 语义缓存 vs 精确缓存

> 一份按层次梳理的 LLM 缓存速查手册：从精确缓存到语义缓存的 3 大策略。

---

## 一、为什么 LLM 需要缓存？

LLM 推理成本高昂：
- GPT-4 每次调用 $0.01 - $0.10
- 自托管 LLM 每千 Token $0.001 - $0.01
- 推理延迟 1-30 秒

**缓存可以**：
- 💰 节省 50-90% 成本
- ⚡ 降低延迟到毫秒级
- 📉 减少 API 调用限制压力

---

## 二、3 大缓存策略

| 缓存类型 | 匹配方式 | 节省成本 | 命中率 | 复杂度 |
|---------|---------|---------|--------|--------|
| **精确缓存** | 完全相同 prompt | 💰💰💰💰 | 10-30% | ⭐ |
| **语义缓存** | 语义相似 prompt | 💰💰💰 | 30-60% | ⭐⭐⭐ |
| **前缀缓存** | 共享前缀 | 💰💰 | 50-80%（长 prompt）| ⭐⭐ |

---

## 三、精确缓存（Exact Cache）

### 3.1 原理

```
请求：prompt = "什么是 RAG？"
   ↓
Redis GET key=hash(prompt)
   ↓
缓存命中 → 直接返回（零成本）
缓存未命中 → 调用 LLM → 缓存结果
```

### 3.2 实现（Redis）

```python
import hashlib
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached_llm_call(prompt: str) -> str:
    # 1. 计算 hash
    cache_key = f"llm:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    # 2. 查缓存
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)['response']
    
    # 3. 调用 LLM
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
    
    # 4. 写缓存（TTL 24 小时）
    redis_client.setex(cache_key, 86400, json.dumps({"response": result}))
    return result
```

### 3.3 局限

- ❌ "什么是 RAG？" 和 "请解释 RAG" 是不同 cache key
- ❌ 用户拼写错误 / 微小变化 → 缓存不命中
- 适合：FAQ / 标准化指令

---

## 四、语义缓存（Semantic Cache）

### 4.1 原理

```
请求：prompt = "什么是 RAG？"
   ↓
计算 prompt 的 Embedding 向量
   ↓
向量数据库中查找 Top-1 相似（cosine > 0.95）
   ↓
命中 → 返回缓存的答案
未命中 → 调用 LLM → 缓存 embedding + 答案
```

### 4.2 实现（GPTCache）

```python
from gptcache import Cache
from gptcache.adapter.api import get_similar_prompt
from gptcache.processor.pre import get_prompt
from gptcache.embedding import Onnx

# 1. 初始化缓存
cache = Cache()
cache.set_openai_key()
cache.init(
    pre_embedding_func=get_prompt,
    embedding_func=Onnx(),
    data_manager="milvus,localhost,19530"  # 向量库
)

# 2. 缓存 LLM 调用
def cached_chat(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    cache_answer = response.choices[0].message.content
    
    # 缓存
    cache.import_data([{"prompt": prompt, "answer": cache_answer}])
    return cache_answer

# 3. 查询
similar_prompts = get_similar_prompt("请解释 RAG", cache)
if similar_prompts and similar_prompts[0].distance < 0.1:  # 0.1 = 极相似
    return similar_prompts[0].answer
```

### 4.3 适用场景

- ✅ 客服问答（同一问题不同说法）
- ✅ 知识库查询（语义等价）
- ✅ 翻译 / 摘要（相似输入）
- ❌ 数学计算（输入变化大）

---

## 五、前缀缓存（Prefix Cache）

### 5.1 原理

```
Prompt 结构：
[系统提示：500 tokens] ← 共享前缀
[Few-shot 示例：1000 tokens] ← 共享前缀
[用户问题：100 tokens] ← 变化
```

**优化**：缓存共同前缀的 KV cache，复用 attention 计算。

### 5.2 实现

| 工具 | 支持 |
|------|------|
| **vLLM** | ✅ Automatic Prefix Caching |
| **SGLang** | ✅ RadixAttention |
| **TGI** | ✅ Cache-Aware |
| **Anthropic Claude** | ✅ Prompt Caching（5x 降价）|
| **OpenAI** | ❌ 不支持（但有 prompt cache）|

### 5.3 vLLM 启用

```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3-8B \
  --enable-prefix-caching        # 启用前缀缓存
```

**效果**：长 prompt（5000+ tokens）场景成本节省 50-80%。

### 5.4 Anthropic Prompt Caching

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "你是一个专业律师...",
            "cache_control": {"type": "ephemeral"}  # 标记可缓存
        }
    ],
    messages=[{"role": "user", "content": "合同违约怎么处理？"}]
)
```

---

## 六、3 大缓存策略对比

| 维度 | 精确缓存 | 语义缓存 | 前缀缓存 |
|------|---------|---------|---------|
| **原理** | Hash 匹配 | Embedding 相似度 | KV cache 复用 |
| **命中率** | 10-30% | 30-60% | 50-80%（长 prompt）|
| **节省成本** | 💰💰💰💰 | 💰💰💰 | 💰💰 |
| **实现复杂度** | ⭐ | ⭐⭐⭐ | ⭐⭐（框架支持）|
| **适用** | 标准化指令 | 客服 / 知识库 | 长 system prompt |
| **数据一致性** | ✅ 强 | ⚠️ 弱（可能返回过时）| ✅ 强 |

---

## 七、缓存策略选型

```
Q1: 输入完全相同（标准化指令）？
├── 是 → 精确缓存
└── 否 ↓

Q2: 输入有微小变化（同一问题不同说法）？
├── 是 → 语义缓存
└── 否 ↓

Q3: Prompt 很长（> 2000 tokens）且有共同前缀？
├── 是 → 前缀缓存
└── 否 → 不缓存

Q4: 答案时效性要求？
├── 强（实时数据）→ 不缓存 / 短 TTL
└── 弱（FAQ）→ 长 TTL
```

---

## 八、缓存架构设计

### 8.1 多级缓存

```
请求
  ↓
L1 精确缓存（Redis，< 1ms）
  ↓ miss
L2 语义缓存（向量库，< 100ms）
  ↓ miss
L3 LLM 调用（1-30s）
```

### 8.2 缓存更新策略

| 策略 | 说明 | 适用 |
|------|------|------|
| **TTL 过期** | 简单 | 通用 |
| **主动刷新** | 后台预热 | 高频查询 |
| **失效通知** | 数据更新时广播失效 | 强一致性 |
| **版本号** | 缓存带版本，数据更新加版本 | 推荐 |

---

## 九、实战案例

### 9.1 客服 AI 缓存

```python
# 客服系统常见问题 + 答案对
FAQ_CACHE = {
    "如何退款？": "请访问 ... 申请退款",
    "怎么联系客服？": "客服电话 400-xxx-xxxx",
    ...
}

# 命中率：60%+
# 节省：60% × LLM 成本 = 60% × $5000/月 = $3000/月
```

### 9.2 RAG + 缓存

```python
# 缓存的 key 包含 query
cache_key = f"rag:{hashlib.md5((query + top_k_docs_hash).encode()).hexdigest()}"

# 命中率：20-40%（相同问题 + 相同文档）
# 节省：20-40% LLM 成本
```

### 9.3 多轮对话 + 前缀缓存

```python
# 多轮对话的 system prompt 不变
# 启用 Anthropic Prompt Caching 后：
# 首轮：$0.003 / 1k tokens
# 后续轮：$0.0003 / 1k tokens（10x 降价）
```

---

## 十、最佳实践

1. **首选精确缓存**：最简单、最高 ROI
2. **语义缓存谨慎用**：答案可能"看起来对但其实错"
3. **长 prompt 必用前缀缓存**：5x 降价
4. **多级缓存**：L1 精确 + L2 语义 + L3 LLM
5. **监控命中率**：命中率 < 30% 说明缓存策略有问题
6. **TTL 不宜过长**：知识会过期（5 分钟 - 24 小时）
7. **缓存版本**：数据更新时缓存失效
8. **成本监控**：实时跟踪缓存节省的成本

---

← [返回 AI 知识体系总览](../../README.md) · 📅 2026-06-28