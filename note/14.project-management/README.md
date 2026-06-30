# 项目管理与成本控制

> **给老板 / PM / 技术总监的另一面** —— 技术之外的另一只手：报价拆解、外包风险、技术决策的成本账本。
>
> 本模块不属于"系统设计技术细节"，而是从**业务实战**视角，回答"花 50 万做 App 值不值？""花 50 万买 AI 工具一年回本不？"等问题。
>
> ⚠️ **定位说明**：本模块的内容是**决策+实战指南**，不是"面试刺刀"（面试高频问题请见 [`13.split-hairs`](../13.split-hairs/README.md)）。每篇 50-200 行，聚焦一个具体场景。

← [返回笔记目录](../README.md)

---

## 1. 与其他模块的关系

| 维度 | `note/04.system-design/` | `note/13.split-hairs/` | **本模块 `14.project-management/`** |
|------|---------------------------|------------------------|----------------------------------------|
| **定位** | 系统设计技术细节 | 面试刺刀 | 业务决策+实战 |
| **深度** | 技术广度 | 单点深挖 | 跨域决策 |
| **典型读者** | 后端 / 架构师 | 求职者 | 老板 / PM / 技术总监 / 创业者 |
| **典型问题** | "限流算法怎么实现？" | "令牌桶和漏桶区别？" | "5 万和 50 万 App 报价差在哪？" |
| **使用场景** | 实现 / 选型 | 面试准备 | 拍板 / 报价 / 合同 |

```
技术决策链路：
  13.split-hairs（高频坑）       → 避开 90% 的常见错
  + 04.system-design（架构基线）  → 学到 80% 的工程主流
  + 14.project-management（本模块）→ 把上述能力"定价" + "落地" + "防坑"
```

---

## 2. 文章清单（2 篇已发布 + 4 篇待补充）

### 已发布（2 篇，2026-06-30 路径整理）

| 主题 | 核心问题 | 难度 | 状态 |
|------|---------|------|------|
| [5 万 vs 50 万 App 报价差在哪](app-quote-breakdown/README.md) | 12 大成本维度拆解 + 决策矩阵 | ⭐⭐⭐ | ✅ |
| [外包项目避坑指南](outsourcing-pitfalls/README.md) | 5 大隐性成本 + 合同 8 条必看 | ⭐⭐⭐ | ✅ |

> 📌 **章节说明**（2026-06-30 路径整理）：
> - 上述 2 篇已从 `13.split-hairs/04.system-design/project-management/` 迁回本主模块。
> - `mobile-tech-stack` 已迁至主模块 [`09.front-end/08-cross-platform/`](../09.front-end/08-cross-platform/)，与 flutter/rn/pwa 同级。

### 已发布（6 篇，2026-06-30 Path Z 完成）

| 主题 | 核心问题 | 难度 | 状态 |
|------|---------|------|------|
| [5 万 vs 50 万 App 报价差在哪](app-quote-breakdown/README.md) | 12 大成本维度拆解 + 决策矩阵 | ⭐⭐⭐ | ✅ |
| [外包项目避坑指南](outsourcing-pitfalls/README.md) | 5 大隐性成本 + 合同 8 条必看 | ⭐⭐⭐ | ✅ |
| [技术选型 ROI：自研 vs SaaS vs 外包](self-vs-saas-vs-outsourcing/README.md) | 自研/SaaS/外包 TCO 对比 + 5 大评估维度 + 决策树 + AI 时代变量 + 实战 checklist | ⭐⭐⭐ | ✅ |
| [AI 项目管理账本：DORA + SPACE + ROI](ai-pm-dora-space/README.md) | DORA 4 指标 + SPACE 5 维度 + ROI 综合，AI 时代研发效能度量 + 月/季/年 三阶段实施 | ⭐⭐⭐⭐ | ✅ |
| [人力配比 + 排期估算：3 倍缓冲原则](team-sizing-3x-buffer/README.md) | 阿里 P5/P6/P7 "2-8-2" 黄金比例 + 排期估算公式 + 3 倍缓冲原则 + AI 时代修正 | ⭐⭐⭐ | ✅ |
| [康威定律下的团队拓扑](conways-law-team-topologies/README.md) | 康威定律原文 + Team Topologies 4 类型 + 平台/业务团队比例 + AI 时代趋势 + 实战 checklist | ⭐⭐⭐⭐ | ✅ |

> 📌 **章节说明**（2026-06-30 路径整理）：
> - 上述 6 篇中，前 2 篇从 `13.split-hairs/04.system-design/project-management/` 迁回本主模块。
> - 后 4 篇（Path Z 新增）覆盖"决策 + AI 时代 + 执行 + 组织"4 大维度。
> - mobile-tech-stack 已迁至主模块 [`09.front-end/08-cross-platform/`](../09.front-end/08-cross-platform/)。

### 候选（待扩展）

按"已有 6 篇 + 候选"思路，**Path Z 完成后**保留以下候选：

1. **决策类**：
   - 上云 vs 自建机房
   - 微服务 vs 单体的"二次成本"（运维 / 数据一致性 / 跨团队沟通税）
2. **执行类**：
   - 需求变更控制（MoSCoW / RICE 评分法）
   - 项目风险登记册
3. **风险类**：
   - 技术债的财务账本（与 [12.story/46-tech-debt-career-trap](../12.story/46-tech-debt-career-trap.md) 互补）
4. **组织类**：
   - 远程团队 / 跨时区协作
5. **AI 时代**：
   - AI Agent 在 PM 流程中的嵌入（Harness / Verifier / Feedback 3 件套）

---

## 4. 适用人群

- 👔 **老板 / 创业者**：评估外包报价、控制项目成本、技术选型
- 📋 **PM / 项目经理**：管理需求变更、识别风险、推进交付、人力配比
- 🧑‍💼 **技术总监 / 架构师**：技术选型 ROI 计算、组织能力建设、康威定律落地
- 🤖 **AI 时代从业者**（2026+ 新）：AI Coding 工程账本、Harness 落地、研发效能度量

---

## 5. 学习路径

1. **快速入门**（30 分钟）：看 [app-quote-breakdown](app-quote-breakdown/README.md)，5 分钟理解报价差异维度
2. **合同避坑**（1 小时）：看 [outsourcing-pitfalls](outsourcing-pitfalls/README.md) → 把它当 checklist 用
3. **技术选型**（30 分钟）：看 [self-vs-saas-vs-outsourcing](self-vs-saas-vs-outsourcing/README.md) + [mobile-tech-stack](../../09.front-end/08-cross-platform/mobile-tech-stack/)
4. **AI 时代**（1 小时）：看 [ai-pm-dora-space](ai-pm-dora-space/README.md) → 串联 [12.story/45-ai-productivity-paradox](../../12.story/45-ai-productivity-paradox.md)
5. **执行类**（30 分钟）：看 [team-sizing-3x-buffer](team-sizing-3x-buffer/README.md) → 阿里 2-8-2 模型 + 排期 3 倍
6. **组织进阶**（半天）：看 [conways-law-team-topologies](conways-law-team-topologies/README.md) → 与 [12.story/07-from-chef-to-ceo](../../12.story/07-from-chef-to-ceo.md) 互补

---

## 相关章节

- 📋 [一页速查](./cheatsheet.md) —— 6 大场景决策矩阵 + 速算公式 + 何时该读本模块
- 🛠️ [scripts/validate.py](./scripts/validate.py) —— 合规校验（0 ERR 已验证）
- 🛠️ [scripts/insert-frontmatter.py](./scripts/insert-frontmatter.py) —— 自动加 frontmatter
- 主模块：[`note/04.system-design`](../04.system-design/README.md)（技术选型的底层支撑）
- 主模块：[`note/09.front-end`](../09.front-end/README.md)（移动端跨端架构决策）
- 面试专题：[`note/13.split-hairs`](../13.split-hairs/README.md)（技术细节高频坑）

---

← [返回笔记目录](../README.md)
