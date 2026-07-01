<!--
module:
  parent: ai
  slug: ai/engineering
  type: article
  category: 主模块子文章
  summary: AI 工程实践
-->

# AI 工程实践

## 引言：反直觉代码

AI 工程实践 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

← 返回 [总览](../README.md)

> 从框架选型到本地部署，AI 工程落地的实用指南。

## 子目录

| 目录 | 内容 |
|------|------|
| [frameworks](frameworks/) | **深度学习框架** (PyTorch/TensorFlow/MindSpore/PaddlePaddle) · **大模型应用框架** (LangChain/LangChain4j/Spring AI/LlamaIndex) |
| [compute-platforms](compute-platforms/) | 计算平台对比 — CUDA / ROCm / CANN |
| [local-deployment](local-deployment/) | 本地部署指南 — Ollama (含Linux部署方案)、Open WebUI、iFlow CLI |
| [ai-platforms](ai-platforms/) | AI平台选购指南 — Dify / Coze / n8n / FastGPT / RAGFlow 对比 |
| [claude-code-practices](claude-code-practices/) | Claude Code 实战 — OpenSpec / Spec Kit / Hooks 实践 |
| [production-agent](production-agent/) | 生产级 Agent 实战 — 编排、监控、错误恢复 |
| [harness-engineering](harness-engineering/) | **Harness Engineering** — 4 大 Harness 类型（规范/流程/工具/反馈）+ OpenSpec + 4 原则 |
| [loop-engineering](loop-engineering/) | **Loop Engineering** — 循环调用 3 大组件 + 4 大失败模式 + 5 大最佳实践 |

## 学习路径

建议顺序：frameworks（选框架）→ compute-platforms（选算力）→ local-deployment（跑起来）→ ai-platforms（选平台）→ **Harness → Loop Engineering**（AI 工程 4 阶段之 3-4 阶段）。

## 相关章节

- 上游：[L2 技术栈](../02-technology-stack/) → **L3 工程实践** → [L4 架构设计](../04-architecture/)
- 关联：[06.spring](../../06.spring/) — Spring 生态（Spring AI 的底层支撑）
- 关联：[11.ai/training](../training/README.md) — Spring AI Agent 16 课实战
- 面试：[13.split-hairs AI 新概念](../../13.split-hairs/11.ai/README.md) — Harness / Loop 面试精炼版
