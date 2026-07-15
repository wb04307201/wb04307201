> ⬅️ [返回目录](README.md)

# 环境安装步骤

> 本文档只是说明Claude Code CLI如何配置阿里云百炼平台模型API

百炼提供的 Anthropic API 兼容服务支持以下千问系列模型：

| **模型系列**             | **支持的模型名称（model）**                                                                                             |
|----------------------|----------------------------------------------------------------------------------------------------------------|
| 千问Max （部分模型支持思考模式）   | qwen3.6-max-preview（支持思考模式）、qwen3-max、qwen3-max-2026-01-23（支持思考模式）、qwen3-max-preview（支持思考模式）                   |
| 千问Plus               | qwen3.6-plus、qwen3.5-plus、qwen3.5-plus-2026-02-15、qwen-plus、qwen-plus-latest、qwen-plus-2025-09-11              |
| 千问Flash              | qwen3.6-flash、qwen3.6-flash-2026-04-16、qwen3.5-flash、qwen3.5-flash-2026-02-23、qwen-flash、qwen-flash-2025-07-28 |
| 千问Turbo              | qwen-turbo、qwen-turbo-latest                                                                                   |
| 千问Coder （不支持思考模式）    | qwen3-coder-next、qwen3-coder-plus、qwen3-coder-plus-2025-09-23、qwen3-coder-flash                                |
| 千问VL （不支持思考模式）       | qwen3-vl-plus、qwen3-vl-flash、qwen-vl-max、qwen-vl-plus                                                          |
| 千问开源模型               | qwen3.5-397b-a17b、qwen3.5-120b-a10b、qwen3.5-27b、qwen3.5-35b-a3b                                                |
| 第三方模型 （仅支持华北2（北京）地域） | - kimi-k2.5、kimi-k2-thinking - glm-5.1、glm-5、glm-4.7、glm-4.6 - MiniMax-M2.5、MiniMax-M2.1                       |


## **1. 安装 Claude Code**

1.  安装或更新 [Node.js](https://nodejs.org/en/download/)（v18.0 或更高版本）。
    > - windows点击Windows Installer (.msi)即可开始下载
    > - 除安装位置外不要修改其他配置

2.  Node.js安装后打开终端中并执行下列命令，安装 Claude Code CLI。

    ```
    npm install -g @anthropic-ai/claude-code
    ```

3.  运行以下命令验证安装。若有版本号输出，则表示安装成功。

    ```
    claude --version
    ```

## **2. Claude Code 常用命令**

### `--dangerously-skip-permissions` 参数说明

`--dangerously-skip-permissions` 是 Claude Code CLI 的一个启动参数，用于跳过所有权限确认提示，让 AI 自动执行所有操作（文件读写、命令执行等）。

**⚠️ 安全警告：** 此参数会禁用所有权限确认，AI 将无需确认即可执行任何操作。仅在完全信任的环境中（如隔离的沙箱、个人测试环境）使用。

**使用方式：**

```bash
# 启动时跳过所有权限确认
claude --dangerously-skip-permissions

# 结合其他参数使用
claude --dangerously-skip-permissions --output-format stream

# 在脚本/自动化流程中使用
claude --dangerously-skip-permissions -p "分析当前项目结构"
```

### 其他常用启动参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p`, `--prompt` | 直接传入提示词并退出 | `claude -p "解释README.md"` |
| `--output-format` | 输出格式（`text`/`stream`/`json`） | `claude --output-format stream` |
| `--allowedTools` | 预授权允许的工具列表 | `claude --allowedTools Bash --allowedTools Read` |
| `--disallowedTools` | 禁止使用的工具列表 | `claude --disallowedTools Write` |
| `--continue` | 继续上一次的对话 | `claude --continue` |
| `--resume` | 恢复指定的历史会话 | `claude --resume <session-id>` |

### 权限模式说明

Claude Code 默认有三种权限模式：

- **默认模式**：每次执行工具前会提示确认
- **自动模式**：安全操作自动确认，危险操作仍需确认
- **跳过权限模式**（`--dangerously-skip-permissions`）：所有操作自动执行

在交互式使用时建议使用默认模式，在自动化脚本或可信环境中可使用 `--dangerously-skip-permissions`。

---

## **3. 在Claude Code配置百炼模型**

1.  创建并打开配置文件`C:\Users\您的用户名\.claude\settings.json`。

### CMD

1.  创建目录

    ```
    if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
    ```

2.  创建并打开文件

    ```
    notepad "%USERPROFILE%\.claude\settings.json"
    ```


### PowerShell
    
1.  创建目录
        
    ```
    mkdir -Force $HOME\.claude
    ```
        
2.  创建并打开文件
        
    ```
    notepad $HOME\.claude\settings.json
    ```

2.  编辑配置文件。将 YOUR\_API\_KEY 替换为[阿里云百炼 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)。

    ```
    {    
        "env": {
            "ANTHROPIC_AUTH_TOKEN": "YOUR_API_KEY",
            "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/apps/anthropic",
            "ANTHROPIC_MODEL": "qwen3.6-plus",
            "ANTHROPIC_SMALL_FAST_MODEL": "qwen3.6-flash",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen3.6-flash",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen3.6-plus",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "qwen3.6-plus",
            "CLAUDE_CODE_SUBAGENT_MODEL": "qwen3.6-plus"
        }
    }
    ```

3.  在终端中使用`claude`命令启动**Claude Code**一次后关闭终端，找到 `C:\Users\您的用户名\.claude.json` 文件，编辑或新增`hasCompletedOnboarding`字段的值并设置为`true`，并保存文件。

    ```
    {
      "hasCompletedOnboarding": true
    }
    ```

## **4. Spec-Kit安装**

1. 安装 Python
    - 访问 [https://www.python.org/downloads/](https://www.python.org/downloads/)
    - 下载 Windows 安装包并安装
    - 勾选 "Add Python to PATH"

2. 安装 uv
   ```powershell
   pip install uv
   ```

3. 验证安装
   ```powershell
   uv --version
   ```

4. 安装 Git
    - 访问 [https://git-scm.com/](https://git-scm.com/)
    - 下载 Windows 安装包并安装
   
5. 安装 Specify CLI
   ```powershell
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```

6. 如果提示`warning: 'C:\Users\[用户]\.local\bin' is not on your PATH. To use installed tools, run '$env:PATH = "C:\Users\Administrator\.local\bin;$env:PATH"' or 'uv tool update-shell'.`请执行对应命令

[更多信息请看：规范驱动开发工具深度解析：Spec-Kit、Kiro、OpenSpec](sh-02-sdd.md)
[更多信息请看：Spec-Kit 规范驱动开发（SDD）工具包使用说明](sh-03-speckit.md)
    
## **5. (可选)添加MCP工具**
1. 打开并编辑配置文件`~/.claude.json`，例如添加如下搜索、网页抓取、浏览器操作、结构化推理、时间等 MCP 服务
```json
{
  "mcpServers": {
    "bing-search": {
      "args": [
        "-y",
        "bing-cn-mcp@latest"
      ],
      "command": "npx"
    },
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest"
      ]
    },
    "mcp-npx-fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@tokenizin/mcp-npx-fetch@latest"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking@latest"
      ]
    },
    "time": {
      "command": "uvx",
      "args": [
        "mcp-server-time",
        "--local-timezone=Asia/Shanghai"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp@latest"
      ]
    },
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp@latest"
      ]
    }
  }
}
```
MCP 是一种开放协议，只要是符合该协议开发的工具都可以接入 AI Agent，因此可能需要适配多种语言的环境。

### 1. **Node.js + npx**

**npx 说明**
    - npx 是 Node.js 包执行工具，随 npm 5.2+ 自动安装
    - 用于直接运行 npm 包而无需全局安装
    - 示例：`npx @playwright/mcp@latest`

> npx已集成在nodejs中，只需验证安装成功`npx --version`


### 2. **Python + uv**

**uv 介绍**
    - uv 是一个超快速的 Python 包管理器和项目管理器
    - 比 pip 快 10-100 倍
    - 支持虚拟环境管理、依赖解析等
    - 可用于运行 MCP 服务器：`uvx mcp-server-time`

> 前面有安装

### 3. **Java + jbang**

**JBang 介绍**
    - JBang 允许无需安装 JDK 或配置项目即可运行 Java 代码
    - 适合快速原型开发和脚本编写
    - 可直接运行 Maven 坐标的 Java 应用
    - 示例：`jbang io.github.wb04307201:http-mcp:1.0.0`

1. **安装 JBang**（PowerShell）
   ```powershell
   iex "& { $(iwr https://ps.jbang.dev) } app setup"
   ```

2. **验证安装**
   ```powershell
   jbang --version
   ```

[更多信息请看：MCP（Model Context Protocol）推荐](sh-01-mcp.md)

## **6. 插件安装**
1. 在终端中使用`claude`命令启动**Claude Code**后执行命令
```powershell
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install code-review@claude-plugins-official
```
如果启动claude时提示` Failed to install Anthropic marketplace · Will retry on next startup`，请按如下方式尝试解决：
  1. 退出 Claude Code，重新进入  
     `/exit`
  2. 添加非官方仓库  
     `/plugin marketplace add obra/superpowers-marketplace`

[更多信息请看：Claude Code插件](cc-02-plugins.md)

## **7. (可选)Skills安装**
[更多信息请看：Claude Code Skills](cc-03-skills.md)

---

> - 📝 Claude Code 调用阿里云百炼配置：`https://help.aliyun.com/zh/model-studio/claude-code`
> - 📘 官方文档：`https://docs.anthropic.com/claude-code`

后续把内容请从[实战Harness工程 V1.4.pdf](实战Harness工程 V1.4.pdf)第10页继续

## 其它
- [Spec-Kit 规范驱动开发（SDD）工具包使用说明](sh-03-speckit.md)
- [Chatbox 一款 AI 客户端应用，支持配置Qwen等API](https://chatboxai.app/zh)