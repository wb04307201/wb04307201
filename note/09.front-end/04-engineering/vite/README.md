<!--
module:
  parent: front-end
  slug: front-end/vite
  type: article
  category: 主模块子文章
  summary: Vite 构建工具
-->

# Vite 构建工具

> 一句话定位：**Vite —— 2026 年前端构建的事实标准，ESM 原生的极速体验**

Vite（法语"快"）由 Vue.js 作者尤雨溪于 2020 年发布，到 2026 年已经占据 **78%+** 新项目构建工具市场份额，满意度比 Webpack 高 78 分。

---
---

## 1. 为什么 Vite 能替代 Webpack

### Webpack 的痛点
- ❌ 启动慢：打包整个应用后才能启动 dev server（大项目 30s+）
- ❌ HMR 慢：修改一个文件，重新打包整条链路
- ❌ 配置复杂：plugin / loader 学习曲线陡

### Vite 的核心突破

```mermaid
graph LR
  A[浏览器原生 ESM] --> B[Dev Server<br/>无需打包]
  B --> C[按需编译<br/>只编译访问到的模块]
  C --> D[极速启动<br/>毫秒级]
  D --> E[HMR<br/>仅更新变更模块]
  style A fill:#e3f2fd
  style D fill:#e8f5e9
```

| 阶段 | Webpack | Vite |
|------|---------|------|
| **Dev 启动** | 打包全部模块（30s+） | **毫秒级**（无打包） |
| **Dev HMR** | 重编译相关模块（1-3s） | **毫秒级**（ESM 热更） |
| **Prod 构建** | 自身打包 | **Rollup**（更优产物） |

---

## 2. Vite 核心架构

### Dev 阶段：esbuild 预构建 + 原生 ESM

1. **依赖预构建**（esbuild）：`node_modules` 转成浏览器 ESM
2. **源码按需编译**：浏览器请求 `import './App.tsx'` 时，Vite 实时编译
3. **HMR**：通过 WebSocket 推送变更，浏览器局部热更

### Prod 阶段：Rollup 打包

- ✅ 树摇（Tree Shaking）
- ✅ 代码分割（动态 `import()`）
- ✅ 资源内联（小图片 base64）
- ✅ CSS 提取

---

## 3. 基础配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
  
  build: {
    target: 'es2022',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
})
```

---

## 4. 插件生态

| 插件 | 作用 | 适用 |
|------|------|------|
| **@vitejs/plugin-react** | React Fast Refresh | React 项目 |
| **@vitejs/plugin-vue** | Vue SFC 支持 | Vue 项目 |
| **vite-plugin-pwa** | PWA 支持 | PWA 应用 |
| **vite-plugin-inspect** | 查看插件链中间产物 | 调试 |
| **vite-plugin-compression** | Brotli / Gzip 压缩 | 性能优化 |
| **vite-plugin-svgr** | SVG 作为 React 组件 | UI 组件 |
| **unplugin-auto-import** | 自动导入 API | 开发体验 |

---

## 5. Vite vs 其他构建工具

| 工具 | 启动速度 | 生产构建 | 适用 |
|------|---------|---------|------|
| **Vite 5+** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐（Rollup） | **新项目首选** |
| **Webpack 5** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 存量项目 |
| **Rspack** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Webpack 兼容 + 极速 |
| **Turbopack** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 仅 Next.js |
| **esbuild** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 库构建 / Vite 底层 |
| **Rollup** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐（库首选） | 库 / 组件库 |

---

## 6. 性能优化

### Dev 优化
```typescript
// 优化依赖预构建
export default defineConfig({
  optimizeDeps: {
    include: ['large-dep'],  // 强制预构建
    exclude: ['dep-to-skip'],
  },
})
```

### Prod 优化
```typescript
export default defineConfig({
  build: {
    // 资源内联阈值（默认 4KB）
    assetsInlineLimit: 8192,
    // 代码分割策略
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        },
      },
    },
    // 压缩（默认 esbuild，可选 terser）
    minify: 'esbuild',
    // CSS 代码分割
    cssCodeSplit: true,
  },
})
```

---

## 7. 环境变量

```bash
# .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App

# 仅 VITE_ 前缀暴露给客户端
```

```typescript
// 使用
const apiUrl = import.meta.env.VITE_API_URL
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
const mode = import.meta.env.MODE
```

```typescript
// 类型声明（env.d.ts）
/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

---

## 8. 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| **HMR 不生效** | 模块没导出 / 命名导入问题 | 检查导出 / 使用 named export |
| **依赖报错** | CJS 模块未预构建 | `optimizeDeps.include` |
| **生产环境路由 404** | 服务端未配置 SPA fallback | Nginx `try_files $uri /index.html` |
| **路径别名不生效** | `resolve.alias` + TS `paths` 需同步 | 两边都配置 |

---

## 9. 学习路径

1. **入门**（1 天）：`npm create vite@latest` 跑通基础项目
2. **进阶**（1 周）：插件配置、环境变量、路径别名
3. **高级**（持续）：自定义插件、构建优化、Monorepo 集成

## 10. 交叉引用

- [`04-engineering/`](../) — 工程化总览
- [`04-engineering/monorepo-practice/`](../monorepo-practice/) — Vite 在 Monorepo 的应用
- [`06-performance/`](../../06-performance/) — 构建与性能
