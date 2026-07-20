<!--
module:
  parent: ai
  slug: ai/frameworks
  type: article
  category: 主模块子文章
  summary: AI/LLM 应用框架选型全景（LangChain / LlamaIndex / Spring AI / Dify / Coze）
-->

# AI/LLM 应用框架选型

> ⬅️ [返回 L3 工程实践](../README.md)

> **一句话定位**：LLM 应用框架 = **Prompt 编排 + 工具调用 + 记忆管理 + RAG + Agent 编排**的脚手架。从 LangChain 的"瑞士军刀"到 Dify 的"低代码"，框架选择决定 80% 的开发效率。

---

## 🎯 学习目标

完成本节后，你能够：

- **5 类框架分类**：编程框架 / 智能体框架 / 低代码平台 / 编排工具 / 训练框架
- **选型决策树**：根据场景（复杂度 / 团队 / 部署）选对框架
- **避坑指南**：识别 LangChain 的过度抽象陷阱、Dify 的企业版锁定

---

## 📊 5 类框架全景

| 类型 | 代表 | 适用场景 | 学习曲线 | 企业采用 |
|------|------|---------|---------|---------|
| **编程框架** | LangChain / LlamaIndex | 复杂 RAG / Agent / 多链编排 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Agent 框架** | LangGraph / AutoGen / CrewAI | 多 Agent 协作 / 状态机 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **低代码平台** | Dify / Coze / 阿里云百炼 | 业务团队 / 快速验证 | ⭐⭐ | ⭐⭐⭐⭐ |
| **编排工具** | Spring AI / Semantic Kernel | 企业 Java 集成 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **训练框架** | HuggingFace Transformers / DeepSpeed / vLLM | 模型微调 / 推理优化 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🛠️ 主流框架对比

### LangChain vs LlamaIndex

| 维度 | LangChain | LlamaIndex |
|------|-----------|------------|
| 核心定位 | LLM 应用通用编排 | RAG 专用数据框架 |
| 抽象层级 | 高（Chain / Agent / Tool） | 中（Index / Query / Retriever） |
| 数据接入 | 100+ connector | 100+ connector（更专） |
| Agent 能力 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | 陡 | 平缓 |
| 适用场景 | 复杂 Agent / 多链 | RAG 检索增强为主 |

### Spring AI vs LangChain（Java 团队选型）

| 维度 | Spring AI | LangChain |
|------|-----------|-----------|
| 语言 | Java / Kotlin | Python 为主 |
| 集成 Spring Boot | ⭐⭐⭐⭐⭐ 原生 | 需独立服务 |
| 多模型支持 | OpenAI / Azure / HuggingFace / 国产模型 | 100+ 模型 |
| RAG 抽象 | ETL + Vector Store + Chat Client | Document Loader + Retriever + Chain |
| 适合团队 | 已有 Java 技术栈 | 已有 Python 技术栈 |

---

## 🌟 选型决策树

```
Q1: 团队主语言？
├── Java     → Spring AI
├── Python   → Q2
└── 无偏好   → 低代码（Dify / Coze）

Q2: 场景复杂度？
├── 简单 RAG / 客服          → LlamaIndex
├── 复杂 Agent / 工具调用    → LangChain
├── 多 Agent 协作             → LangGraph / AutoGen
└── 企业级复杂业务            → LangChain + 自研封装

Q3: 部署形态？
├── 云 SaaS       → Dify 云 / Coze
├── 私有化        → Dify 社区版 / 自研 LangChain 服务
└── 端侧 / 边缘   → Ollama + 自研
```

---

## 📚 子专题导航

| 专题 | 核心内容 |
|------|---------|
| [深度学习框架](deep-learning/README.md) | PyTorch / TensorFlow / MindSpore / PaddlePaddle 对比与选型 |
| [大模型应用开发框架](llm-app/README.md) | LangChain / LangChain4j / Spring AI / LlamaIndex 选型 |
| [LangGraph 迁移](langgraph-migration/README.md) | 从 LangChain 线性 Chain 迁移到显式状态图编排 |

---

## 🔗 兄弟章节

- **L2 栈**：[LLM 驾驭演进史](../../04-architecture/llm-control-evolution/README.md)
- **L3 同级**：[本地部署](../local-deployment/README.md) / [Spring AI vs Dify](../../04-architecture/spring-ai-vs-dify.md)
- **训练框架**：[推理引擎选型](../../../13.split-hairs/11.ai/inference-engine-selection/README.md) / [本地部署 open-webui](../local-deployment/open-webui/README.md)

---

## ⚠️ 高频误区

| 误区 | 真相 |
|------|------|
| ❌ LangChain 是行业标准 | ✅ LangChain 是过度抽象代表，LlamaIndex 在 RAG 场景更聚焦 |
| ❌ Dify 等低代码 = 不专业 | ✅ 80% 企业 AI 应用用低代码平台落地，复杂度≠专业 |
| ❌ Spring AI = LangChain Java 版 | ✅ Spring AI 是 Spring 生态的 LLM 集成，抽象更克制 |

← 返回 [工程实践](../README.md)

← [返回: AI 知识体系](../README.md)