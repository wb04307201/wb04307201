<!--
module:
  parent: ai
  slug: ai/continuous-batching
  type: article
  category: 主模块子文章
  summary: Continuous Batching 动态调度：吞吐量提升 23x
-->

# Continuous Batching（连续批处理）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：Continuous Batching = **请求完成立即调度新请求插入 batch**，调度粒度从 sentence 级降到 **token 级**，**吞吐量提升最高 23x**。vLLM / TGI / SGLang 全部采用。

---

## 🎯 问题：静态 Batching 的浪费

传统 Static Batching：

```
Batch = [Req A (100 token), Req B (1000 token), Req C (50 token)]
必须等 B 全部完成才能返回
GPU 在 B 长尾生成时空转（A 和 C 已完成）
```

**GPU 利用率 < 40%**

---

## 💡 方案：Continuous Batching

```
Time T+0:  Batch = [A(50), B(800), C(20)]
Time T+1:  A 完成 → 插入 Req D
           Batch = [B(799), C(19), D(0)]
Time T+2:  C 完成 → 插入 Req E  
           Batch = [B(798), D(1), E(0)]
```

每个 decode step 都重新组装 batch，**永远填满 GPU**。

---

## 📊 性能对比

| 场景 | Static Batching | Dynamic Batching | Continuous Batching |
|------|----------------|------------------|---------------------|
| **调度粒度** | sentence | sentence | token |
| **GPU 利用率** | 40% | 65% | **90%+** |
| **吞吐量 (req/s)** | 1x | 1.5-3x | **10-23x** |
| **首 token 延迟** | 1x | 0.95x | 0.8-1x |
| **实现复杂度** | 简单 | 中等 | 难（需细粒度调度器） |

---

## 🔧 调度算法演进

1. **Static Batching**（v1, HuggingFace 早期）：等所有完成
2. **Dynamic Batching**（v2, FasterTransformer）：等最短完成
3. **Continuous Batching**（v3, vLLM 2023）：每 token 调度
4. **Iteration-level Scheduling**（v4, SGLang 2024）：复杂 prompt 模板
5. **Disaggregated Prefill-Decode**（v5, DistServe 2024）：prefill/decode 分离部署

---

## 🔗 兄弟章节

- **本专题**：[KV Cache](../kv-cache/README.md) / [PagedAttention](../paged-attention/README.md)
- **咬文嚼字**：[面试深挖版](../../../../../13.split-hairs/11.ai/llm-benchmark/README.md) 顺带提

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 增大 batch 一定能提升吞吐 | ✅ 超过 GPU 显存后 OOM |
| ❌ Continuous Batching 提升延迟 | ✅ 实际略降（首 token 更快） |
| ❌ 所有框架都支持 | ✅ 仅 vLLM / TGI / SGLang 原生支持 |
| ❌ Continuous Batching 不影响输出 | ✅ 完全不影响（每个请求独立调度） |

← [返回 L2 技术栈](../README.md)