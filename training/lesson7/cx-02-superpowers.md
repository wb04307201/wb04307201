> ⬅️ [返回目录](README.md)

# Codex Superpowers 安装与使用

> **一句话定位**：Superpowers 是一套跨 Agent 的**结构化开发方法论**（⭐ 255K+ stars）——Codex CLI 和 Codex App 均可通过**官方插件市场**一键安装，也可手动通过 AGENTS.md 集成。

← [Codex CLI 配置](cx-01-cli.md) · [Claude Code 插件系统](cc-02-plugins.md) · [MCP 推荐](sh-01-mcp.md)

---

## 0. Superpowers 是什么

Superpowers（[obra/superpowers](https://github.com/obra/superpowers)）是一个为 AI 编码 Agent 提供**结构化开发方法论**的技能框架。它不是让 Agent "更聪明"，而是**约束 Agent 的工作流程**——不让它直接跳到写代码，而是强制执行 需求澄清 → 计划 → TDD → 审查 的工程化流程。

**核心工作流**（5 步闭环）：

```
brainstorming → writing-plans → subagent-driven-development → TDD → code-review
  (需求澄清)     (实施计划)        (子 Agent 执行)            (测试驱动)  (代码审查)
```

### 技能清单

| 技能 | 能力 | 触发时机 |
|------|------|---------|
| **brainstorming** | 需求澄清、方案探索、设计文档 | 用户提出新功能时自动激活 |
| **writing-plans** | 拆解为 2-5 分钟粒度的任务 | 设计确认后 |
| **using-git-worktrees** | 创建隔离工作空间（新分支） | 计划确认后 |
| **subagent-driven-development** | 每个任务派子 Agent 执行 + 两阶段审查 | 计划批准后 |
| **executing-plans** | 批量执行 + 人类检查点 | 替代 subagent 模式 |
| **test-driven-development** | 🔴 Red → 🟢 Green → 🔵 Refactor | 实现过程中自动强制 |
| **systematic-debugging** | 复现→隔离→假设→验证→修复 | 遇到 bug 时 |
| **code-review** | 多维度审查（正确性/性能/安全/可读性） | 提交前 |
| **verification-before-completion** | 完成前自检 | 任务结束前 |
| **writing-skills** | 创建自定义技能 | 用户要求自定义工作流 |
| **finishing-a-development-branch** | 收尾、合并、清理 | 分支开发完成 |

---

## 一、跨 Agent 对比

Superpowers 支持 10+ 个 Agent，以下是三大 Agent 的安装差异：

| 维度 | Claude Code | Codex CLI | OpenCode |
|------|------------|-----------|----------|
| **安装命令** | `/plugin install superpowers@claude-plugins-official` | `/plugins` → search `superpowers` → Install | 读取 INSTALL.md 指令 |
| **项目指令文件** | `CLAUDE.md` | `AGENTS.md` | `.opencode/` 配置 |
| **插件目录** | `.claude-plugin` | `.codex-plugin` | `.opencode` |
| **技能目录** | `.claude/skills/` | `.codex/skills/` | 通过配置加载 |
| **插件市场** | 官方 + Superpowers 市场 | 官方市场 | 手动安装 |
| **Hooks 系统** | `settings.json` | 不支持 | 不支持 |

**关键洞察**：三者共享同一套技能文件（`skills/` 目录），差异仅在于**加载机制**。Superpowers 的仓库为每个 Agent 维护独立的插件包装（`.claude-plugin` / `.codex-plugin` / `.opencode` 等）。

---

## 二、安装方式

### 方式一：插件市场安装（推荐）

**Codex CLI**：

```bash
# 1. 打开插件界面
/plugins

# 2. 搜索 superpowers
superpowers

# 3. 选择 Install Plugin
```

**Codex App**（桌面版）：

1. 点击侧边栏的 **Plugins**
2. 在 **Coding** 分类中找到 **Superpowers**
3. 点击 **+** 安装，按提示操作

### 方式二：手动安装（适合离线 / 自定义）

```bash
# 在项目根目录 clone superpowers 仓库
cd your-project/
git clone https://github.com/obra/superpowers.git .codex/superpowers
```

然后在项目根目录创建 `AGENTS.md`，添加加载指令：

```markdown
# AGENTS.md

## Superpowers

你是一个配备了 Superpowers 技能体系的 AI 编码 Agent。
在开始任何任务前，读取 `.codex/superpowers/skills/` 目录中的技能定义，
按技能触发条件自动应用对应的工作流程。

核心规则：
1. 新功能需求 → brainstorming → writing-plans → 执行
2. 写代码 → TDD（先写测试）
3. 遇 bug → systematic-debugging
4. 提交前 → code-review + verification-before-completion
```

### 方式三：AGENTS.md 跨工具方案

如果你同时使用多个 Agent（Codex + Cursor + Amp），可以在项目根目录放一个 `AGENTS.md`，所有工具都会读取：

```markdown
# AGENTS.md

## 开发规范
- 所有新功能必须先写设计文档（brainstorming）
- 代码实现遵循 TDD 红-绿-重构循环
- 提交前必须通过 code-review
```

这个文件会被 Codex、Cursor、Amp 等多个 Agent 自动识别。

---

## 三、核心工作流详解

### 3.1 brainstorming（需求澄清）

Agent 不会直接写代码，而是先通过提问澄清需求：

1. **提问阶段**：问 2-3 个关键问题（目标、约束、边界条件）
2. **方案阶段**：生成 3 个候选方案（每个有 pros/cons/trade-offs）
3. **确认阶段**：用户选择后，输出分段可读的设计文档

**Codex 使用示例**：
```
> 帮我 brainstorming：我想给项目加用户权限系统
```

### 3.2 writing-plans（实施计划）

将设计文档拆解为可执行任务：

- 每个任务 **2-5 分钟**粒度
- 包含**精确文件路径**、完整代码、验证步骤
- 任务间标注依赖关系

### 3.3 subagent-driven-development（子 Agent 执行）

每个任务派一个**新的子 Agent** 执行，带两阶段审查：

1. **阶段一**：是否符合规范（spec compliance）
2. **阶段二**：代码质量审查（code quality）

Agent 可以自主工作数小时，不偏离你批准的计划。

### 3.4 test-driven-development（TDD 强制）

Superpowers **强制** TDD 循环，不允许跳过：

| 阶段 | 动作 | 约束 |
|------|------|------|
| 🔴 Red | 先写失败的测试 | 不写实现代码 |
| 🟢 Green | 写**最少**代码让测试通过 | 不做多余的事 |
| 🔵 Refactor | 重构，保持测试绿色 | YAGNI + DRY |

### 3.5 code-review（多维度审查）

| 维度 | 检查内容 |
|------|---------|
| 正确性 | 逻辑 bug、边界条件 |
| 性能 | 时间/空间复杂度、N+1 查询 |
| 安全 | 注入、认证、数据泄漏 |
| 可读性 | 命名、注释、代码组织 |
| 简化 | 重复代码、过度设计 |

---

## 四、进阶配置

### 4.1 自定义技能

在项目的 `.codex/skills/` 下创建 `SKILL.md` 格式的自定义技能：

```markdown
<!-- .codex/skills/deploy/SKILL.md -->
# 部署技能

## 触发条件
用户说"部署到生产环境"

## 流程
1. 运行测试：`npm test`
2. 构建：`npm run build`
3. 检查环境变量：确认 `.env.production` 存在
4. 执行部署：`./deploy.sh`
5. 验证：`curl https://api.example.com/health`
```

### 4.2 多层 AGENTS.md

| 位置 | 作用域 | 典型用途 |
|------|--------|---------|
| `~/.codex/AGENTS.md` | 全局 | 个人偏好（代码风格、语言） |
| `<project>/AGENTS.md` | 项目级 | 项目规范 + Superpowers 加载 |
| `<project>/src/AGENTS.md` | 目录级 | 特定目录的编码规范 |

### 4.3 与 MCP 工具配合

| 技能 | 推荐 MCP | 效果 |
|------|---------|------|
| brainstorming | Sequential Thinking | 结构化方案推理 |
| code-review | GitHub MCP | 自动读取 PR diff |
| TDD | Playwright MCP | E2E 测试自动化 |
| systematic-debugging | Chrome DevTools MCP | 前端性能追踪 |

### 4.4 更新 Superpowers

```bash
# 插件市场安装的
/plugins → superpowers → Update

# 手动 clone 安装的
cd .codex/superpowers && git pull
```

---

## 五、常见问题

### Q1：安装后 Codex 没有自动使用 Superpowers？

- 确认安装成功：`/plugins` 列表中能看到 superpowers
- 在项目 AGENTS.md 中显式引用："请按 Superpowers 的 brainstorming 流程"
- 新会话中首次使用时可能需要手动触发

### Q2：Superpowers 的 Skills 和 Codex 原生 Skills 有什么区别？

| 维度 | Superpowers Skills | Codex 原生 Skills |
|------|-------------------|-----------------|
| 来源 | obra/superpowers 社区 | OpenAI 官方 + 社区 |
| 格式 | SKILL.md（文本指令） | SKILL.md（相同格式） |
| 定位 | 完整开发方法论 | 单一任务能力 |
| 关系 | 互补（Superpowers 管流程，原生 Skills 管能力） |

### Q3：可以只用部分技能吗？

可以。在 AGENTS.md 中只列出你想启用的技能：

```markdown
## Superpowers（精简版）
只使用以下技能：brainstorming、writing-plans、code-review
不使用：subagent-driven-development、using-git-worktrees
```

---

## 六、相关章节

- 前置：[Codex CLI 配置指南](cx-01-cli.md) — Codex 安装与百炼模型配置
- 通用 MCP：[MCP 推荐](sh-01-mcp.md) — 可配合的 MCP 服务器
- Claude Code 版：[Claude Code 插件系统](cc-02-plugins.md) — Claude Code 的 Superpowers
- Claude Code Skills：[Skills 深度解析](cc-03-skills.md) — Skills 架构详解
- 规范驱动：[SDD 工具对比](sh-02-sdd.md) — Spec-Kit / Kiro / OpenSpec
- 实战案例：[实战 Harness 工程 (PDF)](实战Harness工程 V1.4.pdf) — Superpowers 实战

---

## 📚 参考来源

- [obra/superpowers](https://github.com/obra/superpowers) — Superpowers 官方仓库（255K+ ⭐）
- [Codex CLI Guide 2026](https://blakecrosley.com/guides/codex) — AGENTS.md + Skills + MCP 完整指南
- [The Ultimate Codex Skills Directory](https://www.rzlt.io/blog/the-ultimate-openai-codex-skills-directory---2026) — Codex 技能生态 2026
- [Skills Are the New Agent OS](https://www.developersdigest.tech/blog/skills-are-the-new-agent-operating-system) — 技能即 Agent 操作系统
- [OpenAI Codex AGENTS.md Guide](https://www.oflight.co.jp/en/columns/openai-codex-agents-md-custom-config-guide-2026) — AGENTS.md 配置最佳实践

---

← [返回课程目录](README.md)
