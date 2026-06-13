# Agent 协议 —— MCP 与 A2A

> 从阿明的 20 个 Agent 各自为政，到全栈打通 —— 看 AI 时代的"TCP/IP"：MCP 与 A2A 协议

> **系列定位**：本篇是「阿明餐厅」系列的**续集十一**。在[续集一 · 《当餐厅长出大脑》](./01-ai-agent-architecture.md)第五章，我们讲了多智能体协同（Orchestrator + 消息总线）。在[续集八 · 《Agent Harness》](./32-agent-harness.md)第三章，我们讲了 Tool 设计。但都还是"自己设计、自己实现"。2024-2026 年，业界出现了**两个重量级协议标准** —— **MCP（Model Context Protocol，Anthropic 主导）** 和 **A2A（Agent-to-Agent，Google 主导）** —— 它们正在成为 AI 时代的"TCP/IP"，让 Agent 与 Agent、Agent 与工具之间有了**统一的"语言"**。本篇不谈"如何实现一个协议"，谈**"协议层给整个 AI 生态带来了什么变化、怎么选型、怎么落地"**。

---

## 引言：20 个 Agent 互相听不懂对方说话

2025 年底，阿明的 AI 厨房已经部署了 20 个 Agent：

- 订单 Agent
- 库存 Agent
- 推荐 Agent
- 客服 Agent
- 财务 Agent
- 排班 Agent
- ...

每个 Agent 都有自己定义的"工具"：

- 订单 Agent 有 `query_order`、`update_order`
- 库存 Agent 有 `check_stock`、`decrease_stock`
- 推荐 Agent 有 `recommend_dish`、`update_user_pref`

问题来了：**Agent A 想调用 Agent B 的工具，怎么办？**

老陈最初的做法是写"胶水代码"：

```python
# 订单 Agent 想调库存 Agent
def order_agent_check_stock(item_id):
    # 硬编码 HTTP 调用
    response = requests.post("http://inventory-agent:8000/api/check_stock", 
                              json={"item_id": item_id})
    return response.json()
```

但随着 Agent 数量增长：

```text
问题 1: 接口变更灾难
  库存 Agent 把 check_stock 重命名成 query_stock
  → 订单 Agent 调不通
  → 要改 5 个调用方
  → 改了 3 个就上线
  → 生产事故

问题 2: 协议碎片化
  - HTTP REST (库存 Agent)
  - gRPC (财务 Agent)
  - GraphQL (推荐 Agent)
  - 自定义 JSON-RPC (订单 Agent)
  → 每个 Agent 都要写 4 套适配器
  → 维护成本爆炸

问题 3: 安全模型不统一
  - 库存 Agent 用 mTLS
  - 财务 Agent 用 API Key
  - 订单 Agent 干脆不要认证（内网！）
  → 安全审计没法做

问题 4: 上下文传递缺失
  Agent A 调用 Agent B 时：
  - 要不要传"用户身份"？
  - 要不要传"对话历史"？
  - 要不要传"上次失败的错误信息"？
  → 每个 Agent 自己决定 → 不一致
```

老陈仰天长叹：

> "**这就像 1980 年代的网络 —— 每个厂商都做自己的协议，每台机器都自己定义接口。结果是谁都连不上谁。直到 TCP/IP 出现，互联网才真正爆发。** **AI 时代需要自己的 TCP/IP —— 不然 Agent 之间就是孤岛。**"

2024 年底，**Anthropic 推出 MCP（Model Context Protocol）**；2025 年，**Google 联合 50+ 厂商推出 A2A（Agent-to-Agent）**。这两个协议在 2026 年正在成为事实标准。

---

## 第一章：MCP 是什么 —— Agent 调用工具的"USB-C"

### 1.1 MCP 的诞生

2024 年 11 月，Anthropic 发布 **MCP（Model Context Protocol）**，目标是：

> **让 LLM 统一接入"任何工具 / 任何数据源"** —— 就像 USB-C 接口统一了电子设备的连接。

类比传统软件：

```text
传统软件调用数据库：
  各种数据库 → 各种驱动 → 应用层
  MySQL Driver / PG Driver / Oracle Driver / ...
  → 换数据库要改代码

MCP 之前 AI 调用工具：
  各种工具 → 各种协议 → Agent
  HTTP / gRPC / 自定义 / ...
  → 加新工具要写适配器

MCP 之后：
  工具实现 MCP Server → Agent 实现 MCP Client → 自动发现 + 自动调用
  → 加新工具 = 注册一下，不改 Agent 代码
```

### 1.2 MCP 的核心架构

```mermaid
graph LR
    subgraph Agent
        A[LLM]
        C[MCP Client]
    end
    
    subgraph "MCP Servers (工具集)"
        S1[文件系统<br/>MCP Server]
        S2[数据库<br/>MCP Server]
        S3[GitHub<br/>MCP Server]
        S4[内部业务<br/>MCP Server]
    end
    
    A --> C
    C <-->|JSON-RPC| S1
    C <-->|JSON-RPC| S2
    C <-->|JSON-RPC| S3
    C <-->|JSON-RPC| S4
```

**MCP 三个核心概念**：

```text
1. Resources（资源）
   Agent 可以"读"的数据
   例：文件、数据库表、API 返回值

2. Tools（工具）
   Agent 可以"调"的函数
   例：query_order、send_email

3. Prompts（提示词模板）
   Agent 可以"用"的预定义提示词
   例：总结模板、翻译模板
```

**MCP 的协议层**：

```text
MCP 协议栈（简化）：
  - 传输层：JSON-RPC over stdio / HTTP+SSE
  - 能力层：Tools / Resources / Prompts 三大能力
  - 协商层：Client 和 Server 自动协商能力
  - 鉴权层：可选 OAuth / API Key
```

### 1.3 MCP 解决了什么问题

**问题 1：工具接入的 N×M 复杂度 → N+M 复杂度**

```text
没有 MCP：
  10 个 Agent × 20 个工具 = 200 个集成点
  加 1 个工具 → 改 10 个 Agent

有 MCP：
  10 个 Agent（实现 MCP Client）× 20 个 MCP Server = 30 个实现
  加 1 个工具 → 实现 1 个 MCP Server，所有 Agent 自动可用
```

**问题 2：工具的"可发现性"**

```text
传统工具调用：
  Agent 开发者必须事先知道"有什么工具、怎么用、参数是什么"
  → 文档散落 / 版本不一致

MCP 工具发现：
  Agent 启动时 → 问每个 MCP Server "你有什么能力"
  → Server 返回工具列表 + 描述 + 参数 schema
  → Agent 自动知道能用什么
```

**问题 3：上下文传递标准化**

```text
MCP 定义了"采样"（sampling）和"根"（roots）概念：
  - Sampling：让 Server 能请 Client 的 LLM 来处理复杂任务
  - Roots：让 Server 知道当前操作的"作用域"
  → 跨 Agent 的上下文传递有了标准
```

### 1.4 一个 MCP Server 的实现示例

```python
# 实现一个"查询订单"的 MCP Server
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("order-tools")

@app.tool()
async def query_order(order_id: str) -> list[TextContent]:
    """查询订单状态"""
    order = db.query("SELECT * FROM orders WHERE id = ?", order_id)
    return [TextContent(type="text", text=str(order))]

@app.tool()
async def update_order_address(order_id: str, new_address: str) -> list[TextContent]:
    """修改订单地址（需要 HITL 审批）"""
    if not await human_approval(order_id, "update_address"):
        return [TextContent(type="text", text="需要人工审批")]
    db.execute("UPDATE orders SET address = ? WHERE id = ?", new_address, order_id)
    return [TextContent(type="text", text="地址已更新")]

# 启动：MCP Server 在 stdio 上监听
app.run()
```

**Agent 端（MCP Client）调用**：

```python
# Agent 通过 MCP Client 自动发现 + 调用
from mcp import Client

client = Client()
await client.connect_stdio("python order_server.py")

# 自动列出所有工具
tools = await client.list_tools()
# [Tool(name="query_order", description="查询订单状态", ...), ...]

# 调用工具
result = await client.call_tool("query_order", {"order_id": "123"})
print(result)
```

### 1.5 MCP 的生态现状（2026 年）

| 类别 | 已实现的 MCP Server |
|------|---------------------|
| **数据源** | PostgreSQL / SQLite / Redis / MongoDB / S3 |
| **开发工具** | GitHub / GitLab / Jira / Linear / Notion |
| **生产力** | Slack / Email / Calendar / Drive |
| **浏览器** | Playwright / Puppeteer / Chrome DevTools |
| **AI 工具** | Replicate / Hugging Face / OpenAI |
| **企业内部** | 订单系统 / 库存系统 / 财务系统（自建） |

**主流 Agent 框架已支持 MCP**：
- Claude Desktop / Claude Code
- Cursor / Cline / Continue
- LangChain / LlamaIndex
- OpenAI Agents SDK
- 国内：Qwen Agent / 文心 Agent / 智谱 Agent

### 1.6 MCP 的局限

**局限 1：MCP 是"工具协议"，不是"Agent 协议"**

```text
MCP 解决：Agent ↔ 工具
  Agent 调用数据库 / API / 文件

MCP 不解决：Agent ↔ Agent
  Agent A 让 Agent B 完成一个子任务
  Agent A 和 Agent B 协商"谁来做什么"
  Agent 间的状态同步、消息路由
```

→ **A2A 协议** 解决这些问题（见第二章）

**局限 2：MCP Server 本身的安全责任**

```text
MCP 协议不强制鉴权
  → 任何 MCP Client 都能连任何 MCP Server
  → 需要在 Server 端自己做权限控制

MCP Server 拿到的是 Agent 的"全部上下文"
  → 任何漏洞 = 全部泄露
  → 这是 [33 致命三件套](./33-ai-fatal-trio.md) 中"数据外泄"的新攻击面
```

**局限 3：MCP 的"工具膨胀"问题**

```text
如果一个 Agent 接入 100 个 MCP Server
  → 工具列表爆炸（LLM context window 装不下）
  → 需要"工具检索"（见 32 Agent Harness 第 5 章）
```

---

## 第二章：A2A 是什么 —— Agent 协同的"邮件协议"

### 2.1 A2A 的诞生

2025 年 4 月，Google 联合 50+ 厂商（包括 Salesforce、Atlassian、LangChain、Anthropic 后续加入）发布 **A2A（Agent-to-Agent）协议**。

**目标**：让不同厂商、不同框架的 Agent 能够互相发现、互相通信、互相协作。

类比传统互联网：

```text
TCP/IP：机器 ↔ 机器
SMTP / IMAP：邮件 ↔ 邮件
A2A：Agent ↔ Agent
```

### 2.2 A2A 的核心概念

```text
1. Agent Card（Agent 卡片）
   Agent 的"自我介绍"
   例："我是订单 Agent，能做查询订单、修改地址、退款"

2. Task（任务）
   Agent 间的协作单元
   "我请你做一件事，做完告诉我结果"

3. Artifact（产物）
   任务完成后产出的"结果"
   例：生成的报告、修改后的数据、决策建议

4. Message（消息）
   Agent 间的通信内容
   "用户想要查询订单 123 的状态"
```

### 2.3 A2A 的工作流

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as Orchestrator Agent
    participant B as 订单 Agent
    participant C as 库存 Agent
    participant D as 推荐 Agent
    
    U->>A: "我想点红烧肉，但怕太咸"
    A->>A: 拆解任务
    A->>B: Task: 查询用户最近订单
    B-->>A: Artifact: 最近订单列表
    A->>C: Task: 检查红烧肉库存
    C-->>A: Artifact: 还有 3 份
    A->>D: Task: 推荐咸度低的菜品
    D-->>A: Artifact: 推荐清蒸鱼
    A->>U: 综合回答
```

### 2.4 A2A 的关键特性

**特性 1：能力发现（Capability Discovery）**

```python
# Orchestrator Agent 想知道"附近有哪些 Agent"
async def discover_agents():
    # 通过 A2A 协议，扫描已注册的 Agent Cards
    agents = await a2a_registry.discover(capability="order_management")
    for agent in agents:
        print(f"{agent.name}: {agent.description}")
        print(f"Skills: {agent.skills}")
```

**特性 2：任务委派（Task Delegation）**

```python
# 派发任务给订单 Agent
task = await a2a.send_task(
    to="order-agent",
    skill="query_order",
    inputs={"order_id": "123"},
)

# 异步等结果
result = await task.wait_for_completion(timeout=30)
```

**特性 3：流式协作（Streaming Collaboration）**

```text
A2A 支持 server-sent events (SSE)
  → 任务执行中持续推送进度
  → Orchestrator 实时更新 UI

例：
  "正在查询订单..." (10%)
  "正在检查库存..." (50%)
  "正在生成推荐..." (80%)
  "完成" (100%)
```

**特性 4：多模态产物（Multimodal Artifacts）**

```text
任务的产物可以是：
  - 文本（回答、报告）
  - 图像（生成的图）
  - 文件（生成的 PDF）
  - 数据（结构化 JSON）
  - 引用（"详见 X 文档"）
```

### 2.5 A2A 的安全模型

A2A 设计时考虑了 4 层安全：

```text
Layer 1 - 身份认证
  Agent 之间用 mTLS / OAuth 互相认证
  "你是真的订单 Agent，不是冒牌"

Layer 2 - 能力证明
  Agent Card 声明的能力必须可验证
  "你说你能退款，但有没有退款权限？"

Layer 3 - 任务隔离
  每个任务有独立 context
  任务间不共享敏感信息

Layer 4 - 审计日志
  所有 A2A 通信都有不可篡改的日志
  事故可追溯
```

### 2.6 A2A 解决了什么问题

**问题 1：跨厂商 Agent 互操作**

```text
场景：阿明用 Anthropic 的 Claude Agent + Google 的 ADK Agent + 自研 Agent

没有 A2A：
  每两个 Agent 之间要写胶水代码
  3 个 Agent = 3 套适配器

有 A2A：
  每个 Agent 实现 A2A 接口
  自动发现 + 自动协作
```

**问题 2：Agent 间的"长任务"协作**

```text
场景：用户问"分析上季度销售数据并写报告"
  → 涉及 5 个 Agent（数据 Agent + 分析 Agent + 报告 Agent + 图表 Agent + 审核 Agent）
  → 任务耗时 30 分钟

A2A 支持：
  异步任务 + 状态推送 + 部分结果返回
  → 用户可以"挂着"等，30 分钟后再看
```

**问题 3：异构 Agent 统一管理**

```text
企业内部有：
  - LangChain 写的客服 Agent
  - CrewAI 写的分析 Agent
  - AutoGen 写的决策 Agent

A2A 提供统一管理：
  - 统一注册中心
  - 统一监控
  - 统一计费
  - 统一安全审计
```

---

## 第三章：MCP vs A2A vs 自研 —— 怎么选

很多团队面对 MCP / A2A / 自研不知道选哪个。阿明总结了一个**3 维选型矩阵**。

### 3.1 选型矩阵

| 维度 | MCP | A2A | 自研 |
|------|-----|-----|------|
| **解决什么** | Agent ↔ 工具 | Agent ↔ Agent | 完全自控 |
| **生态成熟度** | 高（2026 标准） | 中（2026 早期） | N/A |
| **学习成本** | 低 | 中 | 高 |
| **定制能力** | 中（受协议约束） | 中 | 高 |
| **安全模型** | 需自实现 | 内置 4 层 | 完全自控 |
| **跨厂商** | 是 | 是 | 否 |

### 3.2 决策树

```text
问题 1: 你要解决的核心问题是什么？
├─ Agent 调用"工具"（数据库 / API / 文件）→ MCP
├─ Agent 协同"其他 Agent"（任务委派 / 多步协作）→ A2A
├─ 两者都要 → MCP + A2A
└─ 极度定制化（金融 / 医疗 / 军工）→ 自研

问题 2: 你的 Agent 数量级？
├─ < 5 个 Agent：自研也行
├─ 5-20 个 Agent：MCP（工具）+ 简单自研（Agent 协同）
└─ > 20 个 Agent：MCP + A2A（标准 + 生态）

问题 3: 你的 Agent 是否跨厂商 / 跨团队？
├─ 同厂商 / 同团队：MCP + 自研协同
└─ 异构 / 跨团队：MCP + A2A（必选）
```

### 3.3 阿明的选型结论

```text
阿明的 20 个 Agent 选型：

工具层：MCP
  - 所有"工具"实现为 MCP Server
  - Agent 都用 MCP Client
  - 加新工具 = 加一个 MCP Server（不改 Agent）

协同层：A2A（早期采用）
  - 复杂任务用 A2A 协议
  - Orchestrator Agent 用 A2A 派发子任务
  - 简单任务还是直接函数调用

特殊场景：自研
  - 财务 Agent 涉及金额，单独跑、不开放
  - 自研协议 + 强审计
```

### 3.4 实施路线图

```text
Phase 1（1-2 月）：MCP 试点
  - 选 1-2 个工具做 MCP Server（订单查询、库存查询）
  - 1-2 个 Agent 接入 MCP Client
  - 验证协议可行性

Phase 2（3-4 月）：MCP 推广
  - 所有"通用工具"实现 MCP Server
  - 所有 Agent 接入 MCP
  - 建立 MCP 注册中心

Phase 3（5-6 月）：A2A 引入
  - 复杂任务用 A2A 协同
  - 至少 3 个 Agent 实现 A2A
  - 跨团队 / 跨厂商的 Agent 优先

Phase 4（7-12 月）：混合架构
  - MCP（工具）+ A2A（协同）+ 自研（特殊）
  - 统一可观测性 / 安全 / 计费
```

---

## 第四章：协议层的 6 大设计原则

无论选 MCP / A2A / 自研，**协议本身的设计原则**是相通的。阿明总结了 6 大原则。

### 4.1 原则 1：能力可发现

```text
好协议：
  Agent 启动时自动知道"周围有什么能力可用"
  → MCP 的 list_tools / A2A 的 Agent Card

差协议：
  Agent 必须事先知道"有什么工具"
  → 文档散落，版本不一致
```

### 4.2 原则 2：调用可追溯

```text
好协议：
  每次调用都有 trace_id
  → 跨 Agent / 跨工具的全链路追踪

差协议：
  调用是黑盒
  → 出问题不知道哪个环节错了
```

### 4.3 原则 3：失败可重试

```text
好协议：
  协议层内置 idempotency_key
  → 失败可重试，不重复执行

差协议：
  失败 = 重头来
  → 邮件发了 3 次 / 钱扣了 3 次
```

### 4.4 原则 4：安全可审计

```text
好协议：
  协议层内置 authn / authz / audit log
  → 谁调了什么 / 改了什么都可查

差协议：
  安全靠"内网" / 靠"约定俗成"
  → 审计缺失
```

### 4.5 原则 5：能力可扩展

```text
好协议：
  协议版本向后兼容
  → 老 Client 调新 Server 不挂

差协议：
  协议一变，所有调用方都要改
```

### 4.6 原则 6：成本可计量

```text
好协议：
  协议层记录 token / 时间 / 算力消耗
  → 不同 Agent 的成本可分摊

差协议：
  成本是黑盒
  → 不知道谁花了多少
```

---

## 第五章：MCP 落地实践

阿明把 MCP 用在了 5 个最常见的场景，本节展开。

### 5.1 场景 1：MCP 接入数据库

```python
# PostgreSQL MCP Server（开源已有）
# Agent 想"查订单 123"
from mcp import Client

client = Client()
await client.connect_stdio("mcp-server-postgres", 
                             args=["postgresql://user:pass@localhost/orders"])

# 列出表
tables = await client.list_resources()
# [Resource(uri="postgres://orders/orders_table", ...)]

# 查询
result = await client.read_resource("postgres://orders/orders_table?where=id=123")
```

**关键配置**：

```yaml
# MCP Server 配置
server:
  name: postgres-orders
  transport: stdio
  auth: oauth
  scope: read-only  # 重要！只读权限
  
# 防止 [33 致命三件套](./33-ai-fatal-trio.md) 的"过度授权"
```

### 5.2 场景 2：MCP 接入内部业务系统

```python
# 内部订单系统 MCP Server
@app.tool()
async def create_order(customer_id: str, items: list, total: float) -> dict:
    """创建订单"""
    # 1. 业务校验
    if not await customer_exists(customer_id):
        return {"error": "Customer not found"}
    
    # 2. HITL（大额订单）
    if total > 1000:
        if not await human_approval("create_large_order", {"customer": customer_id, "total": total}):
            return {"error": "需要人工审批"}
    
    # 3. 创建订单
    order = await db.orders.create(customer_id=customer_id, items=items, total=total)
    return {"order_id": order.id, "status": "created"}
```

### 5.3 场景 3：MCP + 多模态

```python
# 图像识别 MCP Server
@app.tool()
async def analyze_image(image_path: str, question: str) -> dict:
    """分析图像并回答问题"""
    # 调用 Claude Vision
    result = await claude.vision.analyze(image_path=image_path, question=question)
    return {"answer": result.text, "confidence": result.confidence}

# Agent 接到"分析用户上传的菜品照片"
# 1. 读取图片（Resource）
image = await client.read_resource(f"file://{image_path}")

# 2. 调工具分析
result = await client.call_tool("analyze_image", {
    "image_path": image_path,
    "question": "这是什么菜？估算热量？"
})
```

### 5.4 场景 4：MCP + RAG

```python
# 知识库 MCP Server
@app.tool()
async def search_knowledge_base(query: str, top_k: int = 5) -> list:
    """检索知识库"""
    results = await vector_db.search(query=query, top_k=top_k)
    return [{"content": r.text, "score": r.score, "source": r.source} for r in results]

@app.resource("knowledge://menu")
async def get_menu_documents() -> list:
    """获取菜单文档列表"""
    return await db.query("SELECT * FROM menu_docs")
```

### 5.5 场景 5：MCP + 浏览器自动化

```python
# Playwright MCP Server
@app.tool()
async def browse_webpage(url: str, action: str) -> dict:
    """浏览器自动化"""
    async with playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        if action == "screenshot":
            screenshot = await page.screenshot()
            return {"type": "image", "data": screenshot}
        elif action == "extract_text":
            text = await page.text_content("body")
            return {"type": "text", "data": text}
```

---

## 第六章：A2A 落地实践

### 6.1 阿明的 A2A 架构

```mermaid
graph TB
    subgraph "Orchestrator 层"
        O[Master Orchestrator]
    end
    
    subgraph "Specialist Agents (A2A Workers)"
        A1[订单 Agent]
        A2[库存 Agent]
        A3[推荐 Agent]
        A4[客服 Agent]
        A5[财务 Agent]
        A6[分析 Agent]
    end
    
    subgraph "A2A Registry"
        R[Agent 注册中心]
    end
    
    O <-->|A2A| A1
    O <-->|A2A| A2
    O <-->|A2A| A3
    O <-->|A2A| A4
    O <-->|A2A| A5
    O <-->|A2A| A6
    
    A1 -.register.-> R
    A2 -.register.-> R
    A3 -.register.-> R
    A4 -.register.-> R
    A5 -.register.-> R
    A6 -.register.-> R
```

### 6.2 Agent Card 示例

```yaml
# order_agent_card.yaml
name: order-agent
version: 1.2.0
description: 处理订单查询、修改、退款
provider: 阿明餐厅
skills:
  - name: query_order
    description: 查询订单状态
    inputs:
      order_id: string
    outputs:
      order: object
  - name: update_address
    description: 修改订单地址
    inputs:
      order_id: string
      new_address: string
    outputs:
      success: boolean
    requires_hitl: true
  - name: refund_order
    description: 退款
    inputs:
      order_id: string
      amount: number
      reason: string
    outputs:
      refund_id: string
    requires_hitl:
      threshold: 200
auth:
  type: oauth2
  scopes: [order:read, order:write]
security:
  rate_limit: 100/min
  allowed_callers: [orchestrator, customer-service-agent]
```

### 6.3 复杂任务的 A2A 编排

```python
# Master Orchestrator 派发"分析上季度销售并写报告"
async def quarterly_report_task():
    # 任务 1: 数据 Agent 拉数据
    task1 = await a2a.send_task(
        to="data-agent",
        skill="query_sales",
        inputs={"quarter": "Q1-2026"},
    )
    sales_data = await task1.wait_for_completion()
    
    # 任务 2 & 3 并行：分析 + 图表
    task2 = await a2a.send_task("analysis-agent", "analyze_trends", {"data": sales_data})
    task3 = await a2a.send_task("chart-agent", "generate_charts", {"data": sales_data})
    
    trends = await task2.wait_for_completion()
    charts = await task3.wait_for_completion()
    
    # 任务 4: 报告 Agent 综合
    task4 = await a2a.send_task(
        to="report-agent",
        skill="generate_report",
        inputs={"trends": trends, "charts": charts},
    )
    report = await task4.wait_for_completion()
    
    # 任务 5: 审核 Agent 审核
    task5 = await a2a.send_task(
        to="review-agent",
        skill="review_report",
        inputs={"report": report},
        requires_human_approval=True,  # 关键报告人工审核
    )
    final_report = await task5.wait_for_completion()
    
    return final_report
```

### 6.4 A2A 的错误处理

```python
# A2A 的 4 类错误
class A2AError:
    AGENT_UNAVAILABLE = "agent_unavailable"     # 目标 Agent 不可用
    SKILL_NOT_FOUND = "skill_not_found"         # 技能不存在
    TIMEOUT = "timeout"                          # 超时
    PARTIAL_FAILURE = "partial_failure"          # 部分失败

# Orchestrator 的错误处理策略
async def send_task_with_retry(agent, skill, inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await a2a.send_task(agent, skill, inputs, timeout=30)
        except A2AError.AGENT_UNAVAILABLE:
            # 尝试备用 Agent
            backup_agent = get_backup_agent(skill)
            if backup_agent:
                return await a2a.send_task(backup_agent, skill, inputs, timeout=30)
        except A2AError.TIMEOUT:
            # 重试
            await asyncio.sleep(2 ** attempt)
    raise Exception(f"Failed after {max_retries} retries")
```

---

## 第七章：协议层的 5 大安全陷阱

协议层给了我们便利，**也给了我们新的攻击面**。阿明结合[33 致命三件套](./33-ai-fatal-trio.md)总结了 5 大陷阱。

### 7.1 陷阱 1：MCP Server 是新的"特权代码"

```text
传统攻击面：应用代码有 SQL 注入 / RCE 漏洞
MCP 时代攻击面：MCP Server 本身

攻击场景：
  黑客攻破一个 MCP Server
  → 拿到所有调用方的上下文
  → 在工具返回中插入"Prompt 注入"（间接注入）
  → 所有调用的 Agent 都被劫持
```

**防御**：
- MCP Server 最小权限（只给必要的工具 / 只给必要的数据）
- MCP Server 的输出也要"清洗"（防间接注入）
- MCP Server 的审计日志

### 7.2 陷阱 2：A2A 的"信任传递"漏洞

```text
场景：
  Orchestrator Agent 信任订单 Agent
  订单 Agent 被攻破 → Orchestrator 信任了恶意内容

信任传递链：
  A 信任 B → B 信任 C → A 信任 C（错误的！）
```

**防御**：
- A2A 通信不直接信任，需 Orchestrator 二次验证
- 关键决策必须 HITL
- 异常行为检测

### 7.3 陷阱 3：协议层的 DoS

```text
攻击场景：
  注册 1000 个假 Agent → 占据注册中心
  或用大量调用压垮 MCP Server
```

**防御**：
- 注册中心鉴权 + 限流
- MCP Server 限流 + 熔断
- 异常 Agent 自动拉黑

### 7.4 陷阱 4：协议版本的"中间人"

```text
攻击场景：
  老版本 MCP Client 不知道新协议的能力
  攻击者伪造"新协议响应"骗取旧 Client 执行危险操作
```

**防御**：
- 协议版本固定 + 显式声明
- 升级强制 + 灰度
- 关键操作必须最新协议

### 7.5 陷阱 5：跨协议的数据外泄

```text
攻击场景：
  MCP 调数据库 → 数据传到 A2A Agent
  → A2A Agent 把数据发给外部 API
  → 数据离开企业边界

跨协议链：
  数据库（隔离）→ MCP Server → A2A Agent（信任）→ 外部 API（不信任）
```

**防御**：
- 跨协议传递的字段必须有"敏感标签"
- 敏感字段在跨协议时自动脱敏
- 完整的链路审计

---

## 第八章：协议层的可观测性

协议层有了，**观测也要跟上**。阿明建立了"协议可观测性 4 件套"。

### 8.1 4 件套

```text
指标 1 - 协议调用量
  每分钟 MCP 调用次数 / A2A 任务数
  趋势、异常峰值

指标 2 - 协议成功率
  MCP 调用成功率 / A2A 任务完成率
  失败原因分类

指标 3 - 协议延迟
  MCP 调用 P50/P99 / A2A 任务耗时
  超时率

指标 4 - 协议成本
  LLM token / 网络流量 / 计算资源
  按 Agent / 按任务 / 按租户分摊
```

### 8.2 协议层的 Trace

```python
# MCP 调用自动 trace
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def call_mcp_with_trace(server, tool, args):
    with tracer.start_as_current_span(f"mcp_call:{server}:{tool}") as span:
        span.set_attribute("mcp.server", server)
        span.set_attribute("mcp.tool", tool)
        span.set_attribute("mcp.args", str(args))
        
        try:
            result = await mcp_client.call_tool(server, tool, args)
            span.set_attribute("mcp.result_size", len(str(result)))
            return result
        except Exception as e:
            span.set_status(trace.Status.ERROR, str(e))
            raise
```

### 8.3 协议层的告警

| 告警 | 触发条件 | 响应 |
|------|----------|------|
| MCP Server 不可用 | 连续 3 次调用失败 | 自动切备用 Server |
| A2A 任务积压 | 任务队列 > 100 | 扩容 Worker |
| 协议调用量突增 | 1 分钟内 > 10× 均值 | 检查是否被攻击 |
| 协议成本异常 | 单次调用 > $1 | 限流 + 人工 review |
| 协议失败率飙升 | 5 分钟内失败率 > 20% | 紧急排查 |

---

## 第九章：协议层的未来趋势

阿明跟踪了协议层的 5 大趋势（2026-2028）。

### 9.1 趋势 1：协议标准化加速

```text
2024: MCP 出现（Anthropic 单家）
2025: A2A 出现（Google 牵头 50+ 厂商）
2026: MCP 和 A2A 开始融合
2027 (预测): "MCP+A2A" 联盟，可能形成 IETF 标准
2028 (预测): 协议成为 AI 基础设施，类比 HTTP/TLS
```

### 9.2 趋势 2：协议层安全标准化

```text
当前：各家协议安全模型不同
未来：统一的协议安全标准
  - 强制 mTLS
  - 统一审计格式
  - AI BOM 与协议绑定
```

### 9.3 趋势 3：协议与可观测性深度结合

```text
当前：协议 + OpenTelemetry 集成
未来：
  - 协议调用即 trace
  - 协议失败即告警
  - 协议成本即 dashboard
  - 协议安全即 AI BOM
```

### 9.4 趋势 4：协议层的"市场"

```text
当前：MCP Server 各自开发
未来：
  - MCP Server Marketplace
  - 商业版 MCP Server（带 SLA）
  - 协议层计费 / 结算标准
```

### 9.5 趋势 5：协议层的"开源治理"

```text
当前：MCP（Anthropic 主导）/ A2A（Linux Foundation）
未来：
  - 基金会治理（避免厂商锁定）
  - 开放标准 + 多实现
  - 协议兼容性认证
```

---

## 核心总结：MCP + A2A 的全景

```mermaid
graph TB
    subgraph "应用层"
        App[用户应用 / Orchestrator]
    end
    
    subgraph "协同层（A2A）"
        A1[Agent A]
        A2[Agent B]
        A3[Agent C]
    end
    
    subgraph "工具层（MCP）"
        M1[MCP Server: 数据库]
        M2[MCP Server: 业务 API]
        M3[MCP Server: 文件]
        M4[MCP Server: 外部服务]
    end
    
    subgraph "基础设施"
        I1[LLM / 模型]
        I2[可观测性]
        I3[安全 / 审计]
        I4[计费 / 成本]
    end
    
    App <-->|A2A| A1
    App <-->|A2A| A2
    App <-->|A2A| A3
    
    A1 <-->|MCP| M1
    A1 <-->|MCP| M2
    A2 <-->|MCP| M2
    A2 <-->|MCP| M3
    A3 <-->|MCP| M4
    
    A1 & A2 & A3 --> I1
    A1 & A2 & A3 --> I2
    A1 & A2 & A3 --> I3
    A1 & A2 & A3 --> I4
```

| 维度 | MCP | A2A | 关系 |
|------|-----|-----|------|
| **层级** | 工具协议 | 协同协议 | 互补 |
| **解决** | Agent ↔ 工具 | Agent ↔ Agent | 各管一摊 |
| **类比** | USB-C | SMTP | 不同层级 |
| **生态** | 1000+ Server | 50+ 厂商 | A2A 早期 |
| **安全** | 自实现 | 4 层内置 | A2A 更成熟 |
| **未来** | 持续增长 | 标准争夺 | 走向融合 |

### 一句心法

**Agent 时代需要自己的 TCP/IP。MCP 是"USB-C"（工具协议），A2A 是"SMTP"（协同协议），两者缺一不可。** 不上协议，Agent 就是孤岛；上了协议，AI 才能从"单机智能"走向"群体智能"。

---

## 延伸阅读

- [当餐厅长出大脑](./01-ai-agent-architecture.md) —— 续集一，AI Agent 7 大模块，第五章多智能体协同是本篇前传
- [Agent Harness](./32-agent-harness.md) —— 续集八，Harness 内的 Tool 设计直接对接 MCP 协议
- [AI 致命三件套](./33-ai-fatal-trio.md) —— 续集九，协议层是三件套的"新攻击面"
- [厨房装监控](./05-observability.md) —— 正传 2，协议层的可观测性与传统 observability 同构
- [AI 评测工程](./34-ai-evaluation.md) —— 续集十，协议层是评测的对象之一
- [从厨师到 CEO](./07-from-chef-to-ceo.md) —— 终章，协议治理是平台工程 IDP 的核心
- [会自我进化的厨房](./29-self-evolving-company.md) —— 续集五，Agent 协议让自进化组织的"自循环"成为可能
- [Codebase 认知债](./31-codebase-cognitive-debt.md) —— 续集七，协议文档化能降低认知债
- [学徒的困境](./11-ai-learning-paradox.md) —— 续集二，协议标准化降低新人学习成本
- [差评危机](./15-incident-response.md) —— 正传 9，协议层事故的应急响应

---

## 结语

阿明花了 3 个月把 20 个 Agent 从"各自为政"重构成"MCP + A2A"架构，效果立竿见影：

```text
重构前：
  - 20 个 Agent × 50 个工具 = 复杂矩阵
  - 加 1 个工具 = 改 10 个 Agent 代码
  - Agent 间通信 4 套协议
  - 安全审计 4 套标准
  - 上线一个新场景：2 周

重构后：
  - 20 个 Agent（统一 MCP Client）
  - 50 个 MCP Server
  - 1 套协议（MCP）+ 1 套协同（A2A）
  - 统一安全模型（OAuth + 审计）
  - 加新工具 = 1 个 MCP Server
  - 上线一个新场景：3 天
```

阿明对团队说：

> "**协议层是 AI 时代的基础设施**。没有 MCP，每个 Agent 都要重造轮子；有了 MCP，加工具就是加积木。没有 A2A，Agent 协同就是私搭乱建；有了 A2A，Agent 协作就是搭乐高。**MCP 和 A2A 加起来，就是 AI 时代的 TCP/IP。**"

下次当你设计 AI 系统时，不妨问自己：

- 我的 Agent 用 MCP 了吗？还是自己写 HTTP 调工具？
- 我的 Agent 间协同用 A2A 了吗？还是写"胶水代码"？
- 我的 MCP Server 是不是"最小权限"？能读取所有数据库的 MCP Server 是灾难
- 我的 Agent Card 是不是"完整"？能力 / 权限 / HITL 规则都写清楚了吗？
- 我的协议层**有 trace 吗**？调用链路能追踪吗？
- 我的协议层**有告警吗**？失败 / 异常 / 攻击能发现吗？
- 我考虑过协议层的**安全陷阱**吗？（间接注入 / 信任传递 / 跨协议外泄）

> 好的协议层设计，不是"加了 MCP / A2A 就完事"，而是"用协议思维重新设计整个 AI 架构"。这是 AI 时代工程化的**新基建**。

← [返回系列导读](./index.md)
