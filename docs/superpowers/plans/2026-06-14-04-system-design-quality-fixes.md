# 04.system-design 质量修复实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 04.system-design 全面审计中发现的 18 个 IMPORTANT + 几个 MINOR 问题。

**Tech Stack:** Markdown 编辑、git commits

---

## 优先级总览

- **P0**（用户可见错误）：2 项 — 顶层 README 内容数
- **P1**（结构正确性）：14 项 — 标题层次跳级
- **P2**（卫生）：5 项 — 编号重复 + 孤立 PNG
- **P3**（可选）：跳过

---

## Task A：P0 顶层 README 内容数修正

**Files:** `note/04.system-design/README.md`

- [ ] **Step A.1** — 第 71 行：04 高性能篇的"内容数 11" 改 12

  From: `| [04 高性能篇](04-high-performance/README.md) | 11 | 负载均衡、CDN、缓存、数据库优化、消息队列 |`
  To:   `| [04 高性能篇](04-high-performance/README.md) | 12 | 负载均衡、CDN、缓存、数据库优化、消息队列、连接池、序列化、Java 优化 |`

- [ ] **Step A.2** — 第 73 行：06 幂等篇的"内容数 1" 改 5

  From: `| [06 幂等性设计](06-idempotency/README.md) | 1 | 幂等性设计与实现方案 |`
  To:   `| [06 幂等性设计](06-idempotency/README.md) | 5 | 幂等键、乐观锁、状态机、去重表、与分布式事务的关系 |`

- [ ] **Step A.3** — 验证：grep 应无 "11 | 负载均衡"、"1 | 幂等性" 残留
- [ ] **Step A.4** — Commit: `fix(04-sysdes): 顶层 README 内容数修正（04: 11→12, 06: 1→5）`

---

## Task B：P2 编号重复修复

**Files:** `note/04.system-design/README.md`, `note/04.system-design/01-foundation/README.md`, `note/04.system-design/04-high-performance/README.md`

- [ ] **Step B.1** — `04.system-design/README.md:38-46` 学习路线编号去重（5/5/6/6 → 4/5/6/6a/6b/7/8/9）
  - 实际从 git blame 看 6a/6b 是 ArchiMate/IT4IT 后加的，编号应顺延
  - 改完应在文件内重新核对：4 OOD, 5 DDD, 6 TOGAF, 6a ArchiMate, 6b IT4IT, 7 CAP, 8 分布式事务, ... 等
- [ ] **Step B.2** — `01-foundation/README.md:18-25` TOC 11/11a/11b 改 11/12/13，后续 12-16 改 14-18
- [ ] **Step B.3** — `04-high-performance/README.md:8,12` 第二处 "2. 数据库优化概览" 改 "3. 数据库优化概览"，3-11 顺延 4-12
- [ ] **Step B.4** — Commit: `fix(04-sysdes): 修复 3 处编号重复（学习路线 / 01-foundation TOC / 04-high-perf）`

---

## Task C：P1 标题层次跳级 — 01-foundation

**Files:** 6 个

1. `01-foundation/api/graphql/README.md` — H1 跳到 H3；还含 2 个多余 H1（line "优秀实践..." 和 "避免..." 段开头是 `#`）
2. `01-foundation/api/rpc/README.md` — H1→H3 (line 7)，H3→H4 (line 9 之内)
3. `01-foundation/design-patterns/README.md` — H1→H3
4. `01-foundation/microservices/data-consistency/README.md` — H1→H3
5. `01-foundation/microservices/service-contract/README.md` — 多处 H1→H3、H3→H4 跳级
6. `01-foundation/software-engineering/quality-assurance/README.md` — 完全无 H2 段

- [ ] **Step C.1-6** — 读取每个文件，按 H1→H2→H3→H4 顺序重整。统一策略：把现有的 H3 内容（无对应 H2 包裹）降级为 H2；H4 缺 H3 包裹则降为 H3
- [ ] **Step C.7** — 验证：每个文件 `grep -c '^## [1-9]\.'` 不应有跳级（具体策略：H1 后第一个 ## 标题应是 H2）
- [ ] **Step C.8** — Commit: `fix(01-foundation): 修复 6 个文件的标题层次跳级`

---

## Task D：P1 标题层次跳级 — 02-distributed

**Files:** 3 个

1. `02-distributed/cap-and-base/base/README.md` — line 5 H1→H3
2. `02-distributed/cap-and-base/cap/README.md` — line 5 H1→H3
3. `02-distributed/distributed-id/README.md` — line 5 H1→H3

- [ ] **Step D.1-3** — 把 `### 一、...` 改为 `## 一、...`
- [ ] **Step D.4** — Commit: `fix(02-distributed): 修复 3 个文件的标题层次跳级`

---

## Task E：P1 标题层次跳级 — 04-high-performance

**Files:** 2 个

1. `04-high-performance/load-balance/README.md` — line 13/19 重复 H2、line 22 H3→H4 跳级、line 81 H5 过深
2. `04-high-performance/database-optimization/cold-hot-data-separation/README.md` — 段层次混乱

- [ ] **Step E.1** — 读取 `load-balance/README.md`，重整层次（line 19 重复 H2 合并；line 22 H4 升 H3；line 81 段落重整）
- [ ] **Step E.2** — 读取 `cold-hot-data-separation/README.md`，把 line 21/27 H2 降为 H3（"优点/缺点"、"任务调度"）
- [ ] **Step E.3** — Commit: `fix(04-high-perf): 修复 2 个文件的标题层次混乱`

---

## Task F：P2 孤立 PNG 处置

**Files:** 8 张 PNG

1. `03-high-availability/rate-limiting/img.png ~ img_3.png`（4 张）
2. `07-deployment/deploy/img.png ~ img_3.png`（4 张）

处置策略：
- 先 Read 一下两个 README 看看哪个 PNG 适合插在哪里
- 能插入 → 嵌入 README
- 不适合 → 删除（避免遗留）

- [ ] **Step F.1** — 读取 `rate-limiting/README.md`（122 行），判断 4 张图能否插入"三、限流算法"段
- [ ] **Step F.2** — 读取 `deploy/README.md`，判断 4 张图能否插入合适位置
- [ ] **Step F.3** — 处置：嵌入或删除
- [ ] **Step F.4** — Commit: `chore(04-sysdes): 清理 8 张孤立 PNG（嵌入或删除）`

---

## 验证

所有 commit 落地后跑：

```bash
cd "C:/developer/IdeaProjects/wb04307201"
echo "=== 顶层 README 计数 ==="
grep -E '^\| \[' note/04.system-design/README.md | head -10
echo "=== H1→H3 跳级检查（H1 后第一个 ## 必须是 ## 而不是 ###）==="
for f in $(find note/04.system-design -name '*.md' -type f); do
  # 找 H1 后第一个 ## 标题
  awk '/^# /{h1=NR} /^## / && !h2 && h1 && NR-h1<=5{print FILENAME":"NR": "$0; h2=1} {h1=0; h2=0}' "$f"
done
echo "=== 孤立 PNG ==="
# 找 PNG 在 04.system-design 但没在任何 md 中引用的
for img in $(find note/04.system-design -name 'img*.png' -type f); do
  base=$(basename "$img")
  if ! grep -rln "$base" note/04.system-design --include='*.md' 2>/dev/null | head -1 | grep -q .; then
    echo "ORPHAN: $img"
  fi
done
```
