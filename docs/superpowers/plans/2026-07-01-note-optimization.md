# note 知识库优化 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 4 维度（frontmatter / 数字一致性 / 信息架构 / 写作质量）系统化优化 `note/` 14 主模块的 README。

**Architecture:** 每个模块 4 个 commit（顶层 README / 二级子 README / 数字校对 / 写作润色）；批间顺序固定（13 → 06 → 01 → 02~05/09~12 → 07/08/14）；共 56 commit + 1 setup + 1 终验 = 58 commit。

**Tech Stack:** Markdown · YAML frontmatter (HTML 注释) · Git · bash · grep

**Spec:** `docs/superpowers/specs/2026-07-01-note-optimization-design.md`

## Global Constraints

- 不修改正文内容（除非数字明显错误，并在 commit message 中说明）
- 不引入新文件类型（无 .json 索引、无脚本）
- frontmatter 写在 HTML 注释里，GitHub / Obsidian 双兼容
- 所有 commit message 格式：`refactor(<slug>): <动作>` / `fix(<slug>): <动作>` / `style(<slug>): <动作>`
- `<slug>` 使用主模块目录名（如 `01.java`、`13.split-hairs`）
- 自底向上推进：先二级子目录 → 再主模块 README → 最后总目录（`note/README.md`）
- Emoji 限定集合：`📚` 📘 `🎯` `🚀` `⚠️` `✅` `❌` `⭐`

## 共享标准模板

> 所有模块共用此模板（细节见 spec §4）。执行模块任务时直接套用。

### 顶层模块 README 模板

```markdown
<!--
module:
  parent: note
  slug: <本模块目录名>
  type: index
  category: <分类>
  summary: <一句话定位>
-->

# <数字编号>、<模块中文名>

> <一句话导览>

> 📘 **写作与维护规范**：[CONTRIBUTING.md](../CONTRIBUTING.md)
> 📚 **返回总目录**：[note 总目录](../README.md)

## 目录导航

| 序号 | 主题 | 核心内容 |
|------|------|----------|
| 1 | [子目录 1](<子目录>/README.md) | 一句话核心 |
| ... | ... | ... |
```

### 二级子目录 README 模板

```markdown
<!--
module:
  parent: <主模块>
  slug: <主>/<子>
  type: article
  category: <分类>
  summary: <一句话>
-->

# <子目录名>

> <1-2 句本子目录定位>

## 核心内容

| 主题 | 核心问题 |
|------|---------|
| [文章 1](article-1/README.md) | 一句话核心问题 |
| ... | ... |

---

> 📚 **返回主模块**：[主模块名](../README.md)
```

---

## Task 0: Setup — 同步 CONTRIBUTING.md

**Files:**
- Modify: `note/CONTRIBUTING.md`（追加"模块 README 标准结构"段落）
- Create: `note/CONTRIBUTING.md` 末尾的新章节

**Interfaces:**
- Consumes: spec §4 的标准模板
- Produces: 后续 14 个模块任务都引用本章节

- [ ] **Step 1: 在 CONTRIBUTING.md 末尾追加"模块 README 标准结构"章节**

追加内容（直接复制，无需改动）：

```markdown
## 模块 README 标准结构

所有主模块 README 与子目录 README 必须遵循以下模板（详见 `docs/superpowers/specs/2026-07-01-note-optimization-design.md` §4）：

- 顶层模块 README：必须包含 frontmatter + 一句话导览 + 目录导航表格 + 适用人群（可选）+ 学习路径（可选）
- 二级子目录 README：必须包含 frontmatter + 1-2 句定位 + 核心内容表格 + 文末回链
- 三级文章页：按需补 frontmatter

frontmatter 写在 HTML 注释里，示例：

\`\`\`markdown
<!--
module:
  parent: <父模块>
  slug: <路径>
  type: index|article|cheatsheet
  category: <分类>
  summary: <一句话>
-->
\`\`\`

维护原则：所有变更手工逐文件修改，不使用脚本。
```

- [ ] **Step 2: 验证章节已添加**

Run: `grep -n "模块 README 标准结构" note/CONTRIBUTING.md`
Expected: 章节标题出现 1 次。

- [ ] **Step 3: Commit**

```bash
git add note/CONTRIBUTING.md
git commit -m "docs(note): CONTRIBUTING 增 §模块 README 标准结构（引用 note-optimization spec §4）"
```

---

## Task 1: 13.split-hairs（示范批 #1：高频 Q&A 卡片型）

**Files:**
- Modify: `note/13.split-hairs/README.md`（顶层）
- Modify: `note/13.split-hairs/QUESTION-FORMAT-SPEC.md`（如需前向兼容）
- Modify: `note/13.split-hairs/01.java/README.md` ~ `note/13.split-hairs/09.front-end/README.md`（共 6 个分类 README）

**Interfaces:**
- Consumes: Task 0 的 CONTRIBUTING 章节、共享模板
- Produces: 完整可作为其他模块参考的样板

- [ ] **Step 1: 顶层 README 重写**

按"顶层模块 README 模板"重写 `note/13.split-hairs/README.md`：
- frontmatter 完整
- 一句话导览：保持"主模块的刺刀版 —— 专治面试高频问题"风格
- 目录导航表格：6 大分类（Java 33 / 数据库 29 / 系统设计 13 / Spring 13 / AI 14 / 前端 25，**篇数需重新数实际子目录文件**）
- 适用人群：面试候选人 / 转岗工程师
- 学习路径：3 段式（按模块刷 / 按难度刷 / 按公司刷）
- 文末回链：note 总目录

- [ ] **Step 2: Commit (1/4)**

```bash
git add note/13.split-hairs/README.md
git commit -m "refactor(13.split-hairs): 重写主 README（frontmatter + 目录导航 + 适用人群 + 学习路径）"
```

- [ ] **Step 3: 6 个分类 README 补齐**

按"二级子目录 README 模板"逐个补齐：
- `note/13.split-hairs/01.java/README.md`（33 篇）
- `note/13.split-hairs/03.database/README.md`（29 篇）
- `note/13.split-hairs/04.system-design/README.md`（13 篇）
- `note/13.split-hairs/06.spring/README.md`（13 篇）
- `note/13.split-hairs/11.ai/README.md`（14 篇）
- `note/13.split-hairs/09.front-end/README.md`（25 篇）

每个 README：
- frontmatter（`type: article`、`category: 高频面试题`）
- 1-2 句定位
- 核心内容表格（按二级分类分组：集合/并发/JVM/...）
- 文末回链：`> 📚 **返回主模块**：[咬文嚼字（高频面试题）](../README.md)`

- [ ] **Step 4: Commit (2/4)**

```bash
git add note/13.split-hairs/
git commit -m "refactor(13.split-hairs): 补齐 6 个分类 README 标准结构"
```

- [ ] **Step 5: 数字一致性校对**

对照实际文件数与声明篇数：

Run:
```bash
echo "01.java: $(ls note/13.split-hairs/01.java | grep -v README | wc -l)"
echo "03.database: $(find note/13.split-hairs/03.database -mindepth 2 -maxdepth 2 -type d | wc -l)"
echo "04.system-design: $(find note/13.split-hairs/04.system-design -mindepth 2 -maxdepth 2 -type d | wc -l)"
echo "06.spring: $(find note/13.split-hairs/06.spring -mindepth 2 -maxdepth 2 -type d | wc -l)"
echo "11.ai: $(find note/13.split-hairs/11.ai -mindepth 2 -maxdepth 2 -type d | wc -l)"
echo "09.front-end: $(find note/13.split-hairs/09.front-end -mindepth 2 -maxdepth 2 -type d | wc -l)"
```

如有偏差，修正顶层 README 表格中的数字声明。

- [ ] **Step 6: Commit (3/4)**

```bash
git add note/13.split-hairs/README.md
git commit -m "fix(13.split-hairs): 数字一致性校对（6 分类篇数与实际文件对齐）"
```

- [ ] **Step 7: 写作润色**

通读 7 个 README（1 顶层 + 6 分类）：
- 顶部摘要是否简洁不堆砌
- 表格列宽合理（中文术语 + 路径 + 一句话说明）
- emoji 是否统一
- 不引入新术语缩写

如有调整，**只动 README 顶部块**，不动正文。

- [ ] **Step 8: Commit (4/4)**

```bash
git add note/13.split-hairs/
git commit -m "style(13.split-hairs): 顶层 + 6 分类 README 写作润色"
```

- [ ] **Step 9: 验证门**

- [ ] `git diff --check` 无警告
- [ ] 抽查 5 条链接：`grep -RE '\[.*\]\(.*\)' note/13.split-hairs/README.md | head -5`
- [ ] `note/README.md` 中"十三、"章节路径仍指向 `13.split-hairs/README.md`

---

## Task 2: 06.spring（示范批 #2：大型结构文档型）

**Files:**
- Modify: `note/06.spring/README.md`（顶层）
- Modify: `note/06.spring/01-core/README.md` ~ `08-annotations/README.md`（共 8 个分类 README）
- Modify: `note/06.spring/03-data/mybatis/README.md`（重点项目子 README）

**Interfaces:**
- Consumes: Task 0 CONTRIBUTING 章节、Task 1 经验（保留 review 反馈）
- Produces: 第二个示范模块

- [ ] **Step 1: 顶层 README 重写**

按模板重写 `note/06.spring/README.md`：
- frontmatter（`type: index`, `category: 后端框架`）
- 一句话导览
- 目录导航表格：8 大分类（核心容器/Web/数据（含 MyBatis 全栈链接）/Spring Boot/Spring Cloud/集成组件/可观测性/注解速查）
- 适用人群：Java 后端 / Spring 学习者
- 学习路径：3 段式（IoC/AOP → Boot/Cloud → 整合）
- "开源参考" 段落：保留现有的 Multi-Level Cache / Method Trace Log 链接

- [ ] **Step 2: Commit (1/4)**

```bash
git add note/06.spring/README.md
git commit -m "refactor(06.spring): 重写主 README（frontmatter + 8 大分类导航 + 学习路径）"
```

- [ ] **Step 3: 8 个分类 README 补齐**

按模板补齐 `01-core` ~ `08-annotations` 8 个二级 README。每个：
- frontmatter
- 1-2 句定位
- 核心内容表格（如果原 README 已有内容，保留正文并仅改顶部结构）
- 文末回链

**特殊处理**：`06.spring/03-data/mybatis/README.md` 因为是重点项目子模块，按二级标准补齐，但保留现有内容。

- [ ] **Step 4: Commit (2/4)**

```bash
git add note/06.spring/
git commit -m "refactor(06.spring): 补齐 8 个分类 README + mybatis 重点项目 README"
```

- [ ] **Step 5: 数字一致性**

核对 8 大分类的核心内容表格（如 "MyBatis 全栈 4 主题"、Spring Cloud "服务注册/配置中心/..."）与实际子目录数量。

- [ ] **Step 6: Commit (3/4)**

```bash
git add note/06.spring/
git commit -m "fix(06.spring): 数字一致性校对"
```

- [ ] **Step 7: 写作润色**

- [ ] **Step 8: Commit (4/4)**

```bash
git add note/06.spring/
git commit -m "style(06.spring): 顶层 + 8 分类 README 写作润色"
```

- [ ] **Step 9: 验证门**

---

## Task 3: 01.java（示范批 #3：仓库最重且最有版本压力）

**Files:**
- Modify: `note/01.java/README.md`（顶层）
- Modify: `note/01.java/concepts/README.md` ~ `version/README.md`（共 15 个分类 README）

**Interfaces:**
- Consumes: Task 1/2 经验
- Produces: 最重模块的样板

- [ ] **Step 1: 顶层 README 重写**

- 一句话导览："从语言基础到 JVM 原理、并发编程、版本演进，系统性构建 Java 知识体系"
- 目录导航表格：15 大主题
- 适用人群：Java 开发者 / 面试候选人
- 学习路径：3 段式

- [ ] **Step 2-8: 同 Task 1/2 的 4 commit 流程**

```bash
git commit -m "refactor(01.java): 重写主 README（frontmatter + 15 主题导航 + 学习路径）"
git commit -m "refactor(01.java): 补齐 15 个分类 README 标准结构"
git commit -m "fix(01.java): 数字一致性校对"
git commit -m "style(01.java): 顶层 + 15 分类 README 写作润色"
```

- [ ] **Step 9: 验证门**

---

## Task 4-11: 推广批（8 模块）

每个模块独立 task，按 Task 1 同款 9-step 流程：

| Task | 模块 | 顶层分类数 |
|------|------|-----------|
| 4 | `02.computer-basics` | 5（网络/算法/Linux/运维/知识产权）|
| 5 | `03.database` | 12（基础/SQL/事务/索引/MySQL/缓存/Redis/NoSQL/连接池/迁移/监控/云数据库）|
| 6 | `04.system-design` | 7（基础/分布式/高可用/高性能/安全/幂等/部署）|
| 7 | `05.tools` | 6（Git/Docker/Java 库/Nginx/Monorepo/阿里微服务）|
| 8 | `09.front-end` | 9（基础/语言/框架/工程化/架构/性能/安全/跨端/AI）|
| 9 | `10.big-data` | 8（数仓/Hadoop/实时/数据湖/OLAP/调度/治理/同步）|
| 10 | `11.ai` | 8（L1-L6 + LLMOps + 教学）|
| 11 | `12.story` | 1（叙事型，无子目录分类，但需顶层 README 强化）|

**每个 Task 通用 commit 模板**：

```bash
git commit -m "refactor(<slug>): 重写主 README"
git commit -m "refactor(<slug>): 补齐 <N> 个子 README 标准结构"
git commit -m "fix(<slug>): 数字一致性校对"
git commit -m "style(<slug>): 顶层 + <N> 分类 README 写作润色"
```

**特殊处理**：
- `12.story` 因只有 1 个顶层 README（无子目录分类），只做 2 个 commit（重写顶层 + 数字校对），不补子 README
- `11.ai` 有 90 个子 README，量大；如 review 压力过大可拆为 2 个 commit（先 1-4，再 5-8）

---

## Task 12-14: 新建批（3 模块）

| Task | 模块 | 顶层分类数 |
|------|------|-----------|
| 12 | `07.workflow` | 4（定义/引擎/编排/事件驱动）|
| 13 | `08.application-systems` | 6（研发/生产/供应链/销售/运营/专项）+ 系统集成 + 速查表 |
| 14 | `14.project-management` | 1（决策实战，无子目录分类）|

按 Task 4-11 同款流程。`14.project-management` 只做 2 个 commit（顶层重写 + 数字校对），无子 README 需要补齐。

---

## Task 15: 终验 — 全局链接与一致性

**Files:**
- Modify: `note/README.md`（如有路径失效）
- 不动其他模块的 README（除非终验发现失效链接）

- [ ] **Step 1: 验证 `note/README.md` 中所有主模块链接有效**

Run:
```bash
grep -oE '\]\([^)]*README\.md\)' note/README.md | head -50
```

对每条链接，确认目标文件存在。

- [ ] **Step 2: 抽查 14 模块顶层 README 的"返回总目录"链接**

Run:
```bash
for dir in note/0*.java note/0*.computer-basics note/0*.database note/0*.system-design note/0*.tools note/0*.spring note/0*.workflow note/0*.application-systems note/0*.front-end note/1*.big-data note/1*.ai note/1*.story note/1*.split-hairs note/1*.project-management; do
  if [ -f "$dir/README.md" ]; then
    echo "=== $dir/README.md ==="
    grep -E '返回总目录|返回主模块' "$dir/README.md" | head -3
  fi
done
```

每条回链应指向正确路径。

- [ ] **Step 3: 验证 `note/CONTRIBUTING.md` 引用本 spec**

Run: `grep -n "note-optimization" note/CONTRIBUTING.md`
Expected: 至少 1 处引用。

- [ ] **Step 4: 全局 commit log 审查**

Run: `git log --oneline | grep -E "(refactor|fix|style)\((0[1-9]|1[0-4])\." | wc -l`
Expected: 至少 56 条（4 × 14，部分模块如 12.story / 14.project-management 略少）。

- [ ] **Step 5: 终验报告 commit**

如有任何修复需要：

```bash
git add note/
git commit -m "fix(note): 终验修复（链接 / 数字 / 一致性）"
```

如无需修复，跳过本 commit。

- [ ] **Step 6: 验收对照 spec §10**

逐条核对：
1. ✅ 14 主模块顶层 README 全部按标准模板重写
2. ✅ 14 主模块下所有二级子目录 README 顶部补齐 § 模板（如有）
3. ✅ 数字一致性校对无遗留差异
4. ✅ `note/CONTRIBUTING.md` 同步更新
5. ✅ 所有 commit 通过验证门
6. ✅ `note/README.md` 总目录与各主模块相互链接全部有效

---

## 总览

| Task | 内容 | Commit 数 |
|------|------|----------|
| 0 | Setup: CONTRIBUTING 同步 | 1 |
| 1 | 13.split-hairs（示范 Q&A 型）| 4 |
| 2 | 06.spring（示范结构型）| 4 |
| 3 | 01.java（示范重载型）| 4 |
| 4-11 | 推广批 8 模块 | 32 |
| 12-14 | 新建批 3 模块 | 8-12（12.story / 14.pm 略少）|
| 15 | 终验 | 0-1 |
| **合计** | | **~55-60** |