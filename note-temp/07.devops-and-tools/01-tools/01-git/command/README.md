<!--
module:
  parent: tools
  slug: tools/git-command
  type: article
  category: 主模块子文章
  summary: Git 命令清单 + git switch/restore vs checkout/reset 对比表 + 实战工作流场景。
-->

# Git 命令清单

> 一句话定位：覆盖 **配置 / 仓库 / 文件 / 提交 / 分支 / 远程 / 子模块 / 撤销 / 高级** 9 大类常用命令，重点标注 Git 2.23+ 引入的 `switch` / `restore` 与传统 `checkout` / `reset` 的语义边界。

---

## 基础配置
```bash
git config --global user.name "Your Name"
git config --global user.email "email@example.com"
git config --global core.editor "code --wait"
git config --list --show-origin
```

---

## 仓库初始化与克隆
```bash
git init
git clone <repo_url>
git clone --depth=1 <repo_url>  # 浅克隆
```

---

## 新旧命令对比表（Git 2.23+ 语义清晰化）

`git checkout` 历史包袱重 —— 既切换分支、又恢复文件、还创建分支；Git 2.23 起拆成两条专门命令：

| 场景 | 旧命令 (checkout/reset) | 新命令 (switch/restore) | 说明 |
|------|------------------------|------------------------|------|
| 切换分支 | `git checkout <branch>` | `git switch <branch>` | switch 专门管分支，无法误恢复文件 |
| 创建+切换分支 | `git checkout -b <new>` | `git switch -c <new>` | -c / -C（强制覆盖） 显式表达 |
| 丢弃工作区文件修改 | `git checkout -- <file>` | `git restore <file>` | restore 专门管文件，无法误切换分支 |
| 撤回暂存（保留改动） | `git reset HEAD <file>` | `git restore --staged <file>` | 语义直观：把文件从 index "restore" 回 worktree |
| 撤销提交保留改动 | `git reset --soft HEAD~1` | 同左（reset 仍是首选） | 撤回 commit 但保留 staged |
| 撤销提交清空暂存 | `git reset --mixed HEAD~1` | 同左 | 默认 `git reset` 行为 |
| 撤销提交+工作区 | `git reset --hard HEAD~1` | `git restore --source=HEAD~1 --staged --worktree <file>` | **危险！** 会丢未提交改动 |

**结论**：新项目用 `switch` + `restore` 让命令意图自解释；老代码可沿用 `checkout`，但**禁止**将其作为"恢复文件"的工具 —— 误切分支代价大。

---

## 文件操作
```bash
git add <file>                  # 添加文件
git add .                       # 添加所有变更
git restore --staged <file>     # 从暂存区撤回（替代 git reset HEAD）
git restore <file>              # 丢弃工作区修改（替代 git checkout --）
git rm <file>                   # 删除文件
git mv <old> <new>              # 重命名文件
```

---

## 提交与历史
```bash
git commit -m "Message"
git commit --amend --no-edit    # 修改提交（不改 message）
git log --oneline --graph --all # 可视化全分支历史
git blame -L 10,20 <file>       # 查看指定行范围的修改记录
```

---

## 分支管理
```bash
git branch -a                   # 列出所有分支（含远程）
git switch -c <new-branch>      # 创建+切换分支（替代 checkout -b）
git switch <branch>             # 切换分支（替代 checkout）
git merge <branch>              # 合并分支
git rebase <branch>             # 变基
git branch -d <branch>          # 安全删除
git branch -D <branch>          # 强制删除
```

---

## 远程协作
```bash
git remote add origin <url>     # 添加远程仓库
git remote remove origin        # 删除远程仓库
git remote -v                   # 查看远程地址
git fetch --prune origin        # 获取更新并清理本地已删除的远程分支
git pull origin <branch>        # 拉取+合并（默认策略：merge）
git push -u origin <branch>     # 首次推送并关联上游
git push --force-with-lease     # 安全强制推送（**2025 标准**）
git push origin --delete <branch>  # 安全删除远程分支（推荐）
git push origin :<branch>          # 旧式删除（冒号语法）
```

---

## 子模块管理
```bash
git submodule add <repo_url> <path>  # 添加子模块
git submodule init                    # 初始化 .gitmodules 配置
git submodule update --remote         # 更新子模块到最新提交
git submodule update --init --recursive # 克隆时初始化所有子模块
git submodule foreach 'git switch main' # 批量切换所有子模块分支
git rm <submodule_path>               # 安全移除子模块（需手动清理配置）
```

---

## 撤销与回退
```bash
git restore --source=HEAD~1 --worktree --staged <file>  # 丢弃特定文件的修改
git reset --soft HEAD~1           # 撤销提交，保留暂存区
git reset --mixed HEAD~1          # 撤销提交+暂存区（默认）
git reset --hard HEAD~1           # 彻底丢弃（**危险！**）
git revert <commit-id>            # 安全撤销已推送提交
```

---

## 高级工具
```bash
git stash push -m "WIP"           # 保存工作进度（带描述）
git stash pop                     # 恢复最近 stash
git bisect start <bad> <good>     # 二分查找问题提交
git cherry-pick <commit-id>       # 拣选提交
git reflog show --relative-date   # 查看 HEAD 历史（带相对时间）
```

---

## 实战工作流场景

### 场景 1：撤销最近一次 commit，但保留所有改动

**问题**：`git commit` 后发现漏了几个文件，或想拆 commit，但**不想丢失任何工作**。

```bash
# 推荐 1：最新 commit 还未推送，彻底重做
git reset --soft HEAD~1      # 撤销 commit；改动回到暂存区，可重新 git add / commit
# 或
git commit --amend           # 在原 commit 内追加 / 改 message

# 推荐 2：已推送但还没人拉
git revert HEAD              # 生成一个反向 commit，保留历史可追溯
# 然后正常 git push
```

**对比**：`--soft` 会**重写历史**；`revert` **新增一条记录**。已推送共享的提交必须用 `revert`。

### 场景 2：当前分支弄错了，希望迁回 main 上重新切

```bash
git switch main                      # 回到主分支
git branch -D feature/old            # 删掉弄错的本地分支（强删 -D）
# 取回你未推送的所有改动：先 stash，再 unstash
git stash push -m "wip-from-wrong"
git switch -c feature/right          # 新建正确分支
git stash pop                        # 改动回来
```

### 场景 3：在多个提交里拣选修复 cherry-pick

```bash
git switch main
git cherry-pick <commit-id>          # 把某条独立修复搬运到当前分支
git cherry-pick <id1> <id2>          # 多条
git cherry-pick -x <commit-id>       # 记录原始来源（审计友好）
```

### 场景 4：误把敏感信息提交了，怎么"消除"历史

```bash
git filter-repo --path secrets.txt --invert-paths   # 需要安装 git-filter-repo
# 所有 commit 中删除该文件；接着强制推送
git push --force-with-lease --all                   # --all 涵盖所有分支
```

`--force-with-lease` 会校验远程 HEAD 未被别人推进，**比 `git push --force` 安全**。注意：对已拉取此历史的协作者必须告知重置基线（`git fetch origin && git reset --hard origin/main`）。

---

## 相关阅读

- [Git 工具总览](../README.md) — 命令清单 + Gitea 自托管
- [Gitea 自托管](../gitea/README.md) — 团队私有代码托管平台

← [返回 Git 工具](../README.md)
