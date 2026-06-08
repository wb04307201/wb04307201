# 长 Context + Prompt Caching：2025 的甜蜜区

> ⬅️ [返回目录](README.md) | 上一篇：[LLM Wiki 模式](README1.md) | 下一篇：[生产级 RAG](README3.md)

---

## 🎯 一句话定位

**几百份文档内的最优解**——不建向量库、不切 chunk、不搞 embedding，全塞 prompt，靠 Prompt Caching 把成本压到 1/10。  
**Anthropic 官方建议**：知识库 < 200K tokens（约 500 页 A4 / 75 万中文字）时，**直接塞 prompt + Caching**，比建 RAG 更省。

---

## ✅ 适用 vs ❌ 不适用

| ✅ 适用 | ❌ 不适用 |
|:--|:--|
| 文档数量 < 200 份 | 文档 > 200 万 token |
| 知识相对稳定（缓存长期命中） | 文档每天变（缓存频繁失效） |
| 单次查询成本敏感 | 实时性要求极高（强需要最新内容） |
| 团队工程资源紧张 | 文档包含大量图片 / 多模态且超长 |
| 想要"先跑起来再优化" | 强合规要求（需追溯每条引用源） |

---

## 🧠 核心原理

### 1. 上下文窗口的指数增长

| 模型 | Context 窗口 | ≈ 中文字数 | ≈ A4 页（500 字/页） |
|:--|:--|:--|:--|
| Claude Sonnet 4.5 | 1M tokens | 75 万 | 1500 页 |
| Gemini 1.5 Pro | 2M tokens | 150 万 | 3000 页 |
| GPT-4.1 | 1M tokens | 75 万 | 1500 页 |
| Claude 3.5 Sonnet | 200K tokens | 15 万 | 300 页 |

**实操换算**：200 份文档 × 平均 3,000 字 = 60 万字 → **全部装下**。

> 💡 **甜蜜区提醒**：在 200 份文档、150 万字以内，**别建 RAG**——直接塞 prompt。

### 2. Prompt Caching 工作机制

```mermaid
flowchart LR
    A["📚 知识文档<br/>(100K tokens)"] -->|首次写入<br/>$3.75 / MTok| Cache[("💾 Prompt Cache")]
    Cache -->|后续读取<br/>$0.30 / MTok| B["👤 用户提问"]
    B --> C["🧠 LLM 生成回答"]

    classDef cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class Cache cache
```

**关键定价**（以 Claude 3.5 Sonnet 为例）：

| 操作 | 价格 | 对比 |
|:--|:--|:--|
| 基础 Input | $3 / MTok | 100% |
| Cache Write（写入） | $3.75 / MTok | +25% 溢价 |
| **Cache Read（读取）** | **$0.30 / MTok** | **仅 10%（-90%）** |
| Output | $15 / MTok | — |

### 3. 真实数据：Anthropic 官方用例

| 场景 | 延迟（无缓存） | 延迟（有缓存） | 成本下降 |
|:--|:--|:--|:--|
| 与一本书对话（100K token 缓存） | 11.5s | 2.4s（-79%） | **-90%** |
| Many-shot 提示（10K token） | 1.6s | 1.1s（-31%） | -86% |
| 多轮对话（10 轮 + 长 system prompt） | ~10s | ~2.5s（-75%） | -53% |

> 📌 **核心收益**：第二次调用起，成本降到 1/10、延迟降到 1/4。

---

## ⚠️ 陷阱：Lost in the Middle（针在草堆）

长 context ≠ 等同短 context。**关键信息如果放在中间地带，召回率会显著掉**。

### 实验数据

研究显示（Lost in the Middle, Liu et al. 2023）：

```
位置：  [开头]  [1/4]   [中间]   [3/4]   [结尾]
准确率：  高     中      低       中      高
```

### 解法

| 策略 | 说明 |
|:--|:--|
| **重要文档放两头** | 把关键参考资料、首尾分别放 |
| **控制在 200 份甜蜜区** | 别贪多，< 200 份文档时这个效应最弱 |
| **结构化提示** | 显式分块、加索引编号（"参考资料 1：xxx"） |
| **引用跟踪** | 让模型在回答中标注引用编号，便于事后校验 |

### 不适用场景识别

如果你的需求命中以下任意一条，**别用长 Context，请直接跳到 [生产级 RAG](README3.md)**：

- 文档量 > 200 万 token（塞不下）
- 文档每天变（缓存命中率低，成本反升）
- 强需要逐条引用源（合规场景）

---

## 🛠️ 工具链

| 工具 | 用途 | 备注 |
|:--|:--|:--|
| **Anthropic API** | Claude 系列 + Prompt Caching | 已 GA |
| **Amazon Bedrock** | Claude 缓存预览 | 跨云 |
| **Google Vertex AI** | Claude 缓存预览 | 跨云 |
| **Gemini API** | Gemini 2M context + 隐式缓存 | 缓存策略不同 |
| **OpenAI API** | 暂无 prompt caching，但有 Assistants 自动管理 | — |

### 简单实现（Anthropic SDK）

```python
import anthropic

client = anthropic.Anthropic()

# 第一次调用：写入缓存
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "你是知识库助手...",
        },
        {
            "type": "text",
            "text": "以下是完整知识库内容：\n\n" + KNOWLEDGE_BASE,  # 100K tokens
            "cache_control": {"type": "ephemeral"},  # 标记可缓存
        }
    ],
    messages=[{"role": "user", "content": "请介绍启明 11"}],
)

# 第二次调用：自动命中缓存，成本 -90%
response2 = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[...],  # 同样的 system prompt
    messages=[{"role": "user", "content": "它的电池多大？"}],
)
```

---

## 💡 实战经验

### 1. 何时升级到 RAG？

观察以下信号，出现 2 个以上就该考虑升级：

- [ ] 文档超过 200 份
- [ ] 关键信息在中间地带频繁被忽略
- [ ] 缓存命中率 < 50%
- [ ] 每次输出都需要引用源（合规）
- [ ] 文档每天变

### 2. 与"塞不下"场景的衔接

如果某天发现 200 份要塞不下了，**不要立刻全量迁到 RAG**：

```
第一步：拆分为"常用 200 份 + 偶尔查 X 份"两批
第二步：常用批用 Caching，偶尔批用 RAG
第三步：观察一段时间，再决定全量迁移
```

### 3. 客户案例：Notion

> *"We're excited to use prompt caching to make Notion AI faster and cheaper, all while maintaining state-of-the-art quality."*
> — Simon Last, Co-founder at Notion

Notion AI 把 Prompt Caching 用于 AI 助手场景，实现了"又快又便宜的内部运营"。

---

## 🤔 思考

1. **算账练习**：你手头有多少份知识文档？总字数多少 token？够塞几次 Context？
2. **缓存命中率估计**：你的知识库更新频率如何？缓存能维持几天有效？
3. **什么时候你会从甜蜜区溢出**：从 200 份 / 150 万字这个甜蜜区看，你的项目离溢出还有多远？

---

> ⬅️ [返回目录](README.md) | 上一篇：[LLM Wiki 模式](README1.md) | 下一篇：[生产级 RAG](README3.md)
