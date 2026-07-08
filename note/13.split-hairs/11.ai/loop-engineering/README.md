<!--
question:
  id: 11.ai-loop-engineering
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 架构困境
  tags: [11.ai, Loop, loop]
-->

# Loop Engineering — 循环调用 Agent 面试深挖

> 一句话定位：Loop Engineering 是"信任 Agent，让它循环重试直到任务完成"——前提是 Harness 兜底防止失控。完整概念见 [主模块 Loop Engineering](../../../11.ai/03-engineering/loop-engineering/README.md)。

---

## 引子：AI 一次写不对，重试 10 次对了——怎么循环？

```text
你的 Agent 自动做"代码 review"任务：

第 1 次跑："测试通过率 70%，有 5 个问题"
你："继续修。"
第 2 次跑："测试通过率 85%，剩 2 个问题"
你："继续。"
...
第 10 次跑："全过！"

行得通吗？行。但——
**如果它卡在 70%，无限循环怎么办？**
如果它每次"修一修"反而引入新 bug 怎么办？
如果修一次要花 $2，第 10 次就是 $20？
```

Loop Engineering = **让 Agent 智能地循环**：

- **Task**：清晰、可验证、可测试
- **Verifier**：自动化的判断函数（不是人，是代码）
- **Feedback**：具体的、可操作的失败信息（不是"再努力"）
- **Max attempts**：必须设上限（建议 3-5），超时熔断
- **Context 管理**：每轮 History 摘要，避免 Context 爆

## 一、Loop 的 3 大核心组件

1. **Task（任务定义）**：可验证、可测试
2. **Verifier（验证函数）**：自动化、ground-truth
3. **Feedback（反馈循环）**：具体、可操作

```
Task → Agent → 检查结果
  ↑                  │
  └──── 不通过 ←─────┘
              通过
                ↓
              Done
```

---

## 二、面试陷阱

### 陷阱 1：以为 Loop 就是"while True"
- **真相**：生产级 Loop 必须有 Max attempts 上限、超时、Context 管理、Verifier、Harness 兜底。

### 陷阱 2：以为 Loop 能解决所有问题
- **真相**：确定性流程用 DAG 更合适（可预测、易调试），模糊探索性任务用 Loop 更合适。复杂业务用 Loop + DAG 混合。

### 陷阱 3：以为 LLM-as-Judge 是万能验证器
- **真相**：LLM 评估本身有偏差，关键验证必须用 ground-truth（单元测试、benchmark）。LLM-as-Judge 只能辅助。

### 陷阱 4：让 Context 累积不重置
- **真相**：每次循环都把错误堆进 Context，最终超窗口。应该**重置 Context + 关键信息**，而非累积。

### 陷阱 5：以为 Loop 只能累积 Context
- **真相**：Ralph Wiggum Loop 证明了 **Fresh Context 架构** 完全可行 —— 每轮 Agent 拿到全新 context window，状态靠**文件系统 + git** 持久化，彻底避免 context 退化。

### 陷阱 6：不知道 "Bash Loop vs Plugin" 两种架构
- **真相**：Agent 循环有两种架构 —— **Bash Loop**（外部 while 循环，每轮 fresh context，如 open-ralph-wiggum）和 **Plugin**（Agent 内部循环，context 累积，如 Claude Code `/loop`）。前者适合长任务，后者设置更简单。

---

## 三、4 大失败模式 + 防护

| 失败模式 | 防护 |
|---------|------|
| **无限循环** | `MAX_ATTEMPTS=5` + `TIMEOUT=300s` |
| **上下文爆炸** | `trim_context(ctx, max_errors=3)` 只保留最近 3 次错误 |
| **幻觉放大** | 用 ground-truth 测试（单元测试），不累积 Context |
| **资源耗尽** | 限制每轮 token 预算 + cheaper 模型做验证 |

---

## 四、反直觉点

- **"重复"≠"低效"**：让 Agent 循环 5 次（每次 5 分钟）比让人类重写 1 次（1 小时）快 2.4 倍。
- **"失败"是"数据"**：每次失败让 Agent 离正确答案更近，关键是失败模式可被验证。
- **"简单循环 > 复杂 DAG"**：对于探索性任务，简单 Loop 比精心设计的 DAG 更有效 —— Agent 自己会找到路径。
- **"信任但验证"**：Loop 假设 Agent 能完成，Verifier 确保它真的完成。

---

## 五、Loop vs DAG 何时选

| 场景 | 推荐 |
|------|------|
| 任务明确、步骤固定 | DAG Workflow |
| 任务模糊、需要探索 | Loop + Agent |
| 一次性脚本 | 一次性 Agent 调用 |
| 持续运行的服务 | Loop + 监控 |
| 复杂业务流 | DAG + Loop 混合 |

详见 [Agent 架构](../agent-dag-vs-react/README.md)。

---

## 六、30 秒面试话术

> Loop Engineering 是 2026 年 AI 工程第四阶段，演进路径是 Prompt → Context → Harness → Loop。
>
> Loop 是"循环调用 Agent 直到任务完成"的模式，核心 3 大组件：任务定义（可验证）、验证函数（自动化 ground-truth）、反馈循环（具体可操作）。
>
> 4 大失败模式：无限循环、上下文爆炸、幻觉放大、资源耗尽。防护手段：Max attempts + 超时 + Context 重置 + cheaper 模型验证。
>
> **实战落地**：Ralph Wiggum Loop 是 2025-2026 最热门的开源实现，核心洞察是 **Fresh Context 架构** —— 每轮 Agent 拿到全新 context window，状态靠文件系统 + git 持久化，彻底避免 context 退化。两种架构：Bash Loop（外部 while 循环，fresh context）vs Plugin（Agent 内部循环，context 累积）。
>
> 何时用 Loop vs DAG：模糊探索任务用 Loop，确定性流程用 DAG。复杂业务用 Loop + DAG 混合。
>
> 反直觉：Loop 的"重复"不是低效，是数据收集；信任 Agent 但 Verifier 兜底。

---

## 七、深度阅读

- 主模块：[Loop Engineering](../../../11.ai/03-engineering/loop-engineering/README.md)
- 🆕 实战工具：[Ralph Wiggum Loop](../../../11.ai/03-engineering/loop-engineering/ralph-wiggum-loop.md) — Fresh Context 循环 CLI
- 同栏目：[Harness Engineering](../harness-engineering/README.md)
- 关联：[Agent 架构](../agent-dag-vs-react/README.md)
- 实战：[生产级 Agent](../../../11.ai/03-engineering/production-agent/README.md)

---

> 📅 2026-06-30 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · loop-engineering](README.md)
