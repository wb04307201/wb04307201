# note-health Batch 1–5 修复设计

**日期**：2026-07-20  
**状态**：已批准  
**实施分支**：`fix/note-health-remediation`  
**源报告**：`note/.health-tmp/report-2026-07-19.md`

## 1. 背景

2026-07-19 的 note-health 全库体检覆盖 1042 个 Markdown、765 个 README 和 634 个深层 leaf README，并对 71 篇高风险/代表文档进行了质量评分。

体检确认元数据和目录骨架总体健康：765 个 README 全部具备 frontmatter，14 个主模块入口完整，没有有效目录缺 README，也没有孤儿 PNG。但导航、统计和少量正文事实存在集中风险：

- 225 个 README 的返回 footer 指向当前文件自身；
- 16 条本地目标不存在的内部链接；
- 12 篇 Markdown 没有任何入链；
- split-hairs 与 CONTRIBUTING 的多处统计数字漂移；
- 少数事实、代码和安全示例可直接误导读者；
- 1824 处代码围栏没有语言标识，涉及约 500 个文件；
- 71 篇评分对象中存在来源、版本演进、反例/正例和定位不足。

用户批准修复 Batch 1–5，并选择在独立分支中按模块/主题自动分批 commit，不 push。

## 2. 目标

完成报告中 Batch 1–5 的有限范围修复，并使每个批次可验证、可审阅、可回退。

最终必须满足：

1. 225 个 README 自链归零；
2. 内部断链归零；
3. 零入链 Markdown 归零；
4. 634 个深层 leaf 全部具备有效直接父级返回；
5. split-hairs、根目录和 CONTRIBUTING 的统计数字一致；
6. 已复核 P0 事实/示例问题全部修复；
7. 裸代码围栏归零；
8. 报告中 71 篇评分对象的已列 P2/P3 在本设计边界内完成；
9. 所有验证通过，最终工作树 clean；
10. 所有 commit 只存在于修复分支，不 push。

## 3. 非目标

- 不新增 report 未列出的知识专题；
- 不把 71 篇样本的可选建议扩张为 1042 篇全库重写；
- 不因行数短而扩写合法的 `index-only` 页面；
- 不强制给三级非 README `.md` 添加 frontmatter；
- 不修改 `.gitignore`、`.obsidian`、`.idea`、`.vscode`；
- 不删除 tracked 文件；
- 不修改外部项目源码；
- 不 push、不创建 PR。

## 4. 设计原则

### 4.1 风险优先

先修可机械验证的导航，再修统计、事实、格式，最后做质量增强。后续批次不得建立在损坏的导航或错误统计上。

### 4.2 小批可回退

每个 commit 只覆盖一个模块或一个事实主题。一般不超过 30 个文件；超过时继续按子主题拆分。

### 4.3 脚本只读

遵守仓库“正文修改不使用批量改写脚本”的维护原则：

- Python/Bash 只用于枚举、统计和验证；
- tracked Markdown 的实际修改使用逐文件 Edit 或受控 subagent；
- 不运行会批量重写正文的脚本。

### 4.4 证据优先

- 相对路径通过源文件和父 README 实际位置计算，不凭目录名称猜测；
- 外部事实优先引用官方文档、标准、项目公告或原始论文；
- 无法核实的精确数字删除或明确标为“示例假设”，不替换成另一个无来源数字。

### 4.5 评分与执行分离

评分器原始 P0 仅用于发现候选。执行优先级采用体检报告中经过复核的 P0–P3；例如 index-only 行数短、三级 `.md` 无 frontmatter、Java 10 缺额外版本对比均不作为 P0。

## 5. 分支与提交策略

### 5.1 分支

所有修改在 `fix/note-health-remediation` 上完成。

### 5.2 commit 规则

- 导航：`fix(<module>): 修复返回自链与父索引接线`
- 统计：`fix(indexes): 校准 split-hairs 与 README 统计`
- 事实：`fix(<module>): 修正 <主题> 事实与示例`
- 格式：`style(<module>): 补齐代码围栏语言标识`
- 内容：`docs(<module>): 完善 <主题> 引用与选型说明`

每个 commit message 末尾包含：

```text
Co-Authored-By: Claude <noreply@anthropic.com>
```

### 5.3 提交前置条件

任何 commit 前必须满足：

- 该子批次的目标检查通过；
- `git diff --check` 无输出；
- diff 只包含当前子批次范围；
- 没有配置文件、IDE 文件或删除操作混入。

## 6. Batch 1：导航恢复

### 6.1 范围

1. 225 个 README footer 自链；
2. 16 条内部断链；
3. 12 篇零入链文档；
4. 634 个深层 leaf 中未直达父索引的其余错误返回；
5. 父 README 未反链 child 的候选，只修真正应该由直接父级收录的项目。

### 6.2 拆分

按模块顺序处理：

1. `01.java`
2. `02.computer-basics`
3. `03.database`
4. `04.system-design`
5. `05.tools`
6. `06.spring`
7. `07.workflow`
8. `08.application-systems`
9. `09.front-end`
10. `10.big-data`
11. `11.ai`
12. `12.story`
13. `13.split-hairs`
14. `14.project-management`
15. 根 `note/README.md`

自链较多的 `13.split-hairs`、`04.system-design` 和 `11.ai` 必须继续按子目录拆分，避免单 commit 超过 30 个文件。

### 6.3 修改规则

- 当前文件是 `README.md` 时，`(README.md)` 指向自身；应改为实际父级路径，通常为 `../README.md`；
- 当前文件是普通 `.md` 时，`(README.md)` 可能正确指向同目录索引，不得机械替换；
- 父 README 必须增加 child 的真实导航项，不能只在统计或纯文本中提及；
- 已迁走条目应指向新位置，已删除且无替代的入口应删除；
- 重命名遗留应使用现存真实 slug。

### 6.4 完成标准

```text
selfReturnFiles = 0
brokenLinks = 0
orphanMarkdown = 0
leafReturnCoverage = 634/634
```

## 7. Batch 2：统计一致性

### 7.1 范围

- `note/README.md`
- `note/13.split-hairs/README.md`
- `note/13.split-hairs/01.java/README.md`
- `note/13.split-hairs/11.ai/README.md`
- 其他声明分类篇数的 split-hairs 子索引
- `note/CONTRIBUTING.md`

### 7.2 统计口径

split-hairs 文章数按分类目录递归统计 README，并排除分类根 README。当前校对基线：

| 分类 | 篇数 |
|---|---:|
| 01.java | 39 |
| 02.computer-basics | 6 |
| 03.database | 26 |
| 04.system-design | 19 |
| 05.security | 10 |
| 06.spring | 16 |
| 09.front-end | 26 |
| 10.big-data | 6 |
| 11.ai | 40 |
| tools | 4 |
| 合计 | 192 |

README 总数当前基线为 765，Markdown 总数为 1042。实施时必须重新枚举；如果基线因前序合法改动变化，以实时结果为准。

### 7.3 完成标准

- 所有分类之和等于总计；
- 根 README、模块 README、frontmatter summary 和正文清单数字一致；
- CONTRIBUTING 的统计和日期与实时结果一致；
- 不在多个位置写互相独立、无法验证的总数。

## 8. Batch 3：事实和可执行示例

### 8.1 Spring

- 修正 `propagation-and-isolation.md` 中 MySQL InnoDB 默认隔离级别的自相矛盾；
- 为 REQUIRES_NEW 的挂起/连接行为增加 TransactionManager 限定；
- 将 `cross-field.md` 的 `@ScriptAssert` 对象别名从 `_` 改为 `_this`；
- 说明现代 JDK 使用脚本校验时需要显式 JSR-223 引擎，并给出更推荐的类级自定义校验器方案。

### 8.2 Workflow

- 清理 EventMesh/12306 无来源的精确 QPS、收益和错误时间线；
- Serverless Workflow 版本字段区分工作流版本和规范版本；
- cloud-flow 命令补前置条件、版本和真实端点依据；
- Temporal/Cadence 示例补必要 import、Activity/Worker/Client 链路或降为明确伪代码。

### 8.3 Application Systems

- PDM 的“公开案例引用”补 URL、报告名和年份；无法找到时移除“公开引用”措辞并将数字改为示例假设；
- CMS 性能倍数和 QPS 推导补 benchmark，或改成无绝对倍数的定性描述；
- SCRM 的 3–10x 等数字补口径和来源，或删除硬数字。

### 8.4 Front-end

- React 排序示例使用 `toSorted()` 或复制数组后排序；
- 将 Effect 示例从“无限循环”改为“冗余派生状态”；
- 限定 `suppressHydrationWarning` 的适用范围；
- BFF 将“根源杜绝 XSS”改为“降低 Token 被直接读取的风险”，并补 CSP、SameSite、CSRF、mTLS、scope 等边界；
- 删除或来源化 state-management 中的无口径百分比与“2026 共识”。

### 8.5 Big Data

- 区分查询引擎、表格式和文件格式；
- 删除 Iceberg/Hudi 与 CNCF 的错误混写；
- Doris Kafka 示例改成真实 Routine Load 或 Stream Load；
- 区分 DStream 与 Structured Streaming；
- 删除“每分钟 N QPS”等单位错误和无 workload 的绝对排名。

## 9. Batch 4：结构与格式

### 9.1 裸代码围栏

对 1824 处 opening fence：

- ASCII 图、命令输出、决策树：`text`
- Shell：`bash`
- 配置：按真实格式使用 `yaml`、`json`、`xml`、`properties`
- 代码：使用实际语言
- Mermaid 图：`mermaid`

语言无法从上下文确定时使用 `text`，不猜测。

### 9.2 其他结构修复

- 5 个主模块 H1 按现行规范去数字编号；
- 4 个超长主模块定位句压缩至 80 字内；
- 保留 clustering、dimensionality-reduction、optimization 的合法 index 角色，将其接入算法父 README；
- 修正 K-Medoids、t-SNE、Newton 等同目标“伪子文档链接”；
- 清理 WCAG frontmatter summary 污染，但不移动目录；
- 对 35 个“引言：架构困境”候选逐篇判断，仅改泛化模板，不机械删除有效引言；
- 14 个 TODO/待补候选先排除状态机示例，再把真实 backlog 移到 Roadmap 或补全。

## 10. Batch 5：质量增强

### 10.1 边界

仅处理 `score-selection-2026-07-19.json` 对应的 71 篇评分对象及其报告 findings，不新开全库扩写任务。

`.health-tmp` 是本地忽略目录，因此详细实施计划必须把这 71 个路径复制为显式任务清单，不能只留下对临时 JSON 的引用。每条 finding 必须以 `fixed`、`no_change_needed` 或带理由的 `skipped` 关闭；不能用“整体已润色”代替逐项结论。

### 10.2 修复类型

- 13 篇已明确缺来源的样本文档：补官方/原始来源或降级表述；
- A 类文档：仅在版本变化会影响选型或行为时补版本演进；
- 缺反例/正例的文档：补会导致真实错误的最小对照；
- 定位不足文档：H1 后增加不超过 80 字的一句话定位；
- 表格有比较无结论时：增加推荐场景/约束，不只给星级；
- index-only 页面不为追求分数扩写正文。

## 11. 执行架构

### 11.1 主循环职责

- 维护分支和任务清单；
- 提供每个子批次的精确文件清单；
- 审阅 subagent 返回的 diff 与 commit；
- 运行批次/全库验证；
- 发现跨模块冲突时调整后续批次。

### 11.2 subagent 职责

- 每个 subagent 只处理一个模块或一个事实主题；
- 先读父 README 和规范，再逐文件修改；
- 不运行批量写脚本；
- 返回修改清单、验证结果和 commit hash；
- 不 push。

### 11.3 集成

独立模块可在隔离 worktree 并行实施，由主循环按依赖顺序 cherry-pick。共享根索引和统计文件只由单一任务修改，避免冲突。

## 12. 验证设计

### 12.1 每个子批次

- 模块级自链扫描；
- 模块级本地链接存在性；
- 修改文件 frontmatter/返回链抽查；
- `git diff --check`；
- `git status --short` 确认无范围外文件。

### 12.2 每个 Batch

- 全库结构扫描；
- 实时 README/Markdown/分类计数；
- 报告目标指标比较；
- 检查新增 broken link、零入链、裸围栏；
- 记录 batch 完成后的 commit 范围。

### 12.3 最终

- 重新评分既定 71 篇对象；
- 生成修复前后对照报告；
- 运行 `git diff --check`；
- 确认所有预期 commit 位于修复分支；
- 确认工作树 clean；
- 确认没有 push。

## 13. 错误处理与停止条件

以下任一出现时停止当前子批次，不 commit：

- 新增 broken link；
- 返回链解析后仍指向当前文件；
- 分类之和与总数不一致；
- 外部数字找不到官方/原始来源却仍作为事实保留；
- 修改超过当前任务范围；
- `git diff --check` 失败；
- 出现配置文件变更或 tracked 文件删除；
- 测试/扫描脚本报错。

停止后先修复当前批次；不能通过时保持未提交并在最终报告中说明阻塞，不得把部分失败批次标为完成。

## 14. 验收清单

- [ ] Batch 1 导航指标全部归零/达标
- [ ] Batch 2 数字全部实时一致
- [ ] Batch 3 已复核 P0 事实/示例全部修复
- [ ] Batch 4 裸围栏归零，结构候选逐项关闭
- [ ] Batch 5 71 篇范围内 P2/P3 完成
- [ ] 每个 commit 边界清晰且验证通过
- [ ] 最终对照报告生成
- [ ] 工作树 clean
- [ ] 无 push
