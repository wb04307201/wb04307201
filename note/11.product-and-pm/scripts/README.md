<!--module:
  parent: 11.product-and-pm
  slug: 11.product-and-pm/scripts
  type: article
  category: 工具脚本
  summary: PM 实战脚本手册（5 大场景 SQL/邮件/评审模板）+ 项目维护 Python 工具
  depth: ⭐⭐⭐⭐
-->

# PM 实战脚本手册

> PM 日常高频 5 大场景（需求收集 / 优先级排序 / 数据分析 / A/B 测试 / 复盘）的**可复用模板 + SQL + 邮件 + 评审检查表**。
> 配套维护本模块的 Python 脚本（`insert-frontmatter.py` / `validate.py`）。

← [返回 11.product-and-pm 总目录](../README.md) · SPEC.md

---

## 一、脚本手册总览

| 场景 | 模板类型 | 速查位置 |
|------|---------|---------|
| **需求收集** | 用户访谈 / 问卷 / 调研表 | § 2 |
| **优先级排序** | RICE 评分表 / MoSCoW 卡 | § 3 |
| **数据分析** | SQL 模板（漏斗 / 留存 / 分布） | § 4 |
| **A/B 测试** | 实验设计 / 显著性检验 | § 5 |
| **复盘** | 邮件模板 / 评审检查表 | § 6 |

---

## 二、需求收集 —— 5 件套模板

### 2.1 用户访谈提纲（30 分钟版）

```text
□ 1. 热身（3 分钟）：自我介绍 + "今天聊些您日常怎么用 [产品类目]"
□ 2. 行为回溯（10 分钟）：
   - 上一次用 [产品] 是什么时候？什么场景？解决什么问题？
   - 完成了吗？耗时多久？
□ 3. 痛点深挖（10 分钟）：
   - 中间卡在哪里？最不满意的 1 件事是什么？
   - 试过哪些替代方案？为什么不用了？
□ 4. 价值量化（5 分钟）：
   - 如果解决这个痛点，能为您省多少时间/钱？
□ 5. 收尾（2 分钟）：
   - 还有什么我们没问到？
   - 能介绍 1 个朋友一起聊吗？
```

**真实案例 — 字节跳动用户研究**：
字节要求每场访谈必走"行为回溯"环节，禁止直接问"您觉得这个功能怎么样"——用户在抽象层会撒谎，在具体场景下才能讲真话。

### 2.2 需求调研问卷（定量 3 层结构）

```text
L1 人口学（30 秒）：
  - 年龄段 / 职业 / 城市级别 / 使用产品频率

L2 行为（5 分钟）：
  - 上一次使用场景？触发原因？
  - 完成路径有几个步骤？
  - 替代方案用过哪些？

L3 态度（5 分钟，5 级量表）：
  - [场景 1] 满意度 1-5
  - [痛点 1] 痛苦度 1-5
  - NPS 推荐值 0-10
```

### 2.3 PRD 模板（11 类必填项）

```text
1. 需求背景：为什么做？数据依据？
2. 用户故事：作为 [persona]，想 [action]，以便 [benefit]
3. 范围 (In Scope)：必做 3-5 个
4. 非目标 (Out of Scope)：明确不做 3-5 个（防 scope creep）
5. 验收标准：可量化、必过；测试用例
6. 依赖：上游 / 下游 / 第三方
7. 风险：技术 / 业务 / 合规
8. 埋点：用户行为 + 业务指标 + 异常埋点
9. 灰度方案：1% / 5% / 20% / 100% 节奏
10. 回滚方案：触发条件 + 操作步骤
11. 上线 Checklist：性能 / 安全 / 监控 / 文档
```

**真实案例 — 美团外卖 PRD 必填项**：美团 PRD 模板里有 1 项"用户场景模拟"，要求 PM 必须写真实的"用户晚上 10 点加班回家"场景，避免纸上谈兵。

### 2.4 需求评审会议议程（60 分钟版）

```text
0-10  分钟：背景 + 数据 + 业务价值
10-30 分钟：方案 walkthrough（设计 + 交互 + 后端）
30-45 分钟：质疑与挑战（每个 stakeholder 必发言）
45-55 分钟：决策（GO / NO-GO / 改方案）
55-60 分钟：Action item + 责任人 + 时间
```

### 2.5 客户开发访谈（CustDev，Y Combinator 方法）

```text
核心问题（避免引导性提问）：
  ❌"您会买我们的产品吗？"（人人说会，0 信号）
  ✅"上一次为这类问题付费是什么时候？付了多少？"（真实信号）

判别信号：
  - 解决方案描述清晰（5 分钟内讲完）= 真痛点
  - 描述含糊（10 分钟说不清）= 伪痛点
```

**真实案例 — Dropbox 早期 CustDev**：Drew Houston 在 2007 用 CusDev 法访谈 200+ 用户，确认"多设备同步文件"是真痛点后才做 Dropbox。

---

## 三、优先级排序 —— 4 套评分卡

### 3.1 RICE 评分卡（Intercom 模板）

```text
需求名称：_________________________
PM：_________
日期：_________

R (Reach)：每季度触及用户数
  估算依据：DAU × 该功能曝光率
  分数：_________ (用户数)

I (Impact)：影响力度
  □ 3.0 巨大影响（核心指标提升 ≥ 10%）
  □ 2.0 大影响（5-10%）
  □ 1.0 中影响（1-5%）
  □ 0.5 小影响（0.1-1%）
  □ 0.25 极小影响
  分数：_________

C (Confidence)：信心度
  □ 100% 高（有数据 + 案例）
  □ 80%  中（有数据无案例）
  □ 50%  低（仅假设）
  分数：_________ (%)

E (Effort)：工作量
  人月估算：_________
  分数：_________

RICE Score = (R × I × C) / E
  分数：_________
```

### 3.2 ICE 轻量评分卡（个人用，30 秒）

```text
需求名称：_________________________

I (Impact)   [1-10]：_________
C (Confidence)[1-10]：_________
E (Ease)     [1-10]：_________

ICE Score = I × C × E = _________
```

### 3.3 MoSCoW 分类卡（必做 / 应做 / 可做 / 不做）

```text
需求名称：_________________________

□ Must have     必做（无此功能产品不能上线）
□ Should have   应做（重要但可 MVP 推迟）
□ Could have    可做（有资源才做）
□ Won't have    不做（明确不做，防 scope creep）

理由：_________________________________
```

### 3.4 决策矩阵（多 stakeholder 共识）

```text
加权评分 = Σ(维度 × 权重)
  维度                权重  分数(1-10)  加权
  业务价值              30%   ___       ___
  用户影响              25%   ___       ___
  实现成本（倒置）      20%   ___       ___
  风险（倒置）          15%   ___       ___
  合规性                10%   ___       ___
  ─────────────────────────────
  总分                              ___/10
```

**真实案例 — 阿里战略决策矩阵**：阿里在内部"三板斧"决策中用类似矩阵，业务价值 + 用户影响 + 战略匹配度 ≥ 80% 才进入资源池。

---

## 四、数据分析 —— 5 大 SQL 模板

### 4.1 日活 / 月度活跃（DAU / MAU）模板

```sql
-- DAU / MAU（MySQL 8.0+）
SELECT
    DATE(login_time) AS dt,
    COUNT(DISTINCT user_id) AS dau,
    COUNT(DISTINCT user_id) / 
      (SELECT COUNT(DISTINCT user_id) 
       FROM login_log 
       WHERE login_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) AS dau_ma_ratio
FROM login_log
WHERE login_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(login_time)
ORDER BY dt DESC;
```

**业务判读**：
- DAU/MAU ≥ 20% = 高粘性（健康）
- 10-20% = 警告（需优化）
- < 10% = 低粘性（需重设计产品）

### 4.2 留存率模板（次日 / 7 日 / 30 日）

```sql
-- 次日 / 7 日 / 30 日留存
WITH cohort AS (
    SELECT 
        user_id,
        DATE(MIN(login_time)) AS cohort_date
    FROM login_log
    GROUP BY user_id
),
activity AS (
    SELECT DISTINCT
        c.cohort_date,
        a.user_id,
        DATEDIFF(DATE(a.login_time), c.cohort_date) AS day_offset
    FROM login_log a
    JOIN cohort c ON a.user_id = c.user_id
)
SELECT
    cohort_date,
    COUNT(DISTINCT IF(day_offset = 0, user_id, NULL)) AS d0,
    COUNT(DISTINCT IF(day_offset = 1, user_id, NULL)) AS d1,
    COUNT(DISTINCT IF(day_offset = 7, user_id, NULL)) AS d7,
    COUNT(DISTINCT IF(day_offset = 30, user_id, NULL)) AS d30,
    ROUND(COUNT(DISTINCT IF(day_offset = 1, user_id, NULL)) * 100.0 / 
          COUNT(DISTINCT IF(day_offset = 0, user_id, NULL)), 2) AS d1_rate,
    ROUND(COUNT(DISTINCT IF(day_offset = 7, user_id, NULL)) * 100.0 / 
          COUNT(DISTINCT IF(day_offset = 0, user_id, NULL)), 2) AS d7_rate
FROM activity
GROUP BY cohort_date
ORDER BY cohort_date DESC;
```

**业务判读（业界基准）**：
- 次日留存 ≥ 40% 优秀，30-40% 良好，< 30% 需诊断
- 7 日留存 ≥ 20% 优秀，10-20% 良好
- 30 日留存 ≥ 10% 优秀

### 4.3 漏斗转化模板（AARRR）

```sql
-- 5 层漏斗：注册 → 激活 → 留存 → 付费 → 传播
WITH funnel AS (
    SELECT
        COUNT(DISTINCT user_id) AS registered,
        COUNT(DISTINCT CASE WHEN activated_at IS NOT NULL THEN user_id END) AS activated,
        COUNT(DISTINCT CASE WHEN retained_at IS NOT NULL THEN user_id END) AS retained,
        COUNT(DISTINCT CASE WHEN paid_at IS NOT NULL THEN user_id END) AS paid,
        COUNT(DISTINCT CASE WHEN referred_user_id IS NOT NULL THEN user_id END) AS referred
    FROM user_funnel
    WHERE registered_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
SELECT '注册' AS step, registered AS users, 100.0 AS conversion_pct FROM funnel
UNION ALL
SELECT '激活', activated, ROUND(activated * 100.0 / registered, 2) FROM funnel
UNION ALL
SELECT '留存', retained, ROUND(retained * 100.0 / registered, 2) FROM funnel
UNION ALL
SELECT '付费', paid, ROUND(paid * 100.0 / registered, 2) FROM funnel
UNION ALL
SELECT '传播', referred, ROUND(referred * 100.0 / registered, 2) FROM funnel;
```

### 4.4 分布分析模板（用户行为时长）

```sql
-- 用户停留时长分布（P50 / P90 / P99）
WITH duration AS (
    SELECT
        user_id,
        TIMESTAMPDIFF(SECOND, MIN(event_time), MAX(event_time)) AS session_seconds
    FROM events
    WHERE event_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    GROUP BY user_id, DATE(event_time)
)
SELECT
    'P50' AS percentile, 
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY session_seconds), 0) AS seconds
FROM duration
UNION ALL
SELECT 'P90', ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY session_seconds), 0) FROM duration
UNION ALL
SELECT 'P99', ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY session_seconds), 0) FROM duration;
```

### 4.5 用户分群模板（RFM）

```sql
-- RFM 模型（最近购买 / 频次 / 金额）
WITH rfm AS (
    SELECT
        user_id,
        DATEDIFF(CURDATE(), MAX(order_time)) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(order_amount) AS monetary
    FROM orders
    WHERE order_time >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
    GROUP BY user_id
)
SELECT
    user_id,
    recency_days,
    frequency,
    monetary,
    CASE
        WHEN recency_days <= 30 AND frequency >= 10 AND monetary >= 5000 THEN '高价值客户'
        WHEN recency_days <= 90 AND frequency >= 5 THEN '潜力客户'
        WHEN recency_days > 180 THEN '流失客户'
        ELSE '普通客户'
    END AS segment
FROM rfm
ORDER BY monetary DESC;
```

**真实案例 — 阿里 RFM 分群**：阿里在 2008-2012 用 RFM 把用户分 8 群，对高价值客户做 VIP 运营，对流失客户做召回活动，ROI 提升 3-5 倍。

---

## 五、A/B 测试 —— 实验设计 + 显著性检验

### 5.1 实验设计模板（必填 7 项）

```text
1. 假设（Hypothesis）：
   H0（原假设）：新方案与基线转化率无显著差异
   H1（备择假设）：新方案转化率 > 基线转化率 5%

3. 指标：
   - 主指标：转化率（订单/UV）
   - 护栏指标：GMV / 退货率 / 客诉率
   - 反向指标：误操作率 / 流失率

4. 样本量：
   - 基线转化率 p0 = 5%
   - 最小可检测差异 MDE = 0.5%（提升 10%）
   - α = 0.05, β = 0.2（检验功效 80%）
   - 样本量计算：n ≈ 16,000 / 组（共 32,000）

5. 分流：
   - 用户 ID 取模 100 哈希分流
   - 实验组 50%，对照组 50%

6. 时长：
   - 至少 1 个完整周期（7 天，覆盖工作日 + 周末）
   - 最大不超过 14 天（防新变量干扰）

7. 决策门槛：
   - p-value < 0.05 才算显著
   - 提升 ≥ MDE 才算业务显著
```

### 5.2 显著性检验 SQL 模板

```sql
-- 两比例 Z 检验
WITH ab_data AS (
    SELECT
        variant,
        COUNT(*) AS total_users,
        SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) AS converted_users
    FROM ab_test_results
    WHERE experiment_id = 'exp_2026_09_button_color'
    GROUP BY variant
)
SELECT
    a.variant AS test_variant,
    a.converted_users / a.total_users AS test_rate,
    b.converted_users / b.total_users AS control_rate,
    (a.converted_users / a.total_users - b.converted_users / b.total_users) AS lift,
    -- Z 统计量
    (
        (a.converted_users / a.total_users - b.converted_users / b.total_users) /
        SQRT(
            (a.converted_users + b.converted_users) / (a.total_users + b.total_users) *
            (1 - (a.converted_users + b.converted_users) / (a.total_users + b.total_users)) *
            (1/a.total_users + 1/b.total_users)
        )
    ) AS z_score
FROM ab_data a, ab_data b
WHERE a.variant = 'treatment' AND b.variant = 'control';
```

**决策判读**：
- |Z| ≥ 1.96 = p < 0.05（双尾）
- Z ≥ 1.645 = p < 0.05（单尾，看正向上）
- Z ≥ 2.576 = p < 0.01（强显著）

### 5.3 A/B 测试常见反模式（避坑）

```text
❌ 反模式 1：边看边停（peeking）
   → 每天跑一次，看到 p < 0.05 就停 → 假阳性率放大 5-10 倍
   ✅ 正确：定好样本量，到点一次性看

❌ 反模式 2：多重比较
   → 同时测 10 个指标，1 个显著就宣布成功 → 假阳性率 40%
   ✅ 正确：明确 1 个主指标，其他只看不判

❌ 反模式 3：流量倾斜
   → 实验组 90% 流量，对照组 10% → 实验组绝对值大但不显著
   ✅ 正确：50/50 平分

❌ 反模式 4：SRM（Sample Ratio Mismatch）
   → 分流后两组样本数偏离 50/50 → 实验无效
   ✅ 正确：开箱即查 SRM（χ² 检验）

❌ 反模式 5：新颖性效应
   → 新功能上线第 1 周数据好，第 4 周回归基线
   ✅ 正确：实验时长 ≥ 2 周
```

**真实案例 — Booking.com 严格测试**：Booking.com 每年跑 1000+ A/B 测试，"peeking" 是大忌，所有测试必须按预定样本量跑完才能开箱。

---

## 六、复盘 —— 邮件模板 + 评审检查表

### 6.1 项目复盘邮件模板

```text
Subject: [项目名] 复盘 - 2026-09-XX

各位好，

[项目名] 于 2026-XX-XX 上线，已稳定运行 1 个月。今天做一次完整复盘。

────────────────────────────────────
1. 项目结果（vs 目标）

  目标 1：DAU 提升 10%        实际：+ 12%  ✅
  目标 2：转化率提升 5%        实际：+ 3%   ⚠️（未达）
  目标 3：客诉率 < 0.5%        实际：0.3%   ✅

────────────────────────────────────
2. 关键决策回顾

  - 决策 1：[如"砍掉 X 功能"] → 结果：[节省 2 周]
  - 决策 2：[如"用 Y 方案替代 Z"] → 结果：[性能提升 30%]

────────────────────────────────────
3. 做对了什么（Keep）

  - ...
  - ...

────────────────────────────────────
4. 做错了什么（Drop）

  - ...
  - ...

────────────────────────────────────
5. 下次改进（Try）

  - ...
  - ...

────────────────────────────────────
附件：
  - 数据看板链接
  - 原 PRD
  - 测试报告

复盘会议：2026-09-XX 14:00 会议室 A
邀请：[相关 stakeholder]

Best,
[PM 名字]
```

### 6.2 Sprint 评审检查表（迭代前 + 评审中）

```text
迭代前 5 项检查：
  □ 1. PRD 是否齐全（11 类必填项）
  □ 2. UI 设计稿是否定稿
  □ 3. 后端接口文档是否评审
  □ 4. 埋点是否对齐（业务 + 行为 + 异常）
  □ 5. 灰度方案是否明确（比例 + 触发 + 回滚）

评审中 5 项检查：
  □ 6. 每个 stakeholder 必发言（产品 / 设计 / 研发 / 测试 / 运营 / 法务）
  □ 7. 主指标 vs 护栏指标 vs 反向指标是否明确
  □ 8. 依赖项是否识别完整
  □ 9. 风险登记册是否更新
  □ 10. Action item 必填（责任人 + 日期 + 优先级）

上线前 5 项检查：
  □ 11. 监控 / 告警是否配齐
  □ 12. 数据看板是否就绪
  □ 13. 客服 / 运营培训是否完成
  □ 14. 用户告知（公告 / 邮件 / 弹窗）
  □ 15. 回滚脚本演练是否通过
```

### 6.3 KPT 复盘模板（Keep / Problem / Try）

```text
日期：_________
项目：_________
参与者：_________

KEEP（做对了什么）：
  1. ________________________________
  2. ________________________________
  3. ________________________________

PROBLEM（做错了什么）：
  1. ________________________________
  2. ________________________________
  3. ________________________________

TRY（下次怎么做）：
  1. ________________________________
  2. ________________________________
  3. ________________________________
```

**真实案例 — 字节跳动 KPT 标准化**：字节内部 KPT 模板强制"3 + 3 + 3"（每个维度至少 3 条），防止走过场。

### 6.4 事故复盘模板（Post-Mortem，无指责版）

```text
1. 事故概述
   - 时间：2026-XX-XX 14:00-16:00（2 小时）
   - 影响：X 万用户受影响 / GMV 损失 Y 万
   - 级别：P0 / P1 / P2

2. 时间线（Timeline）
   14:00  服务告警
   14:05  oncall 收到通知
   14:15  初步定位：DB 连接池满
   14:30  启动应急方案
   15:00  部分用户恢复
   16:00  全量恢复

3. 根因分析（5 Why）
   Why 1：DB 连接池满 → Why 2：慢查询堆积 → Why 3：缺少索引
   → Why 4：新增字段无索引 → Why 5：未走 SQL Review

4. 改进措施
   - 短期（24 小时内）：回滚 / 限流 / 监控
   - 中期（1 周）：补索引 / SQL Review 流程
   - 长期（1 月）：自动化 SQL Review 工具

5. 责任与流程
   - 责任人：[执行人]
   - 不指责（Blame-free）：个人不背锅，流程优化优先
```

**真实案例 — Google SRE Post-Mortem 文化**：Google 强制所有事故必须 5 工作日内出 Post-Mortem 文档，**严禁直接归咎个人**，重点是"系统为什么允许这个错误发生"。

### 6.5 OKR 季度复盘模板

```text
季度：_________
部门：_________

O（目标）：____________________________
完成度评分：______ / 1.0

KR1：____________________________  完成度：______ / 1.0
  数据：______
  原因：______
KR2：____________________________  完成度：______ / 1.0
  数据：______
  原因：______
KR3：____________________________  完成度：______ / 1.0
  数据：______
  原因：______

下季度 Carry-over（遗留）：
  - ____________

下季度新增：
  - ____________
```

---

## 七、PM 实战工具集总结

| 场景 | 推荐工具 | 模板 / SQL / 邮件 |
|------|----------|-----------------|
| 需求收集 | 访谈提纲 + PRD 模板 | § 2.1, § 2.3 |
| 优先级排序 | RICE + MoSCoW + 决策矩阵 | § 3.1, § 3.3, § 3.4 |
| 数据分析 | SQL（漏斗 / 留存 / RFM） | § 4.1, § 4.2, § 4.3, § 4.5 |
| A/B 测试 | 实验设计 + Z 检验 | § 5.1, § 5.2 |
| 复盘 | 邮件 + KPT + Post-Mortem | § 6.1, § 6.3, § 6.4 |

---

# ─── 以下为「项目维护 Python 工具」原内容 ───

> 本目录还包含 2 个 Python 工具脚本，用于批量维护 `note/11.product-and-pm/` 下的所有 Markdown 文章。

---

## 脚本清单

### 1. `insert-frontmatter.py` — 批量插入 frontmatter

**用途**：给 `note/11.product-and-pm/**/*.md` 中缺 frontmatter 的文件批量插入 `pm:` 模块的 frontmatter 模板（含 `topic` / `audience` / `category` / `summary` 4 个字段）。

**调用方法**：

```bash
# 在项目根目录
python note/11.product-and-pm/scripts/insert-frontmatter.py

# Dry-run（只报告不修改）
python note/11.product-and-pm/scripts/insert-frontmatter.py --dry-run
```

**适用场景**：
- 新建 11.product-and-pm 子模块后批量补 frontmatter
- SPEC.md 升级规范时迁移旧 frontmatter

### 2. `validate.py` — 校验合规性

**用途**：检查 `note/11.product-and-pm/**/*.md` 是否符合 11.product-and-pm 写作规范（详见 [`../SPEC.md`](../SPEC.md)）。

**校验项**：
1. ✓ frontmatter 注释块（`pm:` + `topic` / `audience` / `summary` 字段）
2. ✓ `## 引言` 段（场景开篇）
3. ✓ 文末回链到 `README.md`
4. ✓ 文章行数 ≥ 50
5. ✓ 中文数字章节编号（自动跳过 fenced code block）

**调用方法**：

```bash
python note/11.product-and-pm/scripts/validate.py
```

**退出码**：0 = 全部合规；1 = 存在不合规项。

---

## 维护约定

- 脚本无外部依赖（仅 Python 3.8+ 标准库），可独立运行
- 修改脚本后请同步测试 `note/11.product-and-pm/` 至少 1 个 leaf README
- 重大变更请更新本 README

---

## 相关章节（11 模块内）

- [AI 项目管理账本：DORA + SPACE + ROI 三件套](../ai-pm-dora-space/README.md)
- [人力配比 + 排期估算：3 倍缓冲原则](../team-sizing-3x-buffer/README.md)
- [5万 vs 50万 App 报价差在哪：12 大成本维度拆解](../app-quote-breakdown/README.md)
- [技术选型 ROI：自研 vs SaaS vs 外包](../self-vs-saas-vs-outsourcing/README.md)
- [项目风险登记册：MoSCoW + RICE 实战](../risk-register/README.md)
- [敏捷度量实战：Velocity / Cycle Time / CFD](../agile-metrics/README.md)

← [返回: 项目管理](../README.md)

> 📅 2026-09-01 · 咬文嚼字 · PM 实战脚本 + 维护工具 · ⭐⭐⭐⭐（实战必会）