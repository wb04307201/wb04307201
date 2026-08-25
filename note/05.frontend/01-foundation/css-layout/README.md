<!--
module:
  parent: note
  slug: 09.front-end/foundation/css-layout
  type: article
  category: 主模块子文章
  summary: CSS 布局模式与核心机制
-->

# CSS 布局

> CSS 布局的「核心机制 + 模式选型」——理解 BFC / Flex / Grid / 浮动四套体系的边界与最佳实践。

---

## 主题导航

| 主题 | 状态 | 说明 |
|------|------|------|
| [BFC 块级格式化上下文](bfc.md) | ✓ 已有 | 触发条件 / 三大应用场景 / 与 IFC/FFC/GFC 的对比 |
| Flex 布局 | 📝 速查 | 详见 [css-engineering](../css-engineering/)；核心：`display: flex; justify-content: center; align-items: center` |
| Grid 布局 | 📝 速查 | 详见 [css-engineering](../css-engineering/)；核心：`grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))` |
| Float 浮动布局 | 📝 速查 | 传统方案：`float: left; overflow: hidden`（清除浮动），新项目不再推荐 |

### 学习路径

- **入门**：BFC（理解「为什么 margin 会重叠 / 浮动会塌陷」）
- **进阶**：Flex（一维弹性空间）→ Grid（二维精确网格）
- **避坑**：新项目**直接 Flex / Grid**，避免 Float 布局

---

## 与其他模块的关系

- **横向**：[`css-engineering`](../css-engineering/) — 盒模型 / 工程化方案（Tailwind / CSS Modules）
- **横向**：[`browser-rendering`](../browser-rendering/) — 浏览器渲染流水线（Layout / Paint 阶段）
- **下游**：[`05-architecture/rendering-modes`](../../05-architecture/rendering-modes/) — 客户端渲染模式选型

---

## 速查要点

- **一维用 Flex，二维用 Grid**：单行/列排列用 Flex，行列同时控制用 Grid
- **居中用 `place-items: center`**（Grid）或 `justify-content + align-items`（Flex）
- **BFC 是布局"万能胶"**：`overflow: hidden` / `display: flow-root` 触发 BFC，解决 margin 重叠与浮动塌陷
- **新项目弃 Float**：Flex / Grid 已全面覆盖，Float 仅用于文字环绕图片等语义场景

---

## 📊 本节统计

- **子 README 数**：1
- **数据快照**：2026-08

---

← [返回: 01 基础](../README.md)