<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/01-ml
  type: index-only
  category: AI 基础索引
  summary: 传统机器学习算法——监督学习、无监督学习与强化学习的核心方法与演进脉络。
  depth: ⭐⭐⭐⭐⭐
-->

# 01. 传统机器学习

## 📍 一句话定位

> 经典算法的基座——从监督学习（KNN / 决策树 / SVM）到无监督学习（K-means / PCA），再到强化学习（DQN / PPO / SAC），构建 AI 入门的全景认知。

## 🎯 子模块简介

`01-ml/` 聚焦**深度学习崛起之前的机器学习范式**，覆盖三大类算法与对应的工程场景：

- **监督学习（Supervised Learning）**：KNN、决策树、SVM、朴素贝叶斯、线性 / 逻辑回归——用标注数据学习 X→y 的映射；典型任务为分类（图像识别）与回归（房价预测）。
- **无监督学习（Unsupervised Learning）**：K-means、PCA、高斯混合模型（GMM）——从无标签数据挖掘隐结构；典型任务为聚类（用户分群）与降维（特征压缩）。
- **强化学习（Reinforcement Learning）**：DQN、PPO、SAC、Actor-Critic 家族——智能体通过"试错 + 奖励"与环境交互学习最优策略；典型场景为自动驾驶、游戏 AI、机器人控制。

本节是整个 AI 基础层的"地基"。理解传统 ML 才能真正回答"为什么深度学习在 2012 年后崛起"、"为什么 GPU 改变了 AI 格局"等根本问题。

---

## 🧠 核心原理：三大范式的数学骨架

### 1. 监督学习——条件概率估计

监督学习的本质是从输入 $\mathbf{x} \in \mathbb{R}^d$ 预测输出 $y$，目标是学到映射 $f: \mathcal{X} \rightarrow \mathcal{Y}$，使得经验风险最小化：

$$
\hat{f} = \arg\min_{f \in \mathcal{F}} \frac{1}{n} \sum_{i=1}^{n} L\big(f(\mathbf{x}_i), y_i\big)
$$

其中 $L(\cdot, \cdot)$ 是损失函数（MSE 用于回归、Cross-Entropy 用于分类）。**算法的差异**主要体现在假设空间 $\mathcal{F}$：线性回归是线性函数空间、SVM 是带 margin 的超平面、KNN 是局部插值空间、决策树是分段常数函数。

### 2. 无监督学习——隐结构发现

无监督学习没有标签 $y$，目标是揭示数据的内在结构。两类代表：

- **聚类**（K-means）：最小化类内平方和 $J = \sum_{k=1}^{K} \sum_{\mathbf{x} \in C_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$
- **降维**（PCA）：找到使方差最大的 $k$ 个正交方向，即对协方差矩阵 $\boldsymbol{\Sigma}$ 做特征值分解 $\boldsymbol{\Sigma} = \mathbf{W} \boldsymbol{\Lambda} \mathbf{W}^\top$，保留前 $k$ 个主成分。

### 3. 强化学习——序贯决策

强化学习把决策形式化为马尔可夫决策过程（MDP）$(\mathcal{S}, \mathcal{A}, P, R, \gamma)$，目标是找到策略 $\pi(a|s)$ 最大化长期累积奖励：

$$
G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k}, \quad Q^\pi(s,a) = \mathbb{E}_\pi\left[G_t \mid s_t=s, a_t=a\right]
$$

**DQN** 用神经网络逼近 $Q(s,a;\theta)$；**PPO** 直接优化策略 $\pi_\theta$，用 clipped surrogate objective 限制策略更新幅度：

$$
L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\big(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t\big)\right]
$$

---

## 📜 演进史：从感知机到 PPO 的 70 年

| 时期 | 里程碑 | 关键贡献 |
|------|--------|----------|
| **1943-1958** | McCulloch-Pitts 神经元 → 感知机（Rosenblatt） | 第一个可学习模型，证明"感知"可由算法实现 |
| **1969-1986** | Minsky《Perceptrons》→ 反向传播（Rumelhart） | 寒冬与复苏：BP 算法让多层网络可训练 |
| **1986-1995** | Quinlan ID3/C4.5 → Vapnik SVM | 符号派与统计派的"双轨繁荣" |
| **1995-2006** | Hinton Deep Belief Net → LeNet-5 | 深度学习的雏形，但受限于算力 |
| **2012** | AlexNet（ImageNet）→ GPU 训练 | 深度学习正式"碾压"传统 ML |
| **2013** | DQN（DeepMind）→ Atari 游戏 | 强化学习 + 深度网络解锁高维感知 |
| **2015-2017** | AlphaGo → AlphaGo Zero | 自我对弈超越人类，**RL 不再依赖人类数据** |
| **2017** | PPO（Schulman et al.）→ 成为 RLHF 标配 | 简单、稳定、可大规模部署的策略优化 |
| **2022-2025** | RLHF / DPO 进入 LLM 训练 | 传统 RL 思想成为大模型对齐的核心 |

**设计哲学反思**：从感知机的"线性不可分"局限性（1969 Minsky）→ 核方法 SVM 的"维度上升换可分"（1995）→ 深度网络的"维度下降换表示"（2012）→ 强化学习的"试错换策略"（2017-）。**三条路径都在解决同一个核心问题：泛化能力**。

---

## 🏛️ 三大经典算法实战案例

### 案例 1：KNN + KD-Tree——手写数字识别（MNIST）

- **数据**：60k 训练样本 × 784 维（28×28 灰度图）
- **baseline**：欧氏距离 KNN（k=3），无任何特征工程
- **结果**：准确率约 **97.1%**（对比 LeNet-5 99.3%、ResNet-18 99.7%）
- **价值**：KNN 在小数据上仍可作为"零成本 baseline"，KD-Tree 将搜索从 $O(nd)$ 降到 $O(d \log n)$。

### 案例 2：决策树 / XGBoost——Kaggle Higgs Boson 挑战赛（2014）

- 冠军方案以 **XGBoost**（GBDT 的工程化版本）为核心
- 单模型 AUC > 0.85，远超 SVM（0.78）与神经网络（0.79）
- **意义**：在结构化数据上，**树模型至今仍是 SOTA**（2024-2025 Kaggle 比赛前 10 名中 ~80% 仍含 GBDT 组件）

### 案例 3：DQN + PPO——AlphaGo Zero（DeepMind, Nature 2017）

- 纯强化学习（无人类棋谱）+ 蒙特卡洛树搜索
- 训练 40 天后以 100:0 击败 AlphaGo Master（击败人类冠军的版本）
- **设计哲学**：**Self-play + 奖励稀疏（输赢）+ 大规模算力**——三要素缺一不可。

---

## 💻 代码示例：NumPy 手写 K-means

```python
import numpy as np

def kmeans(X, k=3, max_iter=100, tol=1e-4):
    """极简 K-means 实现——看清聚类本质"""
    n, d = X.shape
    # 1. 随机初始化质心
    centroids = X[np.random.choice(n, k, replace=False)]

    for _ in range(max_iter):
        # 2. 计算每个样本到质心的距离 (n, k)
        dists = np.linalg.norm(X[:, None] - centroids[None, :], axis=2)

        # 3. 分配簇
        labels = np.argmin(dists, axis=1)

        # 4. 更新质心
        new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])

        # 5. 收敛判定
        if np.linalg.norm(new_centroids - centroids) < tol:
            break
        centroids = new_centroids

    return labels, centroids

# 实战：3 类高斯分布聚类
np.random.seed(42)
X = np.vstack([np.random.randn(50, 2) + [0, 0],
               np.random.randn(50, 2) + [5, 5],
               np.random.randn(50, 2) + [0, 5]])
labels, centroids = kmeans(X, k=3)
print(f"聚类完成，质心：\n{centroids}")
```

---

## ⚠️ 常见误区 / 反直觉点（3+）

1. **"KNN 没有训练过程，所以没成本"**——错。训练 = 把所有数据存进内存；推理时间复杂度 $O(nd)$；预测成本远高于神经网络。
2. **"决策树容易过拟合，所以实战不用"**——错。**集成后**（随机森林 / XGBoost）决策树是结构化数据的 SOTA，2025 年 Kaggle 比赛仍在用它。
3. **"强化学习一定能找到最优策略"**——错。奖励函数设计错误会导致**奖励黑客**（reward hacking），如 OpenAI CoastRunners 训练智能体反复撞船刷分而不完成比赛。
4. **"PCA 是降维，所以会丢失信息"**——半错。PCA 是**最优线性降维**（均方误差最小），但非线性结构会被破坏——此时需 t-SNE / UMAP。
5. **"SVM 的核技巧能处理任意非线性"**——半错。核函数选择极端依赖数据，**核函数选错反而不如线性模型**（No Free Lunch 定理）。

---

## 🔗 跨模块反向链

- **同模块相邻**：[02-deep-learning](../02-deep-learning/README.md) — 深度学习框架与训练范式（解决传统 ML 的高维痛点）
- **同模块相邻**：[03-transformer](../03-transformer/README.md) — Transformer 架构核心（MLP/Self-Attention 都是监督学习的延伸）
- **AI 工程实战**：[`09.ai-applications/llm-inference`](../../09.ai-applications/llm-inference/README.md) — LLM 推理优化（K-means 量化聚类在 KV Cache 压缩中的应用）
- **咬文嚼字**：[`12.interview/02.computer-basics/machine-learning`](../../12.interview/02.computer-basics/machine-learning/) — 传统 ML 面试高频题
- **兄弟主题（深度延伸）**：[`08.ai-foundations/01-ml/ml-to-rl`](./ml-to-rl.md) — 监督学习到强化学习的范式跃迁
- **故事叙事**：[`13.story/`](../../13.story/) — "阿明餐厅"系列以餐饮类比讲解 SVM、决策树等算法直觉

---

## 🗂️ 文章清单

| 标题 | 路径 | 状态 | 摘要 |
|------|------|------|------|
| 监督学习 → 强化学习 | [ml-to-rl.md](./ml-to-rl.md) | ✅ 已完成（152 行） | 以自动驾驶为例，梳理监督学习 → 无监督学习 → 强化学习的演进、融合架构与安全探索。 |

> **覆盖说明**：当前 `01-ml/` 仅沉淀 1 篇（ml-to-rl.md），覆盖监督 / 无监督 / 强化学习的演进认知；KNN 与决策树是面试高频算法，建议尽快补齐。

## 🔗 关联主题

- **父模块**：[08.ai-foundations](../README.md) — AI 基础层总索引
- **同模块相邻**：[02-deep-learning](../02-deep-learning/README.md) — 深度学习框架选型与训练范式
- **AI 工程实战**：[`09.ai-applications/llm-inference`](../../09.ai-applications/llm-inference/README.md) — LLM 推理优化实战
- **咬文嚼字**：[`12.interview/02.computer-basics/machine-learning`](../../12.interview/02.computer-basics/machine-learning/) — 传统 ML 面试高频题
- **项目沉淀**：[file-view](https://github.com/wb04307201/file-view) — 传统 ML 工业级应用

## 📚 学习路径

1. **入门**：阅读 [ml-to-rl.md](./ml-to-rl.md)，建立"监督 → 无监督 → 强化"三范式的演进认知
2. **算法深挖**：补充 KNN / 决策树 / SVM 三大经典算法专题（建议先 KNN 原理）
3. **聚类与降维**：补充 K-means / PCA / GMM，对应无监督学习章节
4. **强化学习**：阅读 DQN / PPO / SAC 算法综述，理解 MDP 与策略梯度
5. **面试刷题**：跳转 [12.interview/02.computer-basics/machine-learning](../../12.interview/02.computer-basics/machine-learning/) 巩固核心题
6. **工程落地**：跳转 [09.ai-applications/llm-inference](../../09.ai-applications/llm-inference/) 看工业级推理优化

## 📊 本节统计

- **子目录总数**：1 个（01-ml/）
- **已沉淀文章**：1 篇（ml-to-rl.md）
- **待补占位**：2 篇（KNN 原理 / 决策树剪枝）
- **总行数**（不含 README）：约 152 行
- **最后更新**：2026-09-01

---

> 📅 2026-09-01 · 咬文嚼字 · 传统机器学习 · ⭐⭐⭐（高频面试 + 实战必会）

---

← [返回 08.ai-foundations](../README.md)