## 一、用 Claude Code 提取架构信息
Claude Code 本身不提供一键“架构提取”命令，但可通过**文件读取 + 上下文分析 + 结构化输出**高效完成。

### 1. 准备项目上下文（Windows PowerShell）
```powershell
# 1. 生成干净的目录树（排除依赖/构建产物）
# 方法一：使用 tree 命令（Windows 自带）
tree /F /A | Out-File -Encoding UTF8 ARCHITECTURE_TREE.txt

# 方法二：使用 Get-ChildItem 递归列出（推荐，更灵活）
Get-ChildItem -Recurse -Depth 4 -Exclude 'node_modules','dist','build','.git','.vscode','.idea' | 
    Where-Object { $_.FullName -notmatch '\\(node_modules|dist|build|\.git|\.vscode|\.idea)\\' } | 
    Select-Object FullName, Length | 
    Format-Table -AutoSize | 
    Out-File -Encoding UTF8 ARCHITECTURE_TREE.txt

# 2. 收集关键配置与依赖快照（Windows 方式）
Get-Content package.json, tsconfig.json, vite.config.ts, next.config.ts | Out-File -Encoding UTF8 CONFIGS.md
Get-Content backend/package.json, backend/tsconfig.json | Out-File -Encoding UTF8 BACKEND_CONFIGS.md  # 如有独立后端
```

### 2. 核心分析 Prompt（直接喂给 Claude Code）
```text
你正在分析一个已有前后端项目的架构。请基于以下文件内容，输出结构化架构画像：

📁 目录树：
[粘贴 ARCHITECTURE_TREE.txt]

⚙️ 前端配置：
[粘贴 CONFIGS.md]

⚙️ 后端配置（如有）：
[粘贴 BACKEND_CONFIGS.md]

请输出以下结构化内容（JSON 格式）：
1. frontend_architecture:
   - framework & version
   - routing strategy (e.g., file-based, dynamic, nested)
   - state management (e.g., Redux, Zustand, React Query, Context)
   - component organization (feature-based, domain-driven, atomic?)
   - styling approach (CSS Modules, Tailwind, SCSS, CSS-in-JS?)
   - API layer pattern (fetch, axios, RTK Query, tRPC, OpenAPI client?)
   - testing stack
2. backend_architecture:
   - framework & version
   - routing & controller structure
   - service/repository pattern usage
   - ORM/DB layer
   - auth & middleware stack
   - API style (REST, GraphQL, RPC?)
   - testing & validation strategy
3. cross_cutting_concerns:
   - error handling pattern
   - environment/config management
   - logging & monitoring
   - deployment & CI/CD hints
```

Claude Code 会返回结构化分析结果，你可保存为 `ARCHITECTURE_PROFILE.md` 或 `architecture.json`。

---
## 二、将架构信息转化为开发规范
将提取的“事实架构”转化为“约定规范”，需区分**强制规则**与**推荐实践**。

### 1. 规范维度映射表
| 架构发现点              | 对应规范条目                                                     | 落地方式                                       |
|--------------------|------------------------------------------------------------|--------------------------------------------|
| `feature/` 目录结构    | 模块边界规范：按业务域划分，禁止跨域直接引用                                     | ESLint `import/no-relative-parent-imports` |
| `React Query` 数据获取 | API 层规范：禁止在组件内直接 fetch，统一使用 `@/services`                   | 自定义 ESLint rule / TypeScript 接口约束          |
| `Zustand` 状态管理     | 状态规范：全局状态仅存放跨模块共享数据，局部状态用 `useState`                       | 架构文档 + PR 模板检查项                            |
| `Express + Prisma` | 分层规范：Controller → Service → Repository，禁止 Controller 直连 DB | 代码审查 checklist + 生成器模板                     |
| `OpenAPI` 定义       | API 契约规范：前后端以 OpenAPI 3.0 为准，禁止手动写 DTO                     | `openapi-generator` CI 校验                  |

### 2. 生成规范文档 Prompt
```text
基于以下架构画像，生成《项目开发规范》Markdown 文档。要求：
- 分章节：目录结构、命名约定、分层架构、API 设计、状态管理、异常处理、测试、提交规范
- 每条规范包含：规则描述 ✅ 正例 ❌ 反例 🛠 工具校验方式
- 语气为团队内部标准，可直接放入 CONTRIBUTING.md 或 docs/standards/
- 避免空泛描述，全部绑定到当前项目实际技术栈

架构画像：
[粘贴上一步输出的 JSON/Markdown]
```

---
## 三、自动化落地与持续治理
规范必须可校验、可修复、可阻断，否则极易流于形式。

### 1. 生成工具链配置（Claude Code 一键生成）
```text
请根据上述规范，生成以下配置文件（带注释说明）：
1. .eslintrc.cjs（含 custom rules 用于检测分层越权、状态滥用、API 直调等）
2. prettier.config.js
3. tsconfig.json（开启 strict、noImplicitAny、exactOptionalPropertyTypes 等）
4. husky 配置 + lint-staged 脚本
5. commitlint.config.js（Conventional Commits + scope 限制）
6. CI 检查脚本（.github/workflows/lint-check.yml）
```

### 2. 项目级 AI 规则固化（Claude Code 专属）
在项目根目录创建 `.claude/rules.md`（或 `.cursor/rules` 等效文件），写入：
```markdown
# Project Architecture Rules
- 前端必须通过 `@/api/` 调用接口，禁止组件内直接使用 fetch/axios
- 状态管理：全局状态仅限 `@/store/global.ts`，模块状态放 `@/modules/*/store.ts`
- 后端分层：Controller 仅做参数校验与路由转发，业务逻辑必须在 Service 层
- 错误处理：统一使用 `AppError` 类，禁止 throw String / 返回 null 表示错误
- 命名：组件 PascalCase，工具函数 camelCase，常量 UPPER_SNAKE_CASE
- 新增文件前，先检查是否符合 `docs/standards/folder-structure.md`
```
Claude Code 在后续对话中会自动加载此文件，并在代码生成/审查时强制遵循。

---
## 四、关键工作流示例（Windows PowerShell）
```powershell
# 1. 让 Claude Code 分析现有代码
claude code "分析 src/ 和 server/ 的架构模式，输出架构画像"

# 2. 生成规范文档
claude code "基于画像生成开发规范，输出到 docs/STANDARDS.md"

# 3. 生成校验配置
claude code "根据规范生成 ESLint 规则、pre-commit 钩子、CI 检查脚本"

# 4. 日常开发
claude code "按当前规范实现用户管理模块，输出代码并自检是否符合规范"
```

---
## 五、注意事项与最佳实践
1. **不要一次性提取全部规范**：先抓 3~5 个高频痛点（如 API 调用混乱、状态滥用、分层模糊），跑通工具链后再逐步扩展。
2. **架构画像需定期更新**：每次大版本重构后，重新运行提取 Prompt，对比差异并更新规范。
3. **规范必须配套“逃生通道”**：在 `// @ts-ignore` 或 `/* eslint-disable */` 旁强制要求写 `// reason: 架构例外，已评审`，避免规则僵化。
4. **结合 PR 模板**：在 GitHub/GitLab PR 描述中增加 `架构合规自查` 勾选框，Claude Code 可自动生成预填充内容。
5. **测试覆盖率绑定架构**：对 Service/Repository 层要求 ≥80%，UI 组件 ≥60%，用 `jest --coverage` + CI 门禁拦截。
