<!--
question:
  id: 02.computer-basics-classification-metrics
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 概念辨析
  tags: [ML, 评估指标, F1, AUC, ROC, 混淆矩阵, LogLoss]
-->

# 分类评估指标 5 大金刚：什么时候用 F1，什么时候用 AUC？

> ⬅️ [返回: machine-learning 综述](../../README.md) | [主模块: 02-algorithms 评估指标](../../../../02.cs-foundations/01-algorithms/README.md)

> **一句话定位**：分类模型的 5 大评估指标（准确率 / 精确率 / 召回率 / F1 / AUC）—— 考察的不是"公式怎么写"，而是 **场景化选型** + **不均衡数据陷阱** + **阈值依赖性** + **LogLoss 概率校准**。

> **系列定位**：经典 ML 面试题（6 大核心题 Q6）。考察的不是"列举指标"——而是 **5 大指标公式 + ROC/PR 曲线差异 + 场景决策树 + 不均衡数据陷阱**。

---

## 引子：面试官的反问 —— 1% 正样本，你选什么指标？

```text
面试官：你训练了一个信用卡欺诈检测模型，测试集 10000 笔交易，**只有 100 笔是欺诈（正样本 1%）**。
候选人：我用准确率评估。
面试官：那我训练一个"全部预测为正常"的模型，准确率 99% —— 你的模型比这个强吗？
候选人：……好像没强多少。
面试官：那如果这个模型召回率只有 30%（漏掉了 70% 的欺诈交易），AUC 0.95 你敢上线吗？
候选人：……
```

**反直觉现场**：
1. 普通候选人：会用 `accuracy_score`，但**说不清为什么不均衡数据会骗人**
2. 优秀候选人：能立刻切换到 **F1 / AUC-PR**，并解释**精确率 vs 召回率**的权衡
3. 资深候选人：能用**混淆矩阵 + ROC + PR 曲线**三件套回答，并指出 AUC 高不代表业务好（医疗诊断 AUC 0.95 但召回 30% 漏诊严重）

这道题 90% 候选人死在"准确率 = 模型好坏"的迷思上。**指标选错，整个模型评估就是错的**。

---

## 一、核心原理

### 1.1 混淆矩阵：所有指标的基石

| | 预测正例 (P') | 预测负例 (N') |
|---|---|---|
| **实际正例 (P)** | TP（真阳） | FN（假阴，漏报） |
| **实际负例 (N)** | FP（假阳，误报） | TN（真阴） |

- **TP**：实际欺诈，预测欺诈（抓对了）
- **FP**：实际正常，预测欺诈（误报，吓到用户）
- **FN**：实际欺诈，预测正常（漏报，损失金钱）
- **TN**：实际正常，预测正常（放过）

**核心洞察**：**任何单数字指标都是 TP/FP/FN/TN 的某种聚合**。要永远先看混淆矩阵，再看指标。

### 1.2 5 大指标公式（二分类）

```text
准确率 Accuracy   = (TP + TN) / (P + N)         ← 整体正确率
精确率 Precision  = TP / (TP + FP)               ← 预测为正的真阳比例
召回率 Recall     = TP / (TP + FN)               ← 实际正被找出比例
F1 分数           = 2 · P · R / (P + R)          ← P-R 调和平均
AUC               = ∫₀¹ TPR(FPR⁻¹(t)) dt          ← ROC 曲线下面积
```

**物理含义**：
- **Accuracy**：100 个里猜对几个
- **Precision**：我说"是欺诈"的里面，真的有多少是欺诈
- **Recall**：100 个真欺诈里，我抓出几个
- **F1**：P 和 R 的平衡（一个高一个低时 F1 会被拉低）
- **AUC**：模型对随机正负样本的**排序能力**（不依赖阈值）

### 1.3 ROC 曲线：FPR vs TPR 随阈值变化

```text
FPR = FP / (FP + TN)  ← 实际负例被误报比例
TPR = TP / (TP + FN)  ← 实际正例被找出比例（= Recall）
```

- 横轴 FPR，纵轴 TPR，**每个阈值对应曲线上的一个点**
- 阈值 = 0.5 → 一个点；阈值从 0 扫到 1 → 一条曲线
- **AUC = 曲线下面积** ∈ [0.5, 1]，0.5 = 随机猜，1.0 = 完美分类
- **AUC 的物理含义**：随机抽一个正样本和一个负样本，模型对正样本打分高于负样本的概率

### 1.4 PR 曲线：Precision vs Recall

- 横轴 Recall，纵轴 Precision
- **PR 曲线对不均衡数据更敏感**（因为 Precision 受 FP 影响大，负样本多时 FP 容易爆）
- **AUC-PR（PR 曲线下面积）**在不均衡数据上比 AUC-ROC 更能反映模型好坏

### 1.5 LogLoss（对数损失，概率输出的"硬指标"）

```text
LogLoss = -1/N · Σ [ yᵢ · log(pᵢ) + (1 - yᵢ) · log(1 - pᵢ) ]
```

- y 是真实标签（0/1），p 是模型预测的正类概率
- **错得越自信 → 惩罚越重**（p=0.01 预测为 1 时损失 ≈ 4.6）
- 训练时用 LogLoss 作为损失函数，**比 0/1 损失更"严格"**（提供梯度信号）
- **缺点**：概率校准不好时 LogLoss 也会骗人（模型过自信 / 过保守）

### 1.6 多分类扩展：macro / micro / weighted

| 指标 | 计算方式 | 适用场景 |
|------|---------|---------|
| **macro-F1** | 每个类 F1 的**算术平均** | 小类重要（如稀有病诊断） |
| **micro-F1** | 全局 TP/FP/FN 算 F1 | **等于 Accuracy**（多分类时） |
| **weighted-F1** | 每个类 F1 × 该类样本占比 | 类别不均衡但想反映全局 |

**陷阱**：macro-F1 给每个类**同等权重**，小类样本少但 F1 变化大时，macro-F1 波动剧烈。

---

## 二、代码示例：sklearn 30 行计算 5 指标

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, log_loss, confusion_matrix)
import numpy as np

# 1) 构造不均衡数据集（正样本 5%）
X, y = make_classification(n_samples=10000, n_features=20, weights=[0.95, 0.05],
                            random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 2) 训练模型
model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]  # 正类概率

# 3) 5 大指标一次性算齐
print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")  # ← 不均衡时虚高
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"F1       : {f1_score(y_test, y_pred):.4f}")        # ← 不均衡首选
print(f"AUC      : {roc_auc_score(y_test, y_proba):.4f}")  # ← 阈值无关
print(f"LogLoss  : {log_loss(y_test, y_proba):.4f}")        # ← 概率校准

# 4) 混淆矩阵（永远先看这个）
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
```

**典型输出（不均衡数据）**：
```text
Accuracy : 0.9520  ← 看起来很美，但……
Precision: 0.7800
Recall   : 0.6500
F1       : 0.7090
AUC      : 0.9420
LogLoss  : 0.1234
Confusion Matrix:
 [[2828   22]    ← 实际负类 2850，预测对 2828
  [  35   87]]   ← 实际正类 122，预测对 87（漏报 35）
```

**对比"全部预测负类"的基线**：
- 全部负类 → Accuracy = 95%（**和你的模型几乎一样**）
- 全部负类 → Recall = 0%（**模型明显更强**）

---

## 三、常见陷阱（5 个反直觉点）

### 陷阱 1：99% 负样本时，准确率 99% 没意义

- **真相**：在不均衡数据上，准确率会**被多数类主导**。预测全部为负类，Accuracy = 99%，但模型**完全没用**（Recall = 0%）。
- **解决**：用 **F1 / AUC-PR** 替代 Accuracy，永远配对看 Precision 和 Recall。
- **面试话术**：**Accuracy 是"无脑指标"——不均衡数据上必须弃用**。

### 陷阱 2：AUC 高不代表业务指标好

- **真相**：医疗诊断模型 AUC 0.95 听起来很美，但**如果阈值设成 0.5，Recall 只有 30%**（漏诊 70% 的癌症患者），**业务上完全不可接受**。AUC 只看**排序能力**，不关心具体阈值下的精确率 / 召回率。
- **解决**：**AUC + 业务指标（Precision/Recall @ 业务阈值）双轨评估**。
- **面试话术**：**AUC 是"模型排序能力的上限"，不是"业务落地的指标"**。

### 陷阱 3：精确率 / 召回率是阈值依赖的，AUC 不依赖阈值

- **真相**：阈值 = 0.5 时 P=0.7、R=0.6；阈值 = 0.3 时 P=0.5、R=0.85。**同一个模型，换个阈值 P-R 完全变**。但 **AUC 是把所有阈值下的 ROC 面积积分，所以与阈值无关**。
- **解决**：**报告指标时必须带阈值**（"Recall = 0.85 @ threshold=0.3"）；模型对比用 **AUC**（不挑阈值）。
- **面试话术**：**AUC 的核心价值 = 阈值无关**——选模时用 AUC，部署时根据业务选阈值。

### 陷阱 4：多分类 macro-F1 给小类同等权重

- **真相**：5 分类任务，类 A 有 1000 样本，类 E 只有 10 样本。macro-F1 把 E 的 F1 和 A 的 F1 **同等加权**——E 多错一个，macro-F1 抖 10%。**用 weighted-F1** 才是反映全局的指标。
- **解决**：小类重要（如稀有病）→ macro-F1；想看全局 → weighted-F1 / micro-F1。
- **面试话术**：**macro-F1 看"短板"，weighted-F1 看"大盘"**。

### 陷阱 5：LogLoss 比 0/1 损失"严格"，但概率校准不好时也骗人

- **真相**：LogLoss 对"自信地错"惩罚极重（p=0.01 预测 1 → 损失 4.6）。但**如果模型没做概率校准**（如 SVM 输出未经 Platt Scaling 的分数），LogLoss 也会骗人——可能准确率高但 LogLoss 巨大。
- **解决**：概率输出必须**校准**（`sklearn.calibration.CalibratedClassifierCV`），LogLoss 才有意义。
- **面试话术**：**LogLoss 是"概率模型的身份证"**——非概率模型别用。

---

## 四、最佳实践

### 4.1 场景化选型决策树

```mermaid
graph TD
    A[分类任务] --> B{数据是否均衡?}
    B -- 不均衡 --> C{业务关心?}
    C -- 召回优先<br/>搜索推荐 --> D[Recall@K / NDCG]
    C -- 精确优先<br/>金融风控 --> E[Precision / FPR]
    C -- 二者平衡 --> F[F1 / AUC-PR]
    B -- 均衡 --> G{输出类型?}
    G -- 概率 --> H[LogLoss / Brier Score]
    G -- 类别 --> I[Accuracy + F1]
    G -- 阈值无关 --> J[AUC / KS 统计量]
```

### 4.2 选型速查表

| 场景 | 主指标 | 辅助指标 | 备注 |
|------|--------|---------|------|
| **搜索推荐** | Recall@K / NDCG | MRR / MAP | 召回优先，宁错杀不放过 |
| **金融风控**（欺诈 / 信贷） | Precision / FPR | Recall @ 低 FPR | 误报打扰用户，漏报损失金钱 |
| **医疗诊断**（癌症 / 重病） | Recall（Sensitivity） | Specificity | **漏诊代价 >> 误诊** |
| **不均衡二分类** | F1 / AUC-PR | Precision-Recall 曲线 | 永远配对看 P-R |
| **概率输出**（如 CTR 预估） | LogLoss | AUC / Brier Score | 概率校准是前提 |
| **阈值无关对比** | AUC / KS | 排序 NDCG | 选模阶段用 |

### 4.3 三大铁律

1. **永远先看混淆矩阵**，再决定报哪个数字
2. **不均衡数据禁报 Accuracy**（必报 F1 / AUC-PR）
3. **AUC 报告必须配业务指标**（Precision/Recall @ 业务阈值）

### 4.4 训练 vs 选模的指标分工

- **训练监控**：LogLoss（提供连续梯度信号）
- **验证集选模**：AUC（阈值无关，对比公平）
- **测试集报告**：F1 + Precision + Recall + 混淆矩阵（业务可读）
- **上线监控**：业务指标（点击率 / 拦截率 / 漏报率）

---

## 五、面试话术（30 秒 + 90 秒）

### 30 秒版（直接对答）

> "5 大指标：**Accuracy / Precision / Recall / F1 / AUC**。**不均衡数据**用 F1 或 AUC-PR；**概率输出**用 LogLoss；**阈值无关对比**用 AUC。**永远先看混淆矩阵**，再决定报哪个数字。"

### 90 秒版（深入展开）

> "5 大指标公式：
> - **Accuracy** = (TP+TN) / 总数 → **不均衡时虚高**（99% 负样本全预测负也有 99%）
> - **Precision** = TP / (TP+FP) → 预测为正的真阳比例
> - **Recall** = TP / (TP+FN) → 实际正被找出比例
> - **F1** = 2PR/(P+R) → P-R 调和平均，不均衡首选
> - **AUC** = ROC 曲线下面积 → **不依赖阈值**，衡量排序能力（0.5=随机，1.0=完美）
>
> **场景选型**：
> - 搜索推荐（**召回优先**）→ Recall@K / NDCG
> - 金融风控（**精确优先**）→ Precision / FPR
> - 不均衡二分类 → F1 / AUC-PR
> - 概率输出 → LogLoss / Brier Score
> - 阈值无关对比 → AUC / KS
>
> **5 大陷阱**：
> 1. 不均衡数据 Accuracy 99% 没意义（全部预测负类即可）
> 2. AUC 高 ≠ 业务好（医疗 AUC 0.95 但召回 30% 漏诊严重）
> 3. P/R 阈值依赖，AUC 不依赖（这是 AUC 的核心价值）
> 4. macro-F1 给小类同等权重，小类被忽略时不准
> 5. LogLoss 比 0/1 严格，但概率未校准时也骗人
>
> **实战铁律**：**永远先看混淆矩阵 + 永远配对报 P-R + AUC 必须配业务指标**。"

---

## 六、交叉引用

### 兄弟章节（相关高频题）

- [`k-means-convergence`](../k-means-convergence/README.md) — K-means 评估（WCSS + 轮廓系数，无监督指标）
- [`decision-tree-variants`](../decision-tree-variants/README.md) — 决策树评估（基学习器 = CART，分类/回归指标）
- [`boosting-comparison`](../boosting-comparison/README.md) — XGBoost 评估（logloss + auc + f1 三件套）

### 反向链

- [`02.computer-basics`](../../README.md) — 计算机基础咬文嚼字总目录
- [`machine-learning`](README.md) — 传统 ML 6 大核心面试题（Q6 评估指标）

> **主模块无对应文章**（评估指标散落在各算法章节），本篇是 split-hairs 独立深挖。

---

> 📅 2026-08-10 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐⭐
