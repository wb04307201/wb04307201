<!--
module:
  parent: computer-basics
  slug: algorithms/clustering/k-means
  type: article
  category: 主模块子文章
  summary: K-means 聚类算法 + K-means++ 改进
-->

# K-means 聚类算法

> ⬅️ [返回 02 算法](../../README.md) | [返回 02.computer-basics](../../../README.md)

> **一句话定位**：K-means = **基于距离的聚类，迭代分配质心 → 重新聚类**。1967 年 Lloyd 提出，**最经典的无监督学习算法**，是 GMM / DBSCAN 等高级算法的基石。

---

## 🎯 一句话理解

把 N 个样本分成 K 类，让**类内距离最小、类间距离最大**。流程：

```
1. 随机选 K 个点作为初始质心
2. 每个样本分配到最近的质心（类）
3. 重新计算每个类的质心（均值）
4. 重复 2-3，直到质心不再变化
```

---

## 📐 目标函数

$$J = \sum_{i=1}^{K} \sum_{x \in C_i} ||x - \mu_i||^2$$

最小化**类内平方和**（WCSS, Within-Cluster Sum of Squares）。

---

## 🛠️ Python 实现

```python
import numpy as np
from sklearn.cluster import KMeans

# 1. sklearn 一行调用
X = np.random.randn(300, 2)  # 300 个 2D 样本
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)
centers = kmeans.cluster_centers_

# 2. 手写实现（20 行）
def kmeans(X, k, max_iter=300):
    n = X.shape[0]
    centroids = X[np.random.choice(n, k, replace=False)]
    for _ in range(max_iter):
        # Step 1: 分配
        distances = np.linalg.norm(X[:, None] - centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        # Step 2: 更新
        new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids
    return labels, centroids
```

---

## 📊 9 大变体

| 变体 | 改进 | 适用 |
|------|------|------|
| **K-means++** | 智能选初始质心 | 默认首选 |
| **Mini-Batch K-means** | 抽样批量更新 | 大数据（>10万）|
| **Bisecting K-means** | 自顶向下分裂 | 层次聚类 |
| **X-means** | 自动选 K | 不知道 K 时 |
| **K-medoids** | 中心用真实样本 | 噪声数据 |
| **Fuzzy C-means** | 软分配 | 重叠聚类 |
| **Spherical K-means** | 余弦距离 | 文本聚类 |
| **K-modes** | 分类数据 | 离散特征 |
| **K-prototypes** | 混合数据 | 数值+分类 |

**K-means++** 是工业默认选择。

---

## 📈 K 选择：肘部法则

```
WCSS
  │
  │╲
  │  ╲___
  │      ╲___
  │          ╲____
  │               ╲________
  └──────────────────── K
       ↑ 肘部（K=4）
```

**实操**：

```python
wcss = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)
plt.plot(range(1, 11), wcss, 'bx-')
plt.xlabel('K'); plt.ylabel('WCSS')
```

---

## ⚠️ 5 大局限

| 局限 | 原因 | 缓解 |
|------|------|------|
| 需预设 K | 算法无自动 K 选择 | 肘部法则 / 轮廓系数 |
| 局部最优 | 初始质心敏感 | K-means++ + n_init=10 |
| 仅凸形簇 | 距离度量限制 | DBSCAN / 谱聚类 |
| 噪声敏感 | 异常值拉偏质心 | K-medoids |
| 特征尺度敏感 | 距离受量纲影响 | StandardScaler 归一化 |

---

## 🔗 兄弟章节

- **本目录**：[K-medoids](../) / [EM 算法](../) / [DBSCAN](../)
- **02 同级**：[梯度下降](../../optimization/gradient-descent/README.md) / [PCA](../../dimensionality-reduction/pca/README.md)
- **13.split-hairs**：K-means 面试

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ K-means 一定收敛到全局最优 | ✅ 只能保证局部最优 |
| ❌ K 越大越好 | ✅ 类太多反而过拟合 |
| ❌ 距离只能用欧氏距离 | ✅ 也可曼哈顿 / 余弦 |
| ❌ K-means 可处理大数据 | ✅ 用 Mini-Batch K-means |

← [返回: 聚类算法](../README.md)