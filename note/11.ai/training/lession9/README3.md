# Claude Code Skills

## 🔍 一、什么是 Claude Code Skills？
- **定位**：类似 VS Code 插件或 MCP 工具集，但更偏向“工作流模板+领域知识注入”。
- **结构**：通常包含 `config.yaml`（触发规则/参数）、`prompt.md`（系统提示词）、可选的 `scripts/`（本地可执行脚本）及 `tools.json`（外部 API 或 CLI 调用声明）。
- **运行机制**：安装后会在对话中自动注册为可用能力，通过自然语言或 `/skill <name>` 调用。

---
## 📦 二、安装指南（CLI + Skills）

### 1. 安装 Claude Code CLI
```bash
# 推荐使用 Node.js 18+ 或 Python 3.10+
npm install -g @anthropic-ai/claude-code
# 或
pip install claude-code

# 初始化并登录
claude auth
claude init
```

### 2. Skills 系统启用与安装
```bash
# 查看已安装 Skills
claude skills list

# 从官方/社区注册表安装
claude skills install code-review
claude skills install react-nextjs

# 手动安装（克隆到本地目录）
mkdir -p ~/.claude-code/skills/my-custom-skill
# 放入 config.yaml + prompt.md 后自动生效

# 更新所有 Skills
claude skills update
```
> 💡 提示：首次运行 `claude skills install` 会自动创建 `~/.claude-code/skills/` 目录。可通过 `export CLAUDE_SKILLS_DIR=/custom/path` 修改路径。

---
## 🔥 三、热门 Skills 推荐（按场景分类）

| 类别           | Skill 名称          | 核心功能                                            | 适用场景          |
|--------------|-------------------|-------------------------------------------------|---------------|
| 🛠️ **开发提效** | `git-workflow`    | 自动生成 PR 描述、分支命名规范、冲突解决建议                        | 团队协作/开源贡献     |
|              | `docker-helper`   | 生成多阶段 Dockerfile、docker-compose、健康检查配置          | 容器化部署         |
|              | `ci-cd-automator` | 生成 GitHub Actions / GitLab CI 模板，支持缓存/矩阵构建      | 自动化流水线        |
| 📝 **代码质量**  | `code-review-pro` | 按规范审查代码（命名/复杂度/安全边界），输出结构化报告                    | PR 审查/重构      |
|              | `test-generator`  | 自动生成单元测试/集成测试（支持 Jest/Pytest/Go test）           | TDD/遗留代码补测    |
|              | `security-audit`  | 检测硬编码密钥、依赖漏洞、SQLi/XSS 风险模式                      | 安全左移/合规       |
| 🌐 **框架专精**  | `react-nextjs`    | App Router 路由规范、Server Component 优化、Tailwind 集成 | 前端全栈开发        |
|              | `python-fastapi`  | Pydantic V2 校验、依赖注入、异步路由、OpenAPI 定制             | Python 后端 API |
|              | `rust-async`      | Tokio 运行时优化、错误链处理、Futures 调试建议                  | 高性能系统编程       |
| 📚 **运维与文档** | `docs-builder`    | 自动生成 README、架构图 Mermaid、API 文档骨架                | 项目初始化/交接      |
|              | `log-analyzer`    | 解析 JSON/结构化日志，提取异常堆栈与根因推测                       | 线上排查          |
|              | `infra-terraform` | 生成 AWS/GCP 基础设施模块，带 state 管理提示                  | 云原生架构         |
| 🧩 **高阶扩展**  | `mcp-connector`   | 桥接外部 MCP Server（数据库、浏览器、本地工具）                   | 自定义工具链        |
|              | `prompt-library`  | 内置 50+ 高质量提示词模板（重构/解释/翻译/优化）                    | 日常对话增强        |

> ⚠️ 注意：Skills 命名可能随版本迭代微调，安装前建议用 `claude skills search <keyword>` 查看最新可用列表。

---
## 🛡️ 四、使用建议与注意事项
1. **权限与安全**：部分 Skills 会调用本地命令（如 `docker`, `git`, `terraform`），安装前务必阅读 `config.yaml` 中的 `allowed_commands` 字段。
2. **冲突处理**：若多个 Skills 提供相同工具（如两个 `test-generator`），Claude Code 会按安装顺序加载，可通过 `claude skills disable <name>` 临时关闭。
3. **自定义开发**：在 `~/.claude-code/skills/` 下新建目录，遵循官方模板即可发布。支持环境变量注入与多平台兼容脚本。
4. **版本同步**：CLI 升级后建议运行 `claude skills update`，避免提示词过期或工具协议不匹配。
5. **性能提示**：Skills 会占用上下文窗口，复杂项目建议按需启用，或在 `.claude-code/config.json` 中设置 `max_skills_per_session: 3`。

---
## 🌐 五、社区资源
- 📦 Skills 注册表（非官方但活跃）：`https://github.com/awesome-claude-code/skills`
- 💬 社区交流：Discord `#claude-code` 频道、GitHub Discussions
- 🔍 调试技巧：运行 `claude --verbose` 可查看 Skills 加载日志与工具调用链

> 📌 提示：Anthropic 正逐步将部分 Skills 能力整合进 **MCP（Model Context Protocol）** 生态，未来可通过 `mcp.json` 统一管理局部/远程工具。建议保持关注官方 Release Notes。