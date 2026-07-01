# 基本语法

## 引言：基础概念

基本语法 是入门必学的基础概念。

本篇给出一句话定义 + 最小可运行示例 + 3 个常见误区，**5 分钟读完，10 分钟上手**。

---

## 注释的3种方式

- **单行注释**（`//`）：通常用于解释方法内某单行代码的作用
- **多行注释**（`/* */`）：通常用于解释一段代码的作用
- **文档注释**（`/** */`）：通常用于生成 Java 开发文档（可被 `javadoc` 工具提取）

## Java语言关键字

<table>
  <thead>
    <tr>
      <th>分类</th>
      <th colspan="7">关键字</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>访问控制</td>
      <td>private</td>
      <td>protected</td>
      <td>public</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>类，方法和变量修饰符</td>
      <td>abstract</td>
      <td>class</td>
      <td>extends</td>
      <td>final</td>
      <td>implements</td>
      <td>interface</td>
      <td>native</td>
    </tr>
    <tr>
      <td></td>
      <td>new</td>
      <td>static</td>
      <td>strictfp</td>
      <td>synchronized</td>
      <td>transient</td>
      <td>volatile</td>
      <td>enum</td>
    </tr>
    <tr>
      <td></td>
      <td>void</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>程序控制</td>
      <td>break</td>
      <td>continue</td>
      <td>return</td>
      <td>do</td>
      <td>while</td>
      <td>if</td>
      <td>else</td>
    </tr>
    <tr>
      <td></td>
      <td>for</td>
      <td>instanceof</td>
      <td>switch</td>
      <td>case</td>
      <td>default</td>
      <td>assert</td>
      <td>yield</td>
    </tr>
    <tr>
      <td>错误处理</td>
      <td>try</td>
      <td>catch</td>
      <td>throw</td>
      <td>throws</td>
      <td>finally</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>包相关</td>
      <td>import</td>
      <td>package</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>基本类型</td>
      <td>boolean</td>
      <td>byte</td>
      <td>char</td>
      <td>double</td>
      <td>float</td>
      <td>int</td>
      <td>long</td>
    </tr>
    <tr>
      <td></td>
      <td>short</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>变量引用</td>
      <td>super</td>
      <td>this</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>保留字</td>
      <td>goto</td>
      <td>const</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>受限关键字 (Restricted Keywords)</td>
      <td>record <sup>Java 16</sup></td>
      <td>sealed <sup>Java 17</sup></td>
      <td>permits <sup>Java 17</sup></td>
      <td>non-sealed <sup>Java 17</sup></td>
      <td>yield <sup>Java 14</sup></td>
      <td>var <sup>Java 10</sup></td>
      <td></td>
    </tr>
  </tbody>
</table>

> **受限关键字**：仅在特定上下文中具有特殊含义，在其他位置可作为普通标识符使用（但强烈建议避免）。
> 例如 `record` 仅在类型声明中是关键字，`yield` 仅在 switch 表达式中是关键字。

## 标识符和关键字的区别

标识符是程序员自定义的名字（如变量名、方法名、类名），关键字是 Java 语言保留的、具有特殊语法含义的词（如 `class`、`public` 等）。在 JLS（Java 语言规范）中，关键字和标识符是两种互斥的词法单元（token），标识符不能使用关键字命名。

## `var` 局部变量类型推断（Java 10+）

`var` 是 Java 10 引入的**受限标识符（restricted identifier）**，用于局部变量类型推断，编译器会根据右侧初始值自动推断变量类型。

```java
var list = new ArrayList<String>();     // 推断为 ArrayList<String>
var map = new HashMap<String, Integer>(); // 推断为 HashMap<String, Integer>
```

> **注意**：上表将 `var` 归入"受限关键字"是宽松分类。严格来说，按 JLS（Java 语言规范），`var` 不是关键字，而是**受限标识符（restricted identifier）**——它在局部变量声明上下文中具有特殊含义，但在其他位置仍可作为普通标识符使用。
>
> 完整说明（适用场景、使用限制、与 `final` 结合等）参见 [variable/README.md](../variable/README.md#var-局部变量类型推断java-10)。

## `continue`、`break`和`return`的区别

- **`continue`**：跳出当前的这一次循环，继续下一次循环迭代
- **`break`**：跳出整个循环体，继续执行循环后面的语句
- **`return`**：结束方法执行，直接返回
- **`return value`**：结束方法执行，并返回一个特定值

```java
for (int i = 0; i < 10; i++) {
    if (i == 3) continue;     // 跳过 i=3，继续 i=4
    if (i == 7) break;        // i=7 时终止整个循环
    System.out.println(i);    // 输出: 0 1 2 4 5 6
}
```

## 运算符

### 运算符优先级（从高到低）

| 优先级 | 运算符 | 说明 |
|-------|--------|------|
| 1 | `()` `[]` `.` `expr++` `expr--` | 括号、数组访问、成员访问、后缀运算符 |
| 2 | `++expr` `--expr` `!` `~` `+` `-` `(type)` | 前缀一元运算符 |
| 3 | `*` `/` `%` | 乘除取模 |
| 4 | `+` `-` | 加减 |
| 5 | `<<` `>>` `>>>` | 移位 |
| 6 | `<` `<=` `>` `>=` `instanceof` | 比较 |
| 7 | `==` `!=` | 相等性 |
| 8 | `&` | 按位与 |
| 9 | `^` | 按位异或 |
| 10 | `\|` | 按位或 |
| 11 | `&&` | 逻辑与（短路） |
| 12 | `\|\|` | 逻辑或（短路） |
| 13 | `?:` | 三元运算符 |
| 14 | `=` `+=` `-=` `*=` `/=` 等 | 赋值 |
| 15 | `->` `::` | Lambda 箭头（Java 8+）、方法引用（Java 8+），优先级最低 |

> **示例**：`list.forEach(e -> System.out.println(e));` 等价于 `list.forEach(System.out::println);`
> 其中 `->` 和 `::` 的优先级低于赋值运算符，因此 `Runnable r = () -> doSomething();` 会先计算赋值，再构造 Lambda。

### `&&` 与 `&`、`||` 与 `|` 的区别

- **`&&`（短路与）**：如果左操作数为`false`，不会计算右操作数
- **`&`（非短路与）**：无论左操作数结果如何，都会计算右操作数
- **`||`（短路或）**：如果左操作数为`true`，不会计算右操作数
- **`|`（非短路或）**：无论左操作数结果如何，都会计算右操作数

```java
// 短路保护 - 如果 obj 为 null，不会执行 obj.method()，避免 NPE
if (obj != null && obj.isValid()) { /* 安全调用 */ }

// 位运算 - & 和 | 也可以用于整数位运算
int a = 5 & 3;  // 0101 & 0011 = 0001 = 1
int b = 5 | 3;  // 0101 | 0011 = 0111 = 7
```
