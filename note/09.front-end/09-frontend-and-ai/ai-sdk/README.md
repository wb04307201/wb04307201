# AI SDK 集成

> 一句话定位：**Vercel AI SDK / Anthropic SDK / OpenAI SDK —— 前端集成大模型的事实标准**

2024-2026 是前端集成 AI 能力的爆发期。Vercel AI SDK 以"统一接口 + 流式渲染 + React 深度集成"成为前端首选。

---
## 引言：反直觉代码

AI SDK 集成 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 1. AI SDK 选型对比

| SDK | 优势 | 适用 | 2026 状态 |
|-----|------|------|----------|
| **Vercel AI SDK** | 多模型统一接口 / 流式 SSR / React hooks | Next.js 项目首选 | ⭐⭐⭐⭐⭐ 主流 |
| **Anthropic SDK** | Claude 官方 SDK | Claude 专用 | ⭐⭐⭐⭐ |
| **OpenAI SDK** | 官方 SDK | OpenAI 专用 | ⭐⭐⭐⭐ |
| **LangChain.js** | Agent / RAG / 链式调用 | 复杂工作流 | ⭐⭐⭐ 抽象重 |

---

## 2. Vercel AI SDK 核心能力

### 2.1 多模型统一接口

```typescript
import { generateText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { openai } from '@ai-sdk/openai'

// Anthropic Claude
const { text } = await generateText({
  model: anthropic('claude-sonnet-4-20250514'),
  prompt: 'Hello',
})

// OpenAI GPT
const { text } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Hello',
})

// 同一套 API，切换模型零成本
```

### 2.2 流式响应（Streaming）

```typescript
// Next.js Route Handler
import { streamText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'

export async function POST(req: Request) {
  const { messages } = await req.json()
  
  const result = streamText({
    model: anthropic('claude-sonnet-4-20250514'),
    messages,
  })
  
  return result.toDataStreamResponse()
}
```

### 2.3 React Hook：useChat

```tsx
'use client'
import { useChat } from 'ai/react'

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  })
  
  return (
    <div>
      {messages.map(m => (
        <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} disabled={isLoading} />
        <button type="submit" disabled={isLoading}>Send</button>
      </form>
    </div>
  )
}
```

### 2.4 Function Calling / Tool Use

```typescript
import { generateText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { z } from 'zod'

const result = await generateText({
  model: anthropic('claude-sonnet-4-20250514'),
  prompt: 'What is the weather in Tokyo?',
  tools: {
    weather: {
      description: 'Get weather for a location',
      parameters: z.object({
        location: z.string(),
      }),
      execute: async ({ location }) => {
        // 实际调用天气 API
        return { temp: 22, condition: 'sunny' }
      },
    },
  },
  maxSteps: 3,  // 允许多步工具调用
})

console.log(result.text)
```

---

## 3. AI Native UI 模式

| 模式 | 实现 | 适用 |
|------|------|------|
| **流式渲染** | `useChat()` + SSE | 实时对话 |
| **思维链展示** | `<think>` 标签解析 | 增强信任 |
| **Function Calling UI** | Tool 调用状态机 | 工具调用可视化 |
| **AI 风险提示** | "AI 生成"标识 + 引用源 | 信任校准 |
| **反馈接口** | 👍/ 👎 / 重新生成 | Eval 数据采集 |

```tsx
// 思维链展示
function Message({ content }: { content: string }) {
  const match = content.match(/<think>>([\s\S]*?)<\/think>/)
  
  return (
    <div>
      {match && (
        <details>
          <summary>Thinking...</summary>
          <p>{match[1]}</p>
        </details>
      )}
      <p>{content.replace(/<think>>[\s\S]*?<\/think>/, '')}</p>
    </div>
  )
}
```

---

## 4. 结构化输出（Structured Output）

```typescript
import { generateObject } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { z } from 'zod'

const { object } = await generateObject({
  model: anthropic('claude-sonnet-4-20250514'),
  schema: z.object({
    name: z.string(),
    age: z.number(),
    email: z.string().email(),
  }),
  prompt: 'Extract user info: John Doe, 30, john@example.com',
})

// object 已经是类型安全的 JavaScript 对象
console.log(object.name)  // "John Doe"
```

---

## 5. RAG（检索增强生成）

```typescript
import { generateText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'

// 1. 检索相关文档
const docs = await vectorDB.search(userQuery, { topK: 5 })

// 2. 拼接 context
const context = docs.map(d => d.text).join('\n\n')

// 3. 生成回答
const { text } = await generateText({
  model: anthropic('claude-sonnet-4-20250514'),
  system: 'Answer based on the provided context.',
  prompt: `Context:\n${context}\n\nQuestion: ${userQuery}`,
})
```

---

## 6. 安全与成本

| 关注点 | 实践 |
|--------|------|
| **API Key 保护** | 永远放服务端，不在客户端暴露 |
| **Token 限制** | 输入 / 输出限制，防止超长对话 |
| **成本监控** | 跟踪 token 使用，设置告警 |
| **内容过滤** | 敏感内容检测（AI SDK 支持 Moderation API） |
| **速率限制** | 后端限流，防止滥用 |

---

## 7. 学习路径

1. **入门**（3 天）：跑通 `useChat()` 流式对话 Demo
2. **进阶**（1 周）：Function Calling + 多模型切换
3. **高级**（持续）：RAG 集成 + AI Native UI + Eval 体系

## 8. 交叉引用

- [`09-frontend-and-ai/`](../) — 前端与 AI 总览
- [`09-frontend-and-ai/vibe-coding/`](../vibe-coding/) — AI 辅助开发
- [`11.ai/01-fundamentals/llm-basics/`](../../../11.ai/01-fundamentals/llm-basics/README.md/) — LLM 基础
