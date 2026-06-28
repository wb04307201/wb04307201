# 前端咬文嚼字

> 前端高频面试题与细节深挖，对齐主模块 [`09.front-end`](../../09.front-end/)

---

## 文章清单

### JavaScript 核心
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [闭包 Closure](closure/) | ⭐⭐⭐⭐ | 私有变量 / 内存泄漏 / React Hooks 陷阱 |
| [事件循环 Event Loop](event-loop/) | ⭐⭐⭐⭐ | 宏任务 / 微任务 / async-await 本质 |
| [原型链与继承](prototype-chain/) | ⭐⭐⭐⭐ | `__proto__` vs `prototype` / 继承方案 |
| [this 绑定规则](this-binding/) | ⭐⭐⭐⭐ | 默认 / 隐式 / 显式 / new / 箭头函数 |
| [防抖 + 节流手写](debounce-throttle/) | ⭐⭐⭐⭐ | debounce / throttle 实现与应用场景 |

### HTTP 与网络
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [GET vs POST](get-and-post/) | ⭐⭐ | 7 大差异 + 幂等性 + 安全性 |
| [HTTP 缓存机制](http-cache/) | ⭐⭐⭐⭐ | 强缓存 Cache-Control / 协商缓存 ETag |
| [CORS 跨域详解](cors/) | ⭐⭐⭐⭐ | 简单请求 / 预检请求 / 常见头部 |
| [HTTPS 握手过程](https-handshake/) | ⭐⭐⭐⭐⭐ | TLS 1.2 vs 1.3 / 证书验证 |

### CSS
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [BFC 块级格式化上下文](bfc/) | ⭐⭐⭐ | 触发条件 / 应用场景 / 边距折叠 |
| [按钮 CSS 几十行](css-button-styling/) | ⭐⭐⭐ | 8 状态 + 3 抽象层 + 5 大架构方案 |

### 浏览器机制
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [消息机制](message/) | ⭐⭐⭐ | 浏览器事件循环 + 宏任务 / 微任务 |
| [存储方案](storage/) | ⭐⭐ | Cookie / LocalStorage / SessionStorage / IndexedDB |
| [从 URL 输入到页面展示](from-url-to-page/) | ⭐⭐⭐⭐⭐ | 综合题：网络 + 解析 + 渲染全链路 |
| [CSS 渲染阻塞](css-render-blocking/) | ⭐⭐⭐⭐ | CSS 位置 vs 首屏白屏 + 6 种优化姿势 |
| [回流与重绘](reflow-repaint/) | ⭐⭐⭐⭐ | 渲染队列机制 + Layout Thrashing 避免 |
| [script async / defer](script-async-defer/) | ⭐⭐⭐⭐ | 加载 vs 执行时机 + DOMContentLoaded |
| [懒加载 vs 预加载](lazy-load-preload/) | ⭐⭐⭐⭐ | preload / prefetch / preconnect / dns-prefetch |

### 工具与测试
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Playwright vs Selenium](playwright-vs-selenium/) | ⭐⭐⭐ | 2026 Web 自动化测试选型 + 5 大维度对比 |

### 框架
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Virtual DOM Diff](virtual-dom-diff/) | ⭐⭐⭐⭐ | O(n) 复杂度 / key 的作用 / diff 策略 |
| [React Hooks 原理](react-hooks/) | ⭐⭐⭐⭐ | useState / useEffect / useMemo / useCallback |
| [Vue 响应式原理](vue-reactivity/) | ⭐⭐⭐⭐ | Object.defineProperty vs Proxy |

### 安全
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [XSS / CSRF 攻击防御](xss-csrf/) | ⭐⭐⭐⭐ | 反射型 / 存储型 / Token / SameSite Cookie |

### 工具方法
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [深拷贝实现](deep-copy/) | ⭐⭐⭐⭐ | 递归 / 循环引用 / 特殊类型处理 |

### Promise 专题
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Promise 手写实现](promise-handwriting/) | ⭐⭐⭐⭐⭐ | resolve / reject / then / catch / all / race |

---

## 学习路径

1. **入门**（3 天）：GET vs POST + 存储方案 + 消息机制
2. **进阶**（2 周）：事件循环 + 闭包 + 原型链 + this 绑定 + Promise 手写
3. **冲刺面试**：重点看"从 URL 输入到页面展示"、"HTTPS 握手"、"Virtual DOM Diff"、"Vue 响应式原理"、"CSS 渲染阻塞"、"回流与重绘"、"Playwright vs Selenium"

## 相关章节

- 主模块：[`note/09.front-end`](../../09.front-end/) — 前端知识体系
- 相关章节：[`01-foundation`](../../09.front-end/01-foundation/) / [`02-language`](../../09.front-end/02-language/)（基础与语言）
