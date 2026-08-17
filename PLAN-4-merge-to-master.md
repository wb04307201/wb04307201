# Plan 4：合并 refactor/skill-note-decouple → master

## 目标
将 `refactor/skill-note-decouple` 分支的所有改动合并到 `master`。

## 当前状态

```
分支: refactor/skill-note-decouple
commits ahead of master: 25+ 个
working tree: clean
```

## 关键 commits（按时间倒序）

```
fb43ae3 fix(note-health): Batch 2 单向链接修复（删除遗留 concepts/ + 修 05.frontend）
2becbf78 feat(note-health): Batch 1 体检修复（138 frontmatter + 19 浅 README + 117 拆分标记）
f0b7e4b4 chore: 清理 training-temp/ 测试残留文件
173b253c chore: 删除 docs/superpowers/（plan + spec 临时文件清理）
31c736d2 test(skill): 第 6 轮 Step 6.1 + T2 + T3 端到端验证
5ae60e0a refactor(training-temp): Step 6.1 深度重组
0266b1d5 refactor(skill): note-precipitation-planning 加 Step 6.1 深度重组
1e9c1126 refactor(skill): note-precipitation-planning Step 6 加 Step 6.0 内容驱动决策
67121037 fix(skill): 最后 3 处 broken 全部修复（3 → 0）
（其他 commits 包括 note/ 结构重构、broken 修复、skill 重构等）
```

## 最终验证

| 项 | 验证结果 |
|---|---|
| note/ 总 .md | 1085 |
| broken | **0** ✅ |
| SPEC.md | 19（1 L0 + 13 L1 + 5 L2） |
| frontmatter 覆盖 | 1064 / 1064（非 SPEC.md，100%） |
| 3 skill 重构 | note-health 239 行 + note-knowledge-qa 843 行 + note-precipitation-planning 1135 行 |
| 镜像同步 | ✅（setup.sh 已跑） |
| 工作树 | clean |

## 合并步骤

```bash
# 1. 切到 master
git checkout master

# 2. 合并（无冲突风险，因为 master 没动过）
git merge refactor/skill-note-decouple

# 3. 推送到远程
git push origin master
```

## 合并后建议

- 删除 refactor/skill-note-decouple 分支（远程 + 本地）
- 更新 CHANGELOG（如果项目有）
- 在 Gitee/GitHub 创建 Release Tag（如 v2026.08-note-restructure）

## 风险评估

- **冲突风险**：低（master 期间无相关改动）
- **回滚方案**：`git revert -m 1 <merge-commit>` 或 `git reset --hard <previous-master>`
- **功能完整性**：note/ 结构完整，3 skill 全部重构并通过端到端测试

## 合并后用户操作建议

1. 重新跑 `bash setup.sh` 同步本地 skill 镜像
2. 检查 `.claude/skills/` 与 `.codex/skills/` 是否有更新
3. 在 IDE 中测试 3 个 skill（实际调用）
