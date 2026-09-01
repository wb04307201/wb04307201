<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/02-deep-learning
  type: index-only
  category: AI 基础索引
  summary: 深度学习基础——主流框架对比（PyTorch / TensorFlow / MindSpore / PaddlePaddle）、训练范式与生产部署。
  depth: ⭐⭐⭐⭐⭐
-->

# 02. 深度学习

## 📍 一句话定位

> 工程选型的决策轴——从 PyTorch 的学术灵活到 TensorFlow 的工业部署，再到 MindSpore / PaddlePaddle 的国产化生态，构建"研究 → 训练 → 部署"全链路认知。

## 🎯 子模块简介

`02-deep-learning/` 聚焦**深度学习工程落地的三大支柱**：

- **主流框架对比**：PyTorch（Meta，学术首选）、TensorFlow（Google，工业首选）、MindSpore（华为，国产化首选）、PaddlePaddle（百度，产业首选）——四分天下的市场格局与选型决策。
- **训练范式**：监督训练 / 预训练-微调 / 分布式训练（数据并行、模型并行、流水线并行）/ 混合精度（FP16 / BF16）——不同模型规模对应不同范式。
- **生产部署**：模型压缩（量化、剪枝、蒸馏）、推理引擎（TensorRT、ONNX Runtime、vLLM）、端边云协同（TensorFlow Lite、MindSpore Lite）——从实验室到工业级落地的最后一公里。

本节是连接"理论 Transformer"与"工业 LLM"的桥梁——01-ml 是地基，03-transformer 是核心组件，本节是工程工具链。

---

## 🧠 核心原理：从"为什么深度学习能 work"到"怎么工程化"

### 1. 反向传播 + 链式法则

深度网络的训练本质是梯度下降在复合函数上的传播。给定损失 $L$，对参数 $\mathbf{W}^{(l)}$ 的梯度由链式法则得到：

$$
\frac{\partial L}{\partial \mathbf{W}^{(l)}} = \frac{\partial L}{\partial \mathbf{a}^{(L)}} \cdot \prod_{k=l+1}^{L} \frac{\partial \mathbf{a}^{(k)}}{\partial \mathbf{a}^{(k-1)}} \cdot \frac{\partial \mathbf{a}^{(l)}}{\partial \mathbf{W}^{(l)}}
$$

**框架的核心价值**就是把这套链式求导**自动微分（autograd）**掉，让研究者只写前向图即可。PyTorch 用动态图（define-by-run），TensorFlow 早期用静态图（define-and-run，1.x Session 模式），2.x 已统一到 Keras + Eager。

### 2. 混合精度训练

FP16 显存减半、速度翻倍，但动态范围窄、易下溢；BF16 保持 FP32 指数位但截断尾数，**训练稳定性更佳**——这正是 LLM 训练默认 BF16 的原因：

$$
\mathbf{W}_{\text{FP32}} \xrightarrow{\text{cast}} \mathbf{W}_{\text{BF16}} \rightarrow \text{前向 + 反向} \rightarrow \text{FP32 optimizer 更新} \rightarrow \text{cast 回 BF16}
$$

**关键 trick**：loss scaling + 主权重（master weights）保留 FP32 副本——避免小梯度被舍入到 0。

### 3. 分布式训练的四种并行策略

| 策略 | 切分对象 | 通信开销 | 适用模型规模 |
|------|----------|----------|--------------|
| **数据并行（DDP）** | 样本 | AllReduce（梯度） | 7B 以下，单卡放得下 |
| **张量并行（TP）** | 矩阵分块 | AllReduce（前/后） | 70B+ 单层放不下 |
| **流水线并行（PP）** | 层 | 点对点（activation） | 175B+ 跨多机 |
| **3D 并行（DDP+TP+PP）** | 三者组合 | 综合 | GPT-4 / Claude 3 级 |

LLM 训练标准组合：**FSDP（PyTorch） + TP（Megatron-LM） + ZeRO-3（DeepSpeed）**。Megatron-LM 的张量并行公式：

$$
[Y_1, Y_2] = \left[\mathbf{X}_1 \mathbf{W}_1, \mathbf{X}_2 \mathbf{W}_2\right], \quad Y = \text{AllReduce}\left([Y_1, Y_2]\right)
$$

---

## 📜 演进史：框架 10 年的兴衰

| 时期 | 关键节点 | 设计哲学 |
|------|----------|----------|
| **2010-2014** | Theano → Caffe → Torch | 静态计算图；学术原型期 |
| **2015-2016** | TensorFlow 1.0（Google）→ Keras 整合 | "工业级部署"为目标，但 API 笨重 |
| **2016-2017** | PyTorch（Meta）→ 动态图 + Pythonic | "研究者友好"反超 TF，论文复现首选 |
| **2019** | TF 2.0（Eager 默认）+ SavedModel | TF 反击：向 PyTorch 学习，但仍缺研究生态 |
| **2020** | MindSpore 1.0（华为）→ 昇腾适配 | 国产化主战场，"端边云统一" |
| **2020-2021** | PaddlePaddle 2.0（百度）→ 飞桨 | "产业级"特色，自动并行成为差异化 |
| **2022** | DeepSpeed ZeRO-3 / Megatron-LM TP | 分布式训练进入"万卡时代" |
| **2023-2024** | vLLM（PagedAttention）/ TensorRT-LLM | 推理引擎独立为新赛道 |
| **2024-2025** | MindSpore 2.6 / Paddle 3.0 | 国产框架整合 DeepSeek 类大模型训练能力 |

**设计哲学反思**：

- TF 的"先定义图再执行"（静态）→ 部署友好但调试痛苦；
- PyTorch 的"边执行边定义"（动态）→ 调试友好但部署需 TorchScript；
- **2020 年后两者趋同**——TF 加 Eager、PyTorch 加 `torch.compile()` 静态化。
- **国产框架（MindSpore / Paddle）的差异化**不在 API，而在**与昇腾 / 昆仑芯的软硬协同**——纯软件层面已无壁垒。

---

## 🏛️ 框架选型实战案例（3+）

### 案例 1：Meta LLaMA-3（405B）训练——PyTorch + 16K H100

- **框架**：PyTorch 2.4 + FSDP + Megatron-LM TP + FlashAttention-2
- **训练时长**：约 30 天
- **关键 trick**：`torch.compile()` 让前向图自动融合，吞吐提升 ~30%
- **结论**：超大规模 LLM 训练已是**PyTorch 生态一统天下**（TF 在 GPT-4/Claude 时代的份额几乎为 0）

### 案例 2：阿里 Qwen-2.5 / 华为盘古——国产化栈（MindSpore + 昇腾）

- 训练硬件：昇腾 910B / 800I
- **关键技术**：MindSpore 2.6 的自动并行 + 集群拓扑感知调度
- **价值**：避开 NVIDIA 出口管制，构建"全国产"训练栈
- **挑战**：算子覆盖率 / 生态成熟度仍落后 CUDA 一代（约 2 年）

### 案例 3：Google Gemini——TensorFlow + JAX 双栈

- Google 内部两条线：TF（生产部署）+ JAX（研究 + TPU）
- **JAX** 的优势：`jit`/`vmap`/`pgrad` 三件套对研究极友好；TPU 原生
- **结论**：连 TF 的"亲爹" Google 都在用 JAX 做研究——**框架市场的真实格局是 PyTorch + JAX 二分**

---

## 💻 代码示例：PyTorch 手写混合精度训练

```python
import torch
from torch.cuda.amp import autocast, GradScaler

model = torch.nn.Linear(1024, 1024).cuda()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
scaler = GradScaler()  # FP16 的 loss scaler

for x, y in dataloader:
    optimizer.zero_grad()
    # autocast 自动判断哪些算子用 FP16，哪些用 FP32
    with autocast(dtype=torch.float16):
        out = model(x.cuda())
        loss = torch.nn.functional.cross_entropy(out, y.cuda())

    # scaler 把 loss × 1024，避免小梯度下溢
    scaler.scale(loss).backward()
    scaler.step(optimizer)         # unscale 后再更新
    scaler.update()               # 动态调整 scale 因子

# 现代推荐：直接用 BF16，无需 scaler
with torch.autocast("cuda", dtype=torch.bfloat16):
    out = model(x.cuda())
    loss = torch.nn.functional.cross_entropy(out, y.cuda())
loss.backward()
optimizer.step()
```

---

## ⚠️ 常见误区 / 反直觉点（3+）

1. **"PyTorch 部署不行，TF 部署强"**——历史正确，2025 已过时。**TorchServe + ONNX + vLLM** 让 PyTorch 部署生态追上甚至超越 TF。
2. **"MindSpore / Paddle 是国产版 PyTorch"**——半对。它们的 API 兼容 PyTorch（迁移成本低），但**核心价值在算子层与昇腾 / 昆仑芯的协同优化**，软件 API 是表层。
3. **"混合精度 = FP16"**——错。LLM 训练默认 **BF16**（FP32 动态范围 + FP16 显存），只有推理量化才用 FP16 / INT8。
4. **"模型越大训练越慢"**——错。**并行后** GPU 利用率提升，70B 模型在 1024 卡上训练速度可以快过单卡 7B（线性扩展比 ~85%）。
5. **"TensorFlow Lite 只支持 TF 模型"**——错。TFLite 已支持 **ONNX / PyTorch**（通过 `tf2onnx` 转换）。

---

## 🔗 跨模块反向链

- **同模块相邻**：[01-ml](../01-ml/README.md) — 传统 ML 算法底座（深度网络是监督学习的延伸）
- **同模块相邻**：[03-transformer](../03-transformer/README.md) — Transformer 架构核心（本节为其工程实现层）
- **AI 工程实战**：[`09.ai-applications/fine-tuning`](../../09.ai-applications/fine-tuning/) — LLM 预训练与微调实践（用 PyTorch + LoRA）
- **咬文嚼字**：[`12.interview/11.ai/transformer`](../../12.interview/11.ai/transformer/) — Transformer 面试题
- **兄弟主题**：[`08.ai-foundations/02-deep-learning/deep-learning-frameworks`](./deep-learning-frameworks.md) — 四框架详细对比
- **Java 联动**：[`01.java-and-jvm/`](../../01.java-and-jvm/) — Deeplearning4J / DJL 等 JVM 生态深度学习库的工程类比
- **故事叙事**：[`13.story/`](../../13.story/) — "阿明餐厅"系列讲解 PyTorch vs TF 的"厨房选型"类比

---

## 🗂️ 文章清单

| 标题 | 路径 | 状态 | 摘要 |
|------|------|------|------|
| 深度学习框架 | [deep-learning-frameworks.md](./deep-learning-frameworks.md) | ✅ 已完成（76 行） | 对比 MindSpore / PyTorch / TensorFlow / PaddlePaddle 的定位、特点、选型建议和 2025-2026 发展趋势。 |

> **覆盖说明**：当前 `02-deep-learning/` 仅沉淀 1 篇（deep-learning-frameworks.md），覆盖四框架对比与选型建议；Transformer 训练技巧与分布式训练是工程落地的核心，建议尽快补齐。

## 🔗 关联主题

- **父模块**：[08.ai-foundations](../README.md) — AI 基础层总索引
- **同模块相邻**：[01-ml](../01-ml/README.md) — 传统 ML 算法底座
- **同模块相邻**：[03-transformer](../03-transformer/README.md) — Transformer 架构核心
- **AI 工程实战**：[`09.ai-applications/fine-tuning`](../../09.ai-applications/fine-tuning/) — LLM 预训练与微调实践
- **项目沉淀**：[spring-ai-loomagent](https://github.com/wb04307201/spring-ai-loomagent) — Spring AI 集成框架

## 📚 学习路径

1. **入门**：阅读 [deep-learning-frameworks.md](./deep-learning-frameworks.md)，建立四框架对比脑图
2. **选型决策**：根据团队技术栈、硬件环境、部署需求选择框架（学术 → PyTorch / 国产化 → MindSpore / 工业 → TensorFlow）
3. **训练技巧**：补充 Transformer 训练专题，重点掌握 AMP、Gradient Accumulation、AdamW
4. **分布式训练**：补充分布式训练专题，理解 DDP / TP / PP / 3D 并行的适用场景
5. **深度学习理论**：跳转 [03-transformer](../03-transformer/README.md) 看核心架构
6. **工程落地**：跳转 [09.ai-applications/fine-tuning](../../09.ai-applications/fine-tuning/) 看 LLM 微调实战

## 📊 本节统计

- **子目录总数**：1 个（02-deep-learning/）
- **已沉淀文章**：1 篇（deep-learning-frameworks.md）
- **待补占位**：2 篇（Transformer 训练技巧 / 分布式训练）
- **总行数**（不含 README）：约 76 行
- **最后更新**：2026-09-01

---

> 📅 2026-09-01 · 咬文嚼字 · 深度学习框架与训练范式 · ⭐⭐⭐（高频面试 + 实战必会）

---

← [返回 08.ai-foundations](../README.md)