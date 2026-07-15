<!--
module:
  parent: ai/08-llmops/agent-evaluation
  slug: ai/08-llmops/agent-evaluation/04-pipeline
  type: topic
  category: 评测流程
  summary: Agent 评测完整 pipeline —— 黄金集 → 离线 CI → A/B Test → 用户模拟 + 漂移检测
-->

# Agent 评测 Pipeline · 离线到在线完整流程

> **一句话**：评测不是"上线前跑一次"——是 **黄金集 + CI 自动化 + A/B Test + 用户模拟 + 漂移检测** 的连续 pipeline，每个环节都有进入下环节 / 阻塞发布 / 回滚 的触发条件。

← [返回: Agent Evaluation 总目录](../README.md)

---

## 1. 完整 Pipeline（4 阶段）

```
┌────────────────────────────────────────────────────────────┐
│ 阶段 1：黄金集构建（持续）                                  │
│   - 真实业务场景 500-1000 条                              │
│   - 标注：期望输出 + 期望工具 + 期望步骤                   │
│   - 难度分级：easy / medium / hard / adversarial            │
│   - 来源：用户反馈 + 失败用例 + 人工标注                   │
└─────────────────────┬───────────────────────────────────────┘
                      ↓（PR 触发）
┌────────────────────────────────────────────────────────────┐
│ 阶段 2：离线自动化 CI 评估                                    │
│   - 触发：每次 PR / Push                                   │
│   - 跑黄金集 50-100 条（快） + 自动化指标 + LLM-judge     │
│   - 报告：分数 + 失败样本                                  │
│   - 阈值：score ≥ 0.80 通过，阻塞合并                      │
└─────────────────────┬───────────────────────────────────────┘
                      ↓（merge to main）
┌────────────────────────────────────────────────────────────┐
│ 阶段 3：A/B Test 灰度（3-7 天）                             │
│   - 5% 流量 → 新版本                                      │
│   - 监控：6 维指标 + 显著性检验                            │
│   - 通过条件：完成率显著提升 + 无显著恶化                  │
│   - 回滚：一键 100% 切回 control                          │
└─────────────────────┬───────────────────────────────────────┘
                      ↓（全量发布后）
┌────────────────────────────────────────────────────────────┐
│ 阶段 4：在线持续监控（永不停止）                             │
│   - 实时：完成率 / 延迟 / 成本                            │
│   - 漂移检测：每日 score → 趋势告警                        │
│   - 自动回滚：score 跌破阈值 → 切回旧版本                  │
│   - 每周：跑黄金集全量（500 条）+ 用户模拟                 │
└────────────────────────────────────────────────────────────┘
```

---

## 2. CI 集成最佳实践

```yaml
# .github/workflows/agent-eval.yml
name: Agent Evaluation
on: pull_request
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - name: Run golden set
        run: python -m agent.eval --golden-set tests/golden_set.json --threshold 0.85
      - name: LLM-as-Judge
        run: python -m agent.judge --output eval-results.json
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '🤖 Agent Eval: Score=${SCORE}%, Pass=${PASSED}'
            })
```

---

## 3. A/B Test 关键参数

| 参数 | 推荐值 |
|------|--------|
| 流量比例 | 5% → 25% → 50% → 100% |
| 实验时长 | ≥ 7 天（工作日 + 周末） |
| 显著性检验 | p-value < 0.05 |
| 主要指标 | 任务完成率 |
| 次要指标 | 步骤效率 / 成本 / 满意度 |
| 回滚阈值 | 完成率下降 ≥ 2% |

---

## 4. 漂移检测（Drift Detection）

```python
def detect_drift(historical_scores, current_score):
    """检测模型输出漂移"""
    # KS 检验
    from scipy.stats import ks_2samp
    statistic, p_value = ks_2samp(historical_scores, [current_score])
    
    if p_value < 0.05:
        return True, "显著漂移"
    return False, "无显著漂移"

def daily_drift_check():
    # 每天跑 50 条快测集
    quick_scores = run_quick_eval(n=50)
    
    # 检测漂移
    drifted, msg = detect_drift(historical=last_30_days, current=quick_scores.mean())
    if drifted:
        alert(f"🚨 Agent 输出漂移：{msg}")
        # 可选：自动回滚
```

---

## 5. 黄金集维护

```python
GOLDEN_SET_LIFECYCLE = """
1. 初始：业务专家手工标注 500 条（含难 / 中 / 易）
2. 持续补充：每周从用户反馈 / 失败用例 / 边缘 case 抽 10-20 条
3. 每月 review：
   - 答案是否过时（业务变更）
   - 难度分级是否准确
   - 是否有重复 / 相似题目
4. 季度清理：淘汰过期题目 / 补充新场景
"""
```

---

## 6. Pipeline 反模式 · 5 个常见错

### ⚠️ 反模式 1：上线前跑一次就发布

- **错**：评测一次高就发版
- **对**：每次 PR + 灰度 + 全量监控

### ⚠️ 反模式 2：A/B Test 时间太短

- **错**：A/B 跑 1 天就下结论
- **对**：≥ 7 天（含工作日 / 周末 / 高峰期）

### ⚠️ 反模式 3：黄金集不更新

- **错**：黄金集 1 年没更新，跟不上业务变化
- **对**：每周 / 每月增量补充

### ⚠️ 反模式 4：阈值不合理

- **错**：阈值 100%（永远跑不过）
- **对**：阈值 80-85%，结合业务调整

### ⚠️ 反模式 5：漂移无告警

- **错**：没人看监控大盘
- **对**：自动告警 + 自动回滚

---

## 7. 一句话总结

> **Agent 评测 Pipeline = 黄金集（500 条持续维护）→ CI 自动化（PR 触发 + 阈值 0.85）→ A/B Test（5% 流量 → 7 天 → 全量）→ 漂移检测（每日快测 + KS 检验 + 自动告警）→ 回滚机制。任何环节缺失都是定时炸弹。**

---

← [返回: Agent Evaluation 总目录](../README.md) · 上一章：[03-llm-as-judge](03-llm-as-judge.md) · 下一章：[05-ali-interview](05-ali-interview.md)
