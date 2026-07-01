<!--
module:
  parent: ai
  slug: ai/llmops-stack
  type: article
  category: 主模块子文章
  summary: LLMOps 技术栈
-->

# LLMOps 完整技术栈：从训练到生产的全链路工具链

> 一份按层次梳理的 LLMOps 速查手册：从数据标注到模型部署的完整工具链。

---
## 引言：反直觉代码

LLMOps 完整技术栈：从训练到生产的全链路工具链 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、什么是 LLMOps？

LLMOps（Large Language Model Operations）是 MLOps 的子集，专门针对大语言模型的生产化运维。

```
MLOps（通用机器学习） → LLMOps（专注大语言模型）
   ↓                            ↓
模型训练 + 部署               + RAG / Prompt / 评估 / 安全
```

---

## 二、LLMOps 6 大核心阶段

```
┌─────────────────────────────────────────────┐
│  1. 数据准备（Data Preparation）                │
│     标注 / 清洗 / 切分 / 增强                    │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  2. 模型训练（Training）                         │
│     Pre-training / Fine-tuning / RLHF          │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  3. 模型评估（Evaluation）                      │
│     自动化评测 / 人工评测 / A/B Test           │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  4. 模型部署（Deployment）                      │
│     API / SDK / 边缘设备 / 私有化               │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  5. 监控运维（Monitoring & Ops）                │
│     性能 / 成本 / 质量 / 安全                   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  6. 持续迭代（Continuous Improvement）           │
│     反馈 / 重新训练 / 模型更新                  │
└─────────────────────────────────────────────┘
```

---

## 三、6 大阶段工具全景图

| 阶段 | 开源工具 | 云服务 |
|------|---------|--------|
| **数据准备** | Label Studio / Argilla / Snorkel | Scale AI / Labelbox / AWS SageMaker Ground Truth |
| **训练** | Hugging Face / DeepSpeed / Axolotl | OpenAI Fine-tuning / AWS SageMaker / Vertex AI |
| **评估** | Ragas / DeepEval / LangSmith | Braintrust / LangSmith / Humanloop |
| **部署** | vLLM / TGI / Ollama / Triton | OpenAI API / Bedrock / Azure OpenAI / Together |
| **监控** | LangSmith / Helicone / Phoenix | Datadog / Dynatrace / Arize |
| **持续迭代** | Label Studio / Pipeline tools | AWS SageMaker Pipeline / Vertex AI Pipeline |

---

## 四、数据准备（核心阶段）

### 4.1 数据来源

| 来源 | 示例 |
|------|------|
| **业务数据** | 客服对话 / 工单 / 评论 |
| **人工标注** | Label Studio 标注 |
| **LLM 生成** | 用 GPT-4 生成训练数据 |
| **开源数据** | Hugging Face Datasets |
| **用户反馈** | 真实用户标注（点赞/点踩）|

### 4.2 数据格式

```json
{
  "messages": [
    {"role": "system", "content": "你是专业律师"},
    {"role": "user", "content": "什么是合同违约？"},
    {"role": "assistant", "content": "合同违约是指..."}
  ]
}
```

### 4.3 数据质量

```
数量：1 万+ 条（Fine-tuning 起步）
质量：人工抽检 5% 看准确率
多样性：覆盖各种场景
合规：去除 PII（个人身份信息）
```

---

## 五、模型训练

### 5.1 3 种训练方式

| 方式 | 显存 | 数据量 | 成本 |
|------|------|--------|------|
| **Full Fine-tuning** | 100+ GB | 10 万+ | $$$$$ |
| **LoRA** | 16-24 GB | 1000+ | $$$ |
| **QLoRA** | 8-12 GB | 1000+ | $$ |
| **Prompt Tuning** | 1 GB | 100+ | $ |

### 5.2 主流训练框架

| 框架 | 特点 | 适用 |
|------|------|------|
| **Hugging Face Transformers** | 通用 | 几乎所有场景 |
| **Axolotl** | YAML 配置 | 快速微调 |
| **LLaMA-Factory** | 中文友好 | 中文 LLM |
| **DeepSpeed** | 大模型分布式 | 100B+ 模型 |
| **Unsloth** | 2x 速度 | 显存紧张 |

### 5.3 QLoRA 示例

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    load_in_4bit=True,                # 4-bit 量化
    device_map="auto"
)

lora_config = LoraConfig(
    r=16,                              # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 8,388,608 || all params: 8,030,261,248 || trainable%: 0.10%
```

---

## 六、模型评估

### 6.1 4 大评估维度

| 维度 | 说明 | 工具 |
|------|------|------|
| **准确性** | 答对了没 | 自动化评测 + 人工 |
| **相关性** | 答得切题没 | LLM-as-Judge |
| **安全性** | 有害内容没 | 内容审核 API |
| **成本** | Token / 延迟 | 自建监控 |

### 6.2 评估方法

| 方法 | 说明 | 适用 |
|------|------|------|
| **自动化指标** | BLEU / ROUGE / Exact Match | 标准化 |
| **LLM-as-Judge** | 用 GPT-4 评估其他模型 | 复杂任务 |
| **人工评估** | 标注员打分 | 关键场景 |
| **A/B Test** | 真实用户投票 | 生产验证 |
| **黄金集** | 预先标注的标准答案 | 持续回归 |

### 6.3 Ragas 评估 RAG 实战

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

result = evaluate(
    dataset,
    metrics=[
        faithfulness,            # 答案忠实于检索
        answer_relevancy,        # 答案相关性
        context_precision        # 检索精度
    ]
)
print(result)
```

---

## 七、模型部署

### 7.1 4 种部署方式

| 方式 | 成本 | 适用 |
|------|------|------|
| **API 托管** | 💰 按 Token | 中小企业 / 快速上线 |
| **自托管 vLLM** | 💰💰 GPU 成本 | 大企业 / 数据合规 |
| **Serverless（Together）** | 💰 弹性 | 流量波动 |
| **边缘部署（Ollama）** | 💰💰 本地 | 隐私 / 离线 |

### 7.2 vLLM 高性能推理

```bash
# 启动 vLLM 服务
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3-8B-Instruct \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9
```

**性能**：vLLM 比 HuggingFace Transformers 快 24 倍（continuous batching）。

### 7.3 OpenAI 兼容 API

```python
# 部署后用 OpenAI 客户端调用
from openai import OpenAI

client = OpenAI(
    base_url="http://vllm:8000/v1",  # 自托管 vLLM
    api_key="dummy"
)
response = client.chat.completions.create(
    model="meta-llama/Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 7.4 K8s + vLLM 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args:
        - --model=meta-llama/Llama-3-8B-Instruct
        - --tensor-parallel-size=2
        resources:
          limits:
            nvidia.com/gpu: 2
        ports:
        - containerPort: 8000
```

---

## 八、监控与可观测

### 8.1 4 大监控维度

| 维度 | 关键指标 |
|------|---------|
| **性能** | P50/P99 延迟 / QPS |
| **成本** | Token 用量 / GPU 利用率 / $ |
| **质量** | 答案准确率 / 幻觉率 / 拒绝率 |
| **安全** | 有害请求数 / 注入攻击数 |

### 8.2 LangSmith 监控

```python
from langsmith import traceable

@traceable(run_type="llm")
def my_llm_call(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### 8.3 Prometheus + Grafana

```python
from prometheus_client import Counter, Histogram

llm_tokens = Counter('llm_tokens_total', 'Total LLM tokens', ['model'])
llm_latency = Histogram('llm_latency_seconds', 'LLM latency', ['model'])

@llm_latency.time()
def call_llm(prompt):
    response = client.chat.completions.create(model="gpt-4", messages=[...])
    llm_tokens.labels(model="gpt-4").inc(response.usage.total_tokens)
    return response
```

---

## 九、持续迭代

### 9.1 反馈闭环

```
用户反馈 → 数据收集 → 数据标注 → 重新训练 → 评估 → 部署
   ↑                                              ↓
   └─────────── 持续监控 ─────────────────────┘
```

### 9.2 何时重新训练

- 模型效果下降（用户投诉增加）
- 业务数据分布变化（数据漂移）
- 新版本基模发布（升级）
- 定期重训（建议每 3-6 个月）

### 9.3 影子模式（Shadow Mode）

```
新模型 v2 接收所有流量，但不返回给用户
用户收到的还是 v1 的答案
后台对比 v1 vs v2 的差异
   ↓
验证 v2 效果更好后，再切流量
```

---

## 十、最佳实践

1. **数据为王**：准备 1 万+ 高质量数据，比选模型更重要
2. **先 Prompt 后 RAG 后 Fine-tuning**：80% 任务用 Prompt 就够
3. **QLoRA 优先**：消费级显卡（24GB）能微调 7B-13B 模型
4. **vLLM 高性能部署**：比原生快 24 倍
5. **全面监控**：性能 / 成本 / 质量 / 安全 4 维
6. **A/B Test**：每次模型更新小流量验证
7. **影子模式**：高风险场景用影子模式
8. **成本控制**：缓存 / 路由 / 量化 三大手段

---

← [返回 AI 知识体系总览](../../README.md) · 📅 2026-06-28