<!--
question:
  id: 09.front-end-script-async-defer
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [09.front-end, script, async]
-->

# script 标签的 async / defer：加载时机与 DOMContentLoaded

> 看似简单的 script 三种加载方式，90% 候选人说不清 **「加载时机」和「执行时机」的区别**，也说不清 **DOMContentLoaded 的触发条件**。

## 引子：为什么 `<script>` 放 body 底部以前是"铁律"？

```text
过去 10 年：把 <script> 放 </body> 前是铁律，因为浏览器会阻塞 HTML 解析。
2026 的现实：
- <script>：同步加载执行，阻塞 HTML 解析，阻塞 DOMContentLoaded
- <script async>：并行下载，下载完立即执行（可能中断 HTML 解析）
- <script defer>：并行下载，等 HTML 解析完才执行（保证顺序），DOMContentLoaded 前
```

**真相**：

- HTML 解析过程中遇到 `<script>` → **暂停**，下载、执行完才继续
- 这导致：即使在 HTML 末尾，浏览器也"卡"在那里执行 JS
- DOMContentLoaded：所有 defer + 同步 script 都执行完才触发

**正解**：

- 业务代码用 `defer`，保证顺序 + 不阻塞解析
- 第三方独立 SDK 用 `async`（如 GA）
- 永远不要把 `<script>` 放 `<head>` 里（除非用 defer/async）

## 一、核心结论（TL;DR）

| 方式 | 加载时机 | 执行时机 | 是否阻塞 DOMContentLoaded |
|------|---------|---------|--------------------------|
| 普通 `<script>` | 同步阻塞 | 立即执行 | ✅ 阻塞 |
| `<script async>` | 异步加载 | 加载完立即执行（可能中断 HTML 解析） | ❌ 不保证 |
| `<script defer>` | 异步加载 | DOM 解析完后、`DOMContentLoaded` 前执行 | ❌ 不阻塞 |

> 一句话：**`defer` 是最安全的"按顺序异步"，`async` 是"谁先下完谁先跑"，普通 script 则是"同步阻塞到底"。**

---

## 二、script 标签的 3 种加载方式详解

### 1. 普通 `<script>`（同步阻塞）

```html
<script src="a.js"></script>
<script src="b.js"></script>
```

- 浏览器**暂停 HTML 解析**，下载 a.js，执行 a.js，下载 b.js，执行 b.js
- 执行完才继续解析 HTML
- 执行顺序：a → b（保证）
- **会阻塞 DOMContentLoaded**

### 2. `<script async>`（异步加载 + 谁先到谁先跑）

```html
<script async src="a.js"></script>
<script async src="b.js"></script>
```

- 浏览器**不暂停 HTML 解析**，异步下载 a.js 和 b.js
- 谁先下载完谁先执行（**顺序不保证**）
- 执行时**会中断 HTML 解析**去执行脚本
- **适合**：埋点、独立脚本（如 Google Analytics）

### 3. `<script defer>`（异步加载 + DOM 解析完按顺序执行）

```html
<script defer src="a.js"></script>
<script defer src="b.js"></script>
```

- 浏览器**不暂停 HTML 解析**，异步下载
- DOM 解析完后、`DOMContentLoaded` 触发**之前**按顺序执行
- **保证顺序**：a → b
- **适合**：业务代码、需要操作 DOM 的脚本

---

## 三、加载 vs 执行时机图

```
HTML 解析 ──┬────────────────────────────────────────────┐
            │                                            │
普通 script │  [下载a][执行a][下载b][执行b]              │
            │                                            │
async       │  ─[下载a]─                 [执行a]         │
            │  ──[下载b]──[执行b]                        │
            │                                            │
defer       │  ─[下载a]─                                │
            │  ─[下载b]──                                │
            │                                  [执行a][执行b]
            │                                            │
DOMContentLoaded 触发点 ─────────────────────────────────┤
                                                          │
                                                          ▼
```

---

## 四、DOMContentLoaded vs load

| 事件 | 触发时机 |
|------|---------|
| `DOMContentLoaded` | HTML 解析完成 + 同步脚本执行完 + defer 脚本执行完 |
| `load` | 所有资源（图片、样式表、iframe）加载完成 |

```js
// DOMContentLoaded：DOM 树构建完成即可触发
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM ready');
});

// load：所有资源加载完成
window.addEventListener('load', () => {
  console.log('All resources loaded');
});
```

> ⚠️ **async 脚本不在 DOMContentLoaded 等待范围内**，可能在 DCL 之前或之后执行。

---

## 五、`<script type="module">` 的默认行为

ES Module 脚本**默认带 defer 行为**：

```html
<script type="module" src="a.js"></script>
```

- 异步加载
- DOM 解析完按顺序执行
- 等价于 `<script defer>`
- 额外特性：自动严格模式、CORS、scope 隔离

---

## 六、面试陷阱

### 陷阱 1：以为 `defer` 脚本一定在 `DOMContentLoaded` 前执行

- **真相**：标准上 `defer` 脚本在 DOM 解析完后执行，**早于** `DOMContentLoaded`，但 `async` 脚本可能在 `DOMContentLoaded` 之前或之后执行。

### 陷阱 2：内联脚本可以用 async/defer

```html
<!-- ❌ async/defer 只对外部脚本生效 -->
<script async>console.log('inline')</script>
```

- 内联脚本默认就是同步执行（阻塞），加 `async`/`defer` 被忽略。

### 陷阱 3：动态插入的 script 默认就是 async

```js
// 动态创建的 script 标签，默认 async = true
const script = document.createElement('script');
script.src = 'a.js';
document.body.appendChild(script);  // 默认异步加载
```

可以通过 `script.async = false` 关闭，恢复同步行为。

---

## 七、面试话术

### 30 秒版

> "三种加载方式：普通 `<script>` 同步阻塞 HTML 解析；`async` 下载不阻塞、下载完立即执行、顺序不保证；`defer` 下载不阻塞、按声明顺序在 DOMContentLoaded 前执行。业务代码用 `defer`（或 `type=module` 默认 defer），独立埋点用 `async`。"

### 90 秒版本

> 三种加载方式：普通 script 同步阻塞、`async` 异步加载但顺序不保证、`defer` 异步加载且按顺序在 DOMContentLoaded 前执行。
>
> - 普通 script 会中断 HTML 解析去下载和执行
> - async 加载完立即执行（可能中断解析），执行顺序按下载完成时间
> - defer 等 DOM 解析完后按声明顺序执行
>
> 关键区别：DOMContentLoaded 在 DOM 解析完成 + defer 脚本执行完后触发，**但不会等 async 脚本**。
>
> 现代推荐：业务代码用 `<script defer>` 或 `<script type="module">`（默认 defer），埋点/独立脚本用 `async`。

---

## 八、相关章节

- 同栏目：[`css-render-blocking`](../css-render-blocking/README.md) — CSS 渲染阻塞
- 同栏目：[`reflow-repaint`](../reflow-repaint/README.md) — 回流与重绘
- 同栏目：[`lazy-load-preload`](../lazy-load-preload/README.md) — 懒加载与预加载
- 同栏目：[`from-url-to-page`](../from-url-to-page/README.md) — URL 输入到页面展示
- 主模块：[`09.front-end/06-performance`](../../../09.front-end/06-performance/README.md) — 前端性能优化

---

> 📅 2026-06-28 · 咬文嚼字 · 浏览器机制 · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · script-async-defer](../README.md)
