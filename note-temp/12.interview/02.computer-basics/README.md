<!--
module:
  parent: split-hairs
  slug: 02.computer-basics
  type: article
  category: 高频面试题
  summary: 计算机基础高频面试题（网络 / TCP / HTTP / 操作系统）
question:
  id: 02.computer-basics-02.computer-basics
  topic: 02.computer-basics
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [02.computer-basics, network, TCP]
-->

# 计算机基础咬文嚼字

> 计算机基础高频面试题与细节深挖，对齐主模块 [`02.computer-basics`](../../../note/02.computer-basics/)。

---

## 文章清单（共 6 题，find 校对 2026-07-19）

### 网络与协议
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [TCP 三次握手四次挥手](tcp-handshake-teardown/) | ⭐⭐⭐⭐ | 状态机 + 10 个深挖问题 + TIME_WAIT/CLOSE_WAIT |
| 🆕 [单端口多进程监听](port-reuse-so-reuseport/) | ⭐⭐⭐⭐ | SO_REUSEADDR vs SO_REUSEPORT + Linux 3.9 内核 hash 行为 + 5 大实战场景（Nginx/Envoy/K8s/gRPC）+ 90 秒话术 |
| 🆕 [SSE vs WebSocket](sse-vs-websocket/) | ⭐⭐⭐⭐ | AI 对话为什么选 SSE + 5 维对比 + 4 大理由 + 系统设计 |

### 字符串算法
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| **🆕 [高并发敏感词过滤](sensitive-word-filter/)** | ⭐⭐⭐⭐⭐ | AC 自动机 + Bloom + Caffeine + 分布式 100w QPS 完整方案 + 7 道 Q&A |

### 算法设计
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| **🆕 [贪心算法](greedy-algorithms/)** | ⭐⭐⭐⭐ | 贪心选择性质证明 + 交换论证 + 5 大经典题 + 5 大失效反模式 + 贪心 vs DP 决策 + 90 秒话术 |
| **🆕 传统机器学习 6 大算法**（已拆分为单点 deep-dive） |||
| &nbsp;&nbsp;└ [K-means 收敛性 + K-means++](machine-learning/k-means-convergence/) | ⭐⭐⭐ | WCSS 收敛证明 + K-means++ D² 概率 + 4 大反直觉陷阱 |
| &nbsp;&nbsp;└ [决策树 ID3/C4.5/CART](machine-learning/decision-tree-variants/) | ⭐⭐⭐ | 信息增益 vs 信息增益率 vs Gini 公式对比 + 5 大陷阱 |
| &nbsp;&nbsp;└ [梯度下降 SGD/BGD/Adam/AdamW](machine-learning/gradient-descent-variants/) | ⭐⭐⭐ | Adam 完整公式 + AdamW 权重衰减解耦 + 5 大陷阱 + LLM 训练标配 |
| &nbsp;&nbsp;└ [PCA 数学本质 + SVD](machine-learning/pca-math/) | ⭐⭐⭐⭐ | 拉格朗日推导 + 协方差特征向量 + 6 大陷阱（标准化/无监督/线性等） |
| &nbsp;&nbsp;└ [XGBoost/LightGBM/CatBoost 横评](machine-learning/boosting-comparison/) | ⭐⭐⭐⭐ | XGBoost 二阶泰勒 + LightGBM 直方图/leaf-wise + CatBoost ordered boosting + 选型决策树 |
| &nbsp;&nbsp;└ [分类评估指标 5 大金刚](machine-learning/classification-metrics/) | ⭐⭐⭐ | 准确率/精确率/召回率/F1/AUC + 不均衡陷阱 + 场景化选型 |

---

## 相关章节

- 主模块：[`note/02.computer-basics`](../../../note/02.computer-basics/) — 计算机基础知识体系
- 算法深度：[`02-algorithms/string-algorithms`](../../../note/02.computer-basics/02-algorithms/string-algorithms/README.md) —— Trie / KMP / AC 自动机 4 文件 1092 行
- 高并发实战：[`04.system-design/04-high-performance/sensitive-word-filter`](../../../note/04.system-design/04-high-performance/sensitive-word-filter/README.md) —— 5 文件 1085 行
- 应用场景：[`08.application-systems/cms`](../../../note/08.application-systems/01-rd-innovation/cms/README.md) —— CMS 内容审核
- 相关：[`01.java`](01.java/)（Java 并发 / JVM）/ [`04.system-design`](04.system-design/)（系统设计）

← [返回咬文嚼字（高频面试题）](../README.md)
