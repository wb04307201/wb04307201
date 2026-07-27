<!--
module:
  parent: computer-basics/algorithms
  slug: computer-basics/algorithms/clustering
  type: article
  category: 主模块子文章
  summary: 聚类算法——将数据自动分组的无监督学习方法，覆盖 K-Means / DBSCAN / 层次聚类 / GMM 的原理、实现与选型
-->

# 聚类算法

> ⬅️ [返回: 算法概述](../README.md)

> **一句话定位**：聚类（Clustering）是无监督学习的核心任务——在没有标签的情况下，自动将数据分成若干组，使组内相似、组间差异大。本文覆盖 4 大经典算法的原理、代码实现、边界分析与选型指南。

---

## 🎯 学习目标

- 理解聚类的核心思想：组内相似度高、组间相似度低
- 掌握 K-Means / DBSCAN / 层次聚类 / GMM 4 大算法的原理与实现
- 学会用肘部法则和轮廓系数确定最佳簇数
- 能分析边界情况（空输入、噪声、高维数据）
- 了解多语言实现差异（Python / Java）

---

## 📚 核心概念

### 什么是聚类？

```text
输入：n 个数据点 {x₁, x₂, ..., xₙ}（无标签）
输出：k 个簇 {C₁, C₂, ..., Cₖ}，使得：
  - 同一簇内的点相似度高
  - 不同簇的点相似度低

相似度度量：
  - 欧氏距离：d(x, y) = √Σ(xᵢ - yᵢ)²     ← 最常用
  - 曼哈顿距离：d(x, y) = Σ|xᵢ - yᵢ|
  - 余弦相似度：cos(θ) = (x·y) / (||x|| × ||y||)  ← 文本/高维
```

### 聚类 vs 分类

| 维度 | 聚类（无监督） | 分类（有监督） |
|------|-------------|-------------|
| 标签 | 无标签 | 有标签 |
| 目标 | 发现数据内在结构 | 学习决策边界 |
| 评估 | 轮廓系数 / 肘部法则 | 准确率 / F1 |
| 典型算法 | K-Means / DBSCAN | SVM / 决策树 |

---

## 🧠 4 大算法详解

### 1. K-Means（K 均值）

**核心思想**：迭代优化——分配点到最近中心，重新计算中心。

```text
算法流程：
1. 随机选择 k 个初始中心点 {μ₁, μ₂, ..., μₖ}
2. 重复直到收敛：
   a. 分配：每个点分配到最近的中心
      Cᵢ = {x : ||x - μᵢ|| ≤ ||x - μⱼ||, ∀j}
   b. 更新：重新计算每个簇的中心
      μᵢ = (1/|Cᵢ|) × Σx, x ∈ Cᵢ
3. 返回簇分配 {C₁, C₂, ..., Cₖ}

时间复杂度：O(n · k · t · d)
  n = 点数, k = 簇数, t = 迭代次数, d = 维度
空间复杂度：O(n · d + k · d)
```

**流程图**：

```text
┌─────────────────────────────────────────────────────┐
│                    K-Means 流程                       │
│                                                       │
│  输入: n 个数据点 + k 值                               │
│       ↓                                               │
│  ┌─────────────┐                                      │
│  │ 随机初始化   │ ← k 个中心点                          │
│  │ 中心点       │                                      │
│  └──────┬──────┘                                      │
│         ↓                                             │
│  ┌─────────────┐                                      │
│  │ 分配阶段     │ ← 每个点归到最近中心                    │
│  │ (Assignment) │                                      │
│  └──────┬──────┘                                      │
│         ↓                                             │
│  ┌─────────────┐                                      │
│  │ 更新阶段     │ ← 重新计算 k 个中心                    │
│  │  (Update)    │                                      │
│  └──────┬──────┘                                      │
│         ↓                                             │
│  ┌─────────────┐     否                               │
│  │ 中心点变化?  │─────→ 回到分配阶段                     │
│  └──────┬──────┘                                      │
│         │ 是                                          │
│         ↓                                             │
│  ┌─────────────┐                                      │
│  │ 收敛，输出   │                                      │
│  │ 簇分配结果   │                                      │
│  └─────────────┘                                      │
└─────────────────────────────────────────────────────┘
```

**Python 实现**：

```python
import numpy as np

def kmeans(X, k, max_iters=100, tol=1e-4):
    """
    K-Means 聚类
    
    Args:
        X: 数据矩阵 (n_samples, n_features)
        k: 簇数
        max_iters: 最大迭代次数
        tol: 收敛阈值（中心点移动距离）
    
    Returns:
        labels: 每个点的簇标签 (n_samples,)
        centers: 最终中心点 (k, n_features)
    """
    n_samples, n_features = X.shape
    
    # Step 1: 随机初始化中心点
    indices = np.random.choice(n_samples, k, replace=False)
    centers = X[indices].copy()
    
    for iteration in range(max_iters):
        # Step 2a: 分配阶段 - 计算每个点到所有中心的距离
        # distances shape: (n_samples, k)
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        labels = np.argmin(distances, axis=1)
        
        # Step 2b: 更新阶段 - 重新计算中心点
        new_centers = np.zeros_like(centers)
        for i in range(k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                new_centers[i] = cluster_points.mean(axis=0)
            else:
                # 边界情况：空簇 → 重新随机初始化
                new_centers[i] = X[np.random.choice(n_samples)]
        
        # Step 3: 检查收敛
        shift = np.linalg.norm(new_centers - centers)
        centers = new_centers
        
        if shift < tol:
            print(f"收敛于第 {iteration + 1} 次迭代")
            break
    
    return labels, centers

# 使用示例
X = np.array([[1, 2], [1, 4], [1, 0],
              [10, 2], [10, 4], [10, 0]])
labels, centers = kmeans(X, k=2)
print(f"簇标签: {labels}")     # [0 0 0 1 1 1]
print(f"中心点: {centers}")    # [[1, 2], [10, 2]]
```

**Java 实现**：

```java
public class KMeans {
    
    public static int[] cluster(double[][] data, int k, int maxIters) {
        int n = data.length;
        int d = data[0].length;
        double[][] centers = new double[k][d];
        int[] labels = new int[n];
        
        // 随机初始化中心点
        boolean[] used = new boolean[n];
        for (int i = 0; i < k; i++) {
            int idx;
            do {
                idx = (int)(Math.random() * n);
            } while (used[idx]);
            used[idx] = true;
            System.arraycopy(data[idx], 0, centers[i], 0, d);
        }
        
        for (int iter = 0; iter < maxIters; iter++) {
            // 分配阶段
            for (int i = 0; i < n; i++) {
                double minDist = Double.MAX_VALUE;
                for (int j = 0; j < k; j++) {
                    double dist = euclidean(data[i], centers[j]);
                    if (dist < minDist) {
                        minDist = dist;
                        labels[i] = j;
                    }
                }
            }
            
            // 更新阶段
            double[][] newCenters = new double[k][d];
            int[] counts = new int[k];
            for (int i = 0; i < n; i++) {
                int label = labels[i];
                counts[label]++;
                for (int j = 0; j < d; j++) {
                    newCenters[label][j] += data[i][j];
                }
            }
            for (int i = 0; i < k; i++) {
                if (counts[i] > 0) {
                    for (int j = 0; j < d; j++) {
                        newCenters[i][j] /= counts[i];
                    }
                } else {
                    // 空簇：重新随机初始化
                    int idx = (int)(Math.random() * n);
                    System.arraycopy(data[idx], 0, newCenters[i], 0, d);
                }
            }
            
            // 检查收敛
            double shift = 0;
            for (int i = 0; i < k; i++) {
                shift += euclidean(centers[i], newCenters[i]);
            }
            centers = newCenters;
            if (shift < 1e-4) break;
        }
        
        return labels;
    }
    
    private static double euclidean(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += (a[i] - b[i]) * (a[i] - b[i]);
        }
        return Math.sqrt(sum);
    }
}
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 简单高效，时间复杂度 O(nkt) | 只能发现球形簇 |
| 可解释性强 | 对初始中心敏感（可能陷入局部最优） |
| 适合大数据集 | 需要预先指定 k |
| 保证收敛 | 对噪声和离群点敏感 |

---

### 2. DBSCAN（基于密度的聚类）

**核心思想**：找到密度相连的区域——核心点、边界点、噪声点。

```text
参数：
  ε (eps): 邻域半径
  MinPts: 邻域内最少点数

点的分类：
  核心点：ε 邻域内 ≥ MinPts 个点
  边界点：ε 邻域内 < MinPts 个点，但在某核心点的 ε 邻域内
  噪声点：既不是核心点，也不是边界点

算法流程：
1. 标记所有点为未访问
2. 遍历每个未访问点 p：
   a. 标记 p 为已访问
   b. 计算 p 的 ε 邻域 N(p)
   c. 如果 |N(p)| < MinPts → 标记为噪声（可能后续被归入某簇）
   d. 否则 → 创建新簇，从 p 出发做密度可达扩展：
      - 对 N(p) 中每个未访问点 q：
        - 标记 q 为已访问
        - 计算 N(q)
        - 如果 |N(q)| ≥ MinPts → 将 N(q) 加入待扩展集合
        - 将 q 加入当前簇
```

**Python 实现**：

```python
import numpy as np
from collections import deque

def dbscan(X, eps, min_pts):
    """
    DBSCAN 聚类
    
    Args:
        X: 数据矩阵 (n_samples, n_features)
        eps: 邻域半径
        min_pts: 邻域内最少点数
    
    Returns:
        labels: 簇标签 (-1 表示噪声)
    """
    n = len(X)
    labels = [-2] * n  # -2 = 未访问, -1 = 噪声, 0+ = 簇 ID
    cluster_id = 0
    
    for i in range(n):
        if labels[i] != -2:
            continue
        
        # 计算 ε 邻域
        neighbors = region_query(X, i, eps)
        
        if len(neighbors) < min_pts:
            labels[i] = -1  # 噪声
        else:
            # 创建新簇
            expand_cluster(X, labels, i, neighbors, cluster_id, eps, min_pts)
            cluster_id += 1
    
    return labels

def region_query(X, point_idx, eps):
    """返回 point_idx 的 ε 邻域内所有点的索引"""
    neighbors = []
    for i in range(len(X)):
        if np.linalg.norm(X[point_idx] - X[i]) <= eps:
            neighbors.append(i)
    return neighbors

def expand_cluster(X, labels, point_idx, neighbors, cluster_id, eps, min_pts):
    """从核心点出发，密度可达扩展"""
    labels[point_idx] = cluster_id
    queue = deque(neighbors)
    
    while queue:
        q = queue.popleft()
        
        if labels[q] == -1:
            # 噪声点变为边界点
            labels[q] = cluster_id
        
        if labels[q] != -2:
            continue
        
        labels[q] = cluster_id
        q_neighbors = region_query(X, q, eps)
        
        if len(q_neighbors) >= min_pts:
            # q 是核心点，继续扩展
            queue.extend(q_neighbors)

# 使用示例
X = np.array([[1, 1], [1.1, 1.2], [0.9, 0.9],   # 簇 0
              [5, 5], [5.1, 5.2], [4.9, 4.8],   # 簇 1
              [100, 100]])                         # 噪声
labels = dbscan(X, eps=1.0, min_pts=3)
print(f"簇标签: {labels}")  # [0, 0, 0, 1, 1, 1, -1]
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 可发现任意形状的簇 | 对参数 ε 和 MinPts 敏感 |
| 自动识别噪声点 | 不适合密度差异大的数据集 |
| 不需要预先指定簇数 | 高维数据效果差（维度灾难） |
| 只需 2 个参数 | 时间复杂度 O(n²)，大数据集慢 |

---

### 3. 层次聚类（Hierarchical Clustering）

**核心思想**：构建一棵簇的树状图（Dendrogram），自底向上合并或自顶向下分裂。

```text
凝聚式（Agglomerative，更常用）：
1. 每个点初始化为一个簇
2. 重复直到只剩 1 个簇：
   a. 找到距离最近的两个簇
   b. 合并这两个簇

簇间距离度量（Linkage）：
  - 单链接（Single）：两簇最近点的距离 → 链式效应
  - 全链接（Complete）：两簇最远点的距离 → 紧凑簇
  - 平均链接（Average）：两簇所有点对的平均距离 ← 最常用
  - Ward 链接：合并后方差增加最小的两个簇
```

**Python 实现**：

```python
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist

def hierarchical_clustering(X, n_clusters=2, method='average'):
    """
    层次聚类
    
    Args:
        X: 数据矩阵 (n_samples, n_features)
        n_clusters: 目标簇数
        method: 链接方法 ('single', 'complete', 'average', 'ward')
    
    Returns:
        labels: 簇标签
        Z: 连接矩阵（用于画树状图）
    """
    # 计算距离矩阵
    distances = pdist(X, metric='euclidean')
    
    # 构建层次聚类树
    Z = linkage(distances, method=method)
    
    # 切割树状图得到簇标签
    labels = fcluster(Z, n_clusters, criterion='maxclust')
    
    return labels, Z

# 使用示例
X = np.array([[1, 1], [1.5, 1.5], [5, 5], [5.5, 5.5]])
labels, Z = hierarchical_clustering(X, n_clusters=2)
print(f"簇标签: {labels}")  # [1, 1, 2, 2]

# 画树状图
import matplotlib.pyplot as plt
dendrogram(Z)
plt.show()
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 不需要指定簇数 | 时间复杂度 O(n³)，空间 O(n²) |
| 可发现任意形状 | 一旦合并/分裂不可回退 |
| 树状图直观 | 大数据集不适用（> 10K 点） |
| 提供多粒度视图 | 对噪声敏感 |

---

### 4. 高斯混合模型（GMM）

**核心思想**：假设数据由多个高斯分布混合生成，用 EM 算法估计参数。

```text
模型：
  P(x) = Σₖ πₖ · N(x | μₖ, Σₖ)
  
  其中：
    πₖ = 混合权重（第 k 个高斯的占比），Σπₖ = 1
    μₖ = 第 k 个高斯的均值
    Σₖ = 第 k 个高斯的协方差矩阵

EM 算法：
  E 步：计算每个点属于每个高斯的后验概率
    γ(zₙₖ) = πₖ · N(xₙ | μₖ, Σₖ) / Σⱼ πⱼ · N(xₙ | μⱼ, Σⱼ)
  
  M 步：更新参数
    Nₖ = Σₙ γ(zₙₖ)
    μₖ = (1/Nₖ) Σₙ γ(zₙₖ) · xₙ
    Σₖ = (1/Nₖ) Σₙ γ(zₙₖ) · (xₙ - μₖ)(xₙ - μₖ)ᵀ
    πₖ = Nₖ / N
```

**Python 实现**：

```python
from sklearn.mixture import GaussianMixture
import numpy as np

# 使用 sklearn
X = np.array([[1, 1], [1.5, 1.5], [5, 5], [5.5, 5.5]])

gmm = GaussianMixture(n_components=2, random_state=42)
labels = gmm.fit_predict(X)
print(f"簇标签: {labels}")  # [0, 0, 1, 1]

# 概率分配（软聚类）
probs = gmm.predict_proba(X)
print(f"概率分配:\n{probs}")
# [[0.99 0.01]
#  [0.99 0.01]
#  [0.01 0.99]
#  [0.01 0.99]]

# BIC 用于选择最佳簇数
bic_scores = []
for k in range(1, 6):
    gmm = GaussianMixture(n_components=k, random_state=42)
    gmm.fit(X)
    bic_scores.append(gmm.bic(X))
best_k = np.argmin(bic_scores) + 1
print(f"最佳簇数 (BIC): {best_k}")
```

**优缺点**：

| 优点 | 缺点 |
|------|------|
| 软聚类（概率分配） | 对初始化敏感 |
| 可发现椭球形簇 | 可能陷入局部最优 |
| 可用 BIC/AIC 选簇数 | 计算复杂度高 |
| 比 K-Means 更灵活 | 高维数据协方差矩阵估计困难 |

---

## 📊 4 大算法对比表

| 算法 | 簇形状 | 时间复杂度 | 空间复杂度 | 需要指定 k | 处理噪声 | 适用场景 |
|------|--------|-----------|-----------|-----------|---------|---------|
| **K-Means** | 球形 | O(nkt) | O(n+k) | ✅ 需要 | ❌ 不处理 | 大数据集，球形簇 |
| **DBSCAN** | 任意 | O(n²) | O(n) | ❌ 不需要 | ✅ 自动识别 | 噪声数据，任意形状 |
| **层次聚类** | 任意 | O(n³) | O(n²) | ❌ 不需要 | ❌ 不处理 | 小数据集，需可视化 |
| **GMM** | 椭球形 | O(nkt) | O(nk+k·d²) | ✅ 需要 | ⚠️ 部分 | 需要概率分配 |

---

## 📐 如何确定最佳簇数？

### 1. 肘部法则（Elbow Method）

```python
import matplotlib.pyplot as plt

def find_best_k_elbow(X, max_k=10):
    """肘部法则：画 SSE vs k 曲线，选拐点"""
    sse = []
    for k in range(1, max_k + 1):
        labels, centers = kmeans(X, k)
        # 计算 SSE（Sum of Squared Errors）
        sse_k = sum(
            np.sum((X[labels == i] - centers[i]) ** 2)
            for i in range(k)
        )
        sse.append(sse_k)
    
    plt.plot(range(1, max_k + 1), sse, 'bo-')
    plt.xlabel('k')
    plt.ylabel('SSE')
    plt.title('Elbow Method')
    plt.show()
    
    return sse

# 拐点 = SSE 下降速度突然变缓的 k 值
```

```text
SSE 曲线示意：

SSE
 │
 │●
 │
 │ ●
 │
 │  ●
 │
 │   ●
 │    ● ● ● ●
 └──────────── k
       ↑
     拐点（最佳 k）
```

### 2. 轮廓系数（Silhouette Score）

```python
from sklearn.metrics import silhouette_score

def find_best_k_silhouette(X, max_k=10):
    """轮廓系数：范围 [-1, 1]，越大越好"""
    scores = []
    for k in range(2, max_k + 1):
        labels, _ = kmeans(X, k)
        score = silhouette_score(X, labels)
        scores.append(score)
    
    best_k = np.argmax(scores) + 2
    print(f"最佳簇数: {best_k}, 轮廓系数: {max(scores):.3f}")
    return best_k, scores
```

```text
轮廓系数含义：

对于点 i：
  a(i) = i 到同簇其他点的平均距离（簇内紧密度）
  b(i) = i 到最近簇所有点的平均距离（簇间分离度）
  
  s(i) = (b(i) - a(i)) / max(a(i), b(i))

  s(i) ∈ [-1, 1]：
    s(i) ≈ 1 → 聚类正确
    s(i) ≈ 0 → 在簇边界上
    s(i) ≈ -1 → 可能聚错了
```

### 3. Gap Statistic

```text
思想：比较实际 SSE 与均匀分布的参考 SSE

Gap(k) = E[log(SSE_ref(k))] - log(SSE(k))

选择最大的 Gap(k) 对应的 k
```

---

## 📊 评估指标

| 指标 | 公式/范围 | 含义 | 适用场景 |
|------|---------|------|---------|
| **轮廓系数** | [-1, 1]，越大越好 | 簇内紧密 + 簇间分离 | 通用，最常用 |
| **Davies-Bouldin** | [0, +∞)，越小越好 | 簇间相似度 | 球形簇 |
| **Calinski-Harabasz** | [0, +∞)，越大越好 | 簇间方差 / 簇内方差 | 球形簇 |
| **SSE** | [0, +∞)，越小越好 | 误差平方和 | K-Means 专用 |

---

## ⚠️ 边界与异常

| 边界情况 | 影响 | 处理方式 |
|---------|------|---------|
| **空输入** | 报错 | 检查 `len(X) == 0`，提前返回 |
| **单点数据** | 无意义 | `n < k` 时报错 |
| **重复值** | K-Means 初始化可能重复 | K-Means++ 初始化 |
| **极端规模** | 内存/时间爆炸 | Mini-Batch K-Means / DBSCAN |
| **高维数据** | 维度灾难，距离失效 | 降维（PCA）/ 余弦相似度 |
| **噪声/离群点** | 拉偏中心点 | DBSCAN / 预处理去噪 |
| **k > n** | 无意义 | 检查 `k <= n` |

---

## 🔗 相关章节

- [K-Means 详解](k-means/README.md) — K-Means 算法深入推导 + K-Means++ 初始化
- [降维算法](../dimensionality-reduction/README.md) — PCA / t-SNE 聚类前预处理
- 距离度量 — 欧氏 / 曼哈顿 / 余弦 / Jaccard

---

← [返回: 算法概述](../README.md)
