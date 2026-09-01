<!--module:
  parent: front-end
  slug: 09.front-end/a11y
  type: article
  category: 主模块子文章
  summary: Web 无障碍（a11y）核心原则、ARIA 属性、键盘导航、测试工具与实战案例
  depth: ⭐⭐⭐⭐
-->

# 无障碍（a11y）

> ⬅️ [返回 09.front-end](../README.md)

> **一句话定位**：Web Accessibility（a11y）—— 让所有用户（含视障 / 听障 / 运动障碍 / 认知障碍）都能感知、操作、理解页面内容。是从"页面"到"应用"的必备能力。

---

## 🎯 学习目标

- 理解 WCAG 2.1 四大原则（POUR）及 13 条指南
- 掌握 ARIA 属性的使用场景与最佳实践
- 实现完整的键盘导航支持
- 使用自动化工具 + 手动测试验证可访问性
- 了解浏览器/屏幕阅读器的适配差异

---

## 📚 核心原则：WCAG 2.1 POUR

WCAG（Web Content Accessibility Guidelines）2.1 定义了 4 大原则、13 条指南、78 条成功标准。

### P - Perceivable（可感知）

**原则**：信息和 UI 组件必须以用户能感知的方式呈现。

**关键指南**：
- **1.1.1 非文本内容**（Level A）：所有图片必须有 `alt` 属性
- **1.3.1 信息和关系**（Level A）：使用语义化 HTML（`<nav>`, `<main>`, `<article>`）
- **1.4.3 对比度（最小）**（Level AA）：文本对比度 ≥ 4.5:1

```html
<!-- ❌ 错误 -->
<img src="logo.png">
<div class="button">提交</div>

<!-- ✅ 正确 -->
<img src="logo.png" alt="公司 Logo">
<button type="submit">提交</button>
```

### O - Operable（可操作）

**原则**：UI 组件和导航必须可操作。

**关键指南**：
- **2.1.1 键盘**（Level A）：所有功能可通过键盘访问
- **2.4.3 焦点顺序**（Level A）：焦点顺序保持逻辑顺序
- **2.4.7 焦点可见**（Level AA）：键盘焦点必须可见

```javascript
// ❌ 错误：只支持鼠标点击
<div onclick="submit()">提交</div>

// ✅ 正确：支持键盘（Enter/Space）
<button 
  type="button"
  onclick="submit()"
  onkeydown="if(event.key === 'Enter' || event.key === ' ') submit()"
>
  提交
</button>

// 或者使用原生 <button>，自动支持键盘
```

### U - Understandable（可理解）

**原则**：信息和 UI 操作必须可理解。

**关键指南**：
- **3.1.1 页面语言**（Level A）：`<html lang="zh-CN">`
- **3.2.1 焦点触发**（Level A）：焦点移动不应触发意外变化
- **3.3.1 错误标识**（Level A）：表单错误必须清晰标识

```html
<!-- ❌ 错误：无语言声明 -->
<html>

<!-- ✅ 正确 -->
<html lang="zh-CN">

<!-- ❌ 错误：焦点触发意外提交 -->
<input onchange="submitForm()" />

<!-- ✅ 正确：明确的操作按钮 -->
<input type="text" />
<button type="submit">提交</button>
```

### R - Robust（健壮）

**原则**：内容必须足够健壮，能被各种用户代理（包括辅助技术）解析。

**关键指南**：
- **4.1.2 名称、角色、值**（Level A）：UI 组件必须有可编程的名称和角色
- **4.1.3 状态消息**（Level AA）：状态消息必须用 ARIA live region 呈现

```html
<!-- ❌ 错误：自定义组件无 ARIA -->
<div class="custom-select">
  <div class="selected">选项 1</div>
  <ul class="options">...</ul>
</div>

<!-- ✅ 正确：使用 ARIA 声明角色和状态 -->
<div 
  class="custom-select"
  role="listbox"
  aria-label="选择城市"
  aria-expanded="false"
>
  <div 
    class="selected"
    role="combobox"
    aria-haspopup="listbox"
    aria-expanded="false"
  >
    选项 1
  </div>
  <ul class="options" role="listbox">
    <li role="option" aria-selected="true">选项 1</li>
    <li role="option">选项 2</li>
  </ul>
</div>
```

---

## 🛠️ ARIA 属性实战

### 何时使用 ARIA？

**第一原则**：如果能用原生 HTML 元素实现，就不要用 ARIA。

```html
<!-- ❌ 不推荐：用 div + ARIA 模拟按钮 -->
<div role="button" tabindex="0">提交</div>

<!-- ✅ 推荐：使用原生 button -->
<button type="submit">提交</button>
```

### 常用 ARIA 属性

| 属性 | 用途 | 示例 |
|------|------|------|
| `aria-label` | 为元素提供可访问名称 | `<button aria-label="关闭">✕</button>` |
| `aria-labelledby` | 引用其他元素作为标签 | `<div aria-labelledby="title-id">` |
| `aria-describedby` | 引用描述信息 | `<input aria-describedby="hint-id">` |
| `aria-hidden` | 隐藏装饰性内容 | `<span aria-hidden="true">🎉</span>` |
| `aria-live` | 动态内容区域 | `<div aria-live="polite">` |
| `aria-expanded` | 展开/折叠状态 | `<button aria-expanded="false">` |
| `aria-selected` | 选中状态 | `<li role="option" aria-selected="true">` |
| `aria-disabled` | 禁用状态 | `<button aria-disabled="true">` |

### Live Region：动态内容通知

```html
<!--  polite：用户空闲时通知 -->
<div aria-live="polite" aria-atomic="true">
  已保存 3 个项目
</div>

<!--  assertive：立即打断用户 -->
<div aria-live="assertive">
  错误：请输入有效的邮箱地址
</div>
```

---

## ⌨️ 键盘导航实现

### Tab 顺序管理

```html
<!-- 自然 Tab 顺序：按 DOM 顺序 -->
<nav>
  <a href="/">首页</a>
  <a href="/about">关于</a>
</nav>
<main>
  <button>操作 1</button>
  <button>操作 2</button>
</main>

<!-- 自定义 Tab 顺序（谨慎使用） -->
<button tabindex="1">优先级 1</button>
<button tabindex="2">优先级 2</button>
<div tabindex="0">可聚焦的 div</div>
<div tabindex="-1">程序化聚焦（不在 Tab 顺序中）</div>
```

### 焦点陷阱（模态框）

```javascript
class Modal {
  constructor(modalElement) {
    this.modal = modalElement;
    this.focusableElements = modalElement.querySelectorAll(
      'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
    );
    this.firstFocusable = this.focusableElements[0];
    this.lastFocusable = this.focusableElements[this.focusableElements.length - 1];
    
    this.modal.addEventListener('keydown', this.trapFocus.bind(this));
  }
  
  trapFocus(event) {
    if (event.key !== 'Tab') return;
    
    if (event.shiftKey) {
      // Shift + Tab：从第一个元素跳到最后一个
      if (document.activeElement === this.firstFocusable) {
        event.preventDefault();
        this.lastFocusable.focus();
      }
    } else {
      // Tab：从最后一个元素跳到第一个
      if (document.activeElement === this.lastFocusable) {
        event.preventDefault();
        this.firstFocusable.focus();
      }
    }
  }
  
  open() {
    this.modal.style.display = 'block';
    this.firstFocusable.focus();
  }
  
  close() {
    this.modal.style.display = 'none';
  }
}
```

### Escape 键关闭

```javascript
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    const openModal = document.querySelector('.modal[open]');
    if (openModal) {
      openModal.close();
    }
  }
});
```

---

## 🧪 测试工具与方法

### 自动化工具对比

| 工具 | 类型 | 检测率 | 适用场景 |
|------|------|--------|---------|
| **axe-core** | 浏览器扩展 / CI | ~57% | 开发阶段快速检测 |
| **Lighthouse** | Chrome DevTools | ~30% | 性能 + 可访问性综合评估 |
| **WAVE** | 浏览器扩展 | ~40% | 可视化问题定位 |
| **Pa11y** | CLI / CI | ~57% | 自动化测试集成 |

```bash
# Pa11y CLI 使用
npm install -g pa11y
pa11y https://example.com

# 输出 JSON 格式
pa11y https://example.com --reporter json
```

### 手动测试清单

**键盘测试**：
- [ ] 所有交互元素可通过 Tab 键访问
- [ ] 焦点顺序符合逻辑
- [ ] 焦点样式清晰可见
- [ ] 无键盘陷阱（可正常退出）

**屏幕阅读器测试**：
- [ ] 图片有合适的 alt 文本
- [ ] 表单字段有关联的 label
- [ ] 动态内容有 live region 通知
- [ ] 页面结构清晰（heading 层级正确）

**对比度测试**：
- [ ] 正文文本对比度 ≥ 4.5:1
- [ ] 大文本（18pt+）对比度 ≥ 3:1
- [ ] UI 组件对比度 ≥ 3:1

```javascript
// 计算对比度
function getContrastRatio(color1, color2) {
  const luminance1 = getRelativeLuminance(color1);
  const luminance2 = getRelativeLuminance(color2);
  const lighter = Math.max(luminance1, luminance2);
  const darker = Math.min(luminance1, luminance2);
  return (lighter + 0.05) / (darker + 0.05);
}

// WCAG AA 标准
const ratio = getContrastRatio('#000000', '#ffffff'); // 21:1 ✅
const ratio2 = getContrastRatio('#777777', '#ffffff'); // 4.48:1 ❌
```

---

## 🌐 浏览器适配差异

### 屏幕阅读器支持

| 屏幕阅读器 | 浏览器 | ARIA 支持度 | 备注 |
|-----------|--------|------------|------|
| NVDA | Firefox / Chrome | 优秀 | 免费，Windows |
| JAWS | IE / Chrome | 优秀 | 付费，企业常用 |
| VoiceOver | Safari | 良好 | macOS / iOS 内置 |
| TalkBack | Chrome | 良好 | Android 内置 |

### 常见兼容性问题

```html
<!-- 问题 1：Safari 不支持 fieldset 的 flex 布局 -->
<fieldset style="display: flex;"> <!-- ❌ -->
  <legend>标题</legend>
  <input type="text">
</fieldset>

<!-- 解决：用 div 包裹 -->
<div style="display: flex;">
  <fieldset>
    <legend>标题</legend>
    <input type="text">
  </fieldset>
</div>

<!-- 问题 2：IE11 不支持 aria-current -->
<nav>
  <a href="/" aria-current="page">首页</a> <!-- ❌ IE11 -->
</nav>

<!-- 解决：添加 class 作为 fallback -->
<nav>
  <a href="/" class="current" aria-current="page">首页</a>
</nav>
```

---

## 📊 性能指标量化

### Core Web Vitals 与可访问性

| 指标 | 目标值 | 可访问性影响 |
|------|--------|-------------|
| **LCP** | < 2.5s | 慢加载影响认知障碍用户 |
| **INP** | < 200ms | 交互延迟影响运动障碍用户 |
| **CLS** | < 0.1 | 布局偏移影响低视力用户 |

### 可访问性审计指标

```javascript
// 自动化审计脚本
async function auditAccessibility(url) {
  const lighthouse = await import('lighthouse');
  const result = await lighthouse(url, {
    onlyCategories: ['accessibility']
  });
  
  const score = result.lhr.categories.accessibility.score; // 0-1
  const audits = result.lhr.audits;
  
  console.log(`可访问性得分: ${score * 100}`);
  console.log(`通过: ${audits.passed.length}`);
  console.log(`失败: ${audits.failed.length}`);
  
  // 详细报告
  audits.failed.forEach(audit => {
    console.log(`❌ ${audit.title}: ${audit.description}`);
  });
}
```

---

## 🔗 相关章节

- [WCAG 无障碍指南](wcag/README.md) — POUR 四大原则详解 + 12+ 条成功标准
- 语义化 HTML — 语义化标签与文档结构
- 表单设计 — 表单可访问性最佳实践

---


## 相关章节

- [Vite 构建工具](../04-engineering/vite/README.md)
- [06 性能](../06-performance/README.md)
- [03 框架](../03-frameworks/README.md)

← [返回 09.front-end](../README.md)
