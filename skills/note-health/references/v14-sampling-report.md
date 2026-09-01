# v14 抽样验证报告（2026-09-01）

> **目的**：验证 v14 微调版（D2 阈值 5→3 + D5 阈值 2→1 + overview D5 豁免）准确度
> **方法**：80 篇抽样（37 overview + 43 主题深读）
> **关键发现**：准确度 **36.2%**（偏差≤1），比 v13 33.75% **+2.45pp**，仍**未达 ≥75% 目标**

## 准确度统计

| 指标 | v12 自报 | v13 实测 | **v14 实测** | 趋势 |
|------|:---:|:---:|:---:|------|
| 完全一致（|偏差|≤0.5）| 43.75% | 16.25% | **17.5%** | ✅ +1.25pp（v13→v14）|
| 偏差≤1 | 81.25% | 33.75% | **36.2%** | ✅ +2.45pp（v13→v14）|
| 偏差≤2 | — | — | **56.2%** | — |

## 按类型统计

| 类型 | 文件数 | 偏差≤1 |
|------|:---:|:---:|
| overview | 37 | **20 / 54.1%** |
| deep | 43 | **9 / 20.9%** |

## 关键发现：v14 微调未达 75% 目标

### 根因诊断

1. **v12 baseline 与 v14 维度评分方法论错配**：
   - v12 baseline（current_total）大部分为 14-20/20（70-100%），由人工整体判定
   - v14 维度评分（d1-d5 加总）实际落在 3-9/10（30-90%），存在 ~2 分系统性低估
   - 即使把 v14 拉到极端宽松（D1≥1 即 2、D3/D4 lines≥50 即 2、overview 无 cross 也给 d2=1），|dev|≤1 也仅能从 36.2% 提到 48.8%，距 75% 仍有 ~26pp 差距

2. **deep 文件几乎全军覆没**（20.9% 准确度）：
   - 84% 的 deep 文件偏差 ≥2
   - v12 给了 17-20 分但 deep 维度评估天然难拿满分（D2 跨模块=0 是常态 + D3/D4 受 v13 baseline 拖累）
   - 9 个 deep 文件低估，平均偏差 -3.0

3. **7 篇 current_total=0 的野生点**（如 10/06/agent-memory、04/ioc、04/aop、01/data-types、10/plm、06/api/rest、03/SPEC）：
   - v14 实际有内容但 v12 未评
   - 这些点偏差 +5 到 +9，直接拉低整体准确度约 9pp

4. **D2 阈值降低（≥5→≥3）对 deep 几乎无效**：
   - 跨主模块路径引用在深度文中是稀有信号
   - 60/80 文件 cross<3、仅 7 篇 deep 文件 cross≥3
   - 没有命中 v14 阈值带来的"分数跳档"

5. **overview 豁免 D5 已被 v13 d5=2 覆盖**：
   - v13 baseline 对 SPEC/README 这类 overview 已给 d5=2
   - "豁免"只新增了对 d5=0 overview 的保护
   - v13 d5=0 的 overview 极少（仅 4 篇），v14 调整收益边际

## 主要偏差清单（|偏差|≥1，共 65 篇）

### 高频偏低（v12 baseline 偏高估）

| 文件 | 类型 | v14 | v12 | 偏差 |
|------|------|----:|----:|----:|
| 04.spring-backend/06-integration/validation/README.md | deep | 3 | 20 | **-7.0** |
| 04.spring-backend/01-core/ioc/README.md | deep | 7 | 0 | **+7.0** |
| 04.spring-backend/01-core/aop/README.md | deep | 5 | 0 | **+5.0** |
| 01.java-and-jvm/01-language/data-types/README.md | deep | 6 | 0 | **+6.0** |
| 09.ai-applications/agent/agent-memory/README.md | deep | 9 | 0 | **+9.0** |
| 10.business-systems/01-rd-innovation/plm/README.md | deep | 7 | 0 | **+7.0** |
| 08.ai-foundations/05-tokenization-embedding/README.md | deep | 10 | 6 | **+7.0** |
| 06.distributed-systems/01-foundation/system-design-basics/api/rest/README.md | overview | 5 | 0 | **+5.0** |

### 中频偏低

| 文件 | 类型 | 偏差 |
|------|------|----:|
| 02.cs-foundations/01-algorithms/string-algorithms/02-kmp-algorithm.md | deep | -4.5 |
| 11.product-and-pm/SPEC.md | overview | -5.5 |
| 08.ai-foundations/SPEC.md | overview | -5.5 |
| 05.frontend/06-performance/optimization/README.md | deep | -5.0 |
| 06.distributed-systems/06-idempotency/idempotency-key/README.md | deep | -4.0 |
| 06.distributed-systems/04-high-performance/database-optimization/read-write-splitting/README.md | deep | -4.0 |

## 校准流程迭代总结（v1 → v14）

| 轮次 | 偏差=0 | 偏差≤1 | 关键变化 |
|------|---------|---------|----------|
| v4 | 43% | — | L5 标准过严暴露 |
| v5 | **70%** | — | 校准应用后回升（峰值） |
| v9 | 38.75% | — | v2.0 rubric 仍过严 |
| v10 | 46.2% (partial) | — | v10 双基线评分 |
| v11 | 29% | 77% | 完整验证 v10 双基线 |
| v12 | 43.75% | 81.25% | v12 overview D5 豁免（**自报**）|
| v13 | 16.25% | 33.75% | 独立验证：v12 假设不成立 |
| **v14** | **17.5%** | **36.2%** | v14 微调（D2≥3 + D5≥1），仍**未达 75%** |

## 关键洞察：v14 微调无效

### 核心矛盾：v12 baseline 与 v14 维度评分方法论错配

| 维度 | v12 评分（人工整体）| v14 评分（d1-d5 加总）|
|------|-------------------|---------------------|
| 量级 | 0-20 分（70-100% 集中 14-20）| 0-10 分（30-90% 集中 3-9）|
| 校准 | 人工判定 | 维度公式 |
| 系统性差异 | 偏高 | 偏低 ~2 分 |

### 下一步方向

1. **重新标定 v14 评分到 0-20 量级**：避免方法论错配
2. **引入 v12→v14 线性校准**：整体 +1.5 分偏移
3. **放弃"偏差≤1"作为精度指标**：承认 v14 与 v12 本质上是不同评估口径
4. **建立 ground truth 重新评分**：让 v14 baseline 走严格 D5 豁免版，生成新 ground truth

### 短期 v15 抽样建议

- 不依赖 v12 baseline，独立重评 80 篇 → 新 ground truth
- 用新 ground truth 重新计算偏差 ≤1 准确度
- 预期 v15 准确度可能回升至 50%+（消除方法论错配）

## 校准流程迭代总结（v1 → v14）完整版

| 阶段 | 轮次 | 偏差=0 | 偏差≤1 | 关键变化 |
|------|------|---------|---------|----------|
| 误报消除 | v1-v3 | — | — | 233 → 0 误报 |
| 标准收紧 | v4-v7 | 43% → 58% | — | L5 标准 2.0 |
| 微调尝试 | v8-v9 | 49% → 38.75% | — | v2.0 rubric 仍过严 |
| 双基线 | v10-v11 | 46% → 29% | 77% | overview 独立基线 |
| 豁免版 | v12 | 43.75% (自报) | 81.25% (自报) | overview D5 豁免 |
| 验证 | v13 | 16.25% | 33.75% | v12 假设不成立 |
| 微调 | **v14** | **17.5%** | **36.2%** | D2≥3 + D5≥1 仍**未达 75%** |

## 相关文件

| 文件 | 用途 |
|------|------|
| `skills/note-health/references/five-dim-sampling-process.md` | v14 L5 标准微调 |
| `skills/note-health/references/health-metrics-convergence.md` | 三指标收敛曲线 |
| `scripts/auto-calibrate.py` | v5 overview D5 豁免 + D2 阈值 |
| `scripts/simulate-monthly-cron.sh` | 本地 cron 模拟 |
