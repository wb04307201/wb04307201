# 35a · MCP 协议（续集十一 · 上）

> 从阿明的 20 个 Agent 各自为政，到全栈打通 —— 看 AI 时代的"TCP/IP"：**MCP 协议**

> **系列定位**：本篇是「阿明餐厅」系列的**续集十一（上）**。在[续集一 · 《当餐厅长出大脑》](./01-ai-agent-architecture.md)第五章，我们讲了多智能体协同（Orchestrator + 消息总线）。在[续集八 · 《Agent Harness》](./32-agent-harness.md)第三章，我们讲了 Tool 设计。但都还是"自己设计、自己实现"。2024-2026 年，业界出现了**两个重量级协议标准** —— **MCP（Model Context Protocol，Anthropic 主导）** 和 **A2A（Agent-to-Agent，Google 主导）** —— 它们正在成为 AI 时代的"TCP/IP"，让 Agent 与 Agent、Agent 与工具之间有了**统一的"语言"**。本篇（上）专门讲 **MCP —— Agent ↔ 工具的"USB-C"**；下篇[35b](./35b-a2a-protocol.md)专门讲 **A2A + 协议治理**。

> **兄弟篇**：35b · A2A 协议 + 协议治理（[← 点击阅读](./35b-a2a-protocol.md)）

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

**本篇（上）** 聚焦 **MCP** —— Agent 调用工具的"USB-C"。**下篇[35b](./35b-a2a-protocol.md)** 聚焦 **A2A + 协议治理**（安全 / 可观测 / 趋势）。

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
    db.execute("UPDATE orders SET address = ?", new_address, order_id)
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

→ **A2A 协议** 解决这些问题（见[35b 第二章](./35b-a2a-protocol.md#第二章a2a-是什么--agent-协同的邮件协议)）

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

## 第二章：MCP vs A2A vs 自研 —— 怎么选

很多团队面对 MCP / A2A / 自研不知道选哪个。阿明总结了一个**3 维选型矩阵**。

### 2.1 选型矩阵

| 维度 | MCP | A2A | 自研 |
|------|-----|-----|------|
| **解决什么** | Agent ↔ 工具 | Agent ↔ Agent | 完全自控 |
| **生态成熟度** | 高（2026 标准） | 中（2026 早期） | N/A |
| **学习成本** | 低 | 中 | 高 |
| **定制能力** | 中（受协议约束） | 中 | 高 |
| **安全模型** | 需自实现 | 内置 4 层 | 完全自控 |
| **跨厂商** | 是 | 是 | 否 |

### 2.2 决策树

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

### 2.3 阿明的选型结论

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

### 2.4 实施路线图

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

## 第三章：协议层的 6 大设计原则

无论选 MCP / A2A / 自研，**协议本身的设计原则**是相通的。阿明总结了 6 大原则。

### 3.1 原则 1：能力可发现

```text
好协议：
  Agent 启动时自动知道"周围有什么能力可用"
  → MCP 的 list_tools / A2A 的 Agent Card

差协议：
  Agent 必须事先知道"有什么工具"
  → 文档散落，版本不一致
```

### 3.2 原则 2：调用可追溯

```text
好协议：
  每次调用都有 trace_id
  → 跨 Agent / 跨工具的全链路追踪

差协议：
  调用是黑盒
  → 出问题不知道哪个环节错了
```

### 3.3 原则 3：失败可重试

```text
好协议：
  协议层内置 idempotency_key
  → 失败可重试，不重复执行

差协议：
  失败 = 重头来
  → 邮件发了 3 次 / 钱扣了 3 次
```

### 3.4 原则 4：安全可审计

```text
好协议：
  协议层内置 authn / authz / audit log
  → 谁调了什么 / 改了什么都可查

差协议：
  安全靠"内网" / 靠"约定俗成"
  → 审计缺失
```

### 3.5 原则 5：能力可扩展

```text
好协议：
  协议版本向后兼容
  → 老 Client 调新 Server 不挂

差协议：
  协议一变，所有调用方都要改
```

### 3.6 原则 6：成本可计量

```text
好协议：
  协议层记录 token / 时间 / 算力消耗
  → 不同 Agent 的成本可分摊

差协议：
  成本是黑盒
  → 不知道谁花了多少
```

---

## 第四章：MCP 落地实践

阿明把 MCP 用在了 5 个最常见的场景，本章展开。

### 4.1 场景 1：MCP 接入数据库

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

### 4.2 场景 2：MCP 接入内部业务系统

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

### 4.3 场景 3：MCP + 多模态

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

### 4.4 场景 4：MCP + RAG

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

### 4.5 场景 5：MCP + 浏览器自动化

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

## 核心总结（上篇）：MCP 协议全景

```mermaid
graph TB
    subgraph "应用层"
        App[Agent / Orchestrator]
    end

    subgraph "MCP Client"
        C[MCP Client<br/>自动发现 + 调用]
    end

    subgraph "MCP Servers (工具集)"
        S1[数据库 MCP Server]
        S2[业务 API MCP Server]
        S3[文件 MCP Server]
        S4[外部服务 MCP Server]
        S5[浏览器 MCP Server]
    end

    App <--> C
    C <-->|JSON-RPC| S1
    C <-->|JSON-RPC| S2
    C <-->|JSON-RPC| S3
    C <-->|JSON-RPC| S4
    C <-->|JSON-RPC| S5
```

| 维度 | 核心问题 | 关键能力 |
|------|----------|----------|
| **架构** | 怎么连？ | Client + Server + JSON-RPC |
| **能力** | 能做什么？ | Resources + Tools + Prompts |
| **复杂度** | 加工具要改 Agent 吗？ | N×M → N+M |
| **可发现** | Agent 怎么知道有什么工具？ | 启动时自动 list_tools |
| **上下文** | 跨调用怎么传上下文？ | Sampling + Roots |
| **生态** | 有现成实现吗？ | 1000+ MCP Server（2026） |
| **局限** | 不能解决什么？ | Agent ↔ Agent 协同 → 用 A2A |

### 上篇心法

**MCP 是 Agent 时代的 USB-C —— 让 Agent ↔ 工具的接入从"N×M 复杂度"降到"N+M"。** 接入 MCP 的最大收益不是"省了开发"，是"加新工具 = 加积木"的可组合性。

下一步阅读[35b · A2A 协议 + 协议治理](./35b-a2a-protocol.md)—— 工具层有 MCP，协同层用什么？安全 / 可观测 / 趋势怎么看？

---

## 延伸阅读

- [35b · A2A 协议 + 协议治理（下篇）](./35b-a2a-protocol.md) —— A2A 协议 + 5 大安全陷阱 + 可观测性 + 5 大趋势
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

## 跨章节衔接

- [11.ai/03-engineering/ai-platforms/README.md](../11.ai/03-engineering/ai-platforms/README.md) —— Dify/Coze/LangGraph 平台实现 —— MCP/A2A 协议在主流平台中的落地
- [11.ai/02-technology-stack/README.md](../11.ai/02-technology-stack/README.md) —— AI 技术栈 61 概念 —— 协议层在 AI 技术栈中的位置

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

重构后（仅 MCP 部分）：
  - 20 个 Agent（统一 MCP Client）
  - 50 个 MCP Server
  - 1 套协议（MCP）
  - 加新工具 = 1 个 MCP Server
  - 上线一个新场景：3 天
```

阿明对团队说：

> "**MCP 是 AI 时代的基础设施**。没有 MCP，每个 Agent 都要重造轮子；有了 MCP，加工具就是加积木。MCP 让 Agent ↔ 工具的接入有了标准，让 AI 应用从'私搭乱建'走向'搭乐高'。"

下次当你设计 AI 系统时，不妨问自己：

- 我的 Agent 用 MCP 了吗？还是自己写 HTTP 调工具？
- 我的 MCP Server 是不是"最小权限"？能读取所有数据库的 MCP Server 是灾难
- 我的协议层**有 trace 吗**？MCP 调用链路能追踪吗？
- 我的 MCP Server 注册了**必要的工具**吗？还是把所有工具都暴露了？

> 好的 MCP 接入，不是"加了 MCP Server 就完事"，而是"用协议思维重新设计工具层"。这是 AI 时代工程化的**新基建**。

← [返回系列导读](./index.md) | [下篇：35b A2A + 治理 →](./35b-a2a-protocol.md)