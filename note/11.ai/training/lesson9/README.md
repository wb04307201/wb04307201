# Dify 工作流引擎 · 第九课

⬅️ [返回课程总目录](../README.md)

> **Docker 部署 × Chatflow 搭建 × API 调用** —— 从零开始掌握 Dify 低代码 AI 工作流平台。  
> 本课带你完成 Dify 的部署、智能客服对话流搭建与 API 集成的完整流程。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Dify 工作流引擎 · 第九课 本应该很简单，⬅️ [返回课程总目录](../README.md)

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 学习目标

完成本课程后，你将能够：

- 使用 Docker Compose 部署 Dify 服务
- 理解 Chatflow 和 Workflow 的应用场景差异
- 搭建具备多轮对话记忆的智能客服助手
- 配置 LLM 节点和系统提示词
- 发布应用并通过 REST API 调用
- 实现阻塞模式和流式模式两种调用方式
- 通过 `conversation_id` 管理会话上下文

---

## 章节导航

| 章节 | 文件 | 核心问题 | 建议时长 |
|:----:|:-----|:---------|:--------:|
| **第一章** | [使用 Docker Compose 部署 Dify](./README1.md) | 如何搭建 Dify 运行环境？ | 40 min |
| **第二章** | [Dify 工作流搭建示例教程](./README2.md) | 如何搭建 Workflow 并发布 API？ | 50 min |
| **第三章** | [Dify 对话流搭建示例教程](./README3.md) | 如何搭建 Chatflow 并调用 API？ | 60 min |

---

## 📖 章节详情

### [README1.md](./README1.md) - 使用 Docker Compose 部署 Dify

**内容概要：**
- 部署前的系统要求（硬件和软件）
- Docker Desktop 在 Windows/Mac/Linux 上的安装指南
- 克隆 Dify 源码并启动服务的详细步骤
- 访问和管理员账户设置
- 环境变量自定义配置
- 版本升级注意事项

**关键步骤：**
1. 安装 Docker Desktop
2. 克隆 Dify 仓库
3. 配置环境变量
4. 启动容器服务（5个核心服务 + 6个依赖组件）
5. 访问 `http://localhost/install` 完成初始化

---

### [README2.md](./README2.md) - Dify 工作流搭建示例教程（AI 写作助手）

**内容概要：**
- 从零开始搭建「AI 写作助手」工作流应用
- 工作流（Workflow）类型应用的创建与节点配置
- 应用发布为 API 的完整流程
- API 调用示例与参数说明

---

### [README3.md](./README3.md) - Dify 对话流（Chatflow）搭建示例教程

**内容概要：**
- 从零开始搭建「智能客服助手」Chatflow 应用
- 工作流（Workflow）与 Chatflow 的区别说明
- LLM 节点配置和系统提示词编写
- 知识检索节点集成（可选）
- 应用发布和 API 文档访问
- Chatflow API 调用详解（阻塞模式和流式模式）
- Python 代码示例和多轮对话实现

**核心知识点：**
1. **Chatflow vs Workflow**
   - Chatflow：支持多轮对话记忆，适合客服、助手场景
   - Workflow：单轮自动化任务，无记忆，适合一次性任务

2. **默认画布结构**
   - 开始（用户输入）→ LLM → 直接回复

3. **API 调用端点**
   - Chatflow：`POST /v1/chat-messages`
   - Workflow：`POST /v1/workflows/run`

4. **关键参数**
   - `query`：用户输入内容
   - `conversation_id`：会话 ID，实现多轮对话记忆
   - `response_mode`：`streaming`（流式）或 `blocking`（阻塞）
   - `user`：用户唯一标识

**教程步骤：**
1. 创建空白应用，选择 Chatflow 类型
2. 配置 LLM 节点的系统提示词
3. （可选）添加知识检索节点
4. 预览测试对话功能
5. 发布应用
6. 获取 API Key 并调用接口
7. 通过 `conversation_id` 实现多轮对话

---

## 🖼️ 教程图片资源

本课程的截图位于 `tutorial-images/` 目录，包含：

### Chatflow 相关截图（20张）
- `chatflow-01-create-app.png` - 创建应用
- `chatflow-02-canvas.png` - 默认画布结构
- `chatflow-03-configure-llm.png` - 配置 LLM 提示词
- `chatflow-04-add-knowledge.png` - 添加知识检索节点
- `chatflow-05-full-flow.png` - 完整流程图
- `chatflow-06-preview-panel.png` - 预览面板
- `chatflow-07-conversation-success.png` - 对话测试成功
- `chatflow-08-publishing.png` - 发布状态
- `chatflow-09-api-docs.png` - API 文档页面
- `chatflow-09-publish-status.png` - 发布状态

### 其他教程截图（16张）
- `01-login.png` ~ `16-api-develop-page.png` - 工作流搭建相关截图
- `snapshot-apps.txt` - 应用快照列表

---

## 🔗 相关链接

- [Dify 官方文档](https://docs.dify.ai/)
- [Dify GitHub 仓库](https://github.com/langgenius/dify)
- [Docker 安装指南](https://docs.docker.com/get-docker/)

---

⬅️ 上一课：[AI Agent 设计模式与架构](../lesson8/README.md) | ➡️ 下一课：[Agent 评估方法论](../lesson10/README.md)
