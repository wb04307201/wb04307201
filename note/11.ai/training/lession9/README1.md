# 详细步骤

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

## **2. 在Claude Code配置百炼模型**

1.  创建并打开配置文件`C:\Users\您的用户名\.claude\settings.json`。

    ## CMD

    1.  创建目录

        ```
        if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
        ```

    2.  创建并打开文件

        ```
        notepad "%USERPROFILE%\.claude\settings.json"
        ```


    ## PowerShell
    
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

    保存配置文件，重新打开一个终端即可生效。

3.  编辑或新增 `C:\Users\您的用户名\.claude.json` 文件，将`hasCompletedOnboarding` 字段的值设置为 `true`，并保存文件。

    ```
    {
      "hasCompletedOnboarding": true
    }
    ```
    
## **3. 添加MCP工具**
1. 全局配置（所有项目可用）
> 编辑 ~/.claude/settings.json（或 ~/.claude/settings.local.json）

2. 项目级配置（仅当前项目可用）
> 编辑 .claude/settings.json 或 .claude/settings.local.json（当前项目目录下）

例如：
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": [
        "mcp-server-time",
        "--local-timezone=Asia/Shanghai"
      ]
    },
    "playwright": {
      "command": "npx.cmd",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "fetch": {
      "args": [
        "mcp-server-fetch"
      ],
      "command": "uvx"
    }
  }
}
```
mcp是一种协议，只要是符合这种协议开发的工具都可以接入AI Agent

### Windows 环境安装指南

#### 1. **Node.js + npx**

> npx已集成在nodejs中，只需验证安装成功

1. **验证安装**
```powershell
node --version
npm --version
npx --version
```

2. **npx 说明**
    - npx 是 Node.js 包执行工具，随 npm 5.2+ 自动安装
    - 用于直接运行 npm 包而无需全局安装
    - 示例：`npx @playwright/mcp@latest`

#### 2. **Python + uv**

1. **安装 Python**（如未安装）
    - 访问 [https://www.python.org/downloads/](https://www.python.org/downloads/)
    - 下载 Windows 安装包并安装
    - 勾选 "Add Python to PATH"

2. **安装 uv**
   ```powershell
   pip install uv
   ```

3. **验证安装**
   ```powershell
   where uv
   uv --version
   ```

4. **uv 介绍**
    - uv 是一个超快速的 Python 包管理器和项目管理器
    - 比 pip 快 10-100 倍
    - 支持虚拟环境管理、依赖解析等
    - 可用于运行 MCP 服务器：`uvx mcp-server-time`

#### 3. **Java + jbang**

1. **安装 JBang**（PowerShell）
   ```powershell
   iex "& { $(iwr https://ps.jbang.dev) } app setup"
   ```

2. **验证安装**
   ```powershell
   jbang --version
   ```

3. **JBang 介绍**
    - JBang 允许无需安装 JDK 或配置项目即可运行 Java 代码
    - 适合快速原型开发和脚本编写
    - 可直接运行 Maven 坐标的 Java 应用
    - 示例：`jbang io.github.wb04307201:http-mcp:1.0.0`

[MCP（Model Context Protocol）推荐](README2.md)

## **3. 插件安装**
[Claude Code插件](README3.md)

## **4. Skills安装**
[Claude Code Skills](README4.md)

## **5. 规范驱动开发(Spec-Driven Development, SDD)**
[规范驱动开发工具深度解析：Spec-Kit、Kiro、OpenSpec](README5.md)

> - 📝 Claude Code 调用阿里云百炼配置：`https://help.aliyun.com/zh/model-studio/claude-code`
> - 📘 官方文档：`https://docs.anthropic.com/claude-code`

后续把内容请从[实战Harness工程.pdf](%E5%AE%9E%E6%88%98Harness%E5%B7%A5%E7%A8%8B.pdf)第5页`Superpowers：`继续

## 其它
- [Spec-Kit 规范驱动开发（SDD）工具包使用说明](README6.md)
- [Chatbox 一款 AI 客户端应用，支持配置Qwen等API](https://chatboxai.app/zh)