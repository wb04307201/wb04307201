<!--
module:
  number: 02
  slug: cs-foundations
  topic: 计算机科学基础
  audience: 工程师 / SRE / 学生
  category: 主模块
  summary: 系统性整理计算机科学基础知识，涵盖算法、操作系统、网络、运维与知识产权等核心领域。
-->

# 02. CS Foundations（计算机科学基础）

> **定位**：系统性整理计算机科学基础知识，涵盖算法、操作系统、网络、运维与知识产权等核心领域。
> **继承规范**：[SPEC.md](./SPEC.md)

## 目录导航

| # | 子目录 | 主题 |
|---|--------|------|
| 1 | [01-algorithms/](./01-algorithms/) | 算法（复杂度 · 经典策略 · 字符串 · 优化 · ML 基础） |
| 2 | [02-os/](./02-os/) | 操作系统 + Linux（进程 · 内存 · 调度 · 文件系统 · 常用命令） |
| 3 | [03-network/](./03-network/) | 计算机网络（OSI/TCP-IP · HTTP · DNS · HTTPS/TLS · 协议族） |
| 4 | [04-operations/](./04-operations/) | 运维（服务器性能指标 · 云服务模式） |
| 5 | [05-ipr/](./05-ipr/) | 知识产权（专利 vs 软件著作权） |

> 注：04-operations（运维）与 05-ipr（知识产权）严格意义上不属于"cs-foundations"内核，但 brief 要求 move ALL `02.computer-basics/*` → 本模块，故作为子目录保留。

## 适用人群

- **后端 / 全栈工程师**：网络协议、Linux 命令、性能监控是日常基础
- **运维 / SRE**：服务器指标、云服务选型、生产故障排查
- **求职 / 在校生**：算法复杂度、TCP/IP 模型、HTTP 演进是高频面试题
- **创业者 / 独立开发者**：知识产权保护（专利与软著的差异与申请策略）

## 学习路径

- **新人入门**：网络 → 算法 → Linux → 操作系统（搭建"日常开发 + 面试"基础底盘）
- **运维方向**：Linux → 运维 → 操作系统（文件系统/I/O） → 网络（深入协议栈与监控指标）
- **求职冲刺**：算法（复杂度 + 经典案例）→ 网络（TCP/HTTP/DNS）→ 操作系统（进程/内存/I/O 模型）→ 知识产权（开放题）
- **速查定位**：按需查阅各分类 README 速查表

## 🔗 相关章节

- 上游：本模块是所有技术模块的基础
- 关联：[`04.spring-backend`](../04.spring-backend/) — 后端工程（网络/算法知识的上层应用）
- 关联：[`06.distributed-systems`](../06.distributed-systems/) — 分布式系统（OS/网络知识的工程化）
- 关联：[`07.devops-and-tools`](../07.devops-and-tools/) — 工具链（Linux/网络命令的实战工具）

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 分类主题数 | 5 | 顶层 5 个分类目录（算法 / OS / 网络 / 运维 / 知识产权） |
| 子 README 总数 | 25 | 含 5 个分类 README + 20 个 leaf README（depth ≥ 2） |
| 含 frontmatter 的 README | 待统计 | Phase 2+ 验证 |
| 配套面试题 | 13 篇 | `12.interview/02.computer-basics/` 9 个兄弟（tcp-handshake / sse-vs-websocket / sensitive-word-filter / greedy-algorithms / machine-learning × 6 等） |

> **统计时间戳**：2026-08-12（Plan 2 Task 1 完成）

---

← [返回 note 总目录](../README.md)
