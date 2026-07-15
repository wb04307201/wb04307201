> ⬅️ [返回目录](README.md)

# Codex CLI 环境安装步骤

> 本文档说明 Codex CLI 如何安装并配置阿里云百炼平台模型 API

百炼提供的 OpenAI 兼容服务支持以下千问系列模型：

| **模型系列**             | **支持的模型名称（model）**                                                                                             |
|----------------------|----------------------------------------------------------------------------------------------------------------|
| 千问Max （部分模型支持思考模式）   | qwen3.7-max、qwen3.6-max-preview（支持思考模式）、qwen3-max、qwen3-max-2026-01-23（支持思考模式）                   |
| 千问Plus               | qwen3.7-plus、qwen3.6-plus、qwen3.5-plus、qwen-plus、qwen-plus-latest              |
| 千问Flash              | qwen3.6-flash、qwen3.6-flash-2026-04-16、qwen3.5-flash、qwen-flash |
| 千问Coder （不支持思考模式）    | qwen3-coder-next、qwen3-coder-plus、qwen3-coder-flash                                |
| 千问VL （不支持思考模式）       | qwen3-vl-plus、qwen3-vl-flash、qwen-vl-max、qwen-vl-plus                                                          |
| 第三方模型 （仅支持华北2（北京）地域） | kimi-k2.5、kimi-k2-thinking、glm-5.1、glm-5、glm-4.7、MiniMax-M2.5、MiniMax-M2.1                       |


## **1. 安装 Codex**

1.  安装或更新 [Node.js](https://nodejs.org/en/download/)（v18.0 或更高版本）。
    > - windows点击Windows Installer (.msi)即可开始下载
    > - 除安装位置外不要修改其他配置

2.  Node.js安装后打开终端中并执行下列命令，安装 Codex CLI。

    ```
    npm install -g @openai/codex
    ```

3.  运行以下命令验证安装。若有版本号输出，则表示安装成功。

    ```
    codex --version
    ```


## **2. Codex 常用命令**

### 基本使用

```bash
# 启动交互式对话
codex

# 直接传入提示词
codex "解释 README.md"

# 在当前目录执行编码任务
codex "给这个项目添加单元测试"
```

### 常用启动参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-m`, `--model` | 指定模型 | `codex -m qwen3.7-max` |
| `-q`, `--quiet` | 静默模式，减少输出 | `codex -q "分析代码"` |
| `-a`, `--ask-for-approval` | 审批策略（suggest/on-request/never） | `codex -a never "重构代码"` |
| `-s`, `--sandbox` | 沙箱策略（read-only/workspace-write/danger-full-access） | `codex -s danger-full-access` |

### 权限模式说明

Codex 的审批和沙箱是**两个独立维度**：

**审批策略**（`-a` / `--ask-for-approval`）：
- **suggest**（默认）：每次操作前会提示确认
- **on-request**：模型自行决定何时请求审批
- **never**：永不请求审批，执行失败直接返回给模型

**沙箱策略**（`-s` / `--sandbox`）：
- **read-only**：只读，不可修改文件
- **workspace-write**：可写工作区文件
- **danger-full-access**：完全访问（无沙箱限制）

**全自动组合**（跳过所有确认 + 完全访问）：

```bash
codex -a never -s danger-full-access "重构代码"
# 或更极端（跳过一切，仅用于外部沙箱环境）：
codex --dangerously-bypass-approvals-and-sandbox "重构代码"
```

> ⚠️ 交互式使用建议用默认 suggest 模式。自动化脚本或 Docker 隔离环境可用 `-a never -s danger-full-access`。

---

## **3. 配置百炼模型**

1.  编辑配置文件 `~/.codex/config.toml`。

### CMD

1.  创建目录

    ```
    if not exist "%USERPROFILE%\.codex" mkdir "%USERPROFILE%\.codex"
    ```

2.  创建并打开文件

    ```
    notepad "%USERPROFILE%\.codex\config.toml"
    ```


### PowerShell
    
1.  创建目录
    
    ```
    mkdir -Force $HOME\.codex
    ```
    
2.  创建并打开文件
    
    ```
    notepad $HOME\.codex\config.toml
    ```

2.  编辑配置文件。Codex 支持两种 API 接入方式，根据模型选择：

### Responses API（推荐，适用于 qwen3.7-max 等新模型）

```toml
model_provider = "Model_Studio"
model = "qwen3.7-max"

[model_providers.Model_Studio]
name = "Model_Studio"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

### Chat/Completions API（适用于 qwen3.6-plus 等其他模型）

> ⚠️ Codex 新版本使用 Responses API，不支持 `wire_api = "chat"`。如需使用 Chat API，需安装旧版本：
> ```
> npm install -g @openai/codex@0.80.0
> ```

```toml
model_provider = "Model_Studio"
model = "qwen3.6-plus"

[model_providers.Model_Studio]
name = "Model_Studio"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
env_key = "OPENAI_API_KEY"
wire_api = "chat"
```

3.  配置环境变量。将 YOUR\_API\_KEY 替换为[阿里云百炼 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)。

### Windows（PowerShell）

```powershell
# 临时设置（当前会话有效）
$env:OPENAI_API_KEY = "YOUR_API_KEY"

# 永久设置
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "YOUR_API_KEY", "User")
```

### macOS / Linux

```bash
# 将 YOUR_API_KEY 替换为百炼 API Key
echo 'export OPENAI_API_KEY="YOUR_API_KEY"' >> ~/.zshrc
source ~/.zshrc
```

## **4. 验证配置**

配置完成后，新建终端窗口，执行以下命令启动 Codex：

```
codex
```

如果正常进入对话界面，说明配置成功。

## **5. (可选)添加 MCP 工具**

Codex CLI 支持 MCP 协议。用 `codex mcp add` 命令逐个添加：

```bash
codex mcp add bing-search npx "bing-cn-mcp@latest"
codex mcp add chrome-devtools npx "chrome-devtools-mcp@latest"
codex mcp add mcp-npx-fetch npx "@tokenizin/mcp-npx-fetch@latest"
codex mcp add sequential-thinking npx "@modelcontextprotocol/server-sequential-thinking@latest"
codex mcp add time uvx "mcp-server-time" "--local-timezone=Asia/Shanghai"
codex mcp add playwright npx "@playwright/mcp@latest"
codex mcp add context7 npx "@upstash/context7-mcp@latest"
```

每条命令执行后会提示 `Added global MCP server 'xxx'`。添加完可用 `codex mcp list` 查看已安装的服务。

> ⚠️ **首次启动超时问题**：npx 首次运行需下载包，默认 30 秒超时不够用。添加完后需手动编辑 `~/.codex/config.toml`，给每个 npx 服务加 `startup_timeout_sec`：
>
> ```toml
> [mcp_servers.playwright]
> command = "npx"
> args = ["@playwright/mcp@latest"]
> startup_timeout_sec = 120
> ```
>
> 建议所有 npx 服务统一设为 120 秒（首次下载后后续启动会很快）。

> 🔴 **百炼第三方模型 + MCP 兼容性问题**（2026-07 实测）：
>
> Codex CLI 的 MCP 工具注入目前**只对 OpenAI 原生模型**（GPT-5.x / o-series）生效。使用百炼 Token Plan 接入的 qwen/deepseek 等第三方模型时：
> - `codex mcp list` 显示服务已连接 ✅
> - `/mcp` 命令能看到所有工具 ✅
> - **但模型实际收到的工具列表中没有 MCP 工具** ❌（只有 `web_search`、`shell_command` 等内置工具）
> - `wire_api = "responses"` 和 `"chat"` 均无法解决
>
> **如果你主要用百炼 + MCP**，建议改用 **Claude Code**（MCP 全通）或 **OpenCode**（MCP 正常）。Codex CLI 留作无 MCP 的简单任务使用。

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

### 报错 `wire_api = chat is no longer supported` 怎么办？

**原因**：Codex 新版本使用 Responses API，不支持 `wire_api = "chat"` 配置。

**解决方案**：
- 将 `wire_api` 改为 `responses`，并将 `model` 改为支持 Responses API 的模型（如 `qwen3.7-max`）
- 或降级到旧版本：`npm install -g @openai/codex@0.80.0`

### 报错 `unexpected status 401 Unauthorized` 怎么办？

**原因**：API Key 复制不完整、有空格或拼写错误，或 API Key 已过期。

**解决方案**：
- 重新复制 API Key，确保完整且无空格
- 前往[百炼控制台](https://bailian.console.aliyun.com/)确认 API Key 是否有效
- 如仍报错，可重置 API Key 后重新配置

### 报错 `unexpected status 404 Not Found` 怎么办？

**原因**：配置文件中的 `base_url` 或 `wire_api` 填写错误。

**解决方案**：确认 `base_url` 为 `https://dashscope.aliyuncs.com/compatible-mode/v1`，`wire_api` 与所选模型匹配。

---

> - 📝 Codex 调用阿里云百炼配置：`https://help.aliyun.com/zh/model-studio/codex`
> - 📘 官方文档：`https://openai.com/index/introducing-codex/`
