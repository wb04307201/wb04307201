<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/01-ml
  type: index-only
  category: AI 基础索引
  summary: 传统机器学习算法——监督学习、无监督学习与强化学习的核心方法与演进脉络。
-->

# 01. 传统机器学习

## 📍 一句话定位

> 经典算法的基座——从监督学习（KNN / 决策树 / SVM）到无监督学习（K-means / PCA），再到强化学习（DQN / PPO / SAC），构建 AI 入门的全景认知。

## 🎯 子模块简介

`01-ml/` 聚焦**深度学习崛起之前的机器学习范式**，覆盖三大类算法与对应的工程场景：

- **监督学习（Supervised Learning）**：KNN、决策树、SVM、朴素贝叶斯、线性 / 逻辑回归——用标注数据学习 X→y 的映射；典型任务为分类（图像识别）与回归（房价预测）。
- **无监督学习（Unsupervised Learning）**：K-means、PCA、高斯混合模型（GMM）——从无标签数据挖掘隐结构；典型任务为聚类（用户分群）与降维（特征压缩）。
- **强化学习（Reinforcement Learning）**：DQN、PPO、SAC、Actor-Critic 家族——智能体通过"试错 + 奖励"与环境交互学习最优策略；典型场景为自动驾驶、游戏 AI、机器人控制。

本节是整个 AI 基础层的"地基"。理解传统 ML 才能真正回答"为什么深度学习在 2012 年后崛起"、"为什么 GPU 改变了 AI 格局"等根本问题。

## 🗂️ 文章清单

| 标题 | 路径 | 状态 | 摘要 |
|------|------|------|------|
| 监督学习 → 强化学习 | [ml-to-rl.md](./ml-to-rl.md) | ✅ 已完成（152 行） | 以自动驾驶为例，梳理监督学习 → 无监督学习 → 强化学习的演进、融合架构与安全探索。 |
| KNN 原理 | [knn.md](./knn.md) | ⏳ 待补 | KNN 距离度量（欧氏 / 曼哈顿 / 余弦）/ KD-Tree 加速 / 维度灾难 / 工业级替代品（Faiss, Annoy） |
| 决策树剪枝 | [decision-tree-pruning.md](./decision-tree-pruning.md) | ⏳ 待补 | 预剪枝 vs 后剪枝 / 信息增益 / Gini 系数 / 经典面试题（连续值处理、缺失值处理） |

> **覆盖说明**：当前 `01-ml/` 仅沉淀 1 篇（ml-to-rl.md），覆盖监督 / 无监督 / 强化学习的演进认知；KNN 与决策树是面试高频算法，建议尽快补齐。

## 🔗 关联主题

- **父模块**：[08.ai-foundations](../README.md) — AI 基础层总索引
- **同模块相邻**：[02-deep-learning](../02-deep-learning/README.md) — 深度学习框架选型与训练范式
- **跨模块应用**：[11.ai/automotive](../11.ai/automotive/) — 自动驾驶 ML 实战案例
- **咬文嚼字**：[13.split-hairs/19.ml-algorithms](../12.interview/19.ml-algorithms/) — 传统 ML 面试高频题
- **项目沉淀**：[file-view](https://github.com/wb04307201/file-view) — 传统 ML 工业级应用

## 📚 学习路径

1. **入门**：阅读 [ml-to-rl.md](./ml-to-rl.md)，建立"监督 → 无监督 → 强化"三范式的演进认知
2. **算法深挖**：补充 KNN / 决策树 / SVM 三大经典算法专题（建议先 KNN 原理）
3. **聚类与降维**：补充 K-means / PCA / GMM，对应无监督学习章节
4. **强化学习**：阅读 DQN / PPO / SAC 算法综述，理解 MDP 与策略梯度
5. **面试刷题**：跳转 [13.split-hairs/19.ml-algorithms](../12.interview/19.ml-algorithms/) 巩固核心题
6. **工程落地**：跳转 [11.ai/automotive](../11.ai/automotive/) 看工业级 ML 流水线

## 📊 本节统计

- **子目录总数**：1 个（01-ml/）
- **已沉淀文章**：1 篇（ml-to-rl.md）
- **待补占位**：2 篇（KNN 原理 / 决策树剪枝）
- **总行数**（不含 README）：约 152 行
- **最后更新**：2026-08-20

---

← [返回 08.ai-foundations](../README.md)
