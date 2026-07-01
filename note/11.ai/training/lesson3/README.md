<!--
module:
  parent: ai
  slug: ai/lesson-03
  type: article
  category: 主模块子文章
  summary: 第 3 课 Spring AI Agent
-->

# 第 3 课：Spring AI Agent 搭建

> 从零开始，用 Spring AI 搭建一个具备对话能力和 MCP 工具调用的 AI Agent。

---
## 引言：变更说明

第 3 课：Spring AI Agent 搭建 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 学习目标

学完本课后，你将能够：

- 使用 Spring Boot + Spring AI 创建一个基础的 AI 对话应用
- 集成百炼平台的通义千问模型
- 配置和使用 MCP 工具，让 Agent 能调用外部系统
- 理解 SSE 流式输出的实现原理
- 开发自己的 MCP Server 并集成到 Agent 中

## 前置条件

- 前置课程：[第 1 课：AI Agent 核心概念](../lesson1/README.md)
- 环境准备：JDK 17+、Maven 3.8+、IDE（推荐 IntelliJ IDEA）
- 百炼平台 API Key

## 章节导航

| 章节 | 文件 | 核心问题 | 建议时长 |
|:----:|:-----|:---------|:--------:|
| 第一章 | [Spring AI 从零搭建](README1.md) | 如何创建一个能与大模型对话的 Spring 应用？ | 60 min |
| 第二章 | [添加 MCP 集成](README2.md) | 如何让 Agent 通过 MCP 连接外部工具？ | 45 min |

### 阅读建议

- **第一章** 包含 13 个递进步骤，从创建项目到 RAG 集成，建议按顺序完成
- **第二章** 在第一章基础上添加 MCP 能力，重点理解 MCP 的配置和调用方式

---

> 🚀 从 [第一章：Spring AI 从零搭建](README1.md) 开始 | ⬅️ [返回课程总目录](../README.md)

---

⬅️ 上一课：[Agent Harness 与控制论](../lesson2/README.md) | ➡️ 下一课：[Java MCP 服务开发](../lesson4/README.md)
