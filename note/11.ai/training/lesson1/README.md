<!--
module:
  parent: ai
  slug: ai/lesson-01
  type: article
  category: 主模块子文章
  summary: 第 1 课 AI Agent 核心概念
-->

# 第 1 课：AI Agent 核心概念

⬅️ [返回课程总目录](../README.md)

> **大模型 × 提示词 × 知识库 × 工具** —— 四大核心能力构建 AI Agent 的技术底座。  
> 本课从概念到实战，带你理解 AI Agent 的架构哲学，并动手连接真实外部系统。

---
## 引言：变更说明

第 1 课：AI Agent 核心概念 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 学习目标

学完本课后，你将能够：

- 理解 AI Agent 的核心架构：**LLM + Context Engineering 二分模型**，Context 包含短期记忆、长期记忆、工具与流程三大子模块
- 区分 **Context Engineering 与 Prompt Engineering** 的边界，理解从 Prompt 到 Context 的演变路径
- 掌握 LLM 的推理范式（ReAct / Plan-and-Execute / CoT），理解推理方式与上下文输入的分工
- 理解 RAG（检索增强生成）的原理与短期记忆、长期记忆的协同，用知识库补齐大模型的知识盲区
- 通过 MCP 协议连接外部系统（stdio / HTTP-SSE，本地 / 远程），让 AI 真正"做事"而不只是"说话"
- 区分 MCP（能做什么）与 Skill（怎么做）的边界，理解陈述性记忆与程序性知识的差异

---

## 前置准备

- **Demo 项目**：基于 [spring-ai-chat](https://gitee.com/wb04307201/spring-ai-chat) 搭建  
  ⚠️ 需先在本地启动 demo 项目，再访问 [演示地址](http://localhost:8080/spring/ai/chat)
- **知识库面板**：[Qdrant Dashboard](http://localhost:6333/dashboard)（需先启动 Qdrant）

---

## 章节导航

| 章节 | 文件 | 核心问题 | 建议时长 |
|:----:|:-----|:---------|:--------:|
| **第一章** | [大模型基础能力与概念](README1.md) | AI Agent 由哪些组件构成？它们如何协作？ | 60 min |
| **第二章** | [智医同源："君臣佐使"配伍之道](README2.md) | 四大组件各自的定位是什么？缺了谁会怎样？ | 20 min |
| **第三章** | [MCP 生产实践](README3.md) | 如何将 MCP Server 做到生产级质量？ | 40 min |

### 推荐阅读顺序

```
第一章（概念 + 动手）  →  第二章（思维模型）  →  第三章（生产实战）
    ↑                        ↑                       ↑
 先跑通 demo              建立系统观               深入 MCP 设计模式
 理解四大组件             "君臣佐使"配伍哲学        五大模式 + 上下文优化
```

- **时间紧张**：先读第一章的核心架构图 + 第二章全文（约 30 分钟），建立全局认知
- **动手优先**：从第一章的 demo 演示开始，边跑边读
- **深度研究**：三章通读，重点关注第三章的五大设计模式

---

## AI Agent 核心技术架构

```mermaid
flowchart TB
    subgraph Agent["🤖 AI Agent"]
        direction TB

        subgraph LLM["🧠 LLM（大脑）"]
            L1["模型选型 / 推理能力 / 推理范式<br/>ReAct · Plan-and-Execute · CoT"]
        end

        subgraph Context["📦 Context Engineering（输入工程）"]
            direction TB
            C1["演变<br/>Prompt → Context"]
            C2["短期记忆<br/>会话上下文"]
            C3["长期记忆<br/>RAG · Mem0"]
            C4["工具与流程<br/>MCP · Skill"]
        end

        LLM <-->|"输入 / 输出"| Context
    end

    style LLM fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Context fill:#fff3e0,stroke:#f57c00,stroke-width:3px
```

> 详细架构图见 [第一章](README1.md#一agent-总览llm--context-二分模型)

**一句话总结**：**AI Agent = LLM × Context Engineering**——大模型是大脑，决定 AI Agent 的上限；Context Engineering 决定 AI Agent 的下限。

---

## 本课的知识地图

```mermaid
graph LR
    A["第一章<br/>LLM + Context 概念"] --> B["第二章<br/>君臣佐使思维模型"]
    B --> C["第三章<br/>MCP 生产实践"]

    A --- A1["🧠 LLM<br/>模型选型 · 推理范式"]
    A --- A2["📦 Context 演变<br/>Prompt → Context Engineering"]
    A --- A3["💬 短期记忆<br/>会话上下文"]
    A --- A4["📚 长期记忆<br/>RAG · Mem0"]
    A --- A5["🔧 工具与流程<br/>MCP · Skill"]

    B --- B1["👑 君药 = LLM"]
    B --- B2["💊 臣药 = Context Engineering"]
    B --- B3["🌿 佐药 = 知识库 + 长期记忆"]
    B --- B4["🚀 使药 = MCP + Skill"]

    C --- C1["🏗️ 五大设计模式"]
    C --- C2["⚡ 上下文优化"]
    C --- C3["🧩 MCP + Skills 协同"]
```

---

## 补充资料

| 资料 | 说明 |
|:-----|:-----|
| [百度网盘 Skill 示例](SKILL.md) | 一个完整的 Skill 定义文件，展示 Skills 的核心要素 |
| [启明11 手机介绍](qiming11.md) | RAG 演示用的知识库文档 |
| [demo 项目](demo/) | Spring AI Chat 演示项目源码 |

---

> 🚀 **准备好了吗？** 从 [第一章：大模型基础能力与概念](README1.md) 开始。

---

➡️ [下一课：Agent Harness 与控制论](../lesson2/README.md)
