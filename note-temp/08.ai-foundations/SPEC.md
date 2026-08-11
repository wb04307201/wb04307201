# SPEC for note-temp/08.ai-foundations/

> **Inherits from**: [../SPEC.md](../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-11

---

## 模块定位

AI 基础：传统 ML + 深度学习 + Transformer + LLM 基础 + Tokenization/Embedding。

## 从 L0 继承

- G1-G6 通用评分维度
- 11 类基础扫描规则
- 命名约定 + commit 格式 + 互链规则

## 本模块规则

### 评估维度（追加 G 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| C1 | 量化严谨性 | 有公式/数字 + 变量定义清晰 | 有数字缺公式 | 纯定性 |
| C2 | 架构对比表 | 多维对比表（≥3 维） | 有对比不完整 | 无对比 |
| C3 | 学术/开源引用 | 有论文链接或开源项目引用 | 提及无链接 | 无引用 |

### 写作要求

- 数学公式用 KaTeX/Markdown 块
- 引用论文给 arXiv 链接
- 概念演进有时间线

### 子目录约定

- `01-ml/` 传统机器学习
- `02-deep-learning/` 深度学习基础
- `03-transformer/` Transformer 架构
- `04-llm/` LLM 基础
- `05-tokenization-embedding/` Tokenization + Embedding
