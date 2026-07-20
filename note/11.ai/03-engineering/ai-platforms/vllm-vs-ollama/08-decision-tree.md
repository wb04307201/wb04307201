<!--
module:
  parent: ai-platforms/vllm-vs-ollama
  slug: ai-platforms/vllm-vs-ollama/08-decision-tree
  type: topic
  category: 选型决策
  summary: 「我是 X 场景，应该选 Y 引擎」的场景化决策树 + 推荐配置 + checklist
-->

# 场景化决策树 · 选型不迷路

> **一句话**：选型本质是**对齐约束**——硬件 / 负载 / 团队 / 监控 / 成本 5 维联合约束。给一张「5 分钟决策树」，给一张「实施 checklist」。

← [返回: vLLM vs Ollama](../README.md)

---

## 1. 5 分钟决策树（按问题顺序走）

```text
Q1：你服务的目标用户量级？
├─ 个人 / 5 人小团队        → Ollama
├─ 中小企业 / 100 人内 QPS<10  → Ollama 或 vLLM 单卡
├─ 中型企业 / 1000 人 QPS 50-500 → vLLM (单卡 TP 或多卡)
└─ 大型企业 / QPS>500          → vLLM + 分布式 + 监控 + 缓存层

Q2：硬件是什么？
├─ CPU only                 → Ollama（GGUF Q4_K_M）
├─ 4090 / 3090 单卡         → Ollama 或 vLLM (7B-13B 模型)
├─ A100 40GB                → vLLM (7B-13B INT4 / 70B 全栈)
├─ A100 80GB                → vLLM 全栈 (13B-70B)
├─ H100 / H200              → vLLM + FP8 量化
├─ 国产 GPU（昇腾 / 寒武纪）→ LMDeploy
└─ Apple Silicon (M1/M2)    → Ollama / llama.cpp（MLX 后端）

Q3：模型规模？
├─ ≤ 13B                    → Ollama / vLLM 都行
├─ 13B-70B                  → vLLM（必须量化）
├─ 70B-200B                 → vLLM 分布式 (TP=8+)
└─ 200B+                    → vLLM 分布式 (TP+PP)

Q4：上下文长度？
├─ ≤ 4k                     → 任何引擎都行
├─ 4k-32k                   → vLLM / TGI 优势
├─ 32k-128k                 → vLLM PagedAttention 强项
└─ > 128k                   → vLLM + chunked prefill + sparse

Q5：团队能力？
├─ 数据科学家 / 快速原型    → Ollama
├─ Python 工程师 / 不熟 CUDA → vLLM
├─ HuggingFace 深度用户      → TGI
├─ 国产生态 / 信创           → LMDeploy
└─ 运维能力强 / 多语言团队    → vLLM（最灵活）
```

---

## 2. 反向决策 · 5 个常见错误信号

| 错误信号 | 含义 |
|---------|------|
| 用 Ollama 给生产环境跑 QPS 100+ | Ollama 不是为高 QPS 设计，会被打爆 |
| 用 vLLM 单卡 CPU 跑 | vLLM 强 GPU 绑定，CPU 上比 Ollama 慢 5x |
| 70B 模型用 FP16 不量化 | 显存爆炸，必须量化（W4 / FP8）|
| 无限堆 TP 不想 PP | TP 越大通信成本越高，超 8 卡应切 PP |
| 跑生产不监控 GPU 利用率 / QPS / P99 延迟 | 出问题定位难，至少配 Prometheus + Grafana + vLLM metrics |

---

## 3. 推荐配置（按场景对照表）

| 场景 | 模型 | 引擎 | 量化 | 并发 | 硬件 | 监控 |
|------|------|------|------|------|------|------|
| 个人开发 | Qwen2.5-7B | Ollama | Q4_K_M | 1 | 4090 24GB | - |
| 公司内网 demo | Qwen2.5-7B | Ollama | Q4_K_M | 5 | 4090 24GB | docker stats |
| 小型企业 API | Qwen2.5-14B | vLLM | AWQ-INT4 | 30-50 | 1×A100 40G | Prometheus |
| 中型企业 API | Qwen2.5-72B | vLLM | AWQ-INT4 | 100-200 | 4×H100 80GB | Prometheus + Grafana + 日志 |
| 国产 GPU | Qwen2.5-72B | LMDeploy | W4A16 | 50 | 8×昇腾 910B | 内部监控 |
| HF 生态首选 | LLaMA-3-70B | TGI | GPTQ-INT4 | 80 | 2×A100 80G | HF Hub metrics |
| MoE / DeepSeek | DeepSeek-V3 | vLLM | FP8 | 100+ | 8×H200 | Prometheus + 内部 |

---

## 4. 实施 Checklist

部署 LLM 推理服务（以 vLLM 为例）的前置检查：

### 4.1 硬件层

- [ ] GPU 显存 ≥ 模型权重 + KV cache（公式：`显存 = 权重大小 + (2 × 4 × 并发 × ctx × 层数 × 头维 × 字节)`）
- [ ] 驱动 / CUDA / cuDNN 版本匹配（vLLM 0.6 需要 CUDA 12.x）
- [ ] 多卡间 NVLink / NVSwitch 互联（TP 必备）
- [ ] PCIe 4.0+（避免 NVLink 缺失的性能崩塌）

### 4.2 模型层

- [ ] 模型权重来源合规（HF Hub / ModelScope / 自训）
- [ ] 量化方案选型（参考 [04-quantization](04-quantization.md)）
- [ ] 量化模型质量 A/B 测试（benchmark + 内测）
- [ ] Trust Remote Code（自定义模型架构）

### 4.3 引擎层

- [ ] vLLM 启动参数：
  - `[x]` `--tensor-parallel-size`（TP）
  - `[x]` `--pipeline-parallel-size`（PP）
  - `[x]` `--gpu-memory-utilization 0.9`
  - `[x]` `--max-model-len`（按业务最大上下文）
  - `[x]` `--max-num-seqs`（按显存估算）
  - `[x]` `--enable-prefix-caching`（推荐默认开）
- [ ] 健康检查端点（`/health`）
- [ ] OpenAI 兼容 API 验证（`/v1/models` + `chat/completions`）

### 4.4 服务层

- [ ] API 网关（认证 / 限流 / 路由）
- [ ] 负载均衡（多副本时）
- [ ] 结果缓存（prefix cache / 业务结果）
- [ ] 监控：Prometheus metrics + 日志采集 + Trace
- [ ] 告警：P99 延迟 > 5s / 显存 > 90% / QPS 异常
- [ ] 灰度发布 + 回滚机制

### 4.5 测试层

- [ ] 负载测试（目标 QPS 的 1.5x）
- [ ] 长上下文测试（边界 case）
- [ ] 异常输入测试（超长 / 非法 / 攻击）
- [ ] 质量对比测试（vs 旧版 / vs 基线）

---

## 5. 决策卡（决策树精简版）

```text
┌─────────────────────────────────────────────┐
│  Step 1：硬件确定                           │
│    CPU only → Ollama                        │
│    单卡消费级 → Ollama 或 vLLM              │
│    数据中心 → vLLM                          │
│    国产 GPU → LMDeploy                      │
│                                              │
│  Step 2：场景确定                           │
│    开发原型 → Ollama                        │
│    生产服务 → vLLM                          │
│    HF 生态 → TGI                            │
│    国产优先 → LMDeploy                      │
│                                              │
│  Step 3：模型确定（量化配套）               │
│    ≤ 13B → BF16                             │
│    13B-70B → AWQ-INT4                       │
│    70B+ → AWQ-INT4 + TP                     │
│    H100 → FP8                               │
│                                              │
│  Step 4：实施 checklist（见上 4.1-4.5）     │
└─────────────────────────────────────────────┘
```

---

## 6. 迁移路径

### 6.1 从 Ollama → vLLM

适用：QPS > 50 / 单进程限制 / 需要 prefix sharing / 多卡扩展。

```bash
# Step 1: 准备 vLLM
docker pull vllm/vllm-openai:latest

# Step 2: 模型转换（GGUF → HF）
# Ollama 模型转 HF 格式（用 llama.cpp 的 convert 脚本）

# Step 3: 启动 vLLM
python -m vllm.entrypoints.openai.api_server \
    --model ./qwen2.5-7b-hf \
    --tensor-parallel-size 1 \
    --port 8000

# Step 4: 切换流量（蓝绿）
```

### 6.2 从 vLLM → LMDeploy（国产化）

```bash
# Step 1: 模型转 LMDeploy 格式
lmdeploy convert --model-name qwen2.5-7b --format awq

# Step 2: 启动 TurboMind 服务
lmdeploy serve api_server ./qwen2.5-7b-awq --backend turbomind
```

---

## 7. 一句话总结

> **选型不是问「最强」，是问「最契合」——5 分钟走完决策树 + 严格按 checklist 实施，比纠结技术先进性重要 10 倍。**

---

← [返回: vLLM vs Ollama](../README.md) · 上一章：[07-vs-tgi-lmdeploy](07-vs-tgi-lmdeploy.md) · 下一章：本专题结束
