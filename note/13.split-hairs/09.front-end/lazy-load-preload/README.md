# 懒加载 vs 预加载：4 大资源提示的正确姿势

> 区分不清「懒加载」和「预加载」是前端工程师的常见痛点。考察点不是"loading='lazy' 怎么写"，而是 **4 种资源提示（preload/prefetch/preconnect/dns-prefetch）的精确含义与适用场景**。

## 引子：为什么首页图片总"突然冒出"一卡一卡的？

```text
电商首页打开，前 3 张图秒出，第 4 张开始每滚一下都"冒"出新图。
用户反馈：滚动很卡。
```

**真相**：默认浏览器**等到滚动到图片位置才下载**（lazy by default）。

但 LCP（Largest Contentful Paint）的"最大图"——首屏那张大 banner：

- 如果用 lazy = 用户看到的是**白屏 → 然后图片突然出现**
- 正确做法：banner 用 **preload**（高优先级立即加载）
- 下面看不到的图片用 **loading="lazy"**（默认懒加载）

**preload vs prefetch vs preconnect vs dns-prefetch** —— 4 种提示，4 个用途，全混就翻车。

## 一、核心结论（TL;DR）

| 类型 | 加载时机 | 优先级 | 适用场景 |
|------|---------|--------|---------|
| **懒加载** | 进入视口才加载 | 低 | 非首屏图片、长列表 |
| **preload** | 立即加载（高优先级） | 高 | 首屏关键资源（LCP） |
| **prefetch** | 浏览器空闲时加载 | 最低 | 下一页资源 |
| **preconnect** | 提前建立 TCP/TLS 连接 | — | 跨域 CDN |
| **dns-prefetch** | 提前 DNS 解析 | — | 跨域第三方 |

> 一句话：**懒加载是"按需加载"，预加载是"提前加载"；preload 用于当前页面关键资源，prefetch 用于下一个页面可能用到的资源。**

---

## 二、懒加载（Lazy Loading）

### 图片懒加载

```html
<!-- 原生懒加载（现代浏览器都支持） -->
<img src="placeholder.jpg" 
     data-src="hero.jpg" 
     loading="lazy" 
     decoding="async">
```

### 兼容性兜底（IntersectionObserver）

```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
```

### 路由懒加载

```js
// React Router
const Home = React.lazy(() => import('./pages/Home'));
const About = React.lazy(() => import('./pages/About'));

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/about" element={<About />} />
  </Routes>
</Suspense>
```

---

## 三、预加载（Preloading）

### preload 当前页面关键资源

```html
<!-- 预加载首屏大图（LCP 优化） -->
<link rel="preload" href="hero.jpg" as="image">

<!-- 预加载关键字体 -->
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>

<!-- 预加载关键 CSS -->
<link rel="preload" href="critical.css" as="style">
```

### prefetch 下一个页面资源

```html
<!-- 用户可能访问的下一页资源 -->
<link rel="prefetch" href="/next-page.js">
<link rel="prefetch" href="/next-page.css">
```

> **关键区别**：preload 在当前页面立即加载，prefetch 在浏览器空闲时才加载

---

## 四、四大资源提示深度对比

### 1. preload（预加载）

```html
<link rel="preload" href="hero.jpg" as="image">
```

- **当前页面** 立即加载
- 高优先级
- 必须指定 `as`（image/style/script/font）
- 加载后**不会自动应用**，需要配合 `<link rel="stylesheet">` 等

### 2. prefetch（预取）

```html
<link rel="prefetch" href="next-page.js">
```

- **下一个页面** 浏览器空闲时加载
- 最低优先级
- 适合：路由跳转后的下一页、用户可能点的链接

### 3. preconnect（预连接）

```html
<link rel="preconnect" href="https://cdn.example.com">
```

- 提前建立 TCP 连接 + TLS 握手
- 节省 **~100-300ms**（DNS + TCP + TLS）
- 适合：跨域 CDN、第三方资源

### 4. dns-prefetch（DNS 预解析）

```html
<link rel="dns-prefetch" href="//cdn.example.com">
```

- 只提前做 DNS 解析（不建立连接）
- 比 preconnect 轻量
- 适合：大量第三方资源（Google Analytics、广告 SDK）

### 对比总结

| 资源提示 | 触发时机 | 节省时间 | 适用对象 |
|---------|---------|---------|---------|
| `preload` | 立即加载 | 提前加载时间 | 当前页面关键资源 |
| `prefetch` | 浏览器空闲 | 提前加载时间 | 下一页资源 |
| `preconnect` | 立即建连 | ~100-300ms | 跨域主机 |
| `dns-prefetch` | 立即 DNS | ~20-120ms | 跨域主机 |

---

## 五、H5 活动页实战优化

```html
<head>
  <!-- 1. 预连接 CDN -->
  <link rel="preconnect" href="https://cdn.example.com">
  <link rel="dns-prefetch" href="//cdn.example.com">
  
  <!-- 2. 预加载关键 CSS -->
  <link rel="preload" href="critical.css" as="style">
  
  <!-- 3. 预加载首屏图片（LCP） -->
  <link rel="preload" href="hero.webp" as="image">
  
  <!-- 4. 异步加载非关键 CSS -->
  <link rel="stylesheet" href="big.css" 
        media="print" 
        onload="this.media='all'">
  
  <!-- 5. 预取下一页资源（如果有） -->
  <link rel="prefetch" href="next-page.html">
</head>

<body>
  <!-- 首屏图片：正常 src + fetchpriority="high" -->
  <img src="hero.webp" fetchpriority="high" alt="...">
  
  <!-- 非首屏图片：懒加载 -->
  <img src="placeholder.jpg" 
       data-src="thumb1.webp" 
       loading="lazy" 
       alt="...">
</body>
```

---

## 六、面试陷阱

### 陷阱 1：preload 越多越好

- **真相**：preload 会**抢占带宽和资源**（字体、图片、脚本），过多反而拖慢首屏
- **最佳实践**：只 preload 真正首屏关键的 1-3 个资源

### 陷阱 2：preload 自动应用

- **真相**：preload 只负责**加载**，不负责**应用**。预加载 CSS 后仍需 `<link rel="stylesheet">` 引用

### 陷阱 3：所有图片都用 `loading="lazy"`

- **真相**：**首屏图片（LCP 元素）不能懒加载**，否则会延迟 LCP 触发
- **正确做法**：首屏图片正常 `src`，加 `fetchpriority="high"`

### 陷阱 4：preconnect 用太多

- **真相**：浏览器对每个 origin 同时打开的 TCP 连接数有限（Chrome 默认 6），过多 preconnect 会浪费连接

---

## 七、面试话术（90 秒版本）

> 懒加载是"按需加载"，进入视口或需要时才加载；预加载是"提前加载"，分 preload 和 prefetch。
>
> - `preload`：当前页面立即加载，高优先级，必须指定 `as`（image/style/font/script）
> - `prefetch`：浏览器空闲时加载下一个页面可能用到的资源
> - `preconnect`：提前建立 TCP/TLS 连接，节省 ~100-300ms
> - `dns-prefetch`：只做 DNS 解析，更轻量
>
> H5 活动页实战：预连接 CDN、preload 首屏图片（LCP）、非关键 CSS 用 `media="print"` 异步加载、非首屏图片用 `loading="lazy"`。

---

## 八、相关章节

- 同栏目：[`css-render-blocking`](../css-render-blocking/README.md) — CSS 渲染阻塞
- 同栏目：[`reflow-repaint`](../reflow-repaint/README.md) — 回流与重绘
- 同栏目：[`script-async-defer`](../script-async-defer/README.md) — script 标签加载方式
- 同栏目：[`from-url-to-page`](../from-url-to-page/README.md) — URL 输入到页面展示
- 主模块：[`09.front-end/06-performance`](../../../../09.front-end/06-performance/README.md) — 前端性能优化

---

> 📅 2026-06-28 · 咬文嚼字 · 浏览器机制 · ⭐⭐⭐⭐（高频面试 + 实战必会）