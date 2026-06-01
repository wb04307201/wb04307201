> ⬅️ [返回目录](README.md)

# 📝 文章整理：Using Skills to Accelerate OSS Maintenance - 评估 Agent 技能的最佳实践

> 来源：OpenAI Developers Blog  
> 主题：如何系统性地评估和改进 Codex Agent 的技能（Skills）
> 链接：https://developers.openai.com/blog/eval-skills

---

## 🔍 核心问题

在迭代开发 Agent 技能（如 Codex）时，开发者常面临：
- 难以判断改进是否真实有效，还是仅仅改变了行为
- 回归问题难以发现（技能未触发、跳过步骤、遗留文件等）

**解决方案**：像测试其他软件一样，为技能建立系统化的 **评估机制（Evals）**

---

## 📋 什么是 Evals（评估）？

> Evals = Prompt → 执行记录（Trace + Artifacts）→ 检查规则 → 可比较的分数

**评估要回答的具体问题**：
- ✅ Agent 是否成功调用了该技能？
- ✅ 是否执行了预期的命令？
- ✅ 输出是否符合约定的规范？

---

## 🎯 评估框架：8 步实践指南

### 1️⃣ 先定义"成功"，再写技能

在编写技能前，明确可衡量的成功标准，分为四类：

| 类别       | 示例问题                  |
|----------|-----------------------|
| **结果目标** | 任务是否完成？应用能否运行？        |
| **过程目标** | 是否按预期调用了工具和步骤？        |
| **风格目标** | 输出是否符合代码/格式规范？        |
| **效率目标** | 是否避免了冗余命令或过度消耗 Token？ |

> 💡 原则：聚焦"必须通过"的核心检查，而非面面俱到

---

### 2️⃣ 创建技能：结构化定义

技能本质是一个包含 `SKILL.md` 的目录，关键要素：

```yaml
---
name: setup-demo-app
description: Scaffold a Vite + React + Tailwind demo app...
---
```

**关键提醒**：
- `name` 和 `description` 是 Codex 判断**是否触发技能**的核心信号
- 描述模糊 = 触发不可靠

**推荐工具**：使用内置 `$skill-creator` 向导快速创建

---

### 3️⃣ 手动触发：暴露隐藏假设

首次测试时，显式调用技能（如 `/skills` 或 `$setup-demo-app`），观察：

| 假设类型 | 常见问题 |
|---------|---------|
| 🔹 触发假设 | 应该触发却没触发，或不该触发时误触发 |
| 🔹 环境假设 | 假设空目录、特定包管理器等 |
| 🔹 执行假设 | 跳过 `npm install`、顺序错误等 |

**自动化准备**：使用 `codex exec --full-auto` 便于脚本化执行

---

### 4️⃣ 构建小型提示词集：快速捕捉回归

无需大型基准测试，**10-20 个精心设计的 prompt** 即可有效评估：

```csv
id,should_trigger,prompt
test-01,true,"Create a demo app named `devday-demo` using the $setup-demo-app skill"
test-02,true,"Set up a minimal React demo app with Tailwind for quick UI experiments"
test-03,true,"Create a small demo app to showcase the Responses API"
test-04,false,"Add Tailwind styling to my existing React app"
```

**设计策略**：
- ✅ 显式调用：测试技能名称/描述变更的影响
- ✅ 隐式调用：测试自然语言描述能否正确触发
- ✅ 上下文调用：测试真实场景中的鲁棒性
- ✅ 负向控制：防止误触发（False Positive）

> 🔄 随着使用，持续将真实失败案例加入评估集

---

### 5️⃣ 轻量级确定性检查：快速反馈

使用 `codex exec --json` 获取结构化执行日志（JSONL），编写确定性检查：

```javascript
// 检查是否执行了 npm install
function checkRanNpmInstall(events) {
  return events.some(e => 
    e.item?.type === "command_execution" && 
    e.item?.command?.includes("npm install")
  );
}

// 检查文件是否存在
function checkPackageJsonExists(projectDir) {
  return existsSync(path.join(projectDir, "package.json"));
}
```

**优势**：
- ⚡ 执行快、结果确定、易于调试
- 🔍 回归问题可精确定位到具体事件

---

### 6️⃣ 基于规则的定性评估：处理"风格"问题

确定性检查无法评估"代码风格"、"组件结构"等主观要求，需引入 **模型辅助评分**：

**步骤**：
1. 运行技能生成代码
2. 用 Codex 执行**只读风格检查**
3. 通过 `--output-schema` 强制输出结构化评分

**评分规则示例（style-rubric.schema.json）**：
```json
{
  "type": "object",
  "properties": {
    "overall_pass": { "type": "boolean" },
    "score": { "type": "integer", "min": 0, "max": 100 },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "pass": { "type": "boolean" },
          "notes": { "type": "string" }
        }
      }
    }
  }
}
```

**执行命令**：
```bash
codex exec "Evaluate the demo-app repository..." \
  --output-schema ./evals/style-rubric.schema.json \
  -o ./evals/artifacts/test-01.style.json
```

---

### 7️⃣ 持续扩展：随技能成熟深化评估

| 扩展方向          | 实现方式                           | 价值         |
|---------------|--------------------------------|------------|
| 🔹 命令冗余检测     | 统计 `command_execution` 事件      | 发现死循环/重复执行 |
| 🔹 Token 预算监控 | 读取 `usage.input/output_tokens` | 优化提示词效率    |
| 🔹 构建验证       | 执行 `npm run build`             | 捕获语法/配置错误  |
| 🔹 运行时冒烟测试    | `curl` 或 Playwright 检查服务       | 验证功能可用性    |
| 🔹 仓库洁净度      | 检查 `git status`                | 防止遗留临时文件   |
| 🔹 权限回归       | 验证最小权限原则                       | 保障自动化安全    |

> 🎯 原则：先快后慢，先确定性后主观性，按需叠加

---

### 8️⃣ 关键总结 ✅

| 要点                   | 说明                             |
|----------------------|--------------------------------|
| 🔹 **衡量真正重要的事**      | 好的评估让回归清晰可见、失败可解释              |
| 🔹 **从可检查的"完成定义"开始** | 用 `$skill-creator` 启动，逐步收紧指令   |
| 🔹 **基于行为做评估**       | 用 `--json` 捕获执行轨迹，编写确定性检查      |
| 🔹 **用模型补足规则盲区**     | 通过 `--output-schema` 实现结构化风格评分 |
| 🔹 **让真实失败驱动覆盖**     | 每次手动修复都应转化为自动化测试               |

---

## 🛠️ 实用命令速查

```bash
# 创建技能
$skill-creator

# 手动执行技能（允许文件写入）
codex exec --full-auto 'Use the $setup-demo-app skill...'

# 自动化评估（输出 JSONL 便于解析）
codex exec --json --full-auto "<prompt>"

# 风格评估（输出结构化 JSON）
codex exec "<prompt>" --output-schema ./schema.json -o result.json
```

---

## 💡 适用场景

- ✅ 开发 Codex / Agent 技能时
- ✅ 需要保证技能行为一致性
- ✅ 团队协作中需要可复现的评估标准
- ✅ 希望将"感觉变好"转化为"数据证明"

---

> 📌 **核心理念**：评估不是终点，而是持续改进的起点。建立"执行→记录→评分→对比"的闭环，让每一次迭代都有据可依。