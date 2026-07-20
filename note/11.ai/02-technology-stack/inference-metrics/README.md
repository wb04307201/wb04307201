<!--
module:
  parent: ai
  slug: ai/inference-metrics
  type: article
  category: 主模块子文章
  summary: LLM 推理性能三大指标 TTFT / TPOT / Throughput
-->

# LLM 推理性能指标

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：**TTFT（首 token 延迟）+ TPOT（每 token 延迟）+ Throughput（吞吐量）** 三大指标，定义 LLM 服务质量的"金三角"。生产监控必备。

---

## 📊 三大指标定义

| 指标 | 含义 | 用户感受 | 优化目标 |
|------|------|---------|---------|
| **TTFT** (Time To First Token) | 输入 → 第 1 个 token | 等多久开始打字 | < 200ms（交互式）< 500ms（容忍） |
| **TPOT** (Time Per Output Token) | 后续每 token 平均耗时 | 打字机是否流畅 | < 50ms（流畅）< 100ms（可接受） |
| **Throughput** | tokens/sec 或 reqs/sec | 服务多少用户 | 越高越好（成本） |

---

## 🧮 关系公式

```text
总延迟 = TTFT + (output_tokens - 1) × TPOT
例：100 token 输出，TTFT 200ms + TPOT 50ms
   = 200 + 99 × 50 = 5150 ms ≈ 5 秒

单卡 Throughput 上限 = 1 / TPOT
例：TPOT 50ms → 单卡上限 20 tokens/s
```

---

## 📈 不同场景目标值

| 场景 | TTFT | TPOT | 备注 |
|------|------|------|------|
| **ChatGPT 风格对话** | < 300ms | < 80ms | 交互敏感 |
| **Code Completion** | < 100ms | < 30ms | 实时代码补全 |
| **批量文档摘要** | < 2s | 不限 | 离线批处理 |
| **RAG 检索增强** | < 500ms | < 100ms | 用户等待搜索结果 |
| **Agent 多步推理** | < 1s/step | 不限 | 单步可接受慢 |

---

## 🛠️ Prometheus 监控方案

```python
# vllm 暴露的指标
from prometheus_client import Histogram, Counter

ttft_histogram = Histogram(
    'vllm:time_to_first_token_seconds',
    'Time to first token',
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

tpot_histogram = Histogram(
    'vllm:time_per_output_token_seconds',
    'Time per output token',
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

throughput_counter = Counter(
    'vllm:tokens_total',
    'Total tokens generated'
)
```

**Grafana Dashboard 推荐面板**：
- P50 / P95 / P99 延迟
- QPS（requests per second）
- GPU 利用率 + 显存占用
- KV Cache 使用率

---

## ⚙️ 优化技术映射

| 优化目标 | 推荐技术 |
|---------|---------|
| **降低 TTFT** | Prefill 优化、KV Cache 预热、Speculative Decoding |
| **降低 TPOT** | PagedAttention、Continuous Batching、Flash Attention |
| **提升 Throughput** | Continuous Batching、量化、模型并行 |

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [PagedAttention](../paged-attention/README.md) / [Speculative Decoding](../speculative-decoding/README.md) / [推理框架对比](../inference-frameworks/README.md)
- **LLMOps**：[推理部署实战](../../08-llmops/06-rag-out-of-domain-rejection/README.md) 顺带提

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ TTFT 越低越好 | ✅ 过度追求 < 50ms 会牺牲吞吐量 |
| ❌ TPOT 应该固定 | ✅ TPOT 随 seq_len 增长（O(n²) attention） |
| ❌ Throughput 高 = 延迟低 | ✅ 通常相反，需权衡 |
| ❌ 监控 P50 就够 | ✅ P95/P99 才能反映长尾体验 |

← [返回 L2 技术栈](../README.md)