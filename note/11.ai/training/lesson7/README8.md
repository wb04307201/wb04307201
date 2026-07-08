> ⬅️ [返回目录](README.md)

# OpenCode CLI 环境安装步骤

> 本文档说明 OpenCode CLI 如何安装并配置阿里云百炼平台模型 API

OpenCode 是一款终端 AI 编程工具，通过 Anthropic 兼容 API 接入阿里云百炼。百炼支持的千问系列模型：

| **模型系列**             | **支持的模型名称（model）**                                                                                             |
|----------------------|----------------------------------------------------------------------------------------------------------------|
| 千问Max （支持思考模式）   | qwen3.7-max、qwen3.6-max-preview、qwen3-max                   |
| 千问Plus               | qwen3.7-plus、qwen3.6-plus、qwen3.5-plus、qwen-plus              |
| 千问Flash              | qwen3.6-flash、qwen3.5-flash、qwen-flash |
| 千问Coder              | qwen3-coder-next、qwen3-coder-plus、qwen3-coder-flash                                |
| 千问VL                | qwen3-vl-plus、qwen3-vl-flash、qwen-vl-max、qwen-vl-plus                                                          |
| 第三方模型 （仅支持华北2（北京）地域） | deepseek-v4-pro、deepseek-v4-flash、kimi-k2.7-code、kimi-k2.5、glm-5.2、glm-5.1、MiniMax-M2.5                       |


## **1. 安装 OpenCode**

1.  安装或更新 [Node.js](https://nodejs.org/en/download/)（v18.0 或更高版本）。
    > - windows点击Windows Installer (.msi)即可开始下载
    > - 除安装位置外不要修改其他配置

2.  Node.js安装后打开终端中并执行下列命令，安装 OpenCode CLI。

    ```
    npm install -g opencode-ai
    ```

3.  运行以下命令验证安装。若有版本号输出，则表示安装成功。

    ```
    opencode -v
    ```


## **2. OpenCode 常用命令**

### 基本使用

```bash
# 启动交互式对话
opencode

# 在当前项目目录中启动
cd your-project
opencode

# 直接传入提示词
opencode "解释这个项目的架构"
```

### 常用操作

| 操作 | 说明 |
|------|------|
| `Enter` | 发送消息 |
| `Ctrl+C` | 取消当前操作 |
| `Ctrl+D` | 退出 OpenCode |
| `/help` | 查看帮助信息 |
| `/model` | 切换模型 |

---

## **3. 配置百炼模型**

使用文本编辑器打开配置文件：

- **macOS / Linux**：`~/.config/opencode/opencode.json`
- **Windows**：`C:\Users\<用户名>\.config\opencode\opencode.json`

### CMD

1.  创建目录

    ```
    if not exist "%USERPROFILE%\.config\opencode" mkdir "%USERPROFILE%\.config\opencode"
    ```

2.  创建并打开文件

    ```
    notepad "%USERPROFILE%\.config\opencode\opencode.json"
    ```


### PowerShell
    
1.  创建目录
    
    ```
    mkdir -Force $HOME\.config\opencode
    ```
    
2.  创建并打开文件
    
    ```
    notepad $HOME\.config\opencode\opencode.json
    ```

2.  编辑配置文件。将 YOUR\_API\_KEY 替换为[阿里云百炼 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)。

### 按量计费配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "bailian-payg": {
      "npm": "@ai-sdk/anthropic",
      "name": "Alibaba Cloud Model Studio",
      "options": {
        "baseURL": "https://dashscope.aliyuncs.com/apps/anthropic/v1",
        "apiKey": "YOUR_API_KEY"
      },
      "models": {
        "qwen3.7-max": {
          "name": "Qwen3.7 Max",
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        },
        "qwen3.7-plus": {
          "name": "Qwen3.7 Plus",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        },
        "qwen3.6-plus": {
          "name": "Qwen3.6 Plus",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        },
        "qwen3.6-flash": {
          "name": "Qwen3.6 Flash",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        },
        "deepseek-v4-pro": {
          "name": "DeepSeek V4 Pro"
        },
        "kimi-k2.7-code": {
          "name": "Kimi K2.7 Code",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        }
      }
    }
  }
}
```

> ⚠️ **注意**：`baseURL` 按地域设置，API Key 需与所选地域对应：
> - **华北2（北京）**：`https://dashscope.aliyuncs.com/apps/anthropic/v1`
> - **新加坡**：`https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/apps/anthropic/v1`

### Token Plan 团队版配置

需先购买 Token Plan 团队版套餐。将 `baseURL` 改为 Token Plan 专属地址：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "bailian-token-plan": {
      "npm": "@ai-sdk/anthropic",
      "name": "Alibaba Cloud Model Studio",
      "options": {
        "baseURL": "https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic/v1",
        "apiKey": "YOUR_TOKEN_PLAN_API_KEY"
      },
      "models": {
        "qwen3.7-max": {
          "name": "Qwen3.7 Max",
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        },
        "qwen3.7-plus": {
          "name": "Qwen3.7 Plus",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        }
      }
    }
  }
}
```

### Coding Plan 配置

需先购买 Coding Plan 套餐。将 `baseURL` 改为 Coding Plan 专属地址：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "bailian-coding-plan": {
      "npm": "@ai-sdk/anthropic",
      "name": "Alibaba Cloud Model Studio",
      "options": {
        "baseURL": "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1",
        "apiKey": "YOUR_CODING_PLAN_API_KEY"
      },
      "models": {
        "qwen3.7-plus": {
          "name": "Qwen3.7 Plus",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          },
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        }
      }
    }
  }
}
```

## **4. 验证配置**

配置完成后，新建终端窗口，执行以下命令启动 OpenCode：

```
opencode
```

如果正常进入交互界面，说明配置成功。可以在界面中输入 `/model` 查看可用模型列表。

## **5. (可选)添加 MCP 工具**

OpenCode 原生支持 MCP 协议。在配置文件 `~/.config/opencode/opencode.json` 中添加 `mcpServers` 字段：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "bailian-payg": {
      "npm": "@ai-sdk/anthropic",
      "name": "Alibaba Cloud Model Studio",
      "options": {
        "baseURL": "https://dashscope.aliyuncs.com/apps/anthropic/v1",
        "apiKey": "YOUR_API_KEY"
      },
      "models": {
        "qwen3.7-max": {
          "name": "Qwen3.7 Max",
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 8192
            }
          }
        }
      }
    }
  },
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
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

安装 uv：
```powershell
pip install uv
```

验证安装：
```powershell
uv --version
```

### 3. **Java + jbang**

**JBang 介绍**
    - JBang 允许无需安装 JDK 或配置项目即可运行 Java 代码
    - 适合快速原型开发和脚本编写
    - 可直接运行 Maven 坐标的 Java 应用

安装 JBang（PowerShell）：
```powershell
iex "& { $(iwr https://ps.jbang.dev) } app setup"
```

验证安装：
```powershell
jbang --version
```

## **6. 常见问题**

### 报错 `401 Unauthorized` 怎么办？

**原因**：API Key 复制不完整、使用了错误计费方案的 API Key（按量计费/Token Plan/Coding Plan 三者互不相通）。

**解决方案**：
- 确认使用的是所选方案对应的专属 API Key
- 重新复制 API Key，确保完整且无空格
- 前往[百炼控制台](https://bailian.console.aliyun.com/)确认 API Key 是否有效

### 报错 `404 Not Found` 怎么办？

**原因**：配置文件中的 `baseURL` 填写错误。

**解决方案**：
- 按量计费：`https://dashscope.aliyuncs.com/apps/anthropic/v1`
- Token Plan：`https://token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic/v1`
- Coding Plan：`https://coding.dashscope.aliyuncs.com/apps/anthropic/v1`

### 模型列表为空怎么办？

**原因**：配置文件中 `models` 字段为空或模型名称拼写错误。

**解决方案**：确认 `models` 中至少包含一个有效模型，模型名称需与百炼支持的模型名称完全一致。

---

> - 📝 OpenCode 调用阿里云百炼配置：`https://help.aliyun.com/zh/model-studio/opencode`
> - 📘 官方文档：`https://github.com/opencode-ai/opencode`
