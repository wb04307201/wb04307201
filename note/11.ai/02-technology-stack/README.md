<!--
module:
  parent: ai
  slug: ai/tech-stack
  type: article
  category: 主模块子文章
  summary: LLM 技术栈
-->

# LLM 技术栈

## 引言：反直觉代码

LLM 技术栈 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

← 返回 [总览](../README.md)

> 从模型架构到应用编排，全景理解大语言模型生态。

## 子目录

| 目录 | 内容 |
|------|------|
| [concept-map](concept-map/) | **LLM 技术栈全景** — 6大层61个核心概念，含Mermaid架构图、选型指南、生产部署检查清单 |
| [multimodal](multimodal/) | 多模态感知-认知统一架构、跨模态特征对齐、多模态交互体验优化 |
| [memory-estimation](memory-estimation/) | 大模型显存估算指南 — Transformer/MoE/Mamba 三大架构的训练/推理显存公式 |
| [prompt-engineering](prompt-engineering/) | **Prompt 工程** — 8 种核心技巧（Zero-shot/Few-shot/CoT）+ 注入防御 + 调试优化 + 子目录：模板、系统提示、创意注释 |
| [context-engineering](context-engineering/) | **Context Engineering** — Prompt → Context 范式转移、4 大原则、Lost in Middle、Context Window 限制 |
| [function-calling](function-calling/) | **Function Calling / Tool Use** — OpenAI / Claude 协议对比、多轮编排、5 大场景、5 大安全陷阱 |
| [token-billing](token-billing/) | **Token 与计费** — BPE / WordPiece / SentencePiece、上下文窗口、计费模型、Token 优化 |

## 学习路径

建议顺序：concept-map（全局认知）→ multimodal（感知扩展）→ memory-estimation（资源规划）→ **Prompt → Context → Function Calling → Token 计费**（AI 工程 4 阶段演进）。

## 相关章节

- 上游：[L1 基础概念](../01-fundamentals/) → **L2 技术栈** → [L3 工程实践](../03-engineering/)
- 关联：[04.system-design](../../04.system-design/) — 系统设计（AI 系统也遵循通用设计原则）
- 面试：[13.split-hairs AI 新概念](../../13.split-hairs/11.ai/README.md) — AI 面试深挖（精炼版）
