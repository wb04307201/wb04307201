# Git 命令清单

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
git remote -v                   # 查看远程地址
git fetch --prune origin        # 获取更新并清理本地已删除的远程分支
git pull origin <branch>        # 拉取+合并（默认策略：merge）
git push -u origin <branch>     # 首次推送并关联上游
git push --force-with-lease     # 安全强制推送（**2025 标准**）
# ====== 新增：删除远程分支 ======
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












