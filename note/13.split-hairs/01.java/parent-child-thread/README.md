<!--
question:
  id: 01.java-parent-child-thread
  topic: 01.java
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [01.java, parent, child]
-->

# Java 父子线程数据传递：3 种方案横跨 JDK + 阿里开源

> 经典 Java 面试题（阿里、字节、美团高频）。考察的不是"会不会用 ThreadLocal"，而是 **JDK 原生方案的 3 个限制** + **阿里 TransmittableThreadLocal 的设计精髓** + **线程池场景下的最佳实践**。

## 引子：审计日志 userId 全是 anonymous

```text
你的阿明：
- 主线程里：currentUserTL.set("admin_001")
- Web 请求进来 → 异步线程池里 @Async 写审计日志
- 日志出来：userId=anonymous
- 排查 2 小时才发现：ThreadLocal 在线程池里完全失效
```

**真相**：ThreadLocal 把 value 存在 `Thread.threadLocals`（每个线程独立）。
- `new Thread()` 单次创建：子线程能继承（用 InheritableThreadLocal）
- 线程池：worker 线程**复用**，初始化时只继承一次 → 完全失效

**3 大场景的解法**：

1. **`new Thread()` 单次传**：InheritableThreadLocal（JDK 原生，但线程池失效）
2. **线程池 + 全链路 TraceId / 用户上下文**：TransmittableThreadLocal（阿里开源，工业级）
3. **纯 JDK 临时方案**：CompletableFuture 包装（手动捕获+设置，侵入性强）

## 一、核心结论（TL;DR）

| 方案 | 适用场景 | 限制 |
|------|---------|------|
| **`InheritableThreadLocal`** | 单次父子线程传递（如 `new Thread()`） | ❌ 线程池失效 / 线程复用失效 |
| **`TransmittableThreadLocal`**（阿里） | 线程池 / 异步调用 / 全链路 TraceId | 需引入 `transmittable-thread-local` 依赖 |
| **`CompletableFuture` 包装** | 纯 JDK 方案 / 临时方案 | 需手动封装 / 侵入性强 |

> 一句话：**线程池场景下，InheritableThreadLocal 完全失效；阿里 TransmittableThreadLocal 是工业级标准方案**。

---

## 二、问题起源：ThreadLocal 不能跨线程

```java
// 主线程设置 userId
ThreadLocal<String> userIdTL = new ThreadLocal<>();
userIdTL.set("user_123");

// 子线程读取 —— ❌ null
new Thread(() -> {
    System.out.println(userIdTL.get());  // null
}).start();
```

**根因**：ThreadLocal 的 value 存在 `Thread.threadLocals`（`ThreadLocalMap`），每个线程独立。

---

## 三、方案 1：InheritableThreadLocal（JDK 原生）

### 1. 基本用法

```java
InheritableThreadLocal<String> userIdTL = new InheritableThreadLocal<>();

userIdTL.set("user_123");  // 主线程

new Thread(() -> {
    System.out.println(userIdTL.get());  // ✅ "user_123"
}).start();
```

### 2. 工作原理

`Thread.init()` 时，如果父线程的 `inheritableThreadLocals` 不为空，会浅拷贝到子线程。

### 3. 3 个致命限制

#### 限制 1：线程池场景完全失效

```java
ExecutorService pool = Executors.newFixedThreadPool(2);

// 任务 1：在主线程设置 TL，提交到线程池
userIdTL.set("user_123");
pool.submit(() -> {
    System.out.println(userIdTL.get());  // ❌ null（线程池线程是复用的）
});
```

**原因**：线程池的 worker 线程是**复用**的，子线程创建时只继承了创建那一刻的父线程值；后续提交时父线程值变了，worker 线程感知不到。

#### 限制 2：线程复用时旧值"残留"

```java
pool.submit(() -> {
    System.out.println(userIdTL.get());  // ❌ "user_456"（上次任务的残留值）
});
```

#### 限制 3：父子线程是"浅拷贝"

```java
InheritableThreadLocal<List<String>> listTL = new InheritableThreadLocal<>();
listTL.set(new ArrayList<>(Arrays.asList("a")));

new Thread(() -> {
    List<String> list = listTL.get();
    list.add("b");  // 修改子线程的 list，会影响父线程吗？
    // 答案：不影响（浅拷贝，新 List 对象），但若父线程修改 list 内容，子线程的引用会同步
}).start();
```

---

## 四、方案 2：TransmittableThreadLocal（阿里开源）

### 1. 基本用法

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>transmittable-thread-local</artifactId>
    <version>2.14.5</version>
</dependency>
```

```java
TransmittableThreadLocal<String> ttl = new TransmittableThreadLocal<>();
ttl.set("user_123");

// 关键：用 TtlRunnable 包装
ExecutorService pool = Executors.newFixedThreadPool(2);
pool.submit(TtlRunnable.get(() -> {
    System.out.println(ttl.get());  // ✅ "user_123"
}));
```

### 2. 工作原理（3 步）

```text
任务提交时：
  ① capture()：从当前线程捕获 TTL 值到 holder
  ② 包装成 TtlRunnable，把 holder 传过去
任务执行时：
  ③ replay()：把 holder 的值设置到 worker 线程
  ④ restore()：执行完后恢复 worker 线程的原值
```

### 3. 4 大核心优势

| 优势 | 解释 |
|------|------|
| **线程池兼容** | 用 TtlRunnable/TtlCallable 包装，自动 capture + replay |
| **跨线程池透传** | A 线程池 → B 线程池，TTL 不丢失 |
| **无侵入业务代码** | 业务代码只需 `ttl.get()` |
| **Java Agent 模式** | 用 `-javaagent:` 自动包装所有 Runnable（无需改代码） |

### 4. Java Agent 模式（最常用）

```bash
java -javaagent:transmittable-thread-local-agent.jar \
     -jar my-app.jar
```

启动时自动 hook 所有 `Runnable/Callable/CompletableFuture`，**业务代码零侵入**。

---

## 五、方案 3：CompletableFuture 包装（纯 JDK）

### 1. 基本用法

```java
public static <T> CompletableFuture<T> wrap(Supplier<T> task) {
    String userId = userIdTL.get();  // 捕获当前线程的 TL 值
    return CompletableFuture.supplyAsync(() -> {
        userIdTL.set(userId);  // 在 worker 线程重新设置
        return task.get();
    }, pool);
}

// 调用
wrap(() -> {
    System.out.println(userIdTL.get());  // ✅ "user_123"
}).join();
```

### 2. 局限

- 需手动封装每个异步调用
- 业务代码侵入性强
- 线程复用时需手动清理（`finally { userIdTL.remove(); }`）

---

## 六、实战场景

### 场景 1：TraceId 全链路透传

```java
TransmittableThreadLocal<String> traceIdTL = new TransmittableThreadLocal<>();

// Web 层：设置 TraceId
@RestController
public class UserController {
    @GetMapping("/user/{id}")
    public User getUser(@PathVariable String id) {
        traceIdTL.set(UUID.randomUUID().toString());  // 设置 TraceId
        return userService.getUser(id);
    }
}

// Service 层：异步调用，仍然能拿到 TraceId
@Service
public class UserService {
    @Async
    public CompletableFuture<User> getUserAsync(String id) {
        log.info("traceId={}", traceIdTL.get());  // ✅ 透传成功
        return CompletableFuture.completedFuture(...);
    }
}
```

### 场景 2：用户上下文传递（登录态）

```java
TransmittableThreadLocal<User> currentUserTL = new TransmittableThreadLocal<>();

// Filter 中设置
public void doFilter(...) {
    currentUserTL.set(parseToken(request));
    chain.doFilter(...);
}

// 异步方法中读取
@Async
public void auditLog(String action) {
    User user = currentUserTL.get();  // ✅ 透传登录态
    logService.log(user, action);
}
```

---

## 七、面试陷阱

### 陷阱 1：以为 InheritableThreadLocal 能解决线程池问题

- **真相**：线程池复用 worker 线程，InheritableThreadLocal 完全失效

### 陷阱 2：以为 TransmittableThreadLocal 是"黑魔法"

- **真相**：核心是 capture + replay + restore 三步，原理简单

### 陷阱 3：以为 ThreadLocal 能解决异步问题

- **真相**：ThreadLocal 只能在当前线程有效，跨线程（new Thread / 线程池 / CompletableFuture / @Async）全部失效

### 陷阱 4：以为 CompletableFuture 包装是"标准方案"

- **真相**：手动包装是临时方案，工业级还是用 TransmittableThreadLocal + Agent 模式

---

## 八、面试话术（90 秒版本）

> 父子线程数据传递有 3 种方案：
>
> 1. **InheritableThreadLocal**：JDK 原生，只在 `new Thread()` 单次父子线程传递时有效。线程池完全失效，因为 worker 线程复用，初始化时只继承一次。
>
> 2. **TransmittableThreadLocal**：阿里开源，工业级标准。原理是 capture + replay + restore 三步：任务提交时捕获当前线程的 TTL 值，任务执行前设置到 worker 线程，任务执行后恢复原值。配合 `-javaagent:` 启动参数可实现零侵入。
>
> 3. **CompletableFuture 包装**：纯 JDK 方案，需手动捕获+重设，业务侵入性强。
>
> 生产环境推荐 **TransmittableThreadLocal + Agent 模式**，常见场景是 TraceId 透传、用户登录态透传、分布式 Session。
>
> 反直觉点：很多人以为 ThreadLocal 能解决异步问题，实际上 ThreadLocal 在跨线程时（new Thread/线程池/CompletableFuture）全部失效，必须用 Inheritable 或 Transmittable。

---

## 九、相关章节

- 同栏目：[`threadlocal`](../threadlocal/README.md) — ThreadLocal 原理与内存泄漏
- 同栏目：[`concurrency-vs-parallelism/`](../concurrency-vs-parallelism/) — 并发编程系列
- 主模块：[`01.java/concurrency`](../../../01.java/concurrency/README.md) — Java 并发编程

---

> 📅 2026-06-28 · 咬文嚼字 · Java 基础陷阱 · ⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · parent-child-thread](../README.md)
