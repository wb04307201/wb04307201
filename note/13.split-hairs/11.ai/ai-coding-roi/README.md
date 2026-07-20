<!--
question:
  id: 11.ai-ai-coding-roi
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [11.ai, coding, roi]
-->

# AI 编程 ROI 度量：DORA 4 指标 + SPACE 5 维度

> 怎么证明"AI 编程工具值得投入"？考察的是 **AI 时代研发效能度量框架**——传统 ROI 度量失效，需要 DORA + SPACE 等新框架。

## 引子：花 50 万买 AI 工具，省了 80 万——这个账怎么算？

```text
财务总监："老板要我们列个 AI Coding ROI 报告，半年了快 50 万出去了。"
你（研发负责人）："省了 80 万。这是账本。"
财务总监："……空口说 80 万。我要可追溯的数字。"
你："……呃。"
```

**真相**：AI Coding ROI **极难量化**——价值在哪儿？谁在用？真的省了多少？

成熟的 ROI 度量框架 = **DORA 4 指标 + SPACE 5 维度 + 商业价值**：

- **DORA 4 指标**：部署频率、变更前置时间、变更失败率、MTTR
- **SPACE 5 维度**：Satisfaction（满意度）/ Performance（性能）/ Activity（活动）/
  Communication & Collaboration（协作）/ Efficiency（效率）
- **商业价值**：节省的工程时间 × 时薪 + 加速 release 带来的业务收益

不要只看"代码行数"。**看 bug 率 / 留存率 / 资深 vs 初级差异 / 加班时长 / 商业价值**。

## 一、核心结论（TL;DR）

| 框架 | 维度 | 来源 |
|------|------|------|
| **DORA** | 4 大指标（吞吐量/稳定性/前置时间/失败率） | Google DORA |
| **SPACE** | 5 维度（满意度/绩效/活动/沟通/效率）| Microsoft Research |
| **AI 时代新指标** | 代码流失率 / 6 周留存率 / Token 投入产出比 | Waydev/GitClear 等 |

> 一句话：**传统 ROI 度量（代码行数 / commit 数）在 AI 时代失效，必须切换到 DORA + SPACE 框架**。

---

## 二、为什么传统 ROI 度量失效？

### 1. 旧指标 vs AI 时代

| 旧指标 | AI 时代的真相 |
|--------|-------------|
| 代码行数 | 🚀 +217% 但价值下滑 |
| Commit 数 | 🚀 +861% 但返工暴涨 |
| AI 采纳率 | 🚀 80% 但 6 周留存 30% |
| Token 成本 | 🚀 +1000% 但收益只有 2x |

### 2. 三大失效原因

1. **数量 ≠ 价值**：AI 让"垃圾代码"也能快速产出
2. **短期 ≠ 长期**：短期看着快，长期技术债积累
3. **个人 ≠ 团队**：个人效率上升，团队协作变差（review 压力）

---

## 三、DORA 4 大指标（Google DORA 2025）

DORA（DevOps Research and Assessment）是 Google 主导的研发效能研究项目，2025 年报告专门讨论 AI 时代。

### 1. 部署频率（Deployment Frequency）

- **含义**：单位时间内部署到生产的次数
- **传统基准**：Elite 团队每天多次，Low 团队每月 1 次
- **AI 时代挑战**：AI 让"提交快"，但"部署"还需 CI/CD

### 2. 变更前置时间（Lead Time for Changes）

- **含义**：从代码提交到生产运行的时间
- **传统基准**：Elite < 1 小时，Low > 1 个月
- **AI 时代挑战**：review 排队可能导致前置时间反而上升

### 3. 变更失败率（Change Failure Rate）

- **含义**：导致生产事故或回滚的变更比例
- **传统基准**：Elite 0-15%，Low > 60%
- **AI 时代挑战**：AI 代码修改率 9.4x → 失败率可能暴涨

### 4. 故障恢复时间（MTTR / Failed Deployment Recovery Time）

- **含义**：从生产事故到恢复的时间
- **传统基准**：Elite < 1 小时，Low > 1 周
- **AI 时代挑战**：事故频率高 + 复杂度高 → MTTR 上升

### DORA 4 指标速查表

| 指标 | Elite | High | Medium | Low |
|------|-------|------|--------|-----|
| 部署频率 | 按需（每天多次）| 每周-每天 | 每周-每月 | 每月-每 6 个月 |
| 变更前置时间 | < 1 天 | 1 天-1 周 | 1 周-1 月 | > 1 月 |
| 变更失败率 | 0-15% | 16-30% | 31-45% | > 46% |
| MTTR | < 1 小时 | < 1 天 | < 1 周 | > 1 周 |

---

## 四、SPACE 5 维度（Microsoft Research）

SPACE 框架由 Microsoft Research 提出，专门用于度量开发者生产力，包含 5 个维度：

### 1. Satisfaction（满意度）

- 开发者对工作、AI 工具、流程的满意度
- **度量**：问卷调查（eNPS、1-5 分）
- **AI 时代**：AI 让"低创造性工作"减少，满意度应该上升；如果下降说明 AI 在制造焦虑

### 2. Performance（绩效）

- 实际产出的业务价值
- **度量**：有效功能数、用户满意度、生产事故率
- **AI 时代**：必须用"价值"而非"代码量"

### 3. Activity（活动）

- 开发者的工作活动（commit、PR、review、调试）
- **度量**：commit 数、PR 数、review 数、会议时长
- **AI 时代陷阱**：Activity 暴涨不代表绩效好

### 4. Communication & Collaboration（沟通与协作）

- 团队协作质量（review 反馈、文档、讨论）
- **度量**：review 时间、PR 评论数、知识共享频率
- **AI 时代挑战**：review 压力上升，质量下降

### 5. Efficiency & Flow（效率与流畅）

- 开发者专注时间和心流状态
- **度量**：中断频率、专注时长、加班时长
- **AI 时代挑战**：AI 让"开始变快"，但"完成变慢"（返工多）

### SPACE 5 维度速查表

| 维度 | 度量方式 | AI 时代陷阱 |
|------|---------|------------|
| Satisfaction | eNPS 问卷 | 焦虑上升导致满意度下降 |
| Performance | 有效功能数 / 事故率 | 必须切换到价值指标 |
| Activity | commit / PR 数 | 暴涨不代表提升 |
| Communication | review 时间 / PR 评论数 | review 压力上升 |
| Efficiency | 专注时长 / 加班时长 | 加班暴涨效率反而下降 |

---

## 五、AI 时代的 5 个新指标

### 1. 6 周代码留存率（6-Week Code Retention）

```text
留存率 = 6 周后仍在生产环境的代码 / AI 提交的总代码
基准：> 50% 为健康
```

### 2. 代码流失率（Code Churn Rate）

详见 [`ai-code-churn`](../ai-code-churn/README.md)。

### 3. Token 投入产出比（Token ROI）

```text
Token ROI = 业务价值 / Token 成本
基准：根据业务调整
```

### 4. AI 代码 Review 拒绝率

```text
Review 拒绝率 = 被拒绝合并的 AI 代码 / 总 AI 代码
基准：> 20% 说明 Harness 不够
```

### 5. AI 陷阱发现率

```text
陷阱发现率 = review 中发现的 AI 陷阱数 / AI 代码总数
基准：每 1000 行至少 1 个陷阱被识别
```

---

## 六、6 大改进策略

### 1. 切换考核指标

| 旧考核 | 新考核 |
|--------|--------|
| 代码行数 | 有效功能交付数 |
| Commit 数 | 变更失败率 |
| AI 采纳率 | 6 周留存率 |
| Token 用量 | Token 投入产出比 |

### 2. Harness 优先

详见 [`harness-engineering`](../harness-engineering/README.md)。

### 3. 强制 Code Review

- AI 代码必须资深工程师 review
- 关键模块禁止 AI 直接写

### 4. Token 预算透明化

- 每个工程师每月 Token 预算 $2000
- 超预算需 review 工作流

### 5. 流失率度量与告警

- 每月统计个人/团队流失率
- 流失率 > 60% 触发 review

### 6. 初级工程师强制培训

- AI 协作工程专项培训
- 必须识别 5 类 AI 陷阱

---

## 七、真实案例对比

### 高 ROI 团队（Stripe）

| 指标 | 数值 |
|------|------|
| AI 代码采纳率 | 65% |
| 6 周留存率 | **75%** |
| 变更失败率 | 8% |
| MTTR | < 1 小时 |
| DORA 等级 | **Elite** |

### 低 ROI 团队（普通互联网公司）

| 指标 | 数值 |
|------|------|
| AI 代码采纳率 | 85% |
| 6 周留存率 | **22%** |
| 变更失败率 | 38% |
| MTTR | > 1 天 |
| DORA 等级 | **Medium** |

**关键差异**：高 ROI 团队有完善的 Harness 和 review 流程，**采纳率低但留存率高**；低 ROI 团队采纳率高但返工多。

---

## 八、面试陷阱

### 陷阱 1：以为 ROI 度量只看成本

- **真相**：必须看"成本 + 价值"两边，单纯看 Token 成本会误导

### 陷阱 2：以为 DORA 指标对 AI 时代无效

- **真相**：DORA 2025 报告明确说 DORA 指标仍然有效，但需要补充 AI 时代新指标

### 陷阱 3：以为 SPACE 比 DORA 更先进

- **真相**：SPACE 和 DORA 是互补的——DORA 关注交付，SPACE 关注人

### 陷阱 4：以为"AI 提效 2 倍"就是 ROI 高

- **真相**：要看"提效 2 倍" vs "成本涨 10 倍"的比值

---

## 九、面试话术（90 秒版本）

> AI 时代传统 ROI 度量（代码行数/commit 数）失效，必须切换到 **DORA + SPACE 双框架**：
>
> **DORA 4 指标**：
>
> 1. 部署频率
> 2. 变更前置时间
> 3. 变更失败率
> 4. MTTR
>
> **SPACE 5 维度**：
>
> 1. Satisfaction（满意度）
> 2. Performance（绩效）
> 3. Activity（活动）
> 4. Communication（沟通）
> 5. Efficiency（效率）
>
> **AI 时代 5 个新指标**：6 周留存率、代码流失率、Token ROI、AI Review 拒绝率、AI 陷阱发现率。
>
> 改进策略：切换考核指标 / Harness 优先 / 强制 Review / Token 预算透明化 / 流失率告警 / 初级工程师培训。
>
> 反直觉：高 ROI 团队往往**采纳率低但留存率高**（Stripe：65% 采纳，75% 留存）；低 ROI 团队**采纳率高但留存率低**（85% 采纳，22% 留存）。

---

## 十、相关章节

- 同栏目：[`ai-coding-productivity-paradox`](../ai-coding-productivity-paradox/README.md) — 4 大研究 + DORA 框架
- 同栏目：[`ai-code-churn`](../ai-code-churn/README.md) — 代码流失率专题
- 同栏目：[`harness-engineering`](../harness-engineering/README.md) — Harness Engineering
- 同栏目：[`ai-code-review`](../ai-code-review/README.md) — 验收成本要计入 AI 编程真实 ROI
- 主模块：[`11.ai/05-applications`](../../../11.ai/05-applications/README.md) — AI 行业应用
- 故事：[`12.story/43-ai-productivity-paradox`](../../../12.story/43-ai-productivity-paradox.md) — 阿明餐厅复盘

- Token 成本：[`AI 编程 Token 经济学`](../ai-coding-token-economics/README.md) — 杠杆率法则 + Token 悖论 + 企业成本失控案例

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（2026 面试热点 + 实战必会）

← [返回: 咬文嚼字 · ai-coding-roi](../README.md)
