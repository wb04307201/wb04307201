> ⬅️ [返回目录](README.md)

# Spec-Kit 规范驱动开发（SDD）工具包使用说明

## 📖 目录

1. [工具简介](#工具简介)
2. [核心概念](#核心概念)
3. [标准安装流程](#-标准安装流程)
4. [项目初始化](#-项目初始化)
5. [完整工作流程](#-完整工作流程含可选步骤)
6. [辅助命令](#-辅助命令提升开发质量)
7. [查看当前集成状态](#-查看当前集成状态)
8. [一键切换 AI 代理](#-一键切换-ai-代理)
9. [扩展与定制](#-扩展与定制)
10. [最佳实践建议](#-最佳实践建议)
11. [常见问题](#-常见问题)
12. [学习资源](#-学习资源)

---

## 工具简介

Spec-Kit 是 GitHub 官方开源的 **规范驱动开发（Spec-Driven Development, SDD）** 工具包，通过"规格→计划→任务→实现"的结构化流程，将 AI 从"代码生成工具"转变为"软件开发伙伴"。

> **核心理念**：规格（Specification）成为可执行工件，直接生成工作代码，而非仅作为开发参考。

### 为什么使用 Spec-Kit？

传统开发流程：
```bash
需求 → 代码 → 文档（经常缺失）
```

Spec Kit 流程：
```bash
规范 → 计划 → 任务 → 实现
```

**关键优势**：
- ✅ **提高质量**：通过规范驱动减少返工
- ✅ **加速开发**：AI 理解需求更准确，生成代码更精准
- ✅ **降低风险**：早期发现需求不明确的地方
- ✅ **团队协作**：规范成为团队的共同语言
- ✅ **知识沉淀**：所有决策都有文档记录

---

## 规范驱动开发（SDD）

规范驱动开发是一种软件开发方法论，它将规范文档作为开发的核心驱动力，而不是代码。

**传统开发的问题**：
- 需求不明确就开始编码
- 频繁返工和修改
- 文档经常缺失或过时
- AI 生成代码时理解不准确

**SDD 的优势**：
- 先明确"做什么"，再考虑"怎么做"
- 规范成为可执行文档
- 减少沟通成本
- AI 能更准确地理解需求

---

## 📦 标准安装流程

### 前置条件
| 组件     | 要求                                                   |
|--------|------------------------------------------------------|
| 操作系统   | Linux / macOS / Windows (WSL2)                       |
| Python | ≥ 3.11                                               |
| 包管理器   | `uv`（推荐）或 `pipx`                                     |
| 版本控制   | Git                                                  |
| AI 代理  | Claude Code / GitHub Copilot / Cursor / Gemini CLI 等 |

### 安装 Specify CLI（命令行工具）

```bash
# 【推荐】安装指定稳定版本（替换 vX.Y.Z 为最新 tag）
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# 或安装 main 分支最新版本（可能包含未发布变更）
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 备选方案：使用 pipx
pipx install git+https://github.com/github/spec-kit.git@vX.Y.Z
```

> ⚠️ **重要提示**：官方仅维护从此 GitHub 仓库发布的包。PyPI 上同名包**非官方维护**，请勿使用。

### 验证安装
```bash
specify version
# 输出示例：specify-cli @ git+https://github.com/github/spec-kit.git
```

### 解决"命令未找到"问题（如需要）
```cmd
$env:PATH = "C:\Users\Administrator\.local\bin;$env:PATH"
```

```powershell
uv tool update-shell
```

---

## 🚀 项目初始化

### 创建新项目
```bash
specify init <PROJECT_NAME> --ai <AGENT_NAME>
# 示例：
specify init my-app --ai claude
```

### 在现有项目中启用
```bash
cd /path/to/existing-project
specify init . --ai claude
# 或使用 --here 简写
specify init --here --ai claude

# 强制覆盖（谨慎使用）
specify init . --force --ai claude
```

### 常用 `--ai` 参数值
| 值          | 对应智<br/>能体            |
|------------|-----------------------|
| `copilot`  | GitHub Copilot        |
| `claude`   | Claude Code           |
| `gemini`   | Gemini CLI            |
| `cursor`   | Cursor IDE            |
| `codex`    | OpenAI Codex CLI      |
| `cline`    | Cline (VS Code插件/CLI) |
| `aider`    | Aider (终端CLI)         |
| `roo`      | Roo Code (VS Code插件)  |
| `continue` | Continue (开源扩展)       |
| `windsurf` | Windsurf (原Codeium)   |
| `tabnine`  | Tabnine               |
| `codeium`  | Codeium               |
| `qoder`    | Qoder (阿里云)           |
| `comate`   | Baidu Comate          |
| `lingma`   | 通义灵码 (阿里云)            |
| `trae`     | Trae                  |

---

## 🔧 完整工作流程（含可选步骤）

### 阶段概览

```bash
┌─────────────────────────────────────────────────────────────┐
│  1. /speckit-constitution - 建立项目原则              │
└─────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────┐
│  2. /speckit-specify - 创建功能规范                  │
└─────────────────────────────────────────────────────────────┘
↓
┌──────────────┴──────────────┐
│  可选：/speckit-clarify   │
│  澄清需求                │
└──────────────┬──────────────┘
↓
┌─────────────────────────────────────────────────────────────┐
│  3. /speckit-plan - 创建技术计划                    │
└─────────────────────────────────────────────────────────────┘
↓
┌──────────────┴──────────────┐
│  可选：/speckit-checklist │
│  质量检查清单            │
└──────────────┬──────────────┘
↓
┌─────────────────────────────────────────────────────────────┐
│  4. /speckit-tasks - 分解为任务                     │
└─────────────────────────────────────────────────────────────┘
↓
┌──────────────┴──────────────┐
│  可选：/speckit-analyze    │
│  一致性分析              │
└──────────────┬──────────────┘
↓
┌─────────────────────────────────────────────────────────────┐
│  5. /speckit-implement - 执行实现                   │
└─────────────────────────────────────────────────────────────┘
```

### 详细步骤

#### 步骤 1：建立项目原则 `/speckit-constitution`

**目的**：创建项目的核心原则和开发准则

**输入**：项目原则的描述

**输出**：`.specify/memory/constitution.md`

```bash
# 在 AI 助手对话框中输入：
/speckit-constitution 请生成一套项目原则，重点涵盖：代码质量标准、测试规范（TDD驱动，覆盖率90%）、用户体验一致性要求，以及性能指标（UI响应时间严格控制在100ms以内）。
```

📄 **生成的文档包含**：
- 核心原则（如：测试优先、代码质量、性能标准）
- 技术约束
- 开发流程
- 治理规则

✅ **为什么重要**：
- 指导所有后续开发决策
- 确保团队一致性
- 作为代码审查的依据

---

#### 步骤 2：创建功能规范 `/speckit-specify`

**目的**：用自然语言描述要构建的功能

**关键原则**：
- 专注于"什么"和"为什么"
- 不要涉及"如何实现"
- 从用户视角描述
- 确保可测试和可测量

**输入**：功能描述

**输出**：
- 新的功能分支
- `specs/[###-feature-name]/spec.md`

```bash
/speckit-specify 开发一款任务管理应用，核心功能需支持：
- 任务创建：支持填写任务名称、设置优先级（高/中/低）及截止日期
- 任务筛选：支持按优先级与完成状态进行过滤
- 快捷操作：支持一键标记任务为已完成
注：请严格聚焦于产品功能与业务逻辑（What），无需涉及具体技术选型（How）。
```

📄 **生成的规范包含**：
- 用户场景和故事（按优先级排序）
- 功能需求
- 成功标准（可测量）
- 关键实体
- 边界和约束

---

#### 步骤 2.5（可选）：需求澄清 `/speckit-clarify`

**目的**：在规划之前提出结构化问题，降低模糊领域的风险

**何时使用**：
- 规范中有不明确的地方
- 需要做出重要决策
- 有多个合理的解释

```bash
/speckit-clarify
```

✅ **AI 代理将执行以下操作**：
- **识别模糊点**：自动检测规格中的歧义描述、未明确的边界条件和不完整的需求项
- **生成澄清问题**：针对每个模糊点提出具体的澄清问题，引导用户补充细节
- **完善规格文档**：根据用户回答更新 `spec.md`，确保需求清晰可执行
- **减少返工风险**：在进入技术方案设计前消除理解偏差，避免后续大规模修改

📋 **典型澄清场景**：
- "高优先级"的具体定义是什么？是否有量化标准？
- 离线状态下数据同步的策略是什么？
- 用户权限模型是否需要支持多角色？
- 性能指标的具体阈值是多少？

📋 **输出示例**：
```bash
## 问题 1：数据存储方式

**上下文**：应用需要支持本地存储

**需要知道**：使用哪种本地存储方式？

**建议答案**：

| 选项 | 答案 | 影响 |
|------|------|------|
| A | localStorage | 简单易用，但容量有限（5-10MB） |
| B | IndexedDB | 容量大，但 API 复杂 |
| C | SQLite | 功能强大，但需要额外库 |

**您的选择**：_
```

---

#### 步骤 3：创建技术计划 `/speckit-plan`

**目的**：提供技术栈和架构选择，将功能规范转化为技术设计

**输入**：技术栈和架构选择

**输出**：
- `specs/[###-feature-name]/plan.md`
- `specs/[###-feature-name]/research.md`
- `specs/[###-feature-name]/data-model.md`
- `specs/[###-feature-name]/quickstart.md`
- `specs/[###-feature-name]/contracts/`

```bash
/speckit-plan 技术选型与架构要求：
- UI 实现：采用原生 JavaScript 结合 Web Components 开发
- 数据存储：使用 IndexedDB 进行本地持久化
- 依赖管理：遵循"非必要不引入"原则，严禁无关第三方库
- 架构设计：全面支持离线优先（Offline-First）架构
```

📄 **生成的计划包含**：
- `plan.md` — 架构决策与技术选型
- `data-model.md` — 数据结构定义
- `quickstart.md` — 本地开发指南
- `research.md` — 技术决策与替代方案

---

#### 步骤 3.5（可选）：质量检查清单 `/speckit-checklist`

**目的**：生成需求满足度检查清单，辅助人工审查

```bash
/speckit-checklist
```

📋 **生成内容**：
- 需求验证清单
- 功能完整性检查
- 质量标准符合性检查

---

#### 步骤 4：分解为任务 `/speckit-tasks`

**目的**：将技术计划分解为可执行的独立任务

```bash
/speckit-tasks
```

📄 **输出**：`tasks.md` — 含依赖关系、并行标记 `[P]`、文件路径、测试任务的详细任务清单

**任务列表特点**：
- 按用户故事组织
- 标注依赖关系和执行顺序
- 标记可并行执行的任务 `[P]`
- 每个任务包含明确的文件路径
- 包含对应的测试任务

---

#### 步骤 4.5（可选）：一致性分析 `/speckit-analyze`

**目的**：检查规格、计划、任务之间的一致性

```bash
/speckit-analyze
```

✅ **AI 代理将执行以下检查**：
- **规格与计划一致性**：验证 `spec.md` 中的功能需求是否在 `plan.md` 中有对应的技术方案
- **计划与任务对齐**：确认 `plan.md` 中的技术决策是否完整体现在 `tasks.md` 的任务分解中
- **依赖关系验证**：检查任务依赖链是否合理，是否存在循环依赖或遗漏的前置条件
- **覆盖度分析**：识别未被任何任务覆盖的规格需求，或被任务实现但规格中未定义的功能（范围蔓延）
- **冲突检测**：发现技术方案之间的潜在冲突（如数据库选型与性能要求的矛盾）

📋 **输出**：分析报告，列出所有不一致项、缺失项和建议修复方案

---

#### 步骤 5：执行实现 `/speckit-implement`

**目的**：按照任务列表执行代码实现

```bash
/speckit-implement
```

✅ **AI 代理将**：
- 按任务顺序执行（尊重依赖关系）
- 自动创建/修改文件
- 运行测试并报告结果
- 在 `tasks.md` 中标记完成状态

---

## 🎯 辅助命令（提升开发质量）

| 命令                   | 作用               | 使用时机                              | 输出内容                  |
|----------------------|------------------|-----------------------------------|-----------------------|
| `/speckit-clarify`   | 识别规格模糊点，引导用户澄清   | 在 `/specify` 之后，`/plan` 之前（可选）    | 结构化问题列表，帮助用户明确需求细节    |
| `/speckit-analyze`   | 检查规格/计划/任务之间的一致性 | 在 `/tasks` 之后，`/implement` 之前（可选） | 一致性分析报告，列出不一致项和建议修复方案 |
| `/speckit-checklist` | 生成需求验证清单         | 在 `/plan` 之后或实现完成后审查（可选）          | 需求满足度检查清单，辅助人工审查      |

**使用建议**：
- **简单项目**：可以跳过可选步骤，直接执行核心流程
- **复杂项目**：建议使用所有可选步骤，确保质量和一致性
- **团队协作**：强烈建议使用 `/clarify` 和 `/analyze`，减少沟通成本

---

## 🔌 扩展与定制

### 安装社区扩展
```bash
# 搜索可用扩展
specify extension search

# 安装扩展（如 Jira 集成）
specify extension add jira-integration
```

### 应用预设模板
```bash
# 搜索预设
specify preset search

# 应用组织规范预设
specify preset add enterprise-security
```

### 优先级覆盖机制
```bash
1️⃣ 项目本地覆盖: .specify/templates/overrides/  (最高)
2️⃣ 预设模板:     .specify/presets/templates/
3️⃣ 扩展模板:     .specify/extensions/templates/
4️⃣ 核心模板:     .specify/templates/           (最低)
```

---

## 🔍 查看当前集成状态

Spec-Kit v0.8+ 提供了 `specify integration` 子命令族，专门用于管理 AI 编码代理的集成。

### 命令总览

```bash
specify integration list       # 列出所有可用集成及当前已安装的
specify integration install     # 安装一个集成到已有项目
specify integration switch      # 一键切换（卸载旧 + 安装新）
specify integration uninstall   # 安全卸载当前集成
specify integration upgrade     # 升级当前集成（重新安装，感知文件差异）
```

### 查看环境已安装的工具

```bash
# 检查当前环境已安装的 AI 代理及工具状态
specify check
```

**输出示例**：
```
✓ Git 2.45.0
✓ Claude Code (claude) — 已安装
✗ Gemini CLI (gemini) — 未安装
✓ Cursor (cursor) — 已安装
✗ Codex CLI (codex) — 未安装
```

该命令会检测 `AGENT_CONFIG` 中配置的所有基于 CLI 的代理，包括：
`claude`、`gemini`、`copilot`、`cursor-agent`、`qwen`、`opencode`、`codex`、`windsurf`、`junie`、`kilocode`、`auggie`、`roo`、`codebuddy`、`amp`、`shai`、`kiro-cli`、`agy`、`bob`、`qodercli`、`vibe`、`kimi`、`iflow`、`pi` 等。

### 查看项目当前使用的集成

```bash
# 进入已初始化的项目目录
cd my-project

# 查看当前项目和可用集成
specify integration list
```

**输出示例**：
```
Coding Agent Integrations
┌──────────────┬────────────────────────────────┬───────────┬──────────────┐
│ Key          │ Name                           │ Status    │ CLI Required │
├──────────────┼────────────────────────────────┼───────────┼──────────────┤
│ claude       │ Claude Code                    │ installed │ yes          │
│ copilot      │ GitHub Copilot                 │           │ no (IDE)     │
│ gemini       │ Gemini CLI                     │           │ yes          │
│ ...          │ ...                            │           │ ...          │
└──────────────┴────────────────────────────────┴───────────┴──────────────┘

Current integration: claude
```

> **提示**：`specify integration list --catalog` 需在项目目录下使用（需 `.specify/` 目录存在）。

### 查看当前集成的文件结构

```bash
# 查看当前使用的 AI 代理
cat .specify/integration.json
# 输出: {"integration": "claude", "version": "0.8.2.dev0"}

# 查看已安装的斜杠命令（以 Claude Code 为例）
ls .claude/skills/    # Claude Code 使用 skills 目录
```

项目初始化后，关键目录结构如下：

```
项目根目录/
├── .specify/
│   ├── integration.json          # 当前集成标识
│   ├── integrations/
│   │   ├── claude.manifest.json  # 集成清单（追踪文件状态）
│   │   └── speckit.manifest.json # Speckit 核心清单
│   ├── scripts/powershell/       # 自动化脚本（sh 或 ps1）
│   ├── templates/                # 模板文件
│   ├── specs/                    # 功能规格目录
│   └── memory/                   # 项目章程等
├── .claude/                      # Claude Code 专属目录
│   └── skills/                   # 斜杠命令文件
├── CLAUDE.md                     # Claude Code 项目说明
└── ...
```

---

## 🔄 一键切换 AI 代理

### 方式一：`specify integration switch`（推荐 ✅）

这是最干净的方式，一步完成"卸载旧 agent + 安装新 agent"，同时保留你的 specs、plan、tasks 等核心产出。

```bash
# 先查看当前安装了哪些 agent
specify integration list

# 一键切换到新 agent（例如从 copilot 切换到 claude）
specify integration switch claude

# 如果切换过程中有手动修改过的文件，需要加 --force
specify integration switch claude --force

# 验证切换结果
specify integration list
```

**行为说明**：
1. 自动卸载当前集成（移除 `.claude/` 或 `.gemini/` 等专属目录）
2. 保留 `.specify/` 下的共享基础设施（scripts、templates、specs、memory）
3. 安装新集成（写入新 agent 的命令文件到对应目录，如 `.gemini/commands/`）
4. 更新 `.specify/integration.json` 指向新集成

**⚠️ 注意**：`switch` 会**移除旧 agent 的专属目录**。例如从 claude 切换到 gemini 后，`.claude/` 会被删除，`.gemini/` 会被创建。**同一时刻只有一个"当前"集成**。

### 方式二：先 uninstall 再 install（分步切换）

适用于需要中间检查或分步执行的场景：

```bash
# 先卸载当前集成（保留修改过的文件）
specify integration uninstall

# 再安装新 agent
specify integration install claude

# 验证
specify integration list
# 输出: Current integration: claude
```

### 卸载当前集成

```bash
# 卸载当前集成（安全保留修改过的文件）
specify integration uninstall

# 强制卸载（包括修改过的文件）
specify integration uninstall --force
```

### 升级当前集成

```bash
# 重新安装当前集成，检测本地修改过的文件
specify integration upgrade

# 强制升级（覆盖本地修改）
specify integration upgrade --force
```

### 多个 Agent 如何共存？

Spec-Kit 的 `integration` 子命令采用**单当前集成模型**——同一时刻项目只有一个"当前"集成（由 `.specify/integration.json` 记录）。

**`specify integration install` 不支持多 agent 同时安装**——如果已有集成，会报错并提示先 uninstall 或使用 switch：

```
Error: Integration 'gemini' is already installed.
Run specify integration uninstall first, or use specify integration switch claude.
```

**`specify init . --ai <agent>` 也不会正确追加第二个 agent**——实测发现它只是清理了旧 manifest，但不会写入新 agent 的命令文件。

**如果需要多 agent 并存，唯一可靠的方式是手动保留旧 agent 目录：**

```bash
# 备份当前 agent 的命令文件
cp -r .claude .claude.bak

# 切换到新 agent
specify integration switch gemini

# 此时 .claude.bak 仍然保留，需要时可以恢复
# 恢复时：cp -r .claude.bak .claude
```

共存时的目录结构（两个 agent 的命令文件同时存在）：

```
项目根目录/
├── .claude.bak/skills/   # 手动备份的 Claude Code 技能
├── .gemini/commands/     # Gemini CLI 的命令文件
├── .specify/             # ← 所有 agent 共享的规格目录
│   ├── integration.json    # 当前集成: gemini
│   └── ...
└── ...
```

> ⚠️ **注意**：手动保留的目录不在集成管理范围内，后续 `switch` 或 `upgrade` 不会触及它们。

### 切换后的兼容性说明

| 场景 | 兼容性 | 说明 |
|------|--------|------|
| 章程 (constitution.md) | ✅ 完全兼容 | 所有 agent 读取同一份章程 |
| 规格 (spec.md) | ✅ 完全兼容 | 规格与技术无关 |
| 计划 (plan.md) | ⚠️ 可能需要调整 | 不同 agent 生成的技术方案可能不同 |
| 任务 (tasks.md) | ✅ 完全兼容 | 任务分解独立于 agent |
| 脚本 (.sh/.ps1) | ✅ 自动保留 | 已存在则不会被覆盖 |
| 模板 (templates/) | ✅ 自动保留 | 已存在则不会被覆盖 |
| 项目说明 (CLAUDE.md 等) | ✅ 保留 | 手动修改过则不会被删除 |
| `.vscode/settings.json` | ✅ 保留 | IDE 配置文件保留 |

### 自带 Agent（Generic 模式）

如果使用的 agent 不在预置列表中，可以使用 `generic` 模式：

```bash
# 先确保没有当前集成（如有则先 uninstall）
specify integration uninstall

# 安装 generic 模式 — 指定命令文件目录
specify integration install generic --integration-options="--commands-dir .myagent/cmds"
```

### 完整切换流程（实测验证 ✅）

以下流程经过本地 CLI（v0.8.2.dev0）实际验证：

```bash
# 第 1 步：查看当前状态
specify integration list
# 输出: Current integration: copilot

# 第 2 步：一键切换（例如 copilot → claude）
specify integration switch claude
# 输出:
#   Uninstalling current integration: copilot
#     Removed 19 file(s)
#   ⚠  9 shared infrastructure file(s) already exist and were not updated:
#       .specify\scripts\powershell\...
#       .specify\templates\...
#   Installing integration: claude
#   ✓ Switched to integration 'Claude Code'

# 第 3 步：验证切换结果
specify integration list
# 输出: Current integration: claude

# 第 4 步：确认文件状态
ls .claude/skills/    # 应看到 9 个 SKILL.md 文件
ls .github/ 2>/dev/null   # 应不存在（旧 agent 目录已移除）
```

### 最佳实践

```bash
# ✅ 推荐：在 Git 分支中切换，便于回滚
git checkout -b switch-to-gemini
specify integration switch gemini

# ✅ 推荐：需要保留旧 agent 命令文件时先备份
cp -r .claude .claude.bak
specify integration switch gemini

# ✅ 推荐：切换后用新 agent 重新打开终端
# 确保新 agent 加载了对应的斜杠命令/技能文件

# ⚠️ 注意：不要混用 init 和 integration 命令来切换 agent
# specify init . --ai gemini 在已有集成的项目中不会正确工作
# 请始终使用 specify integration switch <agent>
```

---

## 💡 最佳实践建议

### 1. 先写原则再写规格
在 `constitution.md` 中明确技术边界，避免 AI"自由发挥"。项目原则应该包括：
- 代码质量标准（如：ESLint 规则、代码复杂度限制）
- 测试规范（如：TDD 驱动、覆盖率要求）
- 性能指标（如：响应时间、加载速度）
- 安全要求（如：输入验证、数据加密）

### 2. 规格聚焦业务价值
`/speckit-specify` 阶段只描述 **做什么** 和 **为什么**，不涉及技术实现。
- ✅ 好："用户可以按优先级筛选任务"
- ❌ 坏："使用 SQL WHERE 子句查询 priority 字段"

### 3. 善用可选步骤
根据项目复杂度灵活使用 `/speckit-clarify`、`/speckit-analyze` 和 `/speckit-checklist` 提升质量：
- **个人小项目**：可以跳过可选步骤
- **团队项目**：建议使用 `/clarify` 消除歧义
- **关键系统**：建议使用所有可选步骤

### 4. 迭代优于一次到位
需求变更时，遵循以下流程：
```bash
修改 spec.md → 重跑 /speckit-plan → /speckit-tasks → /speckit-implement
```
不要直接在代码层面修改，保持规范与代码同步。

### 5. 版本控制先行
所有操作在 Git 分支中进行，便于回溯和协作：
```bash
# 为每个功能创建独立分支
git checkout -b feature/task-filter

# 完成后再合并到主分支
git merge feature/task-filter
```

### 6. 用户故事要独立可测试
每个用户故事应该是：
- **独立的**：不依赖其他故事
- **可测试的**：有明确的验收标准
- **可交付的**：完成后即可使用
- **按优先级排序**：P1 > P2 > P3

### 7. 技术计划要考虑约束
在 `/speckit-plan` 阶段，必须考虑：
- 项目原则中的约束
- 现有技术栈的限制
- 团队技能水平
- 性能和安全性要求

### 8. 任务分解要粒度适中
任务应该：
- 足够小：可以在 1-2 小时内完成
- 足够大：有明确的功能意义
- 有依赖关系：标注前置任务
- 可并行：标记 `[P]` 的任务可以并行执行

---

## 🔍 常见问题

### 安装相关

| 问题                           | 解决方案                                                                                      |
|------------------------------|-------------------------------------------------------------------------------------------|
| `specify: command not found` | 将 `uv tool` 的 bin 目录加入 `PATH`。Windows: `$env:PATH = "C:\Users\[用户]\.local\bin;$env:PATH"` |
| Python 版本过低                  | 升级 Python 到 ≥ 3.11                                                                        |
| uv 安装失败                      | 尝试使用 pipx：`pipx install git+https://github.com/github/spec-kit.git`                       |

### 使用相关

| 问题           | 解决方案                                                        |
|--------------|-------------------------------------------------------------|
| AI 生成代码不符合规范 | 检查 `constitution.md` 是否明确，或在 `/speckit-specify` 后使用 `/speckit-clarify` 补充细节 |
| 需求变更后如何同步    | 修改 `spec.md` → 重跑 `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`         |
| 任务执行顺序错误     | 检查 `tasks.md` 中的依赖关系，确保前置任务已完成                              |
| 规格与技术计划不一致   | 运行 `/speckit-analyze` 检查一致性，根据报告修复                          |

### 企业环境

| 问题              | 解决方案                                                                               |
|-----------------|------------------------------------------------------------------------------------|
| 企业内网无法访问 GitHub | 参考 [Air-Gapped 安装指南](https://github.io/spec-kit/enterprise-airgapped.html)  <!-- 链接需核实 --> |
| 需要自定义模板         | 在 `.specify/templates/overrides/` 中放置自定义模板                                         |
| 团队协作冲突          | 使用 Git 分支管理，定期同步 constitution.md 和项目规范                                             |

---

## 📚 学习资源

- 🌐 [官方文档](https://github.io/spec-kit/)  <!-- 链接需核实 -->
- 🎬 [视频概览](https://github.io/spec-kit/video-overview)  <!-- 链接需核实 -->
- 📖 [详细方法论](https://github.io/spec-kit/methodology)  <!-- 链接需核实 -->
- 💬 [社区讨论](https://github.com/github/spec-kit/discussions)

> Spec-Kit 的核心价值：**让开发者聚焦"做什么"，让 AI 专注"怎么做"**，实现需求与代码的同步演化。