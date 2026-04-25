# Spec-Kit 规范驱动开发（SDD）工具包使用说明

## 工具简介

Spec-Kit 是 GitHub 官方开源的 **规范驱动开发（Spec-Driven Development, SDD）** 工具包，通过"规格→计划→任务→实现"的结构化流程，将 AI 从"代码生成工具"转变为"软件开发伙伴"。

> **核心理念**：规格（Specification）成为可执行工件，直接生成工作代码，而非仅作为开发参考。

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
```bash
# macOS/Linux: 将 bin 目录添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🚀 项目初始化

### 创建新项目
```bash
specify init <PROJECT_NAME> --ai <AGENT_NAME>
# 示例：
specify init my-app --ai copilot
```

### 在现有项目中启用
```bash
cd /path/to/existing-project
specify init . --ai copilot
# 或使用 --here 简写
specify init --here --ai copilot

# 强制覆盖（谨慎使用）
specify init . --force --ai copilot
```

### 常用 `--ai` 参数值
| 值         | 对应 AI 代理         |
|-----------|------------------|
| `copilot` | GitHub Copilot   |
| `claude`  | Claude Code      |
| `gemini`  | Gemini CLI       |
| `cursor`  | Cursor IDE       |
| `codex`   | OpenAI Codex CLI |

---

## 🔧 核心工作流：8 步完成从规格到代码

```
┌─────────────────────────────────────────┐
│  /speckit.constitution → 项目原则        │
│  /speckit.specify     → 功能规格         │
│  /speckit.clarify     → 需求澄清（推荐）  │
│  /speckit.plan        → 技术方案         │
│  /speckit.tasks       → 任务分解         │
│  /speckit.analyze     → 一致性分析（推荐）│
│  /speckit.implement   → 代码实现         │
│  /speckit.checklist   → 质量检查（可选）  │
└─────────────────────────────────────────┘
```

### Step 1: 建立项目原则 `/speckit.constitution`
```bash
# 在 AI 助手对话框中输入：
/speckit.constitution Create principles focused on code quality, 
testing standards (TDD with 90% coverage), user experience consistency, 
and performance requirements (UI response <100ms).
```
📄 输出：`.specify/memory/constitution.md` — 项目治理准则

### Step 2: 定义功能规格 `/speckit.specify`
```bash
/speckit.specify Build a task management app where users can:
- Create tasks with name, priority (high/medium/low), and due date
- Filter tasks by priority and completion status
- Mark tasks as complete with one click
Focus on WHAT the app does, not the tech stack.
```
📄 输出：`specs/001-feature-name/spec.md` — 含用户故事、功能需求、成功标准

### Step 3（推荐）: 需求澄清 `/speckit.clarify`
```bash
/speckit.clarify
```
✅ AI 代理将执行以下操作：
- **识别模糊点**：自动检测规格中的歧义描述、未明确的边界条件和不完整的需求项
- **生成澄清问题**：针对每个模糊点提出具体的澄清问题，引导用户补充细节
- **完善规格文档**：根据用户回答更新 `spec.md`，确保需求清晰可执行
- **减少返工风险**：在进入技术方案设计前消除理解偏差，避免后续大规模修改

📋 典型澄清场景：
- "高优先级"的具体定义是什么？是否有量化标准？
- 离线状态下数据同步的策略是什么？
- 用户权限模型是否需要支持多角色？
- 性能指标的具体阈值是多少？

### Step 4: 生成技术方案 `/speckit.plan`
```bash
/speckit.plan Use vanilla JavaScript with Web Components for UI.
Store data in IndexedDB. No external dependencies unless essential.
Support offline-first architecture.
```
📄 输出：
- `plan.md` — 架构决策与技术选型
- `data-model.md` — 数据结构定义
- `quickstart.md` — 本地开发指南

### Step 5: 分解任务列表 `/speckit.tasks`
```bash
/speckit.tasks
```
📄 输出：`tasks.md` — 含依赖关系、并行标记 `[P]`、文件路径、测试任务的详细任务清单

### Step 6（推荐）: 一致性分析 `/speckit.analyze`
```bash
/speckit.analyze
```
✅ AI 代理将执行以下检查：
- **规格与计划一致性**：验证 `spec.md` 中的功能需求是否在 `plan.md` 中有对应的技术方案
- **计划与任务对齐**：确认 `plan.md` 中的技术决策是否完整体现在 `tasks.md` 的任务分解中
- **依赖关系验证**：检查任务依赖链是否合理，是否存在循环依赖或遗漏的前置条件
- **覆盖度分析**：识别未被任何任务覆盖的规格需求，或被任务实现但规格中未定义的功能（范围蔓延）
- **冲突检测**：发现技术方案之间的潜在冲突（如数据库选型与性能要求的矛盾）

📋 输出：分析报告，列出所有不一致项、缺失项和建议修复方案

### Step 8（可选）: 质量检查 `/speckit.checklist`
```bash
/speckit.checklist
```
📋 生成需求满足度检查清单，辅助人工审查

---

## 🎯 辅助命令（提升开发质量）

| 命令                   | 作用               | 使用时机                    |
|----------------------|------------------|-------------------------|
| `/speckit.clarify`   | 识别规格模糊点,引导用户澄清   | 在 `/plan` 之前            |
| `/speckit.analyze`   | 检查规格/计划/任务之间的一致性 | 在 `/implement` 之前（强烈推荐） |
| `/speckit.checklist` | 生成需求验证清单         | 实现完成后审查                 |

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
```
1️⃣ 项目本地覆盖: .specify/templates/overrides/  (最高)
2️⃣ 预设模板:     .specify/presets/templates/
3️⃣ 扩展模板:     .specify/extensions/templates/
4️⃣ 核心模板:     .specify/templates/           (最低)
```

---

## 💡 最佳实践建议

1. **先写原则再写规格**：在 `constitution.md` 中明确技术边界，避免 AI"自由发挥"
2. **规格聚焦业务价值**：`/specify` 阶段只描述 **做什么** 和 **为什么**，不涉及技术实现
3. **迭代优于一次到位**：需求变更时，先更新 `spec.md`，再重新运行 `/plan → /tasks → /implement`
4. **善用澄清命令**：对模糊需求主动使用 `/clarify`，减少返工
5. **版本控制先行**：所有操作在 Git 分支中进行，便于回溯和协作

---

## 🔍 常见问题

| 问题                           | 解决方案                                                                               |
|------------------------------|------------------------------------------------------------------------------------|
| `specify: command not found` | 将 `uv tool` 的 bin 目录加入 `PATH`                                                      |
| AI 生成代码不符合规范                 | 检查 `constitution.md` 是否明确，或用 `/clarify` 补充细节                                       |
| 需求变更后如何同步                    | 修改 `spec.md` → 重跑 `/plan` → `/tasks` → `/implement`                                |
| 企业内网无法访问 GitHub              | 参考 [Air-Gapped 安装指南](https://github.github.com/spec-kit/enterprise-airgapped.html) |

---

## 📚 学习资源

- 🌐 [官方文档](https://github.github.com/spec-kit/)
- 🎬 [视频概览](https://github.github.com/spec-kit/video-overview)
- 📖 [详细方法论](https://github.github.com/spec-kit/methodology)
- 💬 [社区讨论](https://github.com/github/spec-kit/discussions)

> Spec-Kit 的核心价值：**让开发者聚焦"做什么"，让 AI 专注"怎么做"**，实现需求与代码的同步演化。