<!--
question:
  id: 11.ai-llm-inference
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [11.ai, KV Cache, PagedAttention, Continuous Batching, Speculative Decoding, 量化, 推理优化]
-->

# LLM 推理优化面试深挖（5 大核心）

> ⬅️ [返回 AI 咬文嚼字](../README.md) | [主模块深度专题](../../../11.ai/02-technology-stack/llm-inference-optimization/README.md)

> **一句话定位**：5 大 LLM 推理优化技术的**面试深挖版**（每题陷阱 + 反直觉 + 30 秒话术 + 90 秒话术）。

---

## 🎯 5 大核心题

### Q1：KV Cache 是什么？为什么必须有？

**陷阱**：

- ❌ 答"为了加速"（太笼统）
- ❌ 混淆训练 / 推理

**30 秒话术**：

> "KV Cache 是推理时把**已计算的 K/V 矩阵缓存**，避免每 token 重算历史 Attention。训练时**并行算全部 token** 不需要；推理时**逐 token 生成**，没有 KV Cache 就是 O(n²) 重算。"

**90 秒话术**：

> "以 7B 模型 8K context 为例，KV Cache 显存约 4GB，70B 128K 需 320GB。3 大优化方向：**量化（FP16→INT8 省 2x）/ 共享（MQA-GQA 省 4-8x）/ 分页（PagedAttention 碎片 < 4%）**。KV Cache 是**所有 LLM 推理优化的基石**。"

**反直觉**：

- ❌ "KV Cache 越大越好" → ✅ 显存约束下需权衡
- ❌ "训练也需要 KV Cache" → ✅ 训练是并行的，不需要

---

### Q2：PagedAttention 为什么能让 vLLM 吞吐提升 24x？

**陷阱**：

- ❌ 只回答"减少内存碎片"
- ❌ 不知道与 OS 虚拟内存的类比

**30 秒话术**：

> "借鉴 **OS 虚拟内存分页**：把 KV Cache 切成固定大小 block（16 token/页），用 block_table 映射，物理上不连续但逻辑上连续。显存利用率从 40% 提到 96%。"

**90 秒话术**：

> "传统连续分配下，100 token 和 8000 token 请求混跑，**碎片率 60-80%**。PagedAttention 把 KV 切成 16 token 的 block，**碎片 < 4%**。配合 **Continuous Batching**（每 token 调度），vLLM 实际生产**吞吐量提升 4-24x**。这是 vLLM 2023 年 SOSP 论文的核心贡献。"

**反直觉**：

- ❌ "PagedAttention 牺牲了延迟换吞吐" → ✅ 实际首 token 延迟略低

---

### Q3：Continuous Batching 与 Dynamic Batching 的本质区别？

**陷阱**：

- ❌ 回答"都是 batching"
- ❌ 不知道调度粒度差异

**30 秒话术**：

> "**Dynamic Batching** 调度粒度是 **sentence**（等最短完成才返回）；**Continuous Batching** 是 **token**（每 decode step 重新组装 batch，请求完成立即插入新请求）。"

**90 秒话术**：

> "传统 Static Batching 必须等最长请求完成（GPU 空转 60%）。Dynamic 改进为等最短完成（仍 35% 空转）。**Continuous 把调度粒度降到 token 级**，每个 decode step 重新组装，**GPU 利用率 90%+，吞吐量提升 23x**。vLLM / TGI / SGLang 全部支持。"

**反直觉**：

- ❌ "Continuous 增加延迟" → ✅ 实际首 token 略快（无需等待 batch 满）

---

### Q4：Speculative Decoding 为什么能保证输出分布一致？

**陷阱**：

- ❌ 答"小模型猜"（不理解接受/拒绝机制）
- ❌ 不知道数学保证

**30 秒话术**：

> "小模型预测 K 个候选 token，大模型一次 forward 验证。**接受率 60-80% 时加速 2-3x**。数学证明：接受/拒绝机制保证**输出分布与原模型完全一致**。"

**90 秒话术**：

> "传统自回归每步 1 token，要 100 次大模型 forward。投机解码让小模型（7B）猜 5 个，大模型（70B）1 次 forward 验证 5 个。**接受判定**基于大模型采样分布，**拒绝时按大模型分布重新采样**。Leviathan et al. 2022 证明输出分布完全一致。变体：Medusa（多头并行预测）/ EAGLE（特征层预测）。仅适合 **batch=1 在线**场景，batch 大反而变慢。"

---

### Q5：权重量化的 INT4 为什么几乎不掉点？

**陷阱**：

- ❌ 答"反正有误差补偿"（不具体）
- ❌ 不知道 GPTQ / AWQ 的核心算法

**30 秒话术**：

> "GPTQ 用 **Hessian 矩阵引导逐层量化**，AWQ **保护 1-3% 显著权重**。INT4 量化后精度损失 < 0.5%，显存省 4x。"

**90 秒话术**：

> "简单 INT4 截断会掉 5-10% 精度。**GPTQ（2022）**用二阶 Hessian 矩阵找到最优量化顺序，逐层最小化重建误差。**AWQ（2023）**发现激活值大的 1-3% 权重占精度 60%+，跳过这些不量化。**GGUF（llama.cpp）**用 K-means 聚类找最优量化中心。**NF4（QLoRA）**专门为训练设计，NormalFloat 分布匹配正态分布权重。LLaMA-7B 实测：FP16 → INT4 显存 14GB→4GB，加速 2.3x，PPL 损失 < 0.3。"

---

## 🔗 兄弟章节

- **主模块深度**：[llm-inference-optimization](../../../11.ai/02-technology-stack/llm-inference-optimization/README.md) — 10 章完整版
- **兄弟面试题**：[Transformer 架构](../transformer/README.md) / [MoE 架构](../multi-agent-system-design/README.md) 顺带提
- **餐厅叙事**：[12.story LLM 推理故事](../../../12.story/46-llm-inference.md)（续集/番外待补）

---

## 📊 5 题难度速查

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 KV Cache | ⭐⭐⭐ | 高频 | 7B 8K 占 4GB |
| Q2 PagedAttention | ⭐⭐⭐⭐ | 高频 | 吞吐提升 4-24x |
| Q3 Continuous Batching | ⭐⭐⭐ | 高频 | 吞吐提升 23x |
| Q4 Speculative Decoding | ⭐⭐⭐⭐⭐ | 中频 | 加速 2-3x |
| Q5 权重量化 | ⭐⭐⭐⭐ | 中频 | 显存省 4x |

← 返回 [AI 咬文嚼字](../README.md)

← [返回: 咬文嚼字](../README.md)