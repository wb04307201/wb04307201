# 04 工程化

> 一句话定位：**让前端从"能跑"走向"可维护、可发布、可规模化"**

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| 构建工具 | ⏳ 待补 | Vite / Webpack / Turbopack / Rspack / esbuild / Rollup |
| 包管理 | ⏳ 待补 | pnpm / npm / yarn / Bun 选型 |
| Monorepo | ⏳ 待补 | pnpm workspaces / Nx / Turborepo（与 [`05.tools/monorepo`](../../../05.tools/monorepo/) 互补） |
| 测试体系 | ⏳ 待补 | 单元 / 组件 / E2E（Vitest / Jest / Playwright） |
| Lint / 格式化 | ⏳ 待补 | ESLint / Prettier / Biome |

## 与其他模块的关系

- 上游：[02-language](../02-language/) / [03-frameworks](../03-frameworks/)
- 下游：被 [05-architecture](../05-architecture/) / [06-performance](../06-performance/) 依赖

## 学习建议

- 工程化是「实践学科」，建议先在小项目里跑通 Vite + pnpm + Vitest + ESLint 这一最小闭环
- 大型 Monorepo 的复杂度会反推构建与测试选型，按需深入
