<!--
module:
  parent: note
  slug: 09.front-end/foundation/css-layout/bfc
  type: article
  category: 主模块子文章
  summary: BFC（块级格式化上下文）—— CSS 布局隔离的核心机制
  depth: ⭐⭐⭐
-->

# BFC（块级格式化上下文）

> BFC 是 CSS 布局的「隔离罩」——理解它，就能解释 margin 重叠、浮动塌陷、文字环绕三大经典问题的根因与解决方案。

---

## 一、为什么需要 BFC？两个反直觉现象

**现象 1：margin 重叠（取较大值，不相加）**
```html
<div style="margin-bottom: 20px;">A</div>
<div style="margin-top: 30px;">B</div>
<!-- 两个 div 之间是 30px，不是 50px！ -->
```

**现象 2：浮动塌陷（父元素高度变 0）**
```html
<div>
  <div style="float: left; height: 100px;">内容</div>
</div>
<!-- 父 div 高度为 0！子元素浮出去了 -->
```

这两个问题的**共同解决方案**：触发 BFC。

**Block Formatting Context（块级格式化上下文）** 是 Web 页面中盒模型布局的渲染区域。本质上是一个「隔离的渲染容器」——内部布局不影响外部，外部布局也不影响内部。

---

## 二、BFC 的核心特性

| 特性 | 说明 |
|------|------|
| **独立性** | 完全独立的渲染区域，内部布局不影响外部 |
| **垂直排列** | 内部 Box 在垂直方向上一个接一个放置 |
| **边距折叠** | 同一 BFC 内的相邻 Box，margin 会折叠（取较大值） |
| **不重叠** | BFC 区域不会与浮动元素的 box 重叠 |
| **包含浮动** | 计算 BFC 高度时，浮动元素也参与计算 |

可以把 BFC 想象成一个「结界」——结界内外互不干扰。

---

## 三、触发 BFC 的方式

以下任意一种情况都会触发 BFC：

| 触发方式 | 示例 | 副作用 |
|---------|------|--------|
| `display: flow-root` | **推荐**，专为创建 BFC 设计 | 无副作用 |
| `overflow` 不为 `visible` | `overflow: hidden / auto / scroll` | 可能裁剪内容 / 出现滚动条 |
| `float` 不为 `none` | `float: left / right` | 元素自身浮动，影响布局 |
| `position` 为 `absolute / fixed` | 绝对 / 固定定位 | 脱离文档流 |
| `display` 为 `flex / inline-flex` | Flex 容器 | 触发 FFC 而非纯 BFC |
| `display` 为 `grid / inline-grid` | Grid 容器 | 触发 GFC 而非纯 BFC |
| `display` 为 `inline-block / table-cell` | 行内块 / 表格相关 | 影响元素自身行为 |
| 根元素 `<html>` | 天然 BFC | — |

**最佳实践**：现代开发**推荐使用 `display: flow-root`**，它唯一的目的就是创建 BFC，没有任何其他副作用。

---

## 四、BFC 的三大经典应用场景

### 场景一：防止相邻兄弟元素 margin 重叠

同一 BFC 内的相邻兄弟元素，垂直方向的 margin 会折叠（取较大值）。给其中一个元素包裹 BFC 容器可解决。

```css
.box1 { margin-bottom: 30px; }
.box2 { margin-top: 20px; }
/* 实际间距 30px，而非期望的 50px */

.bfc-wrapper {
  display: flow-root; /* 创建新 BFC */
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

子元素浮动时，父容器高度会塌陷为 0。让父容器触发 BFC 后，计算高度会包含浮动元素。

```css
.parent { border: 2px solid #333; }
.child  { float: left; width: 100px; height: 100px; }
/* .parent 高度为 0，边框紧贴顶部 */

/* 解决：父容器触发 BFC */
.parent {
  display: flow-root;
  /* 或 overflow: hidden; */
}
```

### 场景三：阻止普通元素被浮动元素覆盖

浮动元素脱离文档流，可能与后续普通元素重叠。让普通元素触发 BFC 后，会自动让出浮动元素的空间，实现经典的两栏自适应布局。

```css
.float-box { float: left; width: 200px; height: 150px; }
.normal-box { display: flow-root; }
/* .normal-box 与 .float-box 并排，不再重叠 */
```

---

## 五、完整代码示例

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
  .demo3 .float  { float: left; width: 200px; height: 100px; background: #9c27b0; color: #fff; }
  .demo3 .main   { overflow: hidden; background: #ffeb3b; min-height: 100px; }
</style>
</head>
<body>
  <!-- 各示例 HTML 结构见上文场景 -->
</body>
</html>
```

---

## 六、四种格式化上下文对比

CSS 中有四种格式化上下文，对应不同的布局模式：

| 类型 | 全称 | 触发条件 | 布局特点 |
|------|------|---------|---------|
| **BFC** | Block Formatting Context | float / overflow / `display:flow-root` 等 | 块级元素垂直排列，参与高度计算 |
| **IFC** | Inline Formatting Context | 包含 inline / inline-block 元素 | 行内元素水平排列，line-height 决定高度 |
| **FFC** | Flex Formatting Context | `display: flex / inline-flex` | 弹性布局，主轴 / 交叉轴自由排列 |
| **GFC** | Grid Formatting Context | `display: grid / inline-grid` | 网格布局，行列二维控制 |

**核心区别**：
- BFC 关注块级元素的**垂直流式布局**
- IFC 关注行内元素的**水平文本流**
- FFC 关注**一维**的弹性空间分配
- GFC 关注**二维**的网格精确定位

---

## 七、面试话术（30s 版）

> BFC 即块级格式化上下文，是页面中一个独立的渲染区域。可以通过 float、`overflow:hidden`、`display:flow-root` 等方式触发。它有三大作用：第一，防止相邻兄弟元素的 margin 重叠；第二，解决浮动导致的高度塌陷问题；第三，让普通元素自动避开浮动元素，实现自适应两栏布局。本质上，BFC 通过创建一个隔离的布局环境，使得内部元素不会影响外部。

---

## 八、反直觉陷阱清单

1. **margin 重叠是「取大值」而非「相加」**——20px + 30px = 30px，同一 BFC 内才会发生
2. **`overflow: hidden` 会触发 BFC 但可能裁剪内容**——优先用 `display: flow-root` 避免副作用
3. **Flex / Grid 容器虽触发 BFC，但同时也是 FFC / GFC**——讨论「BFC 行为」时需明确上下文
4. **浮动元素本身已触发 BFC**——但它会脱离文档流，不能仅靠浮动解决塌陷问题
5. **BFC 解决的是「内部不影响外部 + 外部不影响内部」的双向隔离**——理解这一点能解释所有 BFC 应用

---

## 九、面试反问（候选追问）

- Q: `display: flow-root` 和 `overflow: hidden` 都能创建 BFC，生产中选哪个？
  A: 优先 `display: flow-root`——语义明确、零副作用；`overflow: hidden` 会裁剪溢出的 `position: absolute` 子元素
- Q: 父元素 `display: flex` 后子元素还会 margin 折叠吗？
  A: 不会。Flex 容器触发的是 FFC，子元素之间不会发生 BFC 式的 margin 折叠
- Q: 行内元素能创建 BFC 吗？
  A: 行内元素本身不能，但 `display: inline-block` 可以触发 BFC（同时也是 IFC 的一部分）

---

## 相关章节

- 上游：[`01-foundation`](../README.md) — 前端基础模块
- 横向：[`css-engineering`](../css-engineering/) — CSS 工程化（盒模型 / Flex / Grid）
- 关联：[`browser-rendering`](../browser-rendering/) — 浏览器渲染流水线

← [返回: 01 基础](../README.md)