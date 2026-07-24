export const meta = {
  name: 'note-health-exhaustive',
  description: '全库穷举内容质量打分：按 leaf 文件批 fan-out，每 agent 5-8 篇',
  phases: [{ title: 'Score', detail: '每批 leaf 文件按 leaf-quality.md 打分' }],
}

// 主循环先把 leaf 文件清单通过 args 传入（避免脚本内跑 shell）
// args = { files: string[], batchSize?: number }
const files = (args && args.files) || []
const batchSize = (args && args.batchSize) || 6

if (files.length === 0) {
  log('⚠️ 未收到 leaf 文件清单，退出（请由 SKILL.md 先枚举后传入 args.files）')
  return { scored: [], error: 'empty_input' }
}

// 切批：~batchSize 篇/agent
const batches = []
for (let i = 0; i < files.length; i += batchSize) {
  batches.push(files.slice(i, i + batchSize))
}
log(`共 ${files.length} 篇 → ${batches.length} 批（每批 ~${batchSize} 篇）`)

const SCHEMA = {
  type: 'object',
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          moduleClass: { type: 'string' },
          total: { type: 'number' },
          maxScore: { type: 'number' },
          grade: { type: 'string' },
          findings: { type: 'array', items: { type: 'string' } },
        },
        required: ['file', 'moduleClass', 'total', 'grade'],
      },
    },
  },
  required: ['results'],
}

phase('Score')
const scored = await pipeline(
  batches,
  (batch, _orig, idx) => agent(
    `你是 note 内容质量评审。严格按 skills/note-health/references/leaf-quality.md 的规则给下列文件逐篇打分。\n\n` +
    `**强制要求**：\n` +
    `1. **必须先 Read 每个文件的完整内容**，禁止凭印象或猜测文件内容\n` +
    `2. 若某文件是新沉淀/新写的（如路径含近期新增、或内容是初稿），先参考 skills/note-health/references/new-file-baseline.md 的 10 段结构基线，再按 leaf-quality.md 打分\n` +
    `3. 先按路径判断模块类型(A~G)，再用「通用 6 维度 + 该模块专属维度」评分\n` +
    `4. findings 每项需包含：section（修改位置）、action（具体操作）、effort（S/M/L 工作量）\n` +
    `5. 输出每篇的 total/maxScore/grade + findings\n\n` +
    `文件清单(批 ${idx + 1}):\n${batch.map(f => '- ' + f).join('\\n')}`,
    { label: `score:batch-${idx + 1}`, phase: 'Score', schema: SCHEMA }
  ).then(r => {
    if (!r || !r.results || r.results.length === 0) {
      log(`⚠️ batch-${idx + 1} 返回空结果，跳过`)
      return []
    }
    return r.results
  })
)

const flat = scored.filter(Boolean).flat()
if (flat.length === 0) {
  log('⚠️ 所有批次均返回空结果，触发 SKILL.md 降级流程（手工 dispatch）')
  return { scored: [], error: 'all_batches_empty' }
}
log(`打分完成：${flat.length} 篇`)
return { scored: flat }