<!--
question:
  id: 02.computer-basics-pca-math
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 数学推导
  tags: [ML, PCA, SVD, 特征值分解, 降维]
-->

# PCA 数学本质：为什么是协方差矩阵的特征向量？

> 一句话定位：PCA 是**找方差最大方向的线性投影**，数学上等价于**协方差矩阵的特征向量**。

> **经典 ML 面试题（中频，深度学习岗必问）**。考察的不是"PCA 是什么"，而是 **数学推导**（为什么特征向量是方差最大方向）+ **SVD 等价性**（sklearn 为什么不用 eig） + **5 大实战陷阱**（标准化 / 监督 / 非线性 / K 选择 / 浮点误差）。

---

## 引子：10000 维人脸特征 → 100 维，怎么选？

```text
🎯 面试官：人脸识别数据集，每张人脸提取 10000 维特征
（HOG / SIFT / 深度特征）。要塞进模型，但 10000 维太高，
过拟合 + 慢。你怎么降到 100 维？凭什么选这 100 维？
```

普通答案："PCA 降维"。但面试官追问：

- ❓ "为什么 PCA 选出的方向是**方差最大**的？数学怎么证？"
- ❓ "PCA 内部是算**协方差矩阵**还是直接算 **SVD**？两者什么关系？"
- ❓ "PCA 之前**不标准化**行不行？"
- ❓ "累积方差贡献率 ≥ 95% 一定最优吗？"
- ❓ "环形分布数据 PCA 还管用吗？"

这一题**深度学习岗必问**（尤其涉及 Embedding 降维 / 推荐系统 / 表征学习），答不出数学推导直接送命。

---

## 一、核心原理

### 1.1 为什么特征向量是方差最大方向？数学推导

设中心化数据 $X \in \mathbb{R}^{n \times d}$（均值为 0），找单位向量 $v$ 使投影后方差最大：

**方差定义**：投影后方差 $= v^T \Sigma v$，其中 $\Sigma = X^T X / (n-1)$ 是**协方差矩阵**。

**优化问题**：$\max_{v} v^T \Sigma v$ s.t. $v^T v = 1$

**拉格朗日乘子**：$\mathcal{L}(v, \lambda) = v^T \Sigma v - \lambda(v^T v - 1)$

$$\frac{\partial \mathcal{L}}{\partial v} = 2\Sigma v - 2\lambda v = 0 \implies \boxed{\Sigma v = \lambda v}$$

**结论**：$v$ 必是 $\Sigma$ 的特征向量，且 $v^T \Sigma v = \lambda$。**最大方差方向 = 协方差矩阵最大特征值对应的特征向量**。多个方向同理（正交 + 方差最大）→ Top-K 特征向量。

### 1.2 协方差矩阵与特征值分解

$$\Sigma = \frac{X^T X}{n-1} = V \Lambda V^T, \quad \Lambda = \text{diag}(\lambda_1, ..., \lambda_d)$$

- $V$：**正交**特征向量矩阵（$V^T V = I$），$\lambda_1 \geq \lambda_2 \geq ...$
- **投影矩阵** $W = [v_1, ..., v_K]$，降维结果 $X_{\text{new}} = X W \in \mathbb{R}^{n \times K}$

### 1.3 与 SVD 的等价关系

对 $X$ 做 SVD：$X = U S V^T$（$S$ 是奇异值对角阵）。

代入协方差矩阵：

$$\Sigma = \frac{X^T X}{n-1} = \frac{V S^2 V^T}{n-1}$$

**关键结论**：**协方差矩阵的特征向量 = SVD 的右奇异向量 $V$**，且 $\lambda_i = \sigma_i^2 / (n-1)$。PCA 投影矩阵 = $V$ 的 Top-K 列。

### 1.4 为什么 sklearn 内部用 SVD 而不是 eig？

| 维度 | `np.linalg.eig` | `np.linalg.svd` |
|------|-----------------|-----------------|
| 计算对象 | 协方差矩阵 $\Sigma = X^T X / (n-1)$ | 直接对 $X$ 分解 |
| 复杂度 | $O(d^3)$ | $O(\min(n,d)^2 \cdot \max(n,d))$ |
| 数值稳定性 | **差**（$X^T X$ 放大浮点误差） | **好** |
| $d=10000$ | 协方差矩阵内存爆炸 | `randomized_svd`（Halko 2009）只算 Top-K |

sklearn 默认 `svd_solver='auto'` → 高维走 `randomized` 路径，**数值稳定 + 内存友好**。

---

## 二、代码示例

### 2.1 NumPy 手写 PCA（25 行）

```python
import numpy as np

def pca_numpy(X, k):
    X_centered = X - X.mean(axis=0)                        # 1. 中心化
    n = X_centered.shape[0]
    Sigma = X_centered.T @ X_centered / (n - 1)            # 2. 协方差矩阵
    eig_vals, eig_vecs = np.linalg.eigh(Sigma)             # 3. 特征值分解
    idx = np.argsort(eig_vals)[::-1]
    W = eig_vecs[:, idx][:, :k]                            # 4. 投影矩阵 d×k
    X_new = X_centered @ W                                 # 5. 降维 n×k
    X_rec = X_new @ W.T + X.mean(axis=0)                   # 6. 反投影重建
    return X_new, X_rec, eig_vals[idx][:k]

X = np.random.randn(100, 50)
X_new, X_rec, eig = pca_numpy(X, k=10)
print(f"{X.shape} -> {X_new.shape}, 重建 MSE = {((X - X_rec)**2).mean():.4f}")
```

### 2.2 sklearn 对比验证

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

X_std = StandardScaler().fit_transform(X)   # 关键：先标准化
pca = PCA(n_components=10, svd_solver='randomized', random_state=42).fit(X_std)
print(f"累积方差 = {pca.explained_variance_ratio_.sum():.4f}")
# 与手写 PCA 余弦相似度接近 1.0（符号可能相反，特征向量符号任意）
```

### 2.3 K 选择（肘部法则）

```python
errors = [((X_std - pca_numpy(X_std, k)[1]) ** 2).mean() for k in range(1, 51)]
# 画 errors vs k，找拐点 —— 加维度收益变小的临界 K
```

---

## 三、常见陷阱

### 陷阱 1：PCA 前必须标准化（否则量纲大的特征主导）

- **真相**：PCA 是方差最大化，**量纲大的特征天然占优**。年龄（0-100）和收入（0-10^6）混在一起 → 收入主导第一个主成分。
- **正例**：先 `StandardScaler`，让所有特征**方差 = 1**。

### 陷阱 2：PCA 是无监督，不能用 y 标签信息

- **真相**：PCA 完全忽略标签 $y$，只保留**方差最大方向**。但**类别可分方向**未必是方差最大方向！
- **对比 LDA**：用 $y$ 信息，找**类间方差最大 / 类内方差最小**方向（监督降维）。人脸识别 100 类场景 LDA 优于 PCA。

### 陷阱 3：PCA 是线性降维，对环形 / 螺旋分布失效

```python
from sklearn.datasets import make_circles
from sklearn.decomposition import KernelPCA
X, _ = make_circles(n_samples=500, noise=0.05, factor=0.3)
# KernelPCA + RBF kernel 能展开同心圆；线性 PCA 完全失效
KernelPCA(n_components=2, kernel='rbf', gamma=0.5).fit(X)
```

### 陷阱 4：累积方差 ≥ 95% 不一定最优

- **真相**：95% 是**经验值**，**下游任务**才是终极指标。高维可视化 → `PCA→50 维` → `t-SNE→2 维`（直接 t-SNE 太慢且破坏全局结构）。盲目追求 99% 方差 → 维度没降多少，模型照样过拟合。

### 陷阱 5：explained_variance_ratio_ 求和有浮点误差

```python
pca = PCA(n_components=50).fit(X_std)
print(pca.explained_variance_ratio_.sum())  # 0.9999999... 而非 1.0
```

- **真相**：SVD 数值计算有 $\sim 10^{-15}$ 浮点误差，求和时累加放大。用 `np.isclose(sum, 1.0, atol=1e-6)` 比较，**不要 `== 1.0`**。

### 陷阱 6（隐藏坑）：IncrementalPCA 与 PCA 略有不同

- `PCA` 一次性加载全部数据；`IncrementalPCA` 支持**流式 batch 训练**（大数据无法全载入内存）。`IncrementalPCA` 用增量 SVD（非 `randomized_svd`），结果**有微小差异**但数学性质一致。

---

## 四、最佳实践

| 场景 | 推荐做法 |
|------|---------|
| 标准流程 | `StandardScaler` → `PCA(n_components=0.95)` |
| 超高维（d > 10000） | `PCA(svd_solver='randomized')`，内存友好 |
| 流式 / 大数据 | `IncrementalPCA(batch_size=1000)` |
| 非线性结构 | `KernelPCA(kernel='rbf', gamma='scale')` |
| 高维可视化 | `PCA(50) → t-SNE(2)` |
| 异常值敏感 | 剔除异常值 or 用 **Robust PCA**（RPCA） |
| 监督降维 | `LinearDiscriminantAnalysis`（LDA）代替 PCA |

**调参重点**：`n_components='mle'`（Minka 2000 最大似然自动选 K）；`whiten=True` 白化让 PC 方差 = 1（对 SVM / KNN 有帮助）。

---

## 五、面试话术

### 30 秒版本

> "PCA 找**方差最大**的正交方向做投影，数学上等价于**协方差矩阵的特征向量**。流程：中心化 → 协方差 → 特征值分解 → Top-K 特征向量 = 投影矩阵。"

### 90 秒版本

> "核心数学：中心化后协方差矩阵 $\Sigma = X^T X / (n-1)$，特征值分解 $\Sigma = V \Lambda V^T$。**Top-K 特征向量**就是 PCA 投影方向。**与 SVD 关系**：$X = U S V^T$，PCA 投影矩阵 = $V$ 的 Top-K 列，且 $\lambda_i = \sigma_i^2 / (n-1)$。sklearn 内部用 `randomized_svd` 而非 `eig`，因为**数值更稳定 + 高维更高效**（$d=10000$ 时协方差矩阵内存爆炸）。
>
> **K 选择**：累积方差 ≥ 95% 是经验值，**要看下游任务**。**标准化前置**：必须 `StandardScaler`，否则量纲大的特征主导。**局限**：仅线性，环形分布失效 → 用 **KernelPCA**；忽略标签 → 监督场景用 **LDA**。Embedding 场景常见：BERT 768 维 → PCA 128 维做 ANN 检索，比原始向量快 5-10x。"

---

## 六、交叉引用

- **同栏目**：[`k-means-convergence`](../k-means-convergence/README.md) — K-means 与 PCA 是**两种范式**（聚类 vs 投影）
- **主模块**：[`02-algorithms/dimensionality-reduction/pca`](../../../../02.cs-foundations/01-algorithms/dimensionality-reduction/pca/README.md) — PCA 完整原理 + 实战代码
- **11.ai 关联**：[`embedding-vs-vectorization`](../../../../08.ai-foundations/05-tokenization-embedding/embedding.md) — BERT/LLM Embedding 高维（768-4096 维），实战中常用 PCA→128 维再入库做 ANN 检索
- **反向链接**：[`02.computer-basics`](../../README.md) — 计算机基础咬文嚼字主目录

---

> 📅 2026-08-10 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐⭐