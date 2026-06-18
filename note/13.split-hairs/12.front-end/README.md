# 前端咬文嚼字

> 前端高频面试题与细节深挖，对齐主模块 [`12.front-end`](../../12.front-end/)

---

## 文章清单

### HTTP
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [GET vs POST](get-and-post/) | ⭐⭐ | 7 大差异 + 幂等性 + 安全性 |

### 浏览器机制
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [事件循环 Event Loop](event-loop/) | ⭐⭐⭐⭐ | 宏任务 / 微任务 / async-await 本质 |
| [消息机制](message/) | ⭐⭐⭐ | 浏览器事件循环 + 宏任务 / 微任务 |
| [存储方案](storage/) | ⭐⭐ | Cookie / LocalStorage / SessionStorage / IndexedDB |

### JavaScript 核心
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [闭包 Closure](closure/) | ⭐⭐⭐⭐ | 私有变量 / 内存泄漏 / React Hooks 陷阱 |
| [从 URL 输入到页面展示](from-url-to-page/) | ⭐⭐⭐⭐⭐ | 综合题：网络 + 解析 + 渲染全链路 |

---

## 待补充的高频面试题（强烈建议）

### JavaScript 核心（必考）
- **事件循环（Event Loop）详解**（宏任务 vs 微任务执行顺序）
- **闭包（Closure）原理与陷阱**（内存泄漏、循环中的闭包）
- **原型链与继承**（`__proto__` vs `prototype`、原型链查找）
- **this 绑定规则**（默认 / 隐式 / 显式 / new / 箭头函数）
- **Promise 手写实现**（resolve / reject / then / catch / all / race / allSettled）
- **async/await 原理**（Generator + 自动执行器）
- **深拷贝实现**（递归 + 处理循环引用 + 特殊类型）
- **防抖（debounce）与节流（throttle）手写**

### CSS（高频）
- **CSS 优先级计算**（Specificity：inline > id > class > tag）
- **BFC（块级格式化上下文）**（触发条件 + 应用场景）
- **Flex 布局详解**（主轴 / 交叉轴、常用属性组合）
- **水平垂直居中 N 种方案**（Flex / Grid / 定位 / transform）
- **CSS 选择器优先级**（!important > inline > #id > .class > tag）

### 浏览器与网络（高频）
- **浏览器渲染流程**（DOM + CSSOM → Render Tree → Layout → Paint → Composite）
- **HTTP/1.1 vs HTTP/2 vs HTTP/3**（多路复用、头部压缩、0-RTT）
- **HTTPS 握手过程**（TLS 1.2 vs 1.3）
- **CORS 跨域详解**（简单请求 vs 预检请求、常见头部）
- **从输入 URL 到页面展示全过程**（经典综合题）
- **浏览器缓存机制**（强缓存 Cache-Control vs 协商缓存 ETag/Last-Modified）

### React / Vue 框架（高频）
- **Virtual DOM 与 Diff 算法**（O(n) 复杂度、key 的作用）
- **React Hooks 原理**（useState / useEffect / useMemo / useCallback）
- **React Fiber 架构**（时间切片、优先级调度）
- **Vue 响应式原理**（Object.defineProperty vs Proxy）
- **Vue 3 Composition API vs Options API**
- **React 合成事件 vs 原生事件**
- **React 性能优化**（memo / useMemo / useCallback / React.memo）

### 性能优化（高频）
- **Core Web Vitals 三大指标**（LCP / INP / CLS）
- **首屏优化方案**（SSR / SSG / 预加载 / 代码分割）
- **图片优化**（WebP / AVIF / 响应式图片 / 懒加载）
- **长列表优化**（虚拟滚动）

### 安全（高频）
- **XSS 攻击与防御**（反射型 / 存储型 / DOM 型）
- **CSRF 攻击与防御**（Token / SameSite Cookie）
- **CSP 内容安全策略**

---

## 学习路径

1. **入门**（3 天）：GET vs POST + 存储方案 + 消息机制
2. **进阶**（2 周）：事件循环 + 闭包 + 原型链 + Promise 手写
3. **冲刺面试**：重点看"从 URL 输入到页面展示"、"CSS 优先级"、"Virtual DOM Diff"（待补）

## 交叉引用

- 主模块：[`note/12.front-end`](../../12.front-end/) — 前端知识体系
- 相关章节：[`01-foundation`](../../12.front-end/01-foundation/) / [`02-language`](../../12.front-end/02-language/)（基础与语言）
