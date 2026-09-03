<!--
module:
  number: 00
  slug: note-root
  topic: note 总目录（L0 导航）
  type: index
  audience: 所有读者
  category: 主入口
  summary: 13 个主模块的知识库总目录（L0 导航），1106 个 .md 文档，frontmatter 覆盖 93.8%（含 module/question/story 三类），含全局 SPEC 规范与 13 模块导航。
-->

# note 总目录

> **定位**：13 模块体系化技术知识库（基于 Obsidian 维护）
> **全局规范**：[SPEC.md](./SPEC.md)
> **状态**：v19 月度抽样 100% 闭环（5 维准确度连续 3 轮 v17/v18/v19 = 100%）

---

## 一、仓库健康度（2026-09-02 实测）

| 维度 | 数值 | 备注 |
|------|------|------|
| **总 .md** | **1106** | 排除 `.health-tmp` / `.obsidian` |
| **总 README** | **785** | 13 模块 + 子目录 |
| **frontmatter 覆盖** | **93.8%**（1037/1106）| module 760 + question 227 + story 50 = 1037 |
| **结构断链** | **0** | Session 6 修复 230 处断链后闭环 |
| **orphan 目录** | **0** | 父 README 100% 回链 |
| **实质弱关联** | **0** | 235 处合规模板导航保留（G4 合规）|
| **5 维深度准确度** | **100%** | v18 校准 80 篇 + v19 月度 19 篇全过 |

## 二、13 模块导航

| # | 模块 | 主题 | 子 README |
|:-:|------|------|:---:|
| 01 | [01.java-and-jvm](./01.java-and-jvm/) | Java 基础 + JVM + 并发 + 设计模式 | 117 |
| 02 | [02.cs-foundations](./02.cs-foundations/) | 算法 + OS + 网络 + 数学 | 43 |
| 03 | [03.data-stack](./03.data-stack/) | 数据库 + 缓存 + 大数据 | 33 |
| 04 | [04.spring-backend](./04.spring-backend/) | Spring 生态 + 后端框架 | 141 |
| 05 | [05.frontend](./05.frontend/) | 前端工程 | 57 |
| 06 | [06.distributed-systems](./06.distributed-systems/) | 分布式 + 微服务 + 云原生 | 161 |
| 07 | [07.devops-and-tools](./07.devops-and-tools/) | DevOps + CI/CD + 工具链 | 47 |
| 08 | [08.ai-foundations](./08.ai-foundations/) | ML + DL + Transformer + LLM 基础 | 13 |
| 09 | [09.ai-applications](./09.ai-applications/) | RAG + Agent + Prompt + LLM 推理 | 133 |
| 10 | [10.business-systems](./10.business-systems/) | 业务系统速查（电商/社交/金融等） | 38 |
| 11 | [11.product-and-pm](./11.product-and-pm/) | 产品 + PM（Product & PM）| 12 |
| 12 | [12.interview](./12.interview/) | 高频面试题（**227 篇**）| 239 |
| 13 | [13.story](./13.story/) | 「阿明餐厅」技术系列（**50 篇**）| 1 |

## 三、3 大沉淀模式

- **单文件**（< 150 行）：主模块子 README
- **双层**（最常用）：`12.interview/<topic>/` + 对应主模块 `<topic>/` + 互链回指
- **三层 + 13.story 联动**：双层 + `13.story/<NN>-xxx.md` 章节反向链

## 四、CI 状态

| Workflow | 触发 | 状态 |
|----------|------|------|
| [grs.yml](../.github/workflows/grs.yml) | 每月 1 日 02:00 | README 卡片更新 |
| [difficulty-calibration.yml](../.github/workflows/difficulty-calibration.yml) | 每月 1 日 03:00 + PR | 5 维校准 + auto-calibrate |
| [structural-link-check.yml](../.github/workflows/structural-link-check.yml) | 每月 1 日 06:00 + PR | 内部路径校验 |

**5 层防护**（含本地 hook）：
- L1 commit-msg（Conventional Commits + 数字警告）
- L2 pre-commit（staged note/*.md 链接）
- L3 §7.2 自检（orchestrator）
- L4 GH Actions（PR 合并前）
- L5 月度 cron（全库扫描）

## 五、关键 Skill

`../skills/` 下 3 个项目级 skill：

| Skill | 何时用 |
|-------|--------|
| `note-precipitation-planning` | 用户问"X 应该沉淀到 note 什么位置" |
| `note-health` | 用户问"note 哪里需要优化" / "这篇文章质量怎么样" |
| `note-knowledge-qa` | 用户问技术问题，从 note/ 检索回答 |

## 六、写作规范入口

- [SPEC.md](./SPEC.md) — 全局规范（命名 / commit / 互链 / frontmatter / G1-G6 评分）
- 各模块自有 SPEC（11/12/13 等已落地）
- [QUESTION-FORMAT-SPEC.md](./12.interview/QUESTION-FORMAT-SPEC.md) — 面试题格式
- [STORY-FORMAT-SPEC.md](./13.story/STORY-FORMAT-SPEC.md) — 故事类章节格式

## 七、关键文档

- [v19 月度抽样报告](../skills/note-health/references/v19-sampling-report.md) — 19/19 = 100%
- [v18 抽样报告](../skills/note-health/references/v18-sampling-report.md) — 突破 100%
- [健康度收敛曲线](../skills/note-health/references/health-metrics-convergence.md) — 双收敛（5 维 + 结构）

---

**Phase 状态**：v13 体系完整（13 模块 + 12.interview + 13.story），结构 + 内容双闭环。

← [返回仓库根](../README.md)