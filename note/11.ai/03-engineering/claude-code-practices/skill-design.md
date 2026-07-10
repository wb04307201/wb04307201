<!--
module:
  parent: ai
  slug: ai/claude-code-practices/skill-design
  type: article
  category: 主模块子文章
  summary: Skill 从 0-1 的设计方法论：决策树（写 Skill vs 改 CLAUDE.md）+ 4 阶段流程 + 5 反模式 + YAML 模板。
-->

# Skill 从 0 到 1：怎么设计一个能用的 Skill？

> 一句话定位：**写 Skill 不是写教程**。它是把"专业知识压缩成 Agent 可加载、可拒识、可评测的工程产物"。本文给出一套"**决策树 + 4 阶段流程 + 5 反模式 + YAML 模板**"的方法论，让你的 Skill 第一次写就能用对。

> **同模块姐妹**：
> - [Skill 命中率](skill-hit-rate.md) — 数量爆炸后**怎么调**（"调度"视角）
> - [Claude Code 大型代码库实践](README.md) — Skill 是怎么"渐进式披露"的（基础）

---

## 一、决策树：什么时候该写 Skill？

写 Skill 之前，先问 3 个问题。**答错任何一个，都不该写 Skill**。

```
Q1：这段知识是"每次会话都要用" 还是 "特定场景才用"？
├─ 每次都要 → 改 CLAUDE.md（不要写 Skill）
└─ 特定场景 → Q2

Q2：这段知识是"行为约束" 还是 "专业知识"？
├─ 行为约束（"不要做 X"、"先 lint 再 commit"）→ 加 Hook（不要写 Skill）
└─ 专业知识（"怎么写 pr-review 报告"、"怎么生成 API 文档"）→ Q3

Q3：这段知识能"渐进式披露" 吗？（即：能拆成"一句话描述"+"按需加载细节"）
├─ 能 → 写 Skill ✅
└─ 不能 → 写 Subagent 或加 MCP server
```

### 1.1 决策树反例（不该写 Skill 的场景）

| 场景 | 错的选择 | 对的选择 | 理由 |
|------|---------|---------|------|
| "提交前必须跑 lint" | 写 Skill `lint-before-commit` | 加 Hook（`PreToolUse` 拦截 Bash） | 行为约束，自动化执行更可靠 |
| "项目用 React 18 + Vite" | 写 Skill `tech-stack` | 放 `CLAUDE.md` 根目录 | 每次会话都要用，应常驻 |
| "怎么审查 PR 的安全性" | 写 Skill `pr-security-review` | **写 Skill ✅**（专业知识 + 按需加载） | 符合决策树 |
| "查询用户订单数据库" | 写 Skill `query-orders` | 加 MCP server | 需要结构化查询 + 权限控制 |

### 1.2 决策树 vs skill-hit-rate 的"调度"视角

| 视角 | 问题 | 答案 |
|------|------|------|
| **设计视角**（本文）| 写 Skill vs 改 CLAUDE.md / 加 Hook？ | 决策树 |
| **调度视角**（[skill-hit-rate](skill-hit-rate.md)）| 50 个 Skill 怎么保证选对？ | 四层模型 |

**两姐妹互补**：本文让 Skill **第一次写就对**，skill-hit-rate 让 Skill **数量爆炸后还能调**。

---

## 二、4 阶段设计流程

### 阶段 1：识别（Identify）——"该不该写 Skill"已经过了决策树

输出物：**Skill 的一句话价值主张**。

模板：
```
我准备写的 Skill：________________
它解决的具体场景：________________
它与 CLAUDE.md / Hook / Subagent 的边界：________________
```

**例**：
```
Skill 名：pr-review-security
场景：审查 PR 时的安全漏洞检测（SQL 注入 / XSS / 鉴权绕过）
边界：不是通用 lint（用 Hook）；不是数据库查询（用 MCP）；不是每次会话都用（不写 CLAUDE.md）
```

### 阶段 2：设计（Design）——写 YAML frontmatter

**frontmatter 必填 6 字段**：

```yaml
---
name: pr-review-security
description: |
  审查 PR 中的安全漏洞。覆盖 SQL 注入 / XSS / 鉴权绕过 / 敏感信息泄露 4 类。
  必须在 pr-review 类任务中显式调用。
when_to_use:
  - "审查 PR 安全性"
  - "检查代码中是否有 SQL 注入 / XSS"
  - "审计鉴权逻辑"
when_not_to_use:
  - "通用代码风格检查（请用 lint-hook）"
  - "性能审查（请用 pr-review-performance）"
  - "架构审查（请用 pr-review-architecture）"
inputs:
  - name: pr_diff
    type: string
    required: true
    description: PR 的 diff 内容
  - name: focus_areas
    type: array
    items: { type: string }
    required: false
    description: 重点关注的漏洞类型，默认全选
---
```

**关键原则**：
- `when_not_to_use` **必须写** —— 让 Agent 能拒识，避免误命中
- `inputs` 要标 `required` —— 防止 Agent 用残缺输入跑 Skill
- `description` 第一句必须是"动词 + 对象 + 边界" —— Agent 扫一眼就知道要不要用

### 阶段 3：实现（Implement）——写 SKILL.md 正文

**正文结构模板**（3 段式）：

```markdown
# <Skill 名>

## 一句话定位
（让 Agent 30 秒内知道这个 Skill 干什么）

## 第一性原理
（不依赖任何上下文的"普适规则"，3-5 条）

## 执行步骤
1. 步骤 1（参数校验）
2. 步骤 2（核心操作）
3. 步骤 3（输出格式）

## 输出示例
（给 Agent 一个具体的输出范本）

## 边界与异常
- 情况 A → 走分支 X
- 情况 B → 报错并提示用户
```

**反模式**：
- ❌ 长篇教程（应该用渐进披露，让 Agent 按需加载）
- ❌ 缺少"输出示例"（Agent 不知道输出长什么样）
- ❌ 没有边界与异常（Agent 不知道什么情况该报错）

### 阶段 4：测试（Test）——离线评测 + 在线埋点

**离线评测集**（最小 30 条）：

```jsonl
{"query": "审查这个 PR 有没有 SQL 注入", "expected_skill": "pr-review-security", "expected_pass": true}
{"query": "检查代码风格", "expected_skill": "lint-hook", "expected_pass": false}
{"query": "看看 PR 的鉴权逻辑", "expected_skill": "pr-review-security", "expected_pass": true}
```

**在线埋点**（生产环境）：

```yaml
metrics:
  - name: skill_invocation_total
    type: counter
    labels: [skill_name, outcome]
    # outcome: success | wrong_choice | error
  - name: skill_hit_rate
    type: gauge
    labels: [skill_name]
    # 命中正确率（来自人工反馈或 LLM judge）
```

**测试通过标准**：
- 离线评测命中率 ≥ 90%
- 在线埋点显示 hit_rate ≥ 85%（人工反馈 30 天均值）

---

## 三、5 大反模式（写 Skill 时必避）

### 反模式 1：大而全（God Skill）

**症状**：一个 Skill 想覆盖所有场景，description 写了 200 字，when_to_use 列了 10 条。

**修复**：**小而精 + 组合**。拆成 3-5 个小 Skill，让 Agent 按需组合。

**反例**：
```yaml
# 错误
name: code-review
description: 审查代码风格、安全、性能、架构、可读性、可维护性...
when_to_use: [审查代码、改进代码、写代码...]

# 正确
name: code-review-security
description: 审查代码安全漏洞
name: code-review-performance
description: 审查代码性能瓶颈
name: code-review-style
description: 审查代码风格与可读性
```

### 反模式 2：描述模糊（Vague Description）

**症状**：description 写"这是一个处理 X 的工具" —— Agent 看完不知道该不该用。

**修复**：**动词 + 对象 + 边界** 三件套。

**反例 vs 正例**：

```yaml
# 反例
description: 处理 API 文档

# 正例
description: |
  生成 REST API 接口文档（OpenAPI 3.0 格式）。
  输入：路由代码或控制器文件路径。
  不做：性能测试、部署、数据库迁移。
```

### 反模式 3：缺 when_not_to_use（Missing Anti-Use）

**症状**：只写什么时候该用，不写什么时候不该用 → Agent 在边界场景乱猜。

**修复**：**至少 3 条 when_not_to_use**，覆盖最容易混淆的边界。

### 反模式 4：没输入校验（No Input Validation）

**症状**：Skill 假设输入一定合法，不校验 → Agent 传残缺数据进来，Skill 默默失败。

**修复**：**inputs 必填 + 类型 + 描述**，Skill 正文第一步必须做校验。

**反例 vs 正例**：
```python
# 反例
def run_skill(pr_diff):
    return analyze(pr_diff)  # pr_diff 可能是 None

# 正例
def run_skill(pr_diff, focus_areas=None):
    if not pr_diff:
        raise SkillInputError("pr_diff is required, got empty/None")
    if focus_areas is None:
        focus_areas = ["sql_injection", "xss", "auth_bypass"]
    return analyze(pr_diff, focus_areas)
```

### 反模式 5：无评估机制（No Evaluation）

**症状**：Skill 上线后，没人知道它效果怎么样 —— Agent 调用了但输出错的，用户默默忍受。

**修复**：
- 离线：30 条评测集跑通，命中率 ≥ 90%
- 在线：埋点 + 人工反馈 30 天均值 hit_rate ≥ 85%

---

## 四、完整 YAML 模板（实战范例）

```yaml
---
# ===== 基础元信息 =====
name: <kebab-case-name>
description: |
  <动词 + 对象>。<补充说明>。
  <必填边界：不做什么>。
version: 1.0.0
owner: <team-or-person>
last_updated: 2026-07-06

# ===== 触发条件 =====
when_to_use:
  - "<场景描述 1>"
  - "<场景描述 2>"
when_not_to_use:
  - "<边界场景 1 — 改用其他方案>"
  - "<边界场景 2 — 改用其他方案>"

# ===== 输入定义 =====
inputs:
  - name: <param_name>
    type: <string | number | array | object>
    required: <true | false>
    default: <默认值（可选）>
    description: <参数说明>
  - name: <param_name_2>
    type: array
    items: { type: string }
    required: false
    description: <参数说明>

# ===== 输出定义 =====
outputs:
  format: <markdown | json | text>
  schema:
    - name: <field_name>
      type: <type>
      description: <字段说明>

# ===== 依赖与约束 =====
requires:
  tools: [<tool-name-1>, <tool-name-2>]
  permissions: [<permission-1>]
  skills: [<other-skill-name>]

# ===== 评估锚点 =====
evaluation:
  offline_dataset: <path-to-eval-set>
  hit_rate_threshold: 0.90
  last_eval_result: <date-and-score>
---
```

**实战：完整的 pr-review-security Skill**

（详见上面"4 阶段流程"中的范例）

---

## 五、Skill 生命周期（写完之后）

```
设计 → 实现 → 测试 → 上线
                    ↓
              监控 hit_rate
                    ↓
        命中率持续 < 85% → 重新设计
        3 个月无调用 → 退役归档
```

**退役标准**：
- 连续 90 天调用次数 < 5
- 或命中率持续 < 70%
- 或被更好的 Skill 替代

退役不是删除，**移到 `skills/retired/`**，保留 frontmatter + 原因说明。

---

## 六、可复用 Checklist（写 Skill 自查）

- [ ] 过了决策树（不是 CLAUDE.md / Hook / Subagent / MCP 的活）
- [ ] frontmatter 6 字段齐全（name / description / when_to_use / when_not_to_use / inputs / outputs）
- [ ] description 第一句是"动词 + 对象 + 边界"
- [ ] when_not_to_use 至少 3 条
- [ ] inputs 有 required + 类型 + 描述
- [ ] 正文 ≤ 300 行（超过就该拆）
- [ ] 有"输出示例"段
- [ ] 有"边界与异常"段
- [ ] 离线评测集 ≥ 30 条，命中率 ≥ 90%
- [ ] 在线埋点接入（invocation_total + hit_rate）

---

## 七、相关章节

**同模块姐妹（写-调双视角）**：
- [Skill 命中率深度章节](skill-hit-rate.md) — 数量爆炸后**怎么调**（四层模型 + 5 反模式 + 实战）

**同模块基础**：
- [Claude Code 大型代码库实践](README.md) — Skill 的"渐进式披露"基础
- [Harness Engineering 体系](../../03-engineering/harness-engineering/README.md) — 上下文工程总论

**面试题（13.split-hairs）**：
- [Skill 设计面试 5 题](../../../13.split-hairs/11.ai/skill-design/README.md) — 配套面试题

**教学场景**：
- [training/lesson4 · Skill 编写与设计模式](../../training/lesson4/README.md) — 教学场景下怎么教新人写 Skill（与本文互补：教学 vs 工程方法论）

---

← [返回 Claude Code 实践总览](README.md)