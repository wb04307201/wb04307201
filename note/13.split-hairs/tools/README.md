<!--
module:
  parent: split-hairs
  slug: split-hairs/tools
  type: index
  category: 高频面试题
  summary: 开发工具面试题 — Git / Docker / Nginx / Kubernetes
-->

# 开发工具面试题 —— Git / Docker / Nginx / Kubernetes

> 一句话定位：**工具链的"会不会"决定了你能不能独立交付 —— 面试官考的不是命令参数，而是工程判断力**

后端 / 全栈工程师的日常工作离不开 Git 版本管理、Docker 容器化、Nginx 反向代理、Kubernetes 编排。但大多数人停留在"会用"层面，面试一旦被追问"为什么这样选"、"出了这个状态怎么办"，就容易答不上来。

本目录聚焦 **4 个高频工具面试题**，每题 80-150 行，从场景到原理到陷阱一次讲透。

---

## 1. 题目列表

| # | 题目 | 场景类型 | 难度 | 核心考点 |
|---|------|---------|------|---------|
| 1 | [Git Rebase vs Merge 怎么选？](git-rebase-vs-merge/README.md) | 架构选型 | ⭐⭐⭐⭐ | 线性历史 / Golden Rule / 冲突解决 |
| 2 | [Docker 多阶段构建为什么能大幅减小镜像体积？](docker-multi-stage/README.md) | 性能对比 | ⭐⭐⭐⭐ | 层缓存 / distroless / .dockerignore |
| 3 | [Nginx 反向代理的负载均衡策略有哪些？](nginx-reverse-proxy/README.md) | 架构选型 | ⭐⭐⭐⭐ | upstream 策略 / 健康检查 / sticky session |
| 4 | [K8s Pod 生命周期中有哪些容易忽略的状态？](k8s-pod-lifecycle/README.md) | 生产 Bug | ⭐⭐⭐⭐⭐ | Probe 三兄弟 / Init Container / PreStop |

---

## 2. 学习路径

| 目标 | 推荐顺序 |
|------|---------|
| **校招 / 实习面试** | #1 Git → #2 Docker → #3 Nginx |
| **社招后端（3 年+）** | #4 K8s → #2 Docker → #3 Nginx → #1 Git |
| **DevOps / SRE 方向** | #4 K8s → #3 Nginx → #2 Docker → #1 Git |

---

## 3. 与其他分类的关系

- **同栏目**：[`04.system-design`](../04.system-design/) — 系统设计面试题（分布式 / 高可用，与工具题互补）
- **主模块**：[`07.workflow`](../../07.workflow/) — 工作流与工程化主模块
- **故事章节**：[`12.story`](../../12.story/) — 阿明餐厅实战故事
- **格式规范**：[`QUESTION-FORMAT-SPEC.md`](../QUESTION-FORMAT-SPEC.md) — 面试题写作模板

---

## 4. 适用人群

- **面试候选人**：后端 / 全栈 / DevOps，准备工具链相关面试题。
- **新晋 Tech Lead**：需要制定团队 Git 工作流 / 容器化规范 / K8s 部署策略。

> **不适用**：纯前端（工具链侧重不同，请走 [`09.front-end`](../09.front-end/)）；纯运维（深度不够，建议直接看官方文档）。

---

← [返回: 咬文嚼字](../README.md)
