<!--
question:
  id: 02.computer-basics-gradient-descent-variants
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [ML, 梯度下降, SGD, Adam, AdamW, 学习率]
-->

# 梯度下降 SGD / BGD / Adam：4 种变体的数学差异

> **一句话定位**：同样沿负梯度更新参数，BGD、SGD、Mini-Batch、Adam 与 AdamW 的差别集中在**梯度估计方式、步长缩放方式和正则化位置**。

> **系列定位**：经典 ML 高频题。考察的不是背一句“Adam 收敛快”，而是能否写出**动量与偏差修正公式**、解释 **AdamW 为何解耦权重衰减**，并按 LLM / CV 场景选优化器。

---

## 引子：训练 7B LLM，为什么不用 SGD？

团队准备训练一个 7B 参数模型：若用 SGD，单步计算简单，却需要对所有参数共享同一个有效学习率，面对稀疏、尺度差异巨大的梯度时收敛很慢；换成 Adam 后，训练初期 loss 降得更快，但把 L2 正则直接塞进梯度又会被二阶动量缩放，权重衰减不再一致。于是方案变成 **AdamW + 前 1%～5% Warmup + Cosine LR**。面试官继续追问：AdamW 只是 Adam 加了正则吗？SGD 在什么任务上反而更好？答案必须落到更新公式和泛化差异，而不是“LLM 都这么用”。

---

## 一、核心原理

### 1.1 BGD / SGD / Mini-Batch：差别在梯度估计

设参数为 $\theta$、学习率为 $\alpha$，全量目标为 $J(\theta)$。

- **BGD（Batch Gradient Descent）**：每一步扫描全部 $N$ 个样本，$\theta = \theta - \alpha \cdot \nabla J(\theta)$。梯度方差小、下降稳定，但单步慢且占用显存大。
- **SGD（Stochastic Gradient Descent）**：每一步只取一个样本，$\theta = \theta - \alpha \cdot \nabla J(\theta; x_i; y_i)$。单步快、噪声大，能跳出部分尖锐极小值，但 loss 曲线震荡。
- **Mini-Batch GD**：取批次 $B$ 估计梯度，$g_t=\frac{1}{|B|}\sum_{i\in B}\nabla J(\theta;x_i,y_i)$。常见 `batch_size=32-256`，可利用 GPU 向量化，是工业训练标准。

| 方法 | 每步样本 | 梯度方差 | 单步成本 | 典型场景 |
|---|---:|---:|---:|---|
| BGD | 全量 $N$ | 最低 | 最高 | 小数据凸优化 |
| SGD | 1 | 最高 | 最低 | 在线学习、经典 CV |
| Mini-Batch | 32～256 | 中等 | 中等 | 深度学习 |

### 1.2 Adam：一阶动量 + 二阶动量 + 偏差修正

令当前 Mini-Batch 梯度为 $g_t=\nabla_\theta J_t(\theta_{t-1})$，Adam（Kingma & Ba，2014）的完整更新为：

$$m_t=\beta_1m_{t-1}+(1-\beta_1)g_t$$

$$v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2$$

$$\hat m_t=\frac{m_t}{1-\beta_1^t},\qquad \hat v_t=\frac{v_t}{1-\beta_2^t}$$

$$\theta_t=\theta_{t-1}-\alpha\frac{\hat m_t}{\sqrt{\hat v_t}+\varepsilon}$$

$m_t$ 平滑梯度方向，$v_t$ 按参数记录梯度平方尺度；帽子项修正零初始化造成的早期偏差。Adam 因而不是“自动找到最佳学习率”，而是用 $\alpha/\sqrt{\hat v_t}$ 为每个参数自适应缩放步长。

### 1.3 AdamW：权重衰减与自适应梯度解耦

AdamW 把衰减项直接作用于参数，而不是先把 $\lambda\theta$ 混入梯度再经过 $1/\sqrt{\hat v_t}$ 缩放：

$$\theta_t=\theta_{t-1}-\alpha\frac{\hat m_t}{\sqrt{\hat v_t}+\varepsilon}-\alpha\lambda\theta_{t-1}$$

也可写成 $\theta_t=(1-\alpha\lambda)\theta_{t-1}-\alpha\hat m_t/(\sqrt{\hat v_t}+\varepsilon)$。这就是数学差异：**Adam + L2** 的正则梯度会被自适应预条件器缩放；**AdamW** 的每个参数都按同一比例衰减，$\lambda$ 的含义更稳定。

---

## 二、代码示例：同一 toy 数据集对比 SGD 与 Adam

下面 25 行 PyTorch 代码固定初始化和数据，只替换优化器，绘制 200 步 MSE loss 曲线：

```python
import torch
import matplotlib.pyplot as plt
torch.manual_seed(42)
x = torch.linspace(-2, 2, 256).unsqueeze(1)
y = 3 * x - 0.7 + 0.4 * torch.randn_like(x)

def run(kind, lr):
    model = torch.nn.Linear(1, 1)
    torch.nn.init.zeros_(model.weight); torch.nn.init.zeros_(model.bias)
    opt_cls = torch.optim.SGD if kind == "SGD" else torch.optim.Adam
    opt = opt_cls(model.parameters(), lr=lr)
    curve = []
    for _ in range(200):
        opt.zero_grad()
        loss = torch.nn.functional.mse_loss(model(x), y)
        loss.backward()
        opt.step()
        curve.append(loss.item())
    return curve

curves = {"SGD(lr=0.05)": run("SGD", 0.05), "Adam(lr=0.05)": run("Adam", 0.05)}
for name, values in curves.items():
    plt.plot(values, label=name)
plt.xlabel("step"); plt.ylabel("MSE loss")
plt.legend(); plt.yscale("log"); plt.show()
```

该例用于观察优化轨迹，不用于证明 Adam 必然优于 SGD；学习率、初始化与数据条件变化都可能改变曲线。

---

## 三、常见陷阱

### 陷阱 1：Adam 默认超参数是“通用最优”

`β1=0.9、β2=0.999、ε=1e-8` 只是稳健默认值。Transformer / LLM 训练常把 `β2` 调到 `0.95`，让二阶动量更快跟踪非平稳梯度；是否更稳仍应结合模型配方验证。

### 陷阱 2：AdamW 的 `weight_decay=0.1` 可有可无

LLM 配方中 `λ=0.1` 常是关键正则项，不加时更容易过拟合、权重范数失控。但“必需”是典型工程配方而非普适定理；Norm 与 bias 参数通常不做衰减，小数据微调也需重新搜索。

### 陷阱 3：Cosine LR 可以从第 1 步直接衰减

大模型训练通常必须先 Warmup 前 `1%-5%` 步，把学习率从接近 0 升至峰值，再做 Cosine 衰减；否则随机初始化阶段的大梯度可能引发震荡、溢出甚至训练崩溃。

### 陷阱 4：深度学习一律使用 Adam

SGD + Momentum 在 CV / CNN 任务上仍常占优：虽然前期收敛慢，但其噪声和隐式正则可能带来更好的最终泛化。优化器应按任务与验证集结果选择。

### 陷阱 5：学习率固定不衰减也能训练到底

固定学习率使参数在最小值附近持续震荡，训练后期难以细化。Step、Cosine 或 Plateau 调度的作用，是逐步减小有效步长以换取更精细的收敛。

---

## 四、最佳实践

| 场景 | 推荐起点 | 关键理由 |
|---|---|---|
| LLM 预训练 | AdamW + Cosine LR + Warmup + `β2=0.95` | 自适应尺度、解耦衰减、稳定早期训练 |
| CV / CNN | SGD + `momentum=0.9` + Step LR | 最终泛化常更好 |
| 表格数据 | SGD / Adam 均可，但优先评估 XGBoost | 树模型自带 Boosting 优化过程 |

- **Linear Scaling Rule**：`batch_size` 翻倍时，可把峰值学习率近似线性放大 2 倍；超大 batch 仍需重新 Warmup，并用验证集确认稳定性。
- AdamW 常对 bias、LayerNorm / RMSNorm 参数关闭权重衰减，避免破坏偏置和归一化尺度。
- 选型时同时记录训练 loss、验证指标、梯度范数与吞吐量，不要只比较“多少步收敛”。

---

## 五、面试话术（30 秒 + 90 秒）

### 30 秒版

> “BGD 每步用全量数据，稳定但慢；SGD 每步用一个样本，快但震荡；Mini-Batch 用 32～256 个样本，是 GPU 训练标准。Adam 用一阶动量 $m$ 平滑方向、二阶动量 $v$ 自适应缩放学习率，并做偏差修正。AdamW 再把权重衰减从梯度更新中解耦，所以 LLM 常用 AdamW + Warmup + Cosine；CV 中 SGD + Momentum 仍可能泛化更好。”

### 90 秒版

> “三类梯度下降先看梯度估计：BGD 用全量梯度，方差低但单步贵；SGD 用单样本，噪声大但更新快；Mini-Batch 在吞吐与稳定性间折中。Adam 再维护 $m_t=\beta_1m_{t-1}+(1-\beta_1)g_t$ 和 $v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2$，偏差修正后按 $\alpha\hat m_t/(\sqrt{\hat v_t}+\varepsilon)$ 更新，因此每个参数有不同的有效步长。
>
> AdamW 的关键不是‘多一个 L2’，而是额外执行 $-\alpha\lambda\theta$，让衰减不经过二阶动量缩放。LLM 常用 AdamW、`β2=0.95`、前 1%～5% Warmup 再 Cosine 衰减；CV / CNN 则常用 SGD + momentum=0.9 获得更好泛化。Batch 翻倍可先按 linear scaling rule 放大学习率，但最终要用验证集和梯度稳定性校准。”

---

## 六、交叉引用

- **主模块**：[`02-algorithms/optimization/gradient-descent`](../../../../02.cs-foundations/01-algorithms/optimization/gradient-descent/README.md) — 梯度下降的几何直觉与收敛条件
- **兄弟**：[`k-means-convergence`](../k-means-convergence/README.md) / [`peft-lora`](../../../11.ai/peft-lora/README.md) — AdamW 在 LLM 参数高效微调中的应用 / [`llm-alignment`](../../../11.ai/llm-alignment/README.md)
- **反向**：[`02.computer-basics`](../../README.md) — 传统 ML 面试综述 Q3

---

> 📅 2026-08-10 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐ · 梯度下降变体
