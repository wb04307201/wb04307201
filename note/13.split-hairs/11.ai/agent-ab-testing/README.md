<!--
question:
  id: 11.ai-agent-ab-testing
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: AI 生产工程
  tags: [11.ai, A.B.Testing, Experiment, Traffic, Statistics, Drift, Holdout, Sticky-Session]
-->

# Agent A/B Test 系统设计 —— 5 大组件 + 4 流量分配 + 显著性检验 + 5 反模式

> 一句话定位：**AI 场景 A/B Test = 多指标 + 流量分层 + 离线/在线双轨 + 显著性检验 + 自动决策**。完整深度 + 5 流量策略 + 3 OSS 实战见 [主模块 · 05-agent-evaluation/02-ab-testing-design 专章](../../../../11.ai/05-agent-evaluation/02-ab-testing-design/README.md)。

> **系列定位**：AI Production Engineering 经典追问（Anthropic / OpenAI / 阿里 / 字节 / 美团 工程师高频）。考察的不是"A/B Test 是什么"，而是 **5 大核心组件 + 4 流量分配 + 显著性检验 + 5 反模式 + 90 秒话术**。

---

⭐⭐⭐⭐⭐ 深度级别（高级 AI 应用工程师 / 平台架构师）
📚 前置知识：传统 A/B Test 基础 / Agent 评测 / Statistics / 流量切分

---

## 引子：3 个崩溃现场

```text
场景：2025 阿里 AI Agent 一面追问——

Q1：「新 Planner 上线，怎么验证比旧的好？」
    → 初级："跑几天看效果"              ❌
    → 高分："5 大组件：流量分配 + 实验配置 +
            评估指标 + 显著性检验 + 自动决策
            + 4 流量分配策略 + 多指标校正"

Q2：「A/B Test 用多少流量？」
    → 初级："50/50"                  ❌
    → 高分："分层 + 10% Holdout +
            灰度 5/10/50/100 + 4 周时间"

Q3：「A/B 跑了 1 周，效果一样怎么办？」
    → 初级："再跑 1 周"              ❌
    → 高分："提前算样本量 →
            不显著 = 早停 + 切换更敏感方法
            （Sequential testing）"
```

**核心陷阱**：很多人以为 AI A/B Test = 传统 web A/B。**AI 场景**有 3 大特殊：输出非确定性、多指标、长期漂移。

---

## 一、核心原理（必选）

### 1.1 AI vs 传统 web A/B Test 区别

| 维度 | 传统 web | AI Agent |
|------|---------|---------|
| **单次结果** | 确定 | 非确定（temperature > 0）|
| **指标数** | 1-2（点击率/转化率）| 4-6（完成率/token/满意度/成本/一致性）|
| **数据分布** | 近似二项分布 | 复杂（长尾 + 重尾）|
| **长期漂移** | 小 | 大（模型迭代 / 用户偏好漂移）|
| **流量分配** | 简单 hash | 需 sticky + 灰度 + holdout |
| **失败模式** | 转化率下降 | 幻觉率突增 / 成本爆炸 |

### 1.2 5 大核心组件（**核心考点**）

```text
┌──────────────────────────────────────────────┐
│  1. 流量分配层（Traffic Allocator）           │
│     - Hash 分流 / Sticky / 分层实验          │
├──────────────────────────────────────────────┤
│  2. 实验配置层（Experiment Config）          │
│     - Variants: A (baseline) / B (新版本)    │
│     - 灰度比例 / 流量切分                    │
├──────────────────────────────────────────────┤
│  3. 评估指标层（Metric Engine）               │
│     - 任务完成率 / Token 成本 / CSAT         │
├──────────────────────────────────────────────┤
│  4. 显著性检验层（Statistics）                 │
│     - t-test / z-test / Bonferroni            │
├──────────────────────────────────────────────┤
│  5. 自动决策层（Auto-Decision）               │
│     - 提升阈值 + 全量 / 回滚                  │
└──────────────────────────────────────────────┘
```

---

## 二、4 大流量分配策略

| # | 策略 | 实战 | 适用 |
|---|------|------|------|
| 1 | **Hash 分流** | `hash(user_id) % 100 < ratio` | 简单、可重现 |
| 2 | **Sticky Session** | 用户首次进 A 全程 A | 防"跨版本污染" |
| 3 | **分层实验** | 流量层 / 体验层 / UI 层 多实验并行 | 大厂标配 |
| 4 | **Holdout 流量** | 10% 永远 baseline 测长期回归 | 必备 |

---

## 三、4 大评估指标（AI 场景专属）

| # | 指标 | 衡量 | 权重 |
|---|------|------|------|
| 1 | **任务完成率** | 业务结果（最核心） | 40% |
| 2 | **Token 成本** | 效率（$ per task）| 20% |
| 3 | **用户满意度** | CSAT / 点赞 / 留存 | 30% |
| 4 | **漂移检测** | 指标稳定性 | 10% |

**注意**：AI 场景必须看**多指标综合分**（weighted score），不能只看任务完成率。

---

## 四、显著性检验（统计保障）

### 4.1 单变量 A/B

```python
from scipy.stats import ttest_ind

def is_significant(a_metrics, b_metrics, alpha=0.05):
    t_stat, p_value = ttest_ind(a_metrics, b_metrics)
    return p_value < alpha
```

### 4.2 多变量 ABn（**必加 Bonferroni**）

```python
def is_significant_multi(metrics_a, metrics_b, n_metrics):
    """n_metrics 个指标同时检验，需要 Bonferroni 校正"""
    p_values = []
    for k, v in metrics_a.items():
        t, p = ttest_ind(v, metrics_b[k])
        p_values.append(p)
    
    # Bonferroni 校正：阈值 = alpha / n
    adjusted_alpha = 0.05 / n_metrics
    return all(p < adjusted_alpha for p in p_values)
```

### 4.3 动态流量（Sequential Testing）

```python
# 不等跑完固定周数就能 early stop
from sequential import SequentialProbabilityRatioTest

def is_significant_sequential(a, b):
    sprt = SequentialProbabilityRatioTest(
        effect_size=0.05,  # 5% 提升视为显著
        alpha=0.05,
        beta=0.20
    )
    for ai, bi in zip(a, b):
        result = sprt.update(ai, bi)
        if result == "significant":
            return True
        if result == "stop_no_effect":
            return False
    return False
```

---

## 五、5 反模式（高频陷阱）

| # | 反模式 | 后果 | 修复 |
|---|--------|------|------|
| 1 | ❌ 跑完 1 周才看结果 | 等发现显著时已亏 1 月 | 提前算样本量 + Sequential |
| 2 | ❌ 多指标全看显著性 | 假阳性率爆炸 | Bonferroni 校正 |
| 3 | ❌ 新版本全量直接上 | 灾难无回滚 | 灰度 5/10/50/100 + 自动回滚 |
| 4 | ❌ 没 Holdout | 长期漂移不可测 | 固定 10% baseline |
| 5 | ❌ 漂移不监控 | 召回率突变无感知 | 每日 vs 历史 baseline 对比 |

---

## 六、实战代码（最小可用 A/B Test Router）

```python
import hashlib
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Variant:
    name: str        # "A" / "B" / "holdout"
    config: dict     # 实验配置（prompt / model / temperature）
    ratio: float     # 0.0 - 1.0

class ABTestRouter:
    def __init__(self, variants: List[Variant], holdout_ratio=0.10):
        self.variants = variants
        self.holdout = holdout_ratio  # 固定 10% baseline
    
    def route(self, user_id: str, query: str) -> dict:
        # 1. Holdout 流量
        h = self._hash(user_id)
        if h < self.holdout * 100:
            return self.variants[0].config
        
        # 2. Sticky Session（同用户同版本）
        adjusted = (h - self.holdout * 100) / (1 - self.holdout)
        cumulative = 0
        for v in self.variants[1:]:
            cumulative += v.ratio
            if adjusted <= cumulative:
                return v.config
        
        return self.variants[-1].config
    
    def _hash(self, user_id):
        return int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
```

```python
# 使用示例
variants = [
    Variant(name="A_baseline", 
            config={"prompt": "...", "model": "gpt-4"}, 
            ratio=0.0),  # baseline
    Variant(name="B_new", 
            config={"prompt": "更优化", "model": "gpt-4"}, 
            ratio=0.5),    # 50% 流量
    Variant(name="C_experimental", 
            config={"prompt": "实验性", "model": "gpt-4-turbo"}, 
            ratio=0.5),    # 50%
]
router = ABTestRouter(variants, holdout_ratio=0.10)

# 调用
config = router.route(user_id="user-123", query="...")
result = llm.invoke(query, **config)
```

---

## 七、面试话术（90 秒版本）

### 题目：怎么设计 Agent / Prompt 的 A/B Test？

**高分答案（4 层递进，60-90 秒）**：

```
1. 一句话（10 秒）：
   "AI 场景 A/B Test ≠ 传统 A/B。
    输出非确定 + 多指标 + 长期漂移。
    需要 5 大组件 + 4 流量策略。"

2. 5 大组件（25 秒）：
   "5 大核心组件：
   ① 流量分配（hash + sticky + 分层）
   ② 实验配置（baseline + 新版本 + 比例）
   ③ 评估指标（完成率 40% + 成本 20% + CSAT 30% + 漂移 10%）
   ④ 显著性检验（t-test + Bonferroni）
   ⑤ 自动决策（提升阈值 + 全量/回滚）"

3. 4 流量策略 + 显著性（30 秒）：
   "4 大流量分配：
   ① Hash 分流（hash(user_id) % 100）
   ② Sticky session（防跨版本污染）
   ③ 分层实验（流量层 + 体验层）
   ④ Holdout 10%（永远 baseline 测长期）
   显著性：单变量 t-test / 多变量 Bonferroni /
   Sequential testing 早停"

4. 5 反模式 + 实战（25 秒）：
   "5 反模式：
   跑完 1 周才看 / 多指标假阳性 / 没灰度 / 
   没 Holdout / 漂移不监控
   实战经验：跑 4 周、10% Holdout、
   5% 提升视为显著、自动灰度 5/10/50/100"
```

---

## 八、面试反问

```
Q1：贵司 Agent 上线怎么验证？
    → 答 5 组件 + 灰度 = 高分
Q2：A/B 用多少流量？
    → 答 10% Holdout + 灰度 = 高分
Q3：多指标怎么防假阳性？
    → 答 Bonferroni 校正 = 高分
Q4：效果不明显怎么办？
    → 答 Sequential testing 早停 + 切换 = 高分
Q5：怎么防版本迭代后召回率突变？
    → 答 Holdout + 漂移检测 = 高分
```

---

## 🔗 系列导航表（13.split-hairs · 11.ai 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [agent-dag-vs-react](../agent-dag-vs-react/README.md) | Agent DAG vs ReAct | ⭐⭐⭐⭐ |
| [agent-memory-classification](../agent-memory-classification/README.md) | Memory 三维分类 | ⭐⭐⭐⭐ |
| [agent-performance-evaluation](../agent-performance-evaluation/README.md) | 6 大评测维度 + 5 方法 | ⭐⭐⭐⭐⭐ |
| [claude-code-agentic-search](../claude-code-agentic-search/README.md) | Claude Code 搜索模式 | ⭐⭐⭐⭐ |
| [context-engineering](../context-engineering/README.md) | Context Engineering | ⭐⭐⭐⭐⭐ |
| [hallucination](../hallucination/README.md) | 幻觉分类 + 4 检测 | ⭐⭐⭐⭐⭐ |
| [long-context-agent-strategy](../long-context-agent-strategy/README.md) | 长上下文 6 策略 | ⭐⭐⭐⭐⭐ |
| [multi-agent-shared-memory](../multi-agent-shared-memory/README.md) | 多 Agent 共享记忆 | ⭐⭐⭐⭐⭐ |
| [rag-out-of-domain-rejection](../rag-out-of-domain-rejection/README.md) | RAG 超范围拒答 | ⭐⭐⭐⭐⭐ |
| [react-vs-plan-execute](../react-vs-plan-execute/README.md) | ReAct vs Plan-Execute | ⭐⭐⭐⭐⭐ |
| **agent-ab-testing**（本篇）| A/B Test 系统设计 + 5 组件 + 显著性 | ⭐⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [11.ai · 05-agent-evaluation/02-ab-testing-design 专章](../../../../11.ai/05-agent-evaluation/02-ab-testing-design/README.md) —— 完整深度 + 5 流量策略 + 3 OSS 实战 + Python 完整代码

---

> 📅 2026-07-13 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 5 组件 + 4 流量 + 显著性 + 5 反模式 + 90 秒话术 + 11 兄弟导航

← [返回: 咬文嚼字 · 11.ai](README.md)
