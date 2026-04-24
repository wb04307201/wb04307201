## 详细步骤

> 本文档只是说明如何配置阿里云百炼平台模型API

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


### **1. 安装 Claude Code**

1.  安装或更新 [Node.js](https://nodejs.org/en/download/)（v18.0 或更高版本）。

2.  在终端中执行下列命令，安装 Claude Code。

    ```
    npm install -g @anthropic-ai/claude-code
    ```

3.  运行以下命令验证安装。若有版本号输出，则表示安装成功。

    ```
    claude --version
    ```

### **2. 在Claude Code配置百炼模型**

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

[更详细内容方可参考](https://help.aliyun.com/zh/model-studio/claude-code)

后续把内容请从《实战Harness工程.pdf》第5页`Superpowers：`继续