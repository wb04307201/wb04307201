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

## 2. 文章清单（3 篇，待扩充）

| 主题 | 核心问题 | 难度 |
|------|---------|------|
| [5 万 vs 50 万 App 报价差在哪](app-quote-breakdown/README.md) | 12 大成本维度拆解 + 决策矩阵 | ⭐⭐⭐ |
| [App 技术栈选型](../13.split-hairs/04.system-design/project-management/mobile-tech-stack/README.md) ⏳ 批 2 计划迁至 `09.front-end/08-cross-platform/` | 原生 vs Flutter vs RN vs H5 vs 小程序 | ⭐⭐⭐ |
| [外包项目避坑指南](outsourcing-pitfalls/README.md) | 5 大隐性成本 + 合同 8 条必看 | ⭐⭐⭐ |

> 📌 **章节说明**（2026-06-30 路径整理）：
> - `app-quote-breakdown` / `outsourcing-pitfalls` 已从 `13.split-hairs/04.system-design/project-management/` 迁回本主模块。
> - `mobile-tech-stack` 暂留 split-hairs，规划批 2 迁至主模块 [`09.front-end/08-cross-platform/`](../09.front-end/08-cross-platform/)，与 flutter/rn/pwa 同级。

---

## 3. 待补充主题

- **预算 / 成本估算**：人力配比模型（按功能 / 按人均 / 按月）
- **风险 / 决策**：技术选型 ROI 评估（自研 vs SaaS vs 外包）
- **组织 / 团队**：康威定律下的小团队 + 大团队协作
- **AI 项目管理**：AI Coding 提效的工程账本（DORA / SPACE / ROI）

---

## 4. 适用人群

- 👔 **老板 / 创业者**：评估外包报价、控制项目成本
- 📋 **PM / 项目经理**：管理需求变更、识别风险、推进交付
- 🧑‍💼 **技术总监 / 架构师**：技术选型 ROI 计算、组织能力建设

---

## 5. 学习路径

1. **快速入门**（30 分钟）：看 [app-quote-breakdown](app-quote-breakdown/README.md)，5 分钟理解报价差异维度
2. **技术决策**（30 分钟）：看 mobile-tech-stack（原 split-hairs），评估技术栈对成本的影响
3. **合同避坑**（1 小时）：看 [outsourcing-pitfalls](outsourcing-pitfalls/README.md) → 把它当 checklist 用

---

## 相关章节

- 主模块：[`note/04.system-design`](../04.system-design/README.md)（技术选型的底层支撑）
- 主模块：[`note/09.front-end`](../09.front-end/README.md)（移动端跨端架构决策）
- 面试专题：[`note/13.split-hairs`](../13.split-hairs/README.md)（技术细节高频坑）

---

← [返回笔记目录](../README.md)
