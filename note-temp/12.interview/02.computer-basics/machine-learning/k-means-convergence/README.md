<!--
question:
  id: 02.computer-basics-k-means-convergence
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [ML, K-means, 收敛, K-means++, 局部最优]
-->

# K-means 收敛性与 K-means++：为什么只保证局部最优？

> 一句话定位：K-means 是**唯一一个"必收敛但只收敛到局部最优"**的经典 ML 算法 —— 面试官考察的不是"会不会写 K-means"，而是 **WCSS 收敛性证明** + **K-means++ D² 概率公式** + **n_init=10 的工程含义**。完整深度见 [主模块 K-means 聚类](../../../../../note/02.computer-basics/02-algorithms/clustering/k-means/README.md)。

> **系列定位**：经典 ML 面试题（K-means 必问 Q1）。考察的不是"聚类怎么跑"，而是 **收敛性数学证明** + **初始质心敏感性** + **K-means++ D² 概率公式** + **K 选择的肘部 / 轮廓**。

---

## 引子：100 万用户分 5 群，每次结果都不一样

```text
场景：用户画像团队要把 100 万用户分 5 个客群，跑 K-means 做 RFM 分层。
第 1 次跑：簇 1 是「高价值 + 低频」、簇 2 是「低价值 + 高频」……运营同学很满意。
第 2 次跑（同一份数据 + 同一份代码 + random_state=42）：
簇 1 变成了「高价值 + 高频」——客群定义全乱了。
```

**反直觉现场**：
1. 普通候选人：会写 `KMeans(n_clusters=5).fit(X)`，但**说不清为什么 2 次结果不同**
2. 优秀候选人：知道是**初始质心敏感**导致局部最优，能写出 WCSS 单调下降的证明
3. 资深候选人：能用 **K-means++ D² 概率** 解释为什么 sklearn 默认 init='k-means++'，能用 **n_init=10** 解释为什么"多次跑取最优"是工业标准

---

## 一、核心原理（WCSS 收敛性证明）

### 1.1 目标函数：WCSS（Within-Cluster Sum of Squares）

$$J(C, \mu) = \sum_{i=1}^{n} \| x_i - \mu_{c(i)} \|^2$$

- $C$：样本到簇的分配方案
- $\mu_k$：第 $k$ 个簇的质心（均值）
- $c(i)$：样本 $i$ 所属的簇编号
- **物理含义**：所有样本到各自簇质心的欧式距离平方和（越小 = 簇越紧凑）

### 1.2 K-means 主循环（伪代码）

```python
# 输入：样本 X、簇数 K、迭代次数 T
def kmeans(X, K, T=300):
    mu = init_centroids(X, K)              # ① 初始化质心（关键！）
    for t in range(T):
        C = assign_step(X, mu)             # ② 分配：每个样本 → 最近质心
        mu_new = update_step(X, C, K)      # ③ 更新：质心 = 簇内均值
        if np.allclose(mu, mu_new, atol=1e-4):  # ④ 收敛判断
            break
        mu = mu_new
    return C, mu
```

### 1.3 收敛性证明（3 步链）

```text
① 分配步骤固定 μ，J 不增：
   把 x_i 从 c(i)=k 改到 c(i)=k'，只有当 ||x_i - μ_k'|| ≤ ||x_i - μ_k|| 时才换 → J 单调下降。

② 更新步骤固定 C，J 不增：
   给定簇 C_k，最小化 Σ_{i∈C_k} ||x_i - μ||² 的解是 μ_k = mean(C_k)（均值定理）→ J 最小化。

③ J 有下界（≥ 0） + J 单调不增 + 有限状态空间
   → K-means 必在有限步内收敛（实际通常 5-50 步）。
```

**关键洞察**：K-means **一定收敛**，但收敛到的是**局部最优**（initialization dependent），不是全局最优。**这正是面试官要的"反差点"**——很多候选人误以为 K-means 是凸优化。

---

## 二、代码示例：反例 vs 正例

### 反例：随机选初始质心（容易陷入局部最优）

```python
from sklearn.cluster import KMeans
import numpy as np

X = np.random.randn(1000, 2)

# ❌ 反例：init='random' + n_init=1（默认老版本）
km_bad = KMeans(n_clusters=5, init='random', n_init=1, random_state=42).fit(X)
print(f"WCSS (random init): {km_bad.inertia_:.2f}")  # 可能是局部最优
```

### 正例：K-means++ + n_init=10（工业标准）

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ✅ 正例：先标准化 + K-means++ + n_init=10
X_scaled = StandardScaler().fit_transform(X)
km_good = KMeans(
    n_clusters=5,
    init='k-means++',   # 智能选初始质心（D² 概率）
    n_init=10,           # 跑 10 次取 WCSS 最小的
    max_iter=300,
    random_state=42
).fit(X_scaled)
print(f"WCSS (k-means++): {km_good.inertia_:.2f}")  # 显著更低、更稳定
```

**对比**：同一份数据，K-means++ + n_init=10 的 WCSS 通常比 random init + n_init=1 **低 5-30%**，且**结果稳定**（多次运行方差小）。

---

## 三、常见陷阱（4 个反直觉点）

### 陷阱 1：随机种子固定 ≠ 结果完全可复现

- **真相**：numpy / sklearn 在多核 BLAS 下做浮点求和时，**累加顺序受线程调度影响**（非完全确定性）。设 `random_state=42` 后单线程可复现，但**多线程 / 多机器**仍可能差几个样本的分配。
- **面试话术**：工程上 K-means 的"复现"应靠 **K-means++ + n_init=10 + 固定 random_state + 单线程**（`os.environ['OMP_NUM_THREADS']=1`）。

### 陷阱 2：silhouette_score 高 ≠ 聚类一定好

- **真相**：silhouette 是**几何指标**，衡量"簇内紧 + 簇间离"，**不反映业务语义**。K=3 时 silhouette 0.6 不一定比 K=5 时 0.5 好——可能 K=5 把"高价值 + 中频"细分出来，运营 ROI 更高。
- **面试话术**：K 选择 = **肘部法则（看 WCSS 拐点）+ 轮廓系数（看几何）+ 业务可解释性**——三者综合判断，不是单一指标。

### 陷阱 3：Mini-Batch K-means ≠ 加速版 K-means

- **真相**：Mini-Batch（`sklearn.cluster.MiniBatchKMeans`）每步只用 **batch_size=256~1024** 个样本更新质心，**收敛目标不同**（不是严格 WCSS 最小化，而是局部近似）。**收敛速度通常快 10x，但 WCSS 比标准 K-means 高 1-5%**。
- **面试话术**：大数据用 Mini-Batch（百万级以上），小数据用标准 K-means。Mini-Batch 的 `batch_size` 越大越接近标准 K-means，但越慢。

### 陷阱 4：K-means 假设"球形等大簇"，对环形 / 月牙形失效

- **真相**：K-means 的目标函数是欧式距离平方，**只能发现凸球形等方差簇**。对**环形（同心圆）、月牙形、流形**数据，K-means 会强行切成两半，而 **DBSCAN / Spectral Clustering / GMM** 更合适。
- **面试话术**：聚类算法选型 = **数据形状 + 簇数已知 + 噪声鲁棒性**。K-means 只在"球形 + 等大 + 无噪声 + K 已知"时是首选。

---

## 四、最佳实践

### 4.1 K-means++ 智能选初始质心（D² 概率公式）

```text
D(x) = ||x - 最近已选质心||
P(x 被选为下一个质心) = D(x)² / Σ_{x'} D(x')²
```

**直觉**：离现有质心**越远**的点，被选为下一个质心的概率越大 —— **避免初始质心扎堆**。这是 2007 年 Arthur & Vassilvitskii 的论文，证明 K-means++ 的 WCSS 期望是**最优解的 O(log K) 倍**（理论保证）。

### 4.2 sklearn 推荐参数

| 参数 | 推荐值 | 含义 |
|------|--------|------|
| `init` | `'k-means++'` | 智能初始化（默认） |
| `n_init` | `10` | 跑 10 次取 WCSS 最小（sklearn 默认） |
| `max_iter` | `300` | 最大迭代次数（实际 5-50 步就收敛） |
| `tol` | `1e-4` | 收敛阈值（质心变化量） |
| `algorithm` | `'lloyd'` | 经典 Lloyd 算法（默认） |

### 4.3 数据预处理铁律

- **必须先 `StandardScaler` 标准化**（K-means 是距离-based，量纲差异会主导结果）
- **类别特征先编码**（OneHot / TargetEncoder）
- **高维先降维**（PCA 保留 95% 方差）—— 维度诅咒下 K-means 失效

### 4.4 大数据方案（百万级 +）

- **百万级**：标准 `KMeans`
- **百万级以上**：`MiniBatchKMeans(batch_size=1024, n_init=3)` —— 收敛快 10x，WCSS 高 1-5%
- **千万级以上**：FAISS / cuML（RAPIDS）GPU K-means，或先采样到 100 万

---

## 五、面试话术（30 秒 + 90 秒）

### 30 秒版（直接对答）

> "K-means **一定收敛**——目标函数 WCSS 单调不增且有下界 0（分配步骤不增 + 更新步骤最小化）。但**只收敛到局部最优**，因为不同初始质心可能收敛到不同结果。"

### 90 秒版（深入展开）

> "证明分三步：① 分配步骤固定质心，每个样本分到最近质心 → WCSS 不增；② 更新步骤固定分配，每个簇的均值使子集 WCSS 最小化 → WCSS 下降；③ WCSS ≥ 0 有下界 + 单调不增 → 必在有限步收敛（实际 5-50 步）。
>
> **但局部最优**是核心问题——**初始质心敏感**。工业上有两层缓解：
> 1. **K-means++**（默认）：按 D² 概率选初始质心，离现有质心越远的点越优先被选，避免扎堆；
> 2. **n_init=10**：跑 10 次取 WCSS 最小的结果（sklearn 默认）。
>
> **K 选择**用**肘部法则**（WCSS 拐点）+ **轮廓系数**（silhouette，几何指标）+ 业务可解释性三维判断。**大数据**用 Mini-Batch K-means。**局限**：K-means 只对球形等大簇有效，环形 / 月牙形应用 DBSCAN 或 Spectral Clustering。"

---

## 六、交叉引用

### 主模块深度（理论细节）

- [`02-algorithms/clustering/k-means`](../../../../../note/02.computer-basics/02-algorithms/clustering/k-means/README.md) — 主模块讲 K-means 完整理论（目标函数推导 + Lloyd 算法细节 + sklearn API）

### 兄弟章节（相关高频题）

- [`gradient-descent-variants`](../gradient-descent-variants/README.md) — 梯度下降收敛性（监督学习 vs K-means 无监督的对比）
- [`greedy-algorithms`](../../greedy-algorithms/README.md) — K-means++ 的"贪心选质心"思想 vs 贪心算法证明

### 反向链

- [`02.computer-basics`](../README.md) — 计算机基础咬文嚼字总目录
- [`machine-learning`](README.md) — 传统 ML 6 大核心面试题（Q1 K-means 收敛）

---

> 📅 2026-08-10 · 咬文嚼字 · 02.computer-basics · ⭐⭐⭐ · K-means 收敛 + K-means++