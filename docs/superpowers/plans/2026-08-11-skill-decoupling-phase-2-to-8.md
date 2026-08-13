# Skill 解耦 + Note 重构 Plan 2：剩余 12 模块迁移 + 健康检查 + 重命名

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完整迁移 `note/`（剩 13 模块，915 个 .md）到 `note-temp/`，填实所有 SPEC.md / README.md，运行健康检查修复所有 P1/P2 问题，最后把 `note-temp/` 重命名为 `note/` 并删除旧 `note/`。

**Architecture:** 沿用 Plan 1 的迁移模式（git mv + MOC + 原子化 + 双向链接）。本 plan 重点：保留 leaf 文章不被覆盖、SPEC.md 填实、最终全库健康检查、原子化重命名。

**Tech Stack:** Markdown / Git / Bash / find / grep / Python

## Global Constraints

- 工作分支：`refactor/skill-note-decouple`（已有 Plan 1 commit）
- 不纳入 pre-existing `note/.../ralph-wiggum-loop.md`
- 沿用 Plan 1 的迁移原则：保留 leaf 文章不被覆盖
- SPEC.md 不带 frontmatter（已全库统一）
- Inherits 用 `../SPEC.md`（已修复）
- 缺失 SPEC.md 时询问用户（3 选项）
- 沿用全局 commit 格式：`feat(note-temp): ...` / `fix(note-temp): ...` / `chore: ...`

---

## Phase 2：基础模块迁移

### Task 1: 02.cs-foundations 迁移

**Files:**
- Move: `note/02.computer-basics/*` → `note-temp/02.cs-foundations/`

**目的:** 算法 + OS + 网络 + 数学基础（42 文件）。

- [ ] **Step 1: 扫描源结构**

```bash
find note/02.computer-basics -name "*.md" | head -30
find note/02.computer-basics -type d
```

- [ ] **Step 2: 列出迁移清单**

按 brief 内容分组：
- `01-algorithms/` 接收 algorithms 内容
- `02-os/` 接收 OS / Linux
- `03-network/` 接收网络 / HTTP
- `04-math/` 接收数学（如果原 02 有）

**先检查目标 README/SPEC.md 是否为 stub**：

```bash
wc -l note-temp/02.cs-foundations/README.md note-temp/02.cs-foundations/SPEC.md
```

期望都是占位（< 30 行）。

- [ ] **Step 3: git mv 迁移**

```bash
git mv note/02.computer-basics/01-algorithms note-temp/02.cs-foundations/01-algorithms 2>/dev/null || true
git mv note/02.computer-basics/02-os note-temp/02.cs-foundations/02-os 2>/dev/null || true
git mv note/02.computer-basics/03-network note-temp/02.cs-foundations/03-network 2>/dev/null || true
git mv note/02.computer-basics/04-math note-temp/02.cs-foundations/04-math 2>/dev/null || true
# 处理剩余文件
for f in $(find note/02.computer-basics -maxdepth 1 -name "*.md"); do
  base=$(basename "$f")
  git mv "$f" "note-temp/02.cs-foundations/$base"
done
```

- [ ] **Step 4: 填实子目录 README（每个子目录一篇导航）**

模板：

```markdown
# {N}. {主题}

> **定位**：{一句话}
> **继承规范**：[../SPEC.md](../SPEC.md)

## 文章清单

（自动生成：列出本目录所有 .md 文件）

---

← [返回 02.cs-foundations](../README.md)
```

- [ ] **Step 5: 填实 02.cs-foundations/README.md（MOC 索引）**

- [ ] **Step 6: 跑 broken links 扫描并修复**

- [ ] **Step 7: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 02.cs-foundations 迁移算法 + OS + 网络 + 数学"
```

---

### Task 2: 03.data-stack 迁移（03.database + 10.big-data）

**Files:**
- Move: `note/03.database/*` → `note-temp/03.data-stack/01-database/`
- Move: `note/10.big-data/*` → `note-temp/03.data-stack/02-big-data/`

**目的:** 数据库 + 大数据合并（19 + 12 = 31 文件）。

- [ ] **Step 1: 扫描源结构**

```bash
find note/03.database -name "*.md" | head -30
find note/10.big-data -name "*.md" | head -30
```

- [ ] **Step 2: 列出迁移清单**

- 03.database → 03.data-stack/01-database/（按原目录结构）
- 10.big-data → 03.data-stack/02-big-data/

- [ ] **Step 3: git mv 迁移**

```bash
# 数据库内容（保留原目录结构）
for d in $(find note/03.database -maxdepth 1 -type d -not -path "note/03.database"); do
  base=$(basename "$d")
  git mv "$d" "note-temp/03.data-stack/01-database/$base"
done
# 顶层 README
git mv note/03.database/README.md note-temp/03.data-stack/01-database/README.md 2>/dev/null

# 大数据
git mv note/10.big-data note-temp/03.data-stack/02-big-data
```

- [ ] **Step 4: 填实子目录 README**

- [ ] **Step 5: 填实 03.data-stack/README.md**

- [ ] **Step 6: broken links 修复**

- [ ] **Step 7: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 03.data-stack 迁移数据库 + 大数据"
```

---

### Task 3: 01.java-and-jvm 迁移

**Files:**
- Move: `note/01.java/*` → `note-temp/01.java-and-jvm/`

**目的:** Java 语言 + JVM + 并发 + 设计模式（112 文件）。

- [ ] **Step 1: 扫描源结构**

```bash
find note/01.java -name "*.md" | wc -l  # 期望 112
find note/01.java -maxdepth 1 -type d
```

- [ ] **Step 2: 列出迁移清单**

按原 01.java 的子目录分类：
- `01-language/` 接收 Java 语言基础
- `02-jvm/` 接收 JVM 原理
- `03-concurrency/` 接收并发
- `04-patterns/` 接收设计模式
- 其他子目录按原样

**注意**：01.java 已经有 `version/` 子目录（Java 8-26），这是大头。

- [ ] **Step 3: git mv 迁移**

```bash
# 整体迁移（保留原结构）
for d in $(find note/01.java -maxdepth 1 -type d); do
  base=$(basename "$d")
  if [ "$base" != "01.java" ]; then
    git mv "$d" "note-temp/01.java-and-jvm/$base"
  fi
done
# 顶层 README
git mv note/01.java/README.md note-temp/01.java-and-jvm/README.md 2>/dev/null
```

- [ ] **Step 4: 填实子目录 README**

- [ ] **Step 5: 填实 01.java-and-jvm/README.md**

- [ ] **Step 6: broken links 修复**

- [ ] **Step 7: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 01.java-and-jvm 迁移 Java + JVM + 并发 + 设计模式"
```

---

## Phase 3：中间模块迁移

### Task 4: 04.spring-backend 迁移

**Files:**
- Move: `note/06.spring/*` → `note-temp/04.spring-backend/`

**目的:** Spring 生态 + 后端框架（141 文件）。

- [ ] **Step 1: 扫描源结构**

```bash
find note/06.spring -maxdepth 1 -type d
find note/06.spring -name "*.md" | wc -l  # 期望 141
```

- [ ] **Step 2: 列出迁移清单**

按 06.spring 子目录结构：
- `01-core/` Spring Core / IoC / AOP
- `02-boot/` Spring Boot
- `03-cloud/` Spring Cloud / 微服务
- `04-data/` Spring Data
- `05-ecosystem/` 其他生态

- [ ] **Step 3: git mv 迁移**

```bash
for d in $(find note/06.spring -maxdepth 1 -type d); do
  base=$(basename "$d")
  if [ "$base" != "06.spring" ]; then
    git mv "$d" "note-temp/04.spring-backend/$base"
  fi
done
git mv note/06.spring/README.md note-temp/04.spring-backend/README.md 2>/dev/null
```

- [ ] **Step 4: 填实子目录 README**

- [ ] **Step 5: 填实 04.spring-backend/README.md**

- [ ] **Step 6: broken links 修复**

- [ ] **Step 7: Commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 04.spring-backend 迁移 Spring 生态 + 后端框架"
```

---

### Task 5: 05.frontend 迁移

**Files:**
- Move: `note/09.front-end/*` → `note-temp/05.frontend/`

**目的:** 前端（54 文件）。

- [ ] **Step 1-3: 扫描 + 迁移**（同 Task 4 模式）

- [ ] **Step 4-7: README 填实 + broken links 修复 + commit**

```bash
git mv note/09.front-end/README.md note-temp/05.frontend/README.md
for d in $(find note/09.front-end -maxdepth 1 -type d); do
  base=$(basename "$d")
  [ "$base" != "09.front-end" ] && git mv "$d" "note-temp/05.frontend/$base"
done
```

---

### Task 6: 06.distributed-systems 迁移

**Files:**
- Move: `note/04.system-design/*` → `note-temp/06.distributed-systems/`
- 部分 `note/08.application-systems/` 架构部分 → `note-temp/06.distributed-systems/`

**目的:** 分布式 + 微服务 + 云原生 + 系统设计（155 + 部分 08）。

- [ ] **Step 1: 扫描源结构**

```bash
find note/04.system-design -maxdepth 1 -type d
find note/04.system-design -name "*.md" | wc -l  # 期望 155
find note/08.application-systems -maxdepth 1 -type d
```

- [ ] **Step 2: 划分 08.application-systems**

08.application-systems 拆分：
- 架构 / 分布式部分 → 06.distributed-systems
- 业务系统（电商 / 社交 / 金融）→ 10.business-systems

```bash
ls note/08.application-systems/01-architecture/ 2>/dev/null
ls note/08.application-systems/02-business/ 2>/dev/null
# 实际目录根据扫描结果调整
```

- [ ] **Step 3: 迁移 04.system-design 整体**

```bash
for d in $(find note/04.system-design -maxdepth 1 -type d); do
  base=$(basename "$d")
  [ "$base" != "04.system-design" ] && git mv "$d" "note-temp/06.distributed-systems/$base"
done
git mv note/04.system-design/README.md note-temp/06.distributed-systems/README.md 2>/dev/null
```

- [ ] **Step 4: 迁移 08.application-systems 的架构部分**

```bash
# 根据 Step 2 划定哪些目录属架构
git mv note/08.application-systems/<架构目录> note-temp/06.distributed-systems/<对应目录>
```

- [ ] **Step 5-7: README + commit**

```bash
git add note/ note-temp/
git commit -m "feat(note-temp): 06.distributed-systems 迁移分布式 + 系统设计 + 架构"
```

---

### Task 7: 07.devops-and-tools 迁移

**Files:**
- Move: `note/05.tools/*` → `note-temp/07.devops-and-tools/01-tools/`
- Move: `note/07.workflow/*` → `note-temp/07.devops-and-tools/02-workflow/`

**目的:** CI/CD + 监控 + 工具 + 流程（33 + 11 = 44）。

- [ ] **Step 1-7: 扫描 + 迁移 + README + commit**

模式同前。

---

## Phase 4：应用模块迁移

### Task 8: 10.business-systems 迁移

**Files:**
- Move: `note/08.application-systems/` 业务部分 → `note-temp/10.business-systems/`

**目的:** 电商 + 社交 + 金融业务系统。

- [ ] **Step 1-7: 扫描 + 迁移 + README + commit**

按 Task 6 划定哪些是业务目录。

---

### Task 9: 11.product-and-pm 迁移

**Files:**
- Move: `note/14.project-management/*` → `note-temp/11.product-and-pm/`

**目的:** 产品 + PM + 流程（12 文件）。

- [ ] **Step 1-7: 同模式**

---

## Phase 5：职业模块迁移

### Task 10: 12.interview 迁移

**Files:**
- Move: `note/13.split-hairs/*` → `note-temp/12.interview/`

**目的:** 面试题（232 文件）。

- [ ] **Step 1: 扫描 13.split-hairs 结构**

```bash
find note/13.split-hairs -maxdepth 1 -type d
```

13.split-hairs 按 14 主模块组织（如 13.split-hairs/01.java/, 13.split-hairs/11.ai/ 等）。新结构 12.interview 可保留这种按主题分类。

- [ ] **Step 2-7: 迁移 + README + commit**

```bash
git mv note/13.split-hairs note-temp/12.interview
# 然后调整 README.md 把目录表更新
```

---

### Task 11: 13.story 迁移

**Files:**
- Move: `note/12.story/*` → `note-temp/13.story/`

**目的:** 阿明餐厅（54 文件）。

- [ ] **Step 1-7: 同模式**

```bash
git mv note/12.story note-temp/13.story
```

---

## Phase 6：SPEC.md + README 填实

### Task 12: 02-07, 10-13 SPEC.md 填实

**Files:**
- Modify: 10 个模块的 SPEC.md（02.cs-foundations / 03.data-stack / 01.java-and-jvm / 04.spring-backend / 05.frontend / 06.distributed-systems / 07.devops-and-tools / 10.business-systems / 11.product-and-pm / 12.interview / 13.story）

**目的:** 把所有占位 SPEC.md 填实为完整规范文档（模块定位、评估维度、写作要求、子目录约定）。

- [ ] **Step 1: 扫描当前 SPEC.md 占位**

```bash
for spec in note-temp/*/SPEC.md; do
  name=$(basename $(dirname "$spec"))
  is_placeholder=$(grep -c "待 Phase X 填实" "$spec" 2>/dev/null)
  echo "$name: placeholder=$is_placeholder"
done
```

- [ ] **Step 2: 起草每个 SPEC.md 内容**

按 spec §5.2 的模块定位 + 该模块对应的评估维度（A/B/C/D/E/Q/S 类），为每个模块写完整 SPEC.md。

- [ ] **Step 3: 写各模块 SPEC.md**

每个 SPEC.md 结构：
- 顶部 `Inherits from: [../SPEC.md]`
- 模块定位
- 从 L0 继承段
- 本模块评估维度（按模块类型）
- 写作要求
- 子目录约定

- [ ] **Step 4: Commit**

```bash
git add note-temp/
git commit -m "feat(note-temp): 11 个模块 SPEC.md 填实"
```

---

### Task 13: 02-13 README.md 填实

**Files:**
- Modify: 11 个模块的 README.md

**目的:** 把占位 README 改为完整 MOC 索引。

- [ ] **Step 1-4: 扫描 + 起草 + 写 + commit**

每个 README 含：
- 模块标题 + 定位
- 子目录导航表（指向所有子目录）
- 主要文章清单
- 回链到 note-temp/README.md

```bash
git add note-temp/
git commit -m "feat(note-temp): 11 个模块 README.md 填实"
```

---

## Phase 6.5：L2 SPEC.md 按需补（Task 16）

### Task 16: L2 SPEC.md 按需补（强特异性子目录）

**Files:**
- Create: 5 个 L2 SPEC.md（`01.java-and-jvm/02-jvm/SPEC.md`、`01.java-and-jvm/04-patterns/SPEC.md`、`01.java-and-jvm/testing/SPEC.md`、`09.ai-applications/rag/SPEC.md`、`09.ai-applications/agent/SPEC.md`）

**目的:** 给强特异性子目录补 L2 SPEC.md，含独特的评估维度 + 写作要求。

- [ ] **Step 1: 扫描需要 L2 SPEC.md 的子目录**

按以下判断清单：
- 子目录有独特评估维度（L1 G + A/B/C 类不够）
- 子目录有专门写作要求
- 子目录内容跨多学科融合

```bash
for sub in note-temp/01.java-and-jvm/02-jvm \
          note-temp/01.java-and-jvm/04-patterns \
          note-temp/01.java-and-jvm/testing \
          note-temp/09.ai-applications/rag \
          note-temp/09.ai-applications/agent; do
  echo "=== $sub ==="
  # 检查内容是否够丰富（≥5 篇 leaf 文章）
  count=$(find "$sub" -maxdepth 2 -name "*.md" -not -name "README.md" 2>/dev/null | wc -l)
  echo "  leaf count: $count"
done
```

- [ ] **Step 2: 起草 5 个 L2 SPEC.md**

每个 SPEC.md 结构：
- 顶部 `Inherits from: [../../../SPEC.md]`（或 `../../SPEC.md`，按深度）
- 子目录定位
- 从 L1 继承段
- 本子目录评估维度（强特异性）
- 写作要求（专门规则）
- 互链要求

参考示例：`note-temp/09.ai-applications/rag/SPEC.md`（如已存在则跳过）

- [ ] **Step 3: 写 5 个 SPEC.md**

每个 L2 SPEC.md 模板：

```markdown
# SPEC for note-temp/<module>/<sub>/

> **Inherits from**: [../../../SPEC.md](../../../SPEC.md)（或 ../）
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 子目录定位

（1-2 句话说明这个子目录专注于什么）

## 从 L1 继承

（继承自 L1 的 G1-G6 + 模块专属 A/B/C 维度）

## 本子目录规则（强特异性）

### 评估维度（追加 L1 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| X1 | {维度名} | {2 分标准} | {1 分标准} | {0 分标准} |
| X2 | {维度名} | ... | ... | ... |

### 写作要求

- {专门规则 1}
- {专门规则 2}
- {专门规则 3}
```

- [ ] **Step 4: 验证 Inherits 路径**

每个 L2 SPEC.md 的 `Inherits from` 路径必须正确解析到 L0 SPEC.md。

```bash
# 验证 02-jvm 路径
echo "test: [../../../SPEC.md]" | grep -oE "\[([^]]+)\]\(([^)]+)\)"
```

- [ ] **Step 5: Commit**

```bash
git add note-temp/
git commit -m "feat(note-temp): 5 个 L2 SPEC.md（强特异性子目录：jvm/patterns/testing/rag/agent）"
```

**全局约束**：
- 不纳入 pre-existing `note/.../ralph-wiggum-loop.md`
- 不修改 L0/L1 SPEC.md（只新增 L2）

**报告文件**：`.superpowers/sdd/2026-08-11-skill-decoupling-phase-2-to-8/task-16-report.md`

**报告契约**：
- 状态
- commit hash
- 5 个 L2 SPEC.md 的内容摘要（每个 1-2 行）
- Inherits 路径验证结果
- concerns

---

## Phase 7：健康检查 + 修复

### Task 14: 全库健康检查（注意：原编号 Task 15 改为 Phase 8 Task 15）

**目的:** 跑所有健康检查，识别 P1/P2 问题。

- [ ] **Step 1: 数字校对**

```bash
echo "总 .md 数:" && find note-temp -name "*.md" | wc -l
echo "SPEC.md 数:" && find note-temp -name "SPEC.md" | wc -l  # 期望 14
echo "README.md 数:" && find note-temp -name "README.md" | wc -l  # 期望 14+
echo "frontmatter 覆盖:" && find note-temp -name "README.md" -exec grep -l "^<!--" {} \; | wc -l
```

- [ ] **Step 2: note-temp broken links 全扫**

```bash
python << 'PYEOF'
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
PLACEHOLDERS = ['x/README', 'xxx', '12.interview/', '13.story/']
broken_total = 0
real_broken = 0
for root, _, files in os.walk('note-temp'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try: c = open(path, encoding='utf-8', errors='ignore').read()
        except: continue
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            if any(p in target_rel for p in PLACEHOLDERS):
                continue
            target_sep = target_rel.replace('/', os.sep)
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_sep))
            if not os.path.isfile(target_abs):
                broken_total += 1
                real_broken += 1
print(f'Real broken: {real_broken}')
PYEOF
```

- [ ] **Step 3: source-side broken links 扫描**

```bash
python << 'PYEOF'
# 扫 note/ 中指向 note-temp/ 的反向链接（应都已迁过去后变 broken）
import os, re
LINK_RE = re.compile(r'(?<![|\[])\[([^\]]*)\]\((?!https?://)(?!mailto:)(?!#)([^)#\s]+?\.md)(?:#[^)]*)?\)')
broken_to_temp = 0
broken_total = 0
for root, _, files in os.walk('note'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try: c = open(path, encoding='utf-8', errors='ignore').read()
        except: continue
        for m in LINK_RE.finditer(c):
            target_rel = m.group(2).strip()
            target_sep = target_rel.replace('/', os.sep)
            target_abs = os.path.normpath(os.path.join(os.path.dirname(path), target_sep))
            if not os.path.isfile(target_abs):
                broken_total += 1
                # 如果目标原本在 note-temp/ 而源在 note/，这就是待修的
                if 'note-temp' in target_abs:
                    broken_to_temp += 1
print(f'Total broken in note/: {broken_total}')
print(f'Broken pointing to note-temp/: {broken_to_temp}')
PYEOF
```

- [ ] **Step 4: dos2unix 扫除**

```bash
# 检查工作树 CRLF 文件数
echo "CRLF files in working tree:"
grep -l $'\r' note-temp -r 2>/dev/null | wc -l
```

- [ ] **Step 5: 修复 source-side broken links**

如果 Step 3 显示 broken-to-temp > 0，按需修改源链接路径：

```bash
# 用 sed 或 Edit 工具批量改指向旧 note/ 路径的链接为 note-temp/ 对应路径
# 这通常是 git mv 后的引用未更新
```

- [ ] **Step 6: Commit 修复**

```bash
git add note/
git commit -m "fix(note): 修复指向 note-temp/ 的反向链接"
```

- [ ] **Step 7: 跑 Phase 0/1 健康检查清单（spec §11）**

按 spec §11 验证清单逐项检查。

- [ ] **Step 8: 写健康检查报告**

```bash
mkdir -p note/.health-tmp  # 如果还没删 note/
echo "Phase 1 + Phase 2 健康检查报告" > note/.health-tmp/report-final.md
# 写入各项指标
```

---

## Phase 8：重命名 note-temp/ → note/

### Task 15: 原子化重命名

**Files:**
- Move: `note-temp/` → `note/`（整体重命名）
- Delete: 旧 `note/` 内容

**目的:** 把 `note-temp/` 作为新 `note/`，删除旧 `note/`。

- [ ] **Step 1: 备份当前状态（git tag）**

```bash
git tag v1-pre-note-restructure HEAD
```

- [ ] **Step 2: 删除旧 note/**

```bash
git rm -r note/
```

- [ ] **Step 3: 重命名 note-temp/ → note/**

```bash
git mv note-temp note
```

- [ ] **Step 4: 更新所有内部链接（不再需要 note-temp 前缀）**

如果有指向 `note-temp/` 的内部链接（应该没有了，因为已经是新结构），用 grep 扫：

```bash
grep -rn "note-temp" note/ | head -10
# 如果有，更新为 note/
```

- [ ] **Step 5: 验证最终状态**

```bash
find note -name "*.md" | wc -l  # 期望 ~1000+
find note -name "SPEC.md" | wc -l  # 期望 14
find note -maxdepth 1 -type d | wc -l  # 期望 14（含 note/ 自身）
```

- [ ] **Step 6: Commit 重命名**

```bash
git add -A
git commit -m "feat: note-temp/ 重命名为 note/（最终结构替换）"
```

- [ ] **Step 7: 健康检查回归**

跑 spec §11 验证清单全部确认通过。

---

## 验证清单（Plan 2 完成时必过）

- [ ] 13 模块全部填实
- [ ] SPEC.md 14 文件完整（1 L0 + 13 L1）
- [ ] note/ 替换后总 .md 数与原 note/ 总数匹配（1100+ ±5）
- [ ] 全库 broken links ≤ 10（剩余应是合理的跨模块占位）
- [ ] 3 个 skill 在新结构上能跑（Phase 6 不属本 plan）
- [ ] pre-existing ralph-wiggum-loop.md 不在任何 commit

---

## 后续 Plans

- **Plan 3**：Phase 6（3 个 Skill 重构）— 独立
- **Plan 4**：合并到 master
