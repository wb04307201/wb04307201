<!--
module:
  parent: note
  slug: 09.front-end/foundation/css-layout
  type: article
  category: 主模块子文章
  summary: CSS 布局模式与核心机制
  depth: ⭐⭐
-->

# CSS 布局

> CSS 布局的「核心机制 + 模式选型」——理解 BFC / Flex / Grid / 浮动四套体系的边界与最佳实践。

---

## 主题导航

| 主题 | 状态 | 核心属性速查 | 决策建议 |
|------|------|------------|---------|
| [BFC 块级格式化上下文](bfc.md) | ✓ 已有 | `display: flow-root` / `overflow: hidden` 触发 | 理解 margin 重叠 / 浮动塌陷的底层原因，面试必考 |
| Flex 布局 | 📝 速查 | `display: flex` + `justify-content`（主轴）+ `align-items`（交叉轴）+ `gap`；伸缩 `flex: 1`、换行 `flex-wrap: wrap` | 一维排列首选：导航栏、工具条、垂直水平居中；子项数量不定需弹性分配空间 |
| Grid 布局 | 📝 速查 | `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`；区域 `grid-template-areas`；对齐 `place-items` | 二维布局首选：整页骨架、卡片瀑布流、仪表盘；行列需要同时精确控制时 |
| Float 浮动布局 | 📝 速查 | `float: left` + 清除浮动（`overflow: hidden` / `::after clear`） | 新项目不再用于布局，仅保留文字环绕图片的语义场景 |

详见 [css-engineering](../css-engineering/) 的完整工程化实践。

### 学习路径

- **入门**：BFC（理解「为什么 margin 会重叠 / 浮动会塌陷」）
- **进阶**：Flex（一维弹性空间）→ Grid（二维精确网格）
- **避坑**：新项目**直接 Flex / Grid**，避免 Float 布局

---

## 布局选型决策表

| 维度 | Flex | Grid | Float |
|------|------|------|-------|
| 布局维度 | 一维（行或列） | 二维（行 + 列同时） | 一维（左右靠边） |
| 对齐控制 | 主轴 + 交叉轴，内容驱动 | 行列轨道 + 区域命名，布局驱动 | 仅浮动方向 |
| 响应式 | `flex-wrap` + `flex-basis` 百分比 | `auto-fit` + `minmax()` 天然响应式 | 需手写媒体查询断点 |
| 性能 | 现代引擎优化充分 | 大网格（>1000 项）需实测，隐式轨道有少量开销 | 触发 BFC 重算，历史负担最重 |
| 兼容性 | IE11 部分语法（-ms- 前缀），现代浏览器全覆盖 | IE 仅旧语法，现代浏览器全覆盖 | 全兼容 |
| 典型场景 | 导航栏 / 按钮组 / 居中 | 页面骨架 / 卡片流 / 报表 | 文字环绕图片 |

**推荐结论**：内容决定尺寸 → Flex；容器决定尺寸 → Grid；两者可嵌套组合（Grid 定骨架、Flex 排组件内元素）。

## 响应式布局

- **移动优先**：基础样式服务小屏，`@media (min-width: ...)` 逐级增强——断点建议 640 / 768 / 1024 / 1280，跟随设计稿而非设备型号
- **自适应网格**：`grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))` —— 卡片自动折行填满，零媒体查询
- **Container Queries（2023+ 基线）**：`@container (min-width: 400px) { ... }` 按**父容器宽度**而非视口响应——组件级响应式，设计系统跨页面复用的正解
- **单位选择**：布局间距用 `rem`（跟随根字号）、容器比例用 `%`/`fr`、图片用 `max-width: 100%` 防溢出

## 布局与可访问性（a11y）

- **DOM 顺序 = 阅读顺序**：屏幕阅读器与键盘 Tab 按 DOM 序列走，视觉重排不能改变语义顺序
- **`order` / `grid-area` 的陷阱**：CSS 可以只改视觉位置不改 DOM——此时键盘焦点顺序与视觉顺序分裂，用户按 Tab 会"跳来跳去"。仅在不影响理解顺序时（如独立卡片）才用
- **语义化标签承载布局区域**：`<header>` / `<nav>` / `<main>` / `<aside>` 让阅读器可跳转区域，纯 `div` 布局则丢失这一导航层

---

## 与其他模块的关系

- **横向**：[`css-engineering`](../css-engineering/) — 盒模型 / 工程化方案（Tailwind / CSS Modules）
- **横向**：[`browser-rendering`](../browser-rendering/) — 浏览器渲染流水线（Layout / Paint 阶段）
- **下游**：[`05-architecture/rendering-modes`](../../05-architecture/rendering-modes/) — 客户端渲染模式选型

---

## 速查要点

- **一维用 Flex，二维用 Grid**：单行/列排列用 Flex，行列同时控制用 Grid
- **居中用 `place-items: center`**（Grid）或 `justify-content + align-items`（Flex）
- **BFC 是布局"万能胶"**：`overflow: hidden` / `display: flow-root` 触发 BFC，解决 margin 重叠与浮动塌陷。两者差异：`overflow: hidden` 是"副作用式"触发——会裁剪溢出内容（下拉菜单、阴影被切）；`display: flow-root` 专为创建 BFC 而生，无裁剪副作用，**仅为触发 BFC 时应首选它**
- **新项目弃 Float**：Flex / Grid 已全面覆盖，Float 仅用于文字环绕图片等语义场景

---

## 📊 本节统计

- **子 README 数**：1
- **数据快照**：2026-08

---

← [返回: 01 基础](../README.md)