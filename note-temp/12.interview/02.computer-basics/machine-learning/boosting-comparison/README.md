<!--
question:
  id: 02.computer-basics-boosting-comparison
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 选型对比
  tags: [ML, XGBoost, LightGBM, CatBoost, Boosting, GBDT]
-->

# XGBoost / LightGBM / CatBoost：三大 Boosting 库的工程取舍

> ⬅️ [返回: 02.computer-basics 综述](../README.md) | [主模块: ensemble](../../../../../note/02.computer-basics/02-algorithms/ensemble/README.md)

> **一句话定位**：3 个 GBDT 实现库（XGBoost / LightGBM / CatBoost）的**工程取舍对比**——面试"选型对比"型经典题，考察的不是"都是 Boosting"，而是**目标函数、近似算法、类别处理**三大差异。

> **系列定位**：经典 ML 面试题（决策树 / Boosting / K-means / PCA / 评估指标）。3 库基学习器**全是 CART**（见 [`decision-tree-variants`](../decision-tree-variants/README.md)），掌握 CART 即可看懂所有 Boosting 实现。

---

## 引子：面试官的反问

> 面试官：你 Kaggle 风控建模这 3 个库都用过吧？
> 候选人：都用过，XGBoost、LightGBM、CatBoost 都跑过。
> 面试官：**那现在给你 100w 行数据 + 30 个类别字段，你选哪个？为什么 LightGBM 比 XGBoost 快 5-10x？CatBoost 的 ordered boosting 解决的是什么泄露问题？**

这道题 90% 候选人死在"都是 Boosting"五个字上。其实三者核心区别就 3 件事：**目标函数展开阶数**（一阶/二阶）、**最佳分裂点搜索策略**（预排序/直方图）、**类别特征处理方式**（One-Hot/原生）。这 3 件事决定了**训练速度、内存占用、类别处理**三大权衡。

---

## 一、核心原理

### 1.1 共同基：CART + GBDT 梯度提升

三者的**基学习器都是 CART 回归树**（不是 ID3、不是 C4.5），都用**加法模型 + 前向分步**：

```text
ŷ_i^(t) = ŷ_i^(t-1) + ε · f_t(x_i)
f_t = CART，目标是拟合前一轮的负梯度 -∂L/∂ŷ
```

### 1.2 XGBoost（2016, Chen & Guestrin）—— 二阶泰勒展开 + 正则

```text
目标函数：
  Obj^(t) = Σᵢ L(y�, ŷᵢ^(t-1) + f_t(xᵢ))  +  Ω(f_t)
          ≈ Σᵢ [ L(yᵢ, ŷᵢ^(t-1)) + gᵢ·f_t(xᵢ) + ½ hᵢ·f_t²(xᵢ) ]  +  ½λ·‖w‖² + γ·T
          = Σᵢ [ gᵢ·f_t(xᵢ) + ½ hᵢ·f_t²(xᵢ) ]  +  ½λ·‖w‖² + γ·T

其中：
  gᵢ = ∂L/∂�          （一阶梯度）
  hᵢ = ∂²L/∂ŷ²         （二阶梯度，海森矩阵）
  Ω(f) = γ·T + ½λ·‖w‖² （结构 + L2 正则）
  T   = 树的叶子数
  λ   = L2 正则系数
  γ   = 分裂最小增益阈值
```

**核心创新**：二阶展开（用 hᵢ 修正梯度）+ 显式正则（γ 控叶子数、λ 控叶子权重）。**Kaggle 2015-2018 霸主**，生态最丰富（调参文档、社区、SHAP 集成）。`tree_method='hist'`（2017 后）是直方图移植版本。

### 1.3 LightGBM（2017, Microsoft）—— 直方图 + leaf-wise + GOSS

**三大创新**（面试重点）：

1. **直方图分箱（Histogram）**：把连续特征分桶成离散 bin（默认 256），**O(data) → O(bin)**，找最佳分裂点不再遍历每个样本。
   ```text
   传统 XGBoost pre-sort：对每个特征排序找 split → O(n·log n)
   LightGBM histogram：把特征分 256 bin，遍历 bin 找 split → O(256·bin)
   ```
2. **leaf-wise 生长**：每次找**增益最大的叶子**分裂（不像 XGBoost 的 level-wise 按层生长）。在相同分裂次数下，**精度更高、深度更深、可能过拟合**——所以必须用 `max_depth` 限制。
3. **GOSS（Gradient-based One-Side Sampling）**：保留**大梯度样本全采**（信息量高），**小梯度样本随机采**（信息量低）。训练样本量可减少 50%+ 但精度几乎不变。

**结果**：比 XGBoost **快 5-10x**、**内存少 50%+**，**大数据首选**（>10w 行）。

### 1.4 CatBoost（2018, Yandex）—— ordered boosting + 原生类别 + 对称树

**三大创新**：

1. **Ordered Boosting**：用**排列（permutation）后的样本**计算梯度，避免**目标泄露（target leakage）**——传统 GBDT 用同一样本算梯度又拟合，导致预测偏移。`catboost` 用前 i-1 个样本的梯度训练第 i 棵树，推理更接近真实分布。
2. **原生类别特征（cat_features）**：无需 One-Hot / Target Encoding。CatBoost 用 **Ordered Target Statistics**（类似带先验的 Target Encoding）自动处理，**支持高基数特征**（如城市 ID、产品 SKU）。
3. **对称树（Oblivious Trees）**：同一层所有节点用**同一个分裂特征和阈值**——推理时可向量化、并行预测，比 XGBoost 非对称树**快 10-100x**，**CPU 推理场景首选**。

---

## 二、代码示例

```python
import time
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb, lightgbm as lgb, catboost as cb

# 加载 Titanic（实际跑可用更大数据集验证速度差异）
X, y = fetch_openml('titanic', version=1, as_frame=True, return_X_y=True)
X = X[['pclass', 'sex', 'age', 'fare', 'embarked']].fillna(0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost
t0 = time.time(); m_xgb = xgb.XGBClassifier(n_estimators=500, max_depth=6, learning_rate=0.05, tree_method='hist', enable_categorical=True).fit(X_train, y_train); print(f'XGBoost:   {time.time()-t0:.2f}s, AUC={roc_auc_score(y_test, m_xgb.predict_proba(X_test)[:,1]):.4f}')

# LightGBM
t0 = time.time(); m_lgb = lgb.LGBMClassifier(n_estimators=500, max_depth=6, learning_rate=0.05).fit(X_train, y_train); print(f'LightGBM:  {time.time()-t0:.2f}s, AUC={roc_auc_score(y_test, m_lgb.predict_proba(X_test)[:,1]):.4f}')

# CatBoost（原生类别特征）
t0 = time.time(); m_cb = cb.CatBoostClassifier(iterations=500, depth=6, learning_rate=0.05, cat_features=['sex','embarked'], verbose=0).fit(X_train, y_train); print(f'CatBoost:  {time.time()-t0:.2f}s, AUC={roc_auc_score(y_test, m_cb.predict_proba(X_test)[:,1]):.4f}')
```

**实测经验**：CatBoost 在有类别列时 AUC 略优（+0.5-1%），但训练慢 2-3x；LightGBM 纯数值列最快。

---

## 三、常见陷阱

### 陷阱 1：XGBoost 默认 learning_rate=0.3 太大，训练慢
**真相**：XGBoost 默认 `learning_rate=0.3`（早期论文值），LightGBM 默认 0.05，CatBoost 默认 0.03。**0.3 在大数据集上慢且震荡**——务必显式设为 `learning_rate=0.05-0.1`，配合 `n_estimators` 调大 + early stopping。

### 陷阱 2：LightGBM 的 categorical_feature 必须显式指定
**真相**：LightGBM 默认把**所有列当数值处理**。必须显式传 `categorical_feature=['col_a', 'col_b']`，否则类别列被当连续值分桶，**类别信息完全丢失**。CatBoost 反而要传 `cat_features`，XGBoost 用 `enable_categorical=True` + 类别 dtype。

### 陷阱 3：CatBoost 的 cat_features 在 predict 时也要传
**真相**：CatBoost 在 `fit` 时用 `cat_features` 学到类别处理参数，**predict 时必须传相同的 cat_features**（顺序也要一致），否则**直接报错** `CatFeatures type differs from training`。这是工程化部署最常见的坑。

### 陷阱 4：3 个库的 GPU 支持差异巨大
**真相**：LightGBM GPU 支持最成熟（`device='gpu'`），XGBoost 次之（`tree_method='gpu_hist'`），CatBoost GPU 也支持但需 `task_type='GPU'`。**CPU 调好的参数不直接适用 GPU**——GPU 通常需要更大 `max_depth` 或更小 `learning_rate`，否则 OOM。

### 陷阱 5：XGBoost 的 tree_method='hist' 是 2017 后才稳定
**真相**：早期 XGBoost 用 `tree_method='exact'`（暴力预排序），**2017 后才移植 LightGBM 的直方图算法**。如果团队用 XGBoost 1.0 之前版本 + 大数据，**速度比 LightGBM 慢的不是 5x 而是 50x**——务必升级到 1.6+。

---

## 四、最佳实践

### 选型决策树

```text
数据规模 + 场景
    │
    ├─ < 10w 行 + 数值特征为主
    │       └─→ XGBoost（Kaggle 霸主，调参文档最全）
    │
    ├─ > 10w 行 + 数值特征为主
    │       └─→ LightGBM（快 5-10x，内存省 50%）
    │
    ├─ 类别特征多（> 10 列 or 高基数）
    │       └─→ CatBoost（无需手动编码，AUC 通常 +0.5-1%）
    │
    ├─ CPU 推理延迟敏感（移动端/嵌入式）
    │       └─→ CatBoost（对称树向量化推理，快 10-100x）
    │
    └─ LLM 时代传统表格 ML
            └─→ 已被 TabPFN / 神经网络超越，但小数据仍首选 Boosting
```

### 通用调参起点（3 库通用）

```python
base_params = dict(
    n_estimators=500,         # 配 early_stopping 实际用到 100-300
    max_depth=6,              # 5-8 是经验值，超过 10 易过拟合
    learning_rate=0.05,       # 0.03-0.1，配合 early_stopping
    subsample=0.8,            # 行采样，防过拟合
    colsample_bytree=0.8,     # 列采样
    reg_lambda=1.0,           # L2 正则
    reg_alpha=0.0,            # L1 正则（稀疏特征开启）
    early_stopping_rounds=50, # 必备，验证集不再下降 50 轮停止
    random_state=42
)
```

---

## 五、面试话术

### 30 秒版本

> "**XGBoost** 用**二阶泰勒展开** + 显式正则（γ 控叶子数、λ 控权重），Kaggle 霸主；**LightGBM** 三大创新：**直方图分箱**（O(data)→O(bin)）、**leaf-wise 生长**、**GOSS 梯度采样**，比 XGBoost **快 5-10x**，大数据首选；**CatBoost** 三大创新：**Ordered Boosting** 解决目标泄露、**原生类别特征** 无需 One-Hot、**对称树**推理快 10-100x，类别多和 CPU 推理首选。**基学习器全是 CART**。"

### 90 秒版本

> "三者都是 **GBDT + CART**，核心区别 3 点：**第一**，**目标函数**——XGBoost 用**二阶泰勒展开**（gᵢ + ½hᵢf²）+ L1/L2 正则，是 Kaggle 2015-2018 霸主，调参文档最全；**第二**，**近似算法**——LightGBM 用**直方图分箱**把连续特征分 256 bin，配合 **leaf-wise 生长**（每次找增益最大的叶子分裂）和 **GOSS 梯度采样**（保留大梯度、小梯度随机采），**比 XGBoost 快 5-10x、内存省 50%+**，但 leaf-wise 可能过拟合需配 `max_depth`；**第三**，**类别处理**——CatBoost 用 **Ordered Boosting** 解决 GBDT 的目标泄露（用 permutation 后的样本算梯度），用 **Ordered Target Statistics** 编码类别特征**无需 One-Hot**，用**对称树**（同一层同一分裂）让 CPU 推理快 10-100x。**选型**：< 10w 选 XGBoost，> 10w 选 LightGBM，类别多 / 推理敏感选 CatBoost。**调参起点**：`max_depth=6`、`learning_rate=0.05`、`n_estimators=500`、配 `early_stopping_rounds=50`。"

---

## 六、交叉引用

- **主模块**：[`02-algorithms/ensemble`](../../../../../note/02.computer-basics/02-algorithms/ensemble/README.md) — 集成学习原理（含 Boosting 推导）
- **兄弟面试题**：[`decision-tree-variants`](../decision-tree-variants/README.md) — ID3/C4.5/CART 划分准则（基学习器 = CART） / [`classification-metrics`](../classification-metrics/README.md)
- **反向链接**：[`02.computer-basics 综述`](../README.md) — 6 大核心题速查表

---

> 📅 2026-08-10 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐⭐
