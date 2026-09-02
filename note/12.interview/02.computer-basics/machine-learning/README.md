<!--
module:
  parent: 02.computer-basics
  slug: 12.interview/02.computer-basics/machine-learning
  type: index-only
  category: 面试题索引
  summary: 传统机器学习 6 大算法单点深挖索引 + 5 大面试速查矩阵 + LLM 时代 ML 选型决策树。深度文档见各子目录（146-293 行）。
  depth: ⭐⭐⭐⭐
-->

<!-- index-only -->

# 传统机器学习 6 大算法（单点深挖索引）

> 原「机器学习 6 大算法综述」已于 2026-08-10 拆分为 6 个 single-topic deep-dive，每篇只讲透一个算法的数学本质 + 反直觉陷阱。完整知识体系见主模块 [02.cs-foundations/01-algorithms](../../../02.cs-foundations/01-algorithms/README.md)。

---

## 一、为什么面试必问 ML 6 大算法？

虽然 LLM/Transformer 已成主流，但**传统机器学习仍是面试必考**：

| 原因 | 说明 |
|------|------|
| **基础功底** | 理解 LR/Tree/Boosting 才能理解 XGBoost/LightGBM |
| **业务落地** | 80% 业务问题用 LR/Tree 解决（解释性 + 性能平衡）|
| **小数据场景** | 数据 < 10000 条，DL 失效，ML 是唯一选择 |
| **解释性要求** | 金融/医疗/法律需解释决策（监管要求）|
| **ML 仍是 AI 基础设施** | Transformer 内部有大量传统 ML（线性层/Softmax/Adam）|

**反直觉 1**（Session 9 实测）：**面试问"Transformer 内部为什么用 Layer Norm 而不是 Batch Norm"**——答案是数学上等价，但 Layer Norm 不依赖 batch size。**这需要 Batch Norm 知识**。

## 二、6 大算法速查矩阵

| 算法 | 监督/无监督 | 核心数学 | 时间复杂度 | 适用场景 | deep-dive |
|------|-----------|---------|----------|---------|---------|
| **K-means** | 无监督 | 距离最小化（WCSS）| O(n·k·d·iter) | 客户分群/图像压缩/异常检测 | [K-means 收敛](./k-means-convergence/README.md) |
| **决策树 (ID3/C4.5/CART)** | 监督 | 信息论/Gini | O(n·d·log n) | 解释性要求高/规则提取 | [决策树变体](./decision-tree-variants/README.md) |
| **梯度下降 (SGD/Adam/AdamW)** | 通用优化 | 一阶梯度 | O(n·d·iter) | 几乎所有 ML/DL 训练 | [GD 变体](./gradient-descent-variants/README.md) |
| **PCA** | 无监督降维 | 协方差矩阵特征分解 | O(d²·n + d³) | 降维可视化/去噪/特征压缩 | [PCA 数学](./pca-math/README.md) |
| **XGBoost/LightGBM/CatBoost** | 监督 | 二阶泰勒 + 直方图 | O(n·d·log n·tree) | 结构化数据竞赛/风控/推荐 | [Boosting 横评](./boosting-comparison/README.md) |
| **分类指标** | 评估 | TP/FP/FN + ROC | O(n) | 模型选型/A-B 测试 | [分类指标 5 大金刚](./classification-metrics/README.md) |

## 三、面试 5 大必考问题速查

### Q1：K-means 为什么用欧氏距离而不是余弦？

**一句话答案**：欧氏距离对球形簇最优，余弦适合文本/方向数据。

**详细**：
- K-means 假设簇是**球形等方差**（WCSS = Σ|x-μ|²），欧氏距离对应此假设
- 余弦距离适合"方向相似、大小不重要"（如文本向量）
- **反直觉 2**：高维稀疏数据（如文本 TF-IDF）用余弦 + K-means 比欧氏更优

### Q2：决策树如何处理连续特征？

**一句话答案**：二分法 — 选最优切分点。

**详细**：
1. 对每个连续特征的所有取值排序
2. 计算每个切分点的信息增益（ID3）/ 信息增益率（C4.5）/ Gini（CART）
3. 选最大者切分
4. **复杂度**：O(n·d·log n)，需先排序

**反直觉 3**：CART 用 Gini 而非信息增益——**Gini 计算无需 log**（更快），且对多分类更稳定。

### Q3：SGD 与 BGD 区别？

**一句话答案**：BGD 用全样本，SGD 用单样本。

| 维度 | BGD | SGD | Mini-batch |
|------|-----|-----|-----------|
| 每次更新样本 | 全部 N | 1 | b (32-512) |
| 收敛速度 | 慢 | 快（前期）| 快 |
| 稳定性 | 稳定 | 震荡 | 折中 |
| 适用 | 小数据 | 在线学习 | 大数据/深度学习 |

**Adam = SGD + 动量 + 自适应学习率** —— LLM 训练标配。

### Q4：PCA 与 SVD 关系？

**一句话答案**：PCA = 中心化数据的 SVD 截断。

| 维度 | PCA | SVD |
|------|-----|-----|
| 输入 | X (中心化) | X (任意) |
| 输出 | 主成分方向 + 投影 | U·Σ·V^T |
| 计算 | 协方差矩阵特征分解 | 直接 SVD 分解 |
| 大数据友好 | ❌ (O(d²n)) | ✅ (O(min(m,n)²·n)) |

**实实战**：sklearn `PCA` 底层调用 `randomized_svd`（随机 SVD 加速）。

### Q5：XGBoost 为什么用二阶泰勒展开？

**一句话答案**：二阶导数提供更精确的步长方向（牛顿法思想）。

| 算法 | 阶数 | 收敛 | 内存 |
|------|------|------|------|
| **GBDT** | 1 阶 | 慢 | 小 |
| **XGBoost** | 2 阶 | 快 | 中（存 g + h）|
| **LightGBM** | 1 阶 + 直方图 | 极快 | 小 |
| **CatBoost** | 1 阶 + ordered | 快（防过拟合）| 中 |

## 四、ML vs DL vs LLM 选型决策树

```
Q1: 数据规模？
  ├─ < 1000 行 → 传统 ML（LR/Tree）
  ├─ 1000-100,000 行 → XGBoost / LightGBM
  └─ > 100,000 行 → DL 或 fine-tune LLM

Q2: 是否结构化数据（表格）？
  ├─ 是 → XGBoost 仍是 SOTA（2024 Kaggle 冠军方案 80% 用 XGBoost/LGBM）
  └─ 否（图像/文本/语音）→ DL/LLM

Q3: 是否需要解释性？
  ├─ 是（金融/医疗/法律）→ 决策树 / LR / SHAP+XGBoost
  └─ 否 → DL/LLM

Q4: 训练资源？
  ├─ < 1 GPU·小时 → ML（XGBoost）
  ├─ 1-100 GPU·小时 → DL（BERT 微调）
  └─ > 100 GPU·小时 → LLM 预训练
```

## 五、ML 面试 5 大反直觉陷阱

| 陷阱 | 真相 |
|------|------|
| "XGBoost 总是最好的" | ❌ 小数据集 LR 更稳定，DL 数据集 Transformer 更优 |
| "标准化对树模型无用" | ⚠️ 严格说对 CART 无用，但 XGBoost 实际有用（分裂点计算）|
| "PCA 保留最多信息" | ⚠️ PCA 保留最大方差，**不等于最多信息**（如分类边界）|
| "K-means 必收敛" | ✅ 一定收敛，但可能收敛到**局部最优**（多次随机初始化）|
| "Adam 总是优于 SGD" | ❌ Adam 泛化常差于 SGD+momentum（sharp minima 问题）|

## 六、LLM 时代 ML 还重要吗？

**反直觉 4**（v3 测试驱动）：**Transformer 内部全是传统 ML**：

| 组件 | 等价的 ML 算法 |
|------|--------------|
| Linear 层 | LR（线性回归 / Softmax 回归）|
| Layer Norm | 标准化（PCA 白化的简化版）|
| Adam Softmax | 梯度下降变体 |
| Softmax | LR 多分类 |
| Cross-Entropy | KL 散度 / MLE |
| Attention | 加权平均（soft K-means）|

**面试必备**：能讲清 Transformer 每个组件对应哪个传统 ML 算法 → **面试官立刻给"基础扎实"标签**。

## 七、生产实战 5 大避坑

| 坑 | 现象 | 修复 |
|----|------|------|
| **数据泄漏** | 用未来数据预测过去 | 严格按时间切分（time-based split）|
| **类别不均衡** | 准确率99%但全预测多数类 | SMOTE / class_weight / focal loss |
| **过拟合** | 训练集 99%，测试集 60% | 正则化 + 交叉验证 + early stopping |
| **特征泄漏** | 标准化用了测试集均值 | 只在训练集 fit，测试集 transform |
| **超参泄漏** | 用测试集选超参 | 严格 train/val/test 三段切分 |

## 八、5 个代码示例索引

| 示例 | 文件 | 用途 |
|------|------|------|
| K-means 实现 | [k-means-convergence](./k-means-convergence/README.md) | 手写 vs sklearn 对比 |
| 决策树可视化 | [decision-tree-variants](./decision-tree-variants/README.md) | graphviz 导出树 |
| Adam 实现 | [gradient-descent-variants](./gradient-descent-variants/README.md) | SGD/Adam/AdamW 对比 |
| PCA 重建 | [pca-math](./pca-math/README.md) | 压缩率 + 重建误差 |
| LightGBM 调参 | [boosting-comparison](./boosting-comparison/README.md) | 5 大超参 + Optuna 自动调参 |

## 九、面试话术模板（90 秒版）

```
机器学习是深度学习的基础。

面试时我会先讲算法本质（数学），再讲代码实现（sklearn），
最后讲业务应用（哪个场景用哪个）。

比如 K-means，本质是 WCSS 最小化（迭代更新簇中心），
代码 5 行（sklearn.cluster.KMeans），
业务用客户分群（先 elbow 法选 K）。

LR 是最被低估的——简单但可解释，
加上 L1/L2 正则化就是 ElasticNet，金融风控首选。

XGBoost 是结构化数据 SOTA（Kaggle 验证），
关键是理解二阶泰勒 + 直方图加速 + leaf-wise 生长。
```

## 十、6 篇 deep-dive 入口

| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [K-means 收敛性 + K-means++](k-means-convergence/) | ⭐⭐⭐ | WCSS 收敛证明 + K-means++ D² 概率 + 4 大反直觉陷阱 |
| [决策树 ID3/C4.5/CART](decision-tree-variants/) | ⭐⭐⭐ | 信息增益 vs 信息增益率 vs Gini 公式对比 + 5 大陷阱 |
| [梯度下降 SGD/BGD/Adam/AdamW](gradient-descent-variants/) | ⭐⭐⭐ | Adam 完整公式 + AdamW 权重衰减解耦 + 5 大陷阱 + LLM 训练标配 |
| [PCA 数学本质 + SVD](pca-math/) | ⭐⭐⭐⭐ | 拉格朗日推导 + 协方差特征向量 + 6 大陷阱（标准化/无监督/线性等）|
| [XGBoost/LightGBM/CatBoost 横评](boosting-comparison/) | ⭐⭐⭐⭐ | XGBoost 二阶泰勒 + LightGBM 直方图/leaf-wise + CatBoost ordered boosting + 选型决策树 |
| [分类评估指标 5 大金刚](classification-metrics/) | ⭐⭐⭐ | 准确率/精确率/召回率/F1/AUC + 不均衡陷阱 + 场景化选型 |

---

## 相关章节

- [02.cs-foundations/01-algorithms 主模块](../../../02.cs-foundations/01-algorithms/README.md) — 算法基础
- [12.interview/02.computer-basics 索引页](../README.md) — 计算机基础面试
- [深度学习入门](../../11.ai/README.md) — DL 基础
- [Transformer 基础](../../11.ai/transformer/README.md) — LLM 核心

← [返回: 02.computer-basics 综述](../README.md)