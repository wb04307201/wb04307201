# 项目管理与成本控制 —— 一页速查

> 一页纸 PM 决策速查表，涵盖 **报价 / 外包 / 技术选型 / AI 时代账本 / 人力配比 / 团队拓扑** 6 大场景。
> 用法：在拍板时打开本速查 → 对照决策树 → 找到最相关文档 → 深读全文。

← [返回项目管理主页](./README.md)

---

## 1. 6 大场景速查矩阵

| 拍板场景 | 关键决策 | 速查公式 | 主文档 |
|---------|---------|---------|--------|
| **收到 3 家报价** | 价格合理性？ | 12 大成本维度对比 | [app-quote-breakdown](./app-quote-breakdown/README.md) |
| **已签外包** | 隐性风险？ | 5 大隐性成本 + 合同 8 条 | [outsourcing-pitfalls](./outsourcing-pitfalls/README.md) |
| **"自研 / SaaS / 外包"选型** | 三选一怎么决策？ | 5 维评分 + 决策树 + TCO 公式 | [self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md) |
| **AI Coding 买了** | 真的提效？ | DORA 4 + SPACE 5 + ROI 综合 | [ai-pm-dora-space](./ai-pm-dora-space/README.md) |
| **团队要扩人** | 招几个高级？ | 阿里 2-8-2 模型 + 排期 3 倍 | [team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md) |
| **组织架构调整** | 调架构还是调系统？ | 团队拓扑 4 类型 + 康威定律 | [conways-law-team-topologies](./conways-law-team-topologies/README.md) |

---

## 2. 报价速查（3 类方案）

```text
5 万档 = 原型验证 / MVP（学生兼职 + H5 套壳）
20 万档 = 商业化产品（5 人小团队 + 双端原生）
50 万档 = 产品级（10+ 人完整团队 + 运维 + 监控）

→ 老板要 50 万档质量但预算只够 5 万档 = 典型"钱不够又要最好"陷阱
→ 正确做法：先选档次，再决定预算
```

详细：[app-quote-breakdown](./app-quote-breakdown/README.md)

---

## 3. 技术选型决策速查（5 维评分）

```text
每项目按 5 维度各打 0-5 分，加权求总分：
  业务匹配度 × 30% + 团队能力 × 25% + 上线时间 × 20%
  + 数据合规 × 15% + 长期 ROI × 10%

总分 ≥ 4 进入候选：
  - 业务匹配 ≥ 4 + 合规严 + 团队能 hold + 长期 ROI 高 → 自研
  - 业务匹配高 + 时间紧 → SaaS
  - 业务匹配高 + 团队能力低 → 外包
```

详细：[self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md)

---

## 4. AI 时代 3 件套

```text
月度 → DORA 4 指标跟踪（速度 + 稳定性）
季度 → DORA + SPACE 5 维度（速度 + 人）
年度 → DORA + SPACE + ROI 三件套全开（+ 业务价值）

DORA 高绩效组（22%）vs 受困组（38%）的差别：
  → 高绩效：DORA + SPACE 都健康
  → 受困：只用 DORA 看速度，没 SPACE 看人
```

详细：[ai-pm-dora-space](./ai-pm-dora-space/README.md)

---

## 5. 排期速算

```text
真实工期 = 估算 × buffer
  buffer = 2.5× （中等项目）
  buffer = 3× （首次 / 复杂 / AI 时代 / 跨团队）
  buffer = 1.5× （成熟项目 / 个人独立）

阿里 2-8-2 人力配比：
  P7 高级 20% + P6 中级 80% + P5 初级 20%
```

详细：[team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md)

---

## 6. 团队拓扑速查

```text
100 人团队标准配比：
  流对齐团队 5-7 个 × 10 人 = 70%
  平台团队 1 个 × 15 人 = 15%
  复杂子系统团队 1 个 × 10 人 = 10%
  促成团队 1-2 个 × 5 人 = 5%（6-12 个月）

平台/业务比 < 10% 瓶颈 / 15-20% 健康 / > 25% 平台侵入
```

详细：[conways-law-team-topologies](./conways-law-team-topologies/README.md)

---

## 7. AI 时代 5 个速查警告

| 警告 | 检查 |
|------|------|
| ⚠️ 用 loc / 人 / 月 度量 AI 效率 | ❌ 作废 |
| ⚠️ DORA 漂亮 = 业务好？ | ❌ 必须同时看 SPACE 满意度 |
| ⚠️ AI Coding "加快 3 倍" → 工期 / 3？ | ❌ review + 测试补回 |
| ⚠️ 团队都用 Cursor → 协作可省？ | ❌ Harness 必须团队共建 |
| ⚠️ SaaS 适合 = 自研不要？ | ❌ 必须过 5 维评分 |

---

## 8. 速查相关的 PM 文件清单

| 文件 | 主题 | 行数 |
|------|------|------|
| [app-quote-breakdown](./app-quote-breakdown/README.md) | 12 大成本维度 | 173 |
| [outsourcing-pitfalls](./outsourcing-pitfalls/README.md) | 5 隐性 + 合同 8 条 | 164 |
| [self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md) | 5 维评分 + TCO 公式 | 290 |
| [ai-pm-dora-space](./ai-pm-dora-space/README.md) | DORA + SPACE + ROI | 340 |
| [team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md) | 阿里 2-8-2 + 排期公式 | 340 |
| [conways-law-team-topologies](./conways-law-team-topologies/README.md) | 康威定律 + 4 类型 | 370 |

---

## 9. 何时该读 PM 模块

- ✅ 评估外包报价 / 风险（老板 / PM）
- ✅ 选自研 / SaaS / 外包（CTO / 技术总监）
- ✅ 看 AI Coding 真实 ROI（研发效能负责人）
- ✅ 调整人力 / 排期（PM / 创业 CTO）
- ✅ 改组织架构（架构师 / CTO）
- ❌ 系统设计技术细节 → 主模块 04.system-design
- ❌ 面试高频陷阱 → 13.split-hairs

---

## 10. 反向索引（找到 PM 主文档的 5 步）

```text
第 1 步：识别"我需要做什么决策"
  ├─ 评估报价 / 选择外包商  → 第 2 步
  └─ 选技术 / 排人力 / 改组织 → 直接看 §1 表格

第 2 步：对照 §1 速查矩阵
  - 找到匹配场景
  - 找到对应主文档链接

第 3 步：阅读"主文档全文"
  - 看 ## 一、核心结论（TL;DR）
  - 看 ## 二/三、具体方法
  - 看 ## 七（文末）"反例 + 避坑"

第 4 步：用 §3-§6 的速查公式实际计算
  - TCO 公式 / 5 维评分 / 排期 buffer / 团队配比

第 5 步：写入自己的方案 / 决策文档
```

---

← [返回项目管理主页](./README.md)
