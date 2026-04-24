## 详细步骤

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