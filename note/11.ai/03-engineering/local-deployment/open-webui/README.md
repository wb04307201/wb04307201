<!--
module:
  parent: ai
  slug: ai/open-webui
  type: article
  category: 主模块子文章
  summary: Open WebUI — Ollama 配套可视化前端（多用户 / RAG / 工具调用）
-->

# Open WebUI

> ⬅️ [返回本地部署](../README.md)

> **一句话定位**：Open WebUI（前身 Ollama WebUI）= Ollama / OpenAI API 的**自托管 ChatGPT 替代品**——支持多用户、对话历史、知识库（RAG）、工具调用、模型对比，企业内部"私有 ChatGPT"首选。

---

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| **多模型接入** | Ollama / OpenAI / 任意 OpenAI 兼容 API |
| **多用户 + 权限** | RBAC、用户组、审计日志 |
| **对话历史** | 持久化、标签、搜索、导出 |
| **RAG 知识库** | 上传文档 → 自动 Embedding → 检索增强 |
| **工具调用** | Function Calling + Web Search + 代码执行 |
| **Web 浏览** | 内置 Web Search（Serper / SerpAPI / Bing） |
| **语音输入输出** | Whisper 语音识别 + TTS |
| **图像生成** | 集成 Stable Diffusion / DALL-E |

---

## 🚀 Docker 部署（5 分钟上线）

```bash
# GPU 版本（推荐，需要 NVIDIA 驱动）
docker run -d -p 3000:8080 \
  --gpus all \
  -v open-webui-data:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:ollama

# 同时启动 Ollama（如果还没有）
docker run -d -p 11434:11434 \
  --gpus all \
  -v ollama-data:/root/.ollama \
  --name ollama \
  --restart always \
  ollama/ollama

# 纯 CPU / 仅 OpenAI API
docker run -d -p 3000:8080 \
  -e OPENAI_API_KEY=sk-xxx \
  -e OPENAI_API_BASE_URL=https://api.openai.com/v1 \
  -v open-webui-data:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

访问 `http://localhost:3000`，首次注册即管理员。

---

## 🧩 RAG 知识库实战

```
步骤 1: Workspace → Documents → Upload
步骤 2: 上传 PDF / Word / Markdown / 代码文件
步骤 3: 系统自动 Embedding（默认 sentence-transformers）
步骤 4: 在对话中 @ 文件名 即可引用知识库
步骤 5: 或开启 "Knowledge" 全局检索（对话时自动 RAG）
```

**支持的文档类型**：PDF、Word、Markdown、TXT、HTML、EPUB、CSV、代码（多语言）。

**高级配置**：
- **Embedding 模型**：可换 Ollama 的 nomic-embed-text
- **Chunk 大小**：默认 1000 tokens，重叠 100
- **检索 Top-K**：默认 4

---

## 🔌 接入多模型示例

```yaml
# config.yaml
OLLAMA_BASE_URL: http://ollama:11434
OPENAI_API_KEY: sk-xxx
OPENAI_API_BASE_URL: https://api.deepseek.com/v1

# 自定义模型（任意 OpenAI 兼容端点）
- name: DeepSeek-V3
  base_url: https://api.deepseek.com/v1
  api_key: sk-xxx
  model_id: deepseek-chat
```

---

## 🔐 企业部署建议

| 部署形态 | 适用 | 关键配置 |
|---------|------|---------|
| **单机演示** | 个人 / 团队试点 | Docker 一键 |
| **生产 K8s** | 企业内多用户 | Helm Chart + 持久化 + LDAP 集成 |
| **混合云** | 数据敏感 | Open WebUI + 私有 Ollama 集群 |

**安全配置**：
- `WEBUI_AUTH=true` 开启登录
- `ENABLE_SIGNUP=false` 关闭公开注册
- `DEFAULT_USER_ROLE=pending` 默认待审核
- 配合 Nginx 反代 + HTTPS

---

## 🔗 兄弟章节

- **本地部署**：[Ollama 实战](../README.md)
- **推理引擎**：[vLLM vs Ollama](../../../../13.split-hairs/11.ai/inference-engine-selection/README.md)
- **RAG 体系**：[LLMOps 章节](../../../08-llmops/README.md)

---

## ⚠️ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 模型列表为空 | Ollama 未连接 | 检查 `OLLAMA_BASE_URL` 网络可达 |
| RAG 无效果 | Embedding 未完成 | Workspace → Documents 看状态 |
| 高并发卡顿 | 单实例瓶颈 | K8s 部署多副本 + Redis 会话共享 |
| 中文回答质量差 | 模型本身弱 | 换 Qwen / DeepSeek 中文强模型 |

← 返回 [本地部署](../README.md)

← [返回: 本地部署](../README.md)