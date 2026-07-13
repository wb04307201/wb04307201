<!--
module:
  parent: ai/04-architecture
  slug: ai/architecture/routing-architecture
  type: article
  category: 主模块子文章
  summary: 分层路由架构：简单问答 Fast Path + 复杂 Agent Path 的统一入口设计
-->

# 分层路由架构：简单问答 + 复杂 Agent 一套架构搞定

← 返回 [架构设计](../README.md)

> 一句话定位：**80% 的用户请求是简单问答，不需要启动 Agent**。分层路由在入口处做复杂度分类，简单请求走 Fast Path（直接 LLM / RAG，< 500ms），复杂请求走 Agent Path（ReAct / Plan-and-Execute，1-30s），失败自动升级/降级——用一套架构覆盖所有复杂度。

---

## 一、为什么需要分层路由？

### 1.1 核心矛盾

| 请求类型 | 占比 | 需要的能力 | 不需要 |
|---------|------|-----------|--------|
| **简单问答** | ~80% | 检索 + 生成 | 工具调用、多步推理 |
| **中等任务** | ~15% | 单步工具调用 | 多 Agent 协作 |
| **复杂任务** | ~5% | 多步推理 + 工具 + 规划 | — |

如果所有请求都走 Agent（ReAct / Multi-Agent）：
- **成本浪费**：Agent 的 token 开销是直接 LLM 的 5-50 倍
- **延迟过高**：Agent 多轮循环 1-30s，简单问题也要等
- **可靠性差**：Agent 链路越长，出错概率越高

如果所有请求都走直接 LLM：
- **能力不足**：复杂任务无法完成（需要工具、多步推理）

### 1.2 解决方案：入口路由 + 双通道

```
用户请求
    │
    ▼
┌─────────────────────────────────────────┐
│  Router（路由决策层）                      │
│  ┌───────────────────────────────────┐  │
│  │  复杂度分类器（3 级递进）            │  │
│  │  Level 1: 规则引擎（0ms）          │  │
│  │  Level 2: 语义路由（10ms）         │  │
│  │  Level 3: 小模型分类（100ms）       │  │
│  └───────────────────────────────────┘  │
└───────┬─────────────────┬───────────────┘
        │                 │
   简单/中等            复杂
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────────┐
│  Fast Path   │  │  Agent Path          │
│              │  │                      │
│  • 直接 LLM  │  │  • ReAct 循环        │
│  • RAG 检索  │  │  • Plan-and-Execute  │
│  • 规则匹配  │  │  • Multi-Agent       │
│              │  │  • DAG 工作流        │
│  延迟 <500ms │  │  延迟 1-30s          │
│  成本 $0.001 │  │  成本 $0.01-0.5      │
└──────┬───────┘  └──────────┬───────────┘
       │                     │
       └──────┬──────────────┘
              ▼
       统一响应 + 可观测性
```

---

## 二、路由决策层：3 级复杂度分类器

### 2.1 Level 1：规则引擎（0ms，零成本）

用正则/关键词快速拦截明确的简单请求：

```python
class RuleClassifier:
    RULES = [
        # 明确的简单问答
        (r"^(什么是|怎么理解|解释一下).{2,20}(？|\?)$", "simple"),
        # 明确的工具调用
        (r"(查天气|查汇率|翻译).+", "tool_call"),
        # 明确的多步任务 → 复杂
        (r"(帮我|请).*(然后|接着|再).*(然后|接着|再)", "complex"),
        # 明确的代码任务
        (r"(写一个|实现|编写).*(函数|类|脚本|代码)", "medium"),
    ]
    
    def classify(self, query: str) -> str | None:
        for pattern, label in self.RULES:
            if re.match(pattern, query):
                return label
        return None  # 无法判断 → 交给下一级
```

**命中率**：~30%（覆盖最明确的请求）
**延迟**：< 1ms

### 2.2 Level 2：语义路由（10ms，近零成本）

用 embedding 相似度匹配预定义的意图类别：

```python
from semantic_router import Route, SemanticRouter

# 预定义路由（embedding 预计算，运行时只做相似度比较）
routes = [
    Route(name="simple_qa", utterances=[
        "什么是机器学习？", "Python 的 GIL 是什么？", "解释 REST API"
    ]),
    Route(name="tool_call", utterances=[
        "北京今天天气怎么样", "100美元等于多少人民币", "翻译这段话"
    ]),
    Route(name="complex_agent", utterances=[
        "帮我分析竞品并写一份报告", "调研市场然后制定营销策略",
        "读取这个 CSV 文件，分析趋势，生成图表"
    ]),
]

router = SemanticRouter(routes=routes)
result = router(query)  # 10ms 内完成
```

**命中率**：~50%（覆盖语义明确的请求）
**延迟**：~10ms（embedding 比较）

### 2.3 Level 3：小模型分类（100ms，低成本）

对前两级无法判断的请求，用小模型做意图分类：

```python
CLASSIFY_PROMPT = """
你是一个查询复杂度分类器。将用户查询分为：
- simple: 简单问答，一次 LLM 调用即可回答
- medium: 需要一次工具调用（搜索/计算/API）
- complex: 需要多步推理、多个工具、或规划

用户查询：{query}

只输出一个词：simple / medium / complex
"""

def level3_classify(query: str) -> str:
    response = small_llm.invoke(CLASSIFY_PROMPT.format(query=query))
    return response.strip()  # small model, ~100ms, $0.0001
```

**命中率**：~20%（覆盖模糊请求）
**延迟**：~100ms

### 2.4 分类器级联总结

| 级别 | 方法 | 延迟 | 命中率 | 累计覆盖 |
|------|------|------|--------|---------|
| L1 | 规则引擎 | < 1ms | 30% | 30% |
| L2 | 语义路由 | ~10ms | 50% | 80% |
| L3 | 小模型分类 | ~100ms | 20% | 100% |

**80% 的请求在 10ms 内完成分类**，只有 20% 需要小模型。

---

## 三、Fast Path：快速通道

```python
class FastPath:
    """简单/中等请求的快速处理通道"""
    
    async def handle(self, query: str, label: str) -> Response:
        if label == "simple":
            # 直接 LLM 生成（或 RAG 检索 + 生成）
            context = await self.rag.retrieve(query, top_k=3)
            return await self.llm.generate(query, context=context)
        
        elif label == "medium":
            # 单次工具调用
            tool = self.tool_selector.select(query)
            result = await tool.execute(query)
            return await self.llm.generate(query, context=result)
        
        elif label == "tool_call":
            # 明确的工具调用（天气/汇率/翻译）
            result = await self.deterministic_tool.execute(query)
            return Response(content=result)
```

**延迟目标**：< 500ms
**成本**：$0.0001-0.001/次

---

## 四、Agent Path：复杂任务通道

```python
class AgentPath:
    """复杂请求的 Agent 处理通道"""
    
    async def handle(self, query: str) -> Response:
        # 根据复杂度选择执行模式
        agent_type = self.select_agent(query)
        
        if agent_type == "react":
            return await self.react_agent.run(query, max_steps=10)
        elif agent_type == "plan_execute":
            return await self.plan_agent.run(query)
        elif agent_type == "multi_agent":
            return await self.multi_agent.run(query)
        elif agent_type == "dag":
            return await self.dag_engine.run(query)
```

> 🔗 **深度阅读**：[Agent 4 大执行模式](../agent-execution-patterns/README.md) — ReAct / Plan-and-Execute / DAG / Multi-Agent 的 6 维对比与选型

---

## 五、升级与降级机制

### 5.1 Fast → Agent 升级

Fast Path 处理失败时，自动升级到 Agent Path：

```python
async def handle_with_escalation(query: str, label: str) -> Response:
    # 先尝试 Fast Path
    response = await fast_path.handle(query, label)
    
    # 质量检查：答案是否靠谱？
    if not quality_checker.is_satisfactory(response, query):
        # 升级到 Agent Path
        logger.info(f"Fast Path 不满意，升级到 Agent: {query[:50]}")
        response = await agent_path.handle(query)
    
    return response
```

**升级触发条件**：
- LLM 输出"我不确定"/"无法回答"
- 质量评分 < 阈值
- 用户反馈不满意（"重新回答"）

### 5.2 Agent → Fast 降级

Agent 超时或出错时，降级到 Fast Path 或兜底响应：

```python
async def handle_with_fallback(query: str) -> Response:
    try:
        # 限时 15 秒
        response = await asyncio.wait_for(
            agent_path.handle(query), timeout=15
        )
        return response
    except asyncio.TimeoutError:
        logger.warning(f"Agent 超时，降级: {query[:50]}")
        # 降级到 Fast Path
        return await fast_path.handle(query, "simple")
    except Exception as e:
        # 最终兜底：友好提示
        return Response(
            content="抱歉，处理您的请求遇到问题，请稍后重试或换个问法。",
            fallback=True
        )
```

> 🔗 **深度阅读**：[成本控制与降级策略](../../03-engineering/llm-production-thinking/02-cost-control-and-degradation.md) — 5 层成本级联（规则→小模型→大模型→SaaS→人工）

---

## 六、可观测性：路由监控 4 指标

| 指标 | 含义 | 健康值 | 告警 |
|------|------|--------|------|
| **路由分布** | simple/medium/complex 比例 | 70/20/10 ± 10% | 复杂比例突增 → 可能路由失效 |
| **分类准确率** | 路由决策是否正确 | > 95% | < 90% → 分类器需要更新 |
| **升级率** | Fast→Agent 的比例 | < 10% | > 20% → Fast Path 能力不足 |
| **降级率** | Agent→Fast 的比例 | < 5% | > 10% → Agent 稳定性问题 |

```python
# Prometheus 指标
router_requests_total = Counter(
    "router_requests_total",
    "Total routing requests",
    ["label", "level"]  # label=simple/medium/complex, level=1/2/3
)

escalation_total = Counter(
    "router_escalation_total",
    "Fast→Agent escalations",
    ["reason"]  # reason=quality/timeout/error
)
```

---

## 七、5 大反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **所有请求都走 Agent** | 80% 简单请求浪费 5-50x token | 入口路由分流 |
| **分类器只有一个** | 规则覆盖不全，小模型太慢 | 3 级递进（规则→语义→模型） |
| **没有升级机制** | Fast Path 回答不好就结束 | 质量检查 + 自动升级 |
| **没有超时控制** | Agent 无限循环 | 限时 + 降级兜底 |
| **不监控路由分布** | 路由失效不知道 | 4 指标 + 告警 |

---

## 八、与现有架构的关系

```
本文（routing-architecture）= 入口层
    │
    ├── Fast Path → 直接 LLM / RAG
    │
    └── Agent Path → agent-execution-patterns（4 大执行模式）
                    → cost-control（5 层成本级联）
                    → agent-memory（记忆管理）
                    → agent-context（上下文工程）
```

本文是**入口路由层**，解决"请求走哪条路"的问题。具体走 Agent 后用什么执行模式、怎么管理记忆和上下文，由已有文章覆盖。

---

## 九、交叉引用

- [Agent 4 大执行模式](../agent-execution-patterns/README.md) — ReAct / Plan-and-Execute / DAG / Multi-Agent 选型
- [成本控制与降级](../../03-engineering/llm-production-thinking/02-cost-control-and-degradation.md) — 5 层成本级联（规则→小模型→大模型→SaaS→人工）
- [Agent 记忆管理](../agent-memory/README.md) — Agent Path 的上下文与记忆
- [Agent 上下文工程](../agent-context/README.md) — Agent Path 的 context 构建
- [Function Calling](../../02-technology-stack/function-calling/README.md) — Fast Path 单次工具调用
- [结构化输出](../../02-technology-stack/structured-output/README.md) — 分类器的 JSON 输出保障
- 主模块：[`11.ai`](../../README.md) — AI 知识体系

---

## 📚 参考来源

- [Router-Based Agents: The Architecture Pattern That Makes AI Systems Scale](https://pub.towardsai.net/router-based-agents-the-architecture-pattern-that-makes-ai-systems-scale-a9cbe3148482) — 路由架构模式综述（2025.12）
- [vLLM Semantic Router](https://vllm.ai/blog/2025-09-11-semantic-router) — 语义路由在推理引擎中的应用（2025.09）
- [AI Agent Model Routing and Dynamic Model Selection](https://zylos.ai/research/2026-03-02-ai-agent-model-routing/) — 模型路由策略分类（2026.03）
- [Model and Agent Orchestration for Adaptive Inference](https://arxiv.org/html/2509.07571v1) — LLM + Agent 联合路由模型（2025.09）
- [Choosing the Right Multi-Agent Architecture — LangChain](https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture) — 多 Agent 架构选型（2026.01）

← [返回 架构设计](../README.md)
