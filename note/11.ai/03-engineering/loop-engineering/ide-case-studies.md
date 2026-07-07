<!--
module:
  parent: ai/loop-engineering
  slug: ai/loop-engineering/ide-case-studies
  type: topic
  category: IDE 案例研究
  summary: 4 大 AI IDE Loop 工程实战 —— Claude Code / Cursor / Devin / Aider 各自的循环工程 + Verifier + 自动修复策略
-->

# 4 大 AI IDE Loop 工程实战案例

> **一句话**：4 大 AI IDE（Claude Code / Cursor / Devin / Aider）都基于 Loop Engineering + Verifier——但**循环粒度、Verifier 设计、自动化程度**各不相同。

← [返回: Loop Engineering 总目录](../README.md)

---

## 1. Claude Code（Anthropic）

### 1.1 Loop 工程

```python
# 简化示意（非 Anthropic 源码）
class ClaudeCodeLoop:
    """Claude Code 内部 Loop 实现原理"""
    def execute(self, task):
        for attempt in range(20):
            code = self.generate(task, context)
            
            # 1. Verifier 1: 静态检查
            ts_errors = run_typecheck(code)
            if ts_errors:
                context.add_errors(ts_errors)
                continue  # 进入下一轮 Loop
            
            # 2. Verifier 2: 单元测试
            test_result = run_tests(code)
            if not test_result.all_passed:
                context.add_test_failures(test_result)
                continue
            
            # 3. Verifier 3: lint
            if not lint_pass(code):
                context.add_lint_errors()
                continue
            
            # 4. 全部通过 → commit
            return code
        
        # 超限 → 转人工
        return None
```

### 1.2 关键特征

- **Loop 触发**：`/loop` 命令 + Plan Mode 自动启用
- **Verifier**：内置 Bash + Edit + Read 工具作为执行验证
- **Context 管理**：自动 summary 压缩（避免 context 爆炸）
- **Harness 兜底**：max_iterations=20 + user confirm

### 1.3 实战示例

```
> /loop "实现用户登录 API"
→ Agent 写代码 → run test (失败) → 修复 → run test (失败) → 修复 → 通过
→ 用了 5 轮 Loop，13 秒内完成
```

---

## 2. Cursor

### 2.1 Loop 工程

```
┌─────────────────────────────────────────────────────────┐
│  Composer (Cursor 的 Loop 引擎)                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Plan: 用户需求 → 子任务列表                      │ │
│  │ 2. Generate: 为每个子任务生成代码                      │ │
│  │ 3. Verify: 运行测试 + lint + typecheck               │ │
│  │ 4. Fix: 失败 → 回到 Step 2 修复                       │ │
│  │ 5. Commit: 全部通过 → 提交                           │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2.2 关键特征

- **Plan-Execute-Reflect**：3 阶段严格分离
- **Verifier**：集成测试 runner + 类型检查 + lint
- **并行执行**：多个子任务可并行 Loop
- **YOLO mode**：可跳过 Verifier（生产慎用）

### 2.3 实战示例

```
> Composer: "重构 user 模块到 DDD"
→ Plan：拆成 5 个子任务（domain/entity, repository, service, controller, test）
→ 串行 Loop：每个子任务独立 verify
→ 全部通过 → 单次提交
```

---

## 3. Devin（Cognition AI）

### 3.1 Loop 工程（Plan-and-Execute 范式）

```python
# Devin 内部简化
class DevinLoop:
    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()
        self.verifier = CompositeVerifier([
            UnitTestVerifier(),
            IntegrationTestVerifier(),
            LintVerifier(),
            TypeCheckVerifier(),
            BrowserTestVerifier(),  # Devin 特色：用浏览器测前端
        ])
    
    def execute(self, task):
        # Phase 1: Plan
        plan = self.planner.plan(task)
        
        # Phase 2: Execute + Verify Loop
        for step in plan.steps:
            result = self.executor.execute(step)
            if not self.verifier.check(result):
                # Phase 3: Reflect + RePlan
                new_plan = self.replan(plan, step, result)
                plan = new_plan
            else:
                plan.mark_done(step)
        
        # Phase 4: Commit
        return self.commit(plan)
```

### 3.2 关键特征

- **Plan-Execute-Reflect**：完整的 Plan-and-Execute Loop
- **Browser Verifier**：Devin 特色，能用浏览器测试前端
- **Long-running**：单任务可跑 10+ 分钟（多轮 Loop）
- **Async feedback**：用户可异步确认

---

## 4. Aider（开源）

### 4.1 Loop 工程（最简）

```python
# Aider 是 Git-aware AI pair programming
class AiderLoop:
    def execute(self, task):
        # 1. 读取当前仓库（git-aware）
        files = git_status()
        
        # 2. 生成 patch
        patches = llm.generate_patches(files, task)
        
        # 3. 应用 patch
        for patch in patches:
            apply_patch(patch)
            
            # 4. Verifier（可选）
            if has_tests():
                if not tests_pass():
                    revert_patch()
                    refine_prompt()
                    continue
        
        # 5. Auto commit
        git_commit(message=auto_generate_message())
```

### 4.2 关键特征

- **简单 Loop**：没有复杂的 Plan-Execute
- **Git-aware**：每次修改都 commit / 可回滚
- **Map-reduce**：多文件并行修改
- **linter**：自动 run linter + auto-fix

---

## 5. 4 大 IDE Loop 对比

| 维度 | Claude Code | Cursor | Devin | Aider |
|------|-------------|--------|-------|-------|
| **Loop 触发** | `/loop` 命令 | Composer | 全自动 | 全自动 |
| **Loop 粒度** | 文件级 | 子任务级 | Plan 内多步 | patch 级 |
| **Verifier** | Bash + Edit | test + typecheck | test + browser | linter + git |
| **Plan 阶段** | 有 | 有 | **强 Plan** | 无 |
| **并行 Loop** | ❌ | ✅（多子任务）| ✅ | ✅（多 patch）|
| **Harness 兜底** | max_iter=20 | YOLO 模式 | long-running | git revert |
| **发布就绪** | ✅ | ✅ | ✅（企业级）| ⚠️（开源） |

---

## 6. 实战选型

```
选型决策：

Q1：是 IDE 插件还是独立工具？
├─ IDE 插件（VSCode / JetBrains）→ Cursor / Aider
└─ 独立工具 / 终端 → Claude Code / Devin

Q2：需要浏览器测前端吗？
├─ 需要 → Devin / Devin-like
└─ 纯后端 / 命令行 → Claude Code / Aider

Q3：需要"异步长任务"吗？
├─ 是（任务超过 5 分钟）→ Devin
└─ 否 → Claude Code

Q4：开源优先？
├─ 是 → Aider
└─ 否（要完整产品）→ Claude Code / Cursor / Devin
```

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：跳过 Verifier 信任 Agent

- 错：Agent 说"我改完了"就直接 commit
- 对：必须有客观 Verifier 信号

### ⚠️ 反模式 2：Verifier 只用 1 种

- 错：只用"测试通过"作为唯一信号
- 对：测试 + 类型 + lint + 编译 组合

### ⚠️ 反模式 3：Loop 无限循环

- 错：失败 100 次还在重试
- 对：max_iterations 上限 + 超限转人工

### ⚠️ 反模式 4：丢失循环上下文

- 错：第 N 次循环丢掉错误历史
- 对：所有错误栈 + 修复尝试写 Context

### ⚠️ 反模式 5：自动 commit 不 review

- 错：每次 Loop 通过就 commit 到 main
- 对：先 commit 到 feature 分支 + CI + PR review

---

## 8. 一句话总结

> **4 大 IDE 都是 Loop Engineering 范式：Plan → Generate → Verify → Fix 循环。Claude Code 重交互 / Cursor 重 Plan / Devin 重 Long-running / Aider 重 Git-aware。实战按场景选 + 不跳过 Verifier + 不超 max_iterations。**

---

← [返回: Loop Engineering 总目录](../README.md) · 上一章：[verifier-design](verifier-design.md) · 下一章：[fix-prompt-templates](fix-prompt-templates.md)
