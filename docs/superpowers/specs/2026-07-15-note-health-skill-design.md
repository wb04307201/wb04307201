# note-health Skill 设计方案

> 日期：2026-07-15
> 主题：合并 `note-audit-and-improvement` + `note-content-quality` 为单一分层体检 skill
> 状态：设计已确认，待写实施计划

## 背景与动机

现有两个 skill 存在真实重叠：都在做「扫 note → 发现问题 → 给修复方案 → P0-P3 分级 → 派 subagent」。

| | note-audit-and-improvement | note-content-quality |
|---|---|---|
| 粒度 | 跨文件 / 仓库级 | 单文件内部 |
| 方法 | 机械扫描（grep/find/python，不读正文） | 判断式（读全文 + 按模块 A~G 打分） |
| 触发范围 | 整个 note | 可以只是单篇 |
| 行数 | 554 | 495 |

**核心洞察**：二者不是平级技能，而是**同一次体检的不同层**：

```
Repo 层    跨模块数字、全局索引、重复目录、架构        （audit 独有）
Module 层  模块 README、索引覆盖、模块内数字          （audit）
Topic 层   兄弟互链、系列完整性、回链双向             （audit）
Leaf 层    单篇内容深度、模块规范、可读性打分          （content-quality 就是这一层）
```

content-quality 天然是 audit 金字塔的**最底层 leaf 检测器**。因此合并成立。

**附带收益**：合并后采用「自底向上分层 + fan-out」执行模型，直接根治历史问题——机械扫描在单个 turn 内狂输出导致 context 撑爆而"跑死"。

## 已确认的三大决策

1. **形态**：单 skill + references 分层引擎（薄 orchestrator + 两份下沉规则）
2. **覆盖**：全库体检时内容质量层**全量穷举**（每个 leaf 文件都判断式打分）
3. **执行**：全库穷举用 **Workflow pipeline + resumeFromRunId** 断点续跑

## 设计详情

### §1 身份与 scope

新 skill：`skills/note-health/`，取代两个旧 skill。触发词为两者并集。

进门先判断 scope，三档：

| scope | 触发例 | 行为 |
|---|---|---|
| 单篇 / 单目录 | "评价 11.ai/RAG" | 只跑 leaf 质量层，直接读 + 打分，**不启动 workflow** |
| 单模块 | "审一下 06.spring" | 结构扫描该模块 + leaf 质量 fan-out（小规模） |
| 全库 | "note 哪里要优化" | 完整自底向上 + Workflow pipeline + 穷举 |

**原则**：单篇请求不得启动重型机器——scope 判断是第一道闸。

### §2 分层文件结构

```
skills/note-health/
├── SKILL.md                     # 薄 orchestrator（~150 行）：scope 判断 + 分层调度 + 综合报告
├── references/
│   ├── structural-checks.md     # ← 现 audit 的 8-9 类机械扫描（grep/find/python）
│   ├── leaf-quality.md          # ← 现 content-quality 的 G1-G6 + A~G 类模块打分
│   └── health-workflow.js       # 可复用 Workflow 脚本（全库穷举时跑）
```

SKILL.md 只保留决策逻辑；两份检查规则下沉到 references（渐进披露，触发时不撑爆 context）。避免「1049 行揉一坨」。

### §3 执行引擎：自底向上 4 相

```
Phase 1  结构扫描（便宜，主循环内）        大输出重定向到文件，不堆进对话
         → 数字/链接/回链/索引/重复/系列    [structural-checks.md]

Phase 2  Leaf 质量 fan-out（Workflow pipeline）
         每个 subagent 扫 1 批 leaf 文件（~5-8 篇），按模块类型 A~G 打分
         返回结构化 findings，resumeFromRunId 断点续跑  [leaf-quality.md]

Phase 3  逐层上卷   leaf → topic（兄弟互链/系列）→ module（均分/README）→ repo（跨模块数字/架构）

Phase 4  综合       结构 + 质量 findings 合并 → 统一 P0-P3 + 机械/判断分类 + 分批计划 → 写报告文件
```

**混合说明（诚实标注）**：结构类检查（数字、重复目录）本质是 grep，不需读正文，是廉价全层扫描；fan-out 只用在需要「读 + 判断」的 leaf 质量层。两路信号在 Phase 4 汇合。既满足「自底向上逐层」直觉，又不为机械检查白付 agent 成本。

### §4 fan-out 粒度（基于实测：note 有 717 个含 .md 目录 / 697 README / 1029 .md）

- **单位 = leaf 文件批**（每 agent ~5-8 篇），从 717 个 leaf 目录聚合分批——**不是** 1 agent/目录（那样会有 ~717 个 agent，逼近 1000 上限且过贵）
- 分批策略：pipeline 前先把 leaf 文件列表按 ~5-8 篇/批 切组 → agent 总数收敛到 **~130-200 个**
- 每 agent 只读自己那批的正文，按模块类型 A~G 打分，返回结构化 findings
- 并发受 Workflow 上限（~10）约束，其余排队；总数远低于 1000 上限
- 直接根治「跑死」：主循环永不持有全部正文，每 agent 的 context 也有界（~8 篇封顶）

### §5 输出格式（两者能力都保留）

统一报告 =
- audit 的**分批执行计划 + P0-P3 + 机械/判断分类**
- content-quality 的**逐篇评分表 + 模块专属维度 + 亮点**

报告写到文件（即 Phase 4 落盘产物）。

### §6 迁移与清理

1. 新建 `skills/note-health/`，从两个旧 skill 迁移重组——**不丢任何检查项 / 模块规则 / Common Mistakes**
2. 删除 `skills/note-audit-and-improvement/`、`skills/note-content-quality/`（直接删，不留 stub）
3. 改交叉引用：`note-knowledge-qa`、`note-precipitation-planning` 中指向旧 skill 名之处
4. 改 `CLAUDE.md` Meta-Skills 表：4 skill → 3 skill
5. `.claude/skills/`、`.codex/skills/` 是 gitignore 的自动镜像，由 `sync-skills.sh` / pre-commit hook 重建——**只动 `skills/`**

## 非目标（YAGNI）

- 不做跨会话持久化断点（Workflow resume 同会话足够；真崩溃靠 journal.jsonl 重建）
- 不为机械检查层引入 fan-out（grep 在主循环足够快）
- 不改 note/ 内容本身（本设计只动 skills/ 与引用它的文档）

## 迁移完整性检查表（实施时验证）

- [ ] structural-checks.md 覆盖 audit 原 8-9 类全部扫描命令
- [ ] leaf-quality.md 覆盖 content-quality 原 G1-G6 + A~G 七类模块规则 + 满分计算表
- [ ] 两份 Common Mistakes 合并去重后无遗漏
- [ ] 三档 scope 行为在 SKILL.md 明确写出
- [ ] 旧 skill 名的所有交叉引用已更新（grep 校验 0 残留）
- [ ] CLAUDE.md skill 表已更新为 3 项
- [ ] `sync-skills.sh` 跑通，镜像重建成功
