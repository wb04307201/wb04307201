# note 知识库优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 5 项设计（PNG 资产治理 / CONTRIBUTING 重盘 / README emoji 统一）实施 note 知识库的剩余优化。

**Architecture:** 5 个独立 commit，每个任务可独立验证。顺序：§1 (doc) → §3 (PNG→Mermaid) → §2 (删孤儿) → §4 (接回引用) → §5 (emoji 统一)。

**Tech Stack:** Markdown / Git Bash / Git / Mermaid（替换 PNG 时）

## 全局约束

- **不动脚本**：用户已禁用所有 scripts（CONTRIBUTING §8 历史说明）
- **手工核对**：每 § 完成后人工对照验收命令
- **commit message 规范**：CONTRIBUTING §6 conventional commits
  - `docs(note):` 文档类
  - `chore(note):` 资产清理
  - `refactor(note):` PNG → Mermaid
  - `fix(note):` 接回引用
  - `style(note):` emoji 一致性
- **emoji 风格**：沿用 06.spring / 07.workflow 已有风格；09.front-end / 10.big-data 保留 "## X、~ ## X一、" 中文序号
- **不动范围**：872 个 markdown 内容质量、scripts/、frontmatter、数字声明、CI workflow、profile/ tools/ .github/

## 文件结构总览

| 操作 | 路径 |
|------|------|
| Modify | `note/CONTRIBUTING.md`（§5 + §11） |
| Modify | `note/07.workflow/apache-eventmesh/cloud-flow/README.md`（3 PNG 处理） |
| Modify | `note/07.workflow/process-engine/camunda/camunda-7/README.md`（4 PNG 处理） |
| Modify | `note/07.workflow/process-engine/camunda/camunda-8/README.md`（2 PNG 处理） |
| Delete | note/ 下 ~107 个孤儿 PNG（散布 25+ 目录） |
| Modify | `note/06.spring/03-data/mybatis/01-architecture/README.md`（加 1 张图引用） |
| Modify | `note/06.spring/03-data/mybatis/04-mybatis-plus/README.md`（加 1 张图引用） |
| Modify | `note/01.java/README.md`（加 emoji） |
| Modify | `note/02.computer-basics/README.md`（加 emoji） |
| Modify | `note/03.database/README.md`（加 emoji） |
| Modify | `note/11.ai/README.md`（加 emoji） |
| Modify | `note/12.story/README.md`（加 emoji） |
| Modify | `note/13.split-hairs/README.md`（加 emoji） |
| Modify | `note/14.project-management/README.md`（加 emoji） |
| Modify | `note/09.front-end/README.md`（加 emoji，保留中文序号） |
| Modify | `note/10.big-data/README.md`（加 emoji，保留中文序号） |

---

### Task 1: CONTRIBUTING §5 + §11 重盘

**Files:**
- Modify: `note/CONTRIBUTING.md`（§5.4 状态行 + §11 自检表"02/03/04/08 缺开源参考"那行）

**前置条件：** 无

**interfaces：**
- 消费：无
- 产出：CONTRIBUTING 数字与现状对齐

- [ ] **Step 1: 修改 §5.4 状态行**

打开 `note/CONTRIBUTING.md`，定位到 L220-228 附近的 §5.4 状态章节，将"其他 11 个文件目录中**有 PNG 文件但 README 未引用**"改为"其他 25 个文件目录中**有 PNG 文件但 README 未引用**"，并在同节末尾加一行：

```
- [ ] 待执行 §2（孤儿 PNG 清理）：见实施计划 `docs/superpowers/plans/2026-07-01-note-optimization.md` Task 3
```

- [ ] **Step 2: 修改 §11 自检表**

定位到 L311-353 附近的 §11，删除"建议 01-11 缺'## 开源参考'的模块补足：02/03/04/08 共 4 个。"这一行，并在末尾加：

```
> 📌 **2026-07-01 现状修正**：02/03/04/08 四个主模块的 `## 开源参考` 段均已补齐，不再列入待补清单。
```

- [ ] **Step 3: 验证修改**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep "02/03/04/08 缺" CONTRIBUTING.md
grep "其他 25 个文件目录" CONTRIBUTING.md
```

预期：第一个命令无输出；第二个命令有 1 处匹配。

- [ ] **Step 4: 提交**

```bash
cd C:/developer/IdeaProjects/wb04307201
git add note/CONTRIBUTING.md
git -c user.name="吴博" -c user.email="wubo_aaa@163.com" commit -m "docs(note): CONTRIBUTING §5.4 + §11 数字与现状对齐

- §5.4: '其他 11 个目录' → '其他 25 个目录'（按 2026-07-01 重盘）
- §11: 删 '02/03/04/08 缺开源参考' 那行（4 个都已补）
- 加引用：指向实施计划 Task 3

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 9 张 PNG → Mermaid 替换（含回退路径）

**Files:**
- Modify: `note/07.workflow/apache-eventmesh/cloud-flow/README.md`（3 张）
- Modify: `note/07.workflow/process-engine/camunda/camunda-7/README.md`（4 张）
- Modify: `note/07.workflow/process-engine/camunda/camunda-8/README.md`（2 张）
- 视情况重命名或删除对应 PNG

**前置条件：** Task 1 完成

**interfaces：**
- 消费：原 PNG 文件路径（用于回退时参照）
- 产出：每个文件要么有等价 Mermaid，要么 PNG 按 §3.2 命名

- [ ] **Step 1: 处理 cloud-flow 3 张 PNG**

打开 `note/07.workflow/apache-eventmesh/cloud-flow/README.md`，找到 L1-L3 的 3 张 PNG（文件名可能为 `img.png` / `img_1.png` / `img_2.png`）。

逐张处理：
1. Read PNG 文件查看图意（用 Read 工具查看）
2. 设计等价 Mermaid（推荐 `graph TB` 或 `flowchart TD`）
3. 替换 markdown 中的 `![img_N.png](img_N.png)` 为 Mermaid 块
4. 删除对应 PNG（用 `git rm`）

> **回退**：如果 Mermaid 表达不了（如复杂泳道 / UI 截图），保留 PNG 并用 Edit 重命名为 `{主题}-{描述}.png`，更新 markdown 引用。

- [ ] **Step 2: 处理 camunda-7 4 张 PNG**

打开 `note/07.workflow/process-engine/camunda/camunda-7/README.md`，找到 L131 / L163 / L234 / L389 的 4 张 PNG（BPMN 流程图）。

注意：BPMN 流程图含用户任务、服务任务、网关等多元素，Mermaid 难以 1:1 表达。**预估 1-2 张需回退为 PNG + 改名**。

操作：与 Step 1 相同。

- [ ] **Step 3: 处理 camunda-8 2 张 PNG**

打开 `note/07.workflow/process-engine/camunda/camunda-8/README.md`，找到 L88 / L102 的 2 张 PNG（Zeebe 架构图）。通常可转为 `graph TB`。

操作：与 Step 1 相同。

- [ ] **Step 4: 验证 PNG 状态**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
ls 07.workflow/apache-eventmesh/cloud-flow/
ls 07.workflow/process-engine/camunda/camunda-7/
ls 07.workflow/process-engine/camunda/camunda-8/
```

预期：每个目录的 PNG 数 = 实际保留数（转 Mermaid 后删除的 PNG 不应存在；回退保留的应已改名）。

- [ ] **Step 5: 提交**

```bash
cd C:/developer/IdeaProjects/wb04307201
git add -A note/07.workflow/
git -c user.name="吴博" -c user.email="wubo_aaa@163.com" commit -m "refactor(note): 9 张 PNG → Mermaid 替换（含回退）

- cloud-flow: 3 张架构图转 Mermaid
- camunda-7: 4 张 BPMN 处理（部分回退为命名规范 PNG）
- camunda-8: 2 张 Zeebe 架构图转 Mermaid

回退保留的 PNG 已按 CONTRIBUTING §3.2 命名规范：{主题}-{描述}.png

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 删除 ~107 个孤儿 PNG

**Files:**
- Delete: `note/` 下 ~107 个孤儿 PNG（散布在 25+ 目录）

**前置条件：** Task 2 完成（确保已迁移/回退的 PNG 状态确定）

**interfaces：**
- 消费：当前 PNG 列表 + 已被 README 引用列表
- 产出：剩余 ~42 个 PNG（与 spec §2 保留清单匹配）

- [ ] **Step 1: 生成孤儿 PNG 清单**

```bash
cd C:/developer/IdeaProjects/wb04307201/note

# 列出所有 PNG
all_pngs=$(find . -name "*.png")

# 列出所有被 README 引用的 PNG
referenced=$(grep -rohE '!\[[^]]*\]\([^)]*\.png\)' . | grep -oE '[^()/]+\.png' | sort -u)

# 差集 = 孤儿
orphans=()
for png in $all_pngs; do
  basename_png=$(basename "$png")
  if ! echo "$referenced" | grep -q "$basename_png"; then
    orphans+=("$png")
  fi
done

printf '%s\n' "${orphans[@]}" > /tmp/orphan_pngs.txt
wc -l /tmp/orphan_pngs.txt
```

预期输出：约 100-110 行（实际数 = 149 - 保留数）。

- [ ] **Step 2: 人工核对孤儿清单**

```bash
cat /tmp/orphan_pngs.txt
```

**关键核对点**：
- 确认 lesson9 tutorial-images 下的 26 张 PNG 全部**不在**孤儿清单（它们都被 README3.md / README2.md 引用）
- 确认 mybatis 下的 2 张规范 PNG 全部**不在**孤儿清单（它们在 Task 4 才接回引用，目前仍属于"孤儿但保留"——处理见 Step 3）
- 确认 lesson1/img.png ~ img_6.png 不在孤儿清单

如果发现应保留的 PNG 在孤儿清单中，**立即停止**，调整 Step 1 的判定逻辑（可能需要更宽松的匹配）。

- [ ] **Step 3: 排除 mybatis 2 张暂留 PNG**

mybatis 2 张图在 Task 4 才接回引用，目前状态是"规范命名但未被 README 引用"。删除它们会导致 Task 4 无图可引。

```bash
# 从孤儿清单排除 mybatis 的 2 张
grep -v "mybatis/.*img/.*\.png" /tmp/orphan_pngs.txt > /tmp/orphan_pngs_filtered.txt
wc -l /tmp/orphan_pngs_filtered.txt
```

预期：比 Step 1 输出少 2 行。

- [ ] **Step 4: 删除孤儿 PNG（用 git rm 跟踪删除）**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
xargs -I {} git rm "{}" < /tmp/orphan_pngs_filtered.txt
```

预期输出：`git rm` 报告每个文件被删除。

- [ ] **Step 5: 验证剩余 PNG 数**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
find . -name "*.png" | wc -l
```

预期：约 42 个（5 篇 README 引用的 + mybatis 2 张 + lesson9 26 张 + lesson1 7 张 + lesson13 1 张 + camunda 命名规范 1-2 张）。

- [ ] **Step 6: 提交**

```bash
cd C:/developer/IdeaProjects/wb04307201
git -c user.name="吴博" -c user.email="wubo_aaa@163.com" commit -m "chore(note): 删除 ~107 个孤儿 PNG

按 spec §2 实施：保留 5 篇 README 引用的 + mybatis 2 张（Task 4 接回）+ lesson9 26 张规范命名 + lesson1 7 张 + lesson13 1 张占位 + camunda 回退保留的规范命名 PNG。

孤儿判定：未被同目录任意 .md 以 ![]() 语法引用。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: Mybatis 2 张规范 PNG 接回 README

**Files:**
- Modify: `note/06.spring/03-data/mybatis/01-architecture/README.md`
- Modify: `note/06.spring/03-data/mybatis/04-mybatis-plus/README.md`

**前置条件：** Task 3 完成（确保 PNG 文件还在）

**interfaces：**
- 消费：`note/06.spring/03-data/mybatis/01-architecture/img/architecture-flow.png`
- 消费：`note/06.spring/03-data/mybatis/04-mybatis-plus/img/wrapper-class-hierarchy.png`
- 产出：两个 README 各自加 1 处图片引用

- [ ] **Step 1: 确认 PNG 存在**

```bash
ls C:/developer/IdeaProjects/wb04307201/note/06.spring/03-data/mybatis/01-architecture/img/
ls C:/developer/IdeaProjects/wb04307201/note/06.spring/03-data/mybatis/04-mybatis-plus/img/
```

预期：第一个命令看到 `architecture-flow.png`；第二个看到 `wrapper-class-hierarchy.png`。

- [ ] **Step 2: 读 01-architecture README 找位置**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep -nE "架构流程|architecture|流程" 06.spring/03-data/mybatis/01-architecture/README.md | head -10
```

预期：找到描述"架构流程"或类似语义的章节位置。

- [ ] **Step 3: 在 01-architecture README 加图片引用**

用 Edit 工具，在最相关的描述段落后插入：

```markdown
![架构流程](img/architecture-flow.png)
```

如果找不到合适的描述段落，**在文末"## 附录"或"## 架构图"段前加**。

- [ ] **Step 4: 读 04-mybatis-plus README 找位置**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep -nE "Wrapper|wrapper|层级|hierarchy" 06.spring/03-data/mybatis/04-mybatis-plus/README.md | head -10
```

预期：找到描述 Wrapper 类的章节。

- [ ] **Step 5: 在 04-mybatis-plus README 加图片引用**

用 Edit 工具，在 Wrapper 类层级描述段落后插入：

```markdown
![Wrapper 类层级](img/wrapper-class-hierarchy.png)
```

- [ ] **Step 6: 验证两处引用都生效**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep -rE "architecture-flow.png|wrapper-class-hierarchy.png" .
```

预期：至少 2 处匹配（每个 README 一处）。

- [ ] **Step 7: 提交**

```bash
cd C:/developer/IdeaProjects/wb04307201
git add note/06.spring/03-data/mybatis/01-architecture/README.md note/06.spring/03-data/mybatis/04-mybatis-plus/README.md
git -c user.name="吴博" -c user.email="wubo_aaa@163.com" commit -m "fix(note): mybatis 2 张规范 PNG 接回 README

- 01-architecture/README.md: 加 img/architecture-flow.png 引用
- 04-mybatis-plus/README.md: 加 img/wrapper-class-hierarchy.png 引用

按 CONTRIBUTING §3.2 命名规范已就绪，仅缺 README 引用。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: 14 主模块 README emoji 统一（加 emoji 档）

**Files:**
- Modify: `note/01.java/README.md`（6 H2）
- Modify: `note/02.computer-basics/README.md`（6 H2）
- Modify: `note/03.database/README.md`（7 H2，含 1 个 🎯）
- Modify: `note/11.ai/README.md`（6 H2）
- Modify: `note/12.story/README.md`（12 H2，叙事系列不规则）
- Modify: `note/13.split-hairs/README.md`（17 H2）
- Modify: `note/14.project-management/README.md`（10 H2）
- Modify: `note/09.front-end/README.md`（11 H2，**保留"## X、"中文序号**）
- Modify: `note/10.big-data/README.md`（11 H2，**保留"## X、"中文序号**）

**前置条件：** Task 1-4 完成（emoji 改动是大动作，最后做）

**interfaces：**
- 消费：每个 README 当前 H2 文本（实施前用 grep 列出）
- 产出：每个 H2 前加 1 个 emoji（语义对应）

**emoji 映射约定**（按 06.spring / 07.workflow 风格）：
- 一句话定位 / 概述 → 🎯
- 知识地图 / 体系 → 🗺️
- 章节导航 / 目录 → 📚
- 速查表 / Cheat Sheet → 📊
- 学习路径 / 路线 → 🧭
- 核心内容 / 详解 → 📖
- 最佳实践 → 🏆
- 案例 / 真实落地 → 💼
- 相关章节 / 上下游 → 🔗
- 开源参考 / 外部参考 → 📖
- 数据时效性 → ⏰
- 章节统计 → 📊
- 变更记录 → 📝
- 术语表 / 附录 → 📖
- 高频面试题 → 🎯
- 思考 / FAQ → 🤔
- 推荐 → ⭐
- 其他 → 🎯（兜底）

- [ ] **Step 1: 处理 01.java/README.md**

读取 `note/01.java/README.md`，按 emoji 映射约定给每个 H2 加前缀。例如：

```markdown
## 🎯 目录导航
## 🗺️ 知识脉络
## 📊 速查表
## 🧭 学习路径
## 🔗 相关章节
## 📖 开源参考
```

**用 Edit 工具逐个修改**。注意保持 H2 后面的中文文本不变。

- [ ] **Step 2: 处理 02.computer-basics/README.md**

读取 `note/02.computer-basics/README.md`，按相同约定加 emoji。结构与 01.java 相似。

- [ ] **Step 3: 处理 03.database/README.md**

读取 `note/03.database/README.md`。注意已有 1 个 `## 🎯 高频面试题`，保持不变；其余 6 个 H2 加 emoji。

- [ ] **Step 4: 处理 11.ai/README.md**

读取 `note/11.ai/README.md`，按 6 节约定加 emoji。

- [ ] **Step 5: 处理 12.story/README.md**

读取 `note/12.story/README.md`，按 12 个 H2 语义加 emoji。叙事系列 H2 语义多样，按映射约定灵活选择。

- [ ] **Step 6: 处理 13.split-hairs/README.md**

读取 `note/13.split-hairs/README.md`，按 17 个 H2 语义加 emoji。13 模块 H2 数最多，需逐个判断。

- [ ] **Step 7: 处理 14.project-management/README.md**

读取 `note/14.project-management/README.md`，按 10 个 H2 语义加 emoji。

- [ ] **Step 8: 处理 09.front-end/README.md（保留中文序号）**

读取 `note/09.front-end/README.md`，在"## 一、" "## 二、" 序号后加 emoji：

```markdown
## 一、🎯 9 模块导航
## 二、🧭 知识脉络
## 三、📊 速查地图
## 四、🤔 选型决策树
## 五、🧭 学习路线
## 5a. 🏆 最佳实践
## 六、🔗 交叉引用
## 七、📖 开源参考
## 八、⏰ 数据时效性
## 九、📊 章节统计
## 十、📝 变更记录
## 十一、📖 附录：术语表
```

- [ ] **Step 9: 处理 10.big-data/README.md（保留中文序号）**

读取 `note/10.big-data/README.md`，与 09.front-end 同模式：

```markdown
## 一、🎯 9 模块导航
## 二、🧭 知识脉络
## 三、🤔 选型决策树
## 四、📊 速查地图
## 五、🧭 学习路线
## 5a. 🏆 最佳实践
## 六、🔗 交叉引用
## 七、📖 开源参考
## 八、⏰ 数据时效性
## 九、📊 章节统计
## 十、📝 变更记录
## 十一、📖 附录：术语表
```

- [ ] **Step 10: 验证 14 主模块 H2 全带 emoji**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
for d in 01.java 02.computer-basics 03.database 04.system-design 05.tools 06.spring 07.workflow 08.application-systems 09.front-end 10.big-data 11.ai 12.story 13.split-hairs 14.project-management; do
  echo "=== $d ==="
  grep -E "^## " "$d/README.md" | head -20
done
```

预期：14 个模块的每个 `## ` 行首字符为 emoji（0-9 开头的不算——但 09/10 的"## 一、"是例外）。

- [ ] **Step 11: 提交**

```bash
cd C:/developer/IdeaProjects/wb04307201
git add note/01.java/README.md note/02.computer-basics/README.md note/03.database/README.md note/11.ai/README.md note/12.story/README.md note/13.split-hairs/README.md note/14.project-management/README.md note/09.front-end/README.md note/10.big-data/README.md
git -c user.name="吴博" -c user.email="wubo_aaa@163.com" commit -m "style(note): 14 主模块 README H2 emoji 统一

C 档加 emoji（7 个）：01/02/03/11/12/13/14
B 档加 emoji 保留序号（2 个）：09/10 「## X、」 中文序号

emoji 映射：🎯概述 / 🗺️体系 / 📚导航 / 📊速查 / 🧭路径 / 📖内容 / 🏆实践 / 🔗关联 / 📖参考 / ⏰时效 / 📝记录

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 整体验收

**Files:** 无（验证步骤）

**前置条件：** Task 1-5 全部完成

**interfaces：** 无

- [ ] **Step 1: 验收 §1**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep "02/03/04/08 缺" CONTRIBUTING.md && echo "❌ FAIL" || echo "✅ PASS"
```

预期：✅ PASS。

- [ ] **Step 2: 验收 §2**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
total=$(find . -name "*.png" | wc -l)
echo "剩余 PNG: $total"
[ "$total" -lt 50 ] && echo "✅ PASS" || echo "⚠️ 大于 50，需要重新核对"
```

预期：剩余 PNG < 50，✅ PASS。

- [ ] **Step 3: 验收 §3**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
echo "cloud-flow PNG:"
ls 07.workflow/apache-eventmesh/cloud-flow/ | grep -c "\.png"
echo "camunda-7 PNG:"
ls 07.workflow/process-engine/camunda/camunda-7/ | grep -c "\.png"
echo "camunda-8 PNG:"
ls 07.workflow/process-engine/camunda/camunda-8/ | grep -c "\.png"
```

预期：每个目录 PNG 数 ≤ 处理前；回退保留的 PNG 命名符合 §3.2 规范（`{主题}-{描述}.png`）。

- [ ] **Step 4: 验收 §4**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
grep -rE "architecture-flow.png|wrapper-class-hierarchy.png" . | wc -l
```

预期：≥ 2。

- [ ] **Step 5: 验收 §5**

```bash
cd C:/developer/IdeaProjects/wb04307201/note
for d in 01.java 02.computer-basics 03.database 11.ai 12.story 13.split-hairs 14.project-management; do
  no_emoji=$(grep -E "^## " "$d/README.md" | grep -vE "^## [🎯🗺️📚📊🧭📖🏆💼🔗⏰📝🤔⭐🛤️✅⚡📋🎯🛡️⚙️🔐🚀🆕]" | wc -l)
  if [ "$no_emoji" -gt 0 ]; then
    echo "❌ $d: $no_emoji 个 H2 缺 emoji"
  else
    echo "✅ $d"
  fi
done
```

预期：7 个 C 档模块全部 ✅。

```bash
for d in 09.front-end 10.big-data; do
  no_emoji=$(grep -E "^## " "$d/README.md" | grep -vE "^## (一|二|三|四|五|六|七|八|九|十|5a)、[🎯🗺️📚📊🧭📖🏆💼🔗⏰📝🤔⭐🛤️✅⚡📋🎯🛡️⚙️🔐🚀🆕]" | wc -l)
  if [ "$no_emoji" -gt 0 ]; then
    echo "❌ $d: $no_emoji 个 H2 不符合 emoji+序号 模式"
  else
    echo "✅ $d"
  fi
done
```

预期：2 个 B 档模块全部 ✅。

- [ ] **Step 6: git log 检查**

```bash
cd C:/developer/IdeaProjects/wb04307201
git log --oneline -8
```

预期：看到 5 个新 commit（Task 1-5 各一个）+ 1 个 spec commit（已存在）+ 1 个总体验收 commit（如需要）。

- [ ] **Step 7: 总结报告**

向用户报告：
- 每个 § 的验收结果
- 9 张 PNG 处理的最终统计（Mermaid 转换数 / 回退保留数）
- 剩余 PNG 总数（应该 < 50）
- emoji 改动文件数
- 任何偏离原计划的情况