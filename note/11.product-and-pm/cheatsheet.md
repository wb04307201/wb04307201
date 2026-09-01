<!--
module:
  parent: 11.product-and-pm
  slug: 11.product-and-pm\cheatsheet
  type: article
  category: 主模块子文章
  summary: 项目管理与成本控制 —— 一页速查
  depth: ⭐⭐⭐⭐
-->

# 项目管理与成本控制 —— 一页速查

> 一页纸 PM 决策速查表，涵盖 **报价 / 外包 / 技术选型 / AI 时代账本 / 人力配比 / 团队拓扑** 6 大场景。
> 用法：在拍板时打开本速查 → 对照决策树 → 找到最相关文档 → 深读全文。

← [返回项目管理主页](./README.md)

---

## 6 大场景速查矩阵
| 拍板场景 | 关键决策 | 速查公式 | 主文档 |
|---------|---------|---------|--------|
| **收到 3 家报价** | 价格合理性？ | 12 大成本维度对比 | [app-quote-breakdown](./app-quote-breakdown/README.md) |
| **已签外包** | 隐性风险？ | 5 大隐性成本 + 合同 8 条 | [outsourcing-pitfalls](./outsourcing-pitfalls/README.md) |
| **"自研 / SaaS / 外包"选型** | 三选一怎么决策？ | 5 维评分 + 决策树 + TCO 公式 | [self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md) |
| **AI Coding 买了** | 真的提效？ | DORA 4 + SPACE 5 + ROI 综合 | [ai-pm-dora-space](./ai-pm-dora-space/README.md) |
| **团队要扩人** | 招几个高级？ | 阿里 2-8-2 模型 + 排期 3 倍 | [team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md) |
| **组织架构调整** | 调架构还是调系统？ | 团队拓扑 4 类型 + 康威定律 | [conways-law-team-topologies](./conways-law-team-topologies/README.md) |

---

## 报价速查（3 类方案）
```text
5 万档 = 原型验证 / MVP（学生兼职 + H5 套壳）
20 万档 = 商业化产品（5 人小团队 + 双端原生）
50 万档 = 产品级（10+ 人完整团队 + 运维 + 监控）

→ 老板要 50 万档质量但预算只够 5 万档 = 典型"钱不够又要最好"陷阱
→ 正确做法：先选档次，再决定预算
```

详细：[app-quote-breakdown](./app-quote-breakdown/README.md)

---

## 技术选型决策速查（5 维评分）
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

## AI 时代 3 件套
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

## 排期速算
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

## 团队拓扑速查
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

## AI 时代 5 个速查警告
| 警告 | 检查 |
|------|------|
| ⚠️ 用 loc / 人 / 月 度量 AI 效率 | ❌ 作废 |
| ⚠️ DORA 漂亮 = 业务好？ | ❌ 必须同时看 SPACE 满意度 |
| ⚠️ AI Coding "加快 3 倍" → 工期 / 3？ | ❌ review + 测试补回 |
| ⚠️ 团队都用 Cursor → 协作可省？ | ❌ Harness 必须团队共建 |
| ⚠️ SaaS 适合 = 自研不要？ | ❌ 必须过 5 维评分 |

---

## 速查相关的 PM 文件清单
| 文件 | 主题 | 行数 |
|------|------|------|
| [app-quote-breakdown](./app-quote-breakdown/README.md) | 12 大成本维度 | 173 |
| [outsourcing-pitfalls](./outsourcing-pitfalls/README.md) | 5 隐性 + 合同 8 条 | 164 |
| [self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md) | 5 维评分 + TCO 公式 | 290 |
| [ai-pm-dora-space](./ai-pm-dora-space/README.md) | DORA + SPACE + ROI | 340 |
| [team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md) | 阿里 2-8-2 + 排期公式 | 340 |
| [conways-law-team-topologies](./conways-law-team-topologies/README.md) | 康威定律 + 4 类型 | 370 |

---

## 何时该读 PM 模块
- ✅ 评估外包报价 / 风险（老板 / PM）
- ✅ 选自研 / SaaS / 外包（CTO / 技术总监）
- ✅ 看 AI Coding 真实 ROI（研发效能负责人）
- ✅ 调整人力 / 排期（PM / 创业 CTO）
- ✅ 改组织架构（架构师 / CTO）
- ❌ 系统设计技术细节 → 主模块 04.system-design
- ❌ 面试高频陷阱 → 13.split-hairs

---

## 反向索引（找到 PM 主文档的 5 步）
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

# ─── 以下为「PM 框架速查」扩充部分（L3 → L4 深化） ───

> PM 日常高频用到的 6 大方法论框架（JTBD / RICE / ICE / OKR / HEART / AARRR），
> 全部按"场景 + 公式 + 案例 + 一句话心法"四件套整理，按需打开即可。

---

## 1. JTBD（Jobs To Be Done）—— 用户买的不是产品，是"雇佣"产品完成一件事

**核心思想**（Clayton Christensen, 2016《与运气无关》）：用户不是在买一个产品，而是在**雇佣**这个产品去完成生活中的某件"job"。

```text
经典句式：
  When [情境]，
  I want to [动机]，
  so I can [期望结果]。

经典反例：
  ❌"我们的产品有 50 个功能" → 用户不关心
  ✅"用户在通勤地铁上，要把 30 分钟碎片时间换成一次完整英语听力"
```

### 决策树（何时用 JTBD）

```text
是否在定义"新功能"或"新用户"？
  ├─ 是 → 跳过 JTBD 会死（先想清楚 job 再做产品）
  └─ 否 → 在做运营 / 体验优化 → 仍推荐用 JTBD 重检用户场景
```

### 真实案例

| 公司 | 案例 | JTBD 视角的成功关键 |
|------|------|---------------------|
| **麦当劳奶昔** | Christensen 经典研究 | 早上买奶昔的顾客 job = "通勤时一只手能吃完、不弄脏衣服、填饱到午饭" → 改浓稠 + 加果粒后销量翻倍 |
| **Slack** | 团队协作工具 | job = "在 1000 条邮件 / IM 中找回一条被淹没的关键决策" → 全部 UI 围绕"搜索 + 频道" |
| **抖音** | 短视频产品 | job = "15 秒碎片时间 + 多巴胺刺激 + 不用动脑" → 算法 + 全屏下滑 + 不能暂停设计 |
| **美团外卖** | 高频外卖业务 | job = "懒得做饭 + 想吃现成 + 30 分钟到手" → 30 分钟必达 + 商家 + 骑手三端飞轮 |

### 速查卡片

```text
┌─────────────────────────────────┐
│  JTBD 三件套                     │
│  1. 情境（When/Where）           │
│  2. 动机（Want to ...）          │
│  3. 期望结果（So I can ...）     │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "卖钻孔机的不是用户，           │
│   用户要的是墙上的那个洞"         │
└─────────────────────────────────┘
```

---

## 2. RICE —— 用 4 维评分给需求排优先级（Intercom 2016）

**公式**（Intercom Sean McBride 内部提出）：

```text
RICE Score = (R × I × C × E) / Effort

  R = Reach     触及用户数（每季度 / 月度）
  I = Impact    影响力度（0.25 / 0.5 / 1 / 2 / 3）
  C = Confidence 信心度（0-100%）
  E = Effort    人月工作量
```

### 决策树（何时用 RICE）

```text
候选需求 ≥ 5 个？用户量可量化？单次决策？
  ├─ 是 → 上 RICE 评分表
  └─ 否（战略性 / 探索性）→ 用 ICE 轻量评分

是否需团队共识（≥ 3 个 stakeholder）？
  ├─ 是 → RICE（数据驱动，争议少）
  └─ 否（PM 个人拍板）→ ICE 即可
```

### 真实案例

| 公司 | 场景 | RICE 实操 |
|------|------|-----------|
| **Intercom** | 内部 50+ 候选需求 | RICE 表每周更新，> 100 进入 sprint 候选池 |
| **字节跳动** | 抖音 / TikTok 内部 | Reach = DAU 影响用户数 × Impact = 留存提升 × 0.1% ~ 5% |
| **美团** | 外卖业务线 | Confidence 卡在 80% 以下的需求必须做小流量 A/B 验证 |
| **Notion** | 产品路线图公开 | 用 RICE 决定每季度 Top 3 features，对外发"build with us" |

### 速查卡片

```text
┌─────────────────────────────────┐
│  RICE 速算表                     │
│  R: 月触及用户 ÷ 1000            │
│  I: 巨大 3 / 大 2 / 中 1 / 小 0.5 │
│  C: 高 100% / 中 80% / 低 50%    │
│  E: 人月                        │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "分数高 = 触达广 × 影响大       │
│   × 信心足 ÷ 成本低"             │
└─────────────────────────────────┘
```

---

## 3. ICE —— RICE 的轻量版（PM 个人拍板用，30 秒打分）

**公式**（GrowthHackers 社区，Avinash Kaushik）：

```text
ICE Score = Impact × Confidence × Ease（每个 1-10 分）

  Impact  = 业务影响度（北极星指标提升）
  Confidence = 信心度（数据 / 直觉占比）
  Ease    = 实现难易度（1 = 半年，10 = 1 天）
```

### 决策树（何时用 ICE）

```text
PM 个人决定 / 试错阶段 / 资源紧张？
  ├─ 是 → ICE（30 秒打分）
  └─ 否（团队共识 / 季度规划）→ RICE

候选 ≤ 5 个 + 时间 < 30 分钟？
  └─ ICE 直接拍，不必上 RICE 表格
```

### 真实案例

| 公司 | 场景 | ICE 用法 |
|------|------|----------|
| **增长黑客社区** | Sean Ellis 推广 | 标准打分卡，0-10 分，影响 9 + 信心 7 + 易做 8 = 504 |
| **Dropbox** | 早期增长 | 5 人团队每周 ICE 评分，分数前 3 进入实验 |
| **字节增长团队** | 抖音早期 | ICE 卡 30 分钟完成，决策周期 < 1 天 |
| **阿里淘宝** | 运营活动 | 大促活动排期用 ICE（活动期间 1 周一次） |

### 速查卡片

```text
┌─────────────────────────────────┐
│  ICE 30 秒打分卡                │
│  Impact:    业务影响 1-10        │
│  Confidence: 信心 1-10           │
│  Ease:      容易做 1-10          │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "3 个维度各打 0-10，            │
│   相乘后看谁排第一"               │
└─────────────────────────────────┘
```

---

## 4. OKR —— Objectives & Key Results（目标 + 关键结果）

**核心思想**（Andy Grove《High Output Management》, 1983；John Doerr 引入 Google 1999）：

```text
Objective（目标） = 定性的、激励性的、有时间限制的野心
Key Results（关键结果） = 3-5 个可量化的"做到了吗"

经典错误：
  ❌ OKR = KPI（错！KPI 是日常度量，OKR 是挑战性目标）
  ❌ OKR 100% 完成 = 目标定低了（应 0.6-0.7 完成度最佳）
```

### 决策树（何时用 OKR）

```text
组织规模 > 30 人？需要跨团队对齐？
  ├─ 是 → OKR（季度对齐 + 周 review）
  └─ 否（小组 / 项目）→ 用 Sprint Goal 即可

公司层 / 部门层 / 个人层？
  ├─ 3 层都需对齐 → OKR 树
  └─ 单层 → OKR 单层
```

### 真实案例

| 公司 | 案例 | OKR 关键经验 |
|------|------|-------------|
| **Google** | 1999 引入至今 | OKR 公开透明，全员可见；0.6-0.7 完成度 = 完美 |
| **字节跳动** | 国内全面 OKR | 双月 OKR + 高目标（1/3 概率完成即可） |
| **阿里** | 阿里巴巴 | "一年香三年醇五年陈" + OKR 季度对齐 |
| **小米** | 2014-2018 | OKR + KPI 双轨，关键战役用 OKR，日常用 KPI |
| **美团** | 王兴引入 | "Eat Better, Live Better" 是 O，3 个 KR 各对应一个业务线 |

### 速查卡片

```text
┌─────────────────────────────────┐
│  OKR 写法速查                    │
│  O: 定性 + 野心 + 30 天 / 90 天  │
│  KR: 3-5 个 + 量化 + 可证伪       │
│  评分: 0.0-1.0（0.6-0.7 最佳）   │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "O 是诗，KR 是数字，            │
│   诗 + 数字 = OKR"              │
└─────────────────────────────────┘
```

---

## 5. HEART —— 用户体验的 5 维度度量框架（Google, 2010）

**框架**（Google Kerry Rodden, CHI 2010 论文）：

```text
Happiness    满意度    NPS / CSAT / 情感分析
Engagement   参与度    DAU / MAU / 访问深度
Adoption     接受度    新功能使用率 / 7 日激活率
Retention    留存率    次日 / 7 日 / 30 日留存
Task Success 任务成功率 首次完成率 / 错误率 / 时长
```

### 决策树（何时用 HEART）

```text
要量化用户体验？
  ├─ 是 → HEART（5 维度全量）
  └─ 只看活跃 → 单独 Engagement 即可

是 ToC / 高频产品？
  ├─ 是 → HEART 全用
  └─ ToB / 低频 → Happiness + Task Success 优先
```

### 真实案例

| 公司 | 案例 | HEART 应用重点 |
|------|------|----------------|
| **Google** | 内部全产品用 | HEART + Google Analytics 全打通，每个产品 5 维度必看 |
| **Microsoft** | Office 365 | Task Success + Happiness 优先（ToB 场景） |
| **美团** | 外卖 App | Engagement + Retention + Task Success 三件套（外卖场景高频） |
| **抖音** | 短视频产品 | Engagement（人均时长）+ Happiness（点赞率）+ Retention（次留） |
| **Slack** | 团队协作工具 | Adoption（新功能 7 日激活）+ Engagement（DAU/MAU） |

### 速查卡片

```text
┌─────────────────────────────────┐
│  HEART 5 维度速查                │
│  H: 满意度（情感 / NPS）         │
│  E: 参与度（DAU / 深度）         │
│  A: 接受度（新功能 / 激活）       │
│  R: 留存率（次日 / 7 日 / 30 日） │
│  T: 任务成功（首次 / 时长）       │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "5 维度各打 1 分，              │
│   永远问 5 维度全绿吗？"         │
└─────────────────────────────────┘
```

---

## 6. AARRR —— 海盗指标 / 增长漏斗（Dave McClure, 2007）

**漏斗 5 层**：

```text
Acquisition    获取     流量 / 注册 / 下载
Activation     激活     首次完成 Aha 时刻
Retention      留存     次留 / 7 留 / 30 留
Revenue        收入     付费 / ARPU / LTV
Referral       传播     邀请 / NPS / 自传播
```

### 决策树（何时用 AARRR）

```text
做增长 / 拉新？
  ├─ 是 → AARRR（漏斗看哪一层最薄弱）
  └─ 做留存 / 体验 → HEART 优先

产品处于哪个阶段？
  ├─ 早期（< 1 万 DAU）→ Activation + Retention 优先
  ├─ 成长期（1-100 万）→ Acquisition + Retention 并发
  └─ 成熟期（> 100 万）→ Revenue + Referral
```

### 真实案例

| 公司 | 案例 | AARRR 优化重点 |
|------|------|----------------|
| **Facebook** | 2008-2012 | Activation（7 日加 7 好友）+ Retention（DAU/MAU） |
| **滴滴** | 2014-2016 | Acquisition（补贴）+ Activation（首单）双驱动 |
| **美团外卖** | 早期 | Activation（首单立减）+ Retention（券包周期） |
| **拼多多** | 2017 起飞 | Referral（拼团裂变）+ Acquisition（社交流量） |
| **Slack** | 增长期 | Activation（团队 5 人 + 2000 条消息即留） |
| **Notion** | 内容营销 | Acquisition（YouTube 教程）+ Referral（模板分享） |

### 速查卡片

```text
┌─────────────────────────────────┐
│  AARRR 5 层漏斗速查              │
│  A: 获取（流量来源 / CAC）       │
│  A: 激活（Aha 时刻 / 首次价值）  │
│  R: 留存（次留 / 7 留）          │
│  R: 收入（ARPU / LTV）          │
│  R: 传播（邀请 / NPS）           │
├─────────────────────────────────┤
│  一句话心法：                    │
│  "5 层全打 1 分，                │
│   看哪层跌最多 = 优化点"         │
└─────────────────────────────────┘
```

---

## 6 大框架综合对比（决策树汇总）

```text
场景                  → 用哪个框架？
─────────────────────────────────────────────────
定义新功能 / 新产品   → JTBD（先想清楚 job）
需求池 ≥ 10 个 / 季度 → RICE（团队共识）
个人决策 / 探索性     → ICE（30 秒拍板）
公司层目标对齐        → OKR（季度联动）
量化用户体验          → HEART（5 维度）
增长 / 漏斗优化       → AARRR（5 层漏斗）
```

---

## 6 框架 × 5 行业 × 真实案例矩阵（总览）

| 框架 \\ 行业 | ToC 电商 | ToC 内容 | ToB SaaS | 工具产品 | 平台型 |
|--------------|---------|---------|---------|---------|--------|
| **JTBD**     | 美团外卖 | 抖音     | Slack   | Notion  | 阿里电商 |
| **RICE**     | 京东     | B 站     | 飞书    | Cursor  | 拼多多 |
| **ICE**      | 早期淘宝 | 早期抖音 | 早期 Slack | 早期 Notion | 早期美团 |
| **OKR**      | 阿里     | 字节跳动 | 微软    | GitHub  | Google |
| **HEART**    | 美团 | 抖音 | Microsoft Office | Slack | Facebook |
| **AARRR**    | 滴滴     | 拼多多   | Slack   | Notion  | Facebook |

---

## PM 6 框架常见陷阱（反面教材）

| 陷阱 | 反例 | 正确做法 |
|------|------|---------|
| ❌ 用 OKR 替代 KPI | 把"日活 100 万"当 KR → 失激励性 | OKR 应挑战性（0.6-0.7 完成） |
| ❌ JTBD 写"产品功能" | "我要做拍照" → 不是 job | "我要留住此刻给未来看" |
| ❌ RICE 不校 Confidence | 信心打分全 100% | 卡 80% 阈值，必做小流量验证 |
| ❌ ICE 全打 10 分 | 没区分度 → 等于没打 | 强制 3 维度各有高低 |
| ❌ HEART 用错产品阶段 | ToB 用 Engagement 优先 | ToB 优先 Task Success + Happiness |
| ❌ AARRR 漏斗全压平 | 5 层都砸钱 → 烧光预算 | 单点突破，找到最薄弱层 |

---

## 何时该用哪个框架（1 分钟决策）

```text
你是？
  ├─ 老板 / CEO         → OKR（公司层）+ JTBD（方向）
  ├─ PM / 产品经理      → RICE（季度）+ ICE（周）+ HEART（度量）
  ├─ 增长 / 运营        → AARRR（漏斗）+ ICE（实验）
  ├─ 用户研究 / UX      → JTBD（定性）+ HEART（定量）
  └─ 创业者 / 全栈      → 6 框架都学，但 JTBD + ICE 是日用
```

---

## 相关章节（11 模块内）

- [app-quote-breakdown](./app-quote-breakdown/README.md) — 报价 + 6 框架无直接关系，但 JTBD 决定"做什么功能"后才有报价
- [outsourcing-pitfalls](./outsourcing-pitfalls/README.md) — 外包决策可用 RICE 评分（自研 / SaaS / 外包三选一）
- [self-vs-saas-vs-outsourcing](./self-vs-saas-vs-outsourcing/README.md) — 自研 / SaaS 决策本身是 5 维评分（类似 RICE 思路）
- [ai-pm-dora-space](./ai-pm-dora-space/README.md) — DORA + SPACE 是 HEART 的工程维度子集
- [team-sizing-3x-buffer](./team-sizing-3x-buffer/README.md) — 排期估算用于 RICE 的 Effort 维度
- [conways-law-team-topologies](./conways-law-team-topologies/README.md) — 团队拓扑决定 OKR 的对齐颗粒度
- [interviewing-cross-disciplinary](./interviewing-cross-disciplinary/README.md) — 面试中评估候选人的 PM 框架思维
- [risk-register](./risk-register/README.md) — RICE + MoSCoW 是风险登记 + 优先级组合

---

← [返回项目管理主页](./README.md)

> 📅 2026-09-01 · 咬文嚼字 · PM 框架速查 + 决策工具 · ⭐⭐⭐⭐（实战必会）