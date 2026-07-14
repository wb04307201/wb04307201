<!--
module:
  number: 14
  slug: project-management
  topic: 项目管理与成本控制
  audience: 老板 / PM / 技术总监 / 创业者
  category: 主模块
  summary: 从报价拆解到 AI 时代研发效能度量的项目决策实战手册
-->

# 十四、[项目管理与成本控制](README.md)

> 从报价拆解到 AI 时代研发效能度量的项目决策实战手册——给老板 / PM / 技术总监的另一只手

本章节是 14 主模块中「项目管理」主题的入口，按 **6 大实战场景** 收纳项目决策类内容，覆盖报价拆解、外包避坑、技术选型、AI 研发效能、人力排期、组织拓扑。

---

## 1. 模块导航

| 序号 | 主题 | 核心内容 | 主要子 README |
|------|------|---------|--------------|
| 1 | [5 万 vs 50 万 App 报价差在哪](app-quote-breakdown/README.md) | 12 大成本维度 + 决策矩阵 + 面试陷阱 | [app-quote-breakdown](app-quote-breakdown/README.md) |
| 2 | [外包项目避坑指南](outsourcing-pitfalls/README.md) | 5 大隐性成本 + 合同 8 条 + 验收量化 | [outsourcing-pitfalls](outsourcing-pitfalls/README.md) |
| 3 | [技术选型 ROI：自研 vs SaaS vs 外包](self-vs-saas-vs-outsourcing/README.md) | TCO 对比 + 5 大评估维度 + 决策树 | [self-vs-saas-vs-outsourcing](self-vs-saas-vs-outsourcing/README.md) |
| 4 | [AI 项目管理账本：DORA + SPACE + ROI](ai-pm-dora-space/README.md) | DORA 4 指标 + SPACE 5 维度 + 月/季/年实施 | [ai-pm-dora-space](ai-pm-dora-space/README.md) |
| 5 | [人力配比 + 排期估算：3 倍缓冲原则](team-sizing-3x-buffer/README.md) | 阿里 P5/P6/P7 "2-8-2" + 排期公式 + AI 时代修正 | [team-sizing-3x-buffer](team-sizing-3x-buffer/README.md) |
| 6 | [康威定律下的团队拓扑](conways-law-team-topologies/README.md) | 康威定律 + Team Topologies 4 类型 + 平台比例 | [conways-law-team-topologies](conways-law-team-topologies/README.md) |
| 7 | [面试跨专业应届生：问题库与评估指南](interviewing-cross-disciplinary/README.md) 🆕 | 5 大场景 × 降维版+场景版双题库 + 底线加分模型 + 潜力 3 维度 | [interviewing-cross-disciplinary](interviewing-cross-disciplinary/README.md) |

### 1.1 学习路径

- **新人入门**（30 分钟）：[app-quote-breakdown](app-quote-breakdown/README.md) → [outsourcing-pitfalls](outsourcing-pitfalls/README.md) — 报价 + 合同两大基本盘
- **决策进阶**（1 小时）：[self-vs-saas-vs-outsourcing](self-vs-saas-vs-outsourcing/README.md) → [team-sizing-3x-buffer](team-sizing-3x-buffer/README.md) — 选型 + 排期
- **AI 时代**（1 小时）：[ai-pm-dora-space](ai-pm-dora-space/README.md) — 研发效能度量
- **组织进阶**（半天）：[conways-law-team-topologies](conways-law-team-topologies/README.md) — 团队拓扑与康威定律
- **招聘面试**（30 分钟）：[interviewing-cross-disciplinary](interviewing-cross-disciplinary/README.md) — 面试非科班应届生的问题库与评估指南

### 1.2 候选扩展（待补充）

1. **决策类**：上云 vs 自建机房、微服务 vs 单体的"二次成本"
2. **执行类**：需求变更控制（MoSCoW / RICE）、项目风险登记册
3. **风险类**：技术债的财务账本（与 [12.story/46](../12.story/44-tech-debt-career-trap.md) 互补）
4. **组织类**：远程团队 / 跨时区协作
5. **AI 时代**：AI Agent 在 PM 流程中的嵌入（Harness / Verifier / Feedback 3 件套）

---

## 2. 与其他模块的关系

| 维度 | `note/04.system-design/` | `note/13.split-hairs/` | **本模块 `14.project-management/`** |
|------|---------------------------|------------------------|----------------------------------------|
| **定位** | 系统设计技术细节 | 面试刺刀 | 业务决策 + 实战 |
| **深度** | 技术广度 | 单点深挖 | 跨域决策 |
| **典型读者** | 后端 / 架构师 | 求职者 | 老板 / PM / 技术总监 / 创业者 |
| **典型问题** | "限流算法怎么实现？" | "令牌桶和漏桶区别？" | "5 万和 50 万 App 报价差在哪？" |
| **使用场景** | 实现 / 选型 | 面试准备 | 拍板 / 报价 / 合同 |

---

## 3. 知识脉络

```mermaid
graph LR
    A[拍板决策<br/>报价拆解] --> B[风险防控<br/>外包避坑]
    B --> C[技术选型<br/>自研 vs SaaS]
    C --> D[效能度量<br/>DORA + SPACE]
    D --> E[执行落地<br/>3 倍缓冲排期]
    E --> F[组织能力<br/>康威 + Team Topologies]
    F --> G[AI 时代变量<br/>Harness + ROI]
```

---

## 4. 速查表

| 场景 | 决策依据 | 关键数字 | 推荐章节 |
|------|----------|----------|----------|
| **报价差异** | 12 大成本维度 | 人月单价 2-8 万 | [app-quote-breakdown](app-quote-breakdown/README.md) |
| **外包合同** | 隐性成本 + 合同条款 | 5 大隐性 / 8 条必看 | [outsourcing-pitfalls](outsourcing-pitfalls/README.md) |
| **自研 vs SaaS** | 5 年 TCO + 团队规模 | < 50 人 SaaS 优先 | [self-vs-saas-vs-outsourcing](self-vs-saas-vs-outsourcing/README.md) |
| **研发效能** | DORA 4 + SPACE 5 | 月/季/年三阶段 | [ai-pm-dora-space](ai-pm-dora-space/README.md) |
| **排期估算** | 3 倍缓冲 + 黄金比例 | 2-8-2 配比 | [team-sizing-3x-buffer](team-sizing-3x-buffer/README.md) |
| **团队拓扑** | 4 类型 + 比例 | 平台 ≤ 30% | [conways-law-team-topologies](conways-law-team-topologies/README.md) |

---

## 5. 核心内容（按场景展开）

### 5.1 拍板决策（报价 / 选型）

- 报价 12 维拆解：人力 / 测试 / 部署 / 合规 / 设计 / 运维 / 售后 / 隐性沟通税
- 自研 vs SaaS vs 外包：5 年 TCO 对比 + 团队规模 + 业务稳定性
- 微服务 vs 单体的"二次成本"：运维、数据一致性、跨团队沟通税

### 5.2 风险防控（合同 / 避坑）

- 5 大隐性成本：需求蔓延、沟通税、试错成本、运维债、人员流动
- 合同 8 条必看：SLA、知识产权、源码归属、验收标准、违约条款、付款节奏
- 项目风险登记册：识别 / 评估 / 响应 / 监控

### 5.3 效能度量（AI 时代 + 传统）

- DORA 4 指标：部署频率 / 前置时间 / 变更失败率 / MTTR
- SPACE 5 维度：满意度 / 绩效 / 活动 / 沟通 / 效率
- 代码流失率：6 周内被修改 / 重写 / 删除的代码比例（AI 时代关键）

### 5.4 执行落地（人力 / 排期）

- 阿里 P5/P6/P7 "2-8-2" 黄金比例
- 排期 3 倍缓冲原则：估算乐观值 × 3 = 实际承诺
- AI 时代修正：单人产能 × 1.5-2.5（看工具熟练度）

### 5.5 组织能力（康威 + Team Topologies）

- 康威定律：系统设计 = 组织沟通结构的镜像
- Team Topologies 4 类型：流对齐 / 平台 / 使能 / 复杂子系统
- 平台团队比例 ≤ 30%，流对齐团队 60-70%

---

## 6. 最佳实践

### 6.1 报价阶段

- **报价必须拆 12 维**，不能只给"总价"——同一 App 报价差异 10× 通常源于维度遗漏
- **留 15-20% 缓冲**给需求变更（特别是在合同不完善时）
- **要求外包方提供过往案例**和可验证的联系方式

### 6.2 选型阶段

- **TCO 计算要算 5 年**，而不是 1 年——SaaS 订阅累积往往超过自研
- **优先选有完整生态的开源**，避免被单一厂商绑定
- **AI 工具先试用再付费**，多数厂商提供免费层或 PoC

### 6.3 排期阶段

- **3 倍缓冲**：估算 × 3 = 承诺给老板的日期
- **2-8-2 配比**：团队中 20% 顶尖 + 80% 主力 + 20% 待优化
- **每周同步进度**，但不过细——日站会浪费 30% 时间

### 6.4 组织阶段

- **平台团队不超过 30%**，避免"为平台而平台"
- **流对齐团队 ≥ 60%**，直接交付业务价值
- **AI Coding 工具全团队铺开**，但保留资深工程师做 code review

---

## 7. 常见面试题

> 本模块主要面向业务决策者，技术面试高频问题请见 [`13.split-hairs`](../13.split-hairs/README.md)。

| 场景 | 典型问题 | 参考答案 |
|------|----------|----------|
| **项目管理** | 5 万 vs 50 万 App 报价差在哪？ | 见 [app-quote-breakdown](app-quote-breakdown/README.md) |
| **风险管理** | 外包项目最常见的隐性成本？ | 见 [outsourcing-pitfalls](outsourcing-pitfalls/README.md) |
| **技术选型** | 自研 vs SaaS vs 外包怎么选？ | 见 [self-vs-saas-vs-outsourcing](self-vs-saas-vs-outsourcing/README.md) |
| **效能度量** | DORA 4 指标是哪些？ | 部署频率 / 前置时间 / 失败率 / MTTR |
| **团队管理** | 康威定律怎么落地？ | 见 [conways-law-team-topologies](conways-law-team-topologies/README.md) |

---

## 8. 适用人群

- 老板 / 创业者：评估外包报价、控制项目成本、技术选型
- PM / 项目经理：管理需求变更、识别风险、推进交付、人力配比
- 技术总监 / 架构师：技术选型 ROI 计算、组织能力建设、康威定律落地
- AI 时代从业者（2026+）：AI Coding 工程账本、Harness 落地、研发效能度量

---

## 9. 相关章节

- 一页速查：[`cheatsheet.md`](./cheatsheet.md) —— 6 大场景决策矩阵 + 速算公式
- 主模块：[`note/04.system-design`](../04.system-design/README.md) — 技术选型的底层支撑
- 主模块：[`note/09.front-end`](../09.front-end/README.md) — 移动端跨端架构决策
- 故事：[`note/12.story/07-from-chef-to-ceo`](../12.story/07-from-chef-to-ceo.md) — 团队管理叙事版
- 故事：[`note/12.story/43-ai-productivity-paradox`](../12.story/43-ai-productivity-paradox.md) — AI 生产力悖论
- 故事：[`note/12.story/44-tech-debt-career-trap`](../12.story/44-tech-debt-career-trap.md) — 技术债困局
- 面试专题：[`note/13.split-hairs`](../13.split-hairs/README.md) — 技术细节高频坑

---

## 10. 开源参考

| 项目 / 资料 | 说明 | 链接 |
|-------------|------|------|
| Team Topologies | 团队拓扑原书 | [teamtopologies.com](https://teamtopologies.com) |
| DORA | DevOps Research & Assessment | [dora.dev](https://dora.dev) |
| SPACE 框架 | 开发者生产力多维度量 | [queue.acm.org](https://queue.acm.org/detail.cfm?id=3454122) |
| 阿里 P 序列 | 阿里 P5/P6/P7 职级体系 | 行业通行参考 |
| 12 Story 餐厅系列 | 阿明餐厅团队管理叙事 | [`12.story/07`](../12.story/07-from-chef-to-ceo.md) |

---

## 📊 本节统计

| 项目 | 数量 | 说明 |
|------|------|------|
| 主模块 README | 1 | 本文件 |
| 顶层分类（实战场景） | 7 | app-quote-breakdown / outsourcing-pitfalls / self-vs-saas-vs-outsourcing / ai-pm-dora-space / team-sizing-3x-buffer / conways-law-team-topologies / interviewing-cross-disciplinary |
| 子 README | 7 | 每个顶层分类 1 个 |
| 一页速查 | 1 | [cheatsheet.md](./cheatsheet.md) |
| 辅助子目录（scripts/） | 1 | 历史脚本占位（保留，未删除） |
| **README 总数** | **9** | 1 顶层 + 7 子 + 1 cheatsheet |

---

← [返回笔记目录](../README.md)