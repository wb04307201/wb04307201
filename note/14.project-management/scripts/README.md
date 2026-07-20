<!--
module:
  parent: project-management
  slug: scripts
  type: article
  category: 工具脚本
  summary: 14.project-management 维护脚本（insert-frontmatter / validate）
-->

# 14.project-management 维护脚本

> 两个 Python 工具脚本，用于批量维护 `note/14.project-management/` 下的所有 Markdown 文章。

← [返回 14.project-management 总目录](../README.md) · [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

## 脚本清单

### 1. `insert-frontmatter.py` — 批量插入 frontmatter

**用途**：给 `note/14.project-management/**/*.md` 中缺 frontmatter 的文件批量插入 `pm:` 模块的 frontmatter 模板（含 `topic` / `audience` / `category` / `summary` 4 个字段）。

**调用方法**：

```bash
# 在项目根目录
python note/14.project-management/scripts/insert-frontmatter.py

# Dry-run（只报告不修改）
python note/14.project-management/scripts/insert-frontmatter.py --dry-run
```

**适用场景**：
- 新建 14.project-management 子模块后批量补 frontmatter
- CONTRIBUTING.md §10 升级规范时迁移旧 frontmatter

### 2. `validate.py` — 校验合规性

**用途**：检查 `note/14.project-management/**/*.md` 是否符合 14.project-management 写作规范（详见 [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md)）。

**校验项**：
1. ✓ frontmatter 注释块（`pm:` + `topic` / `audience` / `summary` 字段）
2. ✓ `## 引言` 段（场景开篇）
3. ✓ 文末回链到 `README.md`
4. ✓ 文章行数 ≥ 50
5. ✓ 中文数字章节编号（自动跳过 fenced code block）

**调用方法**：

```bash
python note/14.project-management/scripts/validate.py
```

**退出码**：0 = 全部合规；1 = 存在不合规项。

---

## 维护约定

- 脚本无外部依赖（仅 Python 3.8+ 标准库），可独立运行
- 修改脚本后请同步测试 `note/14.project-management/` 至少 1 个 leaf README
- 重大变更请更新本 README

← [返回: 项目管理](../README.md)