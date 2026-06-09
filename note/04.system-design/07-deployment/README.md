# 部署与运维篇

> 系统的部署、监控与容量规划是保障服务持续运行的最后一道防线。

> 最后更新: 2026-06-09

## 目录

1. [部署架构与发布策略](deploy/README.md) — 部署架构（单机/多实例/容器化/K8s/Serverless）与发布策略（蓝绿/金丝雀/滚动/A-B Test/灰度/影子流量/Feature Flag）
2. [可观测性](observability/README.md) — Metrics + Logs + Traces 三大支柱 + SLO/SLI/Error Budget
3. [容量规划与压测](capacity-planning/README.md) — 压测方法论、容量估算模型、状态服务容量规划

## 学习路径

- **第 1 步：部署架构**：理解从单机到 Kubernetes、Serverless 的演进与权衡
- **第 2 步：发布策略**：掌握蓝绿、金丝雀、滚动、A/B 等发布模式与适用场景
- **第 3 步：可观测性**：建立 Metrics + Logs + Traces 三大支柱，配合 SLO 体系驱动工程决策
- **第 4 步：容量规划**：从压测到容量估算，再到弹性伸缩策略
