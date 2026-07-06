<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/07-vs-tgi-lmdeploy
  type: topic
  category: 引擎横向对比
  summary: vLLM / TGI / LMDeploy / Ollama 4 大推理引擎在 11 个维度上的全对比表 + 推荐场景
-->

# 4 引擎横向对比 · vLLM / TGI / LMDeploy / Ollama

> **一句话**：4 个引擎没有绝对优劣，是「**生态 + 优化方向 + 部署成本**」的 trade-off。选错代价远高于选优代价。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 全维度对比表

| 维度 | **vLLM** | **TGI** | **LMDeploy** | **Ollama** |
|------|---------|---------|--------------|-----------|
| **开发方** | UC Berkeley | HuggingFace | 上海 AI Lab (书生) | Ollama Inc |
| **底层** | PyTorch + 自研 CUDA kernel | Rust + custom kernel | C++/CUDA TurboMind | llama.cpp (C++) |
| **核心创新** | PagedAttention + 连续批处理 | FlashAttention 2 + custom | TurboMind 后端 + 4bit 量化 | GGUF 量化 + 单机体验 |
| **最大模型** | 200B+（多机 TP+PP）| 70B（多卡）| 100B | 70B（多 GPU 层分流）|
| **多 GPU 支持** | TP/PP/SP/DP 全维度 | TP | TP | 朴素层分流 |
| **量化格式** | GPTQ/AWQ/FP8/SmoothQuant | GPTQ/AWQ/BitsAndBytes | AWQ/FP8/GGUF | GGUF（Q2-Q8）|
| **FP8 原生** | ✅ H100 | ✅ H100 | ✅ H100 | ❌ |
| **Prefix Sharing** | ✅ 默认开 | ⚠️ 部分支持 | ✅ | ❌ |
| **CPU 推理** | ⚠️ 实验性 | ❌ | ⚠️ 实验性 | ✅ 强项 |
| **冷启动延迟** | 30-60s | 20-40s | 20-40s | **2-5s** |
| **API 兼容** | OpenAI API | HuggingFace API | OpenAI API | REST + OpenAI |
| **社区/文档** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **生产案例** | ChatGLM / Qwen / 智谱推理 | HuggingFace Inference Endpoints | 上海 AI Lab / 浦语 | 个人开发者 / 教育 |

---

## 2. 详细打分（10 分制）

| 维度 | vLLM | TGI | LMDeploy | Ollama |
|------|------|-----|----------|--------|
| 单机吞吐 | 8 | 7 | **9** | 5 |
| 高并发 | **10** | 8 | 9 | 3 |
| 长上下文 | **9** | 7 | 8 | 5 |
| 量化精度（4bit）| **9** | 8 | 9 | 7 |
| 多卡多机 | **10** | 7 | 8 | 4 |
| CPU 推理 | 2 | 1 | 2 | **10** |
| 边缘/移动 | 2 | 2 | 3 | **9** |
| 冷启动延迟 | 4 | 5 | 5 | **10** |
| 生态集成 | **9** | **10** | 6 | 6 |
| 中文支持 | 8 | 7 | **10** | 7 |
| 部署成本 | 5 | 6 | 6 | **9** |
| **平均** | **7.0** | **6.0** | **6.5** | **6.1** |

> 分数为社区共识加权估算，实际随版本变化。

---

## 3. 选型决策矩阵

### 3.1 按场景

| 场景 | 第一选择 | 第二选择 |
|------|---------|---------|
| **国内大厂 / 国产 GPU / 书生模型** | LMDeploy | vLLM |
| **HuggingFace 生态 / transformers 重度用户** | TGI | vLLM |
| **生产级 API 服务（OpenAI 兼容）** | vLLM | LMDeploy |
| **极简开发机 / 个人学习** | Ollama | LM Studio |
| **教育 / 离线 / 隐私** | Ollama | LM Studio (GGUF) |
| **多模态（图文 / 视频）** | vLLM 0.6+ | TGI |
| **MoE 模型（Mixtral / DeepSeek-V3）** | vLLM | LMDeploy |
| **Android / iOS 边缘** | llama.cpp | Ollama |

### 3.2 按团队能力

| 团队特征 | 推荐 |
|---------|------|
| Python / PyTorch 强，CUDA 弱 | vLLM |
| HuggingFace transformers 出身 | TGI |
| 国产化要求 / 信创 | LMDeploy |
| 运维能力弱 / 个人开发者 | Ollama |
| 数据科学家 / 实验导向 | Ollama → vLLM |

---

## 4. 技术细节差异

### 4.1 调度器

| 引擎 | 调度粒度 | 实现 |
|------|---------|------|
| vLLM | iteration-level（每 step 重新调度）| Python Scheduler + async |
| TGI | request-level（每请求决策）| Rust 异步 |
| LMDeploy | iteration-level | C++ Scheduler |
| Ollama | 单队列 FIFO | 朴素实现 |

### 4.2 KV cache 管理

| 引擎 | 分页 | 共享 | 替换策略 |
|------|------|------|---------|
| vLLM | ✅ PagedAttention | ✅ prefix sharing | LRU |
| TGI | partial | partial | LRU |
| LMDeploy | ✅ 自研 | ✅ | LRU |
| Ollama | ❌ 连续分配 | ❌ | ❌ |

### 4.3 量化集成

| 引擎 | 加载速度 | 兼容性 |
|------|---------|--------|
| vLLM | 中（需要反量化 kernel）| 高（多种格式）|
| TGI | 中 | 高（HF 生态）|
| LMDeploy | 快（TurboMind 预编译）| 中（AWQ/GGUF）|
| Ollama | **最快**（GGUF 优先）| 中（GGUF 原生）|

---

## 5. 真实生产案例

### 5.1 vLLM

- 智谱 GLM 推理服务
- HuggingFace Inference Endpoints（部分）
- 阿里 PAI / 字节跳动火山方舟

### 5.2 TGI

- HuggingFace Inference Endpoints（默认）
- AWS SageMaker JumpStart
- 各类 HuggingFace Spaces

### 5.3 LMDeploy

- 上海 AI Lab 浦语官方推理
- 商汤、智源、阿里达摩院部分场景

### 5.4 Ollama

- 个人开发者、教育场景
- 公司内网 demo、私有化小团队
- 原型阶段、低 QPS 阶段

---

## 6. 反模式 · 选型常见的 4 个错

### ⚠️ 反模式 1：「听说 vLLM 最强」

- vLLM 在「高并发 GPU 服务」最强，但 CPU / 边缘 / 冷启动场景它不是最优
- **先看场景匹配度**，不要迷信 benchmark

### ⚠️ 反模式 2：「公司统一用 Ollama」

- Ollama 不是为高 QPS 设计，统一用会导致：
  - 单进程受限，难以扩展
  - 监控 / Tracing 弱
  - 多卡利用率低
- 建议：开发环境用 Ollama，生产用 vLLM

### ⚠️ 反模式 3：「上 LMDeploy 因为国产」

- 国产是优点，但不是决定性
- **生态契合度 + 团队熟悉度 + 维护成本** 才是关键
- 信创要求时才必须 LMDeploy

### ⚠️ 反模式 4：忽略「运维成本」

- vLLM 需要熟悉 PyTorch + CUDA + 服务化生态
- TGI 需要熟悉 HuggingFace 工具链
- LMDeploy 文档相对少
- Ollama 一行命令就跑

---

## 7. 一句话总结

> **vLLM 当「工业引擎」、Ollama 当「开发引擎」、TGI 当「HF 生态首选」、LMDeploy 当「国产 / 中文模型首选」——最好组合：Ollama 开发 + vLLM 生产。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[06-benchmark-data](06-benchmark-data.md) · 下一章：[08-decision-tree](08-decision-tree.md)
