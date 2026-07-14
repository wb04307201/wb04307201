<!--
module:
  parent: computer-basics
  slug: algorithms/decision-tree
  type: article
  category: 主模块子文章
  summary: 决策树 3 大经典模型（ID3 / C4.5 / CART）
-->

# 决策树 3 大经典模型（ID3 / C4.5 / CART）

> ⬅️ [返回 02 算法](../README.md) | [返回 02.computer-basics](../../README.md)

> **一句话定位**：决策树 3 经典 = **ID3（信息增益）/ C4.5（信息增益率）/ CART（Gini 系数）**，是 XGBoost / LightGBM / 随机森林的基学习器。

---

## 📊 3 大模型对比

| 模型 | 年份 | 划分准则 | 任务类型 | 代表 |
|------|------|---------|---------|------|
| **ID3** | 1986 | 信息增益 | 分类 | Quinlan |
| **C4.5** | 1993 | 信息增益率 | 分类 | Quinlan |
| **CART** | 1984 | Gini 系数 | 分类 + 回归 | Breiman |

**CART** 是 sklearn 默认，也是 XGBoost / LightGBM 的基学习器。

---

## 📐 1. ID3 — 信息增益

**核心**：选**信息增益最大**的特征。

```
信息熵：H(D) = -Σ p_i log p_i
条件熵：H(D|A) = Σ |D_v|/|D| · H(D_v)
信息增益：Gain(D, A) = H(D) - H(D|A)
```

**问题**：偏向取值多的特征（如"身份证号"增益最大但无意义）。

---

## 📐 2. C4.5 — 信息增益率

**核心**：用**信息增益率**修正 ID3 的偏向。

```
信息增益率：GainRatio(D, A) = Gain(D, A) / IV(A)
其中：IV(A) = -Σ |D_v|/|D| · log(|D_v|/|D|)
```

**优点**：克服 ID3 偏向，是 ID3 的改进版。

---

## 📐 3. CART — Gini 系数

**核心**：用 **Gini 系数** 衡量不纯度，**可分类可回归**。

```
Gini(D) = 1 - Σ p_i²
```

**优点**：
- 计算效率高（无对数）
- 可回归（用 MSE）
- sklearn 默认

---

## 🛠️ Python 实现

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris

# 1. sklearn 一行（CART 算法）
X, y = load_iris(return_X_y=True)
clf = DecisionTreeClassifier(criterion='gini', max_depth=3)
clf.fit(X, y)
print(clf.score(X, y))  # 0.97

# 2. 决策树可视化
from sklearn.tree import plot_tree
plot_tree(clf, feature_names=iris.feature_names, class_names=iris.target_names)
```

---

## 📊 3 模型选择决策

```
Q1: 任务是分类还是回归？
├── 仅分类 → ID3 / C4.5
└── 分类 + 回归 → CART

Q2: 需考虑特征选择稳定性？
├── 是 → C4.5（信息增益率）
└── 否 → CART（计算快）

Q3: sklearn 默认？
└── ✅ CART（criterion='gini'）
```

---

## 🛠️ 关键超参数

| 超参数 | 作用 | 典型值 |
|--------|------|--------|
| max_depth | 树最大深度 | 3-10 |
| min_samples_split | 节点最少样本 | 10-50 |
| min_samples_leaf | 叶子最少样本 | 5-20 |
| max_features | 每次划分考虑的特征数 | sqrt / log2 |
| criterion | 划分准则 | gini / entropy |
| ccp_alpha | 后剪枝参数 | 0.01-0.1 |

**调参重点**：max_depth + min_samples_leaf（防过拟合）。

---

## ⚠️ 4 大过拟合防御

| 防御 | 实现 |
|------|------|
| **预剪枝** | 限制 max_depth / min_samples |
| **后剪枝** | Reduced Error Pruning / ccp_alpha |
| **集成学习** | 随机森林 / XGBoost |
| **特征选择** | 限制 max_features |

---

## 🔗 兄弟章节

- **本目录**：[随机森林](../) / [XGBoost](../) / [SVM](../)
- **02 同级**：[K-means](../clustering/k-means/README.md) / [梯度下降](../optimization/gradient-descent/README.md)
- **13.split-hairs**：[决策树面试](../../../13.split-hairs/02.computer-basics/machine-learning/decision-tree-interview/README.md)

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ ID3 / C4.5 / CART 只能用于表格数据 | ✅ 实际可处理任何特征工程后数据 |
| ❌ 决策树一定过拟合 | ✅ 限制深度 + 集成可避免 |
| ❌ 信息增益 = 信息增益率 | ✅ 不同公式，ID3 vs C4.5 |
| ❌ CART 只支持分类 | ✅ CART 支持分类 + 回归 |
| ❌ 树越深越好 | ✅ 浅树泛化更强 |

← [返回 02 算法](../README.md)