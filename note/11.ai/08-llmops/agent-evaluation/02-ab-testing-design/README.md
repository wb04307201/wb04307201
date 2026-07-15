<!--
module:
  parent: ai/08-llmops/agent-evaluation
  slug: ai/08-llmops/agent-evaluation/02-ab-testing-design
  type: deep-dive
  category: A/B Test 系统设计
  summary: Agent / Prompt A/B Test 系统设计深度 —— 5 大组件 + 4 流量分配 + 显著性检验 + 灰度发布 + 监控告警 + OSS 实战。
-->

# Agent A/B Test 系统设计 · 深度专章

> 一句话定位：**AI 场景 A/B Test ≠ 传统 web A/B；本质是"输出非确定性 + 多指标 + 长期漂移"下的统计对照系统**。完整体系基于 [主模块 · Agent Evaluation](../../README.md) + [LLM 评测专题](../../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)。面试速查版见 [13.split-hairs · agent-ab-testing](../../../../13.split-hairs/11.ai/agent-ab-testing/README.md)。

---

## 一、AI 场景的 A/B Test 与传统 web 区别

### 1.1 三大核心差异

| 维度 | 传统 web A/B | AI Agent A/B Test |
|------|------------|------------------|
| **单次结果** | 确定（点击/不点击）| 非确定（temperature > 0） |
| **指标数** | 1-2（点击率/转化率）| 4-6（完成率/token/成本/CSAT/漂移） |
| **数据分布** | 近似二项 | 长尾 + 重尾 + 季节性 |
| **长期漂移** | 小 | 大（模型迭代 / 用户偏好变化） |
| **流量分配** | 简单 hash | sticky + 灰度 + holdout |
| **失败模式** | 转化率下降 | 幻觉率突增 / 成本爆炸 |
| **实验时长** | 1-2 周 | 4-6 周（含长期漂移观察）|

### 1.2 三大业务驱动力

1. **新 Prompt/Planner 上线** —— 必须证明比 baseline 好（不能凭直觉）
2. **多版本并存** —— 长期运行多个变体，按用户分流
3. **回归保护** —— 监控每次迭代有没有把指标拉低（防漂移）

---

## 二、5 大核心组件（深度）

### 2.1 流量分配层（Traffic Allocator）

#### 4 大流量分配策略

| # | 策略 | 实战 | 优势 | 劣势 |
|---|------|------|------|------|
| 1 | **Hash 分流** | `hash(user_id) % 100 < ratio` | 简单、可重现 | 用户间分布偏差 |
| 2 | **Sticky Session** | 用户首次进 A 全程 A | 防跨版本污染 | 切换版本繁琐 |
| 3 | **分层实验** | 流量层 / 体验层 / UI 层 | 多实验并行 | 配置复杂 |
| 4 | **Holdout** | 10% 永远 baseline | 测长期回归 | 浪费 10% 流量 |

#### 实战：分层实验架构

```python
# 用户请求 → 流量层 → 体验层 → UI 层 → Agent
# 例：流量层切 50% 实验流量，体验层切 Prompt A/B，UI 层切 UI 风格

def assign_layer(user_id, layers_config):
    """layers_config: [
        ('traffic', {'base': 0.5, 'exp': 0.5}),
        ('prompt', {'A': 0.5, 'B': 0.5}),
        ('ui', {'light': 0.3, 'dark': 0.7})
    ]"""
    return {
        layer_name: variant_for_user(user_id, variants, ratios)
        for layer_name, variants in layers_config
    }
```

### 2.2 实验配置层（Experiment Config）

```yaml
# experiments/agent_v2.yaml
experiment_id: "agent_v2_planner"
start_date: "2025-07-13"
end_date: "2025-08-13"
status: "running"

variants:
  - name: "A_baseline"
    ratio: 0.0  # 全部走 holdout + baseline
    config:
      prompt: "..."
      model: "gpt-4"
      temperature: 0.0
  - name: "B_v2"
    ratio: 0.5
    config:
      prompt: "新的 planner prompt"
      model: "gpt-4"
      temperature: 0.0
      extra_param: true

metrics:
  primary: "completion_rate"    # 主指标
  secondary: ["avg_tokens", "csat", "drift_score"]
  weights:
    completion_rate: 0.4
    avg_tokens: 0.2
    csat: 0.3
    drift_score: 0.1

statistical:
  alpha: 0.05
  mcorrection: "bonferroni"     # Bonferroni 校正
  power: 0.8
  effect_size: 0.05              # 5% 提升视为显著

guardrails:
  - "latency_p99 < 5000ms"
  - "error_rate < 0.05"
  - "cost_per_task < $0.10"
```

### 2.3 评估指标层（Metric Engine）

#### 4 大核心指标 + 权重

| # | 指标 | 衡量 | 权重 | 实现 |
|---|------|------|------|------|
| 1 | **任务完成率** | 业务结果 | 40% | 评估器（LLM-as-Judge / 用户反馈） |
| 2 | **Token 成本** | 效率 | 20% | `usage.total_tokens` |
| 3 | **用户满意度** | CSAT | 30% | 👍/👎、STAR 评分 |
| 4 | **漂移检测** | 稳定性 | 10% | 历史 vs 当前分布对比 |

#### 4 大辅助指标

| # | 指标 | 衡量 |
|---|------|------|
| 1 | **延迟** | P50 / P99 |
| 2 | **错误率** | 工具调用失败 / 超时 |
| 3 | **幻觉率** | NLI 检测 / 用户标记 |
| 4 | **重试次数** | 单次任务的平均重试 |

#### 综合分计算（加权）

```python
def calculate_weighted_score(metrics, weights):
    """综合分 = 加权和"""
    score = 0
    for metric, value in metrics.items():
        weight = weights.get(metric, 0)
        score += weight * value
    return score

# 例：completion_rate 0.7 + avg_tokens 0.6 (反转归一化) + csat 0.8 + drift_score 0.9
# 0.4 * 0.7 + 0.2 * 0.4 + 0.3 * 0.8 + 0.1 * 0.9 = 0.28 + 0.08 + 0.24 + 0.09 = 0.69
```

### 2.4 显著性检验层（Statistics）

#### 4 大检验方法

| # | 方法 | 适用 | 关键公式 |
|---|------|------|---------|
| 1 | **t-test** | 连续变量（如 score）| `t = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)` |
| 2 | **z-test**（比例检验）| 二项变量（点击/完成）| `z = (p_a - p_b) / sqrt(p_pool * (1-p_pool) * (1/n_a + 1/n_b))` |
| 3 | **Bonferroni 校正** | 多指标同时检验 | `α_adj = 0.05 / n_metrics` |
| 4 | **Sequential Testing** | 早停 | 每次新数据更新累积证据 |

#### 实战：完整显著性检验

```python
from scipy.stats import ttest_ind, proportion_confint
import numpy as np

def statistical_significance(metrics_a, metrics_b,
                              n_metrics=4, alpha=0.05):
    """多指标 + Bonferroni 校正"""
    p_values = {}
    for name in metrics_a:
        # 连续变量 → t-test
        t_stat, p_val = ttest_ind(metrics_a[name], metrics_b[name])
        p_values[name] = p_val
    
    # Bonferroni 校正
    alpha_adj = alpha / n_metrics  # 0.0125 for 4 metrics
    
    significant = {
        name: p < alpha_adj
        for name, p in p_values.items()
    }
    
    # 综合判定：所有指标都显著 OR 加权综合分显著
    if all(significant.values()):
        return {"result": "all_significant", "p_values": p_values}
    
    # 加权综合分检验
    weighted_a = calculate_weighted_score(metrics_a, weights)
    weighted_b = calculate_weighted_score(metrics_b, weights)
    t_w, p_w = ttest_ind(weighted_a, weighted_b)
    
    return {
        "result": "weighted_significant" if p_w < alpha else "not_significant",
        "p_value": p_w,
        "p_values": p_values,
    }
```

#### 提前算样本量

```python
from statsmodels.stats.power import TTestIndPower

def required_sample_size(effect_size=0.05, alpha=0.05, power=0.8):
    """提前算需要多少样本（典型：5% 提升 + 5% alpha + 80% power）"""
    analysis = TTestIndPower()
    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative='two-sided'
    )
    return int(np.ceil(n))

# 例：detect 5% 提升需要
# n = ~6278 每组 ≈ 12556 总样本
# 假设每天 1000 用户 → 12 天达到显著
```

### 2.5 自动决策层（Auto-Decision）

```python
def auto_decision(experiment_result, statistical_result):
    """基于显著性和效果大小自动决策"""
    
    if statistical_result["result"] == "all_significant":
        if experiment_result["weighted_lift"] > 0.05:
            # 提升 > 5% 且显著 → 全量
            return "promote_to_100%"
        else:
            # 显著但提升小 → 全量但保留 holdout
            return "promote_to_90%"
    
    elif statistical_result["result"] == "weighted_significant":
        # 加权分显著 → 灰度
        return "promote_to_50%"
    
    else:
        # 不显著 → 继续实验 / 回滚
        if experiment_result["cost_increase"] > 0.20:
            return "rollback_for_cost"  # 成本上涨 20% → 回滚
        return "continue_experiment"
```

---

## 三、3 OSS 实战对比

| 工具 / 框架 | 流量分配 | 显著性检验 | OSS 程度 | 适合 |
|------------|---------|-----------|---------|------|
| **Eppo**（商业）| Hash + 分层 | 完整 Bayesian | ⭐⭐⭐⭐⭐ | 大厂首选 |
| **GrowthBook**（开源）| Hash + 分层 | Frequentist | ⭐⭐⭐⭐ | 创业公司 |
| **Statsig**（商业）| Hash + 分层 | 完整 + 实时 | ⭐⭐⭐⭐⭐ | 海外大厂 |
| **LaunchDarkly**（商业）| Feature Flag | 无显著性 | ⭐⭐⭐⭐ | 只切流量 |
| **自研** | 按业务 | 按业务 | ⭐⭐ | 业务专属 |

### 3.1 Eppo 实战（推荐）

```python
import eppo_sdk

# 1. 初始化 SDK
client = eppo_sdk.Client(api_key="eppo-xxxx")

# 2. 分配 variant
variant = client.get_assignment(
    user_id="user-123",
    experiment="agent_v2_planner",
    default="A_baseline"
)

# 3. 记录指标
client.track(
    user_id="user-123",
    metric="completion_rate",
    value=1 if success else 0,
    experiment=variant
)
```

### 3.2 自研 ABTestRouter（已在 L1 中给出完整代码）

适用于"不想引入第三方 + 业务特殊"的场景。

---

## 四、灰度发布 4 步走

### 4.1 标准灰度流程（5/10/50/100）

```
Step 1: 5% 流量
  - 跑 1-2 天看监控指标
  - 检查：错误率 / P99 延迟 / Token 成本
  ↓ 通过
Step 2: 10% 流量
  - 跑 3-5 天看业务指标
  - 检查：完成率 / CSAT
  ↓ 通过
Step 3: 50% 流量
  - 跑 7-14 天看统计显著性
  - 检查：p-value < 0.05 + 提升 > 5%
  ↓ 通过
Step 4: 100% 全量
  - 保留 10% holdout
  - 持续监控长期漂移
```

### 4.2 自动灰度 + 自动回滚

```python
class AutoRollout:
    """自动灰度 + 自动回滚"""
    
    def __init__(self):
        self.canary_pcts = [0.05, 0.10, 0.50, 1.00]
        self.current_idx = 0
    
    def check_health_metrics(self):
        """每 5 分钟检查健康指标"""
        return {
            "error_rate": get_recent_error_rate(minutes=5),
            "p99_latency": get_recent_p99(minutes=5),
            "cost_per_task": get_recent_cost(minutes=5),
        }
    
    def should_promote(self):
        metrics = self.check_health_metrics()
        if (metrics["error_rate"] < 0.01 and 
            metrics["p99_latency"] < 5000 and
            metrics["cost_per_task"] < 0.10):
            return True
        return False
    
    def should_rollback(self):
        metrics = self.check_health_metrics()
        return (metrics["error_rate"] > 0.05 or
                metrics["p99_latency"] > 10000 or
                metrics["cost_per_task"] > 0.20)
    
    def run(self):
        while self.current_idx < len(self.canary_pcts):
            pct = self.canary_pcts[self.current_idx]
            print(f"灰度到 {pct*100:.0f}%")
            
            # 跑 24 小时
            if self.should_rollback():
                print("⚠️ 不健康 → 自动回滚")
                self.current_idx = 0
                # 告警人工
                send_alert("Agent 上线自动回滚")
                return
            
            if self.should_promote():
                self.current_idx += 1
                print(f"✅ 健康 → 提升到下一阶段")
            else:
                print("观察中...")
            
            time.sleep(24 * 3600)
```

### 4.3 GitLab CI 集成（参考）

```yaml
stages: [eval, canary, production]

agent-evaluation:
  stage: eval
  script:
    - python eval/run.py --dataset golden_set.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  artifacts:
    reports:
      junit: eval-results.xml

auto-canary:
  stage: canary
  needs: [agent-evaluation]
  script:
    - python deploy/canary.py --percent 10 --duration 24h
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

---

## 五、4 大反模式深度补充

### 5.1 反模式 1：跑 1 周才看结果（深度）

**反例**：
```python
# ❌ 反例：1 周后看
exp.start()
time.sleep(7 * 24 * 3600)  # 1 周
analyze_results(exp)
```

**正例**：用 Sequential testing 早停。

```python
# ✅ 正例：早停
sprt = SequentialProbabilityRatioTest(
    effect_size=0.05, alpha=0.05, beta=0.20
)
for daily in experiment_data:
    decision = sprt.update(daily)
    if decision == "significant":
        return "promote"
    if decision == "stop":
        return "rollback"
```

**为什么错**：等 1 周才看时，**5% 提升的效果已产生显著业务损失**（每天 ¥10 万的损失 × 7 = ¥70 万）。

### 5.2 反模式 2：多指标全看显著性（深度）

**反例**：
```python
# ❌ 反例：每指标独立显著性
for metric in metrics:
    if p_values[metric] < 0.05:
        # 全看 0.05
```

**问题**：
- 看 20 个指标，p<0.05 的概率 = 1 - (1-0.05)^20 ≈ 64%
- 必有假阳性

**正例**：用 Bonferroni 或 FDR 校正。
```python
# ✅ 正例：Bonferroni 校正
alpha_adj = 0.05 / n_metrics  # 20 个指标 → α=0.0025
for metric in metrics:
    if p_values[metric] < alpha_adj:
        # 严格显著
```

### 5.3 反模式 3：新版本全量直接上（深度）

**反例**：
```python
# ❌ 反例：直接 100%
deploy.traffic_percent = 100  # 没灰度
```

**问题**：上线后才发现 bug，回滚代价大。

**正例**：5/10/50/100 灰度 + 自动回滚（参考 4.2 AutoRollout）

### 5.4 反模式 4：没 Holdout（深度）

**反例**：100% 流量都给实验。

**问题**：基线消失，长期漂移不可测。

**正例**：
```python
# ✅ 留 10% holdout 永久 baseline
holdout_ratio = 0.10
exp_ratio = 0.40  # 实验组
feature_flag_ratio = 0.50  # 功能开关
```

---

## 六、生产级监控体系

### 6.1 6 大监控指标

| # | 指标 | 告警阈值 | 含义 |
|---|------|---------|------|
| 1 | **completion_rate** | 下降 > 5% | 业务结果突变 |
| 2 | **avg_tokens** | 上升 > 20% | 成本风险 |
| 3 | **p99_latency** | > 5000ms | 用户体验 |
| 4 | **error_rate** | > 5% | 系统稳定性 |
| 5 | **drift_score** | > 0.1 | 模型漂移 |
| 6 | **statistical_power** | < 0.7 | 实验可信度 |

### 6.2 监控仪表盘（生产必备）

| 图表 | X 轴 | Y 轴 | 用途 |
|------|------|------|------|
| 完成率趋势 | 时间 | completion_rate | 看趋势 |
| Token 成本分布 | 时间 | token | 看成本 |
| 漂移 vs 历史 | 时间 | KS statistic | 看漂移 |
| 显著性检验 | 实验组 | p-value | 看显不显著 |

### 6.3 自动告警规则

```python
def alert_rules():
    rules = [
        {
            "name": "completion_rate_drop",
            "condition": lambda m: m["completion_rate"] < BASELINE - 0.05,
            "action": "rollback_and_alert",
            "severity": "P0",
        },
        {
            "name": "cost_explosion",
            "condition": lambda m: m["avg_tokens"] > BASELINE * 1.20,
            "action": "alert_cfo",
            "severity": "P1",
        },
        {
            "name": "drift_detected",
            "condition": lambda m: m["drift_score"] > 0.10,
            "action": "recalibrate_and_alert",
            "severity": "P1",
        },
    ]
```

---

## 七、决策树（实战选型）

```text
Q1：你的团队规模？
├─ 大厂（> 50 工程师）→ Eppo / Statsig + Python 自研业务层
├─ 创业公司 → GrowthBook（开源）
└─ 小业务 → 简单自研 Router（参考 4.x 代码）

Q2：你的业务对误判容忍度？
├─ 极低（医疗/金融）→ 加 NLI + 多指标 Bonferroni
└─ 普通 → 单指标 + Sequential testing

Q3：你需要多版本并存吗？
├─ 是 → 分层实验
└─ 否 → 简单 A/B

Q4：你有 Online 流量吗？
├─ 有（> 100 QPS）→ Hash + Sticky + Holdout
└─ 否（< 100 QPS）→ 简单 Switch
```

---

## 八、典型实验时间线

```text
Day 0    : 实验设计（指标 + 流量分配 + 显著性计划）
Day 1    : 灰度 5%（24h 自动健康检查）
Day 3    : 提升到 10%（观察完成率 + CSAT）
Day 7    : 提升到 50%（看 P-value 趋势）
Day 14   : 显著性判定（p<0.05 + 提升>5%）
Day 21   : 全量 100%（保留 10% Holdout）
Day 30   : 长期漂移观察
```

---

## 📚 相关章节

**主模块**：
- [主模块 · Agent Evaluation 总览](../../README.md) —— 6 大指标 + 5 方法 + 4 阶段 Pipeline
- [LLM 评测专题](../../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md) —— 415 行深度

**兄弟评测章节（08 个）**：
- [01-six-metrics.md](../01-six-metrics.md)
- [02-five-methods.md](../02-five-methods.md)
- [03-llm-as-judge.md](../03-llm-as-judge.md)
- [04-evaluation-pipeline.md](../04-evaluation-pipeline.md)
- [05-ali-interview.md](../05-ali-interview.md)
- [06-seven-anti-patterns.md](../06-seven-anti-patterns.md)
- [07-selection-decision-tree.md](../07-selection-decision-tree.md)
- [08-practical-cases.md](../08-practical-cases.md)

**LLMOps**：
- [LLM Evaluation](../../../../11.ai/08-llmops/04-llm-evaluation/README.md)
- [RAG 超范围拒答](../../08-llmops/06-rag-out-of-domain-rejection/README.md)

**面试速查**：
- [13.split-hairs · agent-ab-testing](../../../../13.split-hairs/11.ai/agent-ab-testing/README.md) —— 5 组件 + 4 流量 + 90 秒话术 + 11 兄弟导航

---

> 📅 2026-07-13 · 11.ai/08-llmops/agent-evaluation · ⭐⭐⭐⭐⭐ · 5 组件 + 4 流量 + 显著性 + 4 步灰度 + 6 OSS 实战 + 监控体系

← [返回: Agent Evaluation](README.md)
