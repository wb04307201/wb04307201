# Dify 工作流搭建示例教程：AI 写作助手

本教程将带你从零开始在 Dify 中搭建一个「AI 写作助手」工作流，并将其发布为 API，最后演示如何调用该 API。

## 前置条件

- 已部署 Dify 服务（本教程使用 `http://localhost`）
- 已配置模型供应商（本教程使用通义千问 `qwen3.6-plus`）
- 已有 Dify 账号并已登录

---

## 第一步：创建应用

登录 Dify 后，进入「工作室」页面，点击 **创建空白应用** 按钮。

![01 - 登录后的工作室页面](tutorial-images/01-login.png)

![02 - 点击创建空白应用](tutorial-images/02-create-app.png)

---

## 第二步：选择应用类型并填写信息

在弹出的对话框中：

1. 选择 **工作流** 类型（面向单轮自动化任务的编排工作流）
2. 填写应用名称：**AI 写作助手**
3. 填写描述：**这是一个示例工作流，接收用户输入的主题和风格，自动生成对应的文章内容**
4. 点击 **创建** 按钮

![03 - 选择工作流类型](tutorial-images/03-select-workflow-type.png)

![04 - 填写应用信息](tutorial-images/04-fill-app-info.png)

---

## 第三步：选择开始节点

创建成功后，系统会提示选择开始节点。选择 **用户输入（原始开始节点）**，它允许设置用户输入变量，具有 Web 应用程序、服务 API 等功能。

![05 - 选择开始节点](tutorial-images/05-select-start-node.png)

---

## 第四步：了解工作流画布

进入工作流画布编辑器后，可以看到默认的「开始」节点。画布顶部有发布、测试运行等操作按钮。

![06 - 工作流画布](tutorial-images/06-workflow-canvas.png)

---

## 第五步：添加 LLM 节点

1. 点击「开始」节点右侧的 **添加节点** 按钮
2. 在弹出的搜索框中输入 `LLM`
3. 选择 LLM 节点类型，它将被自动连接到开始节点之后

![07 - 添加 LLM 节点](tutorial-images/07-llm-node-added.png)

---

## 第六步：配置开始节点的输入变量

点击「开始」节点，添加输入字段。

### 添加第一个变量：文章主题

1. 点击 **添加输入字段**
2. 填写如下信息：
    - **变量名称**：`topic`
    - **显示名称**：`文章主题`
    - **默认值**：`人工智能`
    - **必填**：勾选

![08 - 添加 topic 变量](tutorial-images/08-add-topic-variable.png)

### 添加第二个变量：写作风格

1. 再次点击 **添加输入字段**
2. 填写如下信息：
    - **变量名称**：`style`
    - **显示名称**：`写作风格`
    - **默认值**：`正式`
    - **必填**：勾选

![09 - 添加 style 变量](tutorial-images/09-add-style-variable.png)

---

## 第七步：配置 LLM 节点

点击 LLM 节点，在右侧面板中配置提示词：

1. 确认模型已选择为 `qwen3.6-plus`（系统默认模型）
2. 在 **SYSTEM** 提示词编辑区中输入以下内容：

```
你是一位专业的文章写作助手。请根据用户提供的主题和写作风格，生成一篇高质量的文章。

主题：{{#1778986959696.topic#}}
写作风格：{{#1778986959696.style#}}

请直接输出文章内容，无需额外解释。
```

> **说明**：`{{#1778986959696.topic#}}` 和 `{{#1778986959696.style#}}` 是引用开始节点中定义的变量。在实际操作中，你可以在编辑器中输入 `{` 来选择并插入变量。

![10 - 配置 LLM 提示词](tutorial-images/10-configure-llm-prompt.png)

---

## 第八步：添加输出节点

1. 点击 LLM 节点右侧的 **选择下一个节点**
2. 搜索并选择 **输出** 节点类型
3. 在输出节点中：
    - 点击 **添加输出变量**
    - 变量名填写：`text`
    - 变量值选择 LLM 节点的 `text` 输出

![11 - 添加输出节点](tutorial-images/11-add-output-node.png)

![12 - 配置输出变量](tutorial-images/12-configure-output.png)

---

## 第九步：测试运行工作流

完成以上配置后，点击顶部的 **测试运行** 按钮进行测试。

![13 - 测试运行面板](tutorial-images/13-test-run-panel.png)

在测试面板中，系统会自动填充之前设置的默认值（主题：人工智能，风格：正式），点击 **开始运行**。

![14 - 测试运行中](tutorial-images/14-test-running.png)

运行成功后，可以在结果中看到 AI 生成的文章。

![15 - 测试成功](tutorial-images/15-test-success.png)

---

## 第十步：发布工作流

测试通过后，点击右上角的 **发布** 按钮，在弹出菜单中选择 **发布更新**。

![16 - 发布工作流](tutorial-images/16-api-develop-page.png)

发布成功后，状态会显示为「已发布」。

---

## 第十一步：访问 API 文档

点击 **访问 API** 链接，或直接访问：

```
http://localhost/app/{your-app-id}/develop
```

在 API 开发文档页面，可以看到：

- **Base URL**：`http://localhost/v1`
- **API 密钥**：在页面上复制你的 API Key（格式为 `app-xxxxx`）

> **注意**：API Key 请在你的 Dify 实例上自行获取。出于安全考虑，请将 API Key 存储在后端，不要暴露在前端代码或公开仓库中。

---

## 如何调用工作流 API

### API 端点

```
POST http://localhost/v1/workflows/run
```

### 请求头

```
Content-Type: application/json
Authorization: Bearer {你的API_KEY}
```

### 请求体

```json
{
  "inputs": {
    "topic": "人工智能",
    "style": "正式"
  },
  "response_mode": "blocking",
  "user": "user-123"
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inputs` | object | 是 | 工作流输入变量，键值对形式 |
| `inputs.topic` | string | 是 | 文章主题 |
| `inputs.style` | string | 是 | 写作风格 |
| `response_mode` | string | 是 | 返回模式：`streaming`（流式）或 `blocking`（阻塞） |
| `user` | string | 是 | 用户标识，由开发者自行定义 |

### curl 示例

```bash
curl -X POST 'http://localhost/v1/workflows/run' \
  --header 'Authorization: Bearer app-xxxxxxxxxxxxxxxxxxxxxxxx' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "inputs": {
      "topic": "人工智能",
      "style": "正式"
    },
    "response_mode": "blocking",
    "user": "user-123"
  }'
```

### Python 示例

```python
import requests
import json

# 配置
BASE_URL = "http://localhost/v1"
API_KEY = "app-xxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为你的 API Key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "inputs": {
        "topic": "人工智能",
        "style": "正式"
    },
    "response_mode": "blocking",
    "user": "user-123"
}

response = requests.post(f"{BASE_URL}/workflows/run", headers=headers, json=data)
result = response.json()

# 输出结果
print("Workflow Run ID:", result.get("workflow_run_id"))
print("Task ID:", result.get("task_id"))

# 获取文章输出
outputs = result.get("data", {}).get("outputs", {})
if "text" in outputs:
    print("\n生成的文章：\n")
    print(outputs["text"])
```

### 流式响应示例（推荐）

如果希望实时看到生成过程，将 `response_mode` 改为 `streaming`：

```python
import requests

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "inputs": {
        "topic": "人工智能",
        "style": "正式"
    },
    "response_mode": "streaming",
    "user": "user-123"
}

response = requests.post(f"{BASE_URL}/workflows/run", headers=headers, json=data, stream=True)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode("utf-8")
        if decoded_line.startswith("data:"):
            event_data = json.loads(decoded_line[5:])
            if event_data.get("event") == "workflow_finished":
                print("最终输出:", event_data["data"]["outputs"])
                break
            elif event_data.get("event") == "text_chunk":
                print(event_data["data"]["text"], end="", flush=True)
```

### 响应示例（blocking 模式）

```json
{
  "workflow_run_id": "abc123-def456-ghi789",
  "task_id": "task-001",
  "data": {
    "id": "abc123-def456-ghi789",
    "workflow_id": "f9f8eb41-306f-4756-bb50-246fa11d7d93",
    "status": "succeeded",
    "outputs": {
      "text": "人工智能：重塑现代社会的范式转移与伦理考量\n\n随着计算能力的指数级增长..."
    },
    "elapsed_time": 12.5,
    "total_tokens": 3562,
    "total_steps": 3,
    "created_at": 1716087863,
    "finished_at": 1716087875
  }
}
```

---

## 工作流节点总览

最终搭建的工作流包含 3 个节点，线性连接：

```
[开始: 用户输入] → [LLM: 生成文章] → [输出: 返回结果]
      │                    │                    │
   topic, style      qwen3.6-plus          text (LLM输出)
```

- **开始节点**：接收 `topic`（文章主题）和 `style`（写作风格）两个输入变量
- **LLM 节点**：使用 qwen3.6-plus 模型，根据提示词模板和输入变量生成文章
- **输出节点**：将 LLM 的文本输出作为工作流的最终返回结果

---

## 总结

通过这个教程，你学会了：

1. 在 Dify 中创建工作流应用
2. 配置用户输入节点和变量
3. 添加并配置 LLM 节点（提示词模板、变量引用）
4. 添加输出节点并映射输出变量
5. 测试运行工作流
6. 发布工作流并通过 API 调用

你可以在此基础上扩展更多功能，比如添加知识检索节点、条件分支、代码执行节点等，构建更复杂的工作流。
