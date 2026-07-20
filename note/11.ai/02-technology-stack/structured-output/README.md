<!--
module:
  parent: ai
  slug: ai/structured-output
  type: article
  category: 主模块子文章
  summary: 大模型结构化输出（JSON）：5 种稳定性策略 + 框架对比 + 工程反模式
-->

# 大模型稳定输出 JSON：5 种策略 + 框架对比

← 返回 [技术栈](../README.md)

> 一句话定位：让 LLM 稳定输出合法 JSON 不是"prompt 里写一句'输出 JSON'"就够的——需要 **response_format 参数 + JSON Schema 约束 + Function Calling + 解析重试 + constrained decoding** 五层工程策略的组合。

---

## 一、为什么"输出 JSON"这么难？

LLM 本质是**自回归文本生成**——逐 token 预测下一个最可能的 token。它不理解 JSON 语法，只"见过"大量 JSON 文本。这导致：

| 问题 | 原因 |
|------|------|
| 格式不合法 | 漏了闭合括号、多了逗号、字符串没加引号 |
| 字段缺失 | 模型"觉得"某些字段不重要就省略了 |
| 类型错误 | 期望数字却输出了字符串 |
| 额外文本 | JSON 外面包了 ```json``` 或"这是结果：" |
| 嵌套错误 | 数组/对象嵌套层级不对 |

**核心矛盾**：LLM 是概率模型，JSON 是确定性格式。要让概率模型稳定输出确定性格式，需要**外部约束**。

---

## 二、5 种稳定性策略

### 策略 1：response_format 参数（API 层面，首选）

OpenAI / Claude / 通义千问等主流 API 都支持 `response_format` 参数，在 API 层面约束输出格式。

```python
# OpenAI：强制 JSON 模式
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "列出 3 个编程语言"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "languages",
            "schema": {
                "type": "object",
                "properties": {
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "year": {"type": "integer"}
                            },
                            "required": ["name", "year"]
                        }
                    }
                },
                "required": ["languages"]
            }
        }
    }
)
# 输出 100% 符合 JSON Schema，无需解析重试
```

**优点**：零额外代码、100% 合法 JSON、模型层面保证。
**缺点**：需要模型支持、复杂 Schema 可能降低生成速度。

### 策略 2：Function Calling / Tool Use

利用 Function Calling 的结构化输出能力——即使不需要"调用工具"，也可以把期望的 JSON 格式定义为一个"工具"。

```python
# 把 JSON 格式伪装成一个"工具"
tools = [{
    "type": "function",
    "function": {
        "name": "extract_data",
        "description": "从用户输入中提取结构化数据",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age", "email"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "张三，25 岁，zhang@example.com"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "extract_data"}}
)
# tool_calls[0].function.arguments → 100% 合法的 JSON 字符串
```

**优点**：利用 Function Calling 的 Schema 约束、支持所有主流模型。
**缺点**：语义上"滥用"了 FC（不是为了调工具，而是为了格式约束）。

> 🔗 深度阅读：[Function Calling 原理](../function-calling/README.md) — 完整的工具调用机制

### 策略 3：Prompt 指令 + 格式约束

在 prompt 中明确指定 JSON 格式要求，给出示例。

```python
prompt = """
请从以下文本中提取人物信息，严格按 JSON 格式输出。
不要输出任何其他文字，不要使用 markdown 代码块。

输出格式：
{
    "name": "姓名",
    "age": 数字,
    "email": "邮箱"
}

文本：张三，25 岁，zhang@example.com
"""
```

**优点**：无需 API 支持、灵活。
**缺点**：不可靠（~90% 成功率），仍需解析重试。

### 策略 4：解析 + 重试（工程兜底）

不管用什么策略，都要有解析失败的兜底机制。

```python
import json
import re

def robust_json_parse(llm_output: str, max_retries: int = 3) -> dict:
    """健壮的 JSON 解析器：自动修复常见问题"""
    
    for attempt in range(max_retries):
        try:
            # 尝试 1：直接解析
            return json.loads(llm_output)
        except json.JSONDecodeError:
            pass
        
        try:
            # 尝试 2：提取 ```json``` 代码块
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', llm_output)
            if match:
                return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
        
        try:
            # 尝试 3：提取第一个 { 到最后一个 }
            start = llm_output.index('{')
            end = llm_output.rindex('}') + 1
            return json.loads(llm_output[start:end])
        except (ValueError, json.JSONDecodeError):
            pass
        
        # 重试：让模型修复格式
        if attempt < max_retries - 1:
            llm_output = ask_llm_to_fix_json(llm_output)
    
    raise ValueError(f"JSON 解析失败，已重试 {max_retries} 次")
```

### 策略 5：Constrained Decoding（受限解码）

在模型推理层面，强制每个 token 只生成符合 JSON Schema 的输出。**100% 保证合法 JSON**。

```python
# Outlines 框架（开源）
import outlines

model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")

# 用 Pydantic 模型定义 JSON Schema
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    email: str

generator = outlines.generate.json(model, Person)
result = generator("提取人物信息：张三，25 岁，zhang@example.com")
# result → Person(name="张三", age=25, email="zhang@example.com")
# 100% 符合 Schema，不可能生成非法 JSON
```

**优点**：100% 合法、无需重试、支持自部署模型。
**缺点**：只能用于自部署模型（API 不支持）、可能降低生成速度。

---

## 三、策略选型决策树

```text
你的场景？
├─ 使用商业 API（OpenAI / Claude / 通义）
│   ├─ 需要严格 Schema → response_format（首选）
│   └─ 模型不支持 response_format → Function Calling + 解析重试
│
├─ 自部署模型（vLLM / Ollama）
│   ├─ 需要 100% 合法 → Constrained Decoding（Outlines / Guidance）
│   └─ 不需要严格保证 → Prompt 指令 + 解析重试
│
└─ 任何场景
    └─ 必须有 → 解析重试兜底（策略 4）
```

---

## 四、框架对比

| 框架 | 原理 | 支持模型 | 100% 合法 | 适用 |
|------|------|---------|----------|------|
| **Instructor** | 包装 API + Pydantic 校验 + 自动重试 | OpenAI / Claude / 通义 | ❌（重试保证） | 商业 API 首选 |
| **Outlines** | Constrained Decoding（token 级约束） | 自部署（transformers） | ✅ | 自部署首选 |
| **Guidance** | 模板化生成 + 约束 | 自部署 | ✅ | 复杂模板 |
| **LangChain OutputParser** | Prompt 约束 + 解析重试 | 所有 | ❌ | LangChain 生态 |
| **原生 response_format** | API 层面约束 | OpenAI / Claude | ✅ | 最简单 |

```python
# Instructor 用法（最简洁的商业 API 方案）
import instructor
from pydantic import BaseModel
from openai import OpenAI

class UserInfo(BaseModel):
    name: str
    age: int
    email: str

client = instructor.from_openai(OpenAI())
result = client.chat.completions.create(
    model="gpt-4o",
    response_model=UserInfo,  # Pydantic 模型自动转 JSON Schema
    messages=[{"role": "user", "content": "张三，25 岁，zhang@example.com"}]
)
# result → UserInfo(name="张三", age=25, email="zhang@example.com")
# Instructor 自动处理：Schema 注入 + 解析 + 重试
```

---

## 五、5 大反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **只靠 prompt 约束** | 成功率 ~90%，生产不够 | response_format 或 FC + 解析重试 |
| **不做解析重试** | 格式失败直接报错 | 至少 3 次重试 + 自动修复 |
| **不用 JSON Schema** | 字段缺失/类型错误无法检测 | 定义 Pydantic/JSON Schema 校验 |
| **忽略 extra text** | 模型输出 ```json...``` 或前缀文字 | 解析器自动提取 JSON 块 |
| **自部署模型不做 constrained decoding** | 浪费 100% 合法的机会 | 用 Outlines 或 Guidance |

---

## 六、交叉引用

- [Function Calling / Tool Use](../function-calling/README.md) — 工具调用机制（策略 2 的基础）
- [Prompt Engineering](../prompt-engineering/README.md) — 提示词工程（策略 3 的基础）
- [Context Engineering](../context-engineering/README.md) — 上下文工程
- [LLM 幻觉](../../../13.split-hairs/11.ai/hallucination/README.md) — 输出不可靠的另一面
- 主模块：[`11.ai`](../../README.md) — AI 知识体系

---

← [返回 技术栈](../README.md)
