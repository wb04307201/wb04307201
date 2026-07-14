<!--
question:
  id: 11.ai-inference-engine-selection
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [11.ai, vLLM, Ollama, PagedAttention, 推理引擎, 量化, 分布式]
-->

# 工业级大模型部署：为什么优先选 vLLM 而非 Ollama？

> 一句话定位：工业部署下 vLLM 凭借 PagedAttention + 连续批处理 + 分布式 4 引擎领先 Ollama 5-24x，但 Ollama 在单机 / 边缘 / 开发场景仍是首选。完整深度见 [主模块 vllm-vs-ollama 深度专题](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md)。

> **系列定位**：经典大模型部署选型面试题（字节 / 阿里 / 美团 / 智谱高频）。考察的不是「vLLM 比 Ollama 强几个点」，而是 **PagedAttention 显存机制** + **连续批处理调度原理** + **4 引擎场景化选型能力**。

---

## 引子：CTO 拍板上 vLLM 的 3 个理由

```text
场景：2024 Q3 某 SaaS 公司要上线"AI 客服"——
- 数据：客服对话 5 万次/天，平均上下文 8k，预计 QPS 50
- 硬件：3 张 A100 80G
- 选项：①Ollama  ②vLLM  ③TGI  ④LMDeploy
```

**决策现场**：
1. **同事务初创会问："Ollama 不是更简单吗？为什么不先用 Ollama？"**
2. **资深 CTO 会问："3 张卡怎么切分？TP 还是 PP？量化选 INT4 还是 FP8？"**
3. **架构师会问："vLLM 冷启动 30 秒怎么解决？怎么配 prefix sharing？监控告警怎么搭？"**

普通候选人会答："vLLM 性能更好"——踩中"**理由模糊、缺反模式、缺权衡**" 3 大雷区。
高分候选人会答：**场景区分（先说 Ollama 不是被替代）→ 4 大核心差异（PagedAttention / 连续批处理 / 分布式 / prefix sharing）→ 6 个反模式 → 何时反选 Ollama**。

---

## 一、核心原理（必选）

### 1.1 vLLM 与 Ollama 的根本设计差异

| 维度 | vLLM | Ollama |
|------|------|--------|
| 设计目标 | 高并发 GPU 服务化 | 单机 / 边缘 / 离线 |
| 底层 | PyTorch + 自研 CUDA kernel | llama.cpp (C++) |
| KV cache | PagedAttention 分页 + 共享 | 朴素连续分配 |
| 调度 | iteration-level 连续批处理 | 单队列 FIFO |
| 多卡 | TP/PP/SP/DP 全维度 | 朴素层分流 |
| 冷启动 | 30-60s | 2-5s |
| 典型场景 | 100+ QPS 工业级 API | 个人 / 开发机 / 教育 |

**反直觉**：Ollama 不是"低配版 vLLM"——是不同优化方向的引擎。选错场景代价高。

### 1.2 PagedAttention 原理（vLLM 核心创新）

```
操作系统的"虚拟内存分页"思想搬到 KV cache：

- 连续逻辑 KV 切成固定大小"block"（默认 16 token / block）
- 每个序列维护一张 block table（逻辑 → 物理映射）
- attention 计算时查 block table，逻辑连续 / 物理离散
- block 池在所有序列间共享
```

**效果**：

| 指标 | HuggingFace 静态分配 | vLLM PagedAttention |
|------|----------------------|----------------------|
| 显存浪费率 | 60-80% | **< 4%** |
| 同显存并发数 | 1x | 2-4x |
| 端到端吞吐 | 1x | **14-24x** |

> 14-24x 来源：vLLM 论文 SOSP'23 + 社区实测 ShareGPT 数据集 + LLaMA-7B + A10G。

### 1.3 连续批处理（Continuous Batching）

```
传统静态批处理：
[A、B、C 一起开始] → 等最长完成 → 整批返回（短序列 GPU 空转）

连续批处理：
每个 decoding step 重组 batch：
  Step 1: [A, B, C, D]
  Step 2: [B, C, D, E]  ← A 完成，立刻加入新 E
  Step 3: [C, D, E, F]  ← B 完成，加入 F
```

**效果**：吞吐量 +2-5x，P99 延迟 -50%。

### 1.4 Prefix Sharing（前缀共享）

```
场景：系统 prompt 500 token + 用户问题 50 token（多用户共享 system prompt）

vLLM 实现：前 500 token 只存一份物理 block，所有用户共享
效果：显存再省 30-50%（视共享率）
```

### 1.5 分布式 4 维并行

| 维度 | 切分对象 | 通信开销 |
|------|---------|---------|
| TP | 单层权重矩阵 | 高（AllReduce） |
| PP | 不同层到不同卡 | 中（点对点） |
| SP | 长序列 token 维度 | 中 |
| DP | 整个模型副本 | 低 |

**工业范式**：70B 单机 TP=4 + INT4；200B 多机 TP=8 + PP=2-4。

---

## 二、面试话术（90 秒版本 / 高分答案模板）

> ⚠️ **模板不是背答案**，而是当大脑空白时的"骨架"——面试现场结合题目微调。

### 题目 A：工业级部署为什么优先选 vLLM 而不是 Ollama？

**高分答案**（4 层递进，60-90 秒）：

```
1. 场景区分（15 秒）：
   "Ollama 不是被 vLLM 替代——两者服务不同场景。
   Ollama 适合单机 / 边缘 / 开发场景；vLLM 是生产级 GPU 服务引擎。"

2. 核心差异（30 秒）：
   "差异本质是设计目标的 trade-off：
   - KV cache：vLLM 用 PagedAttention 解决显存碎片化（60-80% → <4%）
   - 调度：vLLM 用连续批处理，每个 decoding step 重组 batch，吞吐 +2-5x
   - 分布式：vLLM 支持 TP/PP/SP/DP 多维并行，Ollama 仅朴素层分流
   - Prefix sharing：vLLM 默认开，Ollama 不支持，多轮对话显存再省 40%
   关键数据：100 并发下 vLLM 是 Ollama 的 6-8 倍，500 并发 8-10 倍。"

3. 量化支撑（20 秒）：
   "工业 benchmark：LLaMA-7B 在 A100 上 vLLM 单并发几乎打平，
   但 100 并发 vLLM 320 req/s vs Ollama 52 req/s，500 并发 vLLM 510 vs Ollama 65。"

4. 反模式 + 反选（25 秒）：
   "vLLM 也有不适用的场景——CPU 推理、边缘部署、需要秒级冷启动的 Serverless，
   这些场景 Ollama 反而更优。生产环境我用 vLLM，开发机用 Ollama。"

5. 反问（10 秒）：
   "贵司当前生产是 100 QPS 还是 1000 QPS？数据是否允许本地离线？——这两点决定具体配置。"
```

### 题目 B：PagedAttention 是什么？为什么让 vLLM 快 14-24 倍？

**高分答案**（60 秒）：

```
1. 问题定义（10 秒）：
   "传统 LLM 推理时每个序列都要预分配连续显存存 KV cache，
   因序列长度不一致导致 60-80% 显存浪费，70B 模型单请求就占 16 GB。"

2. 方案类比（15 秒）：
   "PagedAttention 借鉴操作系统的虚拟内存分页——
   把每个序列的 KV 切成固定大小 block（默认 16 token），
   每张 block table 记录逻辑 → 物理映射，
   逻辑连续、物理离散，不同序列可共享 block 池。"

3. 效果（15 秒）：
   "显存浪费从 60-80% 降到 4% 以下，同显存并发数 2-4x，
   配合连续批处理端到端吞吐提升 14-24 倍（SOSP'23 论文 + 社区实测）。"

4. 进阶（15 秒）：
   "PagedAttention 还天然支持 prefix sharing——
   多轮对话共享 system prompt 时，前 N 个 block 指向同一组物理 block，
   显存再省 30-50%。"
```

### 题目 C：连续批处理 vs 静态批处理，吞吐量差几倍？

**高分答案**（30 秒）：

```
"差 2-5 倍。
静态批处理：所有序列同步开始 → 等最长的结束 → 整批返回（GPU 空转）
连续批处理：每个 decoding step 重组 batch，完成一个出队，加入新的

实测：LLaMA-7B A10G + ShareGPT
- 静态：1x（基线）
- 动态：1.4x
- 连续：3.8x，P99 延迟 -50%

工业上 vLLM 默认开启连续批处理，配合 prefix sharing 还能再提升。"
```

### 题目 D：TP / PP / SP / DP 怎么组合？70B 用什么方案？

**高分答案**（45 秒）：

```
"70B 用 单机 TP=4 + AWQ-INT4 量化。
- 显存：72B × 2 字节（FP16）= 144 GB → 4 卡 TP 每卡 36 GB
- INT4：再降到 18 GB / 卡，余量给 KV cache 和 prefix sharing

切分逻辑：
- TP≥8 时通信成本激增，应改 PP（层切）
- PP 2-4 段合适，太多有 bubble 损耗
- SP 与 TP 正交，配合长上下文（32k+）
- DP 适用于小模型高并发（7B / 13B）

反模式：能用单卡就别 TP（70B 单卡 FP16 跑不起来才是时候）；
优先 FP16 跑不了再上量化而非直接 INT4（保留调试余地）。"
```

### 题目 E：4 引擎（vLLM / TGI / LMDeploy / Ollama）怎么选？

**高分答案**（60 秒）：

```
"按 3 维约束选：
1. 硬件：
   - 国产 GPU（昇腾 / 寒武纪）→ LMDeploy（信创生态）
   - 国际 GPU（H100 / A100）→ vLLM / TGI
   - CPU only → Ollama（GGUF Q4_K_M）
   - Apple Silicon → Ollama / MLX

2. 团队：
   - HF 生态重度用户 → TGI（集成度最丝滑）
   - Python / PyTorch 强 → vLLM
   - 国产优先 / 信创 → LMDeploy
   - 运维弱 / 个人 → Ollama

3. 负载：
   - 生产 100+ QPS → vLLM（必备）
   - 长上下文 32k+ → vLLM（PagedAttention 强）
   - 开发原型 / demo → Ollama（最快）
   - MoE 模型 → vLLM / LMDeploy

实操推荐：开发环境用 Ollama（开发体验），生产用 vLLM（吞吐 + 监控）。"
```

### 题目 F：量化的反模式？什么时候不该上 INT4？

**高分答案**（40 秒）：

```
"4 个反模式：
1. 盲目追求 INT3 / INT2：质量掉 1-2%，某些下游任务（数字计算、推理）断崖
2. 忽略反量化开销：W4A16 推理时反量化权重到 FP16，激活占 60% 时省不了 4x
3. FP8 强行上 A100：A100 不支持 FP8 Tensor Core，会回落到 FP16 软件模拟
4. 测试一致但上线掉点：必须 A/B 测试 + benchmark 监控

我的工业实践：
- H100 / H200 → 优先 FP8（H100 原生支持）
- A100 80G → 70B 内 BF16，70B+ INT8
- A100 40G → INT4（AWQ > GPTQ）
- 4090 24G → AWQ-INT4 (7B-13B) / GPTQ-INT4 (30B-70B TP)
- 边缘 / CPU → Ollama Q4_K_M"
```

### 题目 G：vLLM 监控怎么搭？关键指标有哪些？

**高分答案**（40 秒）：

```
"vLLM 原生暴露 Prometheus metrics（端口 8000 的 /metrics）：

核心 SLI：
- vllm:request_success_total（请求成功数）
- vllm:request_latency_seconds（端到端延迟）
- vllm:time_to_first_token_seconds（首 token 延迟）
- vllm:tokens_per_request（每请求 token 数）
- vllm:gpu_cache_usage_perc（KV cache 利用率）
- vllm:cpu_cache_usage_perc

监控告警组合：
- Prometheus + Grafana（指标可视化）
- vLLM 自带 /health 端点（K8s liveness probe）
- 日志：JSON 格式 + Trace ID，方便定位
- 告警阈值：
  * P99 延迟 > 5s 触发
  * 显存利用率 > 90% 提前预警
  * QPS 同比下降 > 30% 立刻排查
  * vLLM restart 次数 > 3/h

进阶：APISIX / Envoy 做 L7 负载均衡 + 限流 + 鉴权。"
```

---

## 三、常见陷阱（必选，5-7 个反模式）

### 陷阱 1：把 Ollama 当万能解

- **错误**：公司统一用 Ollama，因为"简单"。
- **真相**：Ollama 单进程限制，多卡是朴素层分流，不是矩阵级 TP，无法服务 100+ QPS。
- **代价**：生产事故频发（K8s 重启 + 单点故障 + 监控缺失）。

### 陷阱 2：vLLM 单卡 CPU 跑

- **错误**：没有 GPU，用 vLLM 部署"LLaMA"。
- **真相**：vLLM 强依赖 CUDA，CPU 上比 Ollama 慢 5x。
- **代价**：资源浪费，体验劣化。

### 陷阱 3：TP 越大越好

- **错误**：70B 模型强行 TP=16。
- **真相**：TP 通信成本高，超过 8 卡应切 PP（层切）。
- **代价**：通信成为瓶颈，延迟反而恶化。

### 陷阱 4：盲信 peak benchmark

- **错误**：用 vLLM 默认 benchmark 当生产指标。
- **真相**：数据依赖场景：负载 / 上下文长度 / 输入输出比 / batch 大小都会改变结果。
- **代价**：上线后真实场景掉点。

### 陷阱 5：量化就是为了省显存

- **错误**：INT4 只看到显存减少 4x。
- **真相**：W4A16 推理时反量化回 FP16，激活占 60% 时省不到 4x；某些 prompt 类型掉点严重。
- **代价**：质量投诉 + 长上下文显存预估失败。

### 陷阱 6：没做 prefix sharing 配置

- **错误**：多轮对话 / RAG 部署没开 prefix caching。
- **真相**：vLLM 默认开，但有些版本要 `--enable-prefix-caching`，吞吐量差 30%+。
- **代价**：多轮对话场景运维被投诉慢。

### 陷阱 7：忽略冷启动 + 灰度

- **错误**：上线 vLLM 直接 100% 流量切换。
- **真相**：vLLM 冷启动 30-60 秒（CUDA 初始化 + 模型加载），OOM 风险高。
- **代价**：上线即故障，缺回滚机制。

---

## 四、最佳实践（工业级方案）

### 方案 A：标准生产部署（最常用）

```bash
# 1. 启动 vLLM（4×H100 + AWQ-INT4 + TP=4）
python -m vllm.entrypoints.openai.api_server \
    --model Qwen2.5-72B-Instruct-AWQ \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 32768 \
    --max-num-seqs 256 \
    --enable-prefix-caching

# 2. K8s 部署（Deployment + Service + HPA）
# 3. Prometheus + Grafana 监控
# 4. APISIX 网关：限流 + 鉴权 + 灰度
# 5. 蓝绿发布 + 回滚
```

### 方案 B：开发测试（个人 / 团队）

```bash
# Ollama 一行命令
ollama run qwen2.5:7b
# 或 Python 调用
import ollama
client = ollama.Client()
resp = client.chat(model='qwen2.5:7b', messages=[...])
```

### 方案 C：边缘 / 离线（隐私场景）

- Ollama / LM Studio (GGUF)
- Apple Silicon 用 MLX 后端
- 量化 Q4_K_M（性价比最优）

### 关键选型决策表

| 场景 | 第一选择 | 量化 | 并发 | 监控 |
|------|---------|------|------|------|
| 个人开发 | Ollama | Q4_K_M | 1 | - |
| 公司内网 demo | Ollama | Q4_K_M | 5 | docker stats |
| 中小企业 API | vLLM 单卡 | AWQ-INT4 | 30-50 | Prometheus |
| 中大型企业 API | vLLM 4 卡 TP | AWQ-INT4 | 100-200 | Prometheus + Grafana |
| 超大规模 | vLLM 分布式 + 缓存 + 网关 | FP8 | 1000+ | 完整监控 |

---

## 五、相关章节（强制）

### 主模块深度专题

- [11.ai vllm-vs-ollama 总目录](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md)
- [01-paged-attention](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/01-paged-attention.md) —— vLLM 核心创新原理
- [02-kv-cache-management](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/02-kv-cache-management.md) —— KV cache 显存管理
- [03-batching-strategies](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/03-batching-strategies.md) —— 连续批处理
- [04-quantization](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/04-quantization.md) —— 量化与显存估算
- [05-distributed-inference](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/05-distributed-inference.md) —— TP/PP/SP/DP
- [06-benchmark-data](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/06-benchmark-data.md) —— 实测数据
- [07-vs-tgi-lmdeploy](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/07-vs-tgi-lmdeploy.md) —— 4 引擎对比
- [08-decision-tree](../../../11.ai/03-engineering/ai-platforms/vllm-vs-ollama/08-decision-tree.md) —— 5 分钟决策树

### 同栏目（11.ai）姐妹篇

- [transformer](../../11.ai/transformer/README.md) —— Transformer 架构原理
- [rag](../../11.ai/rag/README.md) —— RAG 检索增强生成
- [function-calling](../../11.ai/function-calling/README.md) —— Function Calling 原理
- [token](../../11.ai/token/README.md) —— Token 经济学

### 主模块兄弟

- [11.ai/03-engineering/ai-platforms/coze](../../../11.ai/03-engineering/ai-platforms/coze.md) —— Coze 平台
- [11.ai/03-engineering/ai-platforms/dify](../../../11.ai/03-engineering/ai-platforms/dify.md) —— Dify 平台
- [11.ai/03-engineering/local-deployment/ollama](../../../11.ai/03-engineering/local-deployment/ollama/README.md) —— Ollama 部署
- [11.ai/07-llmops/02-llmops-stack](../../../11.ai/07-llmops/02-llmops-stack/README.md) —— LLMOps 全景

### 实战姐妹（12.story）

- [12.story/39-ai-private-deployment](../../../12.story/39-ai-private-deployment.md) —— 阿明餐厅从 Ollama 试跑到 vLLM 上生产

---

## 六、面试反问（让候选人反客为主）

面试尾声，候选人主动反问会加分：

```
Q1：贵司 LLM 推理是自建还是 SaaS 化（如 OpenAI / 智谱）？
    → 自建 vLLM 是主线；SaaS 则更多聊 Function Calling / RAG
Q2：贵司对 inference latency 的 P99 SLO 是多少？
    → 100ms 内 vs 1s 内，决定 KV cache 策略和 prefix sharing 配置
Q3：贵司 GPU 资源是 A100 还是 H100？
    → H100 推荐 FP8，A100 走 AWQ-INT4
Q4：贵司 LLM 应用 RAG / Agent / Few-shot 哪种多？
    → RAG 多必须开 prefix sharing；Agent 多关注 function calling 缓存
```

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板

← [返回: 咬文嚼字 · inference-engine-selection](README.md)
