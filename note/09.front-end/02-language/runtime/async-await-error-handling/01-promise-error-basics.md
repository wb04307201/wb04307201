<!--
module:
  parent: front-end/async-await-error-handling
  slug: front-end/async-await-error-handling/01-promise-basics
  type: topic
  category: Promise 错误基础
  summary: Promise reject 机制 + async 函数异常抛出 + 5 大误区
-->

# Promise 错误基础 · reject 机制与异常抛出

> **一句话**：Promise 内部 throw 会自动变成 reject；async 函数**永远返回 Promise**——内部抛异常，函数返回的 Promise 立刻变成 rejected。

← [返回: async-await-error-handling 总目录](../README.md)

---

## 1. Promise 的 3 大状态

```
pending ──── resolve() ────→ fulfilled（成功）
   │
   └──── reject()  ────→ rejected（失败）
```

只有这 3 个状态，**一旦确定不可逆**。

---

## 2. 三种抛出错误的方式

### 2.1 方式 1：new Promise 时 reject

```js
new Promise((resolve, reject) => {
  reject(new Error('错误'));  // 主动 reject
});
```

### 2.2 方式 2：throw 自动变 reject

```js
new Promise((resolve, reject) => {
  throw new Error('错误');  // 抛错自动 reject
});
```

等效于 reject，等价 Promise A+ 规范。

### 2.3 方式 3：async 函数 throw

```js
async function foo() {
  throw new Error('错误');  // 等价于：return Promise.reject(new Error('错误'))
}
```

**关键洞察**：async 函数 throw = 返回的 Promise rejected。

---

## 3. async/await 错误传播

### 3.1 同步抛出 → 立即 reject

```js
async function foo() {
  throw new Error('foo error');  // 抛出
}

foo().catch(err => console.log(err));  // foo error
```

### 3.2 await 抛出 → 当前函数 reject

```js
async function bar() {
  await foo();  // foo 抛出 → 当前函数（bar）也 reject
}

bar().catch(err => console.log('bar:', err));
// bar: foo error
```

**关键**：`await` 像"砍一刀"——把内层 Promise 的 reject 抛到外层。

### 3.3 多层 await

```js
async function layer1() { throw new Error('layer1'); }
async function layer2() { await layer1(); }  // 自动 reject
async function layer3() { await layer2(); }  // 自动 reject
async function layer4() { await layer3(); }  // 自动 reject
async function main() {
  try {
    await layer4();
  } catch (err) {
    console.log('main:', err);  // 任意层 throw，这里都接得住
  }
}

main();  // main: layer1
```

**反直觉**：**只有最外层 try/catch 接得到错误**——内部 await 都自动"穿透"。

---

## 4. 5 大误区（必避）

### 误区 1：async 函数 throw vs return error

```js
// 错：以为 throw 会让控制台报错
async function foo() {
  throw new Error('foo');  // 没有 try/catch → unhandledrejection
}
foo();  // 不会自动 console.error，会被 unhandledrejection 事件接住

// 对：要么 try/catch，要么把错误冒泡给调用方
```

### 误区 2：未 await 的 Promise

```js
async function loadUsers() {
  fetch('/api/users');  // ❌ 没 await！fetch 返回的 Promise 没人接
}

loadUsers();  // 错误会被 unhandledrejection 兜住（但 timing 不确定）
```

**修正**：
```js
async function loadUsers() {
  const res = await fetch('/api/users');  // ✅ await 接住
  return res.json();
}
```

### 误区 3：错误吞掉

```js
try {
  await fetch('/api/user');
} catch (err) {
  // 什么都不做 → 错误"消失"
}
```

**修正**：
```js
} catch (err) {
  console.error(err);  // 至少 log
  reportError(err);   // 上报
}
```

### 误区 4：finally 中抛错

```js
try {
  await fetch(...);
} catch (err) {
  /* cleanup */
} finally {
  cleanup();  // ❌ cleanup 抛错会覆盖原错误
}
```

**修正**：
```js
} finally {
  try {
    cleanup();
  } catch (cleanupErr) {
    // 单独处理，不影响原错误
  }
}
```

### 误区 5：在 Promise 链中 return Promise.reject

```js
function step1() {
  return fetch('/api').then(data => {
    if (!data.ok) {
      return Promise.reject(new Error('HTTP error'));  // ❌ 不规范
    }
    return data;
  });
}
```

**正解**：
```js
function step1() {
  return fetch('/api').then(data => {
    if (!data.ok) throw new Error('HTTP error');  // ✅ 抛错更优雅
    return data;
  });
}
```

---

## 5. 一句话总结

> **Promise 错误核心：async 函数总是返回 Promise，内部 throw = 自动 reject；多层 await 错误自动"穿透"到最外层 try/catch。**

---

← [返回: async-await-error-handling 总目录](../README.md) · 下一章：[02-four-error-handlers](02-four-error-handlers.md)
