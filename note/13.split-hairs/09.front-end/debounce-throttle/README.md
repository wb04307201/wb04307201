<!--
question:
  id: 09.front-end-debounce-throttle
  topic: 09.front-end
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [09.front-end, debounce, throttle]
-->

# 防抖与节流手写实现

## 引子：搜索框的性能问题

```javascript
// 用户输入搜索关键词
input.addEventListener('input', (e) => {
  fetch('/api/search?q=' + e.target.value)  // 每输入一个字就请求一次！
})

// 用户快速输入 "hello" → 发了 5 次请求（h, he, hel, hell, hello）
// 服务器：我谢谢你啊...
```

**防抖**解决：用户停止输入 300ms 后才发请求。

再看另一个场景：

```javascript
// 窗口 resize / 滚动监听
window.addEventListener('scroll', () => {
  // 每像素都触发 → 一秒几百次回调 → 页面卡顿
})
```

**节流**解决：固定频率执行，比如每 100ms 最多一次。

---

## 一、核心原理

**防抖（Debounce）**：延迟执行，在指定时间内如果被重新触发，就清除之前的定时器并重新计时。最终只执行最后一次（或第一次）。本质是通过 `setTimeout` + `clearTimeout` + 闭包保存 `timer` 来实现。

**节流（Throttle）**：固定频率执行，在指定时间间隔内只执行一次。无论触发多少次，都按照固定的时间间隔来执行。常见实现有时间戳版和定时器版两种思路。

两者的共同点：都是为了解决高频触发带来的性能问题，都是利用闭包来保存状态。

两者的区别：防抖关注的是「最后一次」，节流关注的是「固定频率」。

---

## 二、防抖实现

### 2.1 基础版

```javascript
function debounce(fn, delay) {
  let timer = null;

  return function (...args) {
    const context = this;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(context, args);
    }, delay);
  };
}
```

核心要点：闭包保存 `timer`，每次调用先 `clearTimeout`，用 `apply` 保证 `this` 正确。

### 2.2 立即执行版

增加 `immediate` 参数，支持第一次立即执行：

```javascript
function debounce(fn, delay, immediate = false) {
  let timer = null;
  let executed = false;

  return function (...args) {
    const context = this;
    if (timer) clearTimeout(timer);

    if (immediate) {
      if (!executed) {
        fn.apply(context, args);
        executed = true;
      }
      timer = setTimeout(() => { executed = false; }, delay);
    } else {
      timer = setTimeout(() => { fn.apply(context, args); }, delay);
    }
  };
}
```

使用场景：搜索框希望第一次按键立即发起请求，后续输入等待用户停止后再发起。

### 2.3 带取消功能

```javascript
function debounce(fn, delay) {
  let timer = null;

  const debounced = function (...args) {
    const context = this;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => { fn.apply(context, args); }, delay);
  };

  debounced.cancel = function () {
    if (timer) { clearTimeout(timer); timer = null; }
  };

  return debounced;
}

// 使用示例
const handleSearch = debounce((keyword) => {
  console.log('搜索:', keyword);
}, 300);
handleSearch('hello');
handleSearch.cancel(); // 取消 pending 的执行
```

### 2.4 Promise 封装版

返回 Promise，方便异步场景中使用：

```javascript
function debounce(fn, delay) {
  let timer = null;

  return function (...args) {
    const context = this;
    return new Promise((resolve, reject) => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        try {
          const result = fn.apply(context, args);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, delay);
    });
  };
}

// 使用示例
const handleSearch = debounce(async (keyword) => {
  const res = await fetch(`/api/search?q=${keyword}`);
  return res.json();
}, 300);
handleSearch('hello').then(data => {
  console.log('搜索结果:', data);
});
```

---

## 三、节流实现

### 3.1 时间戳版

利用时间戳判断是否超过时间间隔：

```javascript
function throttle(fn, interval) {
  let lastTime = 0;

  return function (...args) {
    const context = this;
    const now = Date.now();
    if (now - lastTime >= interval) {
      fn.apply(context, args);
      lastTime = now;
    }
  };
}
```

**特点**：第一次触发会立即执行，最后一次触发如果距离上次执行不足 `interval` 则不会执行。适合需要立即响应的场景。

### 3.2 定时器版

利用定时器控制执行频率：

```javascript
function throttle(fn, interval) {
  let timer = null;

  return function (...args) {
    const context = this;
    if (timer) return;
    timer = setTimeout(() => {
      fn.apply(context, args);
      timer = null;
    }, interval);
  };
}
```

**特点**：第一次触发不会立即执行，而是延迟 `interval` 后执行；最后一次触发一定会执行。适合不需要立即响应但需要保证最后一次执行的场景。

### 3.3 结合版（推荐）

既保证第一次立即执行，又保证最后一次会执行：

```javascript
function throttle(fn, interval) {
  let lastTime = 0;
  let timer = null;

  return function (...args) {
    const context = this;
    const now = Date.now();
    const remaining = interval - (now - lastTime);

    if (timer) clearTimeout(timer);

    if (remaining <= 0) {
      fn.apply(context, args);
      lastTime = now;
    } else {
      timer = setTimeout(() => {
        fn.apply(context, args);
        lastTime = Date.now();
        timer = null;
      }, remaining);
    }
  };
}
```

---

## 四、应用场景

### 4.1 防抖的应用场景

**搜索框输入联想**：用户输入时频繁触发搜索请求，使用防抖可以减少不必要的请求。

```javascript
const searchInput = document.getElementById('search');
const handleSearch = debounce((keyword) => {
  fetch(`/api/suggest?q=${keyword}`).then(res => res.json())
    .then(data => renderSuggestions(data));
}, 300);
searchInput.addEventListener('input', (e) => {
  handleSearch(e.target.value);
});
```

**窗口 resize**：窗口大小改变时重新计算布局，避免频繁重绘。

```javascript
window.addEventListener('resize', debounce(() => {
  recalculateLayout();
}, 200));
```

**按钮防重复点击**：防止用户快速多次点击提交按钮。

```javascript
const submitBtn = document.getElementById('submit');
const handleSubmit = debounce(() => {
  submitForm();
}, 500, true); // 立即执行版，第一次点击立即提交，500ms内再次点击无效
submitBtn.addEventListener('click', handleSubmit);
```

### 4.2 节流的应用场景

**滚动加载**：监听滚动事件实现无限加载，使用节流控制检查频率。

```javascript
window.addEventListener('scroll', throttle(() => {
  if (isNearBottom()) {
    loadMoreData();
  }
}, 200));
```

**鼠标移动轨迹绘制**：记录鼠标移动轨迹，使用节流减少采样点。

```javascript
canvas.addEventListener('mousemove', throttle((e) => {
  drawPoint(e.offsetX, e.offsetY);
}, 50));
```

**视频播放进度上报**：定期上报播放进度，避免过于频繁的 API 调用。

```javascript
video.addEventListener('timeupdate', throttle((e) => {
  reportProgress(e.target.currentTime);
}, 1000)); // 每秒上报一次
```

---

## 五、Lodash 实现分析

Lodash 的 `_.debounce` 和 `_.throttle` 提供了更丰富的配置选项。

### 5.1 leading / trailing 选项

```javascript
// leading: 是否在时间窗口开始时执行
// trailing: 是否在时间窗口结束时执行

// 防抖
const debounced = _.debounce(fn, 300, {
  leading: false,  // 默认 false
  trailing: true   // 默认 true
});

// 节流
const throttled = _.throttle(fn, 300, {
  leading: true,   // 默认 true
  trailing: true   // 默认 true
});
```

组合效果：
- `leading: true, trailing: false` — 只在开始时执行一次
- `leading: false, trailing: true` — 只在结束时执行一次
- `leading: true, trailing: true` — 开始和结束各执行一次（中间忽略）
- `leading: false, trailing: false` — 不执行（无意义配置）

### 5.2 maxWait 选项

`maxWait` 限制最大等待时间，防止函数长时间不执行：

```javascript
const debounced = _.debounce(fn, 300, {
  trailing: true,
  maxWait: 1000  // 最多等待 1000ms，无论如何都会执行
});
```

当持续触发事件时，普通防抖可能永远不执行（因为一直在重新计时），`maxWait` 保证了最长等待时间。

### 5.3 源码核心逻辑简析

Lodash 内部使用 `timestamp` 记录时间，通过 `remaining` 计算剩余时间，同时维护 `timerId`、`lastCallTime`、`lastInvokeTime` 等多个状态变量来处理边界情况。核心思路与我们上面的「结合版」类似，但处理了更多边缘场景如定时器漂移、系统时间变更等。

---

## 六、面试话术（30 秒版）

「防抖和节流都是用来解决高频触发问题的。防抖的核心是延迟执行，被触发就重新计时，通过 setTimeout + clearTimeout + 闭包保存 timer 实现，可以做成基础版、立即执行版、带 cancel 方法、Promise 封装等变体。节流的核心是固定频率执行，有时间戳版和定时器版两种，时间戳版第一次立即执行但最后一次可能不执行，定时器版第一次延迟但最后一次会执行。Lodash 还提供了 leading/trailing/maxWait 等高级选项。实际项目中搜索框用防抖，滚动加载用节流。」

---

## 七、交叉引用

- 主模块：[`09.front-end`](../../../09.front-end/) — 前端知识体系

## 相关章节

- 深度阅读：[`09.front-end`](../../09.front-end/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · debounce-throttle](README.md)
