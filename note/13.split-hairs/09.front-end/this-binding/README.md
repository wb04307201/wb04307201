# this 绑定规则 5 种详解

> 一句话：this 不是词法作用域，而是运行时绑定；由函数调用方式决定，而非定义位置。

---

## 一、核心原理

JavaScript 中的 `this` 是**运行时**绑定，不指向函数自身或词法作用域，完全取决于**调用方式**。

```javascript
var a = 2;
var obj = { a: 1, foo() { console.log(this.a); } };

obj.foo(); // 1（隐式绑定）
(obj.foo = obj.foo)(); // 2（默认绑定）
```

关键点：
- `this` 与声明位置无关，与调用方式相关
- 每次调用可能产生不同的 `this`

---

## 二、5 种绑定规则

### 1. 默认绑定（Default Binding）

独立函数调用时触发。非严格模式 `this` 指向全局对象（`window`），严格模式为 `undefined`。

```javascript
var a = "global";
function foo() { console.log(this.a); }
foo(); // "global"

function bar() { "use strict"; console.log(this); }
bar(); // undefined
```

### 2. 隐式绑定（Implicit Binding）

作为对象方法调用时，`this` 指向调用对象。

```javascript
var obj = { name: "obj", greet() { console.log(this.name); } };
obj.greet(); // "obj"
```

**隐式丢失陷阱**：方法赋值给变量后独立调用，退化为默认绑定。

```javascript
var name = "global";
var fn = obj.greet;
fn(); // "global"
```

### 3. 显式绑定（Explicit Binding）

通过 `call` / `apply` / `bind` 显式指定 `this`。

```javascript
function greet() { console.log("Hello, " + this.name); }
greet.call({ name: "Alice" });   // "Hello, Alice"
greet.apply({ name: "Bob" });    // "Hello, Bob"

var greetAlice = greet.bind({ name: "Alice" });
greetAlice(); // "Hello, Alice"
```

| 方法 | 执行时机 | 参数形式 | 返回值 |
|------|---------|---------|--------|
| `call` | 立即执行 | 逐个传入 | 原函数返回值 |
| `apply` | 立即执行 | 数组传入 | 原函数返回值 |
| `bind` | 返回新函数 | 逐个传入 | 新函数 |

**偏函数应用**：

```javascript
var double = function(a, b) { return a * b; }.bind(null, 2);
double(5); // 10
```

### 4. new 绑定（New Binding）

`new` 调用构造函数时，`this` 指向新创建的对象。

```javascript
function Person(name) { this.name = name; }
var alice = new Person("Alice");
console.log(alice.name); // "Alice"
```

内部过程：
1. 创建新对象
2. 链接 `__proto__` 到 `prototype`
3. `this` 绑定到新对象
4. 返回新对象（若无其他返回）

### 5. 箭头函数（Arrow Function）

箭头函数**没有自己的 `this`**，从外层作用词法继承，且无法被修改。

```javascript
var obj = {
  name: "obj",
  greet() {
    var arrow = () => console.log(this.name);
    arrow();
  }
};
obj.greet(); // "obj"
```

```javascript
var arrow = () => console.log(this);
arrow.call({}); // 仍输出外层 this，无法修改
```

---

## 三、优先级

```
new 绑定 > 显式绑定 > 隐式绑定 > 默认绑定
```

箭头函数不参与优先级比较（词法继承）。

```javascript
function foo() { console.log(this.a); }
var obj1 = { a: 1, foo };
var obj2 = { a: 2 };

obj1.foo();           // 1（隐式）
obj1.foo.call(obj2);  // 2（显式 > 隐式）

var bound = foo.bind(obj1);
new bound();          // this 指向新对象（new > 显式）
```

---

## 四、代码示例 + 陷阱

### 陷阱 1：回调中隐式丢失

```javascript
var name = "global";
var obj = { name: "obj", greet() { console.log(this.name); } };
setTimeout(obj.greet, 100); // "global"
```

**修复**：

```javascript
setTimeout(obj.greet.bind(obj), 100); // "obj"
setTimeout(() => obj.greet(), 100);   // "obj"
```

### 陷阱 2：定时器中的 this

```javascript
var timer = {
  count: 0,
  start() {
    setInterval(function() {
      this.count++; // this 指向 window
    }, 1000);
  }
};
```

**修复**：使用箭头函数（推荐）或保存 `this` 引用。

```javascript
start() {
  setInterval(() => { this.count++; }, 1000);
}
```

### 陷阱 3：事件处理函数

```javascript
button.addEventListener("click", function() {
  console.log(this); // DOM 元素
});
button.addEventListener("click", () => {
  console.log(this); // 外层作用域的 this
});
```

### 陷阱 4：嵌套对象

```javascript
var obj = {
  name: "outer",
  inner: { name: "inner", greet() { console.log(this.name); } }
};
obj.inner.greet(); // "inner"（只有最后一层生效）
```

---

## 五、最佳实践

### 1. 回调/定时器优先用箭头函数

```javascript
class Counter {
  constructor() { this.count = 0; }
  start() { setInterval(() => { this.count++; }, 1000); }
}
```

### 2. bind 适用场景

- 事件处理函数确保 `this` 指向
- 偏函数应用/柯里化
- 借用方法（如 `Array.prototype.slice.call`）

```javascript
class Button {
  constructor(el) {
    this.el = el;
    this.el.addEventListener("click", this.handleClick.bind(this));
  }
  handleClick() { console.log(this.el); }
}
```

### 3. 避免对象方法用箭头函数

```javascript
// ❌ 错误
var obj = { name: "obj", greet: () => console.log(this.name) };

// ✅ 正确
var obj = { name: "obj", greet() { console.log(this.name); } };
```

### 4. 类中统一用箭头函数或 bind

```javascript
class Component {
  handleClick = () => { console.log(this.state.count); }; // 推荐
}
```

---

## 六、面试话术（30 秒版）

> "`this` 是 JavaScript 中运行时绑定的机制，共有五种绑定规则。第一种是**默认绑定**，独立函数调用时，非严格模式下 `this` 指向 `window`，严格模式为 `undefined`。第二种是**隐式绑定**，作为对象方法调用时 `this` 指向该对象，但存在隐式丢失的问题。第三种是**显式绑定**，通过 `call`、`apply`、`bind` 可以手动指定 `this`。第四种是 **new 绑定**，构造函数调用时 `this` 指向新创建的对象。第五种是**箭头函数**，它没有自己的 `this`，会从外层作用域继承。优先级方面，`new` 绑定最高，其次是显式绑定、隐式绑定，最后是默认绑定。实际开发中，我通常用箭头函数来解决回调中的 `this` 问题。"

---

## 七、交叉引用

- 主模块：[`09.front-end`](../../../09.front-end/) — 前端知识体系
- [语言基础](../../../09.front-end/02-language/README.md) — JavaScript 核心概念
