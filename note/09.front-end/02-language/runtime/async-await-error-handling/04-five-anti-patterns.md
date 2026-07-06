<!--
module:
  parent: front-end/async-await-error-handling
  slug: front-end/async-await-error-handling/04-five-anti-patterns
  type: topic
  category: 反模式
  summary: 5 大反模式 —— 未捕获 / 静默吞错 / finally 抛错 / 异步未 await / 错误污染
-->

# 5 大反模式 · async/await 错误处理实战避坑

> **一句话**：5 大反模式每个都"很常见"——未捕获会让 Promise reject 静默失败；finally 中抛错会覆盖原错误；async 函数未 await 是定时炸弹。

← [返回: async-await-error-handling 总目录](../README.md)

---

## 1. 反模式 1：未捕获的 async 异常

### 现象

```js
async function loadUser(id) {
  const user = await fetchUser(id);  // throw '网络错误'
  return user;
}

// 调用方忘了 try/catch
loadUser(123);  // ❌ 没接住，错误进入 unhandledrejection
```

**影响**：错误"消失"，开发时 Console 报警告但 UI 不显示。

### 修复

```js
// 方案 A：调用方接住
try {
  await loadUser(123);
} catch (err) {
  showError(err);
}

// 方案 B：全局兜底
window.addEventListener('unhandledrejection', (event) => {
  showToast('网络异常');
});

// 方案 C：async 函数自处理
async function safeLoadUser(id) {
  try {
    return await fetchUser(id);
  } catch (err) {
    console.error(err);
    return DEFAULT_USER;
  }
}
```

---

## 2. 反模式 2：try/catch 静默吞错

### 现象

```js
try {
  await api.submitOrder(data);
} catch (err) {
  // 啥也不做
}
```

**影响**：错误"消失"，用户不知道为什么订单没提交成功。

### 修复

```js
} catch (err) {
  // 至少 3 件事之一：log / 上报 / UI 提示
  console.error('提交订单失败:', err);  // log
  Sentry.captureException(err);          // 上报
  showToast('订单提交失败，请稍后重试');  // UI
}
```

**最佳实践**：3 件事**都做**——log 调试、上报监控、UI 告知用户。

---

## 3. 反模式 3：finally 中抛错覆盖原错误

### 现象

```js
async function submit() {
  try {
    await api.submit();
  } catch (err) {
    console.error('提交失败:', err);
  } finally {
    cleanup();  // ❌ cleanup 抛错会覆盖原 error
  }
}
```

**影响**：原 error 丢失，只剩 cleanupError，调试困难。

### 修复

```js
} finally {
  try {
    cleanup();
  } catch (cleanupErr) {
    // 单独处理 cleanup 错误（不影响原 error）
    console.error('清理失败:', cleanupErr);
    // 不要 throw，避免覆盖
  }
}
```

**更优雅：用 try/except 包 finally**

```js
async function submit() {
  let primaryErr;
  try {
    await api.submit();
  } catch (err) {
    primaryErr = err;
    console.error('提交失败:', err);
  } finally {
    try {
      cleanup();
    } catch (cleanupErr) {
      console.error('清理失败:', cleanupErr);
    }
  }
  if (primaryErr) throw primaryErr;
}
```

---

## 4. 反模式 4：async 函数未 await

### 现象

```js
async function sync() {
  fetch('/api/log');  // ❌ 没 await
}
sync();  // Promise 没人接，错误进 unhandledrejection
```

**影响**：错误"消失"，且**执行顺序不确定**——你以为是同步，可能 fetch 还没发出去函数就返回了。

### 修复

```js
// 方案 A：不关心结果，fire-and-forget
async function sync() {
  try {
    await fetch('/api/log');
  } catch (err) {
    // 显式接住
  }
}

// 方案 B：标记为不接 Promise
function sync() {
  fetch('/api/log').catch(err => console.error(err));
}

// 方案 C：使用 void 关键字表明意图
async function sync() {
  await Promise.allSettled([
    fetch('/api/log'),
    fetch('/api/analytics')
  ]);
}
```

---

## 5. 反模式 5：错误污染（async function 串接 catch 错位置）

### 现象

```js
async function step1() {
  throw new Error('step1 错了');
}

async function step2() {
  try {
    await step1();
  } catch (err) {
    console.log('step2 catch:', err);  // 这里接住 err
  }
}

async function step3() {
  await step2();
  // ❌ 期待 step2 报错，实际不报
}
```

**陷阱**：`step2` 自己 catch 了，**step3 看不到 step1 的错误**。

### 修复

```js
// 方案 A：step2 不 catch，让错误上抛
async function step2() {
  await step1();  // 错误穿透到 step3
}

// 方案 B：包成 Result
async function step2() {
  const [err, val] = await safeAsync(step1());
  return { err, val };
}
```

**反模式**：catch 不抛 = "吃掉错误"——除非你**明确要处理它**，否则应该让它冒泡。

---

## 6. 5 大反模式速查

| 反模式 | 现象 | 修复 |
|--------|------|------|
| **未捕获** | 错误进 unhandledrejection | try/catch 或全局兜底 |
| **静默吞错** | 错误"消失" | log + 上报 + UI 三件套 |
| **finally 抛错** | 原错误被覆盖 | finally 单独 try/catch |
| **async 未 await** | 错误进 unhandledrejection | await + 自己 catch |
| **catch 不抛** | 错误被中途吃掉 | 不要随便 catch，冒泡给上层 |

---

## 7. 一句话总结

> **5 大反模式都是"错误消失"陷阱——用 try/catch 必须 log/上报/UI 三件套；finally 单独 try/catch；async 必须 await；catch 不抛等于吞错。**

---

← [返回: async-await-error-handling 总目录](../README.md) · 上一章：[03-react-vue-production](03-react-vue-production.md) · 专题结束
