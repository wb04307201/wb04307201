<!--
module:
  parent: ai
  slug: ai/local-deployment
  type: article
  category: 主模块子文章
  summary: LLM 本地部署全景（Ollama / vLLM / LM Studio / llama.cpp / 国产模型）
-->

# LLM 本地部署全景

> ⬅️ [返回 L3 工程实践](../README.md)

> **一句话定位**：本地部署 LLM = **绕过云 API、按 token 零成本、满足数据合规**。本节覆盖 Ollama / vLLM / LM Studio / llama.cpp 四大主流方案，以及国产模型（Qwen / DeepSeek / GLM）的本地化部署。

---

## 🎯 为什么需要本地部署？

| 场景 | 云 API | 本地部署 |
|------|--------|---------|
| **数据合规** | ❌ 数据出企业 | ✅ 全内网 |
| **成本（高频）** | ❌ 按 token 计费 | ✅ 一次部署，零边际成本 |
| **延迟** | ❌ 100-500ms 网络 | ✅ 10-50ms 推理 |
| **模型控制** | ❌ 依赖供应商 | ✅ 自由切换 / 微调 |
| **离线可用** | ❌ 需联网 | ✅ 完全离线 |

---

## 🛠️ 4 大方案对比

| 方案 | 硬件门槛 | 易用性 | 性能 | 适用 |
|------|---------|--------|------|------|
| **Ollama** | 中（16GB+ RAM） | ⭐⭐⭐⭐⭐ 一键 | ⭐⭐⭐ | 个人开发者 / 快速验证 |
| **vLLM** | 高（A100/H100） | ⭐⭐⭐ 需配置 | ⭐⭐⭐⭐⭐ 高吞吐 | 企业级生产 |
| **LM Studio** | 中（16GB+ RAM） | ⭐⭐⭐⭐⭐ GUI | ⭐⭐⭐ | 桌面用户 / 非技术 |
| **llama.cpp** | 低（8GB+ RAM） | ⭐⭐ 命令行 | ⭐⭐⭐⭐ | CPU / 边缘设备 |

---

## 🐮 Ollama 快速上手（推荐入门）

```bash
# 1. 安装（macOS / Linux 一行）
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型（首次约 5-20 分钟）
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
ollama pull deepseek-r1:7b

# 3. 运行
ollama run qwen2.5:7b

# 4. 作为 OpenAI 兼容 API
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:7b","messages":[{"role":"user","content":"你好"}]}'
```

**优势**：自动 GPU 加速、模型版本管理、Modelfile 自定义、OpenAI API 兼容。

---

## 🚀 vLLM 企业级部署

```bash
# 安装
pip install vllm

# 启动 OpenAI 兼容服务
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 32768

# 测试
curl http://localhost:8000/v1/chat/completions \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"hi"}]}'
```

**核心特性**：
- **PagedAttention**：显存利用率提升 4-24x
- **连续批处理**：吞吐量提升 23x
- **多 GPU 并行**：tensor-parallel / pipeline-parallel
- **OpenAI 兼容**：零代码迁移

---

## 💻 国产模型推荐（中文场景）

| 模型 | 参数量 | 显存需求 | 特点 |
|------|--------|---------|------|
| **Qwen 2.5** | 7B / 14B / 32B / 72B | 8-72 GB | 中文 SOTA / 工具调用 / 长上下文 |
| **DeepSeek-V3** | 671B (MoE) | 8x A100 | 数学 / 代码 / 推理强项 |
| **GLM-4** | 9B / 32B | 10-40 GB | 清华系 / 多模态 / Function Calling |
| **Yi-1.5** | 9B / 34B | 10-40 GB | 零一万物 / 长上下文 200K |
| **Baichuan 3** | 7B / 13B | 8-16 GB | 百川 / 中文对齐 |

---

## 📚 文章清单

| 主题 | 核心内容 | 阅读时长 |
|------|---------|---------|
| [Ollama 实战](ollama/README.md) | 安装 / 模型管理 / API 集成 / 性能调优 | 20 min |
| [Open WebUI 可视化](open-webui/README.md) | Ollama 配套 Web UI / 多用户 / RAG | 15 min |
| vLLM 部署 | 企业级 GPU 推理 + 性能基准 | 30 min |
| 国产模型对比 | Qwen / DeepSeek / GLM / Yi 横向评测 | 25 min |

---

## ⚠️ 选型反模式

| 反模式 | 后果 | 修复 |
|--------|------|------|
| **显存不够硬上 70B** | OOM 崩溃 | 量化（Q4/Q8）+ MoE 模型 |
| **生产用 Ollama** | 缺高并发 / 监控 | 换 vLLM / TGI |
| **本地部署闭源模型** | 违反许可证 | 选开源（Qwen / Llama） |

← 返回 [工程实践](../README.md)

← [返回: AI 知识体系](../README.md)