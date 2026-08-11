# Skill 解耦 + Note 重构 Plan 1：骨架 + 11.ai 试点

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `note-temp/` 创建 13 模块骨架（含 L0 SPEC.md + 13 个 L1 SPEC.md + README 占位），然后用 11.ai 试点完整迁移验证 SPEC.md / MOC / 互链机制。

**Architecture:** 新建 `note-temp/` 作为实验目录，先建骨架（占位 SPEC.md + README），然后完整迁移原 `note/11.ai/` 的 191 个文件到 `note-temp/08.ai-foundations/` 和 `note-temp/09.ai-applications/`，应用新结构（MOC + 原子化 + 双向互链）。

**Tech Stack:** Markdown / Git / Bash / find / grep

## Global Constraints

来自 `docs/superpowers/specs/2026-08-11-skill-decoupling-and-note-restructure-design.md`：

- **命名规范**：`{nn}.{english-name}/` 两位数字 + 英文短横线
- **SPEC.md 命名**：每个目录一个 `SPEC.md`（无前缀），L0/L1/L2 一致
- **SPEC.md 不带 frontmatter**（避免污染检索）
- **继承机制**：每个 SPEC.md 顶部显式 `> Inherits from: ...` + skill 运行时隐式向上找
- **互链机制**：只用 markdown `[](path)`，不用 wikilinks
- **MOC 风格**：复杂主题用 `README.md` + 数字编号原子笔记
- **不删 note/**：直到 Phase 8
- **工作分支**：`refactor/skill-note-decouple`（从 master 切出，已存在）
- **commit 格式**：`feat(note-temp): ...` / `refactor: ...` / `chore: ...` / `docs: ...`

---

## Phase 0：骨架（先做这个）

### Task 1: 创建 note-temp/ 目录 + .gitkeep

**Files:**
- Create: `note-temp/.gitkeep`

**目的：** 建立实验目录容器。

- [ ] **Step 1: 创建目录**

```bash
mkdir -p note-temp
touch note-temp/.gitkeep
```

- [ ] **Step 2: 验证**

```bash
ls -la note-temp/
```

期望：`note-temp/.gitkeep` 存在。

- [ ] **Step 3: Commit**

```bash
git add note-temp/.gitkeep
git commit -m "chore: 创建 note-temp/ 实验目录"
```

---

### Task 2: 创建 L0 `note-temp/SPEC.md`

**Files:**
- Create: `note-temp/SPEC.md`

**目的：** 定义全局规范——6 维度评分 + 11 类扫描规则 + 全局约束。

- [ ] **Step 1: 写 SPEC.md 头部**

`note-temp/SPEC.md` 内容（参考 spec §4.2 格式）：

```markdown
# SPEC for note-temp/

> **Inherits from**: (无，L0 是顶层)
> **Mode**: append + override
> **Updated**: 2026-08-11

---

## 全局规范

### 1. 命名约定

- 主模块：`{nn}.{english-name}/`，两位数字 + 英文小写 + 短横线（如 `01.java-and-jvm/`）
- 子目录：按概念或深度，由各模块 SPEC.md 定义
- 文件：`README.md` / `SPEC.md` / `index.md` 保留约定

### 2. commit 格式

```
feat(note-temp): 新增内容
refactor(note-temp): 结构调整
fix(note-temp): 修复
chore: 琐事
docs: 文档
```

### 3. 互链规则

- 每个文件必须有 `← [返回 ...]` 回链到父 README
- 至少 2 个跨模块或同模块的互链
- 系列文章末尾必须有"系列导航表"

### 4. frontmatter 规范（可选）

仅"知识文章"（非 SPEC.md / README.md / index.md）使用：

```
<!--module:
  parent: <module-slug>
  slug: <article-slug>
  type: article | atomic | moc
  category: ...
  summary: ...
-->
```

### 5. G1-G6 通用评分维度

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| G1 | frontmatter 完整性 | 有完整 frontmatter + 字段正确 | 有但缺字段 | 无 |
| G2 | 一句话定位 | H1 后 ≤80 字清晰定位 | 有定位但 >80 字或模糊 | 无 |
| G3 | 代码块规范 | 所有代码块声明语言 | 大部分声明 | 有裸代码块 |
| G4 | 回链 + 互链 | 有 footer 回链 + ≥2 个旧章节互链 | 有回链但互链不足 | 无回链 |
| G5 | 内容深度 | ≥4 个层面 + 实战案例 | 2-3 个层面 | 只有定义 |
| G6 | 可读性 | 结构清晰 + 表格/图/代码辅助 | 基本可读 | 大段纯文字 |

### 6. 11 类基础扫描规则

| # | 类别 | 检测方式 |
|---|------|----------|
| 1 | 数字一致性 | grep "篇\|个\|行" vs find 实测 |
| 2 | H1/H2 标题规范 | grep "^# " 检查数字编号 |
| 3 | 回链覆盖率 | grep "← \[返回" vs find README 数 |
| 3.5 | 孤岛检测 | 新文件未在父 README 登记 |
| 4 | 索引/入口缺失 | find -type d vs README 引用 |
| 5 | 内容重复 | grep 关键概念多文件匹配 |
| 6 | 内容缺口 | find 浅 README (<50 行) |
| 7 | 命名一致性 | 目录命名风格 |
| 8 | PNG/脚本残留 | find *.png vs 引用 |
| 9 | 系列完整性 | 编号系列文件缺失 |
| 10 | 归属合理性 | 子目录与父定位不符 |
| 11 | 合并检测 | 单文件 >500 行 + ≥8 H2 + ≥8 反模式 |
```

- [ ] **Step 2: 验证文件**

```bash
wc -l note-temp/SPEC.md
```

期望：> 50 行。

- [ ] **Step 3: Commit**

```bash
git add note-temp/SPEC.md
git commit -m "feat(note-temp): 创建 L0 全局 SPEC.md（含 6 维度 + 11 类扫描）"
```

---

### Task 3: 创建 13 个模块占位目录

**Files:**
- Create: 13 个 `note-temp/<NN>.<name>/` 目录 + `.gitkeep`

**目的：** 13 个模块的占位骨架，让目录结构可见。

- [ ] **Step 1: 创建所有模块目录**

```bash
cd note-temp
for n in \
  01.java-and-jvm \
  02.cs-foundations \
  03.data-stack \
  04.spring-backend \
  05.frontend \
  06.distributed-systems \
  07.devops-and-tools \
  08.ai-foundations \
  09.ai-applications \
  10.business-systems \
  11.product-and-pm \
  12.interview \
  13.story; do
  mkdir -p "$n"
  touch "$n/.gitkeep"
done
cd ..
```

- [ ] **Step 2: 验证目录数**

```bash
find note-temp -maxdepth 1 -type d | wc -l
```

期望：14（含 `note-temp/` 自身）。

- [ ] **Step 3: 列出所有模块**

```bash
ls note-temp/
```

期望输出：

```
01.java-and-jvm/
02.cs-foundations/
03.data-stack/
04.spring-backend/
05.frontend/
06.distributed-systems/
07.devops-and-tools/
08.ai-foundations/
09.ai-applications/
10.business-systems/
11.product-and-pm/
12.interview/
13.story/
SPEC.md
```

- [ ] **Step 4: Commit**

```bash
git add note-temp/
git commit -m "feat(note-temp): 13 模块占位骨架"
```

---

### Task 4: 为每个模块创建 SPEC.md 模板

**Files:**
- Create: 13 个 `note-temp/<module>/SPEC.md`（每个含模块定位 + 继承声明 + 占位评估维度）

**目的：** 让每个模块有自描述规范文件，便于 skill 读取。

- [ ] **Step 1: 写 01.java-and-jvm/SPEC.md**

```markdown
# SPEC for note-temp/01.java-and-jvm/

> **Inherits from**: [../SPEC.md](../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-11

---

## 模块定位

Java 语言基础 + JVM 原理 + 并发编程 + 设计模式。

## 从 L0 继承

- G1-G6 通用评分维度
- 11 类基础扫描规则
- 命名约定 + commit 格式 + 互链规则

## 本模块规则

### 评估维度（追加 G 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| A1 | 源码级深度 | 有源码片段 + WHY 注释 | 有代码只解释 WHAT | 无代码 |
| A2 | 版本演进对比 | 有 JDK X vs Y 对比 | 提及差异未展开 | 无版本 |
| A3 | ❌/✅ 反例对比 | 有正反例 | 只有正确用法 | 无对比 |
| A4 | 参数调优表 | 有实际参数 + 调优建议 | 有表无建议 | 无参数 |

### 写作要求

- 必须有源码片段（带 JDK 版本）
- 反模式用 ❌ 标识
- 至少 1 个生产实践案例

### 子目录约定（待 Phase 2 填实）

- `01-fundamentals/` 语言基础
- `02-jvm/` JVM 原理
- `03-concurrency/` 并发编程
- `04-patterns/` 设计模式
```

- [ ] **Step 2: 用脚本批量生成其他 12 个模块的 SPEC.md 模板**

```bash
cd note-temp

# 模块定义：name|location|description|dimensions_block
cat > /tmp/spec_template.sh << 'EOF'
#!/bin/bash
module_name="$1"
location="$2"
description="$3"
dimensions="$4"

cat > "$module_name/SPEC.md" << INNER
# SPEC for note-temp/$module_name/

> **Inherits from**: [../SPEC.md](../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-11

---

## 模块定位

$description

## 从 L0 继承

- G1-G6 通用评分维度
- 11 类基础扫描规则
- 命名约定 + commit 格式 + 互链规则

## 本模块规则

### 评估维度（追加 G 维度后）

$dimensions

### 写作要求

（待 Phase X 填实）

### 子目录约定

（待 Phase X 填实）
INNER
EOF

# 生成 02-07 占位 SPEC
./tmp/spec_template.sh "02.cs-foundations" "..." "算法 + OS + 网络 + 数学基础" "（待填实：B 类维度）"
./tmp/spec_template.sh "03.data-stack" "..." "数据库 + 缓存 + 消息队列 + 大数据" "（待填实：A 类维度）"
./tmp/spec_template.sh "04.spring-backend" "..." "Spring 生态 + 后端框架" "（待填实：A 类维度）"
./tmp/spec_template.sh "05.frontend" "..." "前端技术" "（待填实：G 类维度）"
./tmp/spec_template.sh "06.distributed-systems" "..." "分布式 + 微服务 + 云原生" "（待填实：A 类维度）"
./tmp/spec_template.sh "07.devops-and-tools" "..." "CI/CD + 监控 + 开发工具 + 运维" "（待填实：B 类维度）"

cd ..
```

**实际生成**：在 `git bash` 里跑上述脚本（或用 Node.js 脚本批量生成 12 个 SPEC.md）。

- [ ] **Step 3: 验证 SPEC.md 数量**

```bash
find note-temp -name "SPEC.md" | wc -l
```

期望：14（含 L0）。

- [ ] **Step 4: 抽查一个 SPEC.md**

```bash
cat note-temp/04.spring-backend/SPEC.md
```

期望：含 Inherits from 声明 + 模块定位 + 从 L0 继承段。

- [ ] **Step 5: Commit**

```bash
git add note-temp/
git commit -m "feat(note-temp): 13 模块 SPEC.md 模板（含 L1 继承声明）"
```

---

### Task 5: 为每个模块创建 README.md 占位

**Files:**
- Create: 13 个 `note-temp/<module>/README.md`（占位）

**目的：** 每个模块有 README，后续 Phase 填实内容。

- [ ] **Step 1: 批量创建占位 README**

```bash
cd note-temp
for module in 01.java-and-jvm 02.cs-foundations 03.data-stack 04.spring-backend 05.frontend 06.distributed-systems 07.devops-and-tools 08.ai-foundations 09.ai-applications 10.business-systems 11.product-and-pm 12.interview 13.story; do
  cat > "$module/README.md" << EOF
# ${module}

> **定位**：本模块占位，Phase 2+ 填实。
> **继承规范**：[SPEC.md](./SPEC.md)

（待 Phase X 填实：导航表 + 文章清单 + 互链）

← [返回 note-temp 总目录](../README.md)
EOF
done
cd ..
```

- [ ] **Step 2: 验证**

```bash
find note-temp -name "README.md" | wc -l
```

期望：13。

- [ ] **Step 3: Commit**

```bash
git add note-temp/
git commit -m "feat(note-temp): 13 模块 README.md 占位"
```

---

### Task 6: 创建 note-temp/README.md（L0 总目录）

**Files:**
- Create: `note-temp/README.md`

**目的：** L0 总导航，列出所有 13 模块。

- [ ] **Step 1: 写 README.md**

```markdown
# note-temp 总目录

> **定位**：13 模块新结构实验目录（最终替换 note/）
> **全局规范**：[SPEC.md](./SPEC.md)

---

## 13 模块导航

| # | 模块 | 主题 |
|---|------|------|
| 01 | [01.java-and-jvm](./01.java-and-jvm/) | Java + JVM + 并发 + 设计模式 |
| 02 | [02.cs-foundations](./02.cs-foundations/) | 算法 + OS + 网络 + 数学 |
| 03 | [03.data-stack](./03.data-stack/) | 数据库 + 缓存 + 大数据 |
| 04 | [04.spring-backend](./04.spring-backend/) | Spring + 后端框架 |
| 05 | [05.frontend](./05.frontend/) | 前端 |
| 06 | [06.distributed-systems](./06.distributed-systems/) | 分布式 + 微服务 + 云原生 |
| 07 | [07.devops-and-tools](./07.devops-and-tools/) | CI/CD + 监控 + 工具 |
| 08 | [08.ai-foundations](./08.ai-foundations/) | ML + DL + Transformer + LLM 基础 |
| 09 | [09.ai-applications](./09.ai-applications/) | RAG + Agent + Prompt + LLM 推理 |
| 10 | [10.business-systems](./10.business-systems/) | 电商 + 社交 + 金融 |
| 11 | [11.product-and-pm](./11.product-and-pm/) | 产品 + PM + 流程 |
| 12 | [12.interview](./12.interview/) | 面试题 |
| 13 | [13.story](./13.story/) | 阿明餐厅 |

---

**Phase 0 状态**：骨架完成（13 模块占位 + SPEC.md + README.md）。
**Phase 1+**：逐步填实内容。
```

- [ ] **Step 2: 验证**

```bash
cat note-temp/README.md | head -30
```

- [ ] **Step 3: Commit**

```bash
git add note-temp/README.md
git commit -m "feat(note-temp): L0 总目录 README.md（13 模块导航）"
```

---

### Task 7: Phase 0 验证 + 数字校对

**目的：** 验证骨架完整。

- [ ] **Step 1: 统计文件数**

```bash
echo "=== note-temp/ 结构 ==="
find note-temp -maxdepth 1 -type d
echo "=== 模块数 ==="
find note-temp -maxdepth 1 -type d -not -name "note-temp" | wc -l
echo "=== SPEC.md 数 ==="
find note-temp -name "SPEC.md" | wc -l
echo "=== README.md 数 ==="
find note-temp -name "README.md" | wc -l
```

期望：
- 模块数：13
- SPEC.md 数：14（含 L0）
- README.md 数：14（含 L0）

- [ ] **Step 2: 跑 broken links 扫描（应有 0 或极少，因为都是占位）**

```bash
python << 'PYEOF'
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
broken = 0
for root, _, files in os.walk('note-temp'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try: c = open(path, encoding='utf-8', errors='ignore').read()
        except: continue
        for m in LINK_RE.finditer(c):
            target = os.path.normpath(os.path.join(os.path.dirname(path), m.group(2).replace('/', os.sep)))
            if not os.path.isfile(target):
                broken += 1
                print(f'  ⚠ {path} -> {m.group(2)}')
print(f'\nBroken links: {broken}')
PYEOF
```

期望：0 或极少（占位 README 链接目标都在）。

- [ ] **Step 3: Commit（如果有任何修复）**

```bash
git status --short
# 如有未提交修改：
git add note-temp/
git commit -m "fix(note-temp): Phase 0 验证修复 broken links"
```

---

## Phase 1：11.ai 试点（最关键）

### Task 8: 设计 08.ai-foundations/ 子目录结构

**Files:**
- Modify: `note-temp/08.ai-foundations/README.md`
- Modify: `note-temp/08.ai-foundations/SPEC.md`

**目的：** 设计 AI 基础模块的子目录（5 大子领域：ML / DL / Transformer / LLM / Tokenization）。

- [ ] **Step 1: 扫原 note/11.ai 内容**

```bash
find note/11.ai -name "*.md" | head -30
echo "---"
find note/11.ai -type d
```

- [ ] **Step 2: 分析内容主题**

按以下 5 大子领域分类（人工判断）：

| 子领域 | 内容范围 | 原目录 |
|--------|---------|--------|
| **01-ml/** | 传统机器学习 | 11.ai 中 ML 相关 |
| **02-deep-learning/** | 深度学习基础 | 11.ai 中 DL 相关 |
| **03-transformer/** | Transformer 架构 | 11.ai/01-fundamentals/transformer/ |
| **04-llm/** | LLM 基础 | 11.ai/01-fundamentals/llm/ |
| **05-tokenization/** | Tokenization + Embedding | 11.ai/01-fundamentals/tokenization/ |

- [ ] **Step 3: 创建子目录骨架**

```bash
cd note-temp/08.ai-foundations
mkdir -p 01-ml 02-deep-learning 03-transformer 04-llm 05-tokenization-embedding
cd ../../..
```

- [ ] **Step 4: 更新 SPEC.md 填实**

替换 `note-temp/08.ai-foundations/SPEC.md` 占位内容：

```markdown
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
```

- [ ] **Step 5: 更新 README.md 填实**

替换 `note-temp/08.ai-foundations/README.md`：

```markdown
# 08. AI Foundations

> **定位**：AI 基础——传统 ML、深度学习、Transformer、LLM 基础、Tokenization/Embedding。
> **继承规范**：[SPEC.md](./SPEC.md)

## 目录导航

| # | 子目录 | 主题 |
|---|--------|------|
| 1 | [01-ml/](./01-ml/) | 传统机器学习算法 |
| 2 | [02-deep-learning/](./02-deep-learning/) | 深度学习基础 |
| 3 | [03-transformer/](./03-transformer/) | Transformer 架构 |
| 4 | [04-llm/](./04-llm/) | LLM 基础 |
| 5 | [05-tokenization-embedding/](./05-tokenization-embedding/) | Tokenization + Embedding |

---

（Phase 1 试点填实中）

← [返回 note-temp 总目录](../README.md)
```

- [ ] **Step 6: Commit**

```bash
git add note-temp/08.ai-foundations/
git commit -m "feat(note-temp): 08.ai-foundations 子目录结构 + SPEC/README 填实"
```

---

### Task 9: 设计 09.ai-applications/ 子目录结构（含 MOC）

**Files:**
- Modify: `note-temp/09.ai-applications/README.md`
- Modify: `note-temp/09.ai-applications/SPEC.md`
- Create: `note-temp/09.ai-applications/rag/` 等 MOC 子目录

**目的：** 设计 AI 应用模块——RAG / Agent / Prompt / LLM 推理，用 MOC 风格。

- [ ] **Step 1: 创建 MOC 子目录**

```bash
cd note-temp/09.ai-applications
mkdir -p rag agent prompts llm-inference fine-tuning eval
# 每个 MOC 目录加 README 占位
for d in rag agent prompts llm-inference fine-tuning eval; do
  cat > "$d/README.md" << EOF
# ${d}

> **定位**：MOC 索引——${d} 主题的所有内容。

（Phase 1 试点填实中）

← [返回 09.ai-applications](../README.md)
EOF
done
cd ../../..
```

- [ ] **Step 2: 更新 SPEC.md**

替换 `note-temp/09.ai-applications/SPEC.md`：

```markdown
# SPEC for note-temp/09.ai-applications/

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
```

- [ ] **Step 3: 更新 README.md**

替换 `note-temp/09.ai-applications/README.md`：

```markdown
# 09. AI Applications

> **定位**：AI 应用层——RAG、Agent、Prompt、LLM 推理工程、Fine-tuning、Eval。
> **继承规范**：[SPEC.md](./SPEC.md)

## MOC 索引

| # | 主题 | 用途 |
|---|------|------|
| 1 | [rag/](./rag/) | RAG 全景（检索 / rerank / 生成 / 评估 / 生产） |
| 2 | [agent/](./agent/) | Agent 框架（ReAct / Plan-Execute / Multi-Agent） |
| 3 | [prompts/](./prompts/) | Prompt 工程 |
| 4 | [llm-inference/](./llm-inference/) | LLM 推理优化（KV Cache / Flash Attention / Paged） |
| 5 | [fine-tuning/](./fine-tuning/) | 微调方法（SFT / RLHF / DPO） |
| 6 | [eval/](./eval/) | 评估方法 |

---

（Phase 1 试点填实中）

← [返回 note-temp 总目录](../README.md)
```

- [ ] **Step 4: Commit**

```bash
git add note-temp/09.ai-applications/
git commit -m "feat(note-temp): 09.ai-applications 子目录 + 6 个 MOC + SPEC/README 填实"
```

---

### Task 10: 迁移 11.ai 的 ML + DL 内容到 08.ai-foundations

**Files:**
- Move: `note/11.ai/.../ml/*` → `note-temp/08.ai-foundations/01-ml/`
- Move: `note/11.ai/.../deep-learning/*` → `note-temp/08.ai-foundations/02-deep-learning/`

**目的：** 迁移 ML 和 DL 基础内容（~30 文件）。

- [ ] **Step 1: 扫原 11.ai 的 ML / DL 内容**

```bash
find note/11.ai -type d -name "*machine-learning*" -o -name "*deep-learning*" -o -name "*ml*" -o -name "*dl*" 2>/dev/null
find note/11.ai -path "*machine-learning*" -name "*.md" 2>/dev/null | head -20
find note/11.ai -path "*deep-learning*" -name "*.md" 2>/dev/null | head -20
```

- [ ] **Step 2: 列出待迁移清单**

根据扫描结果，列出：
- ML 内容文件列表（待迁到 08.ai-foundations/01-ml/）
- DL 内容文件列表（待迁到 08.ai-foundations/02-deep-learning/）

- [ ] **Step 3: git mv 迁移文件**

```bash
# 示例：迁 ML 内容
git mv note/11.ai/01-fundamentals/machine-learning/README.md note-temp/08.ai-foundations/01-ml/README.md
# 实际根据扫描结果调整路径

# 验证
find note-temp/08.ai-foundations -name "*.md"
```

- [ ] **Step 4: 跑 broken links 扫描**

```bash
python << 'PYEOF'
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
broken = 0
for root, _, files in os.walk('note-temp/08.ai-foundations'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try: c = open(path, encoding='utf-8', errors='ignore').read()
        except: continue
        for m in LINK_RE.finditer(c):
            target = os.path.normpath(os.path.join(os.path.dirname(path), m.group(2).replace('/', os.sep)))
            if not os.path.isfile(target):
                broken += 1
                print(f'  ⚠ {path} -> {m.group(2)}')
print(f'\nBroken links: {broken}')
PYEOF
```

- [ ] **Step 5: 修复 broken links**

对每条 broken link：
1. 找到目标应该在新结构中的哪个文件
2. 更新链接路径

- [ ] **Step 6: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 08.ai-foundations 迁移 ML + DL 内容"
```

---

### Task 11: 迁移 11.ai 的 Transformer + LLM 基础到 08.ai-foundations

**Files:**
- Move: `note/11.ai/01-fundamentals/transformer/*` → `note-temp/08.ai-foundations/03-transformer/`
- Move: `note/11.ai/01-fundamentals/llm/*` → `note-temp/08.ai-foundations/04-llm/`
- Move: `note/11.ai/01-fundamentals/tokenization/*` → `note-temp/08.ai-foundations/05-tokenization-embedding/`

**目的：** 迁移 Transformer + LLM + Tokenization 内容（~50 文件）。

- [ ] **Step 1: 扫源文件**

```bash
find note/11.ai/01-fundamentals/transformer -name "*.md" 2>/dev/null
find note/11.ai/01-fundamentals/llm -name "*.md" 2>/dev/null
find note/11.ai/01-fundamentals/tokenization -name "*.md" 2>/dev/null
find note/11.ai/01-fundamentals/attention-mechanism -name "*.md" 2>/dev/null
find note/11.ai/01-fundamentals/embedding -name "*.md" 2>/dev/null
```

- [ ] **Step 2: git mv 迁移**

```bash
# Transformer 主目录
git mv note/11.ai/01-fundamentals/transformer/README.md note-temp/08.ai-foundations/03-transformer/README.md
# 其他子文件按实际路径调整

# LLM 主目录
git mv note/11.ai/01-fundamentals/llm/README.md note-temp/08.ai-foundations/04-llm/README.md

# Tokenization/Embedding 合并
git mv note/11.ai/01-fundamentals/tokenization/README.md note-temp/08.ai-foundations/05-tokenization-embedding/README.md
git mv note/11.ai/01-fundamentals/embedding/README.md note-temp/08.ai-foundations/05-tokenization-embedding/embedding.md
```

- [ ] **Step 3: 跑 broken links 扫描**

（用 Task 10 Step 4 的脚本）

- [ ] **Step 4: 修复 broken links**

- [ ] **Step 5: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 08.ai-foundations 迁移 Transformer + LLM + Tokenization"
```

---

### Task 12: 填实 08.ai-foundations 各子目录 README

**Files:**
- Modify: `note-temp/08.ai-foundations/01-ml/README.md` 等

**目的：** 每个子目录 README 有导航表 + 文章清单。

- [ ] **Step 1: 扫每个子目录的文章**

```bash
for d in 01-ml 02-deep-learning 03-transformer 04-llm 05-tokenization-embedding; do
  echo "=== $d ==="
  find note-temp/08.ai-foundations/$d -name "*.md" -not -name "README.md" | sort
done
```

- [ ] **Step 2: 为每个子目录填实 README**

模板（以 `01-ml/README.md` 为例）：

```markdown
# 01. 传统机器学习

> **定位**：传统 ML 算法——监督/无监督/强化学习的核心方法。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 文章清单

| 标题 | 路径 | 摘要 |
|------|------|------|
| 监督学习 | [supervised-learning.md](./supervised-learning.md) | ... |
| 无监督学习 | [unsupervised-learning.md](./unsupervised-learning.md) | ... |

---

← [返回 08.ai-foundations](../README.md)
```

- [ ] **Step 3: Commit**

```bash
git add note-temp/08.ai-foundations/
git commit -m "feat(note-temp): 08.ai-foundations 子目录 README 填实"
```

---

### Task 13: 迁移 RAG 主题到 09.ai-applications/rag/（MOC 模式）

**Files:**
- Move: `note/11.ai/.../rag/*` → `note-temp/09.ai-applications/rag/`

**目的：** RAG 是复杂主题，用 MOC 模式——拆分为原子笔记。

- [ ] **Step 1: 扫原 RAG 内容**

```bash
find note/11.ai -path "*rag*" -name "*.md" 2>/dev/null
```

- [ ] **Step 2: 分析 RAG 子主题**

RAG 通常拆为：
- `01-retrieval.md` 检索方法
- `02-rerank.md` 重排序
- `03-generation.md` 生成
- `04-evaluation.md` 评估
- `05-production.md` 生产实践
- `06-frontier.md` 前沿（GraphRAG / Agentic RAG）

- [ ] **Step 3: 迁移原 RAG 文件并拆分**

```bash
# 主 README
git mv note/11.ai/03-engineering/rag/README.md note-temp/09.ai-applications/rag/README.md

# 子文件按 RAG 子主题重新组织（手动判断 + 拆分）
# 示例：retrieval 相关 → 01-retrieval.md
git mv note/11.ai/03-engineering/rag/retrieval-methods.md note-temp/09.ai-applications/rag/01-retrieval.md
```

- [ ] **Step 4: 填实 RAG MOC README**

```markdown
# RAG（Retrieval-Augmented Generation）

> **定位**：MOC——RAG 主题索引，覆盖检索 / 重排序 / 生成 / 评估 / 生产 / 前沿。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 原子笔记清单

| # | 主题 | 路径 | 摘要 |
|---|------|------|------|
| 1 | 检索方法 | [01-retrieval.md](./01-retrieval.md) | 向量检索 / BM25 / 混合检索 |
| 2 | 重排序 | [02-rerank.md](./02-rerank.md) | Cross-encoder / Cohere Rerank |
| 3 | 生成 | [03-generation.md](./03-generation.md) | Prompt 模板 / 上下文组装 |
| 4 | 评估 | [04-evaluation.md](./04-evaluation.md) | 召回率 / 忠实度 / 端到端 |
| 5 | 生产实践 | [05-production.md](./05-production.md) | 索引更新 / 缓存 / 监控 |
| 6 | 前沿 | [06-frontier.md](./06-frontier.md) | GraphRAG / Agentic RAG |

## 关联主题

- [../prompts/](../prompts/) — Prompt 工程
- [../eval/](../eval/) — 评估方法
- [../../08.ai-foundations/03-transformer/](../../08.ai-foundations/03-transformer/) — Transformer 基础

---

← [返回 09.ai-applications](../README.md)
```

- [ ] **Step 5: 跑 broken links 扫描并修复**

- [ ] **Step 6: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 09.ai-applications/rag MOC 模式 + 6 个原子笔记"
```

---

### Task 14: 迁移 Agent + Prompt + LLM 推理主题

**Files:**
- Move: `note/11.ai/.../agent/*` → `note-temp/09.ai-applications/agent/`
- Move: `note/11.ai/.../prompt/*` → `note-temp/09.ai-applications/prompts/`
- Move: `note/11.ai/.../inference/*` → `note-temp/09.ai-applications/llm-inference/`

**目的：** 迁移剩余的 AI 应用层主题。

- [ ] **Step 1: 扫源文件**

```bash
find note/11.ai -path "*agent*" -name "*.md" 2>/dev/null
find note/11.ai -path "*prompt*" -name "*.md" 2>/dev/null
find note/11.ai -path "*inference*" -name "*.md" 2>/dev/null
```

- [ ] **Step 2: 迁移 Agent 主题**

```bash
git mv note/11.ai/03-engineering/agent-frameworks/README.md note-temp/09.ai-applications/agent/README.md
# ... 其他 agent 子文件按需迁移
```

- [ ] **Step 3: 迁移 Prompt 主题**

```bash
git mv note/11.ai/03-engineering/prompt-engineering/README.md note-temp/09.ai-applications/prompts/README.md
```

- [ ] **Step 4: 迁移 LLM 推理主题**

```bash
git mv note/11.ai/02-technology-stack/inference-optimization/README.md note-temp/09.ai-applications/llm-inference/README.md
# 其他推理子文件（KV Cache / Flash Attention 等）
```

- [ ] **Step 5: 填实每个 MOC README**

按 Task 13 Step 4 模板。

- [ ] **Step 6: 跑 broken links 扫描并修复**

- [ ] **Step 7: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 09.ai-applications 迁移 Agent + Prompt + LLM 推理"
```

---

### Task 15: 填实 09.ai-applications/ 子目录 README

**Files:**
- Modify: `note-temp/09.ai-applications/{fine-tuning,eval}/README.md` 等

**目的：** 剩余 MOC（fine-tuning、eval）填实。

- [ ] **Step 1: 扫剩余 11.ai 内容**

```bash
find note/11.ai -path "*fine-tuning*" -name "*.md" 2>/dev/null
find note/11.ai -path "*alignment*" -name "*.md" 2>/dev/null
find note/11.ai -path "*eval*" -name "*.md" 2>/dev/null
```

- [ ] **Step 2: 迁移 fine-tuning**

```bash
git mv note/11.ai/07-research/alignment/README.md note-temp/09.ai-applications/fine-tuning/README.md
```

- [ ] **Step 3: 迁移 eval**

```bash
# 如有 eval 相关
# git mv note/11.ai/.../eval... note-temp/09.ai-applications/eval/...
```

- [ ] **Step 4: 填实所有 MOC README**

- [ ] **Step 5: 跑 broken links 扫描**

- [ ] **Step 6: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 09.ai-applications 迁移 Fine-tuning + Eval"
```

---

### Task 16: Phase 1 验证 + 数字校对

**目的：** 验证 11.ai 试点完整。

- [ ] **Step 1: 数字校对**

```bash
echo "=== 原 11.ai 文件数 ==="
find note/11.ai -name "*.md" | wc -l
echo "=== 新 08 + 09 文件数 ==="
find note-temp/08.ai-foundations -name "*.md" | wc -l
find note-temp/09.ai-applications -name "*.md" | wc -l
total_new=$(($(find note-temp/08.ai-foundations -name "*.md" | wc -l) + $(find note-temp/09.ai-applications -name "*.md" | wc -l)))
echo "总: $total_new"
```

期望：total_new ≈ 191（原 11.ai 文件数，±5 浮动）。

- [ ] **Step 2: 全库 broken links 扫描**

```bash
python << 'PYEOF'
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
broken = 0
for root, _, files in os.walk('note-temp'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try: c = open(path, encoding='utf-8', errors='ignore').read()
        except: continue
        for m in LINK_RE.finditer(c):
            target = os.path.normpath(os.path.join(os.path.dirname(path), m.group(2).replace('/', os.sep)))
            if not os.path.isfile(target):
                broken += 1
                print(f'  ⚠ {path} -> {m.group(2)}')
print(f'\nBroken links: {broken}')
PYEOF
```

期望：broken 较少（仅跨模块到未迁移模块的链接）。

- [ ] **Step 3: 验证 SPEC.md 读取**

手动抽查：读一个 `note-temp/09.ai-applications/rag/01-retrieval.md`，确认：
- 有 `← [返回 ...]` 回链
- 有 ≥2 个互链
- 引用 SPEC.md 中定义的规则

- [ ] **Step 4: 记录 Phase 1 验证结果**

```bash
echo "=== Phase 1 完成状态 ==="
echo "模块数: $(find note-temp -maxdepth 1 -type d -not -name 'note-temp' | wc -l)"
echo "SPEC.md: $(find note-temp -name 'SPEC.md' | wc -l)"
echo "README.md: $(find note-temp -name 'README.md' | wc -l)"
echo "总 .md: $(find note-temp -name '*.md' | wc -l)"
echo "MOC: $(find note-temp -name 'README.md' -path '*/rag/*' -o -name 'README.md' -path '*/agent/*' | wc -l)"
```

- [ ] **Step 5: Commit 验证记录**

```bash
git add docs/ 2>/dev/null  # 如果有记录文档
git commit --allow-empty -m "chore: Phase 1 11.ai 试点验证完成

- 191 文件迁移（11.ai → 08 + 09）
- SPEC.md 继承机制验证
- MOC + 原子化模式验证
- broken links 扫描通过"
```

---

## 验证清单（Plan 1 完成时必过）

- [ ] note-temp/ 有 14 个 SPEC.md（1 L0 + 13 L1）
- [ ] note-temp/ 有 14 个 README.md（1 L0 + 13 L1）
- [ ] 08.ai-foundations 子目录 5 个（01-ml/02-dl/03-transformer/04-llm/05-tokenization）
- [ ] 09.ai-applications 子目录 6 个 MOC（rag/agent/prompts/llm-inference/fine-tuning/eval）
- [ ] 原 note/11.ai/191 文件全部迁移到 note-temp/08 + 09
- [ ] 全库 broken links ≤ 10（仅未迁移模块引用）
- [ ] SPEC.md Inherits from 声明 100% 覆盖
- [ ] 每个文件有回链 + ≥2 互链

---

## 后续 Plans

- **Plan 2**：Phase 2-5（其他 11 个模块迁移）
- **Plan 3**：Phase 6（3 个 Skill 重构）
- **Plan 4**：Phase 7-8（清理 + 替换 note/）
