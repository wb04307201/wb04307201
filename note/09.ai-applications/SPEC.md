
# SPEC for note/09.ai-applications/

> **Inherits from**: [../SPEC.md](../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-11

---

## 模块定位

AI 应用层：RAG、Agent、Prompt、LLM 推理工程、Fine-tuning、Eval。

## 从 L0 继承

- G1-G6 通用评分维度
- 11 类基础扫描规则
- 命名约定 + commit 格式 + 互链规则

## 本模块规则

### 评估维度（追加 G 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| C4 | 实战部署指导 | 有场景化推荐（"X 场景用 Y"） | 有泛泛建议 | 无部署 |
| C5 | 框架对比 | 多框架横向对比 + 选型建议 | 有对比无建议 | 无对比 |
| C6 | 性能基准 | 有 benchmark 数据 + 调优前后对比 | 有数据无对比 | 无基准 |

### MOC 子目录约定

复杂主题用 MOC 目录：
- `rag/` — RAG 全景（检索 / rerank / 生成 / 评估 / 生产 / 前沿）
- `agent/` — Agent 框架（ReAct / Plan-Execute / Multi-Agent）
- `prompts/` — Prompt 工程
- `llm-inference/` — LLM 推理优化
- `fine-tuning/` — 微调方法
- `eval/` — 评估方法

每个 MOC 目录下用数字编号原子笔记（如 `01-retrieval.md`）。

### 互链要求

- MOC 的 README.md 必须链向所有原子笔记
- 每个原子笔记必须回链 MOC README + 至少 2 个相关原子