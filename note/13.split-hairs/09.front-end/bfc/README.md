<!--
question:
  id: 09.front-end-bfc
  topic: 09.front-end
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [09.front-end, bfc]
-->

# BFC（块级格式化上下文）深度剖析

## 引子：两个经典 CSS 问题

**问题 1：margin 重叠**
```html
<div style="margin-bottom: 20px;">A</div>
<div style="margin-top: 30px;">B</div>
<!-- 两个 div 之间是 30px，不是 50px！ -->
```

**问题 2：浮动塌陷**
```html
<div>
  <div style="float: left; height: 100px;">内容</div>
</div>
<!-- 父 div 高度为 0！子元素浮出去了 -->
```

这两个问题的共同解决方案：**触发 BFC**。

BFC（Block Formatting Context）就像一个"隔离罩"——内部的布局不影响外部，外部的布局也不影响内部。

---

## 一、核心原理

**Block Formatting Context（块级格式化上下文）** 是 CSS 布局中的一个概念，它是 Web 页面中盒模型布局的渲染区域。简单来说，BFC 就是一个"隔离的容器"，容器内部的元素无论怎么布局，都不会影响到容器外部的元素。

### BFC 的关键特性

1. **独立性**：BFC 是一个完全独立的渲染区域，内部元素的布局不会影响外部
2. **垂直排列**：内部的 Box 会在垂直方向上一个接一个地放置
3. **边距折叠**：属于同一个 BFC 的两个相邻 Box 的 margin 会发生重叠
4. **不重叠**：BFC 的区域不会与浮动元素的 box 重叠
5. **计算高度**：计算 BFC 高度时，浮动元素也会参与计算

可以把 BFC 想象成一个"结界"，结界内外互不干扰。

---

## 二、触发条件

以下任意一种情况都会触发 BFC：

| 触发方式 | 说明 |
|---------|------|
| `float` 不为 `none` | `float: left` 或 `float: right` |
| `overflow` 不为 `visible` | `overflow: hidden` / `auto` / `scroll` |
| `display: flow-root` | **推荐方式**，专门用于创建 BFC，无副作用 |
| `position` 为 `absolute` 或 `fixed` | 绝对定位或固定定位 |
| `display` 为 `flex` / `inline-flex` | Flex 容器 |
| `display` 为 `grid` / `inline-grid` | Grid 容器 |
| `display` 为 `table-cell` / `table-caption` / `inline-block` | 表格相关或行内块 |
| 根元素 `<html>` | 天然具有 BFC |

**最佳实践**：现代开发推荐使用 `display: flow-root`，它唯一的目的就是创建 BFC，没有任何其他副作用。

---

## 三、BFC 的应用场景

### 场景一：防止相邻兄弟元素 margin 重叠

同一 BFC 内的相邻兄弟元素，垂直方向的 margin 会发生折叠（取较大值）。通过给其中一个元素包裹 BFC 容器可以解决。

```css
/* 问题：两个相邻 div 的 margin 会重叠 */
.box1 { margin-bottom: 30px; }
.box2 { margin-top: 20px; }
/* 实际间距只有 30px，而非期望的 50px */

/* 解决：给 box2 包裹一个 BFC 容器 */
.bfc-wrapper {
  display: flow-root; /* 创建新的 BFC */
}
```

```html
<div class="box1">第一个盒子</div>
<div class="bfc-wrapper">
  <div class="box2">第二个盒子</div>
</div>
<!-- 此时间距为 30px + 20px = 50px -->
```

### 场景二：清除浮动导致的高度塌陷

当子元素浮动时，父容器高度会塌陷为 0。让父容器触发 BFC 后，计算高度时会包含浮动元素。

```css
/* 问题：父容器高度塌陷 */
.parent {
  border: 2px solid #333;
}
.child {
  float: left;
  width: 100px;
  height: 100px;
}
/* .parent 高度为 0，边框紧贴顶部 */

/* 解决：父容器触发 BFC */
.parent {
  border: 2px solid #333;
  overflow: hidden; /* 触发 BFC，包含浮动元素 */
  /* 或使用 display: flow-root; */
}
```

```html
<div class="parent">
  <div class="child">浮动子元素</div>
</div>
<!-- .parent 现在能正确包裹浮动子元素 -->
```

### 场景三：阻止普通元素被浮动元素覆盖

浮动元素会脱离文档流，可能与后续普通元素重叠。让普通元素触发 BFC 后，会自动让出浮动元素的空间。

```css
/* 问题：文字环绕在浮动元素周围 */
.float-box {
  float: left;
  width: 200px;
  height: 150px;
}
.normal-box {
  /* 内容会环绕 .float-box */
}

/* 解决：普通元素触发 BFC */
.normal-box {
  overflow: hidden; /* 触发 BFC */
  /* 或使用 display: flow-root; */
}
/* .normal-box 会与 .float-box 并排，不再重叠 */
```

```html
<div class="float-box">左侧浮动区域</div>
<div class="normal-box">右侧自适应内容区域</div>
<!-- 实现经典的两栏自适应布局 -->
```

---

## 四、完整代码示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<style>
  /* 示例1：margin 重叠修复 */
  .demo1 .top    { margin-bottom: 30px; background: #e3f2fd; }
  .demo1 .bottom { margin-top: 20px; background: #fce4ec; }
  .demo1 .bfc    { display: flow-root; }

  /* 示例2：清除浮动 */
  .demo2 .parent      { border: 3px solid #ff5722; }
  .demo2 .parent--bfc { overflow: hidden; }
  .demo2 .child       { float: left; width: 120px; height: 80px; background: #4caf50; }

  /* 示例3：两栏布局 */
  .demo3 .float       { float: left; width: 200px; height: 100px; background: #9c27b0; color: #fff; }
  .demo3 .main        { overflow: hidden; background: #ffeb3b; min-height: 100px; }
</style>
</head>
<body>
  <!-- 各示例 HTML 结构见上文 -->
</body>
</html>
```

---

## 五、BFC vs IFC vs FFC vs GFC

CSS 中有四种格式化上下文，分别对应不同的布局模式：

| 类型 | 全称 | 触发条件 | 布局特点 |
|------|------|---------|---------|
| **BFC** | Block Formatting Context | float/overflow/display:flow-root 等 | 块级元素垂直排列，参与高度计算 |
| **IFC** | Inline Formatting Context | 包含 inline/inline-block 元素 | 行内元素水平排列，line-height 决定高度 |
| **FFC** | Flex Formatting Context | display: flex/inline-flex | 弹性布局，主轴/交叉轴自由排列 |
| **GFC** | Grid Formatting Context | display: grid/inline-grid | 网格布局，行列二维控制 |

**核心区别**：
- BFC 关注块级元素的**垂直流式布局**
- IFC 关注行内元素的**水平文本流**
- FFC 关注**一维**的弹性空间分配
- GFC 关注**二维**的网格精确定位

---

## 六、面试话术（30 秒版）

> BFC 即块级格式化上下文，是页面中一个独立的渲染区域。可以通过 float、overflow:hidden、display:flow-root 等方式触发。它有三大作用：第一，防止相邻兄弟元素的 margin 重叠；第二，解决浮动导致的高度塌陷问题；第三，让普通元素自动避开浮动元素，实现自适应两栏布局。本质上，BFC 通过创建一个隔离的布局环境，使得内部元素不会影响外部。

---

## 七、交叉引用

- 主模块：[`09.front-end`](../../../09.front-end/) — 前端知识体系

## 相关章节

- 深度阅读：[`09.front-end`](../../09.front-end/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · bfc](README.md)
