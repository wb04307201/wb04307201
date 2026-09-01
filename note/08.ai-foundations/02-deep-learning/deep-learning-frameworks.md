<!--
module:
  parent: 08.ai-foundations/02-deep-learning
  slug: 08.ai-foundations/02-deep-learning/deep-learning-frameworks
  type: article
  category: 主模块子文章
  summary: 深度学习框架四大门派（PyTorch / TensorFlow / MindSpore / PaddlePaddle）的演进、数学内核、训练范式与选型决策树。
  depth: ⭐⭐⭐⭐⭐
-->

# 深度学习框架

> **一句话定位**：深度学习框架 = **自动微分引擎 + 计算图 IR + 算子库 + 分布式运行时**。PyTorch 主攻研究（动态图 + Pythonic）、TensorFlow 主攻生产（静态图 + Serving）、MindSpore/PaddlePaddle 主攻国产化硬件（昇腾/昆仑），**场景决定选择，没有银弹**。

> ⬅️ [返回深度学习](../README.md)

---

## 🎯 学习目标

完成本文后，你能够：

- **技术分层**：用 4 层架构（自动微分 / 计算图 / 算子库 / 运行时）解释任何深度学习框架
- **市场格局**：说出 PyTorch / TensorFlow / MindSpore / PaddlePaddle 在研究与生产中的份额变化
- **选型决策**：根据"硬件 + 阶段 + 团队"3 维度给具体业务场景推荐框架
- **演进认知**：讲清 2014-2026 框架融合趋势（PyTorch 借鉴 TF Serving、TF 借鉴 PyTorch Eager）

---

## 📚 章节清单

| 章节 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 框架的 4 层架构** | 自动微分 / 计算图 / 算子库 / 运行时 | 20 min |
| **02 PyTorch：研究之王** | 动态图 + Pythonic + 生态护城河 | 25 min |
| **03 TensorFlow：生产标杆** | 静态图 + XLA + TF Serving/TFLite/TF.js | 20 min |
| **04 MindSpore / PaddlePaddle：国产化双雄** | 昇腾适配 + 全场景 + 训推一体 | 20 min |
| **05 演进史时间线（2014-2026）** | Theano → Caffe → TF → PyTorch → MindSpore | 15 min |
| **06 选型决策树** | 6 类场景 + 决策矩阵 + 实战案例 | 15 min |
| **07 反直觉与误区** | 5 大高频认知偏差 | 15 min |

---

## 一、框架的 4 层技术架构

理解任何深度学习框架，从这 4 层切入：

```text
┌──────────────────────────────────────────────────────────┐
│ Layer 4：分布式运行时（Distributed Runtime）              │
│   - 集合通讯（NCCL / HCCL / 自研）                       │
│   - 数据并行 / 模型并行 / 流水并行                       │
│   - DeepSpeed / FSDP / Megatron-LM                       │
├──────────────────────────────────────────────────────────┤
│ Layer 3：算子库（Operator Library）                       │
│   - BLAS / cuDNN / cuBLAS / 自定义算子                   │
│   - Conv / MatMul / Attention / Embedding                │
├──────────────────────────────────────────────────────────┤
│ Layer 2：计算图 IR（Intermediate Representation）         │
│   - 静态图（TF Graph / MindSpore GE / TVM IR）          │
│   - 动态图（PyTorch Eager / JAX Trace）                  │
│   - 图优化：算子融合 / 常量折叠 / 内存规划               │
├──────────────────────────────────────────────────────────┤
│ Layer 1：自动微分（Auto-Differentiation）                 │
│   - 反向模式（Reverse-Mode, Backprop）                   │
│   - 前向模式（Forward-Mode, JVP）                       │
│   - Tape / Trace / Operator Overload 三种实现            │
└──────────────────────────────────────────────────────────┘
```

### 1.1 自动微分：所有框架的"心脏"

**核心数学**：链式法则（Chain Rule）

$$
\frac{\partial \mathcal{L}}{\partial \mathbf{W}_l} = \frac{\partial \mathcal{L}}{\partial \mathbf{a}_L} \cdot \prod_{k=l+1}^{L} \frac{\partial \mathbf{a}_k}{\partial \mathbf{a}_{k-1}} \cdot \frac{\partial \mathbf{a}_l}{\partial \mathbf{W}_l}
$$

**三种实现范式**：

| 范式 | 原理 | 代表 | 优缺点 |
|------|------|------|--------|
| **Operator Overload** | 重载 `+`、`*` 记录计算 | PyTorch Eager、NumPy | 灵活但不能重做图优化 |
| **Tape-based** | 录制前向 tape，回放反向 | PyTorch `torch.autograd` | 易调试，性能需 JIT |
| **Trace-based** | 追踪执行构造图 | JAX、TF @tf.function | 性能好但难条件分支 |

**PyTorch 实现**（`torch.autograd.Function`）：

```python
import torch

# 自定义算子带反向传播
class LinearWithBias(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, W, b):
        ctx.save_for_backward(x, W)
        return x @ W + b

    @staticmethod
    def backward(ctx, grad_out):
        x, W = ctx.saved_tensors
        grad_x = grad_out @ W.T
        grad_W = x.T @ grad_out
        grad_b = grad_out.sum(0)
        return grad_x, grad_W, grad_b

# 使用
x = torch.randn(32, 128, requires_grad=True)
W = torch.randn(128, 64, requires_grad=True)
b = torch.randn(64, requires_grad=True)
y = LinearWithBias.apply(x, W, b)
y.sum().backward()  # 反向传播
print(W.grad.shape)  # (128, 64)
```

### 1.2 计算图：静态 vs 动态的世纪之争

**核心问题**：是先构图再执行（静态），还是边执行边构图（动态）？

| 维度 | 静态图（Define-then-Run） | 动态图（Define-by-Run） |
|------|---------------------------|--------------------------|
| **构建时机** | 编译期（`@tf.function`） | 运行时（Eager） |
| **可优化空间** | 大（常量传播、内存复用） | 小（每步重新构造） |
| **调试友好** | 差（print 不到中间 tensor） | 优（Python 原生 debugger） |
| **代表** | TF 1.x / MindSpore GE / XLA | PyTorch / TF 2.x Eager / JAX |
| **现代趋势** | 静态图通过 `torch.compile()` / `torch.export` 复活 | 动态图通过 `torch.compile` + Inductor 获得静态图性能 |

**反直觉点**：**2024 年后 PyTorch 反而在静态图方向追赶**（`torch.compile` 是 2023 PyTorch 2.0 杀手锏，性能比 Eager 快 30-50%），而 TF 2.x 转向 Eager。两者在融合。

---

## 二、PyTorch：研究之王

### 2.1 关键事实

- **开发商**：Meta（原 Facebook，2016 年开源）
- **市场份额**：2024 年研究领域占比 **80%+**（Papers With Code 统计），生产部署占比约 50%
- **GitHub Stars**：85k+（2026 年统计）
- **核心版本**：PyTorch 2.0（2023 年 3 月，引入 `torch.compile`）

### 2.2 核心优势

1. **动态图（Eager Execution）**
   - 训练过程中可实时修改网络结构（`if/while`、动态 shape）
   - Pythonic API，`tensor.numpy()`、GPU tensor 无缝切换
   - 调试便利：`pdb.set_trace()` 直接打断点

2. **生态护城河（LLM 时代核心）**
   - **Transformers（HuggingFace）**：90%+ SOTA 模型原生 PyTorch 实现
   - **DeepSpeed**（Microsoft）：ZeRO-1/2/3 + Offload，万卡训练标配
   - **FSDP**（PyTorch 原生）：替代 DDP 的分片数据并行
   - **vLLM / SGLang**：推理引擎深度集成 PyTorch

3. **学习曲线**
   - 与 Python/NumPy 一致，新手 1 周可上手
   - 文档质量极高（`pytorch.org/tutorials`）

### 2.3 代码示例：训练一个 GPT-2 简化版

```python
import torch
import torch.nn as nn

class MiniGPT(nn.Module):
    def __init__(self, vocab_size, d_model=512, n_heads=8, n_layers=6):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, dim_feedforward=2048)
            for _ in range(n_layers)
        ])
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        x = self.embed(x)
        for layer in self.layers:
            x = layer(x)
        return self.head(x)

# 训练（简化版）
model = MiniGPT(vocab_size=50000).cuda()
optim = torch.optim.AdamW(model.parameters(), lr=3e-4)

for step, batch in enumerate(dataloader):
    x, y = batch["input_ids"].cuda(), batch["labels"].cuda()
    logits = model(x)
    loss = nn.functional.cross_entropy(
        logits.view(-1, logits.size(-1)), y.view(-1)
    )
    loss.backward()
    optim.step()
    optim.zero_grad()

    if step % 100 == 0:
        print(f"step {step}, loss {loss.item():.3f}")
```

### 2.4 PyTorch 2.x 的关键演进

| 版本 | 年份 | 关键特性 |
|------|------|---------|
| **1.0** | 2018 | TorchScript JIT + ONNX 导出 |
| **1.5** | 2020 | DistributedDataParallel 成熟 |
| **1.11** | 2022 | `torch.func`（JAX-style 函数式 API）|
| **2.0** | 2023 | `torch.compile()`（Inductor 后端，性能 30-50% 提升）|
| **2.1** | 2023 | FSDP v2 + 分布式 checkpoint |
| **2.4** | 2024 | `torch.export` + AOTAutograd 稳定 |

---

## 三、TensorFlow：生产标杆

### 3.1 关键事实

- **开发商**：Google Brain（2015 年开源，2019 年 TF 2.0 重大重构）
- **生产地位**：企业级 ML 平台（Vertex AI）、TFX 流水线、移动端 TFLite、Web 端 TF.js 全栈覆盖
- **现状**：研究领域被 PyTorch 蚕食（占比从 2019 年 70% 跌至 2024 年 15%），但**生产部署仍是老大**

### 3.2 TF 的"护城河"：部署生态

| 部署目标 | 框架组件 | 典型应用 |
|---------|---------|---------|
| **服务端** | TF Serving + Docker + Kubernetes | YouTube 推荐、广告 CTR 预估 |
| **移动端** | TFLite + 量化（INT8） | 手机输入法、图像分类 App |
| **Web/JS** | TF.js + WebGL/WebAssembly | 网页端实时手势识别 |
| **边缘设备** | TF Lite Micro + Cortex-M | MCU 上的语音唤醒词检测 |
| **企业流水线** | TFX + Vertex AI | Google 内部 ML 平台 |

### 3.3 TF 2.x 的 Eager 转型

TF 2.x（2019）默认开启 Eager Mode，与 PyTorch 看齐。开发者可选择性使用 `@tf.function` 装饰器切换到静态图：

```python
import tensorflow as tf

# 动态图（Eager，调试友好）
@tf.function  # 切换到静态图（性能优化）
def train_step(x, y):
    with tf.GradientTape() as tape:
        logits = model(x, training=True)
        loss = tf.keras.losses.sparse_categorical_crossentropy(y, logits, from_logits=True)
    grads = tape.gradient(loss, model.trainable_variables)
    optim.apply_gradients(zip(grads, model.trainable_variables))
    return loss
```

### 3.4 TF 的"杀手锏"：XLA 编译器

**XLA（Accelerated Linear Algebra）** = TF 的图优化编译器：

- **算子融合**：将多个小算子融合为一个 GPU kernel（性能 2-5x）
- **内存优化**：减少中间 tensor 显存占用
- **跨硬件**：CPU / GPU / TPU 自动 codegen

PyTorch 直到 2023 年才有等价物（`torch.compile` + Inductor），落后 TF 5 年。

### 3.5 TF 的衰退原因

1. **API 频繁变动**：TF 1.x → 2.x 几乎是重写，旧代码迁移成本高
2. **研究社区转向 PyTorch**：2019 年后 80% SOTA 论文用 PyTorch
3. **静态图调试痛苦**：研究阶段需要频繁修改网络结构，TF 不适配
4. **Windows GPU 支持断裂**：TF 2.10+ 不再原生支持 Windows GPU，需 WSL

---

## 四、MindSpore / PaddlePaddle：国产化双雄

### 4.1 MindSpore（昇思）

**关键事实**：

- **开发商**：华为（2019 年开源，2020 年 3 月正式发布）
- **2024 中国 AI 框架新增市场份额**：30.26%（中国第一）
- **生态规模**：下载量 1300 万+，覆盖 156 国，社区核心贡献者 5.2 万+
- **核心场景**：昇腾 NPU 全栈适配、端边云协同

**关键技术特性**：

1. **动静态图统一**：`ms.jit` 一行装饰器切换
2. **全场景统一架构**：端（手机）、边（IoT 网关）、云（昇腾集群）一套 API
3. **超节点优化**：万卡级集群的软硬件协同（2024 新版本）
4. **强化学习套件**：内置 PPO / SAC / DQN，AlphaFold / AlphaZero 复现支持

**代码示例**：

```python
import mindspore as ms
from mindspore import nn, ops

class MiniGPT(nn.Cell):
    def __init__(self, vocab_size, d_model=512):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.dense = nn.Dense(d_model, vocab_size)

    def construct(self, x):  # 注意不是 forward
        return self.dense(self.embed(x))

model = MiniGPT(vocab_size=50000)
loss_fn = nn.CrossEntropyLoss()
optim = nn.AdamWeightDecay(model.trainable_params(), learning_rate=3e-4)

# 自动并行（MindSpore 杀手锏）
model = ms.set_auto_parallel_context(parallel_mode=ms.ParallelMode.AUTO_PARALLEL)
```

### 4.2 PaddlePaddle（飞桨）

**关键事实**：

- **开发商**：百度（2016 年开源）
- **2024 中国市场份额**：约 25%（中国第二）
- **核心场景**：产业实践、训推一体、昇腾/海光/寒武纪等国产芯片适配

**关键技术特性**：

1. **动静统一设计**：`paddle.jit.to_static` 一键转换
2. **自动并行**：`fleet` 库支持数据并行、张量并行、流水并行
3. **3.0-beta 昇腾版**：专门优化昇腾硬件，国产芯片性能对标 CUDA
4. **产业级模型库**：PP-YOLO、PP-OCR、PP-Structure 等开箱即用

### 4.3 国产化框架的"卡位优势"

| 维度 | MindSpore | PaddlePaddle | 国际框架（PyTorch/TF）|
|------|-----------|--------------|----------------------|
| **昇腾适配** | 原生（华为主导）| 3.0+ 优化 | 需 torch_npu（社区支持）|
| **政策合规** | 信创目录 | 信创目录 | 受限 |
| **国产生态** | 华为云 + 昇腾 | 百度云 + 文心 | 无 |

**反直觉点**：**国产化框架不是"替代"，而是"互补"**——昇腾集群上 PyTorch 也能跑（`torch_npu`），但 MindSpore 性能更优（10-30%）；CPU/GPU 上 PyTorch 仍是首选。

---

## 五、演进史时间线（2014-2026）

```text
2014  Theano          —— 第一个深度学习框架（蒙特利尔大学），已退役
2014  Caffe           —— Berkeley，CNN 时代标杆，2020 年停止维护
2015  TensorFlow      —— Google，静态图 + 生产部署
2016  PyTorch         —— Meta（Facebook），动态图 + 研究友好
2016  PaddlePaddle    —— 百度，国产化先行者
2016  Keras           —— 多后端高级 API，现归入 TF
2017  MXNet           —— Amazon 主推，被 SageMaker 采用
2018  ONNX            —— 跨框架模型交换格式（Meta + Microsoft 主导）
2019  MindSpore       —— 华为，国产化 + 全场景
2019  TF 2.0          —— Eager 模式默认，PyTorch 看齐
2020  JAX             —— Google，函数式 + TPU 优化
2022  PyTorch 2.0     —— torch.compile，静态图性能突破
2023  torch.compile   —— Inductor 默认后端
2024  MindSpore 2.6   —— 类 DeepSeek 训练 + RL 套件
2025  PaddlePaddle 3.0—— 国产异构芯片全适配
2026  框架融合期      —— PyTorch + TF + MindSpore 互操作性 90%+
```

### 关键转折点

| 时间 | 事件 | 影响 |
|------|------|------|
| **2017** | PyTorch 研究领域超越 TF | 学术界全面倒向 PyTorch |
| **2018** | ONNX 标准化 | 跨框架模型可移植 |
| **2019** | TF 2.0 转向动态图 | TF 承认 Eager 是趋势 |
| **2020** | GPT-3 论文引爆 LLM | PyTorch 成为 LLM 训练事实标准 |
| **2022** | ChatGPT 出圈 | LLM 推理生态（vLLM/SGLang）全栈 PyTorch |
| **2023** | PyTorch 2.0 + torch.compile | 性能追平 TF XLA |
| **2024** | DeepSeek-V2 / Qwen-2.5 开源 | 国产框架 + 国产芯片 + 国产模型三角形成 |

---

## 六、选型决策树

### 6.1 6 类场景 + 推荐框架

| 应用场景 | 推荐框架 | 理由 |
|---------|---------|------|
| **学术研究 / 算法创新** | PyTorch | 动态图灵活调试，社区论文复现资源丰富 |
| **LLM 预训练（GPU 集群）** | PyTorch + DeepSpeed/FSDP | HuggingFace 生态 95% 模型原生支持 |
| **LLM 推理服务（GPU）** | PyTorch + vLLM/SGLang/TensorRT-LLM | KV Cache + PagedAttention + 投机解码 |
| **大模型训练（国产硬件）** | MindSpore / PaddlePaddle | 适配昇腾/昆仑芯，全栈协同 |
| **工业部署 / 移动端** | TF Lite / Paddle Lite | 成熟的轻量化部署方案 |
| **企业级生产系统** | TF / PaddlePaddle + TFX | 完善的 MLOps 工具链 |
| **端边云协同场景** | MindSpore | 原生支持全场景统一架构 |
| **跨平台 Web 推理** | TF.js / ONNX Runtime Web | 浏览器内实时推理 |

### 6.2 决策矩阵（团队视角）

| 团队画像 | 推荐 |
|---------|------|
| **学术 PhD / 算法研究员** | PyTorch（不可替代）|
| **互联网大厂 AI 平台团队** | PyTorch（生态优先）+ TF（生产兜底）|
| **国产化要求（信创 / 政企）** | MindSpore / PaddlePaddle |
| **端侧部署（IoT / 嵌入式）** | TF Lite Micro / MindSpore Lite |
| **初创公司快速迭代** | PyTorch + HuggingFace + vLLM |
| **传统企业（银行 / 制造）** | TF + TFX / PaddlePaddle + PaddleX |

### 6.3 实战案例：3 个真实场景

**案例 1：Meta（PyTorch 自家）**

- **业务**：推荐系统、广告 CTR、LLama 训练
- **框架**：PyTorch + FSDP + Megatron-LM
- **规模**：2.4 万 GPU 集群训练 LLaMA-3
- **决策**：研究/生产全栈 PyTorch，无 TF 包袱

**案例 2：华为（MindSpore 自家）**

- **业务**：盘古大模型、昇腾集群、端侧鸿蒙 AI
- **框架**：MindSpore + 昇腾 NPU
- **规模**：万卡昇腾集群，MindSpore 性能比 PyTorch + torch_npu 提升 10-30%
- **决策**：国产化 + 软硬件协同优势

**案例 3：百度文心（PaddlePaddle 自家）**

- **业务**：文心大模型、搜索、广告、自动驾驶
- **框架**：PaddlePaddle + 昆仑芯 / 昇腾
- **规模**：文心 4.0（千亿参数）训练使用 PaddlePaddle
- **决策**：训推同套框架，部署成本低

**案例 4：OpenAI（TF → PyTorch 转型）**

- **业务**：GPT 系列、DALL-E、Sora
- **框架**：早期 TF → 现 PyTorch + 自研引擎
- **决策**：2019 年从 TF 全面转向 PyTorch，因研究迭代速度

**案例 5：Google DeepMind（TF + JAX 双栈）**

- **业务**：Gemini、AlphaFold、AlphaZero
- **框架**：JAX（研究） + TF（生产）
- **决策**：JAX 用于算法原型（函数式 + TPU 优化），TF Serving 用于生产部署

**案例 6：Anthropic（PyTorch）**

- **业务**：Claude 系列
- **框架**：PyTorch + 自研推理引擎
- **规模**：Claude 3.5 Sonnet 训练集群千卡级

---

## 七、反直觉点与误区（5 大高频认知偏差）

### 误区 1：❌ PyTorch 不能用于生产

**真相**：**PyTorch 在生产环境已占主导**

- **TorchServe**（AWS 官方）+ **Triton Inference Server**（NVIDIA）+ **vLLM**（开源）覆盖推理服务全场景
- 2024 年 OpenAI、Anthropic、Mistral、Meta 等头部公司全部生产环境用 PyTorch
- 唯一短板：移动端不如 TF Lite

### 误区 2：❌ 静态图已经过时

**真相**：**静态图通过编译器复活，且性能更优**

- `torch.compile`（2023）是 PyTorch 的图编译器，性能比 Eager 快 30-50%
- JAX 借助 TPU 统治 Google DeepMind
- TF XLA 仍是 Google 生产部署首选

### 误区 3：❌ 国产框架只能"国产硬件"用

**真相**：**国产框架在 GPU 上也可用**，只是国产硬件上性能更优

- MindSpore 支持 GPU（CUDA）和昇腾双后端
- PaddlePaddle 支持 NVIDIA、海光、寒武纪等多芯片
- 选择国产框架不强制绑定国产硬件

### 误区 4：❌ TF 已经"死了"

**真相**：**TF 在生产部署和 Google 生态仍是老大**

- TF Serving 仍是企业 ML 部署最成熟方案
- TFX 流水线覆盖 Vertex AI
- TF Lite 是移动端 + 嵌入式事实标准（80%+ 市场份额）

### 误区 5：❌ 框架选型决定 AI 团队上限

**真相**：**框架是工具，决定上限的是数据 + 算法 + 算力**

- AlphaFold 用 JAX / TF / PyTorch 都做出了诺奖级成果
- 切换框架成本：1-3 个月迁移期，远低于数据/算法迭代成本
- 真正卡脖子的是 GPU 集群规模和数据质量

---

## 八、代码示例：3 个典型场景对比

### 8.1 PyTorch（动态图）

```python
import torch

# 1. 模型定义
model = torch.nn.Sequential(
    torch.nn.Linear(784, 256),
    torch.nn.ReLU(),
    torch.nn.Linear(256, 10)
)

# 2. 训练循环
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
for x, y in dataloader:
    logits = model(x)
    loss = torch.nn.functional.cross_entropy(logits, y)
    optimizer.zero_grad()
    loss.backward()  # 自动微分
    optimizer.step()
```

### 8.2 TensorFlow（静态图 + Eager）

```python
import tensorflow as tf

# 1. 模型定义（Keras API）
model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(10)
])

# 2. 编译 + 训练
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)
model.fit(dataloader, epochs=10)

# 3. 导出 SavedModel（生产部署）
model.save("saved_model/")
```

### 8.3 MindSpore（动静统一）

```python
import mindspore as ms
from mindspore import nn

# 1. 模型定义
class Network(nn.Cell):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Dense(784, 256)
        self.fc2 = nn.Dense(256, 10)

    def construct(self, x):
        return self.fc2(ms.ops.relu(self.fc1(x)))

# 2. 训练（动静统一）
model = Network()
loss_fn = nn.CrossEntropyLoss()
optimizer = nn.Adam(model.trainable_params(), learning_rate=1e-3)

# 静态图加速（一行切换）
model = ms.compile(model, backend="ms")  # 性能提升 20-50%
```

---

## 九、跨模块反向链

| 主题 | 链接 |
|------|------|
| **数学基础（自动微分链式法则）** | [08.ai-foundations/01-ml/ml-to-rl](../01-ml/ml-to-rl.md) |
| **Transformer 架构（PyTorch 实现）** | [08.ai-foundations/03-transformer/transformer-architecture](../03-transformer/transformer-architecture.md) |
| **注意力机制（Flash Attention）** | [08.ai-foundations/03-transformer/attention-mechanism](../03-transformer/attention-mechanism.md) |
| **LLM 训练（DeepSpeed / FSDP）** | [08.ai-foundations/04-llm/llm-basics](../04-llm/llm-basics.md) |
| **Dropout 配置考古** | [08.ai-foundations/04-llm/dropout-in-llm/single-epoch-and-config-evidence](../04-llm/dropout-in-llm/single-epoch-and-config-evidence.md) |
| **Embedding / Tokenization** | [08.ai-foundations/05-tokenization-embedding/embedding](../05-tokenization-embedding/embedding.md) |
| **推理引擎选型（vLLM/TensorRT）** | [09.ai-applications/llm-inference](../09.ai-applications/llm-inference/inference-engine-selection.md) |
| **KV Cache 加速** | [09.ai-applications/llm-inference/kv-cache-mqa-gqa-mla](../09.ai-applications/kv-cache-mqa-gqa-mla.md) |
| **微调（PEFT/LoRA）** | [09.ai-applications/fine-tuning](../09.ai-applications/fine-tuning/) |
| **RAG 检索（向量数据库）** | [09.ai-applications/rag/vector-search-at-scale](../09.ai-applications/rag/vector-search-at-scale/) |
| **分布式训练（万卡集群）** | [06.distributed-systems/distributed-training](../06.distributed-systems/distributed-training/) |
| **GPU 资源调度** | [06.distributed-systems/gpu-cluster-scheduling](../06.distributed-systems/gpu-cluster-scheduling/) |
| **MLOps 平台** | [09.ai-applications/production-stability](../09.ai-applications/production-stability/) |
| **面试题：框架选型** | [12.interview/11.ai/transformer](../12.interview/11.ai/transformer/) |
| **故事：AI 框架演进** | [13.story/11-ai-learning-paradox](../../13.story/11-ai-learning-paradox.md) |
| **故事：AI 工程化** | [13.story/42-ai-engineer-responsibility](../../13.story/42-ai-engineer-responsibility.md) |

---

## 十、面试 Checklist（30 秒话术）

**问题 1：为什么 PyTorch 在研究领域占主导？**

- 答：动态图（Eager）+ Pythonic API + HuggingFace 生态。**研究阶段需要频繁修改网络结构**，PyTorch 调试便利 + 论文复现资源 90%+。1 行答完。

**问题 2：TF 的优势是什么？**

- 答：**生产部署全栈覆盖**（Serving + Lite + JS + TFX）。Google 自家 Vertex AI、企业级 MLOps 流水线、移动端 80%+ 市场。1 行答完。

**问题 3：国产框架（MindSpore/PaddlePaddle）适用场景？**

- 答：**国产硬件（昇腾/昆仑/海光/寒武纪）+ 信创合规**。软硬件深度协同，万卡集群性能比 PyTorch + torch_npu 高 10-30%。1 行答完。

**问题 4：`torch.compile` 为什么重要？**

- 答：**PyTorch 性能追平 TF XLA 的关键**，图优化（算子融合、内存复用）性能 30-50% 提升。2023 PyTorch 2.0 杀手锏。1 行答完。

---

## 📚 参考来源

1. **PyTorch 自动微分原理**：Adam Paszke, Sam Gross, Soumith Chintala, Gregory Chanan et al. *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. NeurIPS 2019. https://arxiv.org/abs/1912.01703
2. **TensorFlow XLA 编译器**：TensorFlow XLA Team. *XLA: Optimizing Compiler for TensorFlow*. 2017. https://www.tensorflow.org/xla
3. **MindSpore 自动微分**：Huawei. *MindSpore: Towards Usability and High Performance*. 2020. https://arxiv.org/abs/2005.00224
4. **DeepSpeed ZeRO**：Samyam Rajbhandari, Olatunji Ruwase, Jeff Rasley, Sam Smith et al. *ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning*. SC 2021. https://arxiv.org/abs/2104.07857
5. **`torch.compile` 论文**：Jason Ansel, Edward Z. Yang, Horace He, Natalia Gimelshein et al. *PyTorch 2.0: Advisor, Compiler, and Performance Features*. 2024. https://pytorch.org/blog/pytorch-2-0/
6. **国产 AI 框架市场报告**：IDC China. *中国 AI 框架市场份额报告 2024*. 2024.
7. **Adam 优化器**：Diederik P. Kingma, Jimmy Ba et al. *Adam: A Method for Stochastic Optimization*. ICLR 2015. https://arxiv.org/abs/1412.6980
8. **JAX 函数式编程**：James Bradbury, Roy Frostig, Peter Hawkins, Matthew James Johnson et al. *JAX: composable transformations of Python+NumPy programs*. 2018. https://github.com/google/jax

---

← [返回 AI 框架选型](../README.md)