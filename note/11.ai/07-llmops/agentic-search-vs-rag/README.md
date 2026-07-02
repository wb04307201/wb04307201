<!--
module:
  parent: ai
  slug: ai/agentic-search-vs-rag
  type: article
  category: 主模块子文章
  summary: Agentic Search 取代 RAG 的反直觉革命：实时 + 跟随引用 + Harness > 索引
-->

# Agentic Search vs RAG —— AI Coding 检索范式的根本转变

← 返回 [LLMOps](../README.md)

> 2025 年 AI Coding 领域最大的范式转变：Claude Code 等主流工具**主动放弃 RAG**，改用 Agentic Search。本文从工程问题、检索范式、Harness 设计、场景边界 4 个层面系统讲清楚。

> **面试场景**：这是反直觉的高频 AI 面试题——很多人以为 RAG 是 AI Coding 标配，但 Claude Code 官方明确否定。面试版（30/60/90 秒话术）见 [咬文嚼字·11.ai/claude-code-agentic-search](../../../13.split-hairs/11.ai/claude-code-agentic-search/README.md)。

---

## 一、RAG 的设计哲学（先回顾）

### 1.1 RAG 工作流

```
文档语料 → 切分 → 嵌入 → 存入向量库 → 查询时向量检索 → 注入 Prompt → LLM 生成
```

### 1.2 RAG 的 3 大假设

1. **文档更新频率低**（FAQ / 知识库 / 产品文档）
2. **检索粒度 = 语义相似**（找相似的内容即可）
3. **中心化索引可接受**（共享同一份索引）

### 1.3 RAG 的最佳场景

- ✅ 文档问答（客服 / Help Center）
- ✅ 政策 / 法律 / 合规检索
- ✅ 个人知识库（Obsidian / Notion AI）
- ✅ 低频更新的产品手册

## 二、RAG 在 AI Coding 上的 3 大工程问题

### 2.1 索引滞后（Index Staleness）—— 最致命

```python
# 简化示意
class RAGPipeline:
    def sync_index(self):
        # 嵌入管道：定时同步代码 → 向量库
        # 通常 1-24 小时延迟
        pass

# 问题场景
# T=09:00: 工程师修改 auth.py
# T=09:05: 工程师问 AI "auth 改了什么？"
# T=09:05: AI 检索 RAG 索引 → 返回的是 T=09:00 之前的内容
# T=09:05: AI 给错误答案
```

**实际数据**（Anthropic 官方）：
> "嵌入管道跟不上活跃的工程团队，导致索引反映的是数周甚至数天前的代码状态。"

### 2.2 粒度错配（Granularity Mismatch）

向量检索返回"语义相似"的代码片段。但工程师实际需要的是：

```
工程师需要："auth.py 第 50 行的函数怎么用？"

RAG 返回：所有包含 "auth" 关键词的代码片段（语义相似，但工程不相关）
Agentic Search 返回：
  - auth.py 第 50 行的定义
  - 调用方（callers）
  - 测试用例
  - 文档注释
```

### 2.3 维护成本（Pipeline Cost）

RAG 在代码库上的持续成本：

| 组件 | 成本 |
|------|------|
| 嵌入管道 | 定时任务 / 监听 git push / CI 触发 |
| 向量数据库 | 百万行代码 → GB 级向量存储 |
| 监控 | 管道挂了没人知道 → 索引悄悄过期 |
| 增量更新 | 处理代码 diff / chunk 边界 |
| 权限过滤 | 不同开发者看不同分支 |

**这是持续的、隐藏的、巨大的运维成本**。

## 三、Agentic Search 的设计哲学

### 3.1 Agentic Search 工作流

```
Agent 接收任务 → 循环：
  ├─ 调用 grep / read / glob / LSP 等工具
  ├─ 分析工具返回结果
  ├─ 决定下一步搜索方向（跟随引用 / 跨文件 / 缩小范围）
  └─ 直到找到答案

→ 直接基于实时代码库回答（无索引滞后）
```

### 3.2 Agentic Search 的 3 大优势

**优势 1：实时（Zero Latency）**

- 无嵌入管道 → 无滞后
- 直接读本地文件
- 工程师 commit 后立即可见

**优势 2：跟随引用（Reference Following）**

```python
# Agentic Search 能做的：
# 找到函数定义 → 跟到调用方 → 跟到测试用例 → 形成完整调用链
def search_call_chain(function_name):
    # 1. grep 函数定义
    definitions = grep(f"def {function_name}")
    # 2. 对每个定义，grep 调用方
    callers = grep(f"{function_name}\\(")
    # 3. 对每个调用方，读测试文件
    tests = glob(f"**/test_{function_name}*.py")
    return {
        "definitions": definitions,
        "callers": callers,
        "tests": tests,
    }
```

**优势 3：本地实例（Local Instance）**

- 每个开发者的 Agent 实例基于**自己的代码库快照**工作
- 不上传代码到服务器（**隐私友好**）
- 不需要集中式索引

### 3.3 Agentic Search 与 RAG 的核心差异

| 维度 | RAG | Agentic Search |
|------|-----|----------------|
| 数据流 | 中心化索引 → 检索 | 实时本地 → 工具调用 |
| 滞后 | 几小时 - 几天 | 0 |
| 粒度 | 语义相似片段 | 跟随引用 / 调用链 |
| 隐私 | 需上传索引 | 本地处理 |
| 成本 | 持续管道维护 | 0 管道 |
| 工具 | 向量检索 | grep / read / glob / LSP / bash |

## 四、Claude Code 的 5 大 Harness 扩展点（深度）

Anthropic 官方原话："**围绕模型构建的生态系统（Harness）对 Claude Code 的表现影响更大**"。

5 个扩展点的**构建顺序很重要**（官方建议）：

### 4.1 CLAUDE.md 文件（优先级最高）

**机制**：每次会话开始时自动读取的上下文文件
- 根目录文件：全局视图
- 子目录文件：本地约定

**vs RAG 的优势**：
- 比 RAG **更聚焦**（人工挑选的，不是自动嵌入的）
- 比 RAG **更可控**（人工维护的，不是自动同步的）
- 比 RAG **更精确**（针对代码库的，不是一般化的）

### 4.2 Hooks（钩子）

**机制**：自动化检查脚本
- Pre-commit hooks：提交前自动检查
- Stop hook：会话结束自动反思

**vs RAG 的优势**：
- **确定性执行**（不依赖 AI 检索质量）
- 例：lint / format / 测试覆盖率检查

### 4.3 Skills（技能）

**机制**：渐进式披露（Progressive Disclosure）
- 安全审查技能：在 Claude 评估代码漏洞时加载
- 文档处理技能：在代码变更需要更新文档时加载

**vs RAG 的优势**：
- **按需加载**（比 RAG 的"先检索所有可能相关"更精准）
- 限定到特定路径（只在相关部分激活）

### 4.4 Plugins（插件）

**机制**：打包 skills + hooks + MCP 配置

**vs RAG 的优势**：
- 团队复用（一个插件 → 全员受益）
- 不需要共享 RAG 索引

### 4.5 MCP 服务器

**机制**：Claude 连接到内部工具 / 数据源 / API

**vs RAG 的优势**：
- **结构化查询**（SQL / GraphQL / LSP）比非结构化 RAG 更可靠
- 例：暴露 GitHub API 为 MCP 工具 → Agent 可直接调

## 五、RAG vs Agentic Search vs Hybrid：场景化决策

### 5.1 决策矩阵

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **大规模代码库**（百万行+）| **Agentic Search** | RAG 滞后致命 |
| **文档问答 / 客服知识库** | **RAG** | 更新频率低 / 结构化 |
| **私人知识库（Obsidian）** | **RAG + 全文搜索** | 个人代码量小 |
| **企业合规文档** | **RAG + 权限过滤** | 严格访问控制 |
| **多模态内容（图、文、音）** | **RAG（多模态嵌入）** | 跨模态检索 |
| **金融/医疗行业知识** | **RAG + 审计日志** | 可追溯性要求 |
| **代码片段搜索** | **传统 grep + LSP** | 比 RAG 更精准 |
| **企业内部 API 检索** | **MCP + Agentic** | 结构化优先 |

### 5.2 Hybrid 方案（实战推荐）

```
用户问 → Agent 接收
  ├─ Step 1: 快速 RAG 检索找大致范围（粗排）
  ├─ Step 2: Agentic Search 精细定位（精排）
  ├─ Step 3: 综合答案 + 引用
  └─ 返回结果
```

**优势**：RAG 提供候选集，Agentic 提供精确答案。

## 六、与"驾驭演进"主线的关联

Agentic Search 是 AI Coding 检索范式的演进，**与 [驾驭演进主线（Prompt → Context → Harness → Loop）](../../04-architecture/llm-control-evolution/README.md) 同源**：

| 阶段 | 类比 |
|------|------|
| Prompt | 工程师手写 Prompt → 写菜单 |
| Context | 给 Agent 准备上下文 → 给厨师配助手 |
| **Agentic Search** | **让 Agent 实时检索本地代码库 → 厨师现场找食材** |
| Harness | 用 CLAUDE.md / Skills / Hooks 约束 Agent → 标准化厨房 |

**核心范式转移**：从"中心化索引"到"去中心化实时检索"——和云计算从"集中式数据中心"到"边缘计算"是同一个故事。

## 七、相关章节

**面试题**：
- [咬文嚼字·11.ai/claude-code-agentic-search（30/60/90 秒话术）](../../../13.split-hairs/11.ai/claude-code-agentic-search/README.md)

**同主模块**：
- [Claude Code 最佳实践](../../03-engineering/claude-code-practices/README.md)
- [RAG vs Finetuning](../01-rag-vs-finetuning/README.md)

**架构视角**：
- [11.ai 驾驭演进主线](../../04-architecture/llm-control-evolution/README.md)

---

## 📊 本节统计

- **覆盖深度**：4 个层面（工程问题 / 检索范式 / Harness / 场景边界）
- **官方原话引用**：2 处（Anthropic 博客）
- **决策矩阵**：8 大场景
- **Hybrid 方案**：1 个实战模板
- **关联章节**：3 大类（面试题 / 主模块 / 架构）

---

> 📅 2026-07-03 · 11.ai/07-llmops · ⭐⭐⭐⭐⭐