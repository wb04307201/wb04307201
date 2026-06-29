# 12 篇 AI 应用案例 · 设计规格

> 创建于：2026-06-29
> 状态：已通过用户确认，待进入实施

## 一、目标

在 `note/11.ai/05-applications/case-studies/` 下新增 12 篇 AI 应用案例文章，每篇聚焦一个真实公司/产品，呈现"AI 如何重塑某个具体工作流"。目的是给读者启发——看到别人怎么落地 AI，并提炼出可迁移的机制设计点。

## 二、放置与命名

在 `note/11.ai/05-applications/` 下新建 `case-studies/` 子目录（与现有 `ai-written-prd/`、`shopify-ai-agent/` 平铺风格保持一致）。

**目录结构**：

```
note/11.ai/05-applications/
├── automotive/                          ← 现有
├── embodied-ai/                        ← 现有
├── ai-written-prd/                     ← 现有
├── shopify-ai-agent/                   ← 现有
├── README.md                           ← 现有，需追加索引
└── case-studies/                       ← 新建
    ├── README.md                       ← 12 篇总索引 + 行业版图
    ├── 01-anthropic-claude-code/README.md
    ├── 02-cursor-tab/README.md
    ├── 03-klarna-ai-customer-service/README.md
    ├── 04-harvey-ai-legal/README.md
    ├── 05-khan-academy-khanmigo/README.md
    ├── 06-duolingo-max/README.md
    ├── 07-jpmorgan-coin/README.md
    ├── 08-microsoft-365-copilot/README.md
    ├── 09-glean-enterprise-search/README.md
    ├── 10-salesforce-agentforce/README.md
    ├── 11-hippocratic-ai/README.md
    └── 12-siemens-industrial-copilot/README.md
```

**命名规则**：`NN-<公司或产品>-<关键词>/`，全小写、kebab-case、两位数字前缀。

## 三、写作体例（每篇统一）

**总长控制**：1.8k–2.5k 字 / 篇。

**结构模板**：

```markdown
# [标题：核心机制 + 公司/产品]

> #编程 #Anthropic #AI编程  ← 顶部 3-4 个领域标签

> **一句话总结**：[30-50 字概括"做了什么 + 为什么值得看"]

> 原文链接：[官方博客/视频/GitHub]
> 参考资料：[补充链接，可选]

---

## 一、背景：[行业/公司面临的核心问题]
[300-400 字，描述这个场景原来怎么运转、痛点是什么]

## 二、做法：[产品/机制是如何设计的]
[600-800 字，重点写"机制"而不是"功能"。突出 2-3 个关键设计决策]

## 三、机制亮点：为什么这样设计能 work
[400-500 字，深入 1-2 个最值得借鉴的机制设计点；可配 mermaid 图]

## 四、结果与代价：[业务数据 + 落地中的反向调整]
[300-400 字，给出可量化的结果（如果有），并诚实记录"踩过的坑"]

## 五、对我们的启发
[200-300 字，提炼 1-2 个"对所有 AI 落地项目都成立"的方法论启发；不绑定个人开源项目]

---

*本文基于 XXX 公开资料整理，感谢原作者。*
```

**风格约束**：
- 像 Uber/Shopify 现有案例一样"叙事化"，不是产品说明书
- 不写"AI 强大"这种空话，每段必须有一个具体的"机制点"
- 数据要标注来源（链接/截图）
- "对我们的启发"写普适方法论，不绑定个人项目

## 四、12 篇选题清单

| # | 目录 | 标题 | 核心机制点（写作时必须落地） |
|---|---|---|---|
| 01 | `01-anthropic-claude-code/` | **Anthropic 让 Claude Code 写 Claude Code：研究型公司如何让 50% 工程师每天跑 Agent** | "AI 写 AI"的飞轮 + 内部对 Agent 输出的 review 机制 |
| 02 | `02-cursor-tab/` | **Cursor Tab：把 IDE 从"补全代码"重定义为"预测你的下一次编辑"** | 编辑级预测 + 主动拒绝打扰的"克制设计" |
| 03 | `03-klarna-ai-customer-service/` | **Klarna AI 客服先激进、后回调：AI 替代 700 个工位后，又把人工请回来** | 经验教训：客服不是单轮问答，而是情绪劳动 |
| 04 | `04-harvey-ai-legal/` | **Harvey AI：当一家 AI 公司 30% 员工是律师，法律知识如何被产品化** | "懂行"才是壁垒——模型只是载体 |
| 05 | `05-khan-academy-khanmigo/` | **Khanmigo：故意不直接给答案的 AI 导师，苏格拉底式交互的产品哲学** | "教"vs"代写"——教育 AI 的根本分歧 |
| 06 | `06-duolingo-max/` | **Duolingo Max：把 GPT-4 变成"陪练角色"，让语言学习有真实的对话对象** | LLM 把"练习频次"这个最稀缺资源变得无限 |
| 07 | `07-jpmorgan-coin/` | **JPMorgan COiN：12 万小时法律文书 → 秒级，金融危机逼出来的白领流水线** | 早于 LLM 时代 5 年的"AI 流程化"先驱 |
| 08 | `08-microsoft-365-copilot/` | **Microsoft 365 Copilot：存量办公套件如何被 AI 改写为"协作者"** | "工具→协作者"——传统 SaaS 的 AI 升级路径 |
| 09 | `09-glean-enterprise-search/` | **Glean：把企业散落的 Slack/邮件/工单/Notion 装进同一个 RAG** | 企业知识真正的杀手场景——RAG 落地比想象中朴素 |
| 10 | `10-salesforce-agentforce/` | **Salesforce Agentforce：让销售 Agent 自己挖线索、约会议、跟进客户** | "RPA 流程自动化"→"Agent 自主决策"的范式跃迁 |
| 11 | `11-hippocratic-ai/` | **Hippocratic AI：不替代医生的护理 Agent，7×24 患者随访的边界设计** | "非替代"定位的边界：什么该 AI 做、什么绝不能让 AI 做 |
| 12 | `12-siemens-industrial-copilot/` | **Siemens Industrial Copilot：自然语言生成 PLC 代码，工业 know-how 才是门槛** | 工业 LLM 的真相：模型不是壁垒、领域知识才是 |

## 五、case-studies/README.md 总索引

包含三部分：
1. **行业版图**（mermaid 图或表格，呈现 12 篇的行业分布）
2. **12 篇速查表**（标题 + 一句话总结 + 核心机制 + 启发关键词）
3. **横向对比维度**：每篇标 3 个标签——`#机制设计` / `#行业` / `#产品阶段（验证/规模化/回调）`

## 六、现有 README 更新

`note/11.ai/05-applications/README.md` 需更新：
- 在"子目录"表格加一行 `[case-studies](case-studies/)` 链接
- 在"行业版图"里追加 12 篇对应的位置标记
- 末尾"相关章节"区不变

## 七、验收标准

- ✅ 12 个目录 + 12 个 README.md 全部存在
- ✅ 每篇遵循统一结构（一句话总结 → 5 节 → 资料链接）
- ✅ 每篇都有领域标签（顶部 3-4 个）
- ✅ 每篇第五节"对我们的启发"不绑定个人开源项目
- ✅ 关键数据有来源链接
- ✅ `case-studies/README.md` 含 12 篇索引 + 行业版图
- ✅ `05-applications/README.md` 已更新指向 case-studies
- ✅ 文字总量 1.8k–2.5k 字 / 篇
- ✅ 中文行文流畅，无明显 AI 写作痕迹
- ✅ 整体不与现有 `automotive/` `embodied-ai/` `ai-written-prd/` `shopify-ai-agent/` 重复

## 八、交付节奏

12 篇一次性交付，不分批。
