<!--
module:
  parent: ai
  slug: ai/local-deployment
  type: article
  category: 主模块子文章
  summary: 本地部署
-->

# 本地部署

---

← 返回 [工程实践](../README.md)

## 子目录

| 目录 | 内容 |
|------|------|
| [ollama](ollama/) | Ollama — 本地 LLM 运行管理工具（含 [Linux 部署方案](ollama/linux-deploy/)） |
| [open-webui](open-webui/) | Open WebUI — 开源自托管 AI 交互平台，兼容 Ollama / OpenAI API |
| [iflow-cli](iflow-cli/) | iFlow CLI — 终端 AI 助手，集成免费模型，支持代码分析与自动化 |

## 快速上手

```mermaid
graph LR
    A["Ollama<br/>运行本地 LLM"] --> B["Open WebUI<br/>Web 交互界面"]
    A --> C["iFlow CLI<br/>终端 AI 助手"]
```

## 相关章节

- 父级：[L3 工程实践](../README.md) — 框架 / 计算平台 / 本地部署 / AI 平台
- 关联：[05.tools Docker](../../../05.tools/02-docker/) — 容器化部署基础
- 关联：[11.ai/training](../../training/README.md) — Spring AI Agent 16 课实战
- 🆕 **工业部署对比**：[../ai-platforms/vllm-vs-ollama/](../ai-platforms/vllm-vs-ollama/README.md) — Ollama 适合本地/边缘，工业生产用 vLLM；选型决策树 + PagedAttention 原理 + 4 引擎对比

← [返回: AI 知识体系 · local-deployment](README.md)
