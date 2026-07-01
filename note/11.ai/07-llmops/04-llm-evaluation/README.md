# LLM 评估体系：6 大维度 + 5 种评估方法完整实战

> 一份按层次梳理的 LLM 评估速查手册：从自动化指标到 A/B Test 的完整评估框架。

---
## 引言：反直觉代码

LLM 评估体系：6 大维度 + 5 种评估方法完整实战 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、LLM 评估的 3 大挑战

1. **答案多样**：同一问题多个正确答案
2. **评估主观**：质量无客观标准（"好"的回答因场景而异）
3. **成本高**：人工评估贵 / 自动化评估不准

---

## 二、6 大评估维度

| 维度 | 含义 | 衡量指标 |
|------|------|---------|
| **准确性** | 答对了没 | 准确率 / 召回率 / F1 |
| **相关性** | 答得切题没 | 人工评分 / LLM Judge |
| **一致性** | 多次答得一样没 | 重复率 / 自相矛盾率 |
| **安全性** | 有害内容没 | 违规率 / 注入成功率 |
| **性能** | 多快返回 | 延迟 / QPS |
| **成本** | 一次调用多少钱 | Token / $ |

---

## 三、5 种评估方法

### 3.1 方法对比

| 方法 | 准确性 | 成本 | 速度 | 适用 |
|------|--------|------|------|------|
| **自动化指标** | 中 | 极低 | 极快 | 标准化任务 |
| **黄金集** | 高 | 低 | 快 | 持续回归 |
| **LLM-as-Judge** | 中高 | 低 | 快 | 复杂任务 |
| **人工评估** | 最高 | 高 | 慢 | 关键场景 |
| **A/B Test** | 真实 | 中 | 中 | 生产验证 |

---

## 四、方法 1：自动化指标

### 4.1 通用 NLP 指标

| 指标 | 适用 | 说明 |
|------|------|------|
| **Exact Match** | 标准化答案 | 字符级匹配 |
| **BLEU** | 翻译 | n-gram 精度 |
| **ROUGE** | 摘要 | n-gram 召回 |
| **METEOR** | 翻译 | 考虑同义词 |
| **BERTScore** | 通用 | 基于 BERT embedding 相似度 |

### 4.2 任务特定指标

| 任务 | 指标 |
|------|------|
| **分类** | Accuracy / F1 / AUC |
| **问答** | Exact Match / F1 |
| **摘要** | ROUGE-1/2/L |
| **翻译** | BLEU / METEOR |
| **代码生成** | Pass@k / CodeBLEU |
| **RAG** | Faithfulness / Answer Relevancy |

---

## 五、方法 2：黄金集评估

### 5.1 构建黄金集

```json
{
  "test_cases": [
    {
      "id": "qa-001",
      "input": "什么是 RAG？",
      "expected_output": "RAG 是检索增强生成...",
      "context": "...",
      "tags": ["基础知识", "RAG"]
    },
    ...
  ]
}
```

### 5.2 评估流程

```
黄金集（1000 条）→ 跑模型 → 对比答案 vs 期望
   ↓
准确率 / F1 / 分类报告
   ↓
报告失败案例 → 改进模型
```

### 5.3 持续集成

```yaml
# GitLab CI / GitHub Actions
- name: LLM Evaluation
  run: |
    pytest tests/eval/test_model.py --goldset=goldset.json
    # 失败则 PR 阻断
```

---

## 六、方法 3：LLM-as-Judge

### 6.1 核心思想

```
用 GPT-4（或更强的模型）当"裁判"，评估其他模型的输出
```

### 6.2 DeepEval 示例

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

# 1. 定义测试用例
test_case = LLMTestCase(
    input="什么是 RAG？",
    actual_output="RAG 是检索增强生成...",
    expected_output="RAG 是一种结合检索和生成的技术...",
    retrieval_context=["..."]    # RAG 检索的文档
)

# 2. 定义指标
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8)   # 答案不能幻觉
]

# 3. 评估
evaluate([test_case], metrics)
```

### 6.3 5 大 LLM-as-Judge 评估指标

| 指标 | 说明 |
|------|------|
| **Faithfulness** | 答案忠实于检索（不幻觉）|
| **Answer Relevancy** | 答案回答了问题 |
| **Context Precision** | 检索的文档相关 |
| **Context Recall** | 检索召回率 |
| **Answer Correctness** | 答案正确（vs 标准答案）|

### 6.4 评分 Prompt 模板

```python
JUDGE_PROMPT = """
你是一个严格的评估员。请根据以下标准给 LLM 答案打分（0-10 分）：

问题：{question}
LLM 答案：{llm_answer}
标准答案：{reference_answer}

评分标准：
- 准确性（40%）：与标准答案的核心信息是否一致
- 完整性（30%）：是否覆盖了所有要点
- 表达（20%）：是否清晰流畅
- 简洁（10%）：是否冗余

请输出：
- 总分：0-10
- 理由：[详细说明]
"""
```

---

## 七、方法 4：人工评估

### 7.1 评估维度模板

| 维度 | 1 分 | 3 分 | 5 分 |
|------|------|------|------|
| 准确性 | 完全错 | 部分对 | 完全对 |
| 有用性 | 无帮助 | 一般 | 非常有用 |
| 流畅性 | 不通顺 | 较流畅 | 自然流畅 |
| 安全性 | 有害 | 中性 | 友好安全 |

### 7.2 标注员管理

```
专业标注员 > 众包标注 > 内部员工
  ↓         ↓          ↓
 高质量    中质量      低成本
```

### 7.3 评估数据平台

- **Label Studio**（开源）
- **Scale AI**（商业）
- **Labelbox**（商业）
- **Amazon SageMaker Ground Truth**

---

## 八、方法 5：A/B Test

### 8.1 实施流程

```
用户访问
   ↓
分流（50% v1 / 50% v2）
   ↓
v1 模型回答 vs v2 模型回答
   ↓
收集用户反馈（点赞 / 点踩 / 停留时间）
   ↓
统计显著性检验
```

### 8.2 关键指标

| 指标 | 说明 |
|------|------|
| **CTR** | 点击率 |
| **停留时间** | 用户停留时长 |
| **点赞率** | 👍 / 👎 比 |
| **转化率** | 完成业务动作 |
| **跳出率** | 用户是否继续对话 |

### 8.3 工具

- **LaunchDarkly**（Feature Flag + A/B）
- **Statsig**（A/B Test + 指标）
- **Eppo**（企业 A/B Test）

---

## 九、综合评估实战

### 9.1 评估流水线

```yaml
# .gitlab-ci.yml
stages:
  - eval
  - test

llm-eval:
  stage: eval
  script:
    - python -m pytest tests/eval/ --goldset=goldset-1000.json
    - python -m deepeval run --metrics=faithfulness,relevancy

# 黄金集：1000 条标准问答
# 自动化指标：BLEU / ROUGE / F1
# LLM-as-Judge：GPT-4 评分

integration-test:
  stage: test
  script:
    - python -m locust -u 100 -r 10    # 性能压测
```

### 9.2 评估报告示例

```
模型 v2 评估报告（2026-06-28）
─────────────────────────
黄金集（1000 条）：
  - 准确率：92.3%（v1: 88.5%）
  - F1：91.8%
  
LLM-as-Judge（GPT-4 评分）：
  - Faithfulness：0.89（v1: 0.82）
  - Answer Relevancy：0.93
  
人工评估（100 条抽样）：
  - 准确性 4.5/5
  - 有用性 4.2/5
  
性能：
  - P50 延迟：800ms
  - P99 延迟：2.3s
  
成本：
  - 单次调用：$0.012
  - 日成本：$360

结论：v2 全面优于 v1，建议全量上线
```

---

## 十、最佳实践

1. **多维度评估**：不能只看准确率
2. **黄金集必备**：每次发版必跑（CI 集成）
3. **LLM-as-Judge 谨慎用**：GPT-4 也会错（"裁判偏见"）
4. **A/B Test 是金标准**：用真实用户数据
5. **持续监控**：线上指标变化（数据漂移）
6. **人工评估抽检**：每月 1 次（100-200 条）
7. **评估成本控制**：用小模型 + 黄金集做高频评估
8. **评估数据版本管理**：黄金集和评估脚本进 Git

---

← [返回 AI 知识体系总览](../../README.md) · 📅 2026-06-28