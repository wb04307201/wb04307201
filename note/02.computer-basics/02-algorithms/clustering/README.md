<!--
module:
  parent: computer-basics
  slug: computer-basics/algorithms/clustering
  type: index
  category: 主模块子文章
  summary: 聚类算法——将数据自动分组的无监督学习方法
-->

# 聚类算法

> 将数据自动分组的无监督学习方法，目标是组内相似、组间差异大。

## 目录

| 算法 | 核心思想 | 子 README |
|------|---------|-----------|
| [K-Means](k-means/README.md) | 迭代划分 k 个簇，最小化簇内平方和 | [子入口](k-means/README.md) |

---

## 如何确定最佳簇数 k？

| 方法 | 原理 | 适用场景 |
|------|------|---------|
| **肘部法则（Elbow Method）** | 画 SSE vs k 曲线，选拐点 | 簇数较少、数据分布清晰 |
| **轮廓系数（Silhouette）** | 衡量样本与自身簇的相似度 vs 与最近邻簇的相似度，范围 [-1, 1]，越大越好 | 通用，可自动化 |
| **Gap Statistic** | 比较实际 SSE 与均匀分布的参考 SSE | 更严谨，计算量大 |

## 4 大算法对比表

| 算法 | 簇形状 | 时间复杂度 | 适用场景 | 局限 |
|------|--------|---------|---------|------|
| **K-Means** | 球形/凸形 | O(n·k·t) | 大数据集、簇数已知、簇大小相近 | 对噪声/离群点敏感；只能发现球形簇 |
| **层次聚类 (Hierarchical)** | 任意 | O(n³) | 簇数未知、需可视化树状图 (Dendrogram) | 时间复杂度高；合并/分裂决策一旦做出无法回退 |
| **DBSCAN** | 任意（密度） | O(n log n) | 噪声数据、非凸形状、簇大小差异大 | 高维数据表现差；参数 ε 和 MinPts 难调 |
| **高斯混合 (GMM)** | 椭球形 | O(n·k·t) | 簇大小/形状差异大、需概率分配 | 对初始化敏感；可能陷入局部最优 |

**评估指标**：轮廓系数 (Silhouette, 范围 [-1, 1])、Davies-Bouldin Index (越小越好)、Calinski-Harabasz Index (越大越好)。

---

← [返回: 算法概述](../README.md)
