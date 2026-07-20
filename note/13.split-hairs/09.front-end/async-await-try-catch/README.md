<!--
question:
  id: 09.front-end-async-await-try-catch
  topic: 09.front-end
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 异步错误处理
  tags: [09.front-end, async, await, try/catch, Promise, unhandledrejection, ErrorBoundary]
-->

# async/await 必须 try/catch 吗？4 种错误处理深挖

> 一句话定位：**必须 try/catch 吗？不是！** 4 种错误处理方式（try/catch、.catch()、unhandledrejection、Result 模式）都有效——按场景选最合适的。完整深度见 [主模块 async-await-error-handling 专题](../../../09.front-end/02-language/runtime/async-await-error-handling/README.md)。

> **系列定位**：经典前端面试题（字节 / 阿里 / 美团 / 滴滴 / 拼多多 出题率 80%+）。考察的不是"try/catch 怎么写"，而是 **4 种错误处理方式** + **5 大反模式** + **React/Vue 异步错误全链路**。

---

## 引子：CTO 大会上"异步错误"踩坑的 3 个现场

```text
场景：2024 Q4 某电商前端 CTO 阿明——
- 痛点 1：用户反馈"下单失败"但开发查 log 没记录（错误被静默吞了）
- 痛点 2：错误被全局监听但没上报（unhandledrejection 没接 Sentry）
- 痛点 3：React 组件树异步错误导致整页白屏（ErrorBoundary 不捕异步）
```

**决策现场**：
1. **初创会问**：「async/await 必须 try/catch 吗？」
2. **资深会问**：「4 种错误处理方式怎么选？React/Vue 各自最佳实践？」
3. **架构师会问**：「异步错误全链路 4 道防线？ErrorBoundary 的致命限制是什么？」

普通候选人会答"必须 try/catch"——踩中"**反直觉答案 + 缺反模式 + 缺实战**" 3 大雷区。
高分候选人会答：**不一定（4 种都有效）+ 4 道防线 + React ErrorBoundary 不捕异步 + 5 大反模式**。

---

## 一、核心原理（必选）

### 1.1 必须 try/catch 吗？

**答案：不是必须。** 4 种错误处理方式都有效：

| 场景 | 推荐 |
|------|------|
| **局部兜底** | try/catch |
| **纯转发** | .catch() |
| **最后防线** | unhandledrejection |
| **TS/函数式** | Result 模式 |

实战推荐组合：**try/catch 局部 + unhandledrejection 全局双保险**

### 1.2 Promise 错误机制核心

```js
async function fetchUser() {
  throw new Error('网络错误');
}

fetchUser()
  .catch(err => console.log(err));  // 接住
  // 或 throw / try/catch / unhandledrejection
```

**关键洞察**：
- async 函数**永远返回 Promise**
- 内部 throw = 自动 reject
- 多层 await 错误**自动穿透**到最外层 catch

### 1.3 React ErrorBoundary 的致命限制

```jsx
class ErrorBoundary extends React.Component {
  render() {
    if (this.state.hasError) return <div>Error</div>;
    return this.props.children;  // 只捕渲染错误
  }
}

function Profile() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetchUser().then(setUser);  // ❌ async 错误 ErrorBoundary 接不住
  }, []);
}
```

**反直觉**：ErrorBoundary **不捕异步错误**——必须业务层 try/catch + 全局兜底。

### 1.4 unhandledrejection 全局兜底

```js
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  console.error('未捕获:', event.reason);
  Sentry.captureException(event.reason);
});
```

**触发条件**：Promise 被 reject 但**没 .catch() / try/catch 接住**

---

## 二、面试话术（90 秒版本 / 7 题）

> ⚠️ **模板不是背答案**——面试现场结合题目微调。

### 题目 A：async/await 必须使用 try/catch 吗？

**高分答案**（4 层递进，60-90 秒）：

```text
1. 明确答案（10 秒）：
   "不是必须——4 种错误处理方式都有效。"

2. 4 种方式对比（30 秒）：
   "4 种错误处理方式：
   - try/catch：局部兜底（最常用）
   - .catch()：链式转发，纯 Promise 风格
   - unhandledrejection：全局兜底（最后防线）
   - Result 模式：[err, data] 返回值，TS 友好

   实战推荐：try/catch 局部 + unhandledrejection 全局。"

3. 反直觉陷阱（25 秒）：
   "3 个反直觉：
   - React ErrorBoundary 不捕异步错误（致命）
   - 多层 await 错误自动穿透到最外层
   - finally 中抛错会覆盖原错误"

4. 反问（10 秒）：
   "贵司用 React 还是 Vue？是否有 axios 拦截器？"
```

### 题目 B：解释 unhandledrejection 与 try/catch 关系

**高分答案**（40 秒）：

```text
"两者是'局部+全局'的兜底关系。

try/catch 局部处理（同步代码风格，可读性高）；
unhandledrejection 全局兜底（兜所有漏掉的）。

触发链：
- async throw → Promise reject
- 有 try/catch → 错误被局部处理
- 没有 → 进入 '未捕获' 队列
- 浏览器 / Node 抛出 unhandledrejection 事件

实战：try/catch 处理已知错误 + unhandledrejection 上报未捕获。
反模式：try/catch 静默吞错 + 不写 unhandledrejection → 错误消失。"
```

### 题目 C：async 函数内的 try/catch 能捕获 await 抛出的错误吗？

**高分答案**（30 秒）：

```text
"能，而且多层 await 错误会自动穿透到最外层 catch。

async function layer1() { throw new Error('layer1'); }
async function layer2() { await layer1(); }  // 自动 reject
async function layer3() { await layer2(); }  // 自动 reject

try {
  await layer3();
} catch (err) {
  console.log(err);  // 'layer1' — 注意是原始错误
}

关键：错误穿透但丢失上下文（不知道在哪一层 throw）。
反模式：多层 catch 但不重新 throw，导致错误被中途吃掉。"
```

### 题目 D：async 函数不写 try/catch 也不写 .catch 会发生什么？

**高分答案**（35 秒）：

```text
"错误进 unhandledrejection，但有 5 个坑：

1. console 报警告（不影响流程）
2. 错误上下文丢失（不知道从哪个调用来）
3. UI 没提示（用户不知道）
4. 监控缺失（没接 Sentry 不会上报）
5. 性能影响（微任务队列堆积）

修复：
1. 全局 unhandledrejection 上报
2. 业务层 try/catch 处理已知错误
3. 返回兜底值
4. UI 提示
5. 上报监控"
```

### 题目 E：React ErrorBoundary 能否捕获 async 错误？

**高分答案**（40 秒）：

```text
"❌ 不能！这是 React 异步错误最常见的踩坑。

ErrorBoundary 只 catch 渲染时的 throw：
- 同步 throw → 接住 ✅
- 事件处理 throw → 接住 ✅
- useEffect / setTimeout / async → 接不住 ❌

原因是 React 渲染流程是同步的，async 错误发生在 React 之外。

修复方案：
1. async 函数 try/catch，setState 显示错误
2. react-error-boundary 库的 useErrorBoundary hook
3. 错误状态提升到 redux / zustand

反模式：以为 ErrorBoundary 兜底所有 → 异步错误全消失"
```

### 题目 F：finally 中抛错会发生什么？

**高分答案**（35 秒）：

```text
"finally 中抛错会覆盖原 try/catch 的错误。

async function submit() {
  try {
    await api.submit();
  } catch (err) {
    console.error('提交失败:', err);
  } finally {
    cleanup();  // 抛错会覆盖原 error
  }
}

错误流：try 错误 → 准备 catch → finally 抛错 → catch 收不到
最终：外层只看到 cleanup 错误，原错误丢失。

修复：finally 内单独 try/catch，cleanup 错误不影响原错误。
更优雅：用变量暂存原错误。"
```

### 题目 G：4 种错误处理方式怎么选？

**高分答案**（45 秒）：

```text
"按场景选 4 种之一：

1. try/catch 局部兜底（80% 场景）：
   - UI 显示错误
   - 返回默认值
   - 立即处理

2. .catch() 链式转发：
   - 纯 Promise 风格
   - 链式组合错误处理

3. unhandledrejection 全局兜底：
   - 最后防线（防止错误消失）
   - 上报监控
   - UI toast

4. Result 模式（TS/函数式）：
   - [err, data] 返回值
   - 错误显式判断
   - 避免 try/catch

实战 80%：try/catch 局部 + unhandledrejection 全局
TS 项目：Result 模式可替代部分 try/catch"
```

---

## 三、常见陷阱（必选，5 个核心反模式）

### 陷阱 1：未捕获的 async 异常

- **错误**：async 函数 throw 异常但调用方没接住
- **真相**：错误进 unhandledrejection
- **代价**：错误"消失"，开发时 Console 警告

### 陷阱 2：try/catch 静默吞错

- **错误**：catch 里什么都不做
- **真相**：错误"消失"，调试困难
- **代价**：用户不知道为什么失败

### 陷阱 3：finally 抛错覆盖原错误

- **错误**：finally 中 cleanup 抛错
- **真相**：原 try 错误丢失
- **代价**：排查时间 +10x

### 陷阱 4：async 函数未 await

- **错误**：fire-and-forget 模式但没标记
- **真相**：错误进 unhandledrejection，时序不确定
- **代价**：race condition 难复现

### 陷阱 5：catch 不抛 = 错误吞掉

- **错误**：catch 错误但不重新抛出
- **真相**：上层永远收不到
- **代价**：下游模块 silent fail

---

## 四、最佳实践（4 大场景方案）

### 方案 A：React + axios 全链路兜底

```js
// 1. 全局兜底
window.addEventListener('unhandledrejection', (event) => {
  Sentry.captureException(event.reason);
  showToast('网络异常');
});

// 2. axios 拦截器
axios.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) redirectLogin();
    return Promise.reject(err);
  }
);

// 3. ErrorBoundary
class ErrorBoundary extends React.Component { ... }

// 4. 业务 try/catch
async function loadUser() {
  try {
    return await api.user();
  } catch (err) {
    showToast('加载失败');
    return null;
  }
}
```

### 方案 B：Vue 3 + Pinia

```js
// 1. 全局 errorHandler
app.config.errorHandler = (err) => Sentry.capture(err);

// 2. axios 同上

// 3. errorCaptured
errorCaptured(err) { this.error = err; return false; }

// 4. 业务 try/catch（同 React）
```

### 方案 C：纯 H5（移动端）

```js
// unhandledrejection + try/catch
// 不需要 ErrorBoundary（无组件树）

async function loadPage() {
  try {
    return await api.page();
  } catch (err) {
    showAlert(err.message);
    return [];
  }
}
```

### 方案 D：TypeScript + 函数式

```ts
// Result 模式
async function safeAsync<T>(p: Promise<T>): Promise<[Error, null] | [null, T]> {
  try {
    return [null, await p];
  } catch (err) {
    return [err instanceof Error ? err : new Error(String(err)), null];
  }
}

const [err, user] = await safeAsync(api.user());
if (err) {
  // 类型保护：err 是 Error
} else {
  // user 必定是 T
}
```

---

## 五、相关章节（强制）

### 主模块深度专题

- [async-await-error-handling 总目录](../../../09.front-end/02-language/runtime/async-await-error-handling/README.md)
- [01-promise-error-basics](../../../09.front-end/02-language/runtime/async-await-error-handling/01-promise-error-basics.md) —— Promise reject 机制
- [02-four-error-handlers](../../../09.front-end/02-language/runtime/async-await-error-handling/02-four-error-handlers.md) —— 4 种错误处理深度
- [03-react-vue-production](../../../09.front-end/02-language/runtime/async-await-error-handling/03-react-vue-production.md) —— React/Vue 实战
- [04-five-anti-patterns](../../../09.front-end/02-language/runtime/async-await-error-handling/04-five-anti-patterns.md) —— 5 反模式

### 同栏目（09.front-end）姐妹篇

- [event-loop](../event-loop/README.md) —— async/await 执行顺序本质
- [promise-handwriting](../promise-handwriting/README.md) —— Promise 手写 / thenable 实现
- [deep-copy](../deep-copy/README.md) —— 深拷贝面试题

### 主模块兄弟

- [09.front-end/02-language/runtime/README](../../../09.front-end/02-language/runtime/README.md) —— JS 运行时

### 实战姐妹（12.story）

- 暂无（前端的"前端 CTO"叙事待沉淀）

---

## 六、面试反问（让候选人反客为主）

```text
Q1：贵司用 React 还是 Vue？是否有 ErrorBoundary？
    → 答：React → ErrorBoundary 限制必须知道；Vue → errorHandler
Q2：贵司有 Sentry / 监控吗？
    → 没的话：错误消失是严重问题，建议接入
Q3：贵司异步错误有全局兜底吗？
    → 不一定有：需要 unhandledrejection 兜底
Q4：贵司 axios 用拦截器吗？
    → 用：401 状态码判断 / 取消重复请求都需要
Q5：贵司有取消重复请求的机制吗？
    → 答：高频请求场景必备
```

---

> 📅 2026-07-06 · 咬文嚼字 · 09.front-end · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板 + 5 反模式 + 4 实战方案

← [返回: 咬文嚼字 · async-await-try-catch](../README.md)
