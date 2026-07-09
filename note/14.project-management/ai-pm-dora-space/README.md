<!--
module:
  parent: project-management
  slug: pm/ai-pm-dora-space
  type: article
  category: 主模块子文章
  summary: DORA + SPACE + ROI 三件套，AI 时代研发效能度量框架。
-->

# AI 项目管理账本：DORA + SPACE + ROI 三件套

> CTO / PM / 研发效能负责人都面对一个共同问题：**花 50 万买 AI Coding 工具，半年后真的"省了 80 万"吗？应该看哪些指标？**考察的是 **AI 时代的研发效能度量能力**，不是"AI Coding 好不好用"。

> **前置知识**：[12.story/45-ai-productivity-paradox](../../12.story/45-ai-productivity-paradox.md)（Waydev/GitClear 数据真相）、[12.story/31-codebase-cognitive-debt](../../12.story/31-codebase-cognitive-debt.md)（认知债）、[13.split-hairs/09.front-end/this-binding](../../13.split-hairs/09.front-end/this-binding/README.md)等 AI 主题面试题。

---

## 引言：DORA 2025 显示——AI 编码让公司两极分化

```text
Google DORA 2025 Report 核心发现：
- 22% 公司是"AI 高绩效组"：吞吐 +30% / 稳定性 +20%
- 38% 公司是"AI 受困组"：吞吐 +20% / 稳定性 -40%
- 40% 公司是"AI 影响微弱组"

为什么会两极分化？

"AI 受困组"的共同特征：
- 提交量暴涨（+217%）但生产 bug 也暴涨（+383%）
- Token 月成本激增 5 倍
- 工程师加班时长 +77%
- 资深 vs 初级差异：高级 +60%，初级 -15%

老板拍板："AI 提效了，但质量降了、成本涨了、人更累了"。
```

**真相**：AI 是 **放大器**，不是"提效工具"。
- 基础设施好的团队：AI 让你更强（DORA 高绩效组）
- 基础设施差的团队：AI 让 bug 也更多（DORA 受困组）

**单纯看"代码量" = 看错账户**。必须用 **DORA + SPACE + ROI 三件套** 立体度量。

---

## 一、核心结论（TL;DR）：3 个框架组合用法

| 框架 | 度量 | 时间窗 | 谁用 |
|------|------|--------|------|
| **DORA** | 4 大流程指标（速度 + 稳定性） | 月度 / 季度 | CTO / 工程效能 |
| **SPACE** | 5 大开发者体验维度 | 季度 / 半年 | HR / EM |
| **ROI** | 业务价值 / 总投入 | 项目级 / 年度 | CEO / CFO |

**正确组合**：
- 月度 → **DORA** 跟踪
- 季度 → **DORA + SPACE** 组合（速度 + 人）
- 年度 → **DORA + SPACE + ROI** 三件套全开

---

## 二、DORA 4 指标详解（速度 + 稳定性）

### 指标 1：部署频率（Deployment Frequency）

```text
定义：单位时间内部署到生产的次数
目标：精英团队每日多次，普通团队每周几次
落后信号：周部署 < 1 次（很可能手工）
```

### 指标 2：变更前置时间（Lead Time for Changes）

```text
定义：代码 commit 到生产部署的时间
目标：< 1 天（精英），< 1 周（普通），< 1 月（落后）
落后信号：> 1 月（CI/CD 有问题）
```

### 指标 3：变更失败率（Change Failure Rate）

```text
定义：导致生产事故或回滚的部署占比
目标：0-15%（精英），15-30%（普通），> 30%（高风险）
AI 时代陷阱：AI 让代码修改率 +217%（GitClear），失败率可能暴涨
```

### 指标 4：MTTR（Mean Time To Recovery）

```text
定义：生产事故从发生到恢复的平均时间
目标：< 1 小时（精英），< 1 天（普通），> 1 天（落后）
AI 时代陷阱：AI 可能让 bug 频率高，但 MTTR 反而更快（AI 协助排障）
```

### DORA × AI 时代的陷阱

| 指标 | 表面 | 真实 |
|------|------|------|
| 部署频率 | +217%（AI 自动提交） | 但失败率从 5% 涨到 15% |
| 前置时间 | -50%（AI 加速） | **但代码修改率 +9.4 倍**，净效益接近 0 |
| 变更失败率 | 5% → 15% | **Token 成本 +488%** 抵消吞吐 |
| MTTR | 改善 | 但 **P0 事故 +200%** |

→ **DORA 4 指标必须配合 ROI 看**，否则就是"指标漂亮但公司亏损"。

---

## 三、SPACE 5 维度详解（开发者体验）

### S：Satisfaction（满意度）

```text
指标：
- 工单 NPS / 团队调研 / Glassdoor 评分
- "我想继续在这工作"打分

AI 时代：满意度可能上升（AI 让工作爽），也可能下降（偷懒了反而焦虑）
```

### P：Performance（绩效）

```text
指标：
- 目标达成率 / OKR 评分
- 项目交付质量（线上事故数 / SLA 达成率）

AI 时代：高级 +60%，初级 -15%（晋升通道变窄）
```

### A：Activity（活动）

```text
指标：
- commit 数 / PR 数 / 评审数 / code review 次数

AI 时代：表面暴涨（AI 自动提交），但 ❌ 不可单独看
```

### C：Communication & Collaboration（沟通协作）

```text
指标：
- 跨团队 PR 数量 / 文档贡献度 / On-call 时长
- "团队感受"调研

AI 时代：Cursor 不替你开会；协作仍然是人的协作
```

### E：Efficiency（效率）

```text
指标：
- 故事点完成率 / DORA 4 指标（速度类）
- 单位代码产量（loc/人/天）—— AI 时代此指标**作废**

AI 时代关键修正：**别再用 loc / 人 / 天衡量效率**。AI 让"代码量"暴涨，但价值不一定涨。
```

---

## 四、ROI 综合计算（CEO/CFO 视角）

### 公式

```text
ROI = (业务价值 - 总投入) / 总投入 × 100%
```

### 3 块价值来源

| 价值 | 怎么算 |
|------|--------|
| **节省工程时间** | 时薪 × 节省小时数 = 25 万 × 节省时间 |
| **加快 release** | 提前上线的业务收益（GMV）|
| **减少事故** | 减少的 P0 / P1 损失 |

### 真实案例（用 [12.story/45](../../12.story/45-ai-productivity-paradox.md) 的数据）

```text
公司半年盘点：
- 工具花费：Token + 云 = 23.5 万/年
- 节省工程时间：估算约 80 万
- 加速 release：1 个新业务提前上线 2 周，估算 200 万 GMV
- 减少事故：原本该有的 P0 反而多了？反而 -50 万（事故损失）

ROI = (80 + 200 - 50 - 23.5) / 23.5 × 100%
    = 206.5 / 23.5 × 100%
    = **879%**
```

> **但**：上述假设"加速 release"和"减少事故"都需要 **PM 主动验证**。AI Coding 经常看起很美，实际上：
> - 提前 2 周上线的业务，可能**根本没上线**（因为 AI 写的代码测试不全）
> - 节省工程时间，可能是**节省在新功能 bug 修复上**

→ **ROI 必须用 SPACE 验证** —— 如果满意度下降，不能算 ROI 真实。

---

## 五、AI 时代 3 个特别提醒

### 提醒 1：不要只盯代码量

```text
commit 数 = AI 自动提交
PR 数 = AI 自动提
loc = AI 自动写

→ 这三个"看起爆涨"的指标在 AI 时代**作废**。
→ 真正有效的是"DORA 4 指标 + SPACE 5 维度 + ROI"组合。
```

### 提醒 2：资深 vs 初级分化

```text
Waydev 数据：AI 代码采纳率
- 资深工程师 60-70%
- 初级工程师 85-95%

采纳率 ≠ 留存率：
- 6 周后资深留存 60%
- 6 周后初级留存 20%
```

→ **AI 让"前辈吃经验、初级吃错误率"更明显**。**晋升通道收窄** —— SPACE 满意度下降的元凶。

### 提醒 3：3 件套不是同时上

```text
实际项目上线顺序：
  第 1 月：DORA 4 指标（技术侧）
  第 3 月：+ SPACE 5 维度（人侧）
  第 6 月：+ ROI 综合（业务侧）
```

→ 边做边度量，避免 3 套一起上的"度量灾难"。

---

## 六、实战 checklist（月度 / 季度 / 年度）

### 月度

- [ ] **DORA 部署频率** 是否在目标区间
- [ ] **DORA 失败率** 是否比上个月恶化
- [ ] **事故复盘** —— 列出 3 个最大事故的根因 + 改进项
- [ ] **Token 成本** 同期比 —— 警惕"暴涨但吞吐未涨"信号

### 季度

- [ ] **DORA 4 指标综合评估**（调用 gooreport 等工具）
- [ ] **SPACE 1 次团队调研** —— 关注满意度与"我想继续"
- [ ] **AI Coding 留存率** —— 找出"AI 提交但 6 周被回滚"的代码
- [ ] **资深 vs 初级 AI 采纳率对比** —— 警惕 DORA 放大器陷阱

### 年度

- [ ] **DORA + SPACE + ROI 三件套全开**
- [ ] **对外汇报** —— 让 CEO/CFO 看到"AI 投的钱真实回本"
- [ ] **架构债 / 认知债** —— 同时看 [12.story/31-codebase-cognitive-debt](../../12.story/31-codebase-cognitive-debt.md)
- [ ] **组织能力评估** —— 用 SPACE 中"沟通 / 协作"维度，结合 [12.story/07-from-chef-to-ceo](../../12.story/07-from-chef-to-ceo.md)

---

## 七、避坑指南（5 大坑）

| 坑 | 失败模式 | 避坑 |
|----|---------|------|
| ① **只追 DORA 不追 SPACE** | 增速漂亮，但工程师离职 | DORA + SPACE 组合 |
| ② **只看 ROI 不看 DORA** | 业务收益好看，但天天出事故 | ROI 之前必须先稳定 |
| ③ **用 loc 算 AI 效率** | 表面暴涨，实际全是 AI 写的"屎山" | 改用"留存率 / 改动率" |
| ④ **三件套一次上** | 调研失控，团队疲劳 | 月/季/年 三阶段上 |
| ⑤ **DORA 数值对外汇报** | 老板只想看 ROI，不是"我们多努力" | DORA → 内部；ROI → 对外 |

---

## 相关章节

- 主模块：[`note/14.project-management`](../README.md)（项目管理主页）
- 故事章节：[`12.story/45-ai-productivity-paradox`](../../12.story/45-ai-productivity-paradox.md) — Waydev/GitClear/Faros/Jellyfish 数据
- 故事章节：[`12.story/31-codebase-cognitive-debt`](../../12.story/31-codebase-cognitive-debt.md) — AI 时代认知债
- 故事章节：[`12.story/44-ai-engineer-responsibility`](../../12.story/44-ai-engineer-responsibility.md) — AI 责任金字塔
- 故事章节：[`12.story/07-from-chef-to-ceo`](../../12.story/07-from-chef-to-ceo.md) — 组织管理康威定律
- 主模块：[`note/11.ai/03-engineering/harness-engineering`](../../11.ai/03-engineering/harness-engineering/README.md) — Harness 工程

---

← [返回项目管理主页](../README.md)
