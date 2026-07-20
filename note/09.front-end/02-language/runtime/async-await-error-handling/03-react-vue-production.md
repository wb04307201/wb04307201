<!--
module:
  parent: front-end/async-await-error-handling
  slug: front-end/async-await-error-handling/03-react-vue-production
  type: topic
  category: 框架实战
  summary: React/Vue 异步错误生产实战 —— ErrorBoundary / axios 拦截器 / Vue errorHandler / unhandledrejection 全链路兜底
-->

# React/Vue 异步错误生产实战

> **一句话**：前端框架**不捕获异步组件渲染错误**——必须用 **ErrorBoundary**（React）或 **errorHandler**（Vue）+ **axios 拦截器** + **unhandledrejection** 四道防线全链路兜底。

← [返回: async-await-error-handling 总目录](../README.md)

---

## 1. 4 道防线全景

```text
┌────────────────────────────────────────────────────────────┐
│ 防线 1：组件渲染错误                                          │
│   React: ErrorBoundary / Vue: errorHandler + errorCaptured    │
│   ↓ 渲染中 throw 错误                                        │
├────────────────────────────────────────────────────────────┤
│ 防线 2：异步操作错误                                          │
│   async/await + try/catch / .catch()                          │
│   ↓ Promise 链条错误                                         │
├────────────────────────────────────────────────────────────┤
│ 防线 3：网络层错误                                            │
│   axios 拦截器（response / request）                          │
│   ↓ HTTP 4xx/5xx 统一处理                                    │
├────────────────────────────────────────────────────────────┤
│ 防线 4：全局兜底                                              │
│   window.addEventListener('unhandledrejection')              │
│   ↓ 任何没被捕获的 Promise 错误                                │
└────────────────────────────────────────────────────────────┘
```

---

## 2. 防线 1：React ErrorBoundary

### 2.1 ErrorBoundary 基础组件

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('组件错误:', error, errorInfo);
    Sentry.captureException(error, { extra: errorInfo });
  }
  
  render() {
    if (this.state.hasError) {
      return <div>出错了：{this.state.error.message}</div>;
    }
    return this.props.children;
  }
}
```

### 2.2 使用

```jsx
<ErrorBoundary>
  <UserProfile userId={123} />  {/* 内部 throw 会被 ErrorBoundary 接住 */}
</ErrorBoundary>
```

### 2.3 **致命限制**：ErrorBoundary **不捕获异步错误**

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);  // ❌ async 错误 ErrorBoundary 接不住
  }, [userId]);
  
  return <div>{user?.name}</div>;
}
```

**反直觉**：ErrorBoundary 只能捕获**渲染中**的 throw，**异步错误必须靠 try/catch + unhandledrejection + 业务状态**。

### 2.4 React 18+：async ErrorBoundary 替代方案

```jsx
// 使用 react-error-boundary 库
import { ErrorBoundary } from 'react-error-boundary';

function UserProfile({ userId }) {
  // react-error-boundary 提供 useErrorBoundary hook
  const { showBoundary } = useErrorBoundary();
  
  useEffect(() => {
    fetchUser(userId).catch(err => {
      showBoundary(err);  // 主动抛给 ErrorBoundary
    });
  }, [userId]);
}
```

---

## 3. 防线 2：Vue errorHandler + errorCaptured

### 3.1 全局 errorHandler

```js
// main.js
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 错误:', err, info);
  Sentry.captureException(err, { extra: { info } });
};
```

### 3.2 组件级 errorCaptured

```vue
<template>
  <div>
    <UserProfile v-if="!error" :userId="userId" />
    <div v-else>出错了：{{ error.message }}</div>
  </div>
</template>

<script>
export default {
  data() { return { error: null }; },
  errorCaptured(err, vm, info) {
    this.error = err;
    console.error('组件错误:', err);
    Sentry.captureException(err);
    return false;  // 阻止错误继续传播
  }
};
</script>
```

### 3.3 Vue 3 vs Vue 2

| Vue 版本 | 错误捕获机制 |
|---------|-------------|
| Vue 2 | `errorCaptured` + `errorHandler` |
| Vue 3 | 同上 + 异步错误捕获增强 |

---

## 4. 防线 3：axios 拦截器

### 4.1 response 拦截器（4xx/5xx）

```js
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401: 重新登录
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    
    // 403: 无权限
    if (error.response?.status === 403) {
      showToast('无权限访问');
    }
    
    // 500: 上报
    if (error.response?.status >= 500) {
      Sentry.captureException(error);
    }
    
    // 网络错误
    if (!error.response) {
      showToast('网络异常，请检查连接');
      // 可选：返回兜底数据
      return Promise.resolve({ data: { items: [] } });
    }
    
    return Promise.reject(error);  // 继续向下抛
  }
);
```

### 4.2 request 拦截器（统一 token / loading）

```js
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

### 4.3 取消重复请求

```js
const pendingRequests = new Map();

axios.interceptors.request.use((config) => {
  const key = `${config.method}:${config.url}`;
  if (pendingRequests.has(key)) {
    pendingRequests.get(key).cancel('重复请求');
  }
  const controller = new AbortController();
  config.signal = controller.signal;
  pendingRequests.set(key, controller);
  return config;
});

axios.interceptors.response.use(
  (response) => {
    pendingRequests.delete(`${response.config.method}:${response.config.url}`);
    return response;
  },
  (error) => {
    pendingRequests.delete(`${error.config.method}:${error.config.url}`);
    return Promise.reject(error);
  }
);
```

---

## 5. 防线 4：全局 unhandledrejection

```js
window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  console.error('未捕获 Promise 错误:', event.reason);
  Sentry.captureException(event.reason);
  
  // 根据错误类型 UI 提示
  const err = event.reason;
  if (err?.code === 'NETWORK_ERROR') {
    showToast('网络异常');
  } else if (err?.response?.status === 500) {
    showToast('服务器异常');
  }
});
```

---

## 6. 完整链路示例（React + axios）

```jsx
// App.jsx
function App() {
  useEffect(() => {
    // 全局兜底
    window.addEventListener('unhandledrejection', handleGlobalError);
    return () => window.removeEventListener('unhandledrejection', handleGlobalError);
  }, []);
  
  return (
    <ErrorBoundary>
      <UserList />
    </ErrorBoundary>
  );
}

// UserList.jsx
function UserList() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    axios.get('/api/users')
      .then(res => setUsers(res.data))
      .catch(err => setError(err));  // 局部 catch → UI 显示
  }, []);
  
  if (error) return <div>加载失败：{error.message}</div>;
  return users.map(u => <UserCard key={u.id} user={u} />);
}
```

---

## 7. 选型决策

| 场景 | 推荐组合 |
|------|---------|
| **React 项目** | ErrorBoundary + axios 拦截器 + try/catch + unhandledrejection |
| **Vue 项目** | errorHandler + axios 拦截器 + try/catch + unhandledrejection |
| **纯 H5** | try/catch + unhandledrejection |
| **后台管理** | 4 道全用（最严格）|
| **移动端 H5** | 上报 SDK 替代 Sentry + 4 道 |

---

## 8. 一句话总结

> **React/Vue 异步错误 = 4 道防线全链路：组件渲染（ErrorBoundary/errorHandler）+ 异步操作（try/catch）+ 网络层（axios 拦截器）+ 全局兜底（unhandledrejection）—— 缺一不可。**

---

← [返回: async-await-error-handling 总目录](../README.md) · 上一章：[02-four-error-handlers](02-four-error-handlers.md) · 下一章：[04-five-anti-patterns](04-five-anti-patterns.md)
