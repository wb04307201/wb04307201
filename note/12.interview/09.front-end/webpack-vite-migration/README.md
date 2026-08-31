<!--
question:
  id: 09.front-end-webpack-vite-migration
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 工程迁移
  tags: [09.front-end, webpack, vite, rspack, migration, ESM, CJS]
-->

# Webpack → Vite/Rspack 迁移的 5 大坑

> **一句话定位**：Webpack → Vite 迁移 5 大坑：构建模型差异（ESM vs CJS）导致 CJS/Tree-Shaking/环境变量/HMR 翻车。

## 引子：一个真实的迁移事故

```text
项目：中型电商后台（~500 个模块）
迁移目标：Webpack 5 → Vite 5
预计时间：1 周
实际时间：3 周

事故：
- Day 1：`npm run dev` 启动成功，以为搞定了
- Day 2：生产构建失败，Tree-Shaking 把业务代码删了
- Day 3：CJS 依赖报错，`moment.js` 加载失败
- Day 5：环境变量丢失，`process.env.NODE_ENV` 是 undefined
- Day 10：终于上线，但 HMR 在某些场景失效
```

## 一、核心原理：Webpack vs Vite 的本质差异

### 1.1 构建模型差异

| 维度 | Webpack | Vite |
|------|---------|------|
| **Dev 启动** | 打包全部模块（30s+） | 毫秒级（无打包，原生 ESM） |
| **HMR** | 重编译相关模块（1-3s） | <50ms（ESM 热更） |
| **Prod 构建** | 自身打包（Rollup 可选） | Rollup（更优产物） |
| **模块系统** | 支持 CJS + ESM，自动转换 | **原生 ESM**，CJS 需预构建 |
| **Tree-Shaking** | 基于静态分析（依赖标记 `sideEffects`） | 基于 Rollup（更严格，依赖 ES Module 规范） |

### 1.2 关键差异点

```text
Webpack：
  - 把所有模块打包成 CommonJS 格式
  - 自动处理 CJS ↔ ESM 转换
  - Tree-Shaking 相对宽松（基于 `sideEffects: false`）

Vite：
  - Dev 阶段用浏览器原生 ESM（不打包）
  - Prod 阶段用 Rollup（严格 ES Module）
  - CJS 模块需要 esbuild 预构建
  - Tree-Shaking 更严格（不符合 ESM 规范的代码可能被删）
```

## 二、5 大迁移坑 + 解决方案

### 坑 1：CJS 依赖加载失败

**现象**：
```text
[plugin:vite:import-analysis] Failed to resolve import "moment" from "src/utils/date.js".
Does the file exist?
```

**原因**：Vite Dev 阶段用原生 ESM，但 `moment.js` 是 CJS 模块，浏览器无法直接加载。

**解决方案**：
```javascript
// vite.config.js
export default defineConfig({
  optimizeDeps: {
    include: ['moment', 'lodash']  // 强制预构建 CJS 依赖
  }
});
```

**原理**：Vite 用 esbuild 将 CJS 转换为 ESM，放入 `node_modules/.vite/deps/`。

### 坑 2：Tree-Shaking 误删业务代码

**现象**：
```javascript
// src/utils/helper.js
export function usedFunction() { /* ... */ }

function unusedFunction() { /* ... */ }
unusedFunction();  // 内部调用，但未被外部引用

// 生产构建后：usedFunction 也被删了！
```

**原因**：Rollup 的 Tree-Shaking 比 Webpack 更严格，如果代码不符合 ES Module 规范（如副作用代码、动态导入），可能被误删。

**解决方案**：
```javascript
// 方案 A：标记 sideEffects
// package.json
{
  "sideEffects": ["./src/utils/helper.js"]  // 告诉 Rollup 不要删这个文件
}

// 方案 B：用 /* @__PURE__ */ 注释
// src/utils/helper.js
export function usedFunction() { /* ... */ }

/* @__PURE__ */ function unusedFunction() { /* ... */ }
unusedFunction();  // Rollup 知道这是纯函数，可以安全删除
```

### 坑 3：环境变量丢失

**现象**：
```javascript
console.log(process.env.NODE_ENV);  // undefined
console.log(process.env.API_KEY);   // undefined
```

**原因**：Vite 不用 `process.env`，而是用 `import.meta.env`。

**解决方案**：
```javascript
// ❌ Webpack 写法
const env = process.env.NODE_ENV;
const apiKey = process.env.API_KEY;

// ✅ Vite 写法
const env = import.meta.env.MODE;  // 'development' | 'production'
const apiKey = import.meta.env.VITE_API_KEY;  // 自定义变量必须以 VITE_ 开头
```

**环境变量配置**：
```bash
# .env
VITE_API_KEY=xxx
VITE_API_BASE_URL=https://api.example.com
```

### 坑 4：CommonJS 动态导入失败

**现象**：
```javascript
// 动态导入 CJS 模块
const moment = require('moment');  // ❌ Vite 不支持 require
```

**原因**：Vite Dev 阶段用原生 ESM，浏览器不支持 `require()`。

**解决方案**：
```javascript
// ✅ 用 ES Module 语法
import moment from 'moment';

// 或动态导入
const moment = await import('moment');
```

### 坑 5：HMR 在某些场景失效

**现象**：
- 修改 Vue/React 组件后，页面不自动更新
- 需要手动刷新

**原因**：
1. 组件没有正确导出（匿名导出）
2. 模块有副作用（如全局变量修改）
3. 插件配置问题

**解决方案**：
```javascript
// ✅ 确保组件有明确的命名导出
export default defineComponent({
  name: 'MyComponent',  // 必须有 name
  // ...
});

// ✅ 检查 vite.config.js 插件配置
import react from '@vitejs/plugin-react';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [react(), vue()]  // 确保插件正确加载
});
```

## 三、迁移检查清单

| 检查项 | 通过？ |
|--------|-------|
| CJS 依赖已加入 `optimizeDeps.include`？ | ☐ |
| `sideEffects` 已正确配置？ | ☐ |
| 环境变量已迁移到 `import.meta.env`？ | ☐ |
| `require()` 已替换为 `import`？ | ☐ |
| 组件有明确的命名导出？ | ☐ |
| 插件配置正确（React/Vue）？ | ☐ |
| 生产构建已验证 Tree-Shaking？ | ☐ |

## 四、面试话术（30 秒版）

> "Webpack 迁移 Vite 主要有 5 个坑：**CJS 依赖加载失败**——Vite Dev 阶段用原生 ESM，CJS 模块需要 esbuild 预构建（`optimizeDeps.include`）；**Tree-Shaking 误删代码**——Rollup 比 Webpack 更严格，需要正确标记 `sideEffects`；**环境变量丢失**——Vite 用 `import.meta.env` 替代 `process.env`，自定义变量必须以 `VITE_` 开头；**CommonJS 动态导入失败**——`require()` 要替换为 `import`；**HMR 失效**——组件必须有命名导出，插件配置要正确。
>
> 核心差异是构建模型：Webpack 把所有模块打包成 CJS，Vite Dev 阶段用原生 ESM（不打包），Prod 阶段用 Rollup。迁移关键是理解 ESM 规范，确保代码符合 ES Module 标准。"

## 五、交叉引用

- [Vite 构建工具](../../../05.frontend/04-engineering/vite/README.md) — Vite 核心原理
- 主模块：[`05.frontend`](../../../05.frontend/README.md) — 前端知识体系

## 相关章节

- 深度阅读：[`05.frontend`](../../../05.frontend/README.md) — 主模块详细内容

> 📅 2026-09-01 · 咬文嚼字 · webpack-vite-migration · ⭐⭐⭐⭐（中频面试 + 实战必会）

← [返回: 咬文嚼字 · 09.front-end](../README.md)
