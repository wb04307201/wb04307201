<!--
question:
  id: 01.java-reflection
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [01.java, reflection]
-->

# Java 反射原理与性能深度剖析

## 引子：一个"不可能"的操作

```java
// 你拿到了一个私有的方法
class Secret {
    private String password = "12345";
    private void hackMe() { System.out.println("hacked!"); }
}

// 正常情况下根本调不了
Secret s = new Secret();
// s.password;      // 编译报错
// s.hackMe();      // 编译报错

// 但反射可以做到！
Field f = Secret.class.getDeclaredField("password");
f.setAccessible(true);
System.out.println(f.get(s));  // "12345" ？？？

Method m = Secret.class.getDeclaredMethod("hackMe");
m.setAccessible(true);
m.invoke(s);  // "hacked!" ？？？
```

私有字段、私有方法，编译期完全不可见，运行时却被强行访问。这就是**反射**的力量。

但天下没有免费的午餐——反射的性能代价有多大？

---

## 一、核心原理

> 📚 **前置知识**：[反射](../../../01.java/concepts/reflection/README.md)

### 1.1 Class 对象的四种获取方式

| 方式 | 示例 | 特点 |
|------|------|------|
| `.class` 字面量 | `String.class` | 编译期确定，不触发类加载初始化 |
| `getClass()` | `"hello".getClass()` | 运行时获取，适用于实例对象 |
| `Class.forName()` | `Class.forName("java.lang.String")` | **触发类初始化**（执行 static 块），最常用 |
| `ClassLoader.loadClass()` | `classLoader.loadClass("com.example.MyClass")` | 仅加载不初始化，用于自定义类加载器场景 |

**关键区别**：`Class.forName()` 会执行 `<clinit>`（静态初始化块），而 `ClassLoader.loadClass()` 只执行 `<clinit>` 之前的加载阶段（loading → linking）。在 JDBC 驱动注册等场景中，必须使用 `Class.forName()` 确保静态代码执行。

### 1.2 反射 API 体系

```text
java.lang.Class<T>          ← 入口：描述类的元数据
├── java.lang.reflect.Field     ← 字段（get/set/getName/getType）
├── java.lang.reflect.Method    ← 方法（invoke/getName/getParameterTypes/getReturnType）
├── java.lang.reflect.Constructor ← 构造器（newInstance/getParameterTypes）
└── java.lang.reflect.Modifier  ← 修饰符工具（isPublic/isPrivate/isFinal）
```

**核心能力**：
- **自省**：`getDeclaredFields()`、`getMethods()`、`getAnnotations()` 等读取元数据
- **动态调用**：`method.invoke(obj, args)`、`constructor.newInstance(args)`
- **访问突破**：`field.setAccessible(true)` 绕过 private/protected 检查
- **泛型擦除后读取**：通过 `Field.getGenericType()` 读取声明时的泛型签名（但运行时已擦除）

---

## 二、反射调用流程

### 2.1 标准三步走

```java
// ① 获取 Class 对象（触发类初始化）
Class<?> clazz = Class.forName("com.example.UserService");

// ② 获取 Method 对象（缓存复用，避免重复查找）
Method method = clazz.getMethod("findById", Long.class);

// ③ 动态调用（核心开销所在）
Object result = method.invoke(instance, 1L);
```

**底层链路**：
```text
Method.invoke()
  → DelegatingMethodAccessorImpl.invoke()   ← 委派层（前 15 次走 NativeAccessor）
    → NativeMethodAccessorImpl.invoke0()    ← JNI 调用（解释执行，极慢）
      → 第 15 次调用后触发"膨胀"（inflation）
        → 动态生成字节码 MethodAccessorImpl_XXX  ← ASM 生成直接调用指令
          → 后续调用走生成的字节码（接近直接调用速度）
```

**膨胀阈值**：JVM 参数 `-Dsun.reflect.inflationThreshold=15` 控制，前 15 次走 Native 路径，第 16 次开始生成字节码代理类。可通过 `-Dsun.reflect.noInflation=true` 强制直接生成字节码（启动稍慢，但长期运行更快）。

### 2.2 动态代理中的反射

Spring AOP 的 JDK 动态代理本质是反射 + 代理模式：

```java
// Proxy.newProxyInstance 内部为每个方法生成：
public Object invoke(Object proxy, Method method, Object[] args) {
    // 前置通知
    advice.before(method);
    // 反射调用目标方法
    Object result = method.invoke(target, args);
    // 后置通知
    advice.after(method);
    return result;
}
```

每次代理方法调用都经过 `method.invoke()`，因此高频调用场景下反射性能直接影响 AOP 吞吐量。CGLIB 通过字节码生成子类重写方法，避免了反射调用，但引入了类加载开销。

---

## 三、性能问题

### 3.1 性能对比表格

| 调用方式 | 相对耗时（ns） | 倍数关系 | 说明 |
|----------|---------------|---------|------|
| 直接调用 | ~5 ns | 1x | JIT 内联优化后的理想情况 |
| `setAccessible(true)` + 反射 | ~50-80 ns | 10-15x | 跳过安全检查，但仍需参数装箱 |
| 普通反射调用 | ~500-800 ns | 100-150x | 首次调用含 Native 路径，膨胀后降至 ~100 ns |
| MethodHandle | ~20-30 ns | 4-6x | 可被 JIT 内联，接近直接调用 |
| LambdaMetafactory | ~10-15 ns | 2-3x | 动态生成 lambda 字节码，几乎零开销 |

**测试环境参考**：JDK 17, macOS M1, JMH 基准测试，预热 10 轮，每轮 10000 次调用取平均值。

### 3.2 慢的根本原因

1. **安全检查开销**：每次 `invoke()` 内部调用 `AccessController.doPrivileged()` 验证权限（private/protected 成员访问检查）
2. **参数装箱/拆箱**：基本类型（int/long）需包装为 `Integer/Long`，产生 GC 压力
3. **数组拷贝**：`invoke()` 的 `Object[] args` 需要防御性拷贝防止外部修改
4. **JIT 内联失效**：反射调用目标是动态确定的，JIT 无法在编译期内联，失去常量折叠、逃逸分析等优化
5. **异常处理成本**：反射调用抛出 `InvocationTargetException`，需要额外 unwrap 原始异常

---

## 四、优化手段

### 4.1 setAccessible(true) —— 跳过安全检查

```java
Method method = clazz.getDeclaredMethod("privateMethod");
method.setAccessible(true);  // 核心：绕过 AccessController.doPrivileged 检查
method.invoke(obj);           // 不再验证权限，直接执行
```

**原理**：`AccessibleObject.setAccessible(true)` 将内部的 `override` 标志位设为 true，后续 `invoke()` 检测到该标志后跳过 `Reflection.verifyMemberAccess()` 调用。注意这需要 JVM 启动参数 `--add-opens` 或在模块化系统中开放对应包（JDK 9+ 强封装后更为严格）。

**风险**：绕过封装可能导致安全漏洞（见第五节），生产环境慎用。

### 4.2 MethodHandle vs 反射

```java
// MethodHandle 方式（JDK 7+）
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle handle = lookup.findVirtual(UserService.class, "findById",
    MethodType.methodType(User.class, Long.class));
User user = (User) handle.invokeExact(instance, 1L);
```

**优势**：
- **JIT 友好**：`MethodHandle` 是 `final` 类且调用链清晰，JIT 可内联优化
- **类型安全**：`invokeExact()` 在编译期检查参数类型和返回类型
- **无膨胀过程**：不存在"前 15 次慢"的问题，始终稳定
- **支持函数式组合**：可与 `LambdaMetafactory` 配合生成 lambda

**劣势**：API 较复杂，学习曲线陡峭；`Lookup` 对象创建有权限限制（只能访问当前上下文可见的成员）。

### 4.3 LambdaMetafactory —— 终极方案

```java
// 动态生成 lambda 调用点（JDK 8+）
CallSite site = LambdaMetafactory.metafactory(
    lookup,
    "apply",
    MethodType.methodType(Function.class),
    MethodType.methodType(User.class, Long.class),
    handle,
    MethodType.methodType(User.class, Long.class)
);
Function<Long, User> func = (Function<Long, User>) site.getTarget().invokeExact();
User user = func.apply(1L);  // 几乎零开销
```

**原理**：`LambdaMetafactory` 在运行时动态生成一个匿名类实现函数式接口，该类内部持有 `MethodHandle` 的直接引用。首次生成有类加载开销，但后续调用等同于直接调用接口的 `apply()` 方法，JIT 可完全内联。

**适用场景**：高频调用的函数式编程场景（如 Stream 中的 map/filter）、RPC 框架的动态代理、序列化框架的字段访问器生成。

### 4.4 缓存复用

```java
// 错误示范：每次都重新查找 Method（极慢）
for (int i = 0; i < 10000; i++) {
    Method m = clazz.getMethod("findById", Long.class);  // 重复查找
    m.invoke(obj, i);
}

// 正确做法：缓存 Method 对象
Method cachedMethod = clazz.getMethod("findById", Long.class);
for (int i = 0; i < 10000; i++) {
    cachedMethod.invoke(obj, i);  // 复用已查找的 Method
}
```

`Class.getMethod()` 内部会遍历所有方法并匹配签名，虽然 JVM 有内部缓存，但显式缓存仍可减少 HashMap 查找开销。

---

## 五、常见陷阱

### 5.1 泛型擦除后的反射局限

```java
List<String> list = new ArrayList<>();
// 运行时无法通过反射获取泛型参数 T 的具体类型
Type type = field.getGenericType();  // 只能读取声明时的签名 "Ljava/util/List<Ljava/lang/String;>;"
// 但无法在运行时判断某个 List 实例是否是 List<String> 还是 List<Integer>
```

**影响**：JSON 反序列化库（Jackson/Gson）需要通过 `TypeReference` 或 `@JsonProperty` 显式传递泛型信息，因为运行时 `list.getClass()` 只返回 `ArrayList`，丢失了 `<String>` 信息。

### 5.2 final 方法无法通过反射"修改"

反射可以调用 private 方法，但**不能改变方法的语义**：
- `final` 方法仍可正常调用，但不能被子类重写（这是编译期决定的）
- `private` 字段可通过 `field.set()` 修改，但 `final` 字段在 JDK 12+ 中即使 `setAccessible(true)` 也无法修改（JEP 371 强化封装）

```java
Field field = clazz.getDeclaredField("CONSTANT");
field.setAccessible(true);
field.set(obj, newValue);  // JDK 12+: 抛出 IllegalAccessException
```

### 5.3 安全性风险

```java
// 危险操作：反射修改 private 字段
Field passwordField = User.class.getDeclaredField("password");
passwordField.setAccessible(true);
passwordField.set(user, "hacked");  // 绕过所有业务逻辑直接修改
```

**风险点**：
- **破坏封装**：攻击者可通过反射修改 `private` 字段绕过校验逻辑（如权限标志、余额检查）
- **RCE 漏洞**：某些反序列化漏洞（Fastjson/ColdFusion）利用反射链执行任意代码
- **模块系统绕过**：JDK 9+ 的 `--add-opens` 参数若配置不当，会暴露内部 API 给恶意代码

**防护建议**：
- 生产环境启用 SecurityManager 或使用 `-XX:+UnlockDiagnosticVMOptions -XX:+ShowHiddenFrames` 审计反射调用
- 敏感字段使用 `VarHandle`（JDK 9+）替代 `Field`，提供更细粒度的访问控制
- 框架层面通过注解（如 `@ReflectiveAccess`）白名单控制允许反射的类

### 5.4 Spring 中的反射应用与优化

**IoC 容器**：`BeanUtils.instantiateClass()` 通过 `Constructor.newInstance()` 创建 Bean，首次启动时大量反射导致冷启动慢。Spring 5 引入 `InstantiationAwareBeanPostProcessor` 缓存构造器引用。

**AOP 代理**：JDK 动态代理每次方法调用都经过 `ReflectiveMethodInvocation.proceed()` → `method.invoke()`。高频接口建议使用 CGLIB（字节码继承）或 AspectJ（编译期织入）避免反射开销。

**PropertyAccess**：`BeanWrapperImpl.setPropertyValue()` 内部使用 `CachedIntrospectionResults` 缓存 `PropertyDescriptor`，避免重复反射查找 getter/setter。

---

## 六、面试话术（30 秒版）

> "反射的核心价值是**运行时动态性**，让框架能在编译期未知的情况下操作类。但它有三个性能瓶颈：一是每次 invoke 都要做权限检查，二是参数装箱拆箱产生 GC，三是 JIT 无法内联导致 CPU 流水线失效。优化思路分三层：轻量级用 `setAccessible(true)` 跳过检查；中量级用 `MethodHandle` 让 JIT 能内联；重量级用 `LambdaMetafactory` 动态生成字节码彻底消除反射开销。实际项目中，Spring 的 Bean 创建和 AOP 都用到了反射，所以冷启动慢，但通过缓存 Class/Method 对象和 CGLIB 代理缓解了这个问题。"

---

## 七、交叉引用

- 主模块：[`01.java`](../../../01.java/) — Java 知识体系
- 相关主题：
  - [JVM 类加载](../../../01.java/jvm/README.md) — 类加载机制与双亲委派
  - [volatile 与内存模型](../../../01.java/concurrency/volatile/README.md) — volatile 与内存模型
  - [代理模式](../../../01.java/design-patterns/README.md) — 代理模式与动态代理
  - [Spring AOP](../../../06.spring/08-annotations/aop.md) — Spring AOP 实现原理

## 相关章节

- 深度阅读：[`01.java`](../../01.java/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · reflection](../README.md)
