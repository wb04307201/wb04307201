<!--
question:
  id: 09.front-end-reflow-repaint
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [09.front-end, reflow, repaint]
-->

# 回流与重绘：触发条件 + 性能优化

> 前端性能优化的"老八股"。考察点不是"什么是回流"，而是 **浏览器的渲染队列机制 + 如何避免强制同步布局（Layout Thrashing）**。

## 引子：循环读 offsetWidth，页面卡到主线程报红

```js
// ❌ 经典 Layout Thrashing
for (let i = 0; i < 1000; i++) {
  const w = el.offsetWidth;   // 触发强制 layout
  el.style.width = (w + 1) + 'px';
  // 立刻又 offsetWidth 一次...
}
```

打开 DevTools 看 **Performance**：黄色的 Forced Reflow 警告密密麻麻。

**真相**：浏览器渲染有"队列"机制，你读 layout 属性（offsetWidth / scrollTop）会**强制刷新队列**（因为你的代码需要的是"最新值"）。

高频读 + 高频写交错 = **Layout Thrashing**（强制同步布局）。

**正解**：

- 先把所有读 batch 起来（缓存到变量）
- 再统一写
- 用 `requestAnimationFrame` 把写操作推到下一帧

## 一、核心结论（TL;DR）

| 概念 | 含义 | 性能开销 |
|------|------|---------|
| 回流（Reflow / Layout） | 几何属性变化导致重新计算布局 | ⭐⭐⭐⭐⭐ |
| 重绘（Repaint） | 外观变化但不改变布局 | ⭐⭐⭐ |
| 合成（Composite） | 仅 transform / opacity 变化 | ⭐ 不触发回流 |

> 一句话：**回流一定触发重绘，重绘不一定触发回流；优先用 transform/opacity 走合成层，避开回流。**

---

## 二、什么是回流 / 重绘

### 渲染流水线

```
DOM + CSSOM → Render Tree → Layout（回流）→ Paint（重绘）→ Composite（合成）→ 屏幕
                                       ↑                ↑
                                  几何属性变化      外观属性变化
```

### 关键区别

- **回流**：元素的几何属性（宽高、位置、显示状态）变化 → 需要重新计算所有受影响的节点位置
- **重绘**：元素的外观（颜色、背景、阴影）变化但不改变布局 → 跳过 Layout 直接 Paint
- **合成**：仅 transform/opacity 变化 → 跳过 Layout 和 Paint，只走合成层 GPU 加速

---

## 三、浏览器渲染队列机制

**关键事实**：浏览器并不是每次样式变化都立刻回流，而是把多次修改**合并到一次渲染**。

```js
// ✅ 一次回流（浏览器自动合并）
el.style.width = '100px';
el.style.height = '100px';
el.style.margin = '10px';

// ❌ 强制同步布局（强制立即回流）
el.style.width = '100px';
console.log(el.offsetWidth);   // ← 强制浏览器立即回流一次
el.style.height = '100px';
console.log(el.offsetHeight); // ← 再次强制回流
```

**触发"强制同步布局"**：在写样式后**立即读取几何属性**，浏览器必须立即回流以保证读到的值是最新的。

---

## 四、触发回流的操作清单

### 高频触发（几何属性读取）

| 操作 | 触发回流 |
|------|---------|
| `offsetWidth` / `offsetHeight` / `offsetTop` / `offsetLeft` | ✅ 强制同步布局 |
| `clientWidth` / `clientHeight` / `clientTop` / `clientLeft` | ✅ |
| `scrollTop` / `scrollLeft` / `scrollWidth` / `scrollHeight` | ✅ |
| `getComputedStyle()` | ✅ |
| `getBoundingClientRect()` | ✅ |
| `scrollIntoView()` | ✅ |
| `element.focus()`（触发滚动） | ✅ |

### DOM 操作

| 操作 | 触发回流 |
|------|---------|
| 添加/删除 DOM 节点 | ✅ |
| `display: none` ↔ 显示 | ✅ |
| 改变元素几何属性（width/height/margin/padding/border） | ✅ |
| 改变字体大小、内容（文字换行） | ✅ |

### CSS 触发

| 操作 | 触发 |
|------|------|
| 改变几何属性（width/height/top/left/margin） | ✅ 回流 |
| 改变颜色（color/background） | ❌ 只重绘 |
| 改变 transform / opacity | ❌ 只合成 |

---

## 五、性能优化 5 大技巧

### 1. 批量 DOM 操作（DocumentFragment）

```js
// ❌ 100 次回流
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  document.body.appendChild(div);
}

// ✅ 1 次回流
const frag = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  frag.appendChild(document.createElement('div'));
}
document.body.appendChild(frag);
```

### 2. 离线 DOM 操作

```js
// 先 display:none，离线修改，再显示（只触发 2 次回流）
const el = document.getElementById('list');
el.style.display = 'none';
// ...大量修改...
el.style.display = 'block';
```

### 3. 用 transform 替代 top/left

```js
// ❌ 触发回流
el.style.top = '100px';
el.style.left = '200px';

// ✅ 只触发合成
el.style.transform = 'translate(200px, 100px)';
```

### 4. 读写分离（避免 Layout Thrashing）

```js
// ❌ Layout Thrashing：读 → 写 → 强制回流 → 读 → 写 → 强制回流 ...
for (let i = 0; i < 100; i++) {
  el.style.width = el.offsetWidth + 1 + 'px';
}

// ✅ 读写分离：先批量读，再批量写
const width = el.offsetWidth;
for (let i = 0; i < 100; i++) {
  el.style.width = (width + i) + 'px';
}
```

### 5. requestAnimationFrame 包装动画

```js
function animate() {
  el.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

---

## 六、面试陷阱

### 陷阱 1：以为 `transform: translateZ(0)` 一定能开启 GPU 加速

- **真相**：现代浏览器会自动判断是否需要 GPU 加速；过度使用反而增加显存占用

### 陷阱 2：以为 `position: fixed` 能避开回流

- **真相**：`position: fixed` 元素仍然参与回流（只是相对视口）

### 陷阱 3：把"读取几何属性"放进循环里一定慢

```js
// 这两种写法性能相同 —— 浏览器会自动批处理"读取"操作
for (let i = 0; i < 100; i++) {
  console.log(el.offsetWidth);
}
```

- **真相**：纯读取不会触发回流，浏览器会合并读取；只有**混合读写**才会触发 Layout Thrashing。

---

## 七、面试话术（90 秒版本）

> 回流是几何属性变化导致重新布局，重绘是外观变化但布局不变，合成是仅 transform/opacity 变化只走 GPU。回流一定触发重绘，重绘不一定触发回流。
>
> 浏览器有渲染队列机制，会自动合并多次 DOM 修改到一次回流，但**强制同步布局**会打破这个机制 —— 典型场景是先写样式再读几何属性（`el.style.width = '100px'; el.offsetWidth`），会导致每次都强制回流。
>
> 优化策略：用 `transform`/`opacity` 替代 `top`/`left`/颜色、用 DocumentFragment 批量插入 DOM、读写分离、用 `requestAnimationFrame` 包装动画。

---

## 八、相关章节

- 同栏目：[`css-render-blocking`](../css-render-blocking/README.md) — CSS 渲染阻塞
- 同栏目：[`script-async-defer`](../script-async-defer/README.md) — script 标签加载方式
- 同栏目：[`event-loop`](../event-loop/README.md) — 浏览器事件循环机制
- 主模块：[`09.front-end/06-performance`](../../../09.front-end/06-performance/README.md) — 前端性能优化

---

> 📅 2026-06-28 · 咬文嚼字 · 浏览器机制 · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · reflow-repaint](../README.md)
