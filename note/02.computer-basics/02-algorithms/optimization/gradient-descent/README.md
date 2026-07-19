<!--
module:
  parent: computer-basics
  slug: algorithms/optimization/gradient-descent
  type: article
  category: 主模块子文章
  summary: 梯度下降 4 大变体（BGD/SGD/Mini-batch/Adam）
-->

# 梯度下降（Gradient Descent）

> ⬅️ [返回 02 算法](../../README.md) | [返回 02.computer-basics](../../../README.md)

> **一句话定位**：梯度下降 = **沿负梯度方向迭代更新参数**，**深度学习的优化基石**。BGD / SGD / Mini-Batch / Adam 4 大变体覆盖所有训练场景。

---

## 🎯 一句话理解

目标：最小化损失函数 L(θ)

```
θ_new = θ_old - lr * ∇L(θ_old)
```

**核心**：沿负梯度方向（最陡下降）走一小步。

---

## 📐 4 大变体对比

| 变体 | 每次更新用 | 优点 | 缺点 | 适用 |
|------|----------|------|------|------|
| **BGD** (Batch) | 全量数据 | 稳定 | 慢 / 内存大 | 小数据 |
| **SGD** (Stochastic) | 1 个样本 | 快 / 可在线 | 震荡大 | 大数据 |
| **Mini-Batch** | 32-512 样本 | 平衡 | 仍需调 batch | 主流选择 |
| **Adam** | 自适应 LR | 收敛快 | 调参复杂 | 深度学习默认 |

---

## 🛠️ Python 实现

```python
import torch

# Adam 优化器
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(100):
    for batch in dataloader:
        # 1. 前向
        pred = model(batch.x)
        loss = loss_fn(pred, batch.y)
        # 2. 反向（自动求梯度）
        loss.backward()
        # 3. 更新
        optimizer.step()
        optimizer.zero_grad()
```

---

## 📊 4 大优化器动量对比

```
SGD:        θ ← θ - lr * g
SGD+M:      v ← μ*v + g
            θ ← θ - lr * v
Adam:       m ← β1*m + (1-β1)*g      # 一阶动量
            v ← β2*v + (1-β2)*g²     # 二阶动量
            m̂ = m / (1-β1^t)
            v̂ = v / (1-β2^t)
            θ ← θ - lr * m̂ / (√v̂ + ε)
```

**Adam** = RMSProp + Momentum，是 2014 至今最主流。

---

## 🎯 6 大学习率策略

| 策略 | 公式 | 适用 |
|------|------|------|
| **Constant** | lr = const | 简单场景 |
| **Step Decay** | lr *= 0.1 每 30 epoch | CV |
| **Exponential** | lr *= gamma^epoch | 经典 |
| **Cosine Annealing** | lr = 0.5 * (1 + cos(πt/T)) * lr_0 | 主流 |
| **Warmup + Cosine** | 先 warmup 再 cosine | 训练大模型 |
| **ReduceLROnPlateau** | 验证集不升则降 | 不规则收敛 |

**Warmup + Cosine** 是 LLM 训练标配。

---

## ⚠️ 7 大调参陷阱

| 陷阱 | 现象 | 解决 |
|------|------|------|
| LR 太大 | loss 震荡/NaN | 降 10x |
| LR 太小 | loss 不降 | 增 10x |
| 无 warmup | 早期 loss 爆炸 | 加 5% warmup |
| 无 weight decay | 泛化差 | wd=0.01 |
| 无梯度裁剪 | 训练崩溃 | clip=1.0 |
| 局部最优 | 早停假象 | 调 LR / 换 optimizer |
| 鞍点 | 卡住 | Adam 自适应 |

---

## 🔗 兄弟章节

- **本目录**：[Newton 法](../) / [LBFGS](../)
- **02 同级**：[K-means](../../clustering/k-means/README.md) / [PCA](../../dimensionality-reduction/pca/README.md)
- **AI 训练**：[SFT 训练](../../../../11.ai/03-engineering/llm-alignment/01-sft.md) / [RLHF PPO](../../../../11.ai/03-engineering/llm-alignment/02-rlhf.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ Adam 永远优于 SGD | ✅ CV 任务 SGD+动量仍强 |
| ❌ LR 越小越好 | ✅ 过小卡在局部最优 |
| ❌ 收敛 = 全局最优 | ✅ 仅保证局部最优 |
| ❌ 凸函数才有唯一最优 | ✅ 非凸问题 Adam 表现更好 |

← [返回: 优化算法](../README.md)