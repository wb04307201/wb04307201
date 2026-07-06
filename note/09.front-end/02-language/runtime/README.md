<!--
module:
  parent: front-end
  slug: front-end/runtime
  type: article
  category: 主模块子文章
  summary: JS 运行时：Node.js / Deno / Bun
-->

# JS 运行时：Node.js / Deno / Bun

> 一句话定位：**三大 JS 运行时 —— 同一个语言，不同的生态与取舍**

JavaScript 不再只是"浏览器的语言"。2026 年，Node.js / Deno / Bun 三大运行时让 JS 成为服务端、CLI、工具链、Edge 函数的通用语言。

---
---

## 1. 三大运行时概览

| 维度 | Node.js | Deno | Bun |
|------|---------|------|-----|
| **首发** | 2009 | 2018（1.0 在 2021） | 2022 |
| **核心语言** | C++ + V8 | Rust + V8 | Zig + JavaScriptCore |
| **TypeScript** | 需 ts-node / tsx | **原生支持** | **原生支持** |
| **包管理** | npm / pnpm / yarn | 内置（npm 兼容） | 内置（npm 兼容） |
| **性能（HTTP）** | 中 | 中 | **快 2-3 倍** |
| **生态** | 200 万+ 包 | 成长中 | 快速追赶 |
| **适用** | 通用服务端 | Edge / 安全优先 | 高性能 I/O / 工具链 |

---

## 2. Node.js：行业事实标准

### 优势
- ✅ 生态最完整（200万+ npm 包）
- ✅ 文档最全、社区最大
- ✅ 企业生产环境久经考验
- ✅ 所有云平台（Vercel / AWS / GCP）原生支持
- ✅ Node.js 22+ 原生支持 ES Modules（终于摆脱 `.mjs` 困惑）

### 劣势
- ❌ 包管理历史包袱（node_modules 黑洞）
- ❌ TypeScript 需要额外工具链（tsx / ts-node）
- ❌ 启动速度慢（不适合 CLI / serverless）
- ❌ 单线程 CPU 密集场景弱

### 适用场景
- ✅ 企业级后端服务
- ✅ 传统 Web 应用
- ✅ 与现有 npm 生态强绑定

---

## 3. Deno：Ryan Dahl 的"修正版"

### 优势
- ✅ **原生 TypeScript**：无需 `ts-node`，直接 `deno run app.ts`
- ✅ **安全沙箱**：默认无权限，需显式 `--allow-read` / `--allow-net`
- ✅ **标准库完善**：URL 引入，无需 `npm install`
- ✅ **Node 兼容层**：`npm:` 前缀支持 npm 包
- ✅ **Edge 友好**：与 Deno Deploy / Cloudflare Workers 深度集成

### 劣势
- ❌ 生态不如 Node 完整（部分 npm 包不兼容）
- ❌ 社区规模较小
- ❌ 企业采用率低
- ❌ 历史 API 不稳定（虽 1.0 后改善）

### 适用场景
- ✅ Edge Functions（Deno Deploy）
- ✅ 安全敏感的脚本（CI 工具、构建脚本）
- ✅ 云函数（Cloudflare Workers 兼容）

---

## 4. Bun：极速新贵

### 优势
- ✅ **启动快 4 倍**：JavaScriptCore + Zig 优化
- ✅ **安装快 25 倍**：全局缓存 + 硬链接
- ✅ **内置一切**：包管理、测试运行器、打包器、TS 支持
- ✅ **Node 100% 兼容**：几乎所有 npm 包可用
- ✅ **内置 SQLite**：`bun:sqlite` 零配置

### 劣势
- ❌ 历史最短（2022 年发布），生态还在成长
- ❌ 部分边缘 Node API 不完全兼容
- ❌ 企业生产案例还在积累

### 适用场景
- ✅ 高性能 HTTP 服务（吞吐量需求）
- ✅ CLI 工具 / 脚本（启动速度敏感）
- ✅ 开发环境（pnpm install → bun install）
- ✅ 测试运行器（`bun test` 比 Vitest 快）

---

## 5. 性能对比

### HTTP 吞吐量

| 运行时 | 请求/秒 | 相对 Node |
|--------|---------|----------|
| Node.js 22 | 50,000 | 1x |
| Deno 2.x | 60,000 | 1.2x |
| Bun 1.x | **140,000** | **2.8x** |

### 启动时间

| 运行时 | 启动时间 |
|--------|---------|
| Node.js | ~80ms |
| Deno | ~60ms |
| Bun | **~20ms** |

### 包安装速度（100 个包）

| 包管理 | 冷启动 | 缓存命中 |
|--------|--------|---------|
| npm | 15s | 3s |
| pnpm | 4s | 1s |
| Bun | **0.6s** | **0.2s** |

---

## 6. Edge Runtime：运行时的第四形态

**Edge Runtime** = 轻量级 V8 环境，运行在 CDN 边缘节点。

| 平台 | 运行时 | 限制 |
|------|--------|------|
| **Vercel Edge** | 基于 V8 isolates | 无 Node API，冷启动 0 |
| **Cloudflare Workers** | V8 isolates | 1MB 内存，无文件系统 |
| **Deno Deploy** | Deno | 完整 Deno API |
| **Netlify Edge** | Deno | 同上 |

**适用场景**：
- ✅ A/B 测试中间件
- ✅ 地理位置路由
- ✅ 请求转换 / 鉴权
- ✅ 边缘缓存逻辑

**不适用场景**：
- ❌ 需要 Node API（fs / path / child_process）
- ❌ 长时间计算（内存 / 时间受限）
- ❌ 需要持久连接（数据库连接池）

---

## 7. Web Platform APIs：运行时的未来

2026 年，三大运行时都在**向 Web 标准靠拢**：

| API | Node | Deno | Bun |
|-----|------|------|-----|
| `fetch` | ✅ | ✅ | ✅ |
| `Request` / `Response` | ✅ | ✅ | ✅ |
| `URL` / `URLSearchParams` | ✅ | ✅ | ✅ |
| `Web Crypto` | ✅ | ✅ | ✅ |
| `ReadableStream` | ✅ | ✅ | ✅ |
| `setTimeout` / `setInterval` | ✅ | ✅ | ✅ |
| `structuredClone` | ✅ | ✅ | ✅ |

**趋势**：写一次 Web 标准代码，跑在浏览器 + Node + Deno + Bun + Edge。

---

## 8. 选型决策

| 场景 | 推荐运行时 | 理由 |
|------|----------|------|
| **企业生产** | Node.js LTS | 生态 + 稳定性 |
| **新项目 CLI / 脚本** | Bun | 启动速度 |
| **Edge Functions** | Deno Deploy / Cloudflare Workers | 边缘计算 |
| **高性能 HTTP 服务** | Bun | 吞吐量 |
| **CI 脚本** | Deno | 安全沙箱 |
| **学习 / 实验** | Bun | 一体化，开箱即用 |

---

## 9. 跨运行时开发建议

1. **优先使用 Web Platform APIs**（fetch / URL / Crypto 等）
2. **避免 Node 特有 API**（`fs` / `path` / `child_process`），用 `node:fs/promises` 显式导入
3. **用 `import.meta`** 替代 `__dirname` / `__filename`
4. **测试跨运行时**：GitHub Actions matrix 跑 Node / Deno / Bun
5. **TypeScript 优先**：TS 在三大运行时都是一等公民

---

## 10. 学习路径

1. **入门**（3 天）：Node.js 基础（fs / http / npm）
2. **进阶**（1 周）：Bun / Deno 上手；Web APIs 在运行时的应用
3. **高级**（持续）：Edge Runtime；跨运行时库开发；性能调优

## 11. 交叉引用

- [`02-language/`](../) — 语言基础
- [`05-architecture/bff/`](../../05-architecture/bff/) — BFF 通常跑在 Node / Bun
- [`09-frontend-and-ai/ai-sdk/`](../../09-frontend-and-ai/ai-sdk/) — AI SDK 在各运行时的支持
- 🆕 [async-await-error-handling/](async-await-error-handling/README.md) —— async/await 错误处理 4 方式 + React/Vue 实战 + 5 大反模式 1258 行深度

---

← [返回 语言与运行时](../README.md)
