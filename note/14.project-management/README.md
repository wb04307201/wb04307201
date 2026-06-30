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

### 候选（4 篇，待 Path Z 完成后发布）

| 主题 | 核心问题 | 难度 | 状态 |
|------|---------|------|------|
| 技术选型 ROI：自研 vs SaaS vs 外包 | [自研/SaaS/外包 TCO 对比 + 5 大评估维度 + 决策树 + AI 时代变量 + 实战 checklist](self-vs-saas-vs-outsourcing/README.md) | ⭐⭐⭐ | ✅ |
| AI 项目管理账本：DORA + SPACE + ROI | AI 时代研发效能度量框架 | ⭐⭐⭐⭐ | ⏳ 待写 |
| 人力配比 + 排期估算：3 倍缓冲原则 | 阿里 "2-8-2" 模型 + 排期公式 | ⭐⭐⭐ | ⏳ 待写 |
| 康威定律下的团队拓扑 | Team Topologies 4 类型 + 流对齐 | ⭐⭐⭐⭐ | ⏳ 待写 |

---

## 3. 待补充主题（2026 候选）

按 PM 实用度排序：

1. **决策类**：
   - 自研 vs 购并 vs 集成（C1：技术选型 ROI）
   - 上云 vs 自建机房
   - 微服务 vs 单体的"二次成本"
2. **执行类**：
   - 人力配比模型（C3：阿里 P5/P6/P7 比例）
   - 排期估算 + 3 倍缓冲原则（C3）
   - 需求变更控制（MoSCoW / RICE）
3. **风险类**：
   - 项目风险登记册
   - 技术债的财务账本（与 [46-tech-debt-career-trap](../12.story/46-tech-debt-career-trap.md) 互补）
4. **组织类**：
   - 康威定律（C4）
   - 平台团队 vs 业务团队比例
   - 远程团队 / 跨时区协作
5. **AI 时代**（C2）：
   - AI Coding 提效的工程账本
   - AI Agent 在 PM 流程中的嵌入

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
3. **技术选型**（30 分钟）：看 C1（待补充）+ [09.front-end/08-cross-platform/mobile-tech-stack](../09.front-end/08-cross-platform/mobile-tech-stack/)
4. **AI 时代**（1 小时）：看 C2（待补充）→ 串联 [12.story/44-46](../12.story/45-ai-productivity-paradox.md)（个人 / 数据 / 责任视角）
5. **组织进阶**（半天）：看 C3 + C4（待补充）→ 与 [12.story/07-from-chef-to-ceo](../12.story/07-from-chef-to-ceo.md) 互补

---

## 相关章节

- 主模块：[`note/04.system-design`](../04.system-design/README.md)（技术选型的底层支撑）
- 主模块：[`note/09.front-end`](../09.front-end/README.md)（移动端跨端架构决策）
- 面试专题：[`note/13.split-hairs`](../13.split-hairs/README.md)（技术细节高频坑）

---

← [返回笔记目录](../README.md)
