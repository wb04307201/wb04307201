<!--module:
  parent: 08.ai-foundations
  slug: 08.ai-foundations/02-deep-learning
  type: index-only
  category: AI 基础索引
  summary: 深度学习基础——主流框架对比（PyTorch / TensorFlow / MindSpore / PaddlePaddle）、训练范式与生产部署。
-->

# 02. 深度学习

## 📍 一句话定位

> 工程选型的决策轴——从 PyTorch 的学术灵活到 TensorFlow 的工业部署，再到 MindSpore / PaddlePaddle 的国产化生态，构建"研究 → 训练 → 部署"全链路认知。

## 🎯 子模块简介

`02-deep-learning/` 聚焦**深度学习工程落地的三大支柱**：

- **主流框架对比**：PyTorch（Meta，学术首选）、TensorFlow（Google，工业首选）、MindSpore（华为，国产化首选）、PaddlePaddle（百度，产业首选）——四分天下的市场格局与选型决策。
- **训练范式**：监督训练 / 预训练-微调 / 分布式训练（数据并行、模型并行、流水线并行）/ 混合精度（FP16 / BF16）——不同模型规模对应不同范式。
- **生产部署**：模型压缩（量化、剪枝、蒸馏）、推理引擎（TensorRT、ONNX Runtime、vLLM）、端边云协同（TensorFlow Lite、MindSpore Lite）——从实验室到工业级落地的最后一公里。

本节是连接"理论 Transformer"与"工业 LLM"的桥梁——01-ml 是地基，03-transformer 是核心组件，本节是工程工具链。

## 🗂️ 文章清单

| 标题 | 路径 | 状态 | 摘要 |
|------|------|------|------|
| 深度学习框架 | [deep-learning-frameworks.md](./deep-learning-frameworks.md) | ✅ 已完成（76 行） | 对比 MindSpore / PyTorch / TensorFlow / PaddlePaddle 的定位、特点、选型建议和 2025-2026 发展趋势。 |

> **覆盖说明**：当前 `02-deep-learning/` 仅沉淀 1 篇（deep-learning-frameworks.md），覆盖四框架对比与选型建议；Transformer 训练技巧与分布式训练是工程落地的核心，建议尽快补齐。

## 🔗 关联主题

- **父模块**：[08.ai-foundations](../README.md) — AI 基础层总索引
- **同模块相邻**：[01-ml](../01-ml/README.md) — 传统 ML 算法底座
- **同模块相邻**：[03-transformer](../03-transformer/README.md) — Transformer 架构核心
- **AI 工程实战**：[`09.ai-applications/fine-tuning`](../../09.ai-applications/fine-tuning/) — LLM 预训练与微调实践
- **项目沉淀**：[spring-ai-loomagent](https://github.com/wb04307201/spring-ai-loomagent) — Spring AI 集成框架

## 📚 学习路径

1. **入门**：阅读 [deep-learning-frameworks.md](./deep-learning-frameworks.md)，建立四框架对比脑图
2. **选型决策**：根据团队技术栈、硬件环境、部署需求选择框架（学术 → PyTorch / 国产化 → MindSpore / 工业 → TensorFlow）
3. **训练技巧**：补充 Transformer 训练专题，重点掌握 AMP、Gradient Accumulation、AdamW
4. **分布式训练**：补充分布式训练专题，理解 DDP / TP / PP / 3D 并行的适用场景
5. **深度学习理论**：跳转 [03-transformer](../03-transformer/README.md) 看核心架构
6. **工程落地**：跳转 [09.ai-applications/fine-tuning](../../09.ai-applications/fine-tuning/) 看 LLM 微调实战

## 📊 本节统计

- **子目录总数**：1 个（02-deep-learning/）
- **已沉淀文章**：1 篇（deep-learning-frameworks.md）
- **待补占位**：2 篇（Transformer 训练技巧 / 分布式训练）
- **总行数**（不含 README）：约 76 行
- **最后更新**：2026-08-20

---

← [返回 08.ai-foundations](../README.md)
