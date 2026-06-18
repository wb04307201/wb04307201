# 05 架构

> 一句话定位：**前端架构——把"应用"拆成"模块",把"模块"拆成"组件",并组织它们之间的协作**

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| 渲染模式 | ✓ 已有 | [rendering-modes/](rendering-modes/) — CSR / SSR / SSG / ISR / RSC / Islands 全景 |
| 状态管理 | ✓ 已有 | [state-management/](state-management/) — Redux / Zustand / Jotai / Pinia / Nano Stores |
| 路由 | ✓ 已有 | [routing/](routing/) — React Router / Vue Router / TanStack Router |
| 微前端 | ✓ 已有 | [micro-frontend/](micro-frontend/) — 微前端综述与选型 |
| Web Components | ✓ 已有 | [web-components/](web-components/) — 浏览器原生组件化标准 |
| BFF | ✓ 已有 | [bff/](bff/) — Backend For Frontend 模式 |
| 设计系统 | ✓ 已有 | [design-system/](design-system/) — 组件库 / Token / 主题 / Storybook |

## 与其他模块的关系

- 上游：[03-frameworks](../03-frameworks/) / [04-engineering](../04-engineering/)
- 下游：被 [06-performance](../06-performance/) / [07-security](../07-security/) / [08-cross-platform](../08-cross-platform/) 复用

## 学习建议

- 架构选型与「项目规模」强相关：单体应用不需要微前端，营销页不需要 SSR
- 推荐先理解「为什么需要」再决定「用哪个」
