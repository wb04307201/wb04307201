<!--
question:
  id: tools-git-rebase-vs-merge
  topic: tools
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构选型
  tags: [tools, Git, Rebase, Merge, 提交历史, 冲突解决]
-->

# Git Rebase vs Merge 怎么选？

> 一句话定位：Rebase 制造线性历史，Merge 保留真实分支拓扑 —— 选错会污染主干或丢失上下文。

> **系列定位**：经典工具链面试题（Git 工作流高频）。考察的不是"两个命令的参数"，而是 **历史可读性** + **团队协作规范** + **冲突处理成本**。

---

## 引子：一次"消失"的提交

```text
你在 feature/login 分支开发了 3 天，提交了 12 个 commit。
同事说："rebase 一下 main 再提 PR。"
你执行了 git rebase main，解决了 4 个冲突，push --force。
PR 合并了，但第二天 QA 发现一个 bug —— 回溯历史时，
你 3 天前的一个关键 commit 找不到了，因为 rebase 改写了 hash。
```

Rebase 让历史干净了，但也让"真实发生了什么"变得模糊。Merge 保留了一切，但提交图变成了意大利面。**到底该怎么选？**

---

## 一、核心原理

### 1.1 Merge：保留真实历史

`git merge feature` 会在当前分支创建一个 **merge commit**，将两个分支的历史"缝合"在一起。

- ✅ 保留完整的分支拓扑（谁在什么时候合并了什么）
- ✅ 不改变已有 commit 的 hash
- ❌ 提交图可能很乱（大量交叉线）

### 1.2 Rebase：重写历史为线性

`git rebase main` 会把当前分支的 commit "摘下来"，逐个重新应用到 main 的最新节点上。

- ✅ 提交历史线性、干净
- ✅ 适合个人分支整理（squash / 改 commit message）
- ❌ **改写了 commit hash** —— 任何已 push 的 commit 被 rebase 后，协作者会冲突

### 1.3 TL;DR 对比表

| 维度 | Merge | Rebase |
|------|-------|--------|
| 历史形态 | 非线性（保留分支分叉） | 线性（一条直线） |
| Commit Hash | 不变 | 改写 |
| 冲突解决 | 一次性（merge commit 时） | 逐个 commit 解决 |
| 适用场景 | 公共分支合并 | 个人分支整理 |
| Golden Rule | — | **不要 rebase 已 push 的公共分支** |

---

## 二、详解：三种工作流模式

### 2.1 Feature Branch + Merge（GitHub Flow 标准）

```bash
git checkout -b feature/login
# 开发...多次 commit
git checkout main
git merge feature/login          # 创建 merge commit
```

适合：开源项目、大团队、需要审计历史的场景。

### 2.2 Feature Branch + Rebase + Squash Merge

```bash
git checkout -b feature/login
# 开发...多次 commit
git rebase -i main               # 交互式 rebase，squash 成一个 commit
git checkout main
git merge --squash feature/login  # 或直接 merge（已经 rebase 过了）
```

适合：中小团队、追求干净历史、CI 友好。

> Interactive rebase 常用操作：`pick`（保留）/ `squash`（合并到上一个）/ `reword`（改 message）/ `drop`（删除）。

---

## 三、常见陷阱

### 陷阱 1：Rebase 已 push 的公共分支

- **现象**：你 rebase 了 main，force push 后同事 pull 出现大量冲突
- **真相**：Rebase 改写了 hash，同事本地的 commit 和远程的不再是同一个

### 陷阱 2：Rebase 后丢失关键 commit

- **现象**：`git rebase -i` 时不小心 drop 了一个 commit
- **真相**：可以用 `git reflog` 找回，但大多数人不知道这个命令

### 陷阱 3：Merge 冲突解决错了方向

- **现象**：merge 时 "Accept Current Change" 点成了对方分支的代码
- **真相**：用 `git merge --abort` 回退，重新 merge

### 陷阱 4：长期分支不 rebase 导致最终冲突爆炸

- **现象**：feature 分支开了 2 周没同步 main，最后合并时 50+ 文件冲突
- **真相**：定期（每天 / 每两天）把 main rebase 到 feature 分支

---

## 四、最佳实践

1. **个人 feature 分支**：用 rebase 整理历史（squash + reword），push 前保持 1-3 个有意义的 commit
2. **合并到 main/develop**：用 merge（或 squash merge），不 force push 公共分支
3. **定期同步**：feature 分支每天 rebase main 一次，避免冲突积压
4. **团队规范先行**：在 CONTRIBUTING.md 写明"rebase 还是 merge"，减少争论
5. **善用 reflog**：`git reflog` 是 rebase 操作的安全网，找回任何"丢失"的 commit

---

## 五、面试话术（90 秒版本）

> "Rebase 和 Merge 的核心区别在于**是否改写历史**。Rebase 把当前分支的 commit 重新应用到目标分支顶部，产生线性历史，但会改变 commit hash；Merge 保留分支拓扑，创建一个 merge commit。
>
> Golden Rule：**不要 rebase 已经 push 到远程的公共分支**，否则协作者会因 hash 不一致而冲突。
>
> 我的实践是：个人 feature 分支用 interactive rebase 整理提交（squash / reword），合并到 main 时用 merge 或 squash merge。长期分支每天 rebase main 一次，避免最终冲突爆炸。团队层面在 CONTRIBUTING.md 里明确规范，减少无谓争论。"

---

## 六、交叉引用

- 同栏目：[Docker 多阶段构建](../docker-multi-stage/README.md) — 容器化工具链面试题
- 同栏目：[Nginx 反向代理](../nginx-reverse-proxy/README.md) — 部署与负载均衡
- 同栏目：[K8s Pod 生命周期](../k8s-pod-lifecycle/README.md) — 编排与调度
- 系统设计：[分布式锁](../../04.system-design/distributed-lock/README.md) — 系统设计高频题

---

← [返回: 咬文嚼字 · 工具](../README.md)

> 📅 2026-07-16 · 咬文嚼字 · 工具 · ⭐⭐⭐⭐（高频面试 + 团队协作规范）
