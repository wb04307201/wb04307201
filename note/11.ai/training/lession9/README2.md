# Claude Code插件

截至 2026 年，Claude Code 的插件生态已逐步成熟，主要分为 **官方插件（`claude-plugins-official`）** 和 **社区插件（`claude-plugins-community`）**。以下为当前开发团队中使用率较高、口碑较好的热门插件清单及对应安装命令：

---

### 📦 官方热门插件（`claude-plugins-official`）
| 插件名称              | 核心功能                                      | 安装命令                                                      |
|-------------------|-------------------------------------------|-----------------------------------------------------------|
| `superpowers`     | 全栈开发工作流（需求澄清→任务拆解→TDD→子智能体调度→代码审查）        | `/plugin install superpowers@claude-plugins-official`     |
| `frontend-design` | 高颜值 UI/前端生成（支持风格定向、排版设计、响应式适配，拒绝“AI 模板风”） | `/plugin install frontend-design@claude-plugins-official` |
| `code-review`     | 自动化 PR/代码审查，提供可操作建议、复杂度分析与潜在 Bug 提示       | `/plugin install code-review@claude-plugins-official`     |
| `security-audit`  | 依赖漏洞扫描、OWASP Top 10 检查、敏感信息泄漏检测与安全加固建议    | `/plugin install security-audit@claude-plugins-official`  |
| `test-assistant`  | 单元/集成测试生成、覆盖率分析、失败用例自动修复与 Mock 数据构建       | `/plugin install test-assistant@claude-plugins-official`  |
| `git-flow`        | 分支策略管理、自动化 Changelog、冲突预判与 PR 模板生成        | `/plugin install git-flow@claude-plugins-official`        |

---

### 🌍 社区精选插件（`claude-plugins-community`）
| 插件名称              | 核心功能                                            | 安装命令                                                       |
|-------------------|-------------------------------------------------|------------------------------------------------------------|
| `docker-helper`   | Dockerfile / Compose 生成、多阶段构建优化、镜像体积精简建议        | `/plugin install docker-helper@claude-plugins-community`   |
| `api-docs-gen`    | 从路由/控制器代码自动生成 OpenAPI 3.0 规范与交互式文档站点            | `/plugin install api-docs-gen@claude-plugins-community`    |
| `tailwind-studio` | Tailwind CSS 组件库调用、任意值转换、未使用类清理与性能优化            | `/plugin install tailwind-studio@claude-plugins-community` |
| `db-schema-sync`  | 数据库结构逆向解析、ORM 模型生成、迁移脚本自动补全                     | `/plugin install db-schema-sync@claude-plugins-community`  |
| `prompt-refiner`  | 提示词多版本对比测试、上下文压缩、角色设定优化与幻觉率评估                   | `/plugin install prompt-refiner@claude-plugins-community`  |
| `mcp-bridge`      | 桥接外部 MCP 服务器（数据库、API、本地工具链），扩展 Claude Code 能力边界 | `/plugin install mcp-bridge@claude-plugins-community`      |

---

### 🔍 插件管理常用命令
```bash
# 搜索插件（支持关键词/分类过滤）
/plugin search <关键词>

# 查看已安装插件列表及版本
/plugin list

# 查看插件详情（权限、依赖、使用示例）
/plugin info <插件名>

# 更新指定插件或全部插件
/plugin update <插件名>
/plugin update --all

# 卸载插件
/plugin remove <插件名>
```

---

### ⚠️ 注意事项
1. **注册源区分**：官方插件经过 Anthropic 安全与兼容性审核；社区插件由开发者自主发布，安装前建议通过 `/plugin info <name>` 查看权限声明与代码仓库。
2. **版本兼容**：插件可能与特定 Claude Code CLI 版本绑定，若安装失败请运行 `claude --version` 确认当前版本，或使用 `plugin update --all` 升级。
3. **动态生态**：插件市场每周更新，完整列表请访问 [Claude Plugins Registry](https://plugins.claude.ai) 或在终端运行 `/plugin search *`。

需要我针对某个具体插件提供 **使用示例、配置参数或与其他工具的联动方案** 吗？