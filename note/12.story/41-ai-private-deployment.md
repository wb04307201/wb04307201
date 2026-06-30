<!--
story:
  number: 41
  type: 续集
  position: 续集十七
  title: 自建中央厨房
  audience: AI 工程师 / 架构师
-->

# 41 · 自建中央厨房

> 从阿明的"OpenAI 又被封 + 数据不能出云"，看 AI 私有化部署 —— **5 大部署形态 + 4 大推理框架 + 量化 / 微调 / GPU 利用率 + 成本对比**

> **系列定位**：本篇是「阿明餐厅」系列的**续集十七**。在[续集十六 · 40 · AI 合规](./40-ai-compliance-and-regulation.md)我们讲了数据出境的合规要求。在[续集十二 · 36a 成本结构](./36a-ai-token-cost-structure.md)我们讲了 LLM API 的成本。本篇是**AI 模型私有化部署专题** —— 当你不能或不想用 OpenAI API 时，怎么在自有环境部署 LLM。从单 GPU 到分布式，从量化到微调，从性能到成本。

---

## 引言：阿明的"OpenAI 封号 + 数据出云"双危机

> **阿明的厨房类比（开篇场景）**：阿明的餐厅用着"外卖大厨"（OpenAI API）做菜 —— 顾客点单后，订单发给 OpenAI 大厨，做好的菜通过快递送回。突然有一天，OpenAI 快递公司说"你的地址被列入风控名单了，暂停配送 7 天"！80 家分店的"AI 厨师"全部瘫痪。这就是阿明面临的"AI 厨房双危机"—— 外部依赖（API）+ 数据合规（数据出云）。

2026 年初，阿明餐厅遇到两场危机：

```text
危机 1：OpenAI 封号
  - 中国 IP 大量访问触发风控
  - 账号被封 7 天
  - 业务全停（AI 客服、推荐、内容生成）
  - 损失：日均 30 万

危机 2：合规要求
  - 中国《数据出境安全评估办法》生效
  - 用户数据不能出云
  - 必须私有化
  - 法务部下达最后通牒
```

老陈当机立断：**3 个月内完成核心 AI 系统的私有化部署**。本篇就是这次"私有化战役"的完整复盘。

---

> **阿明的厨房类比（第一章）**：阿明要做个决策 —— 继续叫"外卖大厨"（OpenAI API，便宜但有风险），还是"自建厨房"（私有化部署，贵但稳定）。这就像开餐厅 —— 一直叫外卖还是开中央厨房？本章阿明用 5 维度决策矩阵，帮你判断什么时候应该私有化。

## 第一章：私有化 vs API 决策 —— 自建厨房还是叫外卖

### 1.1 决策矩阵

| 维度 | API（公有云） | 私有化（自建） |
|------|--------------|----------------|
| **数据合规** | ❌ 数据出云 | ✅ 数据不出域 |
| **初期成本** | ✅ 低（0 投入） | ❌ 高（GPU + 运维） |
| **长期成本** | ❌ 高（按 token 计费） | ✅ 低（一次投入持续使用） |
| **性能** | ✅ 顶级模型 | ⚠️ 取决于硬件 |
| **可控性** | ❌ 黑盒 | ✅ 完全可控 |
| **稳定性** | ⚠️ 依赖供应商 | ✅ 自主可控 |
| **定制化** | ⚠️ 仅 Fine-tuning | ✅ 深度定制 |
| **运维** | ✅ 零运维 | ❌ 高运维 |

### 1.2 何时选择私有化？

```text
必须私有化：
  1. 数据合规要求（金融 / 医疗 / 政府）
  2. 业务核心（离了 AI 业务停摆）
  3. 大规模调用（> 1 亿 token/月，私有化更便宜）
  4. 深度定制（Fine-tuning 满足不了）
  5. 网络不稳定（API 经常断）

可继续用 API：
  1. 早期原型（< 100 万 token/月）
  2. 非核心功能（辅助性 AI）
  3. 临时性需求（一次性 / 短期）
  4. 缺乏 GPU 资源
  5. 缺乏运维能力
```

### 1.3 阿明的决策

```text
阿明的私有化策略（4 阶段）：

阶段 1（核心 + 高频）：
  - 推荐系统（每日 100 万次调用）
  - 客服系统（每日 50 万次调用）
  - → 私有化（Qwen 2.5-72B）

阶段 2（核心 + 中频）：
  - 内容审核
  - 文档摘要
  - → 私有化（Qwen 2.5-32B）

阶段 3（辅助 + 低频）：
  - 数据分析
  - 报表生成
  - → 继续用 API（GPT-4o-mini）

阶段 4（兜底）：
  - 复杂推理
  - 创意内容
  - → 继续用 API（Claude / GPT-4o）
```

---

> **阿明的厨房类比（第二章）**：决定自建厨房后，阿明要选"建多大"—— 一口小灶（单 GPU / 试菜）、三口灶（多卡 / 小店）、大型厨房（GPU 集群 / 中央厨房）、混合厨房（私有云 + 公有云 / 联营）、移动餐车（边缘部署 / 流动）。5 种开店方案的成本和规模都不一样。

## 第二章：5 大部署形态 —— 从单灶小馆到中央厨房，五种开店方案

### 2.1 形态 1：单 GPU 服务器

```text
硬件：1-4 张 A100 / H100
适合：
  - 7B-13B 模型
  - 中小规模（日均 < 100 万次）
  - 早期验证

成本：
  - 一次性：30-100 万
  - 年运维：10-20 万
  - 单价：约 0.0003 元/千 token（Qwen 7B）

优势：
  - 简单（单机部署）
  - 成本低
  - 适合中小公司

劣势：
  - 单点故障
  - 性能有限
  - 难扩展
```

### 2.2 形态 2：多 GPU 服务器（单机多卡）

```text
硬件：8-16 张 H100（如 NVIDIA DGX H100）
适合：
  - 70B 模型（张量并行）
  - 中大规模
  - 高吞吐

工具：
  - vLLM（张量并行）
  - TensorRT-LLM
  - DeepSpeed

成本：
  - 一次性：200-500 万
  - 年运维：30-50 万
  - 单价：约 0.0005 元/千 token（Qwen 72B）
```

### 2.3 形态 3：GPU 集群

```text
硬件：多台 GPU 服务器 + 高速网络（InfiniBand）
适合：
  - 100B+ 模型
  - 大规模（日均 > 1000 万次）
  - 高可用

部署：
  - Kubernetes + GPU Operator
  - 多机张量并行
  - Pipeline 并行

成本：
  - 一次性：1000-5000 万
  - 年运维：200-500 万
  - 单价：约 0.0008 元/千 token
```

### 2.4 形态 4：私有云 + 公有云混合

```text
架构：
  - 私有化：核心 + 敏感
  - 公有云：弹性 + 峰值
  - API：兜底

适合：
  - 业务波动大
  - 突发流量
  - 灾备需求

工具：
  - Kong / APISIX（API 网关）
  - 自研流量调度
  - 多云管理平台
```

### 2.5 形态 5：边缘部署

```text
硬件：消费级 GPU / NPU / 端侧芯片
适合：
  - 小模型（1B-7B）
  - 离线场景
  - 低延迟要求

部署：
  - Ollama（Mac / Linux）
  - LM Studio（桌面）
  - llama.cpp（CPU 推理）
  - MNN / NCNN（移动端）

应用：
  - 端侧智能助手
  - 离线翻译
  - 智能客服终端
```

---

> **阿明的厨房类比（第三章）**：厨房建好了，要选"智能灶品牌" —— vLLM（米其林首选）、TensorRT-LLM（性能最强）、DeepSpeed-MII（微软生态）、TGI（HuggingFace）。每个品牌擅长的"菜系"不同 —— 凉菜 / 热菜 / 汤品 / 甜点。本章阿明对比 4 大品牌"智能灶"。

## 第三章：4 大推理框架对比 —— 四大品牌灶台，哪个炒菜最快

### 3.1 总览对比表

| 框架 | 厂商 | 强项 | 弱项 | 适合 |
|------|------|------|------|------|
| **vLLM** | UC Berkeley | 吞吐高（PagedAttention） | 显存占用高 | 通用首选 |
| **TensorRT-LLM** | NVIDIA | 性能最强 | 仅 NVIDIA | 高性能 |
| **DeepSpeed-MII** | Microsoft | 易用 + 集成好 | 性能略弱 | 微软生态 |
| **TGI** | HuggingFace | 易用 + 兼容性好 | 性能中等 | 快速起步 |

### 3.2 vLLM（推荐首选）

```bash
# 安装
pip install vllm

# 启动（Qwen 2.5-72B，4 卡 A100）
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct \
    --tensor-parallel-size 4 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 32768 \
    --port 8000

# 调用（OpenAI 兼容 API）
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "messages": [{"role": "user", "content": "你好"}]
    }'
```

**vLLM 优势：**
- PagedAttention：显存利用率提升 4x
- 连续批处理：吞吐提升 10-20x
- OpenAI 兼容：迁移成本低
- 动态批处理：高并发友好

**实测性能（A100 80G ×4）：**
- Qwen 2.5-72B：约 50 tokens/秒/用户
- 并发 100 用户：吞吐 5000 tokens/秒

### 3.3 TensorRT-LLM（性能最强）

```python
import tensorrt_llm
from tensorrt_llm import LLM, SamplingParams

# 编译（首次需要）
llm = LLM(model="Qwen/Qwen2.5-72B-Instruct")

# 推理
sampling_params = SamplingParams(temperature=0.7, max_tokens=512)
output = llm.generate(["你好，请介绍阿明餐厅"], sampling_params)
print(output[0].outputs[0].text)
```

**TensorRT-LLM 优势：**
- 性能最强（NVIDIA 优化到极致）
- 支持 INT8 / FP8 量化
- 内核融合优化

**劣势：**
- 编译时间长（首次 30+ 分钟）
- 仅支持 NVIDIA GPU
- 配置复杂

### 3.4 DeepSpeed-MII（微软生态）

```python
import mii

# 部署
mii.serve("Qwen/Qwen2.5-72B-Instruct", deployment_name="qwen_deploy")

# 推理
result = mii.inference("qwen_deploy", "你好")
print(result)
```

**优势：**
- 与 DeepSpeed 训练无缝衔接
- 支持多种优化（ZeRO / Tensor Parallel）
- 微软生态集成

### 3.5 TGI（HuggingFace）

```bash
# Docker 部署
docker run --gpus all -p 8080:80 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id Qwen/Qwen2.5-72B-Instruct \
    --num-shard 4
```

**优势：**
- 易用（一行命令启动）
- HuggingFace 模型直接用
- 文档好

---

> **阿明的厨房类比（第四章）**：大模型动辄几百 GB，普通的家用灶（消费级 GPU）根本装不下。本章阿明学会"把大菜切小份"（量化 INT8 / INT4 / AWQ / GGUF）—— 让小灶也能做大餐。本章是"硬件省钱"的关键技术。

## 第四章：模型量化与压缩 —— 大菜切小份，小灶也能做大餐

### 4.1 量化的必要性

```text
显存占用（Qwen 2.5-72B 为例）：
  - FP16（原始）：144 GB
  - INT8：72 GB
  - INT4：36 GB
  - INT4 + GPTQ：30 GB
  - INT4 + AWQ：28 GB

实际部署：
  - 1 张 A100 80G → INT4（72B 模型勉强）
  - 4 张 A100 80G → FP16（72B 模型）
  - 8 张 A100 80G → FP16 + 大 batch
```

### 4.2 量化方法对比

| 方法 | 精度 | 显存节省 | 性能损失 | 工具 |
|------|------|----------|----------|------|
| **FP16** | 原始 | 1x | 0% | - |
| **INT8 (GPTQ)** | 中 | 2x | 1-3% | AutoGPTQ |
| **INT4 (AWQ)** | 中 | 4x | 3-5% | AutoAWQ |
| **INT4 (GGUF)** | 中 | 4x | 3-5% | llama.cpp |
| **FP8** | 中 | 2x | < 1% | TensorRT-LLM |

### 4.3 AWQ 量化实战

```bash
# 安装 AutoAWQ
pip install autoawq

# 量化 Qwen 2.5-72B
python -m awq.entry --model_path Qwen/Qwen2.5-72B-Instruct \
    --w_bit 4 --q_group_size 128 \
    --run_awq --dump_awq \
    --output_dir ./Qwen2.5-72B-Instruct-AWQ

# 部署（vLLM 自动识别 AWQ）
python -m vllm.entrypoints.openai.api_server \
    --model ./Qwen2.5-72B-Instruct-AWQ \
    --quantization awq \
    --tensor-parallel-size 4
```

**实测（Qwen 2.5-72B + AWQ INT4）：**
- 显存：72 GB（4 张 A100 100% 满载）
- 性能：与 FP16 相比，P99 延迟 +5%
- 质量：评测分数下降 2-3%

### 4.4 GGUF 量化（CPU 推理）

```bash
# 转换模型
python convert.py Qwen/Qwen2.5-72B-Instruct \
    --outfile qwen2.5-72b.gguf \
    --outtype q4_K_M

# CPU 推理
./main -m qwen2.5-72b.gguf \
    -p "你好，请介绍阿明餐厅" \
    -n 512 -t 8
```

**适合：**
- 边缘设备
- 离线推理
- 极低成本

---

> **阿明的厨房类比（第五章）**：阿明想让"通用大厨"做出"阿明餐厅味"的红烧肉 —— 不是从零学，而是"老汤底加阿明的独家料"。这就是 LoRA 微调 —— 用 1% 的算力，调出 80% 的"阿明味"。本章讲怎么训练"阿明专属 AI 厨师"。

## 第五章：模型微调 —— 老汤底加新料，调出阿明味

### 5.1 微调方法对比

| 方法 | 显存 | 训练速度 | 数据量 | 适合 |
|------|------|----------|--------|------|
| **Full Fine-tuning** | 100% | 慢 | 多 | 充足资源 |
| **LoRA** | 10% | 中 | 中 | 通用首选 |
| **QLoRA** | 5% | 中 | 中 | 资源紧张 |
| **Prefix Tuning** | 1% | 快 | 少 | 快速适配 |
| **RLHF** | 100% | 慢 | 多 | 对齐训练 |

### 5.2 LoRA 微调实战

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载基础模型
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

# LoRA 配置
lora_config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 应用 LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 8,388,608 || all params: 7,625,439,744 || trainable%: 0.11%

# 训练
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./qwen-7b-lora-restaurant",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,  # 阿明餐厅数据集
    tokenizer=tokenizer,
)
trainer.train()

# 合并 LoRA 权重
model = model.merge_and_unload()
model.save_pretrained("./qwen-7b-restaurant")
```

### 5.3 阿明的微调策略

```text
阿明的数据集（5 万条）：
  - 客服对话：2 万条
  - 推荐理由：1 万条
  - 菜单描述：1 万条
  - 投诉处理：1 万条

微调参数：
  - 基础模型：Qwen 2.5-7B（中文 + 小巧）
  - 方法：LoRA（r=16）
  - 数据：5 万条
  - 训练：3 epoch / 8 A100 / 6 小时
  - 成本：300 元（GPU 租用）

微调效果：
  - 客服意图识别：85% → 95%
  - 推荐理由质量：4.2/5 → 4.6/5
  - 投诉处理满意度：70% → 88%
```

---

> **阿明的厨房类比（第六章）**：阿明的厨房上了智能灶，但发现"灶台火力才用 30%"（GPU 利用率低）—— 智能灶一会儿炒菜一会儿闲着。本章阿明学会"连续炒菜"（Continuous Batching）+ "提前备菜"（Prefetch）—— 让灶台火力全开，食材一点不浪费。

## 第六章：性能优化与 GPU 利用率 —— 灶台火力全开，食材一点不浪费

### 6.1 关键指标

```text
1. 吞吐（Throughput）：
  - tokens/秒（生成）
  - requests/秒（请求）
  - batch 大小 / 并发数

2. 延迟（Latency）：
  - TTFT（Time To First Token）：首 token 时间
  - TPOT（Time Per Output Token）：每 token 间隔
  - 总延迟

3. GPU 利用率：
  - GPU SM 利用率（> 70% 优秀）
  - 显存利用率（> 80% 优秀）
  - 通信开销（多卡时）

4. 成本：
  - $/百万 token
  - $/千次请求
  - ROI
```

### 6.2 6 大优化技巧

```text
1. 连续批处理（Continuous Batching）：
  - 工具：vLLM / TGI
  - 效果：吞吐 10-20x

2. PagedAttention：
  - 工具：vLLM
  - 效果：显存利用率提升 4x

3. KV Cache 优化：
  - 工具：vLLM / TensorRT-LLM
  - 效果：长上下文支持 + 2x 吞吐

4. 量化（INT8 / INT4）：
  - 效果：吞吐 2-3x，显存 2-4x

5. 预编译（TensorRT / AOT）：
  - 效果：首 token 时间 -50%

6. 推测解码（Speculative Decoding）：
  - 工具：vLLM
  - 效果：吞吐 2-3x（小模型 + 大模型组合）
```

### 6.3 GPU 利用率调优

```bash
# 1. 监控 GPU
nvidia-smi -l 1

# 2. 调整 batch size
python -m vllm.entrypoints.openai.api_server \
    --max-num-seqs 256 \  # 最大并发
    --max-num-batched-tokens 8192  # 最大 batch token

# 3. 调整显存分配
--gpu-memory-utilization 0.95  # 显存使用率（0-1）

# 4. 启用 chunked prefill
--enable-chunked-prefill

# 5. 启用 prefix caching
--enable-prefix-caching
```

### 6.4 阿明的优化效果

```text
优化前：
  - 硬件：8 × A100 80G
  - 模型：Qwen 2.5-72B FP16
  - 吞吐：500 tokens/秒
  - GPU 利用率：45%
  - 延迟 P99：2 秒

优化后：
  - 硬件：8 × A100 80G（不变）
  - 模型：Qwen 2.5-72B AWQ INT4
  - 吞吐：3000 tokens/秒（+500%）
  - GPU 利用率：85%
  - 延迟 P99：0.8 秒（-60%）

关键动作：
  1. FP16 → INT4（吞吐 2x）
  2. vLLM PagedAttention（吞吐 2.5x）
  3. 连续批处理（吞吐 1.5x）
  4. Prefix caching（首 token -50%）
  5. Speculative decoding（生成 2x）
```

---

> **阿明的厨房类比（第七章）**：5 年账单一算 —— 自建厨房（前 2 年投入 500 万装修 + 200 万厨师工资）vs 叫外卖大厨（每年 50 万 API 订阅）。本章阿明给你算清"自建 vs 外包"的 5 年 TCO，帮你做决策。

## 第七章：成本对比 —— 五年账单一算，自建还是外包一目了然

### 7.1 私有化 vs API 长期成本

```text
场景：每日 500 万 token 调用，Qwen 2.5-72B 质量水平

API 方案（GPT-4o）：
  - 单价：$5/M input + $15/M output
  - 日均成本：500 万 × 0.6（input+output 加权）÷ 100 万 × $10 = $30
  - 年成本：$30 × 365 = $10,950 = 7.7 万 RMB
  - 5 年总成本：38.5 万 RMB

私有化方案（自建 GPU）：
  - 一次性：300 万（4 × A100 80G 服务器）
  - 年运维：50 万（电费 + 运维 + 机房）
  - 5 年总成本：300 + 50 × 5 = 550 万

对比：
  - 5 年内 API 成本 < 私有化成本
  - 但私有化后单 token 成本几乎为 0
  - 6 年后开始，私有化优势显现

阿明的决策：
  - 短期（< 1 年）：API
  - 中期（1-3 年）：混合（核心私有化 + 辅助 API）
  - 长期（> 3 年）：全私有化
```

### 7.2 阿明的成本优化路径

```text
第 1 年（2026）：
  - 私有化：70%（核心 4 个场景）
  - API：30%（辅助 + 兜底）
  - 总成本：250 万

第 2 年（2027）：
  - 私有化：85%（再私有化 3 个场景）
  - API：15%
  - 总成本：300 万（含扩容）

第 3 年（2028）：
  - 私有化：95%
  - API：5%
  - 总成本：280 万（规模效应）

总成本：830 万
对比"全 API"：1800 万
节省：54%
```

---

> **阿明的厨房类比（第八章）**：80 家分店，如果 A 店厨房停电了怎么办？阿明学"双厨房备灶" —— A 店 + B 店互为备份（同城双活），跨城市再备份（异地容灾）。本章阿明建"AI 厨房的灾备体系"。

## 第八章：高可用与灾备 —— 双厨房备灶，一家停电照样上菜

### 8.1 高可用架构

```text
1. 流量调度层：
  - API 网关（Kong / APISIX）
  - 健康检查
  - 流量切换

2. 推理服务层：
  - 多个推理实例
  - 负载均衡
  - 自动重启

3. 模型层：
  - 模型版本管理
  - A/B 测试
  - 灰度发布

4. 监控层：
  - GPU 监控
  - 推理延迟
  - 业务指标
```

### 8.2 灾备方案

```text
1. 同城双活：
  - 两个机房
  - 流量分担
  - 故障自动切换

2. 异地灾备：
  - 主机房 + 备份机房（500 公里外）
  - 数据同步（10 秒级）
  - RTO < 5 分钟

3. 公有云兜底：
  - 私有化故障时切到 API
  - 成本高但保业务
  - 自动切换 + 人工确认
```

---

## 核心总结：AI 私有化全景

| 维度 | 核心内容 | 关键工具/方法 |
|------|----------|---------------|
| **决策** | 何时私有化 | 见第一章 |
| **5 大形态** | 单 GPU / 多卡 / 集群 / 混合 / 边缘 | 见第二章 |
| **4 大框架** | vLLM / TensorRT-LLM / DeepSpeed / TGI | 见第三章 |
| **量化** | INT8 / INT4 / AWQ / GGUF | 见第四章 |
| **微调** | LoRA / QLoRA / Full FT | 见第五章 |
| **性能** | 6 大优化 + GPU 利用率 | 见第六章 |
| **成本** | 5 年 TCO 对比 | 见第七章 |
| **高可用** | 双活 / 灾备 / 兜底 | 见第八章 |

### 一句心法

**AI 私有化不是"为了私有而私有"，而是"为了业务可控"**：合规 + 成本 + 可控的三方平衡。**前期用 API 起步，中期混合部署，长期核心私有化** 是大多数企业的最佳路径。

---

## 延伸阅读

- [AI 成本结构 36a](./36a-ai-token-cost-structure.md) / [36b 成本优化](./36b-ai-token-cost-optimization.md) —— 续集十二，私有化 vs API 成本对比
- [AI 合规与监管 40](./40-ai-compliance-and-regulation.md) —— 续集十六，数据出境的合规要求
- [可观测性 37](./37-ai-observability.md) —— 续集十三，私有化部署的监控
- [RAG 38](./38-rag-retrieval-augmented-generation.md) —— 续集十四，私有化 RAG 系统
- [向量数据库 39](./39-vector-database-and-embedding.md) —— 续集十五，私有化向量库

---

## 跨章节衔接

- 11.ai/02-technology-stack/README.md —— AI 技术栈 —— 推理框架选型
- 11.ai/03-engineering/ai-platforms/README.md —— AI 平台 —— 私有化部署
- 11.ai/04-operation/ai-ops/README.md —— AI 运维 —— 私有化 GPU 运维

---

## 结语

阿明完成 4 阶段私有化部署后，效果立竿见影：

```text
6 个月成果：
  - 核心 4 个 AI 场景 100% 私有化
  - 累计节省成本 50%
  - 数据零出境
  - 推理延迟降低 60%
  - 业务连续性 99.99%

关键动作 6 条：
  1. 先核心后辅助（推荐 + 客服先私有化）
  2. vLLM + AWQ INT4 黄金组合
  3. LoRA 微调提升业务效果
  4. 连续批处理 + Prefix caching 提升吞吐
  5. 公有云 API 兜底
  6. 双机房 + 异地灾备
```

下次当你考虑私有化时，不妨问自己：

- 我的**数据合规要求**是什么？**必须私有化吗**
- 我的**调用量**有多大？**月均 1 亿 token 是分水岭**
- 我的**硬件预算**是多少？**300 万是入门门槛**
- 我的**运维能力**如何？**需要 MLOps 团队**
- 我的**模型选型**是什么？**Qwen / Llama / GLM**
- 我的**推理框架**？**vLLM 首选**
- 我需要**量化**吗？**INT4 是平衡点**
- 我需要**微调**吗？**LoRA 是性价比首选**
- 我的**灾备方案**？**同城双活 + API 兜底**
- 我的**成本预期**？**3 年回本**

> 好的 AI 私有化设计，不是"砸钱买 GPU"，而是"业务驱动 + 渐进式 + 度量驱动"。**先量后建，先测后上，先核心后边缘，先试点后规模**。这是 AI 私有化的"四先四后"原则。

---

## 延伸阅读（2026 新增）

- 续集十八：[`44-ai-engineer-responsibility`](./44-ai-engineer-responsibility.md) —— **私有化场景下的责任分工**：私有化后谁负责运维、谁负责安全、谁负责更新
- 续集十九：[`45-ai-productivity-paradox`](./45-ai-productivity-paradox.md) —— **私有化的 ROI 真相**：DORA 放大器理论告诉你私有化是否值得
- 续集十二：[`36b-ai-token-cost-optimization`](./36b-ai-token-cost-optimization.md) —— **私有化的成本优化**：5 层路由 + 3 级缓存 + 4 策略压缩

← [返回系列导读](./index.md)