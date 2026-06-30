<!--
question:
  id: 09.front-end-css-render-blocking
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [09.front-end, css, render]
-->

# CSS 渲染阻塞：把 CSS 放底部为什么白屏更长

> 一个经典的"看似合理实则翻车"陷阱题。考察的不是 CSS 本身，而是 **渲染阻塞（Render Blocking）的触发时机** 和 **首屏绘制（First Paint）的前置条件**。

## 引子：CSS 放 `<body>` 底部，首屏竟然更慢了

```text
工程师小白：听说 CSS 会阻塞渲染，我把 CSS 放 body 底部，应该能先渲染顶部内容？
上线后看到真实数据：

| 位置 | 首屏绘制（FCP） |
|------|---------------|
| `<head>` 内（标准） | 1.2 秒 |
| `<body>` 底部 | 2.8 秒（慢了 2 倍）|
```

**真相**：

- 浏览器遇到 `<link rel="stylesheet">` 时**暂停 HTML 解析**，下载并合并 CSS 后才继续
- CSS 在 body 底部，前面的图片资源已经按"无样式"的方式渲染了
- CSS 加载完要 **重新渲染整个页面** → 之前画的全部白费

**正解**：CSS 放 `<head>` + **关键 CSS 内联** + 非关键 CSS 异步加载。

## 一、核心结论（TL;DR）

| 问题 | 答案 |
|------|------|
| CSS 放 `<body>` 底部能让首屏更快？ | **不会，反而更慢** |
| 为什么？ | 浏览器在遇到 CSS link 时**仍然 render-blocking**，且之前下载的图片资源全部白费 |
| 真正的优化？ | **内联关键 CSS** + `media="print"` 异步加载 + 图片 `loading="lazy"` |

> 一句话：**CSS 文件大小不是问题，"CSS 在哪被解析"才是关键 —— CSS 在 body 底部仍然是 render-blocking 资源。**

---

## 二、浏览器渲染流水线（3 分钟版本）

```
HTML 字节流 → 字符流 → Token → 节点 → DOM Tree ─┐
                                                 ├─→ Render Tree → Layout → Paint → Composite → 屏幕
CSS 字节流 → CSSOM Tree ─────────────────────────┘
```

**First Paint 的前置条件**：DOM + CSSOM 都必须就绪，缺一不可。

---

## 三、CSS 位置的三种姿势

### 姿势 1：CSS 放在 `<head>`（✅ 标准做法）

```html
<head>
  <link rel="stylesheet" href="styles.css">
</head>
```

- 浏览器解析到 `<link>` → 暂停 HTML 解析 → 下载 CSS → 构建 CSSOM → 继续
- CSSOM 就绪 → 构建 Render Tree → 首次绘制（带样式）
- **白屏时间 ≈ 一次 RTT + CSS 下载 + CSSOM 构建**

### 姿势 2：CSS 放在 `<body>` 底部（❌ 常见误区）

```html
<body>
  ...首屏图片...
  <link rel="stylesheet" href="styles.css">   <!-- ❌ 这样写 -->
</body>
```

- 浏览器解析 HTML 不停顿 → 下载图片 → 撞到 CSS link
- **此时仍然 render-blocking**（HTML5 规范）→ 必须停下来下载 CSS
- **CSS 之前的图片资源被白白下载**，但用户没看到
- 加载 CSS → CSSOM → 首次绘制 → 重排重绘之前渲染的节点（FOUC）

### 姿势 3：关键 CSS 内联（✅ 推荐）

```html
<head>
  <style>/* 首屏关键 CSS 直接内联 */</style>
  <link rel="stylesheet" href="non-critical.css" 
        media="print" 
        onload="this.media='all'">
</head>
```

---

## 四、为什么放底部反而更慢（4 个原因）

1. **CSS link 在 body 里仍然是 render-blocking**
2. **浪费了首屏图片的下载带宽**：CSS 之前的资源都白拉
3. **FOUC（Flash of Unstyled Content）**：用户先看到无样式页面再闪一下，感知更差
4. **额外的重排重绘**：CSSOM 加载完成后，之前渲染的无样式 DOM 全部需要重新计算样式

---

## 五、真正正确的 6 种优化姿势

### 1. 内联关键 CSS（Critical CSS）

```html
<head>
  <style>
    /* 只有首屏需要的 CSS，压缩到几 KB */
    body { margin: 0; font-family: sans-serif; }
    .hero { ... }
  </style>
</head>
```

### 2. 异步加载非关键 CSS

```html
<link rel="stylesheet" href="big.css" 
      media="print" 
      onload="this.media='all'">
```

原理：先以 `media="print"` 加载（不阻塞渲染），onload 时切回 `media="all"` 立即生效。

### 3. 预加载 CSS

```html
<link rel="preload" href="styles.css" as="style" onload="this.rel='stylesheet'">
```

### 4. 图片懒加载

```html
<img src="placeholder.jpg" 
     data-src="hero.jpg" 
     loading="lazy" 
     decoding="async">
```

### 5. 图片预加载（LCP 优化）

```html
<link rel="preload" href="hero.jpg" as="image">
```

### 6. 现代图片格式

```html
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="...">
</picture>
```

---

## 六、面试陷阱

### 陷阱 1：以为 CSS 放底部能"先渲染 HTML 再补样式"

- **真相**：浏览器不会"先渲染无样式版本等样式补上" —— CSS link 一旦遇到就阻塞渲染。

### 陷阱 2：以为 `media="print"` 能减少下载体积

- **真相**：`media="print"` 只是不阻塞渲染，文件**仍然要下载**。

### 陷阱 3：H5 活动页所有图片都 `loading="lazy"`

- **真相**：首屏图片（LCP）**不能懒加载**，否则会延迟 LCP 触发。

---

## 七、面试话术（90 秒版本）

> CSS 放底部反而更慢，是因为浏览器遇到 CSS link 时**仍然会 render-blocking**，并不是"先渲染 HTML 再补样式"。这会导致：CSS 之前的图片资源被白白下载、CSSOM 构建后还要重排重绘、用户看到 FOUC 闪烁。
>
> 真正的优化是：把首屏关键 CSS 内联到 `<head>`、非关键 CSS 用 `media="print" onload="this.media='all'"` 异步加载、首屏图片用 `<link rel="preload" as="image">` 预加载、非首屏图片用 `loading="lazy"` 懒加载、格式用 WebP/AVIF。

---

## 八、相关章节

- 同栏目：[`reflow-repaint`](../reflow-repaint/README.md) — 回流与重绘
- 同栏目：[`script-async-defer`](../script-async-defer/README.md) — script 标签加载方式
- 同栏目：[`lazy-load-preload`](../lazy-load-preload/README.md) — 懒加载与预加载
- 同栏目：[`from-url-to-page`](../from-url-to-page/README.md) — URL 输入到页面展示全链路
- 主模块：[`09.front-end/06-performance`](../../../../09.front-end/06-performance/README.md) — 前端性能优化

---

> 📅 2026-06-28 · 咬文嚼字 · 浏览器机制 · ⭐⭐⭐⭐（高频面试 + 实战必会）