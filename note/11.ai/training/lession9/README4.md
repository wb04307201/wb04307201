# Claude Code Skills

## 🔍 一、什么是 Claude Code Skills？
- **定位**：Claude Code 的扩展能力集合，类似 VS Code 插件或 MCP 工具集，通过"技能包"将特定领域的知识、工作流模板和工具链固化下来。
- **核心价值**：让 Claude 具备更专业的领域知识（如前端设计、代码规范检查），执行特定的复杂任务，极大扩展其能力边界。
- **运行机制**：安装后会在对话中自动注册为可用能力，通过自然语言或 `/skill` 命令调用，Claude 会自动遵守技能包中定义的编码规范、注释要求等。
- **两种形式**：
  - **全局 Skills**：通过插件市场或命令行安装，对所有项目生效
  - **项目级 Skills**：通过 `CLAUDE.md` 文件配置，仅对当前项目生效

---
## 📦 二、安装指南（CLI + Skills）

### 1. 安装 Claude Code CLI
```bash
# 推荐使用 Node.js 18+
npm install -g @anthropic-ai/claude-code

# 初始化并登录（首次运行会自动引导）
claude

# 验证安装成功
claude --version
```

> ⚠️ **注意**：Claude 官方不支持中国大陆用户，如遇网络问题可使用国内镜像站或配置代理。

### 2. Skills 系统启用与安装

#### 方式一：通过插件市场安装（推荐）
```bash
# 在 Claude Code 中添加插件市场
/plugin marketplace add forrestchang/andrej-karpathy-skills

# 安装具体插件
/plugin install andrej-karpathy-skills @karpathy-skills

# 查看已安装的 Skills
/skill
```

#### 方式二：通过 npx skills 命令行工具安装（全局）
```bash
# 安装 Vercel Labs 官方 Skills 仓库中的技能
npx skills add anthropics/claude-code/frontend-design

# 安装社区维护的 Skills（需配置代理）
npx skills add vercel-labs/skills/find-skills

# 示例：安装 Web Access 技能（用于联网搜索）
npx skills add eze-is/web-access
```

#### 方式三：通过 CLAUDE.md 项目级配置（每个项目独立）
```bash
# 新项目：直接下载 CLAUDE.md
curl -o CLAUDE.md https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md

# 现有项目：追加到已有 CLAUDE.md
echo "" >> CLAUDE.md
curl https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md
```

> 💡 **提示**：
> - 全局 Skills 安装在 `~/.claude/skills/` 目录下
> - 项目级 Skills 通过根目录的 `CLAUDE.md` 文件配置，优先级更高
> - 如需网络代理，可在安装命令中指定端口（如 `npx skills add xxx --proxy http://127.0.0.1:7890`）

---
## 🔥 三、热门 Skills 推荐（按场景分类）

| 类别           | Skill 名称/来源                          | 核心功能                                            | 适用场景          |
|--------------|---------------------------------------|-------------------------------------------------|---------------|
| 🛠️ **开发提效** | `frontend-design` (anthropics)        | 根据设计稿生成前端代码，支持图片识别和分析                        | UI 开发/设计转代码     |
|              | `web-access` (eze-is)                 | 联网搜索、多平台内容抓取（小红书/微博/知乎/B站/GitHub）         | 信息调研/竞品分析      |
|              | `opencli` (jackwener)                 | 公众号/小红书/B站/知乎等多平台数据获取与自动化操作                | 内容运营/数据采集      |
| 📝 **代码质量**  | `andrej-karpathy-skills` (forrestchang) | Karpathy 编程四原则：简洁代码、测试驱动、文档完善、持续重构          | 高质量代码实践       |
|              | `code-review` (vercel-labs)           | 按规范审查代码（命名/复杂度/安全边界），输出结构化报告              | PR 审查/重构      |
|              | `security-audit`                      | 检测硬编码密钥、依赖漏洞、SQLi/XSS 风险模式                  | 安全左移/合规       |
| 🌐 **框架专精**  | `react-nextjs` (vercel-labs)            | App Router 路由规范、Server Component 优化、Tailwind 集成 | 前端全栈开发        |
|              | `python-fastapi`                      | Pydantic V2 校验、依赖注入、异步路由、OpenAPI 定制             | Python 后端 API |
|              | `rust-async`                          | Tokio 运行时优化、错误链处理、Futures 调试建议               | 高性能系统编程       |
| 📚 **运维与文档** | `docs-builder`                        | 自动生成 README、架构图 Mermaid、API 文档骨架              | 项目初始化/交接      |
|              | `log-analyzer`                        | 解析 JSON/结构化日志，提取异常堆栈与根因推测                    | 线上排查          |
|              | `docker-helper`                       | 生成多阶段 Dockerfile、docker-compose、健康检查配置            | 容器化部署         |
|              | `ci-cd-automator`                     | 生成 GitHub Actions / GitLab CI 模板，支持缓存/矩阵构建        | 自动化流水线        |
|              | `infra-terraform`                     | 生成 AWS/GCP 基础设施模块，带 state 管理提示                 | 云原生架构         |
| 🧩 **高阶扩展**  | `mcp-connector`                       | 桥接外部 MCP Server（数据库、浏览器、本地工具）                 | 自定义工具链        |
|              | `everything-claude-code`              | 多平台社交内容引擎，一键分发到微博/微信公众号/知乎等平台             | 内容创作/分发       |

> ⚠️ **注意**：Skills 命名和来源可能随版本迭代变化，安装前建议访问以下资源查看最新可用列表：
> - Vercel Labs Skills 仓库：`https://github.com/vercel-labs/skills`
> - Awesome Claude Plugins：`https://github.com/quemsah/awesome-claude-plugins`
> - Skills.sh 平台：`https://skills.sh/`

---
## 🛡️ 四、使用建议与注意事项

### 1. 权限与安全
- **本地命令调用**：部分 Skills 会调用本地命令（如 `docker`, `git`, `terraform`），安装前务必阅读技能仓库中的权限说明。
- **网络代理配置**：在中国大陆使用时，可能需要配置 HTTP 代理（如 `--proxy http://127.0.0.1:7890`）。
- **API Key 保护**：避免在 Skills 配置中硬编码敏感信息，优先使用环境变量。

### 2. 安装方式选择
- **全局 Skills**：适合通用工具（如 `web-access`, `frontend-design`），一次安装所有项目可用。
- **项目级 CLAUDE.md**：适合团队规范、项目特定约束，优先级高于全局 Skills，便于版本控制。
- **混合使用**：可同时使用两种方式，项目级配置会覆盖全局配置的冲突部分。

### 3. 验证安装成功
```bash
# 在 Claude Code 中输入以下命令查看已激活的 Skills
/skill

# 或通过自然语言询问
"你当前加载了哪些 Skills？"
```

### 4. 自定义开发
- **创建项目级 Skills**：在项目根目录创建 `CLAUDE.md`，编写团队编码规范、注释要求、测试标准等。
- **发布到社区**：将自定义 Skills 上传至 GitHub，其他用户可通过 `npx skills add <username>/<repo>` 安装。
- **MCP 集成**：高级用户可通过 MCP（Model Context Protocol）连接外部服务（数据库、浏览器、本地工具）。

### 5. 性能与上下文管理
- **按需启用**：Skills 会占用上下文窗口，复杂项目建议按需安装，避免一次性加载过多技能。
- **禁用不需要的 Skills**：通过 `/plugin uninstall <name>` 卸载不再使用的全局 Skills。
- **版本同步**：定期运行 `npx skills update` 或重新拉取 `CLAUDE.md`，确保使用最新版本。

### 6. 常见问题
- **安装失败**：检查网络连接，必要时配置代理；确认 Node.js 版本 ≥ 18。
- **Skills 未生效**：重启 Claude Code 会话；检查 `CLAUDE.md` 格式是否正确。
- **冲突处理**：若多个 Skills 提供相同功能，项目级配置优先于全局配置。

---
## 🌐 五、社区资源与学习路径

### 官方与社区资源
- 📦 **Vercel Labs Skills 仓库**（官方维护）：`https://github.com/vercel-labs/skills`
- 📦 **Awesome Claude Plugins**（社区聚合）：`https://github.com/quemsah/awesome-claude-plugins`
- 🌐 **Skills.sh 平台**（一键安装）：`https://skills.sh/`
- 💬 **社区交流**：GitHub Discussions、Discord `#claude-code` 频道、CSDN/Juejin 技术博客

### 实战教程推荐
- 🔍 **配置 Skills 与图片识别**：CSDN 教程 `https://blog.csdn.net/hejuan___/article/details/160382342`
- 🚀 **Claude Code 进阶技巧**：CSDN 教程 `https://blog.csdn.net/2604_95843151/article/details/160288221`
- 📖 **完整使用指南**：包括 MCP 集成、配置系统、安全管理等：`https://php.cn/faq/2279945.html`

### 调试技巧
```bash
# 查看详细日志（调试模式）
claude --verbose

# 检查 Skills 依赖（以 web-access 为例）
bash ~/.claude/skills/web-access/scripts/check-deps.sh
```

> 📌 **未来趋势**：Anthropic 正逐步将 Skills 能力整合进 **MCP（Model Context Protocol）** 生态，未来可通过 `mcp.json` 统一管理局部/远程工具。建议关注官方 Release Notes 和社区动态，及时更新最佳实践。