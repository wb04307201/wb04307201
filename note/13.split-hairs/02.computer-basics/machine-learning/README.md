<!--
question:
  id: 02.computer-basics-machine-learning
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 算法基础
  tags: [ML, K-means, 决策树, 梯度下降, PCA, 集成学习]
-->

# 传统机器学习面试深挖（6 大核心）

> ⬅️ [返回 计算机基础咬文嚼字](../README.md) | [主模块深度](../../../02.computer-basics/02-algorithms/README.md)

> **一句话定位**：6 大传统 ML 算法**面试深挖版**：K-means / 决策树 / 梯度下降 / PCA / 集成学习 / 评估指标。

---

## 🎯 6 大核心题

### Q1：K-means 一定收敛吗？为什么是局部最优？

**陷阱**：
- ❌ 答"随机选质心"（太浅）
- ❌ 不知道收敛性证明

**30 秒话术**：
> "K-means 一定收敛，因为**目标函数 J（WCSS）单调递减且有下界**。但只保证**局部最优**——不同初始质心可能收敛到不同结果。"

**90 秒话术**：
> "证明：每次分配步骤 J 不增（每个点分到最近质心），每次更新步骤 J 不增（重新计算质心最小化子集 J），J 单调下降 + 有下界 0 → **必收敛**。但**初始质心敏感**是主要问题。缓解：**K-means++** 智能选初始质心（按 D² 概率），**n_init=10** 多次随机取最优。**K 选择**：肘部法则 + 轮廓系数。"

---

### Q2：决策树 ID3 / C4.5 / CART 三大模型的核心区别？

**陷阱**：
- ❌ 答"都是决策树"（废话）
- ❌ 混淆划分准则

**30 秒话术**：
> "ID3 用**信息增益**，C4.5 用**信息增益率**（修正 ID3 偏向），CART 用 **Gini 系数**（计算快，sklearn 默认）"

**90 秒话术**：
> "**ID3**（1986）用信息熵 H(D) = -Σp log p，**偏向取值多的特征**（身份证号等）。**C4.5**（1993）用信息增益率 Gain/IV，**克服 ID3 偏向**，但计算稍慢。**CART**（1984）用 Gini = 1 - Σp²，**计算效率高**（无对数），**支持分类和回归**（用 MSE），是 sklearn 和 XGBoost 默认。**调参重点**：max_depth（防过拟合）+ min_samples_leaf。**集成学习**（XGBoost / LightGBM）的基学习器就是 CART。"

---

### Q3：梯度下降 SGD / BGD / Adam 的区别？

**陷阱**：
- ❌ 答"SGD 快"（不够）
- ❌ 不知道 Adam 内部机制

**30 秒话术**：
> "**BGD** 用全量数据（稳但慢），**SGD** 用 1 个样本（快但震），**Mini-Batch** 是平衡（32-512），**Adam** = RMSProp + Momentum（自适应学习率，深度学习默认）。"

**90 秒话术**：
> "**BGD**（Batch GD）每步用全部 n 样本，稳定但内存大、慢。**SGD**（Stochastic）每步用 1 样本，快但震荡大。**Mini-Batch** 是工业标准（batch=32-256），兼顾速度与稳定。**Adam**（2014 Kingma）= 一阶动量 m（指数移动平均梯度）+ 二阶动量 v（梯度平方），**自适应学习率**：lr·m̂/(√v̂+ε)。比 SGD+动量收敛快 2-3x，**LLM 训练默认用 AdamW**（Adam + 权重衰减解耦）。**学习率策略**：Warmup + Cosine 是 2024 大模型标配。"

---

### Q4：PCA 的数学本质是什么？与 SVD 关系？

**陷阱**：
- ❌ 答"降维"（废话）
- ❌ 不知道特征值分解

**30 秒话术**：
> "PCA = **找数据方差最大的正交方向**（协方差矩阵的特征向量）。数学：中心化 → 协方差矩阵 → 特征值分解 → Top-K 特征向量 = 投影矩阵。"

**90 秒话术**：
> "**核心数学**：X (中心化) 的协方差矩阵 Σ = X^T X / (n-1)，特征值分解 Σ = V Λ V^T，**V 的 Top-K 列**就是 PCA 投影方向。**PCA = 找方差最大方向 = 保留最多信息**。**与 SVD 关系**：X = U Σ V^T（SVD），PCA 投影矩阵 = V 的 Top-K 右奇异向量。**sklearn PCA 内部用 SVD**（数值稳定，避免显式计算协方差）。**K 选择**：累积方差贡献 ≥ 95% 的最小 K。**Kernel PCA** 处理非线性。**局限**：仅线性，对异常值敏感（用 Robust PCA）。"

---

### Q5：XGBoost / LightGBM / CatBoost 三大 Boosting 库横评？

**陷阱**：
- ❌ 答"XGBoost 最好"（不准确）
- ❌ 不知道各自优势

**30 秒话术**：
> "**XGBoost** = 二阶导数 + 正则化，**SOTA 准确率**，调参丰富。**LightGBM** = 直方图 + leaf-wise，**5-10x XGBoost**，大数据首选。**CatBoost** = 原生类别特征，**无需手动编码**。"

**90 秒话术**：
> "**XGBoost**（2016）用二阶泰勒展开 + L1/L2 正则 + 列采样，**Kaggle 霸主 2016-2020**。**LightGBM**（2017）创新：直方图分箱（O(data) 寻找最佳分裂）+ leaf-wise 生长（而非 level-wise）+ GOSS 梯度采样，**比 XGBoost 快 5-10x**，大数据集首选。**CatBoost**（2018）创新：**ordered boosting**（解决目标泄露）+ **原生类别特征**（无需 One-Hot）+ **对称树**（推理快 10x）。**选型**：小数据 → XGBoost（稳），大数据 → LightGBM（快），类别多 → CatBoost（方便）。**统一基学习器**：都是 CART 决策树。"

---

### Q6：如何评估分类模型？5 大指标

**陷阱**：
- ❌ 只答"准确率"（不够）
- ❌ 不知道场景选指标

**30 秒话术**：
> "**准确率 / 精确率 / 召回率 / F1 / AUC** 五大指标。**不均衡数据**用 F1 / AUC；**多分类**用 macro-F1 / micro-F1；**概率输出**用 LogLoss / AUC。"

**90 秒话术**：
> "**准确率** = 正确数 / 总数（**不均衡数据失效**，99% 负样本全预测负也有 99%）。**精确率** = TP / (TP+FP)（预测为正的真阳比例）。**召回率** = TP / (TP+FN)（实际正被找出的比例）。**F1** = 2PR/(P+R)（P-R 平衡）。**AUC** = ROC 曲线下面积（**不依赖阈值**，0.5=随机，1.0=完美）。**LogLoss** = 概率输出的对数损失。**场景选择**：搜索推荐（**召回优先**）/ 金融风控（**精确优先**）/ 不均衡数据（**F1 / AUC**）。**混淆矩阵**是基础工具。"

---

## 🔗 兄弟章节

- **主模块深度**：[02-algorithms](../../../02.computer-basics/02-algorithms/README.md)
- **兄弟面试题**：[字符串算法](../string-algorithms/README.md) / [贪心算法](../greedy-algorithms/README.md) / [复杂度分析](../complexity/README.md)
- **AI 关联**：[K-means 聚类](../../../02.computer-basics/02-algorithms/clustering/k-means/README.md) / [梯度下降](../../../02.computer-basics/02-algorithms/optimization/gradient-descent/README.md) / [决策树](../../../02.computer-basics/02-algorithms/decision-tree/README.md)

---

## 📊 6 题难度速查

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 K-means 收敛 | ⭐⭐⭐ | 高频 | K-means++ D² 概率 |
| Q2 决策树 3 模型 | ⭐⭐⭐ | 高频 | Gini 公式 |
| Q3 梯度下降变体 | ⭐⭐⭐ | 高频 | Adam m̂/(√v̂+ε) |
| Q4 PCA 数学 | ⭐⭐⭐⭐ | 中频 | 协方差特征值 |
| Q5 XGBoost 横评 | ⭐⭐⭐⭐ | 中频 | LightGBM 5-10x |
| Q6 评估指标 | ⭐⭐⭐ | 高频 | F1 / AUC |

← 返回 [计算机基础咬文嚼字](../README.md)