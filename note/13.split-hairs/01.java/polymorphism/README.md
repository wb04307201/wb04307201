<!--
question:
  id: 01.java-polymorphism
  topic: 01.java
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 原理深挖
  tags: [01.java, polymorphism, override, vtable, default-method]
-->

# Java 多态面试深挖（4 大核心）

> ⬅️ [返回 Java 咬文嚼字](../README.md) | [主模块深度专题](../../../01.java/concepts/polymorphism/README.md)

> **一句话定位**：**4 大核心 Java 多态面试深挖**（校招+社招高频）：编译时 vs 运行时 / 重载 vs 重写 / vtable super / 接口 default 冲突。

---

## 🎯 4 大核心题

### Q1：编译时多态 vs 运行时多态有什么区别？

**陷阱**：
- ❌ 只答「重载是编译时多态，重写是运行时多态」（不够深）
- ❌ 不区分 `invokevirtual` / `invokestatic` / `invokespecial`

**30 秒话术**：
> 「**编译时多态 = 编译期就能确定调哪个**（`invokestatic` / `invokespecial`：静态方法、私有方法、构造方法、`final` 方法）。**运行时多态 = 运行期才确定**（`invokevirtual`：实例方法，从 vtable 查）。」

**90 秒话术**：
> 「**3 个字节码指令 + vtable 实现**：
>
> - `invokestatic` → 静态方法，**编译期绑定**
> - `invokespecial` → 私有方法 / 构造方法 / `super.method()`，**编译期绑定**
> - `invokevirtual` → 实例方法（虚方法），**运行期查 vtable**
>
> **vtable 关键事实**：① 类加载时建表，子类继承父类 vtable ② 子类 override 的方法**替换** vtable entry ③ 子类新增方法 **append** 到 vtable 末尾 ④ `invokevirtual` 字节码只存常量池方法引用 + nargs，**实际方法实现运行期从 obj 实际类型的 vtable 查**。
>
> **实战对比**：① 静态方法调用看**引用类型**（不看实际对象） ② 实例方法调用看**实际对象**（动态分派） ③ `private` 方法不算多态（不参与 vtable） ④ `final` 方法不参与 vtable 动态分派（编译期优化为 `invokespecial`）。记住：**JVM 的多态只对实例方法（virtual method）开放**，其他都走静态绑定。」

---

### Q2：重写 `@Override` 不是语法必需，但推荐用。为什么？

**陷阱**：
- ❌ 答「不加 `@Override` 编译器会报错」（不准确——只对接口实现报错，对类重写不报错）
- ❌ 不知道 `@Override` 不影响运行时

**30 秒话术**：
> 「`@Override` 是 **Java 5+ 注解**，作用 = **编译期校验**（验证方法确实是 override）。**不影响运行时**，JVM 不读取注解（默认 `RetentionPolicy.SOURCE`）。**强烈推荐用**。」

**90 秒话术**：
> 「**3 大价值 + 1 个误区**：
>
> - **价值 1**：编译期拦截签名错误（如父类方法改了形参，子类 `@Override` 立即编译失败，不会变成「看起来没重写」的 bug）
> - **价值 2**：接口 default / abstract 重写时显式声明（多接口同名方法二义性时一眼可辨）
> - **价值 3**：重构友好（父类签名变了，所有 `@Override` 子类立即报错，覆盖所有调用点）
>
> - **误区**：不加 `@Override` 也能重写——Java 编译器对「**方法名相同 + 形参一致 + 返回类型协变**」就视为重写，**运行时通过 vtable 分派**
>
> **反直觉细节**：① override 的方法**访问修饰符必须 ≥ 父类**（不能更严格，例如父类 `protected` 不能重写为 `private`） ② 子类**不能新抛 checked 异常**（只能更少或不抛） ③ **协变返回**（Java 5+）：子类 override 返回类型可以是父类返回类型的子类型，编译器自动生成**桥接方法**（bridge method）保证 vtable 签名匹配。」

---

### Q3：Java vtable 实际怎么实现？`super.method()` 怎么工作？

**陷阱**：
- ❌ 答「Java 有 vtable」（Yes，但具体结构？vtable vs itable 区别？`super` 指令是什么？）
- ❌ 不知道 `invokeinterface` 用的是 itable 而不是 vtable

**30 秒话术**：
> 「**HotSpot 用 vtable（虚方法表） + itable（接口方法表）**。`super.method()` 编译为 **`invokespecial`**，**跳过 vtable** 直接调指定类的方法（绕过动态分派）。」

**90 秒话术**：
> 「**vtable 详解（HotSpot 实例）**：
>
> - 类加载在方法区建 `Klass` 结构（C++ 对象），含 **method table**
> - 虚方法放 **vtable**，按方法签名 hash 索引
> - 子类继承父类 vtable，**子类 override 替换 entry**，新增方法 append
> - 实例方法调用 `invokevirtual`：从对象 header 的 Klass 指针找到 vtable，按常量池方法引用查 entry
>
> **itable**（接口方法表，Java 8+ 重要，default 方法出现后必须）：
>
> - 当类实现多个接口，编译器为该类生成一个 **itable**
> - 存储 default 方法入口 + 抽象方法入口（按接口名 + 方法签名组织）
> - `invokeinterface` 从对象头找到 itable，再 vtable dispatch
>
> **`super.method()` 工作机制**：
>
> - **编译时**：方法调用前加 `super.` 前缀 → 编译成 `invokespecial #SuperKlass.method`，常量池引用已经**绑定到具体父类**
> - **运行期**：直接调 SuperKlass（指定类）的方法，**不查 vtable**，**不走动态分派**
> - **实战 1**：构造函数中 `super(xxx)` 必须第一行（编译期校验，JVM 强制）
> - **实战 2**：重写父类时 `super.method()` 复用父类逻辑（模板方法模式的核心），等价于「绕过自己的 override，直奔父类实现」」

---

### Q4：Java 8 接口 default 方法，多接口冲突怎么解决？

**陷阱**：
- ❌ 答「编译器直接报错」（只对了一半——某些情况能自动消歧）
- ❌ 不知道钻石继承问题的完整优先级规则

**30 秒话术**：
> 「**3 大冲突解决规则**（按优先级）：① **类方法**（实例方法 / 抽象方法）胜 default 方法 ② **子类 override** 胜所有 default ③ 否则**必须显式指定** `InterfaceName.super.method()`。否则编译报错。」

**90 秒话术**：
> 「**钻石继承问题**（Diamond Problem）：
>
> ```java
> interface A { default void hello() { System.out.println(\"A\"); } }
> interface B { default void hello() { System.out.println(\"B\"); } }
> class C implements A, B {
>     // 编译错误: ambiguous inherited from A and B, must override
> }
> ```
>
> **Java 8+ 3 大冲突解决规则**（按优先级，**类胜接口**）：
>
> 1. **类方法 > 任何 default 方法** —— 如果 C 自己有实例方法 `hello()`，优先用 C 的
> 2. **更具体接口的方法胜出** —— 如果 A extends B 且 A 有 `default hello()`，实现 A 的类用 A 的方法（B 的被屏蔽）
> 3. **必须显式指定** —— 否则编译错误，调用 `A.super.hello()` 显式选择
>
> **实战细节**：① **Java 9+ 接口可以 private 方法**（default 方法内部复用，避免暴露实现细节） ② 接口 **static 方法**不属于实例方法（**不参与 default 方法冲突**） ③ **不要随意加 default**：会强制所有实现类必须遵守新行为（**破坏接口兼容性**——一旦发了 default，再删就编译报错）。Map 接口的 `putIfAbsent` / `getOrDefault` / `forEach` 是 Java 8 default 演化经典案例。」

---

## 🔗 兄弟章节

- 主模块深度链：[01.java/concepts/polymorphism](../../../01.java/concepts/polymorphism/README.md) — 多态专题（重载 vs 重写 + 编译时 vs 运行时分派 + vtable + default + 协变返回）
- 兄弟面试题：
  - [object](../object/README.md) — 为什么需要 Integer / Double 包装类？
  - [reflection](../reflection/README.md) — Reflection API 使用与性能开销
  - [final-finally-finalize](../final-finally-finalize/README.md) — 三个关键字的区别与用法
  - [equals-hashcode](../equals-hashcode/README.md) — 相等性判断契约与陷阱

---

## 📊 4 题难度速查表

| 题 | 难度 | 频率 | 关键数字 |
|---|------|------|---------|
| Q1 编译时 vs 运行时 | ⭐⭐⭐ | 高频 | 3 字节码指令 / vtable 4 事实 / final 优化 |
| Q2 @Override | ⭐⭐⭐ | 高频 | 1 注解 + 3 价值 + 协变返回 + 桥接方法 |
| Q3 vtable super | ⭐⭐⭐⭐ | 高频 | vtable + itable + invokespecial |
| Q4 接口 default 冲突 | ⭐⭐⭐⭐ | 高频 | 3 优先级规则 + A.super 显式 |

---

## 📚 参考来源

1. [JLS §8.4.8 Override 等价签名](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.4.8) — 方法重写的签名匹配、协变返回与异常约束。
2. [JLS §15.12 方法调用表达式](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.12) — 编译期与运行期方法选择、`invokestatic` / `invokespecial` / `invokevirtual` / `invokeinterface` 分派语义。
3. [JLS §9.4 接口成员 / §9.4.1 默认方法](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html#jls-9.4) — default 方法的继承、冲突解决与 `InterfaceName.super.method` 显式选择。
4. [HotSpot VM Internals: Klass / vtable / itable](https://github.com/openjdk/jdk/blob/master/src/hotspot/share/oops/klass.hpp)（二手来源） — C++ Klass 结构、虚方法表与接口方法表的内存布局。
5. [Aleksey Shipilëv: The Black Magic of (Java) Method Dispatch](https://shipilev.net/blog/2015/black-magic-method-dispatch/) — JIT 编译期/运行期方法分派、内联缓存与 vtable 实战基准。

---

← 返回 [Java 咬文嚼字](../README.md)