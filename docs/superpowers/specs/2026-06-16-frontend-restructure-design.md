# 前端章节(note/12.font-end)重构设计 spec

> 日期：2026-06-16
> 范围：`note/12.font-end/` 整体目录重构 + 拼写更正(`font-end` → `front-end`)
> 目标:把扁平 6 篇内容,重构为对齐 `04.system-design` / `06.spring` / `11.ai` 的 9 模块分层结构,
>      并修复现有内容的过时/错误项

---

## 1. 背景与动机

### 1.1 现状

`note/12.font-end/` 是仓库里**唯一没有顶层 README**、**唯一未做序号分层**的大章节,包含 6 个扁平子目录:

| 子目录 | 字节级评估 |
|---|---|
| `frameworks/` | 2026 框架格局(State of JS 2025),数据较新,质量较高 |
| `cors/` | CORS 基础 + Java 示例,质量尚可 |
| `bff/` | BFF 模式,质量较好 |
| `micro-frontend/` | 微前端综述,选型停留在 Single-SPA / Qiankun |
| `web-components/` | WC 综述,把已废弃的 HTML Imports 仍列为"四大核心"之一 |
| `sessions/` | Cookies vs LocalStorage 翻译稿 |

### 1.2 问题清单

1. **结构层面**
   - 没有顶层 README / 知识地图(其他大章节都有"模块导航 + 学习路线 + 开源参考")
   - 没有序号分层,新内容不知道往哪里放
   - 目录名 `font-end` 拼写错误,正确拼写为 `front-end`
   - 与 `13.split-hairs/12.font-end` 的边界不清(`sessions/` vs `split-hairs/storage/` 内容重叠)

2. **内容层面 — 现有错误/过时点**
   - `cors/README.md` 第 129-142 行的 JavaScript 代码块语言标记为 `java`
   - `cors/README.md` 第 188-201 行使用 Spring 5 起已废弃的 `WebMvcConfigurerAdapter`
   - `cors/README.md` 第 205-238 行 5 段示例的小标题重复为「允许所有源访问」,实为复制错漏
   - `web-components/README.md` 第 18 行把已废弃的 HTML Imports 列入"四大核心组成",应改为"三大核心 + 一项已废弃"
   - `micro-frontend/README.md` 未涵盖 Module Federation 2、Native Federation、wujie、micro-app、Modern.js Garfish 等 2025-2026 实际选型

3. **覆盖面层面 — 缺失主题**(约占现代前端知识 70%)
   - 基础:浏览器原理、HTML/CSS、HTTP 演进(前端视角)
   - 语言:JavaScript ES2024-2026、TypeScript 5 工程实践
   - 框架深度:React/Vue/Svelte/元框架各自的展开
   - 工程化:构建工具、包管理、Monorepo、测试、Lint
   - 架构:渲染模式全景、状态管理、路由、设计系统
   - 性能:Core Web Vitals、Lighthouse、监控
   - 安全:XSS/CSRF/CSP/SRI、依赖安全
   - 跨端:移动 / 桌面 / 小程序 / PWA
   - AI × 前端:AI SDK、AI Native UI、AI IDE、Vibe Coding

---

## 2. 设计目标

1. **结构对齐**:与 `04.system-design` / `06.spring` / `11.ai` 一致的"序号分层 + 顶层 README"风格
2. **零内容损失**:现有 6 篇全部原位迁入新结构,不删不重写
3. **顺手修订**:迁移过程中修订 CORS、Web Components 的过时点
4. **未来可扩展**:9 模块占位 README 标注"已有 ✓ / 待补 ⏳"主题清单,后续按需补深度内容不破坏骨架
5. **拼写更正**:`12.font-end` 改为 `12.front-end`,同步修正 `13.split-hairs/12.font-end`
6. **不引入新风险**:仅做骨架 + 迁移,不展开二级深度子主题,本轮 1-2 个工作日可完成

---

## 3. 目录结构(落盘形态)

```
note/12.front-end/                                ← 由 12.font-end 改名
├── README.md                                     ← 新增:知识地图 + 学习路线 + 9 模块导航 + 开源参考
├── 01-foundation/
│   └── README.md                                 ← 占位:浏览器 / HTML / CSS / Web 标准 + 待补清单
├── 02-language/
│   └── README.md                                 ← 占位:JavaScript / TypeScript + 待补清单
├── 03-frameworks/
│   ├── README.md                                 ← 由原 frameworks/README.md 迁入(2026 格局)
│   └── (后续:react/ vue/ svelte/ meta-frameworks/ selection/)
├── 04-engineering/
│   └── README.md                                 ← 占位:构建 / 包管理 / Monorepo / 测试 / Lint + 待补清单
├── 05-architecture/
│   ├── README.md                                 ← 模块索引:列出本模块已有 + 待补主题
│   ├── micro-frontend/
│   │   └── README.md                             ← 由原 micro-frontend/ 迁入
│   ├── web-components/
│   │   └── README.md                             ← 由原 web-components/ 迁入 + 修订废弃项
│   └── bff/
│       └── README.md                             ← 由原 bff/ 迁入
├── 06-performance/
│   └── README.md                                 ← 占位:CWV / Lighthouse / 监控 + 待补清单
├── 07-security/
│   ├── README.md                                 ← 模块索引:列出本模块已有 + 待补主题
│   ├── cors/
│   │   ├── README.md                             ← 由原 cors/ 迁入 + 修订 3 处过时
│   │   ├── img.png
│   │   └── img_1.png
│   └── sessions/
│       └── README.md                             ← 由原 sessions/ 迁入
├── 08-cross-platform/
│   └── README.md                                 ← 占位:移动 / 桌面 / 小程序 / PWA + 待补清单
└── 09-frontend-and-ai/
    └── README.md                                 ← 占位:AI SDK / AI Native UI / AI IDE / Vibe Coding + 待补清单
```

**文件计数**:
- **新写 9 个 Markdown**:1 顶层 README + 6 个占位模块 README(01/02/04/06/08/09)+ 2 个模块索引 README(05/07)
- **迁移 6 个 Markdown**:`frameworks/README.md`(直接作为 03-frameworks 的模块 README)、`micro-frontend/`、`web-components/`、`bff/`、`cors/`、`sessions/`(后 5 个迁入子目录),内容保留;其中 CORS、Web Components 顺手修订
- **迁移 2 个图片**:`cors/img.png`、`cors/img_1.png` 随 `cors/` 目录一起 `git mv`
- **最终目录下 Markdown 总数**:15 个

---

## 4. 顶层 12.front-end/README.md 内容模板

参考 `04.system-design/README.md` 与 `11.ai/README.md` 的结构,本 README 包含 6 块:

1. **一句话定位**
   - "现代前端工程的知识地图——从浏览器原理到 AI 协同开发"

2. **9 模块导航表**(模仿 11.ai L1-L6 的表格)

   | 序号 | 主题 | 核心内容 |
   |------|------|---------|
   | 01 | [基础](01-foundation/) | 浏览器原理 / HTML 语义化 / CSS 工程化 / Web 标准 |
   | 02 | [语言](02-language/) | JavaScript ES2024-2026 / TypeScript 5 工程实践 |
   | 03 | [框架](03-frameworks/) | 2026 框架格局 / React / Vue / Svelte / 元框架 / 选型 |
   | 04 | [工程化](04-engineering/) | Vite / Webpack / 包管理 / Monorepo / 测试 / Lint |
   | 05 | [架构](05-architecture/) | 渲染模式 / 微前端 / Web Components / BFF / 状态 / 路由 |
   | 06 | [性能](06-performance/) | Core Web Vitals / Lighthouse / 监控 |
   | 07 | [安全](07-security/) | XSS/CSRF/CSP / CORS / Sessions / 依赖供应链 |
   | 08 | [跨端](08-cross-platform/) | 移动 / 桌面 / 小程序 / PWA |
   | 09 | [前端与 AI](09-frontend-and-ai/) | AI SDK / AI Native UI / AI IDE / Vibe Coding |

3. **ASCII 知识脉络图**

   ```
   基础 → 语言 → 框架 → 工程化 → 架构 → 性能 → 安全 → 跨端 → AI
   ```

4. **学习路线**(4 条)
   - 新人入门:01 → 02 → 03(React/Vue 任一)→ 04
   - 后端补前端:02(TypeScript)→ 03(React 或 Vue)→ 05(BFF/微前端)
   - 架构师:05 → 06 → 07 → 03(选型)
   - AI 时代前端:03 → 04 → 09

5. **交叉引用**
   - `02.computer-basics/01-network/` — HTTP/HTTPS/HTTP2/HTTP3 协议族
   - `05.tools/monorepo/` — Monorepo 工具链(与 04-engineering 互补)
   - `11.ai/` — AI 知识体系(09-frontend-and-ai 的上游)
   - `14.story/` — 阿明餐厅故事:前端篇、多端篇、AI 学习悖论
   - `13.split-hairs/12.front-end/` — 前端咬文嚼字小专题

6. **开源参考**:暂留"暂无,后续补充"占位

---

## 5. 9 个模块 README 模板(占位页)

每个模块 README 约 100-200 字,包含 4 段:

```markdown
# <模块名>

> 一句话定位

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| <主题 A> | ⏳ 待补 | ... |
| <主题 B> | ✓ 已有 | [链接到子目录](xxx/) |

## 与其他模块的关系

- 上游:依赖 [<其他模块>](../0X-xxx/)
- 下游:被 [<其他模块>](../0X-xxx/) 使用

## 学习建议

简述阅读顺序、推荐资源(本节后续按需补充)。
```

---

## 6. 迁移与修订动作清单

| # | 类型 | 源 | 目标 | 备注 |
|---|------|----|------|------|
| 1 | rename | `note/12.font-end/` | `note/12.front-end/` | `git mv`,保留历史 |
| 2 | new | — | `12.front-end/README.md` | 按 §4 模板编写 |
| 3 | new | — | `12.front-end/01-foundation/README.md` | 占位 |
| 4 | new | — | `12.front-end/02-language/README.md` | 占位 |
| 5 | move | `frameworks/README.md` | `03-frameworks/README.md` | 内容保留,顶部加面包屑导航 |
| 6 | new | — | `12.front-end/04-engineering/README.md` | 占位 |
| 7 | new | — | `12.front-end/05-architecture/README.md` | 模块索引 |
| 8 | move | `micro-frontend/README.md` | `05-architecture/micro-frontend/README.md` | 内容保留,顶部加导航 |
| 9 | move + edit | `web-components/README.md` | `05-architecture/web-components/README.md` | 修订:HTML Imports 从"四大核心"剔除,改为"三大核心 + 一项已废弃" |
| 10 | move | `bff/README.md` | `05-architecture/bff/README.md` | 内容保留,顶部加导航 |
| 11 | new | — | `12.front-end/06-performance/README.md` | 占位 |
| 12 | new | — | `12.front-end/07-security/README.md` | 模块索引 |
| 13 | move + edit | `cors/README.md` + 2 张图片 | `07-security/cors/README.md` + 图片 | 修订:① 代码语言 java→javascript ② `WebMvcConfigurerAdapter` 替换为 `WebMvcConfigurer` ③ 5 处「允许所有源访问」标题改为分别准确的小标题(允许指定源 / 允许携带凭据 / 限定方法与头部 / 配置预检缓存) |
| 14 | move | `sessions/README.md` | `07-security/sessions/README.md` | 顶部加 "本文 vs `13.split-hairs/12.front-end/storage/`" 关系说明 |
| 15 | new | — | `12.front-end/08-cross-platform/README.md` | 占位 |
| 16 | new | — | `12.front-end/09-frontend-and-ai/README.md` | 占位 |
| 17 | edit | `note/README.md` 第 170-174 行 | — | 改为 9 模块导航表,所有链接由 `12.font-end/...` → `12.front-end/...` |
| 18 | rename | `note/13.split-hairs/12.font-end/` | `note/13.split-hairs/12.front-end/` | `git mv` |
| 19 | edit | `note/README.md` 第 216-218 行 | — | 链接由 `13.split-hairs/12.font-end/...` → `13.split-hairs/12.front-end/...` |
| 20 | verify | — | — | `grep -r "12.font-end" .` 全仓校验,确保无残留 |

---

## 7. CORS 修订细节

### 7.1 代码块语言标记
- 现:第 129 行 ```` ```java ````,内容是 JavaScript
- 改:```` ```javascript ````

### 7.2 替换废弃的 `WebMvcConfigurerAdapter`
- 现(第 188-201 行):
  ```java
  @Configuration
  public class CorsConfig extends WebMvcConfigurerAdapter { ... }
  ```
- 改:
  ```java
  @Configuration
  public class CorsConfig implements WebMvcConfigurer { ... }
  ```
- 增加一行说明:"`WebMvcConfigurerAdapter` 自 Spring 5(2017)起标记 deprecated,Spring 6 仅保留兼容性,新项目应直接实现 `WebMvcConfigurer` 接口(其方法均为 Java 8 default 方法,无需 Adapter)。"

### 7.3 修复 5 段示例的重复小标题
原文(第 205-238 行)5 段都叫「允许所有源访问」,实际示例不同:

| 段 | 改后标题 |
|---|----------|
| 1 | 1. 允许所有源访问(通配符) |
| 2 | 2. 允许指定源访问 |
| 3 | 3. 允许指定源 + 携带凭据 |
| 4 | 4. 限定方法与头部 |
| 5 | 5. 配置预检请求缓存时间 |

---

## 8. Web Components 修订细节

### 8.1 "四大核心"改为"三大核心 + 一项已废弃"

- 现(第 6 行):"Web Components 由四大核心技术构成"
- 改:"Web Components 由三大核心技术构成"
- 第 18-19 行 `HTML Imports(已废弃)` 从主列表移出,新增一段:
  > **已废弃技术**:HTML Imports 曾是 Web Components 的第四项标准,但因与 ES Modules 重叠且浏览器支持不一,2019 年起被各主流浏览器全面移除。现代项目应使用 ES Modules + 构建工具替代。

---

## 9. 不做什么(YAGNI 边界)

- ⛔ 不展开 9 模块的二级深度子主题(留给后续按需写,本轮只立骨架)
- ⛔ 不重写现有 6 篇正文(除 CORS、WC 必须修订的过时点外)
- ⛔ 不引入新的框架/库尝鲜内容(如 Lit 3 / Tailwind 4 等深度比较)
- ⛔ 不动 `09.other`、`13.split-hairs` 其他章节;只对 `13.split-hairs/12.font-end` 做拼写改名
- ⛔ 不修改 `frameworks/README.md` 内容(仅迁移),其 2026 数据已较新
- ⛔ 不动 `bff/`、`micro-frontend/`、`sessions/` 的正文(仅迁移 + 顶部加导航/关系说明)

---

## 10. 风险与回滚

### 10.1 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 外部链接指向 `12.font-end`(博客/IDE 书签) | 私人 repo,影响可控 | 暂不引入 redirect |
| 全仓链接漏改 | 顶层 README 导航失效 | 执行 `grep -r "12.font-end" .` 与 `grep -r "12.font-end" docs/` 双向校验 |
| 误删图片 | CORS 流程图丢失 | 用 `git mv` 而非 `rm + add`,图片随目录迁移 |
| `git mv` 在 Windows 上大小写敏感问题 | `font-end` → `front-end` 是改字符不是改大小写,无此风险 | 无需特殊处理 |

### 10.2 回滚

本轮所有变更分 1-2 个 commit 提交,任一时刻 `git revert <commit>` 可恢复。

---

## 11. 验收标准

- [ ] `note/12.front-end/README.md` 存在,符合 §4 模板,含 9 模块导航表
- [ ] 9 个模块 README 全部就位:01/02/04/06/08/09 为占位、05/07 为模块索引、03 为迁入(原 frameworks)
- [ ] 5 个子目录 README 全部迁入(`05-architecture/micro-frontend|web-components|bff/`、`07-security/cors|sessions/`),内容无丢失
- [ ] CORS 3 处修订全部落实(代码语言 / Adapter 替换 / 5 处小标题去重)
- [ ] Web Components "四大核心"修订为"三大核心 + 一项已废弃"
- [ ] `note/README.md` 第 170-174 行更新为 9 模块导航表;第 216-218 行链接更新
- [ ] `note/13.split-hairs/12.font-end` 改名为 `12.front-end`
- [ ] `grep -r "12.font-end" .` 在仓库下应返回 0 行(本 spec 文档本身除外)
- [ ] 所有图片(`cors/img.png`、`cors/img_1.png`)随目录迁移,链接仍可点击

---

## 12. 后续(本 spec 范围外)

本轮只建骨架。后续可独立、按需推进的工作:
- 03-frameworks 拆出 react/vue/svelte/meta-frameworks/selection 深度页
- 04-engineering 补 Vite/Webpack/Turbopack 对比、pnpm/Bun 选型
- 06-performance 补 CWV 实战、Lighthouse 评分项详解
- 09-frontend-and-ai 补 Vercel AI SDK 实战、Cursor/Windsurf/Claude Code 工作流
- 05-architecture 补渲染模式全景图(CSR/SSR/SSG/ISR/RSC/Islands)

每个后续主题都按"小步快跑"独立写一个 README,无需再走骨架重构。
