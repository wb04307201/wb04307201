# 前端章节 note/12.font-end 重构 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `note/12.font-end/` 重构为 9 模块分层结构,与 `04.system-design`/`06.spring`/`11.ai` 一致;同时修正拼写错误(`font-end` → `front-end`)并修订 CORS、Web Components 的过时点。

**Architecture:** 分 5 个 commit 推进:① 拼写改名 ② 子内容迁入模块子目录 ③ 修订迁入内容 ④ 新建模块 README ⑤ 更新顶层 note/README.md。每一步用 `git mv` 保留历史,每个 commit 都能独立通过验收。

**Tech Stack:** git (Windows 11 / bash shell)、Markdown、no build/test pipeline(纯文档章节)

**Spec:** `docs/superpowers/specs/2026-06-16-frontend-restructure-design.md`

---

## 文件结构总览(完成后)

```
note/
├── README.md                                      (修改 §6 行 170-174 & 216-218)
├── 12.front-end/                                  (改名 from 12.font-end)
│   ├── README.md                                  (新建 — 顶层知识地图)
│   ├── 01-foundation/README.md                    (新建 — 占位)
│   ├── 02-language/README.md                      (新建 — 占位)
│   ├── 03-frameworks/README.md                    (迁入 from frameworks/README.md)
│   ├── 04-engineering/README.md                   (新建 — 占位)
│   ├── 05-architecture/
│   │   ├── README.md                              (新建 — 模块索引)
│   │   ├── bff/README.md                          (迁入)
│   │   ├── micro-frontend/README.md               (迁入)
│   │   └── web-components/README.md               (迁入 + 修订)
│   ├── 06-performance/README.md                   (新建 — 占位)
│   ├── 07-security/
│   │   ├── README.md                              (新建 — 模块索引)
│   │   ├── cors/                                  (迁入 + 修订)
│   │   │   ├── README.md
│   │   │   ├── img.png
│   │   │   └── img_1.png
│   │   └── sessions/README.md                     (迁入 + 顶部加关系说明)
│   ├── 08-cross-platform/README.md                (新建 — 占位)
│   └── 09-frontend-and-ai/README.md               (新建 — 占位)
└── 13.split-hairs/
    └── 12.front-end/                              (改名 from 12.font-end)
        ├── get-and-post/README.md
        ├── message/README.md
        └── storage/README.md
```

---

## Task 1: 改名 — `font-end` → `front-end`

**Files:**
- Rename: `note/12.font-end/` → `note/12.front-end/`
- Rename: `note/13.split-hairs/12.font-end/` → `note/13.split-hairs/12.front-end/`

- [ ] **Step 1.1: 改名主章节目录**

Run:
```bash
cd "D:/developer/IdeaProjects/wb04307201"
git mv note/12.font-end note/12.front-end
```
Expected: 命令静默成功,无 stderr 输出

- [ ] **Step 1.2: 改名 split-hairs 子目录**

Run:
```bash
git mv note/13.split-hairs/12.font-end note/13.split-hairs/12.front-end
```
Expected: 命令静默成功

- [ ] **Step 1.3: 校验改名结果**

Run:
```bash
ls note/12.front-end/ && ls note/13.split-hairs/12.front-end/
```
Expected: 第一个 ls 列出 `bff cors frameworks micro-frontend sessions web-components`;第二个 ls 列出 `get-and-post message storage`

- [ ] **Step 1.4: 校验 git 已识别为 rename**

Run:
```bash
git status --short
```
Expected: 看到一系列 `R  note/12.font-end/... -> note/12.front-end/...` 与 `R  note/13.split-hairs/12.font-end/... -> note/13.split-hairs/12.front-end/...`,**不应**出现 `D` (delete) 或 `??` (untracked) 行

- [ ] **Step 1.5: Commit**

Run:
```bash
git commit -m "refactor(note): 12.font-end 改名为 12.front-end 修正拼写

note/12.font-end 与 note/13.split-hairs/12.font-end 一并改名,
为后续 9 模块分层重构准备。

详见 docs/superpowers/specs/2026-06-16-frontend-restructure-design.md

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 出现 `1 file changed` 或多个 file changed(取决于 git 自动检测的 rename 数量),无报错

---

## Task 2: 迁入 — 现有 6 个子目录进入新的模块结构

**Files:**
- Move: `12.front-end/frameworks/` → `12.front-end/03-frameworks/`
- Move: `12.front-end/micro-frontend/` → `12.front-end/05-architecture/micro-frontend/`
- Move: `12.front-end/web-components/` → `12.front-end/05-architecture/web-components/`
- Move: `12.front-end/bff/` → `12.front-end/05-architecture/bff/`
- Move: `12.front-end/cors/` → `12.front-end/07-security/cors/`
- Move: `12.front-end/sessions/` → `12.front-end/07-security/sessions/`

- [ ] **Step 2.1: 创建 05-architecture 与 07-security 父目录**

git 不会跟踪空目录,但 `git mv` 需要目标父目录存在。Windows 上用 mkdir 加上 -p 等价物:

Run:
```bash
cd "D:/developer/IdeaProjects/wb04307201"
mkdir -p note/12.front-end/05-architecture note/12.front-end/07-security
```
Expected: 命令静默成功

- [ ] **Step 2.2: 迁入 frameworks → 03-frameworks**

Run:
```bash
git mv note/12.front-end/frameworks note/12.front-end/03-frameworks
```
Expected: 静默成功。整个 `frameworks/` 文件夹改名为 `03-frameworks/`,其内的 `README.md` 直接成为模块 README

- [ ] **Step 2.3: 迁入 micro-frontend → 05-architecture/micro-frontend**

Run:
```bash
git mv note/12.front-end/micro-frontend note/12.front-end/05-architecture/micro-frontend
```
Expected: 静默成功

- [ ] **Step 2.4: 迁入 web-components → 05-architecture/web-components**

Run:
```bash
git mv note/12.front-end/web-components note/12.front-end/05-architecture/web-components
```
Expected: 静默成功

- [ ] **Step 2.5: 迁入 bff → 05-architecture/bff**

Run:
```bash
git mv note/12.front-end/bff note/12.front-end/05-architecture/bff
```
Expected: 静默成功

- [ ] **Step 2.6: 迁入 cors → 07-security/cors(包含 2 张图片)**

Run:
```bash
git mv note/12.front-end/cors note/12.front-end/07-security/cors
```
Expected: 静默成功。`README.md`、`img.png`、`img_1.png` 全部随目录迁移

- [ ] **Step 2.7: 迁入 sessions → 07-security/sessions**

Run:
```bash
git mv note/12.front-end/sessions note/12.front-end/07-security/sessions
```
Expected: 静默成功

- [ ] **Step 2.8: 校验迁入结果**

Run:
```bash
find note/12.front-end -type f | sort
```
Expected: 输出以下 8 个文件(顺序可能不同):
```
note/12.front-end/03-frameworks/README.md
note/12.front-end/05-architecture/bff/README.md
note/12.front-end/05-architecture/micro-frontend/README.md
note/12.front-end/05-architecture/web-components/README.md
note/12.front-end/07-security/cors/README.md
note/12.front-end/07-security/cors/img.png
note/12.front-end/07-security/cors/img_1.png
note/12.front-end/07-security/sessions/README.md
```

- [ ] **Step 2.9: 校验 git 识别为 rename**

Run:
```bash
git status --short | head -20
```
Expected: 所有变更都是 `R` (rename) 而非 `D` + `A`(delete + add);若出现 `D` 行,说明 git 未识别为 rename,需 `git add .` 后让 git 凭内容相似度重新匹配

- [ ] **Step 2.10: Commit**

Run:
```bash
git commit -m "refactor(note/12.front-end): 6 个子目录迁入 9 模块分层结构

- frameworks/ → 03-frameworks/
- micro-frontend/ → 05-architecture/micro-frontend/
- web-components/ → 05-architecture/web-components/
- bff/ → 05-architecture/bff/
- cors/ → 07-security/cors/ (含 2 张图片)
- sessions/ → 07-security/sessions/

内容零修改,仅 git mv。

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: 显示 `8 files changed, 0 insertions(+), 0 deletions(-)`(全部是 rename,无内容变化)

---

## Task 3: 修订 — CORS 文档(3 处过时点)

**Files:**
- Modify: `note/12.front-end/07-security/cors/README.md`

- [ ] **Step 3.1: 修订 ① — JavaScript 代码块语言标记**

Edit `note/12.front-end/07-security/cors/README.md`:

old_string(精确匹配第 129 行起的代码块开头):
````
如下示例代码:在`CORS`请求中以`Authorization`标头的形式发送凭据:
```java
function sendAuthRequestToCrossOrigin() {
````

new_string:
````
如下示例代码:在`CORS`请求中以`Authorization`标头的形式发送凭据:
```javascript
function sendAuthRequestToCrossOrigin() {
````

- [ ] **Step 3.2: 修订 ② — `WebMvcConfigurerAdapter` 替换为 `WebMvcConfigurer`**

Edit 同一文件:

old_string:
```
方法3:配置`Configuration`

如下示例代码:增加一个配置类继承`WebMvcConfigurerAdapter`或者实现`WebMvcConfigurer`接口,项目启动时,会自动读取配置。
```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;
@Configuration
public class CorsConfig extends WebMvcConfigurerAdapter {
    static final String ORIGINS[] = new String[]{"GET", "POST", "PUT", "DELETE"};

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**").allowedOrigins("*").allowCredentials(true).allowedMethods(ORIGINS).maxAge(3600);
    }
}
```

new_string:
```
方法3:配置`Configuration`

如下示例代码:增加一个配置类实现 `WebMvcConfigurer` 接口,项目启动时会自动读取配置。
```java
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    static final String[] METHODS = new String[]{"GET", "POST", "PUT", "DELETE"};

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns("*")   // Spring 5.3+ 推荐:支持 allowCredentials=true 时不限源
                .allowCredentials(true)
                .allowedMethods(METHODS)
                .maxAge(3600);
    }
}
```

> ⚠️ `WebMvcConfigurerAdapter` 自 Spring 5.0(2017)起被标记 `@Deprecated`,Spring 6 仅保留兼容性,新项目应直接实现 `WebMvcConfigurer` 接口——该接口的所有方法均为 Java 8 `default` 方法,无需 Adapter 提供空实现。
>
> 另:`allowCredentials(true)` 与 `allowedOrigins("*")` 在 Spring 5.3+ 不再允许同时使用(浏览器规范也禁止),应改用 `allowedOriginPatterns(...)`。
```

- [ ] **Step 3.3: 修订 ③ — 5 段重复小标题去重**

Edit 同一文件:

old_string:
```
另外,在服务器,可以通过设置响应头部来细粒度配置 CORS,具体的如下:
1.允许所有源访问
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
```

2.允许所有源访问
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
```

3.允许所有源访问
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Credentials: true
```

4.允许所有源访问
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

5.设置预检请求的缓存时间
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600  // 3600秒
```
```

new_string:
```
另外,在服务器端可以通过设置响应头部来细粒度配置 CORS,具体如下:

1. 允许任意源访问(通配符,不能与 credentials 同用)
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
```

2. 仅允许指定源访问
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
```

3. 允许指定源 + 携带凭据(Cookie)
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Credentials: true
```

4. 限定允许的方法与自定义头部
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

5. 配置预检请求的缓存时间(减少 OPTIONS 频次)
```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://yuanjava.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600
```
```

- [ ] **Step 3.4: 校验修订**

Run:
```bash
grep -n "WebMvcConfigurerAdapter\|允许所有源访问" note/12.front-end/07-security/cors/README.md
```
Expected: 无输出(两个老字符串均已不存在)

Run:
```bash
grep -n "WebMvcConfigurer\|允许任意源\|仅允许指定源\|配置预检请求的缓存时间" note/12.front-end/07-security/cors/README.md
```
Expected: 至少 4 行命中

- [ ] **Step 3.5: Commit**

Run:
```bash
git add note/12.front-end/07-security/cors/README.md
git commit -m "fix(note/12.front-end/cors): 修订 3 处过时与错漏

1. JavaScript 代码块语言标记由 java 修正为 javascript
2. 替换已废弃的 WebMvcConfigurerAdapter → WebMvcConfigurer
   并补充 allowedOriginPatterns 的 Spring 5.3+ 用法说明
3. 5 段示例的重复小标题「允许所有源访问」改为分别准确的小标题

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: `1 file changed`,内容有增删

---

## Task 4: 修订 — Web Components(HTML Imports 归类)

**Files:**
- Modify: `note/12.front-end/05-architecture/web-components/README.md`

- [ ] **Step 4.1: 修订四大核心 → 三大核心 + 已废弃**

Edit `note/12.front-end/05-architecture/web-components/README.md`:

old_string:
```
## 一、核心组成
Web Components 由四大核心技术构成,共同实现组件的封装与复用:
1. **Custom Elements**
    - 允许开发者定义全新的 HTML 标签(如 `<my-button>`),并为其绑定自定义逻辑。
    - 提供生命周期回调(如 `connectedCallback`、`attributeChangedCallback`),便于管理组件状态。

2. **Shadow DOM**
    - 为组件创建独立的 DOM 树,实现样式和行为的隔离,避免全局 CSS/JS 污染。
    - 通过 `slot` 机制支持内容投影,增强组件灵活性。

3. **HTML Templates**
    - 定义可复用的 HTML 片段(`<template>` 标签),通过 JavaScript 动态实例化,减少重复代码。

4. **HTML Imports(已废弃)**
    - 原用于跨文件导入组件,现被 ES Modules 或构建工具替代。
```

new_string:
```
## 一、核心组成
Web Components 由**三大核心技术**构成,共同实现组件的封装与复用:
1. **Custom Elements**
    - 允许开发者定义全新的 HTML 标签(如 `<my-button>`),并为其绑定自定义逻辑。
    - 提供生命周期回调(如 `connectedCallback`、`attributeChangedCallback`),便于管理组件状态。
    - **进阶**:Form-associated Custom Elements(2022+)让自定义元素可以参与表单提交、校验与重置。

2. **Shadow DOM**
    - 为组件创建独立的 DOM 树,实现样式和行为的隔离,避免全局 CSS/JS 污染。
    - 通过 `slot` 机制支持内容投影,增强组件灵活性。
    - **进阶**:Declarative Shadow DOM(2023+)允许 SSR 时直接以 HTML 标记声明 Shadow Tree,无需 JS 介入。

3. **HTML Templates**
    - 定义可复用的 HTML 片段(`<template>` 标签),通过 JavaScript 动态实例化,减少重复代码。

> **已废弃的第四项**:HTML Imports 曾是 Web Components 早期标准的第四项技术,但因与 ES Modules 重叠且仅 Chrome 实现,2019 年起被各主流浏览器全面移除,2020 年从 Chrome 80 中正式删除。现代项目应使用 ES Modules + 构建工具(Vite/Rollup/Webpack)替代。
```

- [ ] **Step 4.2: 校验修订**

Run:
```bash
grep -n "四大核心\|HTML Imports(已废弃)" note/12.front-end/05-architecture/web-components/README.md
```
Expected: 无输出

Run:
```bash
grep -n "三大核心\|Form-associated\|Declarative Shadow DOM\|已废弃的第四项" note/12.front-end/05-architecture/web-components/README.md
```
Expected: 至少 4 行命中

- [ ] **Step 4.3: Commit**

Run:
```bash
git add note/12.front-end/05-architecture/web-components/README.md
git commit -m "fix(note/12.front-end/web-components): HTML Imports 从四大核心移出

- 四大核心 → 三大核心
- HTML Imports 改为独立段「已废弃的第四项」并说明 2020 年从 Chrome 删除
- 补充 Form-associated Custom Elements(2022+)
- 补充 Declarative Shadow DOM(2023+)与 SSR 场景

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: `1 file changed`

---

## Task 5: 在 sessions 文档顶部加关系说明

**Files:**
- Modify: `note/12.front-end/07-security/sessions/README.md`

- [ ] **Step 5.1: 在标题下加关系说明**

Edit `note/12.front-end/07-security/sessions/README.md`:

old_string:
```
# Cookies vs LocalStorage 用于会话管理:你需要知道的一切

**原文链接**:[https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know](https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know)
```

new_string:
```
# Cookies vs LocalStorage 用于会话管理:你需要知道的一切

> 📚 **相关阅读**:本文聚焦**安全视角**——为什么会话 Token 应该用 Cookie 而不是 LocalStorage。
> 若想从**全景视角**对比 Cookie / localStorage / sessionStorage / IndexedDB 4 种前端存储的容量/生命周期/作用域,请看 [`13.split-hairs/12.front-end/storage/`](../../../13.split-hairs/12.front-end/storage/README.md)。
> 两篇互补,本文为安全选型,split-hairs 为存储 API 全景速查。

**原文链接**:[https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know](https://supertokens.com/blog/cookies-vs-localstorage-for-sessions-everything-you-need-to-know)
```

- [ ] **Step 5.2: 校验**

Run:
```bash
grep -n "相关阅读\|两篇互补" note/12.front-end/07-security/sessions/README.md
```
Expected: 2 行命中

- [ ] **Step 5.3: Commit**

Run:
```bash
git add note/12.front-end/07-security/sessions/README.md
git commit -m "docs(note/12.front-end/sessions): 顶部加与 split-hairs/storage 的关系说明

避免读者在两篇内容重叠的文章间不知所择:
- 本篇 = 安全视角(为什么会话 Token 不能放 LocalStorage)
- split-hairs/storage = 4 种存储 API 的全景速查表

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: `1 file changed`

---

## Task 6: 新建 — 9 个模块 README + 1 个顶层 README

**Files:**
- Create: `note/12.front-end/README.md`
- Create: `note/12.front-end/01-foundation/README.md`
- Create: `note/12.front-end/02-language/README.md`
- Create: `note/12.front-end/04-engineering/README.md`
- Create: `note/12.front-end/05-architecture/README.md`
- Create: `note/12.front-end/06-performance/README.md`
- Create: `note/12.front-end/07-security/README.md`
- Create: `note/12.front-end/08-cross-platform/README.md`
- Create: `note/12.front-end/09-frontend-and-ai/README.md`

注意:`03-frameworks/README.md` 已存在(由 Task 2 迁入),本任务不创建它。

- [ ] **Step 6.1: 写顶层 12.front-end/README.md**

Write to `note/12.front-end/README.md`:

````markdown
# 十二、前端

> 现代前端工程的知识地图——从浏览器原理到 AI 协同开发。本章按 **9 个分层模块**组织,从基础理论到工程实践,从单端到多端,从经典到 AI 时代。

---

## 目录导航

| 序号 | 主题 | 核心内容 |
|------|------|---------|
| **01** | [基础](01-foundation/README.md) | 浏览器原理(事件循环/渲染流水线/Web API)、HTML 语义化、CSS 工程化、Web 标准 |
| **02** | [语言](02-language/README.md) | JavaScript ES2024-2026 关键特性、TypeScript 5 工程实践、类型体操、tsconfig |
| **03** | [框架](03-frameworks/README.md) | 2026 框架格局(State of JS 2025)、React / Vue / Svelte 深度、元框架、选型决策树 |
| **04** | [工程化](04-engineering/README.md) | 构建(Vite/Webpack/Turbopack/Rspack/esbuild)、包管理、Monorepo、测试、Lint |
| **05** | [架构](05-architecture/README.md) | 渲染模式全景(CSR/SSR/SSG/ISR/RSC/Islands)、微前端、Web Components、BFF、状态管理、路由 |
| **06** | [性能](06-performance/README.md) | Core Web Vitals(LCP/INP/CLS)、Lighthouse、Web Worker、前端监控/RUM |
| **07** | [安全](07-security/README.md) | XSS/CSRF/CSP/SRI、CORS、Session 存储、依赖供应链(SBOM / npm 投毒) |
| **08** | [跨端](08-cross-platform/README.md) | React Native / Flutter / 鸿蒙 ArkUI、Electron / Tauri、小程序 / Taro / uni-app、PWA |
| **09** | [前端与 AI](09-frontend-and-ai/README.md) | AI SDK(Vercel AI SDK / Mastra)、AI Native UI(流式/生成式)、AI IDE(Cursor / Windsurf / Claude Code)、Vibe Coding |

---

## 知识脉络

```
                  ┌─────────────────────────────┐
                  │     12.front-end 前端       │
                  └──────────────┬──────────────┘
                                 │
       ┌──────────┬──────────┬───┴────┬──────────┬──────────┬──────────┐
       ▼          ▼          ▼        ▼          ▼          ▼          ▼
   ┌───────┐ ┌──────┐ ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐
   │01 基础 │ │02 语言│ │03 框架    │ │04 工程│ │05 架构│ │06 性能│ │07 安全 │
   └───────┘ └──────┘ └──────────┘ └──────┘ └──────┘ └──────┘ └────────┘
                                                  │          │
                                                  ▼          ▼
                                          ┌──────────────┐ ┌──────────┐
                                          │ 08 跨端       │ │ 09 前端AI │
                                          └──────────────┘ └──────────┘

   层次:理论基础 → 语言核心 → 框架生态 → 工程方法 → 架构模式 → 横切关注点 → 时代延伸
```

---

## 学习路线(4 条)

| 路线 | 推荐顺序 | 适用人群 |
|------|---------|---------|
| **🆕 新人入门** | 01 → 02(JS)→ 03(React 或 Vue 任一)→ 04 | 0 经验,系统建立认知 |
| **🔄 后端补前端** | 02(TypeScript)→ 03 → 05(BFF / 微前端)| 已有后端基础,补前端工程视角 |
| **🏛️ 架构师视角** | 05 → 06 → 07 → 03(选型) | 主导技术选型与架构设计 |
| **🤖 AI 时代前端** | 03 → 04 → 09 | 关注 AI Native UI / Vibe Coding |

---

## 与其他章节的交叉引用

- 🌐 [`02.computer-basics/01-network/`](../02.computer-basics/01-network/README.md) — HTTP/HTTPS/HTTP2/HTTP3 协议族(本章「07 安全」的底层依赖)
- 🛠️ [`05.tools/monorepo/`](../05.tools/monorepo/README.md) — Monorepo 工具链全景(与「04 工程化」互补)
- 🤖 [`11.ai/`](../11.ai/README.md) — AI 知识体系(「09 前端与 AI」的上游)
- 📖 [`14.story/`](../14.story/index.md) — 阿明餐厅故事系列(前端篇、多端篇、AI 学习悖论可对照阅读)
- 🔍 [`13.split-hairs/12.front-end/`](../13.split-hairs/12.front-end/) — 前端咬文嚼字小专题(GET vs POST / 消息推送方式 / 前端存储)

---

## 开源参考

> 本章节暂无配套开源仓库,后续按需补充。
````

- [ ] **Step 6.2: 写 01-foundation/README.md**

Write to `note/12.front-end/01-foundation/README.md`:

```markdown
# 01 · 基础

> 前端的"地基":浏览器如何工作、HTML/CSS 如何表达结构与样式、Web 平台标准在演进什么。脱离这一层,框架/工程化的优化都是空中楼阁。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| 浏览器原理 | ⏳ 待补 | 事件循环、Microtask vs Macrotask、渲染流水线(Style/Layout/Paint/Composite)、Web API |
| HTML 语义化 | ⏳ 待补 | 结构化标签、ARIA、可访问性(WCAG 2.2 / 3.0) |
| CSS 工程化 | ⏳ 待补 | Tailwind 4、CSS-in-JS、CSS Modules、OKLCH 色彩空间、Container Queries |
| Web 标准演进 | ⏳ 待补 | WebAssembly、WebGPU、WebTransport、View Transitions、File System Access API |

---

## 与其他模块的关系

- **上游**:依赖 [`02.computer-basics/01-network/`](../../02.computer-basics/01-network/README.md) 的 HTTP 协议基础
- **下游**:为 [`02 语言`](../02-language/README.md)、[`03 框架`](../03-frameworks/README.md)、[`06 性能`](../06-performance/README.md) 提供底层模型
- **横向**:与 [`07 安全`](../07-security/README.md) 共享浏览器同源策略、CSP 等概念

---

## 学习建议

- 顺序建议:浏览器原理 → HTML 语义化 → CSS 工程化 → Web 标准演进
- 推荐参考:MDN Web Docs、web.dev、Chrome DevTools 文档
- 本模块后续按需补充具体主题。
```

- [ ] **Step 6.3: 写 02-language/README.md**

Write to `note/12.front-end/02-language/README.md`:

```markdown
# 02 · 语言

> 现代前端的两门核心语言:**JavaScript**(浏览器原生)与 **TypeScript**(类型工程的事实标准)。State of JS 2025 显示 85%+ 新项目默认使用 TS。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| JavaScript ES2024-2026 | ⏳ 待补 | Pipeline、Records & Tuples、Temporal、Decorators、Iterator helpers、`using` 声明 |
| TypeScript 5 工程实践 | ⏳ 待补 | tsconfig 全配置、项目引用(Project References)、增量构建、性能优化 |
| 类型体操 | ⏳ 待补 | 条件类型、映射类型、模板字面量、类型推导极限 |
| 运行时:Node / Deno / Bun | ⏳ 待补 | 三者生态、性能、API 兼容性对比 |

---

## 与其他模块的关系

- **上游**:依赖 [`01 基础`](../01-foundation/README.md) 的浏览器执行环境
- **下游**:为 [`03 框架`](../03-frameworks/README.md)、[`04 工程化`](../04-engineering/README.md) 提供语言底座

---

## 学习建议

- JS/TS 同步学:语法层 JS 优先,工程层 TS 优先
- 推荐参考:TypeScript Handbook、TC39 Proposals 仓库、Type Challenges
- 本模块后续按需补充具体主题。
```

- [ ] **Step 6.4: 写 04-engineering/README.md**

Write to `note/12.front-end/04-engineering/README.md`:

```markdown
# 04 · 工程化

> 从「能跑」到「能可靠地交付」之间的全部工具链:构建、依赖、Monorepo、测试、Lint。State of JS 2025 显示 Vite 使用率 78%+,Webpack 进入维护期。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| 构建工具 | ⏳ 待补 | Vite 7 / Webpack / Turbopack / Rspack / esbuild 对比、何时用哪个 |
| 包管理器 | ⏳ 待补 | npm / yarn / pnpm / Bun 安装速度、磁盘占用、工作空间能力 |
| Monorepo | ⏳ 待补 | Turborepo / Nx / Lerna(与 [`05.tools/monorepo/`](../../05.tools/monorepo/README.md) 互补) |
| 测试 | ⏳ 待补 | Vitest / Playwright / Testing Library / MSW、单元 vs 组件 vs E2E |
| Lint & Format | ⏳ 待补 | ESLint 9 Flat Config、Biome、Oxlint、Prettier、Husky + lint-staged |
| CI / CD | ⏳ 待补 | 前端独有的部署模型、Preview Environment、Edge Runtime |

---

## 与其他模块的关系

- **上游**:依赖 [`02 语言`](../02-language/README.md) 的 TypeScript 配置
- **横向**:与 [`05.tools/monorepo/`](../../05.tools/monorepo/README.md) 互补(本模块前端视角、tools/monorepo 通用视角)
- **下游**:为 [`06 性能`](../06-performance/README.md) 提供构建期优化能力(Tree Shaking / Code Splitting)

---

## 学习建议

- 推荐顺序:构建工具 → 包管理器 → 测试 → Lint → Monorepo → CI/CD
- 本模块后续按需补充具体主题。
```

- [ ] **Step 6.5: 写 05-architecture/README.md(模块索引)**

Write to `note/12.front-end/05-architecture/README.md`:

```markdown
# 05 · 架构

> 前端"在大",架构问题随之出现:多页面如何渲染、多团队如何拆分、多端如何聚合数据、状态如何流动。本模块按"渲染—拆分—聚合—状态—路由"组织。

---

## 本模块已有

| 主题 | 文档 | 一句话定位 |
|------|------|-----------|
| ✓ 微前端 | [`micro-frontend/`](micro-frontend/README.md) | 大型前端按业务模块拆分、独立部署、统一聚合 |
| ✓ Web Components | [`web-components/`](web-components/README.md) | 浏览器原生组件标准,跨框架可复用 |
| ✓ BFF(Backend For Frontend) | [`bff/`](bff/README.md) | 为前端定制的后端层,解决聚合/裁剪/鉴权问题 |

## 本模块待补

| 主题 | 状态 | 说明 |
|------|------|------|
| 渲染模式全景 | ⏳ 待补 | CSR / SSR / SSG / ISR / RSC / Islands / Streaming 6+ 种模式横向对比 |
| 状态管理 | ⏳ 待补 | Redux Toolkit / Zustand / Jotai / Pinia / Signal 范式与选型 |
| 路由 | ⏳ 待补 | React Router 7 / TanStack Router / Vue Router、文件路由 vs 配置路由 |
| 设计系统 / 组件库 | ⏳ 待补 | Material / Ant Design / Shadcn / Radix Primitives 的取舍 |

---

## 与其他模块的关系

- **上游**:依赖 [`03 框架`](../03-frameworks/README.md) 的具体框架能力
- **横向**:渲染模式与 [`06 性能`](../06-performance/README.md) 紧密相关
- **下游**:本模块的架构选择直接影响 [`08 跨端`](../08-cross-platform/README.md) 的实现成本

---

## 与全仓的交叉引用

- [`04.system-design/01-foundation/system-design-basics/microservices/`](../../04.system-design/01-foundation/system-design-basics/microservices/README.md) — 微服务设计(微前端的方法论来源)
- [`14.story/`](../../14.story/index.md) — 阿明餐厅多端篇、API 篇可参考
```

- [ ] **Step 6.6: 写 06-performance/README.md**

Write to `note/12.front-end/06-performance/README.md`:

```markdown
# 06 · 性能

> Core Web Vitals 直接影响搜索排名、转化率与留存。本模块聚焦"可度量、可优化、可监控"的前端性能工程。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| Core Web Vitals | ⏳ 待补 | LCP / INP(2024 起替代 FID)/ CLS 三大指标的定义、阈值、优化路径 |
| Lighthouse 实战 | ⏳ 待补 | 5 大类评分项详解、CI 集成、Lighthouse CI |
| 运行时性能 | ⏳ 待补 | 虚拟化(react-window/vue-virtual-scroller)、Web Worker、OffscreenCanvas |
| 资源优化 | ⏳ 待补 | 图片(AVIF/WebP/响应式)、字体子集化、HTTP 缓存策略、CDN |
| 前端监控 | ⏳ 待补 | Sentry / RUM(Real User Monitoring)/ 自建埋点、错误归因 |

---

## 与其他模块的关系

- **上游**:依赖 [`01 基础`](../01-foundation/README.md) 的浏览器渲染原理
- **依赖**:[`05 架构`](../05-architecture/README.md) 的渲染模式选择(SSR/Islands 直接影响 LCP)
- **依赖**:[`04 工程化`](../04-engineering/README.md) 的构建优化(Tree Shaking / Code Splitting)

---

## 学习建议

- 顺序:CWV(知道度量什么)→ Lighthouse(知道怎么度量)→ 运行时/资源(知道怎么优化)→ 监控(知道线上效果)
- 推荐参考:web.dev/vitals、Chrome DevTools Performance 面板、PageSpeed Insights
- 本模块后续按需补充具体主题。
```

- [ ] **Step 6.7: 写 07-security/README.md(模块索引)**

Write to `note/12.front-end/07-security/README.md`:

```markdown
# 07 · 安全

> 前端是攻击面的最前线。本模块涵盖浏览器侧的安全机制(同源/CORS/CSP)、会话存储选型、以及供应链安全。

---

## 本模块已有

| 主题 | 文档 | 一句话定位 |
|------|------|-----------|
| ✓ CORS 跨域 | [`cors/`](cors/README.md) | 同源策略、预检请求、Spring 服务端配置(已修订至 Spring 6 兼容写法) |
| ✓ Session 存储选型 | [`sessions/`](sessions/README.md) | Cookies vs LocalStorage,从安全角度看会话 Token 该放哪 |

## 本模块待补

| 主题 | 状态 | 说明 |
|------|------|------|
| XSS / CSRF / CSP / SRI | ⏳ 待补 | 四大经典威胁与防护:CSP3 nonce/strict-dynamic、SRI 子资源完整性 |
| 依赖供应链安全 | ⏳ 待补 | SBOM、npm 投毒案例复盘、Socket.dev、Snyk、Dependabot |
| Clickjacking & Postmessage | ⏳ 待补 | iframe 钳制、X-Frame-Options 与 CSP frame-ancestors、跨窗口通信防护 |
| 隐私与合规 | ⏳ 待补 | 第三方 Cookie 退场、CHIPS、隐私沙盒、GDPR/CCPA 对前端的影响 |

---

## 与其他模块的关系

- **上游**:依赖 [`01 基础`](../01-foundation/README.md) 的同源策略
- **横向**:与 [`04.system-design/05-security/`](../../04.system-design/05-security/README.md) 共享 JWT、OAuth2、API 安全等通用安全知识(本模块只覆盖"浏览器侧"特有部分)

---

## 与全仓的交叉引用

- [`04.system-design/05-security/access-control/`](../../04.system-design/05-security/access-control/README.md) — 6 大权限模型(DAC/MAC/RBAC/ABAC/ReBAC/混合)
- [`13.split-hairs/12.front-end/storage/`](../../13.split-hairs/12.front-end/storage/README.md) — 前端存储 4 种方式速查表(与 `sessions/` 互补)
```

- [ ] **Step 6.8: 写 08-cross-platform/README.md**

Write to `note/12.front-end/08-cross-platform/README.md`:

```markdown
# 08 · 跨端

> Write once, run anywhere 30 年未真正达成,但工程妥协的选项越来越多。本模块覆盖移动、桌面、小程序、PWA 4 个方向的主流方案。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| 移动端 | ⏳ 待补 | React Native(0.76 新架构)/ Flutter / 鸿蒙 ArkUI 的取舍 |
| 桌面端 | ⏳ 待补 | Electron / Tauri 2 — 内存占用、包体积、Rust 后端的代价 |
| 小程序 | ⏳ 待补 | 微信原生 / Taro / uni-app / Remax — 多端代码复用方案 |
| PWA | ⏳ 待补 | Service Worker、Web App Manifest、Push API、离线策略 |
| Hybrid / WebView | ⏳ 待补 | JSBridge 设计、性能优化、与原生的接缝 |

---

## 与其他模块的关系

- **上游**:依赖 [`03 框架`](../03-frameworks/README.md) 的具体框架(React/Vue 是多数跨端方案的基础)
- **横向**:[`05 架构`](../05-architecture/README.md) 的状态/路由选择影响跨端复用率

---

## 与全仓的交叉引用

- [`14.story/`](../../14.story/index.md) — 阿明餐厅多端篇

---

## 学习建议

- 选择路径取决于团队技术栈:RN-React 团队 / Flutter-独立栈 / 鸿蒙-国内场景
- 本模块后续按需补充具体主题。
```

- [ ] **Step 6.9: 写 09-frontend-and-ai/README.md**

Write to `note/12.front-end/09-frontend-and-ai/README.md`:

````markdown
# 09 · 前端与 AI

> 2026 年前端工程发生的最大结构性变化:AI 进入 IDE、UI 流式渲染、Vibe Coding 成为新工作流。本模块是「前端」与 [`11.ai`](../../11.ai/README.md) 的交叉地带。

---

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| AI SDK | ⏳ 待补 | Vercel AI SDK 5、Mastra、LangChain.js — 在前端/Node 调用 LLM 的工程化框架 |
| AI Native UI | ⏳ 待补 | 流式渲染(Streaming UI)、生成式 UI(Generative UI)、工具调用可视化 |
| AI IDE | ⏳ 待补 | Cursor、Windsurf、Claude Code、Continue、Zed — 工作流对比与选型 |
| Vibe Coding | ⏳ 待补 | 用自然语言驱动开发的范式:适用边界、协作模型、风险 |
| 前端 + Agent | ⏳ 待补 | Agentic UI、人在回路(HITL)、Tool UI、MCP 客户端在浏览器中的形态 |

---

## 与其他模块的关系

- **上游**:依赖 [`11.ai`](../../11.ai/README.md) 的 LLM 基础、Agent 架构、MCP/A2A 协议
- **横向**:本模块的 IDE 工具直接改变 [`04 工程化`](../04-engineering/README.md) 的工作方式

---

## 与全仓的交叉引用

- [`11.ai/03-engineering/`](../../11.ai/03-engineering/README.md) — AI 工程实践(本模块的上游)
- [`14.story/11-ai-learning-paradox.md`](../../14.story/11-ai-learning-paradox.md) — AI 时代的学习悖论(与「Vibe Coding」的反思对照)
- [`14.story/`](../../14.story/index.md) — 续集 2-12 · AI 时代 11 篇

---

## 学习建议

- 建议顺序:AI SDK(怎么调)→ AI Native UI(怎么展示)→ AI IDE(怎么开发)→ Vibe Coding(怎么协作)
- 本模块后续按需补充具体主题。
````

- [ ] **Step 6.10: 校验 9 个新 README 已创建**

Run:
```bash
ls note/12.front-end/README.md note/12.front-end/0?-*/README.md
```
Expected: 列出 10 个文件(顶层 README + 9 模块 README,包括迁入的 03-frameworks)

- [ ] **Step 6.11: Commit**

Run:
```bash
git add note/12.front-end/README.md note/12.front-end/01-foundation/ note/12.front-end/02-language/ note/12.front-end/04-engineering/ note/12.front-end/05-architecture/README.md note/12.front-end/06-performance/ note/12.front-end/07-security/README.md note/12.front-end/08-cross-platform/ note/12.front-end/09-frontend-and-ai/
git commit -m "docs(note/12.front-end): 新建顶层 README + 8 个模块 README

- 顶层 README:9 模块导航表 + ASCII 知识脉络图 + 4 条学习路线 + 交叉引用
- 6 个占位模块 README(01/02/04/06/08/09)含待补主题清单
- 2 个模块索引 README(05/07)含本模块已有 + 待补主题
- 全部对齐 11.ai/04.system-design 的目录风格

详见 docs/superpowers/specs/2026-06-16-frontend-restructure-design.md

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: `9 files changed, NN insertions(+)`

---

## Task 7: 更新顶层 note/README.md

**Files:**
- Modify: `note/README.md` 第 170-174 行(原 # 十二、前端 块)
- Modify: `note/README.md` 第 215-218 行(原 ## 12.前端 在 # 十三、咬文嚼字 下)

- [ ] **Step 7.1: 替换 # 十二、前端 整块**

Edit `note/README.md`:

old_string:
```
# 十二、前端
## [前端框架](12.font-end/frameworks/README.md)
## [CORS 跨域](12.font-end/cors/README.md)
## [微前端](12.font-end/micro-frontend/README.md)
## [Web Components](12.font-end/web-components/README.md)
```

new_string:
```
# 十二、[前端](12.front-end/README.md)

> 现代前端工程的知识地图——从浏览器原理到 AI 协同开发。9 个分层模块,覆盖基础 / 语言 / 框架 / 工程 / 架构 / 性能 / 安全 / 跨端 / AI。

## 目录导航

| 序号 | 主题 | 核心内容 |
|------|------|---------|
| 01 | [基础](12.front-end/01-foundation/README.md) | 浏览器原理、HTML 语义化、CSS 工程化、Web 标准 ⏳ |
| 02 | [语言](12.front-end/02-language/README.md) | JavaScript ES2024-2026、TypeScript 5 工程实践 ⏳ |
| 03 | [框架](12.front-end/03-frameworks/README.md) | 2026 框架格局(State of JS 2025)、React/Vue/Svelte/元框架/选型 ✓ |
| 04 | [工程化](12.front-end/04-engineering/README.md) | Vite/Webpack/Turbopack、包管理、Monorepo、测试、Lint ⏳ |
| 05 | [架构](12.front-end/05-architecture/README.md) | 渲染模式、[微前端](12.front-end/05-architecture/micro-frontend/README.md)、[Web Components](12.front-end/05-architecture/web-components/README.md)、[BFF](12.front-end/05-architecture/bff/README.md)、状态、路由 ✓ |
| 06 | [性能](12.front-end/06-performance/README.md) | Core Web Vitals、Lighthouse、Web Worker、前端监控 ⏳ |
| 07 | [安全](12.front-end/07-security/README.md) | XSS/CSRF/CSP/SRI、[CORS](12.front-end/07-security/cors/README.md)、[Session 存储](12.front-end/07-security/sessions/README.md)、依赖供应链 ✓ |
| 08 | [跨端](12.front-end/08-cross-platform/README.md) | React Native/Flutter/鸿蒙、Electron/Tauri、小程序、PWA ⏳ |
| 09 | [前端与 AI](12.front-end/09-frontend-and-ai/README.md) | AI SDK、AI Native UI、AI IDE、Vibe Coding ⏳ |

> 标注 ✓ 为已有内容,⏳ 为占位待补
```

- [ ] **Step 7.2: 修正 # 十三、咬文嚼字 下的链接**

Edit 同一文件:

old_string:
```
## 12.前端
### [HTTP 请求中的 GET 和 POST](13.split-hairs/12.font-end/get-and-post/README.md)
### [网页端接受推送消息的方式](13.split-hairs/12.font-end/message/README.md)
### [前端存储方式](13.split-hairs/12.font-end/storage/README.md)
```

new_string:
```
## 12.前端
### [HTTP 请求中的 GET 和 POST](13.split-hairs/12.front-end/get-and-post/README.md)
### [网页端接受推送消息的方式](13.split-hairs/12.front-end/message/README.md)
### [前端存储方式](13.split-hairs/12.front-end/storage/README.md)
```

- [ ] **Step 7.3: 校验顶层 README 不再有任何 font-end**

Run:
```bash
grep -n "font-end" note/README.md
```
Expected: 无输出

Run:
```bash
grep -cn "front-end" note/README.md
```
Expected: 至少 14 行命中

- [ ] **Step 7.4: Commit**

Run:
```bash
git add note/README.md
git commit -m "docs(note/README): 12.前端 章节扩为 9 模块导航表

- 第 170-174 行的扁平 4 链接,替换为 9 模块导航表
  + 一句话定位、✓/⏳ 状态标注、嵌套链接到子目录
- 第 216-218 行 13.split-hairs/12.font-end 链接同步改为 12.front-end

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
Expected: `1 file changed`

---

## Task 8: 全仓最终校验

**Files:** 无修改,仅校验

- [ ] **Step 8.1: 全仓 grep `12.font-end` 应只剩 spec/plan 文档自身**

Run:
```bash
cd "D:/developer/IdeaProjects/wb04307201"
grep -rln "12.font-end" --include="*.md" .
```
Expected: **只**命中以下 2 个文件(spec 与 plan 文档需要引用旧路径作为历史说明):
- `docs/superpowers/specs/2026-06-16-frontend-restructure-design.md`
- `docs/superpowers/plans/2026-06-16-frontend-restructure.md`

如果在 `note/` 下命中任何 `12.font-end`,说明遗漏,需手工修复。

校验 note 子树下确实为 0 命中:
```bash
grep -rln "12.font-end" --include="*.md" note/
```
Expected: 无输出

- [ ] **Step 8.2: 校验目录结构与 spec §3 一致**

Run:
```bash
find note/12.front-end -type f | sort
```
Expected: 输出以下 17 个文件:
```
note/12.front-end/01-foundation/README.md
note/12.front-end/02-language/README.md
note/12.front-end/03-frameworks/README.md
note/12.front-end/04-engineering/README.md
note/12.front-end/05-architecture/README.md
note/12.front-end/05-architecture/bff/README.md
note/12.front-end/05-architecture/micro-frontend/README.md
note/12.front-end/05-architecture/web-components/README.md
note/12.front-end/06-performance/README.md
note/12.front-end/07-security/README.md
note/12.front-end/07-security/cors/README.md
note/12.front-end/07-security/cors/img.png
note/12.front-end/07-security/cors/img_1.png
note/12.front-end/07-security/sessions/README.md
note/12.front-end/08-cross-platform/README.md
note/12.front-end/09-frontend-and-ai/README.md
note/12.front-end/README.md
```

- [ ] **Step 8.3: 校验图片可点击**

Run:
```bash
grep -n "img.png\|img_1.png" note/12.front-end/07-security/cors/README.md
```
Expected: 2 行命中(对应 `![img.png](img.png)` 与 `![img_1.png](img_1.png)`),证明图片引用未失效

- [ ] **Step 8.4: 校验 CORS 修订全部就位**

Run:
```bash
grep -cn "WebMvcConfigurer\b" note/12.front-end/07-security/cors/README.md
```
Expected: 至少 2 次命中(import 行 + class 声明行)

Run:
```bash
grep -n "WebMvcConfigurerAdapter" note/12.front-end/07-security/cors/README.md
```
Expected: 无输出

- [ ] **Step 8.5: 校验 Web Components 修订全部就位**

Run:
```bash
grep -n "三大核心" note/12.front-end/05-architecture/web-components/README.md
```
Expected: 1 行命中

Run:
```bash
grep -n "四大核心" note/12.front-end/05-architecture/web-components/README.md
```
Expected: 无输出

- [ ] **Step 8.6: 查看 git log 确认 5 commit 全部就位**

Run:
```bash
git log --oneline -7
```
Expected: 最新 6 个 commit 类似(顺序):
```
xxxxxxx docs(note/README): 12.前端 章节扩为 9 模块导航表
xxxxxxx docs(note/12.front-end): 新建顶层 README + 8 个模块 README
xxxxxxx docs(note/12.front-end/sessions): 顶部加与 split-hairs/storage 的关系说明
xxxxxxx fix(note/12.front-end/web-components): HTML Imports 从四大核心移出
xxxxxxx fix(note/12.front-end/cors): 修订 3 处过时与错漏
xxxxxxx refactor(note/12.front-end): 6 个子目录迁入 9 模块分层结构
xxxxxxx refactor(note): 12.font-end 改名为 12.front-end 修正拼写
```

- [ ] **Step 8.7: 若有任何校验失败,在本任务下记录后回到对应 Task 修复**

无失败则收工。

---

## 验收清单(对照 spec §11)

完成所有 Task 后,逐项 ☑️:

- [ ] `note/12.front-end/README.md` 存在,符合 spec §4 模板,含 9 模块导航表
- [ ] 9 个模块 README 全部就位:01/02/04/06/08/09 为占位、05/07 为模块索引、03 为迁入(原 frameworks)
- [ ] 5 个子目录 README 全部迁入(`05-architecture/{micro-frontend,web-components,bff}`、`07-security/{cors,sessions}`),内容无丢失
- [ ] CORS 3 处修订全部落实(代码语言 / Adapter 替换 / 5 处小标题去重)
- [ ] Web Components "四大核心"修订为"三大核心 + 一项已废弃"
- [ ] `note/README.md` 第 170-174 行更新为 9 模块导航表;第 216-218 行链接更新
- [ ] `note/13.split-hairs/12.font-end` 改名为 `12.front-end`
- [ ] `grep -r "12.font-end" .` 在仓库下应返回 0 行(本 spec 文档本身除外)
- [ ] 所有图片(`cors/img.png`、`cors/img_1.png`)随目录迁移,链接仍可点击
