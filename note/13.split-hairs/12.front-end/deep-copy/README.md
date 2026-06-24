# 深拷贝实现深度剖析

## 引子：一个让人困惑的 Bug

```javascript
const user = { name: "张三", address: { city: "北京" } }

// 浅拷贝
const user2 = { ...user }
user2.address.city = "上海"

console.log(user.address.city)  // "上海" ？？？
// 我明明只改了 user2，user 也被改了！
```

`{ ...user }` 只复制了第一层，嵌套的 `address` 还是共享引用。

要彻底断开引用，需要**深拷贝**——递归复制所有层级。

但深拷贝有很多坑：**循环引用、Date、RegExp、Map、Set**……都要特殊处理。

---

> 📚 **前置知识**：[JavaScript 基础](../../12.front-end/02-language/README.md)

## 一、核心原理

### 浅拷贝 vs 深拷贝

JavaScript 中的数据类型分为**基本类型**（String、Number、Boolean、Null、Undefined、Symbol、BigInt）和**引用类型**（Object、Array、Date、RegExp、Map、Set 等）。

- **浅拷贝**：只复制对象的第一层属性。对于引用类型，拷贝的是内存地址的引用，而非实际值。修改拷贝后的对象会影响原对象。
- **深拷贝**：递归复制对象的所有层级，包括嵌套的对象和数组。拷贝后的对象与原对象完全独立，互不影响。

### 引用类型的问题

```javascript
const obj = { a: 1, b: { c: 2 } };
const shallow = { ...obj };
shallow.b.c = 99;
console.log(obj.b.c); // 99 — 原对象被修改了！
```

引用类型的赋值操作只是传递了指针，多个变量指向同一块内存空间。这就是为什么需要深拷贝——彻底断开引用关系。

---

## 二、浅拷贝方法

### Object.assign()

```javascript
const obj = { a: 1, b: { c: 2 } };
const copy = Object.assign({}, obj);
copy.b.c = 99;
console.log(obj.b.c); // 99 — 第二层仍共享引用
```

`Object.assign()` 只拷贝第一层属性，嵌套对象仍然是引用。

### 展开运算符（Spread Operator）

```javascript
const arr = [1, [2, 3]];
const copy = [...arr];
copy[1][0] = 99;
console.log(arr[1][0]); // 99 — 嵌套数组仍共享引用
```

展开运算符的行为与 `Object.assign()` 类似，都是浅拷贝。

### Array.prototype.slice()

```javascript
const arr = [1, [2, 3]];
const copy = arr.slice();
copy[1][0] = 99;
console.log(arr[1][0]); // 99 — 同样是浅拷贝
```

`slice()` 对数组进行浅拷贝，不处理嵌套结构。

---

## 三、深拷贝实现

### JSON.parse(JSON.stringify()) 的缺陷

这是最简单的"深拷贝"方式，但存在严重问题：

```javascript
const obj = {
  a: 1,
  b: undefined,           // ❌ 丢失
  c: function() {},       // ❌ 丢失
  d: Symbol('sym'),       // ❌ 丢失
  e: new Date(),          // ⚠️ 变成字符串 "2026-06-18T00:00:00.000Z"
  f: /abc/gi,             // ⚠️ 变成空对象 {}
  g: NaN,                 // ⚠️ 变成 null
  h: Infinity,            // ✅ 保留
};

const copy = JSON.parse(JSON.stringify(obj));
// 结果: { a: 1, e: "2026-06-18T00:00:00.000Z", f: {}, h: Infinity }
```

**主要缺陷：**
1. 丢失 `undefined`、`Function`、`Symbol` 类型的值
2. `Date` 对象变成 ISO 格式字符串
3. `RegExp` 对象变成空对象 `{}`
4. 无法处理循环引用（直接抛出错误）
5. 丢失 `Map`、`Set` 等特殊集合类型
6. `NaN`、`Infinity` 序列化为 `null`

### 递归实现 + 处理循环引用

```javascript
/**
 * 完整深拷贝实现
 * @param {*} obj - 要拷贝的对象
 * @param {Map} visited - 记录已拷贝的对象，防止循环引用
 * @returns {*} 拷贝后的对象
 */
function deepClone(obj, visited = new Map()) {
  // 处理基本类型和 null
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  // 处理循环引用：如果已经拷贝过，直接返回缓存的副本
  if (visited.has(obj)) {
    return visited.get(obj);
  }

  // 处理 Date
  if (obj instanceof Date) {
    const copy = new Date(obj.getTime());
    visited.set(obj, copy);
    return copy;
  }

  // 处理 RegExp
  if (obj instanceof RegExp) {
    const copy = new RegExp(obj.source, obj.flags);
    visited.set(obj, copy);
    return copy;
  }

  // 处理 Map
  if (obj instanceof Map) {
    const copy = new Map();
    visited.set(obj, copy);
    obj.forEach((value, key) => {
      copy.set(deepClone(key, visited), deepClone(value, visited));
    });
    return copy;
  }

  // 处理 Set
  if (obj instanceof Set) {
    const copy = new Set();
    visited.set(obj, copy);
    obj.forEach((value) => {
      copy.add(deepClone(value, visited));
    });
    return copy;
  }

  // 处理数组
  if (Array.isArray(obj)) {
    const copy = [];
    visited.set(obj, copy);
    for (let i = 0; i < obj.length; i++) {
      copy[i] = deepClone(obj[i], visited);
    }
    return copy;
  }

  // 处理普通对象（包括 Symbol 作为 key）
  const copy = {};
  visited.set(obj, copy);

  // 拷贝字符串 key
  const stringKeys = Object.keys(obj);
  for (const key of stringKeys) {
    copy[key] = deepClone(obj[key], visited);
  }

  // 拷贝 Symbol key
  const symbolKeys = Object.getOwnPropertySymbols(obj);
  for (const key of symbolKeys) {
    copy[key] = deepClone(obj[key], visited);
  }

  return copy;
}
```

### 测试用例

```javascript
// 测试循环引用
const circular = { a: 1 };
circular.self = circular;
const circularCopy = deepClone(circular);
console.log(circularCopy.self === circularCopy); // true — 循环引用正确恢复

// 测试特殊类型
const special = {
  date: new Date('2026-06-18'),
  regex: /abc/gi,
  map: new Map([['key', 'value']]),
  set: new Set([1, 2, 3]),
  sym: Symbol('test'),
  fn: function() { return 42; },
  undef: undefined,
};
const specialCopy = deepClone(special);
console.log(specialCopy.date instanceof Date);   // true
console.log(specialCopy.regex instanceof RegExp); // true
console.log(specialCopy.map instanceof Map);      // true
console.log(specialCopy.set instanceof Set);      // true
console.log(typeof specialCopy.sym === 'symbol'); // true
console.log(typeof specialCopy.fn === 'function');// true
console.log(specialCopy.undef === undefined);     // true

// 验证独立性
specialCopy.date.setFullYear(2000);
console.log(special.date.getFullYear()); // 2026 — 原对象不受影响
```

---

## 四、处理特殊类型

| 类型 | 处理方式 | 说明 |
|------|---------|------|
| `Date` | `new Date(obj.getTime())` | 通过时间戳创建新实例 |
| `RegExp` | `new RegExp(obj.source, obj.flags)` | 拷贝模式和标志 |
| `Map` | 遍历 `forEach` 递归拷贝 key 和 value | key 也可能是对象 |
| `Set` | 遍历 `forEach` 递归拷贝 value | - |
| `Symbol` | `Object.getOwnPropertySymbols()` 获取 Symbol key | 单独处理 |
| `Function` | 直接返回原函数 | 函数不需要深拷贝，保持引用即可 |
| `Error` | `new Error(obj.message)` | 可选，根据需求处理 |

---

## 五、循环引用

循环引用是深拷贝中最容易踩坑的地方：

```javascript
const obj = { a: 1 };
obj.self = obj; // 循环引用
JSON.parse(JSON.stringify(obj)); // TypeError: Converting circular structure to JSON
```

**解决方案：使用 Map 记录已拷贝的对象**

```javascript
const visited = new Map();

function deepClone(obj) {
  if (visited.has(obj)) {
    return visited.get(obj); // 返回之前创建的副本，避免无限递归
  }
  // ... 创建副本并记录到 visited 中
}
```

`WeakMap` 也可以用于此场景，优势是当原对象被垃圾回收时，对应的映射也会自动清除，避免内存泄漏。但在深拷贝场景中，由于拷贝过程是同步的，`Map` 和 `WeakMap` 的效果基本一致。

---

## 六、第三方库

### lodash cloneDeep 实现思路

lodash 的 `cloneDeep` 是工业级实现，核心思路：

1. **类型标签检测**：使用 `Object.prototype.toString.call()` 获取精确的类型标签（如 `[object Date]`、`[object RegExp]`）
2. **克隆标记**：内部维护一个 `stack` 记录已克隆对象，处理循环引用
3. **缓冲区复用**：对某些类型使用内部缓冲区优化性能
4. **原型链处理**：可选是否克隆原型链上的属性
5. **ArrayBuffer/TypedArray 支持**：处理二进制数据
6. **惰性初始化**：只在需要时创建 visited 映射

简化版 lodash 思路：

```javascript
function cloneDeep(value, customizer, thisArg) {
  // 1. 调用自定义克隆器（如果有）
  if (customizer) {
    const result = customizer.call(thisArg, value);
    if (result !== undefined) return result;
  }

  // 2. 基本类型直接返回
  if (!isObject(value)) return value;

  // 3. 根据类型标签分发处理
  const tag = Object.prototype.toString.call(value);
  switch (tag) {
    case '[object Date]':
      return new Date(+value);
    case '[object RegExp]':
      return new RegExp(value.source, value.flags);
    case '[object Map]':
    case '[object Set]':
      // 遍历拷贝
    case '[object Array]':
      // 递归拷贝数组元素
    default:
      // 递归拷贝普通对象
  }
}
```

---

## 七、面试话术（30 秒版）

> "浅拷贝只复制第一层属性，嵌套对象仍共享引用，常用 `Object.assign` 或展开运算符。深拷贝递归复制所有层级，完全断开引用关系。`JSON.parse(JSON.stringify())` 简单但有缺陷：丢失 `undefined`、`Function`、`Symbol`，`Date` 变字符串，`RegExp` 变空对象，无法处理循环引用。完整的深拷贝需要用递归 + `Map` 记录已拷贝对象来处理循环引用，同时特殊处理 `Date`、`RegExp`、`Map`、`Set` 等类型。生产环境推荐用 `lodash.cloneDeep`。"

---

## 八、交叉引用

- 主模块：[`12.front-end`](../../../12.front-end/) — 前端知识体系
