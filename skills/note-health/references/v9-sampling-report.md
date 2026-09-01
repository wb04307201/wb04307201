# v9 抽样验证报告（2026-09-01）

> **目的**：验证 v8 校准 + L5 标准 2.0 微调后准确度
> **方法**：80 篇大样本抽样（70% 已校准 + 30% 未评估）
> **关键发现**：准确度 **38.75%**（31/80 完全一致），比 v8 的 49% 下降 -10pp

## 评分明细（80 篇）

### 完全一致（31 篇，38.75%）

完整清单：包括 09.ai-applications 主题 7 篇、02.cs-foundations 4 篇、10.business-systems 4 篇、05.frontend 2 篇、06.distributed-systems 4 篇等。

### 低估（24 篇）

详见 commit `6fb0b122`（v9 calibrations）。升级 24 篇。

### 高估（25 篇）

详见 commit `6fb0b122`（v9 calibrations）。降级 19 篇（其余 4 篇因路径错误未应用）。

## 准确度评分

| 维度 | v4 | v5 | v6 | v7 | v8 | **v9** |
|------|----|----|----|----|----|------|
| 完全一致 | 43% | 70% | 53.3% | 58% | 49% | **38.75%** |
| 低估 | 17% | 13% | 0% | 16% | 47% | **30%** |
| 高估 | 40% | 17% | 47% | 26% | 4% | **31.25%** |
| depth 缺失 | 3% | 3% | 0% | 0% | 1.4% | 0% |

## 校准流程迭代总结（v1 → v9）

| 轮次 | 准确度 | 高估 | 低估 | 关键变化 |
|------|--------|------|------|----------|
| v4 | 43% | 40% | 17% | L5 标准过严暴露 |
| v5 | 70% | 17% | 13% | 校准应用后回升 |
| v6 | 53.3% | 47% | 0% | 标准偏宽松反弹 |
| v7 | 58% | 26% | 16% | L5 标准 2.0 收紧 |
| v8 | 49% | 4% | 47% | v2.0 微调低估反弹 |
| **v9** | **38.75%** | **31.25%** | **30%** | 调整方向正确但力度不够 |

## 关键诊断

**v2.0 rubric 仍过严**：
- v9 的 D5 ≥ 2 案例调整**显著抑制了低估率**（47% → 30%）
- 但**反向产生高估反弹**（4% → 31.25%）
- 整体准确度反而下降 -10pp

**主要问题**：
1. **D2（跨模块联动）** 维持 ≥5 跨主模块 = 2 分仍偏紧，导致 overview/index 文件被低估
2. **D3（系统性）** "演进时间线 + 设计哲学"过于严格，overview 类文件普遍吃亏
3. **D5 ≥ 2 案例**调整有效降低低估率，但 D2/D3/D4 仍严 → 高估反弹

## 已应用校准（commit 6fb0b122）

43 篇校准：
- 24 升级（含 6 篇 L4 → L5）
- 19 降级（含 5 篇 L5 → L4）

## v10 调整建议

### 1. 区分 overview/index vs 主题深读独立评分基线

- overview 类（如 `01-database/README.md`、`01-core/README.md`）给独立基线评分
- 主题深读类（如 `01-database/05-mysql/README.md`）保持 v2.0 标准

### 2. D2 接受"同模块多兄弟 + 2 跨主模块"

- 当前 ≥5 跨主模块硬指标 → 降低为 ≥2 跨主模块 + 同模块联动

### 3. D3 接受"多视角对比表"

- 当前"演进时间线 + 设计哲学"双条件 → 接受任一即可

## 相关文件

| 文件 | 用途 |
|------|------|
| `skills/note-health/references/five-dim-sampling-process.md` | 流程 + L5 标准 2.0 |
| `skills/note-health/references/v4-sampling-report.md` | v4 偏差清单 |
| `skills/note-health/references/v5-sampling-report.md` | v5 准确度回升 |
| `skills/note-health/references/v6-sampling-report.md` | v6 标准偏宽松 |
| `skills/note-health/references/v7-sampling-report.md` | v7 收紧初见效 |
| `skills/note-health/references/v8-sampling-report.md` | v8 微调低估反弹 |
| `scripts/auto-calibrate.py` | 自动化校准脚本 |
| `.github/workflows/difficulty-calibration.yml` | CI + 月度 cron |
