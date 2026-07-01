# note 知识库优化设计 — 2026-07-01

> **状态**：设计中（待用户最终审核）
> **范围**：`note/` 知识库全局，不动 `profile/` / `tools/` / `.github/`
> **作者**：与 Claude 协作完成调研

---

## 1. 背景与现状

`note/` 是基于 Obsidian 维护的体系化技术知识库，14 主模块、872 个 markdown 文件、619 个 README 已有 frontmatter。最近两次重构（`bb4ab43`、`a327dc9`）已下线 5 个脚本（用户偏好"手工而非脚本"）、清理了 AUTO 引言、补齐了 frontmatter 与数字一致性。

本次优化针对 4 个维度的"剩饭"：
- **PNG 资产**（维度 1）：149 个 PNG 中 ~135 个孤儿，CONTRIBUTING §5.1/§5.4 数字过期
- **CONTRIBUTING 规范**（维度 2）：§5、§11 写过时信息
- **模块 README 一致性**（维度 3）：emoji 风格分 3 档
- **内容质量**（维度 4）：抽样后无明显问题，本设计不动

---

## 2. 目标

1. 让 PNG 资产与文档引用保持一致（删孤儿 / 改命名 / 接回引用）
2. 让 CONTRIBUTING 规范数字与现状匹配
3. 让 14 主模块 README 的 emoji 风格统一
4. **不动**：内容质量（无问题）；脚本（用户已禁用）；目录结构（用户偏好手工）

---

## 3. 设计

### §1. CONTRIBUTING §5 + §11 重盘（doc-only）

| 节 | 改动 | 行数变化 |
|----|------|----------|
| §5.1 表头 | "实际有 PNG 引用的文件（按目录）2026-07-01 重盘" | 不变 |
| §5.4 状态 | "其他 25 个目录有 PNG 但 README 未引用"（原 11，已过期）| +1 |
| §11 自检表 | 删"02/03/04/08 共 4 个缺开源参考"那行（4 个都已补）| -3 |

**验收**：`grep "02/03/04/08 缺" CONTRIBUTING.md` 无结果。

### §2. 135 孤儿 PNG 清理

**判定逻辑**：`find . -name "*.png"` 后逐个检查在同目录所有 `*.md` 中是否被 `![](name.png)` 引用。未引用 = 孤儿。

**保留清单**（实际有引用）：
- `07.workflow/.../camunda-7/img.png` `img_1.png` `img_2.png` `img_3.png`（4）
- `07.workflow/.../camunda-8/img_4.png` `img_5.png`（2）
- `11.ai/training/lesson1/img.png` `img_1.png` ... `img_6.png`（7）
- `11.ai/training/lesson9/tutorial-images/*.png`（26，命名规范）
- `11.ai/training/lesson13/img.png`（1，占位）
- `06.spring/03-data/mybatis/01-architecture/img/architecture-flow.png`（1，规范但待接回）
- `06.spring/03-data/mybatis/04-mybatis-plus/img/wrapper-class-hierarchy.png`（1，规范但待接回）

总计保留 ~42；删除 ~107（实际删除数需实施时再核一次精确数字）。

**风险**：⚠️ 中——commit message 列出每个被删 PNG 所在目录。

### §3. 9 张 PNG → Mermaid 替换（可适度回退）

候选（来自 CONTRIBUTING §5.2）：

| 文件 | 候选数 | 实施 |
|------|--------|------|
| `07.workflow/apache-eventmesh/cloud-flow/README.md` L1-L3 | 3 | 看 PNG → 设计 Mermaid → 替换 |
| `07.workflow/.../camunda-7/README.md` L4-7 | 4 | 同上（BPMN 流程图可能无法 1:1 转换）|
| `07.workflow/.../camunda-8/README.md` L4-5 | 2 | 同上（Zeebe 架构图通常可转）|

**回退策略**：Mermaid 表达不了的（如 BPMN 详细泳道），保留 PNG 并按 §3.2 改名 `{主题}-{描述}.png`。

**验收**：9 张全处理；最终迁移清单写入 CONTRIBUTING §5.4 状态行。

### §4. Mybatis 2 张规范 PNG 接回 README

| 文件 | 位置 |
|------|------|
| `06.spring/03-data/mybatis/01-architecture/README.md` | 在架构流程描述附近插入 `![架构流程](img/architecture-flow.png)` |
| `06.spring/03-data/mybatis/04-mybatis-plus/README.md` | 在 Wrapper 类层级描述附近插入 `![Wrapper 层级](img/wrapper-class-hierarchy.png)` |

**验收**：`grep -r "architecture-flow.png\|wrapper-class-hierarchy.png" note/` ≥ 2 处。

### §5. emoji 风格统一（加 emoji 档）

**目标**：14 主模块 README 的 H2 标题全部带 emoji。

**当前分档**：
- A 档（真 emoji）：04/05/06/07/08（5 个）— 已带
- B 档（中文数字式）：09/10（2 个）— 加 emoji **但保留"## 一、" ~ "## 十一、"序号**
- C 档（纯文字）：01/02/03/11/12/13/14（7 个）— 加 emoji

**emoji 映射约定**（参考 06.spring/09.front-end）：

| 节类型 | 推荐 emoji |
|--------|-----------|
| 一句话定位 / 概述 | 🎯 |
| 知识地图 / 体系 | 🗺️ / 🧭 |
| 章节导航 / 目录 | 📚 |
| 速查表 / Cheat Sheet | 📊 / ⚡ |
| 选型决策 | 🤔 |
| 学习路径 / 路线 | 🛤️ / 🧭 |
| 核心内容 | 📖 |
| 最佳实践 | 🏆 / ✅ |
| 案例 / 真实落地 | 💼 |
| 相关章节 / 上下游 | 🔗 |
| 开源参考 / 外部参考 | 📖 / 🔗 |
| 数据时效性 | ⏰ |
| 章节统计 | 📊 |
| 变更记录 | 📝 |
| 术语表 / 附录 | 📖 |
| 高频面试题 | 🎯 |
| 思考 / FAQ | 🤔 |

具体映射由实施时按各模块 H2 实际语义决定。

**验收**：14 主模块 README 全部 H2 带 emoji；09/10 保留 "## X、~## X一、" 中文序号。

---

## 4. 风险与缓解

| 风险 | 等级 | 缓解 |
|------|------|------|
| 误删孤儿 PNG | 中 | commit message 列目录清单；删除前 `git status` 对照 |
| Mermaid 无法 1:1 还原 BPMN | 中 | 回退保留 + 按 §3.2 改命名 |
| emoji 映射不当破坏阅读体验 | 低 | 沿用 06/07/08 已有 emoji 风格 |
| README 大量改 H2 触发链接锚点失效 | 低 | H2 文本未变（仅加前缀 emoji），锚点 `#一-xxx` 仍生效 |

---

## 5. 范围外

- 不动 872 个 markdown 的内容质量（抽样无问题）
- 不动 scripts 目录（已下线）
- 不动 frontmatter（已 100%）
- 不动数字一致性（已统一）
- 不动 CI workflow（`.github/workflows/grs.yml`、`link-check.yml`）
- 不动 `profile/` `tools/` `.github/` `README.md`（顶层）

---

## 6. 实施顺序

1. **§1 CONTRIBUTING 重盘**（1 文件，安全）
2. **§3 9 张 PNG 处理**（3 README，需看图决策）
3. **§2 135 孤儿 PNG 删除**（基于 §3 结果的差集）
4. **§4 Mybatis 2 张接回**（2 README）
5. **§5 emoji 统一**（9 README，最后做以减少冲突）

每个 § 单独 commit；commit message 按 CONTRIBUTING §6 conventional commits。

---

## 7. 验收总览

| § | 验收命令 / 标准 |
|---|----------------|
| §1 | `grep "02/03/04/08 缺" CONTRIBUTING.md` 无结果 |
| §2 | `find . -name "*.png" \| wc -l` 从 149 → ~42 |
| §3 | 9 张全处理；CONTRIBUTING §5.4 状态更新 |
| §4 | `grep -r "architecture-flow\|wrapper-class-hierarchy" note/` ≥ 2 处 |
| §5 | 14 主模块 H2 全带 emoji；09/10 序号保留 |