# 5-dim difficulty 校准流程（Phase 6 长期流程）

> **目的**：长期维护 frontmatter `difficulty:` 字段与 5 维评分（E7-E11）的校准一致性
> **触发频率**：建议季度一次（每年 4 次）+ 新模块/大批量内容沉淀后触发
> **来源**：本流程从 2026-08-31 / 2026-09-01 两轮抽样验证沉淀（48 篇 v1 + 49 篇 v2 = 97 篇评估数据）

## 1. 为什么需要校准

**历史教训**（来自 48+49 篇抽样）：
- **62.5% frontmatter difficulty 与实际内容深度不匹配**（v1 数据）
- **agent 间主观性差异显著**：同一文件 v1 vs v2 评分可能偏差 1-2 分（如 concurrency-vs-parallelism、boosting-comparison）
- **v1 agent 评分宽松**：10.big-data 100% 满分 10/10，过度推荐 5 星升级
- **v2 严格审计后撤回 4 处过度升级**（flink/hive/doris 5→4，agent-memory-classification 5→4）

**核心矛盾**：frontmatter `difficulty`（⭐ 数量）是主观维护的，与正文实际深度可能脱节。

## 2. 5 维评分标准（E7-E11）

每个维度 0-2 分，总分 0-10：

| 维度 | 2 分 | 1 分 | 0 分 |
|------|------|------|------|
| **D1 知识深度（depth）** | 源码级 + JVM/字节码/引擎 + 版本演进对比 | 讲解原理（不到源码）| 概念定义 / 语法层 |
| **D2 知识广度（breadth）** | 3+ 跨主模块联动 | 1-2 个相关概念联动 | 单一概念无关联 |
| **D3 面试频次（frequency）** | 高频（90% 候选人都会被问）| 中频（2-4 年经验）| 冷门（特定公司才问）|
| **D4 追问空间（followup）** | 可追 5+ 层完整知识图 | 可追 2-3 层 | 一句话答完，无追问 |
| **D5 反直觉/陷阱（trap）** | 3+ 反直觉陷阱 / 生产事故案例 | 1-2 个常见错误 | 直接定义无陷阱 |

## 3. 星级映射（structural-checks.md §15）

```
9-10 → ⭐⭐⭐⭐（4 星）
7-8  → ⭐⭐⭐（3 星）
5-6  → ⭐⭐（2 星）
≤4   → ⭐（1 星，迁出候选）
⭐⭐⭐⭐⭐（5 星）是人工保留档，需五维 ≥ 9 才合理
```

**关键规则**：
- **5 星门槛 = 五维 ≥ 9**（不只是总分）
- **D1 必须 ≥ 1**：源码级深度是 5 星的硬性条件
- **D5 必须 ≥ 1**：≥3 个反直觉陷阱是 5 星的硬性条件
- **⭐⭐⭐⭐⭐ 自动升级需谨慎**：必须 Read 全文 + footer 交叉验证

## 4. 校准流程（季度执行）

### 步骤 1：生成抽样清单

```bash
# 用 v2 脚本生成 12.interview 各 subdir 的分层抽样
python note/.health-tmp/sample-files-v2.py
```

输出：
- `sample-files-v2.json`（主清单）
- `consensus-files.json`（双副本共识批次）
- `batch-{subdir}.txt`（10 个 subdir 批次）

**v2 关键改进**：
- 用 `os.walk` 而非硬编码路径（解决题目迁出 / 重命名失效）
- 按 `(subdir, difficulty)` 单元格分层抽样
- 同文件评分 2 次取均值（共识机制）

### 步骤 2：Dispatch 并行 subagent（v2 共识）

为每个 subdir 派 1 个 subagent（或 2 个做双副本共识）：

```python
# Agent prompt 关键要求（参考 2026-09-01 v2 prompt）
- 必须 Read 全文（不要只看文件名）
- 评分锚定 batch baseline 难度（避免宽松）
- 与 v1 上轮评分偏差 ≥2 时降 1 分取保守值
- 5 星保留档审计：D1=1 或 D5=1 时降 ⭐⭐⭐⭐
```

### 步骤 3：人工抽查高偏差文件

- **偏差 ≥ 2 的文件**：必须 Read 全文人工确认
- **⭐⭐⭐⭐⭐ 保留档**：所有 5 星文件必须人工 Read footer + 正文 ⭐ 标注交叉验证
- **frontmatter 与 footer 不一致**：以 footer 为准（footer 是作者自觉评级）

### 步骤 4：批量提交校准 commit

```bash
# 应用校准（每批一条 commit）
git add note/12.interview/
git commit -m "fix(12.interview): N 处 difficulty 深度校准（5-dim 评分抽样结果）

依据 Phase 2 5 维评分抽样验证：

升级：
- file1: ⭐⭐ → ⭐⭐⭐（D1=1 + D5=2，9 分）
- file2: ⭐⭐⭐ → ⭐⭐⭐⭐（D1=2 + D2=2 + D5=2，10 分）

降级：
- file3: ⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐（5 维仅 9 分但 D1=1，未达保留档严格标准）

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

### 步骤 5：报告产出

```bash
# 写 .health-tmp/difficulty-calibration-{date}.md（gitignored）
```

报告应包含：
- 全局偏差统计（一致 / 低估 / 高估）
- 各 subdir 偏差分布
- 保留档审计结果
- 与上轮 v1 对比（识别 agent 间主观性差异）
- 5 星降级清单（如有）

## 5. 常见陷阱（2026-09-01 历史教训）

### ❌ 陷阱 1：仅依据 v1 agent 评分升级

**症状**：10.big-data 6/6 满分 10/10 → 4 处 4→5 升级

**修复**：v2 严格审计撤回 3 处（flink/hive/doris），仅 iceberg-acid 保留 5 星

### ❌ 陷阱 2：忽视 footer 自评级

**症状**：flink-checkpoint-vs-savepoint footer 标 ⭐⭐⭐⭐，frontmatter 升级到 ⭐⭐⭐⭐⭐

**修复**：以 footer 为准的交叉验证机制

### ❌ 陷阱 3：5 星门槛只看总分不看维度

**症状**：agent-memory-classification 5 维 9 分（D1=1）升级 5 星

**修复**：D1 ≥ 1 是 5 星硬性条件

### ❌ 陷阱 4：抽样清单硬编码导致路径失效

**症状**：v1 抽样 6 篇路径不存在（css-vertical-center / cap-theorem 等已迁出）

**修复**：v2 用 `os.walk` 动态生成

## 6. 触发条件清单

| 触发场景 | 频率 | 关键文件 |
|----------|------|---------|
| 季度体检 | 每 3 月 | `note/.health-tmp/sample-files-v2.py` + 10 agent dispatch |
| 新模块首次沉淀 | 一次性 | 全模块抽样 |
| 批量内容深化（>10 篇源码级扩展）| 1 周内 | 该模块专项抽样 |
| 用户反馈"难度不准" | 立即 | 单模块抽样 |
| 5 星保留档文件变动 | 立即 | 单文件人工审核 |

## 7. 与其他 Phase 的关系

```
Phase 1（结构扫描）  → 发现 frontmatter 缺失 / 异常
Phase 2（5-dim 评分） → E7-E11 内容深度打分
Phase 3（roll-up）    → 模块级 difficulty 分布
Phase 6（5-dim 校准） → 本流程：frontmatter 与 5-dim 一致性
Phase 7（拆分检测）   → 检测 ⭐（1 星）迁出候选
```

## 8. 与 skills/note-health 的集成

- **入口**：用户问"难度校准" / "difficulty 不准" / "⭐ 不对" 时触发
- **复用 Phase 1-7 的扫描框架**：不重新发明轮子
- **报告格式**：参考 `note/.health-tmp/five-dim-calibration-54.md`（v1 报告模板）
- **数据持久化**：`.health-tmp/calibration-history.json`（按季度记录）
