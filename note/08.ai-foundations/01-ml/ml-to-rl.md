<!--
module:
  parent: 08.ai-foundations/01-ml
  slug: 08.ai-foundations/01-ml/ml-to-rl
  type: article
  category: 主模块子文章
  summary: 从监督学习到强化学习的范式跃迁——数学骨架、算法谱系、融合架构与具身智能演进。
  depth: ⭐⭐⭐⭐⭐
-->

# 监督学习 → 强化学习

> **一句话定位**：从「被动模仿」到「主动决策」的 AI 范式跃迁——监督学习（SL）长于感知与标注映射，强化学习（RL）长于动态决策与长期奖励，二者**分层融合**是自动驾驶、LLM 对齐（RLHF）、AlphaFold 等具身智能的工程路径。

> ⬅️ [返回传统机器学习](../README.md)

> 当自动驾驶汽车在暴雨中识别模糊的车道线，或在无保护左转时与对向车流"默契"交互——背后正是一场从"被动模仿"到"主动决策"的 AI 范式革命。

---

## 🎯 学习目标

完成本文后，你能够：

- **数学骨架**：用 MDP 五元组 + Bellman 方程 + 策略梯度 3 个公式解释 RL
- **算法谱系**：区分 DQN / PPO / SAC / A3C 4 大主流算法的适用场景
- **融合范式**：理解"SL + RL"分层架构在自动驾驶、LLM 对齐中的实战
- **反直觉**：识别 5 大误区（如"RL > SL"、"RL 不需要数据"）

---

## 📚 章节清单

| 章节 | 核心内容 | 阅读时长 |
|------|---------|---------|
| **01 引言与历史脉络** | 监督学习瓶颈 + 强化学习崛起 | 10 min |
| **02 监督学习：精准感知的基石** | 数学骨架 + 4 大算法 + 案例 | 15 min |
| **03 无监督学习：挖掘隐结构** | K-means / PCA / GMM | 10 min |
| **04 强化学习：在交互中学会思考** | MDP + Bellman + 算法谱系 | 25 min |
| **05 融合之道：SL + RL 分层架构** | 模仿学习 + 分层决策 + RLHF | 20 min |
| **06 神经网络架构演进** | CNN / RNN / GNN / World Models | 15 min |
| **07 未来趋势与具身智能** | World Models / Sim2Real / Safe RL | 15 min |
| **08 反直觉与误区** | 5 大高频认知偏差 | 10 min |

---

## 一、引言：为何需要超越监督学习？

在 AI 演进长河中，监督学习曾是无可争议的主角：它通过海量标注数据教会机器"是什么"。然而，当应用场景从静态识别转向**动态决策**——如自动驾驶面对突发施工路段、机器人在未知环境中导航——监督学习的局限性日益凸显：

> **标注数据无法穷尽现实世界的无限可能性**。

```text
监督学习的"长尾困境"：

训练分布：
[晴天: 95%] [雨天: 4%] [雪天: 1%] [沙尘暴: 0.001%]

模型在训练分布外的表现：
- 长尾场景（罕见）：错误率 > 50%
- 极端天气：模型"没见过"，输出随机
```

**核心矛盾**：

| 维度 | 监督学习 | 现实需求 |
|------|---------|----------|
| 数据 | 静态、有限 | 动态、无限 |
| 决策 | 一次性映射（输入→输出）| 序贯决策（动作→环境→奖励）|
| 反馈 | 即时 loss | 延迟 reward |
| 长尾 | 训练分布外失效 | 必须泛化到未知 |

本文系统梳理从监督学习到强化学习的技术跃迁，解析二者融合的前沿实践，并展望下一代智能体的进化方向。

---

## 二、监督学习：精准感知的基石

### 2.1 数学骨架

监督学习依赖**输入-输出对**的标注数据 $(\mathbf{x}_i, y_i)$ 训练，本质是学习从观测到行为的映射函数：

$$
\hat{f} = \arg\min_{f \in \mathcal{F}} \frac{1}{n} \sum_{i=1}^{n} L\big(f(\mathbf{x}_i), y_i\big)
$$

其中 $L(\cdot, \cdot)$ 是损失函数（MSE 用于回归、Cross-Entropy 用于分类）。

**算法的差异**主要体现在**假设空间 $\mathcal{F}$**：

- 线性回归 → 线性函数空间
- SVM → 带 margin 的超平面
- KNN → 局部插值空间
- 决策树 → 分段常数函数
- 神经网络 → 多层非线性变换

### 2.2 4 大算法与适用场景

| 算法 | 核心思想 | 优势 | 劣势 | 自动驾驶应用 |
|------|----------|------|------|--------------|
| **线性回归** | 最小化 MSE | 简单、可解释 | 只能建模线性 | 预测油门与加速度关系 |
| **决策树** | 特征阈值分层 | 可解释、不需归一化 | 易过拟合 | 简单场景变道决策 |
| **SVM** | 最优分类超平面 | 高维小样本强 | 大规模慢 | 交通标志二分类 |
| **朴素贝叶斯** | 贝叶斯定理概率分类 | 训练快、概率输出 | 假设特征独立 | 传感器融合置信度加权 |
| **深度神经网络** | 多层非线性变换 | 表达力强 | 需大量数据 + 黑盒 | 端到端感知 |

### 2.3 实战案例：车道保持系统

在 CARLA 仿真环境中，研究者用 **LSTM** 处理连续图像序列，直接回归方向盘转角：

```python
# 简化版 LSTM 车道保持
class LaneKeepingLSTM(nn.Module):
    def __init__(self, cnn_feature_dim=512, lstm_hidden=128):
        super().__init__()
        self.cnn = models.resnet18(pretrained=True)  # 视觉特征
        self.cnn.fc = nn.Identity()  # 去掉最后分类层
        self.lstm = nn.LSTM(cnn_feature_dim, lstm_hidden, batch_first=True)
        self.head = nn.Linear(lstm_hidden, 1)  # 输出转角

    def forward(self, image_seq):  # (B, T, 3, H, W)
        B, T = image_seq.size(0), image_seq.size(1)
        # 每帧提特征
        features = self.cnn(image_seq.view(B*T, 3, 224, 224))  # (B*T, 512)
        features = features.view(B, T, -1)
        # LSTM 时序建模
        lstm_out, _ = self.lstm(features)
        # 输出最终时刻转角
        return self.head(lstm_out[:, -1, :])  # (B, 1)
```

**实验结果**：

- 训练数据：10 万帧人类驾驶视频
- 晴天场景：转向误差 < 0.1 度
- 强眩光场景：性能骤降 **30%**

**暴露的致命短板**：**泛化能力受限于训练数据分布**。

### 2.4 监督学习的局限性

1. **标注成本高昂**：1 小时高质量驾驶数据标注需 8-10 人工时
2. **长尾场景覆盖不足**：突发障碍物、极端天气等罕见事件难以采集足够样本
3. **缺乏因果推理**：模型学会"相关性"而非"因果性"（如将"雨刮器开启"误判为"下雨"的充要条件）
4. **决策能力缺失**：只能输出"是什么"，不能输出"该怎么做"

---

## 三、无监督学习：挖掘数据的隐性结构

作为监督学习的补充，无监督学习在无标签数据中发现模式：

### 3.1 3 大经典方法

| 算法 | 目标 | 数学本质 | 应用 |
|------|------|---------|------|
| **K-means** | 聚类 | 最小化 $J = \sum_k \sum_{\mathbf{x} \in C_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|^2$ | 驾驶行为分群（激进/保守） |
| **PCA** | 降维 | 协方差矩阵特征分解 $\boldsymbol{\Sigma} = \mathbf{W} \boldsymbol{\Lambda} \mathbf{W}^\top$ | 高维传感器压缩 |
| **GMM** | 密度估计 | EM 算法拟合多高斯混合 | 交通流多模态分布建模 |

### 3.2 实战案例：自动驾驶数据预处理

```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# 1. PCA 降维：128 维雷达点云 → 32 维
pca = PCA(n_components=32)
radar_features_compressed = pca.fit_transform(radar_features)

# 2. K-means 聚类驾驶行为
kmeans = KMeans(n_clusters=4)  # 4 种驾驶风格
driving_styles = kmeans.fit_predict(driving_trajectories)

# 输出："激进型"、"稳健型"、"保守型"、"激进+稳健"
```

> **注**：无监督学习在感知层提供数据预处理支持，但难以直接生成决策行为，因此在自动驾驶中多作为辅助技术。

---

## 四、强化学习：在交互中学会"思考"

### 4.1 核心原理

强化学习（RL）让智能体通过**环境交互**学习策略：

$$
\text{执行动作} \rightarrow \text{环境反馈} \rightarrow \text{更新策略} \rightarrow \text{更优动作} \rightarrow \cdots
$$

**数学本质**：求解**马尔可夫决策过程（MDP）**：

$$
\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)
$$

- $\mathcal{S}$：状态空间（如自车位置 + 周围车辆 + 车道线）
- $\mathcal{A}$：动作空间（方向盘转角、油门、刹车）
- $P(s'|s, a)$：状态转移概率
- $R(s, a)$：奖励函数
- $\gamma \in [0, 1]$：折扣因子（未来奖励的衰减）

**目标**：最大化长期累积奖励

$$
G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k}
$$

### 4.2 Bellman 方程

**状态价值函数** $V^\pi(s)$：在状态 $s$ 遵循策略 $\pi$ 的期望回报：

$$
V^\pi(s) = \mathbb{E}_\pi \left[ \sum_{k=0}^{\infty} \gamma^k r_{t+k} \mid s_t = s \right]
$$

**Bellman 方程**：

$$
V^\pi(s) = \sum_{a} \pi(a \mid s) \sum_{s', r} p(s', r \mid s, a) \left[ r + \gamma V^\pi(s') \right]
$$

**Bellman 最优方程**：

$$
V^*(s) = \max_{a} \mathbb{E}_{s', r} \left[ r + \gamma V^*(s') \mid s, a \right]
$$

### 4.3 算法谱系：3 大流派

| 类型 | 代表算法 | 核心思想 | 优点 | 缺点 | 适用场景 |
|------|----------|----------|------|------|----------|
| **值函数法** | DQN | 用神经网络逼近 Q 值 | 离散动作友好 | 不稳定、max 1 | Atari 游戏、离散决策 |
| **策略梯度法** | REINFORCE / PPO | 直接优化策略 | 连续动作、稳定 | 高方差 | 连续控制（自动驾驶） |
| **Actor-Critic** | A3C / SAC | 值函数 + 策略梯度融合 | 样本效率高、稳定性好 | 调参复杂 | 复杂动态环境 |

#### 4.3.1 DQN（2013，DeepMind）—— 离散动作

**创新**：用神经网络逼近 Q 值 + Experience Replay + Target Network。

```python
import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, state_dim, n_actions):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, n_actions)  # 输出每个动作的 Q 值
        )

    def forward(self, state):
        return self.net(state)

# 训练
q_net = DQN(state_dim=128, n_actions=4)  # 4 个离散动作
target_net = DQN(state_dim=128, n_actions=4)
optim = torch.optim.Adam(q_net.parameters(), lr=1e-4)

for step, (s, a, r, s_next, done) in enumerate(replay_buffer):
    # 当前 Q 值
    q_pred = q_net(s).gather(1, a.unsqueeze(1))

    # TD target
    with torch.no_grad():
        q_next = target_net(s_next).max(dim=1, keepdim=True)[0]
        q_target = r.unsqueeze(1) + gamma * q_next * (1 - done.float().unsqueeze(1))

    # MSE Loss
    loss = ((q_pred - q_target) ** 2).mean()
    optim.zero_grad()
    loss.backward()
    optim.step()
```

#### 4.3.2 PPO（2017，OpenAI）—— 连续动作

**核心**：限制策略更新幅度（clip ratio 0.1-0.2）。

$$
\mathcal{L}^{CLIP}(\theta) = \mathbb{E}_t \left[ \min \left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{old}}(a_t \mid s_t)}$ 是重要性采样比。

**应用**：ChatGPT 的 RLHF 第一步、机器人控制、自动驾驶。

#### 4.3.3 SAC（2018，UC Berkeley）—— 最大熵 + 连续动作

**核心**：在最大化奖励的同时最大化策略熵（鼓励探索）。

### 4.4 优势与挑战

**优势**：

- ✅ **无需标注数据**：通过试错自主探索，适应未知场景（如雪地打滑时的反向打舵）
- ✅ **长期规划能力**：权衡即时奖励与未来收益（如"减速让行"换取后续畅通）

**挑战**：

- ⚠️ **样本效率低**：真实车辆训练成本高，需依赖仿真（Wayve / CARLA）
- ⚠️ **奖励设计困境**：不合理的奖励函数导致"奖励黑客"（如为避免碰撞而急刹引发追尾）
- ⚠️ **安全边界模糊**：探索过程可能产生危险行为

### 4.5 实战案例：PRIMEDrive-CoT 框架

该框架将**思维链（Chain-of-Thought）推理**融入强化学习，在无保护左转场景中：

1. 智能体首先**推理对向车辆意图**（"减速→可能让行"）
2. **评估自身行动风险**（"加速通过"的碰撞概率）
3. 选择最优时机切入

在 nuPlan 数据集测试中，该方法将误判率降低 **30%**，证明**结构化推理可显著提升 RL 的决策可解释性**。

---

## 五、融合之道：SL + RL 的协同架构

单一范式难以应对复杂现实，产业界正走向"分层融合"。

### 5.1 模仿学习（Imitation Learning）

#### 5.1.1 行为克隆（BC）

用监督学习复现专家数据，快速获得基础能力：

```python
# 行为克隆
expert_dataset = load_expert_demos()  # (state, action) 对
policy = PolicyNetwork()

for state, action in expert_dataset:
    pred_action = policy(state)
    loss = ((pred_action - action) ** 2).mean()
    loss.backward()
```

**问题**：分布偏移（distribution shift）—— 累积误差导致模型偏离专家分布。

#### 5.1.2 DAgger 算法

**核心**：在交互中持续收集专家纠正数据，缓解分布偏移：

```text
Round 1: 用 BC 训练 policy π_1
Round 2: 用 π_1 跑仿真，遇到状态让专家标注正确 action
Round 3: 用累积数据集训练 π_2
...
直到 policy 表现稳定
```

> **案例**：Waymo 初期用人类驾驶数据训练基础策略，再通过 RL 在仿真中优化边缘场景。

### 5.2 分层决策架构

```text
┌─────────────────────────────────────┐
│  高层：强化学习（任务规划）          │
│  • 路径选择 • 社会交互 • 风险权衡    │
│  • 输出："超车" / "减速让行" / "停车"│
└──────────────┬──────────────────────┘
               │ 动作指令（离散）
┌──────────────▼──────────────────────┐
│  低层：监督学习/经典控制（执行）     │
│  • 车道保持 • 速度跟踪 • PID控制     │
│  • 输出：方向盘转角、油门开度       │
└─────────────────────────────────────┘
```

> **优势**：高层专注"做什么"（宏观决策），低层专注"怎么做"（精确控制），**解耦复杂度**。

### 5.3 LLM 对齐中的 RL—— RLHF / DPO

RLHF（Reinforcement Learning from Human Feedback）是**SL + RL 分层架构**在 LLM 时代的最大成果：

```text
┌─────────────────────────────────────────────┐
│ Stage 1：监督学习（SFT）                    │
│ • 输入：(prompt, human-written response)    │
│ • 训练：语言模型模仿人类示范                 │
│ • 输出：基础对话模型                         │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ Stage 2：奖励模型（Reward Model）            │
│ • 输入：(prompt, response_A, response_B)    │
│ • 人类标注：A vs B 哪个更好                 │
│ • 训练：学习人类偏好 → 标量奖励              │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ Stage 3：强化学习（PPO）                    │
│ • 输入：prompt → SFT 模型生成 response      │
│ • 奖励：Reward Model 给分                    │
│ • 训练：PPO 优化 LLM 最大化奖励              │
│ • 输出：Aligned LLM                         │
└─────────────────────────────────────────────┘
```

**DPO（2024，斯坦福）**：**简化版本**，直接用偏好数据优化策略，无需奖励模型：

$$
\mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l) \sim D} \log \sigma \left( \beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right)
$$

其中 $y_w$ 是偏好 response，$y_l$ 是不偏好 response。

---

## 六、神经网络架构演进：从感知到推理

| 架构 | 核心能力 | 自动驾驶应用 | 局限 |
|------|----------|--------------|------|
| **CNN** | 局部特征提取 | 交通标志识别（YOLOv5） | 不能建模长程依赖 |
| **RNN / LSTM** | 时序建模 | 预测行人轨迹（5s 历史） | 长序列梯度消失 |
| **GAN** | 数据生成 | 合成极端天气图像 | 训练不稳定 |
| **GNN** | 关系推理 | 建模车辆-行人-信号灯拓扑 | 计算复杂度高 |
| **贝叶斯 GNN** | 不确定性量化 | 输出预测置信度 | 推理慢 |
| **Transformer** | 全局注意力 | BEV 感知、轨迹预测 | O(n²) 复杂度 |
| **World Model** | 预测未来状态 | Wayve GAIA-1 | 训练数据需求大 |

**关键趋势**：

- **从"特征提取器"转向"世界模型"**——不仅感知现状，更预测未来状态演化
- **从"模块化"转向"端到端"**——感知-决策一体化（如 Tesla FSD v12）
- **从"规则驱动"转向"数据驱动"**——LLM/VLM 作为决策大脑

---

## 七、未来趋势：下一代智能体的三大方向

### 7.1 世界模型（World Models）

智能体内部构建环境动态模型，实现"想象式规划"。

**Wayve GAIA-1（2023）**：仅通过视觉输入即可预测 **10 秒后**的道路状态，大幅降低真实交互需求。

```python
# 简化版世界模型
class WorldModel(nn.Module):
    def __init__(self, obs_dim, action_dim, hidden_dim=512):
        super().__init__()
        self.encoder = nn.Sequential(...)  # 编码观测
        self.dynamics = nn.Sequential(...)  # 预测下一状态
        self.decoder = nn.Sequential(...)  # 解码预测图像

    def predict(self, obs, action):
        z = self.encoder(obs)
        z_next = self.dynamics(z, action)  # 预测下一隐状态
        obs_next = self.decoder(z_next)  # 解码为图像
        return obs_next
```

**意义**：

- 在"想象"中训练策略，**避免真实世界试错成本**
- 数据效率提升 10-100x

### 7.2 仿真-现实迁移（Sim2Real）

```text
┌─────────────────────────────────────┐
│  仿真（Sim）                         │
│  • CARLA / Waymax / nuPlan          │
│  • 1 GPU 跑 1 个月 = 1000 万公里    │
│  • 完美 ground truth                │
└──────────────┬──────────────────────┘
               │ 迁移
┌──────────────▼──────────────────────┐
│  现实（Real）                        │
│  • 真实车辆路测                      │
│  • 1 辆测试车跑 1 年 = 100 万公里   │
│  • 罕见场景、传感器噪声               │
└─────────────────────────────────────┘
```

**关键技术**：

1. **域随机化（Domain Randomization）**：在仿真中随机化光照/纹理/物理参数，提升泛化性
2. **神经辐射场（NeRF）**：构建高保真数字孪生，缩小仿真与现实差距
3. **数字孪生**（Digital Twin）：1:1 复现真实环境

**目标**：**90% 训练在仿真完成，仅 10% 真实路测用于校准**。

### 7.3 安全对齐（Safe Alignment）

1. **约束强化学习（CRL, Constrained RL）**：将安全规则编码为约束条件（如"横向加速度 < 0.3g"）
2. **逆向强化学习（IRL）**：从人类示范中反推隐式安全偏好

**核心挑战**：如何在**探索与安全**间取得平衡？

---

## 八、5 大反直觉点

### 误区 1：❌ RL 比 SL 更强

**真相**：**RL 不比 SL 强，是不同场景的互补**

- SL 强在感知、标注数据充足场景（人脸识别、机器翻译）
- RL 强在序贯决策、长尾场景（自动驾驶、游戏、机器人）
- **工程现实**：90% 的 AI 系统用 SL，10% 用 RL，融合架构（SL+RL）是趋势

### 误区 2：❌ RL 不需要数据

**真相**：**RL 需要大量仿真交互数据**

- 真实环境：成本极高（自动驾驶每真实路测 1 万公里需 $100 万）
- **仿真数据**：1 GPU 跑 1 个月可生成等效 1000 万公里数据
- RL 训练量 = 仿真数据规模（远大于 SL 标注数据）

### 误区 3：❌ DQN / PPO 等算法通用

**真相**：**不同算法适用不同场景**

| 算法 | 适用 | 不适用 |
|------|------|--------|
| DQN | 离散动作、低维状态 | 连续动作（自动驾驶方向盘）|
| PPO | 通用、连续控制 | 大规模（样本效率低）|
| SAC | 连续控制 + 探索 | 离散动作 |
| AlphaZero | 完美信息博弈 | 真实世界（无完整 simulator）|

### 误区 4：❌ 奖励函数 = 业务目标

**真相**：**奖励黑客（Reward Hacking）问题**

```text
设计奖励："到达目的地 + 不碰撞"

错误行为：
- 永远在原地不动 → 不碰撞 + 不到达（最大化 safety）
- 撞墙后被弹出 → 不碰撞（短期内）
- 高速冲过路口 → "不碰撞"概率高但实际危险

→ 智能体学会了"绕过规则"
```

**解决**：多目标奖励 + 人工评估 + 安全性约束（CRL）

### 误区 5：❌ RLHF 是 LLM 对齐的终极方案

**真相**：**DPO / Constitutional AI / RLAIF 是 RLHF 的演进和替代**

- **RLHF**（2022）：OpenAI InstructGPT 用 PPO + 奖励模型
- **DPO**（2024）：直接优化偏好，无需奖励模型，训练稳定 2-3x
- **Constitutional AI**（Anthropic 2023）：用规则约束代替人类标注
- **RLAIF**（Google 2023）：用 LLM 评判替代人类标注

**趋势**：**RLHF 仍是主流，但 DPO / Constitutional AI 是重要替代**

---

## 九、跨模块反向链（10+）

| 主题 | 链接 |
|------|------|
| **深度学习框架（PyTorch 实现 RL）** | [08.ai-foundations/02-deep-learning/deep-learning-frameworks](../02-deep-learning/deep-learning-frameworks.md) |
| **LLM 基础** | [08.ai-foundations/04-llm/llm-basics](../04-llm/llm-basics.md) |
| **Dropout 实证** | [08.ai-foundations/04-llm/dropout-in-llm/single-epoch-and-config-evidence](../04-llm/dropout-in-llm/single-epoch-and-config-evidence.md) |
| **Embedding** | [08.ai-foundations/05-tokenization-embedding/embedding](../05-tokenization-embedding/embedding.md) |
| **RLHF / DPO 算法** | [09.ai-applications/llm-alignment](../09.ai-applications/llm-alignment/) |
| **Agent 架构** | [09.ai-applications/agent/agent-architecture](../09.ai-applications/agent/agent-architecture/) |
| **多智能体系统** | [12.interview/11.ai/multi-agent-system-design](../12.interview/11.ai/multi-agent-system-design/) |
| **故事：自动驾驶** | [13.story/01-ai-agent-architecture](../../13.story/01-ai-agent-architecture.md) |
| **故事：AI 学习悖论** | [13.story/11-ai-learning-paradox](../../13.story/11-ai-learning-paradox.md) |
| **故事：AI 致命三胞胎** | [13.story/31-ai-fatal-trio](../../13.story/31-ai-fatal-trio.md) |
| **分布式 RL 训练（Ray / RLlib）** | [06.distributed-systems/distributed-training](../06.distributed-systems/distributed-training/) |
| **Wayve / Tesla FSD 案例** | [10.business-systems/autonomous-driving](../10.business-systems/autonomous-driving/) |

---

## 十、面试 Checklist（30 秒话术）

**问题 1：监督学习 vs 强化学习的核心区别？**

- 答：**SL 是静态映射（输入→输出，一次性）；RL 是序贯决策（动作→环境→奖励，长期）**。SL 强感知，RL 强决策。1 行答完。

**问题 2：MDP 的五元组是什么？**

- 答：$(\mathcal{S}, \mathcal{A}, P, R, \gamma)$ — 状态、动作、转移、奖励、折扣。**目标是最大化长期累积奖励** $G_t = \sum \gamma^k r_{t+k}$。1 行答完。

**问题 3：DQN 的 3 大创新？**

- 答：**Q 网络 + Experience Replay + Target Network**，解决值函数逼近不稳定。1 行答完。

**问题 4：RLHF 三阶段？**

- 答：**SFT（监督微调）→ Reward Model（奖励建模）→ PPO（强化学习）**。GPT-4、Claude 都用此对齐。1 行答完。

**问题 5：自动驾驶中如何融合 SL 和 RL？**

- 答：**分层架构**——高层 RL 任务规划（超车/让行），低层 SL 执行（车道保持/PID）。Waymo、Tesla FSD 都在用。1 行答完。

---

## 📚 参考来源

1. **DQN 论文（Atari 深度强化学习）**：Volodymyr Mnih, Koray Kavukcuoglu, David Silver et al. *Playing Atari with Deep Reinforcement Learning*. arXiv 2013. https://arxiv.org/abs/1312.5602
2. **AlphaGo 论文（围棋深度网络与树搜索）**：David Silver, Aja Huang, Chris J. Maddison et al. *Mastering the Game of Go with Deep Neural Networks and Tree Search*. Nature 2016. https://arxiv.org/abs/1603.06955
3. **PPO 论文（近端策略优化）**：John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radon, Oleg Klimov. *Proximal Policy Optimization Algorithms*. arXiv 2017. https://arxiv.org/abs/1707.06347
4. **SAC 论文（柔性 Actor-Critic）**：Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, Sergey Levine. *Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor*. ICML 2018. https://arxiv.org/abs/1801.01290
5. **RLHF 经典（人类偏好强化学习）**：Paul F. Christiano, Jan Leike, Tom B. Brown, Miljan Martic, Shane Legg, Dario Amodei. *Deep Reinforcement Learning from Human Preferences*. NeurIPS 2017. https://arxiv.org/abs/1706.03741
6. **InstructGPT / RLHF**：Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida et al. *Training Language Models to Follow Instructions with Human Feedback*. NeurIPS 2022. https://arxiv.org/abs/2203.02155
7. **DPO（直接偏好优化）**：Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon et al. *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*. NeurIPS 2023. https://arxiv.org/abs/2305.18290
8. **DAgger**：Stéphane Ross, Geoffrey Gordon, Drew Bagnell. *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning*. AISTATS 2011. https://arxiv.org/abs/1011.0686
9. **GAIA-1（Wayve World Model）**：Wayve. *GAIA-1: A Generative World Model for Autonomous Driving*. 2023. https://arxiv.org/abs/2309.17080
10. **Bellman 方程**：Richard E. Bellman. *Dynamic Programming*. 1957.（强化学习奠基）

---

← [返回 传统机器学习](../README.md)