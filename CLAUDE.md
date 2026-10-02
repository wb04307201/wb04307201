# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Type

**个人主页仓库**(GitHub/Gitee profile repo):
- **README.md** — 个人主页 + **12 个开源项目**展示(File View、Spring AI LoomAgent、Flexible Lock 等)
- **profile/** — GitHub README 统计卡片(stats.svg / top-langs.svg,由 grs.yml 每月更新)
- **hp/** — 主页展示图片(PNG)
- **training/** — 培训课件目录

> **2026-09 拆分**:原 `note/` 知识库(13 模块 1100+ .md)及其配套(`skills/`、`scripts/`、`.githooks/`、`setup.sh`、2 个 CI workflow)已整体迁移到独立仓库 **`wb04307201/note`**(本地 `C:\developer\IdeaProjects\note`,内容平铺在其仓库根)。
> 笔记相关的沉淀 / 体检 / 问答 meta-skill、链接校验、commit 规范 hook 均在**新仓库**中维护,本仓库不再包含。
> 完整历史(1975 个 note 相关 commit)保留在本仓库 git 历史中,可通过 `git log --all -- note/` 追溯。

## CI Workflows

`.github/workflows/`(**1 个 workflow**):

| Workflow | 触发时机 | 职责 |
|----------|---------|------|
| **`grs.yml`** | 每月 1 日 02:00 + workflow_dispatch | 更新 `profile/stats.svg` + `top-langs.svg`(GitHub README 卡片,需要 `secrets.TOKEN`) |

> 原 difficulty-calibration.yml / structural-link-check.yml 已随知识库迁至 `wb04307201/note` 仓库。

## 常用命令

```bash
# 主页项目表维护:直接编辑 README.md 的项目表格(12 行)

# 追溯已迁出的笔记历史
git log --oneline --all -- note/ | head -20

# 查看某篇笔记的旧版本(拆分前)
git show <commit>:note/<path>.md
```

## 工作约定

- **README.md 项目表**:新增开源项目时保持表格列对齐(项目名 + 简介 + Gitee/GitHub star 徽章)
- **commit 格式**:沿用 Conventional Commits(`docs(readme): ...` / `chore(profile): ...`);本仓库已无 commit-msg hook,靠自觉
- **profile/*.svg 不要手改** — 由 grs.yml 自动生成
- **技术笔记相关需求** → 去 `C:\developer\IdeaProjects\note` 仓库操作(沉淀规划 / 健康体检 / 知识问答 skill 都在那边)
