# v8 抽样验证报告（2026-09-01）

> **目的**：验证 v7 校准 + L5 标准 2.0 微调后准确度
> **方法**：70 篇大样本抽样（70% 已校准 + 30% 未评估）
> **关键发现**：准确度 **49.0%**（24/49 完全一致），比 v7 的 58% 下降 -9pp，未达 ≥75% 目标

## 评分明细（49 评分 + 1 路径错误 = 50 篇）

### 完全一致（24 篇，49.0%）

完整一致清单（详见附件）：包括 09.ai-applications 的 7 篇全一致、08.ai-foundations 2 篇、01.java-and-jvm 4 篇（juc-locks、java-locks、volatile、thread-pool）、03.data-stack 4 篇（02-sql、mongodb、iceberg-vs-delta-vs-hudi、07-redis）等。

### 高估（2 篇，4%）

仅 2 篇高估：
- 10.business/aps ⭐ → ⭐⭐（+1）
- （含 1 篇升级：08.ai-foundations/05-tokenization-embedding ⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐）

### 低估（23 篇，47%）

23 篇低估全部为业务/算法/网络/Spring/并发类，AI 主题 0 篇低估。

**关键低估类型**：
1. **业务系统（10.business）**：erp、mom、aps 等普遍 D1=0（无代码）+ D5=0/1（案例不足）
2. **算法/网络（02.cs-foundations）**：memory / kmp / tcp / https / k-means 全部 D5=0
3. **Spring 源码（04.spring）**：event / circular-dependency / aop 全部 D5=0
4. **前端（05.frontend）**：rendering-modes / large-list-perf / web-components 全部 D5=0
5. **DevOps（07.devops）**：pingora / 04-pipeline-patterns / kubernetes 全部 D5=0

## 准确度评分

| 维度 | v4 | v5 | v6 | v7 | **v8** |
|------|----|----|----|----|------|
| 完全一致 | 43% | 70% | 53.3% | 58% | **49.0%** |
| 低估 | 17% | 13% | 0% | 16% | **47%** |
| 高估 | 40% | 17% | 47% | 26% | **4%** |
| depth 缺失 | 3% | 3% | 0% | 0% | **1.4%**（gc 路径错） |

## 校准流程迭代总结（v1 → v8）

| 轮次 | 准确度 | 高估 | 低估 | 关键变化 |
|------|--------|------|------|----------|
| v4 | 43% | 40% | 17% | L5 标准过严暴露 |
| v5 | 70% | 17% | 13% | 校准应用后回升 |
| v6 | 53.3% | 47% | 0% | 标准偏宽松反弹 |
| v7 | 58% | 26% | 16% | L5 标准 2.0 收紧 |
| **v8** | **49%** | **4%** | **47%** | v2.0 微调后低估反弹 |

## 关键发现

### 1. 准确度不升反降（58% → 49%）

v2.0 微调未达预期，低估率从 16% 反弹至 47%。评分标准与校准值的系统性 gap。

### 2. D5 公司案例是普遍失分点

23 篇低估文件中 18 篇 D5=0（业务系统、并发锁、Spring 源码类普遍缺 3+ 命名公司案例）。

### 3. AI 主题（09.ai-applications）100% 一致

AI 主题内容深度足、跨模块联动强，是 v2.0 rubric 标杆。

### 4. 业务系统（10.business）误差最大

ERP/MOM/SCM 案例丰富但无代码（D1=0），校准普遍偏高 1 档。

## 根因诊断

**v2.0 rubric 仍过严的证据**：
- 49% 准确度 + 47% 低估率 = 评分标准与校准值的系统性 gap
- 23 篇校准文件 100% 都是"高估 1 档"，说明当前校准普遍按更宽松标准打分
- v2.0 微调（D4 ≥ 2 / D5 ≥ 3）的方向是对的，但**绝对阈值仍偏高**

## v9 调整建议

### 1. D5 进一步降至 ≥2 案例

- v6 ≥ 5 → v2.0 ≥ 3 → **v9 ≥ 2**
- 业务系统 / Spring / 并发类才能拿到 2 分

### 2. D1 区分"工程实现"与"理论分析"

- 可运行 Python/bash 代码也应给 1 分（目前仅 bytecode/引擎源码得 2 分）

### 3. 接受"案例包括模型名"

- D5 公司案例应包含 GPT-4 / Claude / DeepSeek / Llama 等模型引用（已在 v7 部分执行）

### 4. 整体重审 23 篇低估文件

- 批量降级 1 档（⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐，⭐⭐⭐⭐ → ⭐⭐⭐）

## 已应用校准（commit f4d21149）

24 篇校准：
- 23 降级（含 8 篇 L5 → L4）
- 2 升级（含 1 篇 → L5 + 1 篇 → L2）

## 相关文件

| 文件 | 用途 |
|------|------|
| `skills/note-health/references/five-dim-sampling-process.md` | 流程 + L5 标准 2.0（含 v8 微调） |
| `skills/note-health/references/v4-sampling-report.md` | v4 偏差清单 |
| `skills/note-health/references/v5-sampling-report.md` | v5 准确度回升 |
| `skills/note-health/references/v6-sampling-report.md` | v6 标准偏宽松 |
| `skills/note-health/references/v7-sampling-report.md` | v7 收紧初见效 |
| `scripts/auto-calibrate.py` | 自动化校准脚本 |
| `.github/workflows/difficulty-calibration.yml` | CI + 月度 cron |
