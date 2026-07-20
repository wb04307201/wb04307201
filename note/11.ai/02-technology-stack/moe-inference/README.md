<!--
module:
  parent: ai
  slug: ai/moe-inference
  type: article
  category: 主模块子文章
  summary: MoE 推理优化：DeepSeek-V3 671B 部署实战
-->

# MoE 推理优化

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：MoE 推理优化 = **专家并行 + 通信优化 + 路由缓存**三大策略，让 DeepSeek-V3 671B 等 MoE 模型在 8 张 A100 上跑起来，**激活 37B 但参数 671B**。

---

## 🎯 MoE 推理的独特挑战

**问题 1：显存爆炸** —— 671B 参数全在显存（FP16 = 1.3 TB）

**问题 2：专家调度开销** —— 每个 token 要查路由表，跨 GPU 通信

**问题 3：负载不均** —— 路由坍缩 → 部分专家过热

---

## 📐 三大优化策略

### 1. 专家并行（Expert Parallelism, EP）

```text
传统张量并行：切分每个专家的权重
专家并行：每个 GPU 放部分专家，token 跨 GPU 路由

例：8x A100 + 671B 模型
  每张卡 84B 参数（专家子集）
  激活 37B 时跨卡通信收集
```

### 2. 通信优化（DeepSeek-V3 Dual-Pipe）

```text
Pipe 1: 计算 Expert 1 → 计算 Expert 2
Pipe 2: 通信 All-to-All（同时进行）
两管道时间重叠 → 通信开销隐藏
```

### 3. 路由缓存（Routing Cache）

```text
第一次请求：完整路由计算
后续请求：复用路由决策（特别是 system prompt 相同场景）
```

---

## 📊 部署方案对比

| 模型 | 部署方式 | 硬件 | 吞吐量 | 备注 |
|------|---------|------|--------|------|
| Mixtral 8x7B | EP-2 | 2x A100 | 30 req/s | 入门 |
| Mixtral 8x22B | EP-4 | 4x A100 80G | 15 req/s | 中等 |
| DeepSeek-V3 671B | EP-8 + Dual-Pipe | 8x H100 | 50 req/s | SOTA |
| Qwen-MoE 72B | TP-4 | 4x A100 | 25 req/s | 国产 |

---

## 🛠️ 实操：vLLM 部署 DeepSeek-V3

```bash
# 1. 下载模型
huggingface-cli download deepseek-ai/DeepSeek-V3 --local-dir DeepSeek-V3

# 2. 启动 vLLM 服务（需 v0.6.0+）
vllm serve DeepSeek-V3 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.92 \
  --quantization awq  # INT4 量化
```

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ MoE 推理比 Dense 快 | ✅ 专家调度 + 通信，实际更慢 |
| ❌ 专家越多越好 | ✅ 太多 → 单专家弱 + 路由难学 |
| ❌ MoE 不需要量化 | ✅ 671B 必须量化才能塞进 8x A100 |
| ❌ EP 永远比 TP 好 | ✅ 视模型大小和网络拓扑而定 |

---

## 🔗 兄弟章节

- **L1**：[MoE 架构](../../01-fundamentals/moe-architecture/README.md)
- **本专题**：[KV Cache](../kv-cache/README.md) / [PagedAttention](../paged-attention/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **LLMOps**：[推理部署](../../08-llmops/) 顺带提

← [返回: AI 知识体系](../README.md)