<!--
module:
  parent: computer-basics
  slug: algorithms/dimensionality-reduction/pca
  type: article
  category: 主模块子文章
  summary: PCA 主成分分析 + 与 SVD 关系
-->

# PCA 主成分分析

> ⬅️ [返回 02 算法](../../README.md) | [返回 02.computer-basics](../../../README.md)

> **一句话定位**：PCA = **找方差最大的正交方向做降维**，**保留 90%+ 信息用 10% 维度**。1901 年 Karl Pearson 提出，**降维算法鼻祖**。

---

## 🎯 一句话理解

把 N 维数据降到 K 维（K < N），让**投影后方差最大、信息损失最小**。

---

## 📐 算法流程

```text
1. 中心化：X = X - X.mean(axis=0)
2. 协方差矩阵：Σ = X^T X / (n-1)
3. 特征值分解：Σ = V Λ V^T
4. 取 Top-K 特征向量组成投影矩阵 W
5. 降维：X_new = X @ W
```

**数学本质**：找数据**方差最大**的正交方向。

---

## 🛠️ Python 实现

```python
from sklearn.decomposition import PCA
import numpy as np

X = np.random.randn(100, 50)  # 100 个样本 50 维

# 1. sklearn 一行
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X)

# 2. 解释方差比
print(pca.explained_variance_ratio_.sum())  # 保留信息比例
# 输出：0.92

# 3. 手写
def pca(X, k):
    X_centered = X - X.mean(axis=0)
    cov = np.cov(X_centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    # 排序：按特征值降序
    idx = np.argsort(eigenvalues)[::-1]
    top_k = eigenvectors[:, idx[:k]]
    return X_centered @ top_k, top_k
```

---

## 📐 与 SVD 的关系

```text
X (中心化) = U Σ V^T     (SVD)
ΣΣ^T / (n-1) = V Λ V^T    (特征分解)

PCA 的投影矩阵 = V[:, :K]  (SVD 的右奇异向量)
```

**结论**：SVD 是数值稳定的 PCA 实现，**sklearn PCA 内部用 SVD**。

---

## 📊 K 选择：方差贡献率

```python
pca = PCA().fit(X)
cumsum = np.cumsum(pca.explained_variance_ratio_)
# 找方差贡献 > 95% 的最小 K
k = np.argmax(cumsum >= 0.95) + 1
```

**肘部法则**：

```text
累积方差
  │
  │            ┌──── 95%
  │         ┌──┘
  │      ┌──┘
  │   ┌──┘
  │ ┌─┘
  │─┘
  └──────────── K
       ↑ 肘部
```

---

## 🛠️ 4 大应用场景

| 场景 | 用法 | 降维效果 |
|------|------|---------|
| **可视化** | 100 维 → 2 维 | t-SNE 更佳 |
| **去噪** | 保留 Top-K 主成分 | 显著 |
| **特征工程** | 100 维 → 10 维 | 5-10x 训练加速 |
| **压缩** | 图像 256 维 → 50 维 | 5x 压缩率 |

---

## ⚠️ 5 大局限

| 局限 | 原因 | 缓解 |
|------|------|------|
| 仅线性 | 主成分是线性组合 | Kernel PCA |
| 假设高斯分布 | 方差是线性度量 | ICA / t-SNE |
| 方差≠信息 | 类别信息可能丢失 | LDA |
| 对异常值敏感 | 协方差受极值影响 | Robust PCA |
| 难解释 | 主成分无语义 | 因子分析 |

---

## 🔗 兄弟章节

- **本目录**：[t-SNE](../) / [LDA](../) / [Kernel PCA](../)
- **02 同级**：[K-means](../../clustering/k-means/README.md) / [梯度下降](../../optimization/gradient-descent/README.md)
- **AI 应用**：[向量检索](../../../../11.ai/02-technology-stack/vector-search-algorithms/README.md) 顺带提

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ PCA 保留最多信息 | ✅ 仅保留最多方差 |
| ❌ PCA 可视化效果好 | ✅ t-SNE / UMAP 更好 |
| ❌ 降维越多越好 | ✅ K 太小损失信息 |
| ❌ PCA 需要标准化 | ✅ 强烈建议（避免大值特征主导）|

← [返回: 降维算法](../README.md)