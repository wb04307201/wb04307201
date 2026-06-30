# Monorepo 工程实践

> 一句话定位：**pnpm workspaces / Turborepo / Nx —— 多包协作的工程化实战**

Monorepo 是把多个包（apps / packages）放在一个 Git 仓库中统一管理的工程模式。2026 年，几乎所有大型前端项目（React、Vue、Babel、Next.js）都采用 Monorepo。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Monorepo 工程实践 本应该很简单，一句话定位：**pnpm workspaces / Turborepo / Nx —— 多包协作的工程化实战**

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 1. Monorepo 的核心价值

| 价值 | 说明 |
|------|------|
| **代码共享** | UI 库 / 工具库直接 import，无需发包 |
| **原子提交** | 跨包改动一次 commit，不会版本不一致 |
| **统一工具链** | ESLint / TSConfig / Prettier 共享配置 |
| **依赖统一** | 一个 lockfile，版本一致性 |
| **CI 优化** | 只构建受影响的项目 |

---

## 2. 典型目录结构

```text
monorepo/
├── apps/                       # 应用
│   ├── web/                    # Web 应用（Vite + React）
│   ├── docs/                   # 文档站（Astro）
│   └── mobile/                 # 移动应用（React Native）
├── packages/                   # 共享包
│   ├── ui/                     # 共享 UI 组件库
│   ├── utils/                  # 工具函数库
│   ├── config-eslint/          # 共享 ESLint 配置
│   ├── config-ts/              # 共享 TSConfig
│   └── design-tokens/          # Design Token
├── package.json                # 根 package.json
├── pnpm-workspace.yaml         # pnpm workspaces 配置
├── turbo.json                  # Turborepo 配置
└── pnpm-lock.yaml              # 单一 lockfile
```

---

## 3. pnpm workspaces 配置

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```json
// apps/web/package.json
{
  "name": "@myorg/web",
  "dependencies": {
    "@myorg/ui": "workspace:*",
    "@myorg/utils": "workspace:*"
  }
}
```

```bash
# 安装依赖
pnpm install

# 在特定项目运行脚本
pnpm --filter @myorg/web dev

# 在所有项目运行构建
pnpm -r build
```

---

## 4. Turborepo：构建编排

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],  // 依赖包先构建
      "outputs": ["dist/**"],
      "inputs": ["src/**", "*.json"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

```bash
# 运行所有项目的 build（自动依赖排序 + 缓存）
turbo build

# 仅运行 @myorg/web 及其依赖
turbo build --filter=@myorg/web

# 远程缓存（团队协作）
turbo build --remote-only
```

---

## 5. Nx：企业级 Monorepo

| 特性 | Turborepo | Nx |
|------|----------|-----|
| **学习曲线** | 低 | 高 |
| **构建编排** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **远程缓存** | ✅ Vercel | ✅ Nx Cloud |
| **代码生成器** | ❌ | ✅（插件化生成） |
| **依赖图可视化** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **适用** | 中大型 | 大型企业级 |

---

## 6. 共享配置实战

### 共享 TSConfig
```json
// packages/config-ts/base.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext"
  }
}

// apps/web/tsconfig.json
{
  "extends": "@myorg/config-ts/base.json",
  "compilerOptions": {
    "outDir": "./dist"
  }
}
```

### 共享 ESLint
```javascript
// packages/config-eslint/index.js
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  // ...
}

// apps/web/.eslintrc.js
module.exports = {
  extends: ['@myorg/config-eslint'],
}
```

---

## 7. 包发布策略

| 策略 | 适用 | 工具 |
|------|------|------|
| **内部包（不发布）** | 内部共享 | `private: true` |
| **发布到 npm** | 对外库 | Changesets + npm publish |
| **私有 Registry** | 企业内部 | Verdaccio / GitHub Packages |

### Changesets 版本管理

```bash
# 创建变更集
npx changeset

# 版本发布
npx changeset version
npx changeset publish
```

---

## 8. CI 优化

```yaml
# GitHub Actions
- name: Cache Turbo
  uses: actions/cache@v4
  with:
    path: .turbo
    key: turbo-${{ hashFiles('**/pnpm-lock.yaml') }}
    
- name: Build
  run: turbo build --filter=...[origin/main]  # 仅构建受影响的
```

---

## 9. 常见陷阱

| 陷阱 | 解决 |
|------|------|
| **幽灵依赖** | pnpm 严格模式 + `pnpm.strict-peer-dependencies` |
| **循环依赖** | Turborepo 报错，重新设计包结构 |
| **构建顺序错** | `dependsOn: ["^build"]` 显式声明 |
| **Dev Server 端口冲突** | 各 app 不同端口 + turbo `persistent: true` |
| **包间类型不共享** | 用 `workspace:*` + TS project references |

---

## 10. 学习路径

1. **入门**（3 天）：pnpm workspaces 搭建最小 monorepo
2. **进阶**（1 周）：Turborepo 集成 + 共享配置
3. **高级**（持续）：远程缓存、CI 优化、Nx 企业级方案

## 11. 交叉引用

- [`04-engineering/`](../) — 工程化总览
- [`04-engineering/vite/`](../vite/) — Vite 与 Monorepo 集成
- [`05.tools/monorepo/`](../../../05.tools/monorepo/README.md/) — Monorepo 工具链专题
