<!--
module:
  parent: front-end/async-await-error-handling
  slug: front-end/async-await-error-handling/02-four-error-handlers
  type: topic
  category: 4 种错误处理
  summary: try/catch / .catch() / unhandledrejection / Result 4 种错误处理方式深度对比
-->

# 4 种错误处理方式深度对比

> **一句话**：**没有"必须 try/catch"**——4 种方式都有效，关键看场景：局部兜底用 try/catch，纯转发用 .catch()，最后防线用 unhandledrejection，函数式风格用 Result。

← [返回: async-await-error-handling 总目录](../README.md)

---

## 1. 方式 A 深度：try/catch

### 1.1 基础用法

```js
async function loadUser(id) {
  try {
    const user = await fetchUser(id);
    return user;
  } catch (err) {
    console.error('加载失败:', err);
    return DEFAULT_USER;
  }
}
```

### 1.2 finally 清理

```js
let loading = false;
async function submit() {
  loading = true;
  try {
    await api.submit();
  } catch (err) {
    showError(err);
  } finally {
    loading = false;  // 无论成功失败都执行
  }
}
```

### 1.3 catch 中重新抛出（冒泡）

```js
async function load() {
  try {
    return await fetch('/api/data');
  } catch (err) {
    // 局部 log，但重新抛出（让上层知道）
    console.warn('警告：加载失败，继续重试');
    throw err;  // 主动冒泡
  }
}
```

### 1.4 适用场景

| 场景 | 推荐度 |
|------|--------|
| **立即处理错误 + 返回兜底默认值** | ⭐⭐⭐⭐⭐ |
| **UI 显示错误信息** | ⭐⭐⭐⭐⭐ |
| **Promise 链很短的纯转发** | ⭐⭐ |
| **嵌套很深的错误处理** | ⭐（啰嗦）|

---

## 2. 方式 B 深度：.catch()

### 2.1 基础用法

```js
function loadUser(id) {
  return fetchUser(id)
    .then(user => user)
    .catch(err => {
      console.error(err);
      return DEFAULT_USER;
    });
}
```

### 2.2 链式组合

```js
function loadUserWithPosts(id) {
  return fetchUser(id)
    .catch(err => DEFAULT_USER)        // 错误冒泡兜底
    .then(user => fetchPosts(user.id))
    .catch(err => DEFAULT_POSTS);     // 又是错误冒泡兜底
}
```

### 2.3 适用场景

| 场景 | 推荐度 |
|------|--------|
| **纯转发希望上层也看到错误** | ⭐⭐⭐⭐⭐ |
| **链式调用风格统一** | ⭐⭐⭐⭐ |
| **需要链式组合多个 catch** | ⭐⭐⭐⭐⭐ |

---

## 3. 方式 C 深度：unhandledrejection 全局兜底

### 3.1 基础用法

```js
// 全局注册（应在 app 入口）
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();  // 阻止默认 console.error
  console.error('全局兜底:', event.reason);
  
  // 上报到监控
  Sentry.captureException(event.reason);
  
  // UI 提示
  if (event.reason?.code === 'NETWORK_ERROR') {
    showToast('网络异常，请稍后重试');
  }
});
```

### 3.2 2 大事件对比

| 事件 | 触发场景 |
|------|---------|
| `unhandledrejection` | Promise 被 reject 但没 .catch() 也没 try/catch |
| `error` | 同步代码 throw 但没 try/catch |

### 3.3 适用场景

| 场景 | 推荐度 |
|------|--------|
| **统一错误监控** | ⭐⭐⭐⭐⭐ |
| **最后一道防线** | ⭐⭐⭐⭐⭐ |
| **想知道哪些错误"漏掉了"** | ⭐⭐⭐⭐ |

### 3.4 重大反模式

```js
// ❌ 错：在 unhandledrejection 里静默吞掉
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  // 没有 console / 上报 / UI → 错误真的消失了
});

// ✅ 对：上报 + 提示 + 必要时弹 toast
window.addEventListener('unhandledrejection', (event) => {
  Sentry.captureException(event.reason);
  showToast('出错了，请稍后重试');
});
```

---

## 4. 方式 D 深度：Result 模式

### 4.1 基础模式

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
  console.error(err);
} else {
  console.log(user);
}
```

### 4.2 TypeScript 加强版

```ts
type Result<T> = [Error, null] | [null, T];

async function safeAsync<T>(promise: Promise<T>): Promise<Result<T>> {
  try {
    const data = await promise;
    return [null, data];
  } catch (err) {
    return [err instanceof Error ? err : new Error(String(err)), null];
  }
}

// 类型安全
const [err, user] = await safeAsync(fetchUser(123));
if (err) {
  // err 是 Error 类型
} else {
  // user 是 T 类型（不会 null）
  console.log(user.name);
}
```

### 4.3 适用场景

| 场景 | 推荐度 |
|------|--------|
| **TypeScript 项目** | ⭐⭐⭐⭐⭐ |
| **函数式编程风格** | ⭐⭐⭐⭐⭐ |
| **错误频繁需要显式判断** | ⭐⭐⭐⭐ |
| **业务代码（业务流程长）** | ⭐⭐⭐⭐ |
| **短期脚本** | ⭐⭐（包装啰嗦）|

---

## 5. 4 种方式组合实战

### 5.1 双保险组合（最推荐）

```js
// 1. 局部：try/catch 处理已知错误
async function loadUser(id) {
  try {
    return await fetchUser(id);
  } catch (err) {
    console.warn('用户加载失败，使用默认');
    return DEFAULT_USER;
  }
}

// 2. 全局：unhandledrejection 兜底
window.addEventListener('unhandledrejection', (event) => {
  Sentry.captureException(event.reason);
  showToast('系统繁忙，请稍后重试');
});
```

### 5.2 链式转发 + 全局兜底

```js
function loadPipeline() {
  return step1()
    .catch(handleStep1Error)  // 已知错误处理
    .then(step2)
    .catch(handleStep2Error)
    .then(step3);
}
// 全局兜底捕获未捕获的
window.addEventListener('unhandledrejection', handler);
```

### 5.3 Result 模式 + try/catch

```js
async function loadUser() {
  const [err, user] = await safeAsync(api.user());
  if (err) return null;
  
  try {
    return await transformUser(user);
  } catch (transformErr) {
    return DEFAULT_USER;
  }
}
```

---

## 6. 一句话总结

> **没有"必须 try/catch"——4 种方式按场景选：局部兜底用 try/catch，纯转发用 .catch()，最后防线用 unhandledrejection，函数式用 Result。推荐组合：try/catch 局部 + unhandledrejection 全局。**

---

← [返回: async-await-error-handling 总目录](../README.md) · 上一章：[01-promise-error-basics](01-promise-error-basics.md) · 下一章：[03-react-vue-production](03-react-vue-production.md)
