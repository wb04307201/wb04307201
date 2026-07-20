<!--
module:
  parent: front-end/02-language/runtime
  slug: front-end/async-await-error-handling
  type: deep-dive
  category: 异步错误处理
  summary: async/await 必须 try/catch 吗？—— 4 种错误处理方式对比 + 5 反模式 + React/Vue 生产实战
-->

# async/await 错误处理 · 4 种方式深度对比

> **一句话答案**：**必须 try/catch 吗？不是！** 4 种错误处理方式都有效：try/catch（局部）、.catch()（链式）、全局兜底（unhandledrejection）、Result 模式（不抛异常）。**实战推荐 try/catch + 全局兜底 组合**。

← [返回: runtime 总目录](../README.md) · 同级：[promise-handwriting](../../../../13.split-hairs/09.front-end/promise-handwriting/README.md) · [event-loop](../../../../13.split-hairs/09.front-end/event-loop/README.md)

---

## 0. 面试高频拷问

```text
Q：async/await 必须使用 try/catch 吗？
```

**回答框架（4 层递进）**：

1. **明确答案**：不是必须，但 try/catch 是**最常用**
2. **4 种错误处理方式**：try/catch、.catch()、全局 unhandledrejection、Result 模式
3. **何时用哪个**：根据错误是否可恢复、调用层级、是否需要冒泡
4. **5 大反模式**：未捕获 / 静默吞掉 / 在 finally 抛 / 异步函数未 await

完整 5-7 道精选面试题见 [13.split-hairs/09.front-end/async-await-try-catch](../../../../13.split-hairs/09.front-end/async-await-try-catch/README.md)。

---

## 1. async/await 本质回顾

```js
async function fetchUser() {
  const res = await fetch('/api/user');   // ① await 抛出 reject → 抛 Error
  return res.json();
}

// 等价于 Promise：
function fetchUser() {
  return fetch('/api/user').then(res => res.json());
}
```

**关键**：async 函数**总是返回 Promise**——如果函数体内抛异常，Promise 会变成 rejected。

---

## 2. 4 种错误处理方式

### 2.1 方式 A：try/catch（最常用）

```js
async function loadUser(id) {
  try {
    const user = await fetchUser(id);
    return user;
  } catch (err) {
    console.error('加载失败:', err);
    return DEFAULT_USER;  // 兜底
  }
}
```

**适用**：需要**立即处理错误**或**兜底默认值**的场景

**优点**：
- 同步代码风格，可读性高
- 局部处理，不影响其他代码
- 支持 finally 清理

**缺点**：
- 嵌套多层 try/catch 啰嗦
- 不适合纯转发场景（错误需要冒泡）

### 2.2 方式 B：.catch() 链式

```js
async function loadUser(id) {
  return fetchUser(id)
    .catch(err => {
      console.error('加载失败:', err);
      return DEFAULT_USER;
    });
}
```

**适用**：纯转发错误或希望错误冒泡给上层

**优点**：
- 链式风格，符合 Promise 思维
- 错误自动冒泡到调用方

**缺点**：
- 与 try/catch 混用时代码风格不一致

### 2.3 方式 C：全局 unhandledrejection（兜底）

```js
// 在 app 入口统一注册
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  console.error('全局兜底:', event.reason);
  // 上报到监控 / Sentry
  reportError(event.reason);
});

// async 函数未捕获的 reject 自动到这
loadUser(123);  // 没 try/catch 也没 .catch()
```

**适用**：**最后一道防线**——所有未捕获的错误到这里

**优点**：
- 不需要每个调用都加 try/catch
- 防止"沉默失败"

**缺点**：
- 错误**丢失上下文**（不知道是哪个调用）
- 不能阻止流程继续

### 2.4 方式 D：Result 模式（不抛异常）

```js
async function safeAsync(promise) {
  try {
    const data = await promise;
    return [null, data];
  } catch (err) {
    return [err, null];
  }
}

// 使用
const [err, user] = await safeAsync(fetchUser(123));
if (err) {
  console.error('加载失败:', err);
} else {
  console.log(user);
}
```

**适用**：函数式编程风格 / TypeScript 项目 / 错误频繁场景

**优点**：
- 类型明确（TypeScript 友好）
- 错误不会"漏掉"
- 显式判断，无需 catch 链

**缺点**：
- 包装代码冗长
- 团队需统一约定

---

## 3. 4 种方式对比

| 维度 | try/catch | .catch() | unhandledrejection | Result 模式 |
|------|-----------|----------|---------------------|-------------|
| **可读性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **错误冒泡** | ❌ 局部 | ✅ 自动 | ❌ 顶层 | ❌ 必须用返回值 |
| **局部处理** | ✅ | ✅ | ❌ | ✅ |
| **TypeScript 友好** | ⚠️ catch 类型 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **适用** | 局部兜底 | 纯转发 | **最后防线** | 错误频繁 |

---

## 4. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [Promise 错误基础](01-promise-error-basics.md) | Promise reject + 异常抛出机制 |
| 02 | [4 种错误处理方式深度](02-four-error-handlers.md) | try/catch / .catch() / unhandledrejection / Result |
| 03 | [React/Vue 异步错误实战](03-react-vue-production.md) | 组件级 ErrorBoundary + axios 拦截器 + 全局兜底 |
| 04 | [5 大反模式](04-five-anti-patterns.md) | 未捕获 / 静默 / finally 抛 / 异步未 await / 错误污染 |

---

## 5. 一句话速查

```text
async/await 错误处理选择：
- 需要立即兜底（默认值 / 上报）→ try/catch
- 需要冒泡给上层 → .catch()
- 全局兜底（最后防线）→ unhandledrejection
- TypeScript / 函数式 → Result 模式
实战：try/catch 局部 + unhandledrejection 兜底，**双保险**
```

---

## 6. 速查 · 关联资源

- **事件循环**（执行顺序视角）：[event-loop](../../../../13.split-hairs/09.front-end/event-loop/README.md)
- **Promise 手写**（then/catch 实现）：[promise-handwriting](../../../../13.split-hairs/09.front-end/promise-handwriting/README.md)
- **面试题**：[13.split-hairs/09.front-end/async-await-try-catch](../../../../13.split-hairs/09.front-end/async-await-try-catch/README.md)

---

← [返回: runtime 总目录](../README.md)
