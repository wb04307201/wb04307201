<!--
question:
  id: 09.front-end-css-button-styling
  topic: 09.front-end
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [09.front-end, css, button]
-->

# 一个按钮为什么写几十行 CSS：8 状态 + 5 大架构

> 看似简单的"按钮"，企业级组件可能要写 50-100 行 CSS。考察的不是"按钮怎么写"，而是 **CSS 工程化的设计思维** + **5 大架构方案的权衡**。

## 引子：接手别人的设计系统，按钮改动有 5 处冲突

```text
阿明的设计系统 v2 升级，要把"主按钮"的圆角从 4px 改到 8px。
改完发版，全站 30 个页面有 5 个样式错位：

- 列表卡片按钮：padding 不对，高度被 padding 撑大
- 表单提交按钮：focus 圈变小
- 弹窗操作按钮：文字颜色在 dark mode 下看不清
- 移动端按钮：touch target 小于 iOS 推荐的 44pt
- 带图标的按钮：图标垂直居中错位
```

**真相**：一个企业级按钮 ≠ 一行 `background`。

要管 **8 状态 × 3 尺寸 × 5 主题色** ≈ 50-100 行 CSS。
少一行就出 bug，多一行就难维护。**CSS 工程化**的功底，从这种"小东西"看得出来。

## 一、核心结论（TL;DR）

| 状态 | 必要性 | 实现要点 |
|------|--------|---------|
| default | 必须 | 基础样式 |
| hover | 必须 | 鼠标悬停反馈 |
| active / pressed | 必须 | 按下反馈 |
| focus / focus-visible | 必须 | 无障碍（键盘 Tab 焦点） |
| disabled | 必须 | 不可交互态 |
| loading | 重要 | 异步操作反馈 |
| selected | 按需 | 多选/单选选中态 |
| error / invalid | 按需 | 表单错误态 |

> 一句话：**一个企业级按钮要管 8 种状态 + 3 个尺寸 + 5 种主题色变体，50-100 行 CSS 是"基础款"**。

---

## 二、一个按钮的"完整生命周期"：8 种状态

### 1. default（默认态）

```css
.button {
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}
```

### 2. hover（悬停态）

```css
.button:hover {
  background: var(--color-primary-hover);
}
```

### 3. active / pressed（按下态）

```css
.button:active {
  background: var(--color-primary-pressed);
  transform: translateY(1px);  /* 微微下沉，给用户反馈 */
}
```

### 4. focus / focus-visible（键盘焦点态）

```css
/* ❌ 不推荐：鼠标点击也显示焦点环 */
.button:focus {
  outline: 2px solid blue;
}

/* ✅ 推荐：仅键盘 Tab 触发时显示 */
.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### 5. disabled（禁用态）

```css
.button:disabled {
  background: var(--color-gray-300);
  color: var(--color-gray-500);
  cursor: not-allowed;
  opacity: 0.6;
}
```

### 6. loading（加载态）

```css
.button.loading {
  position: relative;
  color: transparent;  /* 隐藏文字 */
  pointer-events: none;
}

.button.loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

### 7. selected（选中态）

```css
.button.selected {
  background: var(--color-primary-active);
  box-shadow: inset 0 0 0 2px var(--color-primary);
}
```

### 8. error（错误态）

```css
.button.error {
  background: var(--color-error);
}
```

**8 状态合计**：~80 行 CSS（不算尺寸和主题变体）

---

## 三、设计系统的 3 个抽象层

```
┌─────────────────────────────────────┐
│ Layer 1: Design Tokens（设计变量）   │  ← 全局变量，定义"颜色/间距/字号"
├─────────────────────────────────────┤
│ Layer 2: Component Styles（组件样式）│  ← 按钮/输入框等组件
├─────────────────────────────────────┤
│ Layer 3: Variant Classes（变体类）   │  ← primary / secondary / danger
└─────────────────────────────────────┘
```

### Layer 1：Design Tokens

```css
:root {
  /* 颜色 */
  --color-primary: #1890ff;
  --color-primary-hover: #40a9ff;
  --color-primary-pressed: #096dd9;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
}
```

### Layer 2：Component Styles

```css
.button {
  /* 基础样式，引用 Token */
  background: var(--color-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
}
```

### Layer 3：Variant Classes

```css
.button--primary { background: var(--color-primary); }
.button--secondary { background: var(--color-gray-500); }
.button--danger { background: var(--color-error); }
.button--success { background: var(--color-success); }

.button--small { padding: 4px 8px; font-size: 12px; }
.button--medium { padding: 8px 16px; font-size: 14px; }
.button--large { padding: 12px 24px; font-size: 16px; }
```

---

## 四、5 种 CSS 架构方案对比

| 架构 | 代表 | 优点 | 缺点 |
|------|------|------|------|
| **BEM** | `.button__icon--active` | 简单 / 无依赖 / 团队接受度高 | 命名长 / 没有作用域 |
| **OOCSS** | `.button .large .blue` | 高度复用 / 灵活组合 | 类名爆炸 |
| **SMACSS** | 5 类别分层 | 结构清晰 | 学习成本高 |
| **CSS Modules** | `.button_x7y3z` | 作用域隔离 / 主流方案 | 需要构建工具 |
| **CSS-in-JS** | `<Button css={...}>` | 动态样式 / 与组件同生命周期 | 运行时性能开销 / SSR 复杂 |
| **Utility-First** | Tailwind | 不写 CSS / 高度一致 | 类名长 / 学习曲线 |

### 1. BEM（Block Element Modifier）

```html
<button class="button button--primary button--large">
  <span class="button__icon">→</span>
  Submit
</button>
```

```css
.button { /* 基础样式 */ }
.button--primary { /* 主按钮变体 */ }
.button__icon { /* 图标元素 */ }
```

### 2. CSS Modules（主流 React 项目）

```css
/* Button.module.css */
.button {
  background: var(--color-primary);
}
```

```jsx
import styles from './Button.module.css';
<button className={styles.button}>Submit</button>
```

**编译后**：`button_x7y3z`，自动作用域隔离。

### 3. CSS-in-JS（styled-components / emotion）

```jsx
import styled from 'styled-components';

const Button = styled.button`
  background: ${props => props.primary ? 'blue' : 'gray'};
  padding: 8px 16px;
  
  &:hover {
    background: ${props => props.primary ? 'darkblue' : 'darkgray'};
  }
`;

<Button primary>Submit</Button>
```

### 4. Utility-First（Tailwind CSS）

```html
<button class="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded text-white">
  Submit
</button>
```

### 5. 5 大架构选型决策

```
Q1: 团队规模？
├── 小（< 5 人）→ BEM 或 OOCSS
├── 中（5-20 人）→ BEM 或 CSS Modules
└── 大（> 20 人）→ CSS Modules + Design Tokens

Q2: 框架？
├── React → CSS Modules 或 styled-components
├── Vue → scoped CSS 或 CSS Modules
└── 无框架 → BEM

Q3: 设计系统？
├── 有 → Design Tokens + 组件库
└── 无 → Tailwind 或 BEM

Q4: 性能敏感？
├── 是 → CSS Modules（构建时编译）
└── 否 → 任何方案都行
```

---

## 五、实战：一个企业级按钮组件

### 设计 Token（tokens.css）

```css
:root {
  /* 主色 */
  --color-primary: #1890ff;
  --color-primary-hover: #40a9ff;
  --color-primary-pressed: #096dd9;
  
  /* 文字色 */
  --color-text-primary: #ffffff;
  --color-text-disabled: rgba(0, 0, 0, 0.25);
  
  /* 背景 */
  --color-bg-disabled: #f5f5f5;
  
  /* 边框 */
  --color-border: #d9d9d9;
  
  /* 间距 */
  --spacing-sm: 8px;
  --spacing-md: 16px;
  
  /* 字号 */
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  
  /* 圆角 */
  --radius-sm: 4px;
  
  /* 动画 */
  --transition-fast: 0.1s ease-in-out;
}
```

### 组件样式（Button.module.css）

```css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: var(--font-size-md);
  padding: var(--spacing-sm) var(--spacing-md);
}

/* 变体 */
.primary {
  background: var(--color-primary);
  color: var(--color-text-primary);
}
.primary:hover { background: var(--color-primary-hover); }
.primary:active { background: var(--color-primary-pressed); }

.secondary {
  background: white;
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.secondary:hover { background: rgba(24, 144, 255, 0.1); }

/* 尺寸 */
.small { font-size: var(--font-size-sm); padding: 4px 8px; }
.medium { font-size: var(--font-size-md); padding: 8px 16px; }
.large { font-size: var(--font-size-lg); padding: 12px 24px; }

/* 状态 */
.button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
.button:disabled,
.disabled {
  background: var(--color-bg-disabled);
  color: var(--color-text-disabled);
  cursor: not-allowed;
}

/* 加载态 */
.loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}
.loading::after {
  content: '';
  position: absolute;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### 组件代码（Button.tsx）

```tsx
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={[
        styles.button,
        styles[variant],
        styles[size],
        loading && styles.loading,
      ].filter(Boolean).join(' ')}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

**总计**：~100 行 CSS + 30 行 TSX。

---

## 六、反 CSS 过度设计——什么时候该简化

### 1. 不需要 Design Tokens 的场景

- 一次性活动页 / 落地页
- 个人项目 / 内部工具

### 2. 不需要 CSS Modules 的场景

- 纯静态 HTML 页面
- 样式 < 100 行的简单项目

### 3. 不需要 CSS-in-JS 的场景

- 静态主题，不动态切换
- 团队不熟悉 JS

### 4. 判断标准

| 指标 | 应该复杂 | 应该简单 |
|------|---------|---------|
| CSS 总行数 | > 1000 行 | < 200 行 |
| 组件数 | > 10 个 | < 5 个 |
| 主题切换 | 需要 | 不需要 |
| 团队规模 | > 3 人 | 1-2 人 |

---

## 七、面试陷阱

### 陷阱 1：以为按钮的 CSS 都很简单

- **真相**：企业级按钮要管 8 状态 + 5 主题变体 + 3 尺寸 = 100 行 CSS

### 陷阱 2：以为 BEM 是"过时"架构

- **真相**：BEM 仍是 2026 年最稳定的 CSS 命名规范之一

### 陷阱 3：以为 CSS-in-JS 性能不好

- **真相**：现代框架（styled-components v6 / emotion）已优化 SSR 和性能

### 陷阱 4：以为 Tailwind 是"万能解"

- **真相**：Tailwind 适合快速开发，但样式集中管理困难（要去 HTML 里找）

---

## 八、面试话术（90 秒版本）

> 一个企业级按钮要管 8 种状态（default/hover/active/focus/disabled/loading/selected/error）+ 5 种主题变体（primary/secondary/danger/success/warning）+ 3 个尺寸（small/medium/large），CSS 行数 80-100 行是基础款。
>
> 设计系统的 3 个抽象层：Design Tokens（全局变量）/ Component Styles（组件基础样式）/ Variant Classes（变体类）。
>
> 5 大 CSS 架构方案：
>
> - **BEM**：命名规范，无依赖，简单场景
> - **CSS Modules**：作用域隔离，React 项目主流
> - **CSS-in-JS**（styled-components）：动态样式，与组件同生命周期
> - **Utility-First**（Tailwind）：不写 CSS，快速开发
> - **OOCSS/SMACSS**：早期方案，现已较少用
>
> 选型决策：团队规模小→BEM，React 项目→CSS Modules + Design Tokens，设计系统→Tokens + 组件库。
>
> 反过度设计：CSS 行数 < 200、组件 < 5 个时不需要复杂架构。

---

## 九、相关章节

- 同栏目：[`bfc`](../bfc/README.md) — BFC 块级格式化上下文
- 主模块：[`09.front-end/05-architecture`](../../../09.front-end/05-architecture/README.md) — 前端架构

---

> 📅 2026-06-28 · 咬文嚼字 · 前端 CSS · ⭐⭐⭐（高频实战 + 设计思维）

← [返回: 咬文嚼字 · css-button-styling](README.md)
