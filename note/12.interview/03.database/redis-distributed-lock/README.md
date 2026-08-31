<!--
question:
  id: 03.database-redis-distributed-lock
  topic: 03.database
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 面试追问陷阱
  tags: [03.database, redis, distributed-lock, redisson, watchdog]
-->

# Redis 分布式锁的 3 大坑 + Redisson 看门狗机制

> **一句话定位**：分布式锁 3 大坑：锁提前过期、误删他人锁、不可重入——Redisson 看门狗 + Lua + Hash 计数全解决。

## 引子：一个标准的面试回答

面试官："如何实现 Redis 分布式锁？"

候选人："用 `SET key value NX EX 30` 啊，NX 表示不存在才设置，EX 30 表示 30 秒过期。"

面试官："如果业务执行了 31 秒，锁已经过期了，其他线程拿到锁，原线程执行完删除锁时会发生什么？"

候选人："呃...会删除别人的锁？"

面试官："对！这就是第一个坑。还有第二个坑、第三个坑，你知道吗？"

---

**Redis 分布式锁的 3 大坑**：
1. **锁提前过期**：业务没执行完，锁已过期
2. **误删他人锁**：删除锁时，删掉了别人的锁
3. **不可重入**：同一个线程无法重复获取同一把锁

## 一、核心原理：从原始写法到 Redisson

### 1.1 原始写法（setnx + expire）

```java
// ❌ 错误示范
public boolean tryLock(String key, String value) {
    // 问题 1：非原子操作
    if (jedis.setnx(key, value) == 1) {
        jedis.expire(key, 30);  // 如果这行执行前崩溃，锁永不过期
        return true;
    }
    return false;
}

public void unlock(String key) {
    jedis.del(key);  // 问题 2：可能删除别人的锁
}
```

**问题**：
1. `setnx` + `expire` 不是原子操作，中间崩溃会导致锁永不过期
2. `del` 删除锁时，没有校验 value，可能删除别人的锁

### 1.2 改进版（SET NX EX 原子操作）

```java
// ✅ 原子操作
public boolean tryLock(String key, String value) {
    // SET key value NX EX 30 是原子操作
    String result = jedis.set(key, value, "NX", "EX", 30);
    return "OK".equals(result);
}

public void unlock(String key, String value) {
    // 先获取，校验 value 后再删除
    String currentValue = jedis.get(key);
    if (value.equals(currentValue)) {
        jedis.del(key);
    }
}
```

**问题**：
- `get` + `del` 仍然不是原子操作，中间可能被其他线程抢占

### 1.3 最终版（Lua 脚本保证原子性）

```java
// ✅ Lua 脚本保证原子性
public void unlock(String key, String value) {
    String luaScript =
        "if redis.call('get', KEYS[1]) == ARGV[1] then " +
        "    return redis.call('del', KEYS[1]) " +
        "else " +
        "    return 0 " +
        "end";
    jedis.eval(luaScript, Collections.singletonList(key), Collections.singletonList(value));
}
```

**解决了问题 2（误删他人锁）**，但**问题 1（锁提前过期）仍未解决**。

## 二、3 大陷阱（现象 → 真相）

### 坑 1：锁提前过期（业务没执行完，锁已过期）

**场景**：
```text
线程 A：获取锁，设置过期时间 30 秒
线程 A：执行业务逻辑（耗时 31 秒）
  ↓ 第 30 秒，锁自动过期
线程 B：获取锁成功（因为锁已过期）
线程 B：执行业务逻辑
  ↓ 第 31 秒，线程 A 执行完，删除锁
  ↓ 线程 A 删除的是线程 B 的锁！
线程 C：获取锁成功
  ↓ 现在线程 B 和 C 同时持有锁，分布式锁失效
```

**解决方案**：
1. **延长过期时间**：设置足够长的过期时间（如 60 秒、120 秒）
   - 问题：无法预知业务执行时间，设置过长会导致锁释放延迟
2. **Redisson 看门狗机制**：自动续期（推荐）

### 坑 2：误删他人锁（删除锁时没校验 value）

**场景**：
```text
线程 A：获取锁，value = "thread-a"
线程 A：执行业务（耗时 31 秒）
  ↓ 第 30 秒，锁过期
线程 B：获取锁，value = "thread-b"
线程 B：执行业务
  ↓ 第 31 秒，线程 A 执行完
线程 A：删除锁（没有校验 value，直接 del）
  ↓ 线程 A 删除的是线程 B 的锁！
```

**解决方案**：
- 删除锁前校验 value（Lua 脚本保证原子性）

### 坑 3：不可重入（同一个线程无法重复获取同一把锁）

**场景**：
```java
public void methodA() {
    boolean locked = tryLock("order:123", "thread-a");
    if (locked) {
        try {
            methodB();  // 内部也需要获取同一把锁
        } finally {
            unlock("order:123", "thread-a");
        }
    }
}

public void methodB() {
    boolean locked = tryLock("order:123", "thread-a");  // ❌ 获取失败（锁已被自己持有）
    // ...
}
```

**问题**：同一个线程无法重复获取自己已持有的锁（死锁）

**解决方案**：
- 可重入锁（Redisson 实现）

## 三、Redisson 看门狗机制（自动续期）

### 3.1 原理

```text
Redisson 获取锁时：
1. 设置锁过期时间（默认 30 秒）
2. 启动看门狗线程（后台定时任务）
3. 每 10 秒检查一次：如果线程仍持有锁，自动续期（重置为 30 秒）
4. 线程主动释放锁 → 停止看门狗

效果：
- 业务执行多久，锁就持有多久
- 线程崩溃 → 看门狗停止 → 锁自动过期（不会死锁）
```

### 3.2 代码示例

```java
// Redisson 分布式锁
RLock lock = redisson.getLock("order:123");
try {
    // 获取锁（自动续期）
    lock.lock();

    // 执行业务逻辑（无论多久，锁都会保持）
    doBusiness();

} finally {
    // 释放锁
    lock.unlock();
}
```

### 3.3 可重入锁

```java
// Redisson 可重入锁
RLock lock = redisson.getLock("order:123");
lock.lock();  // 第一次获取
try {
    lock.lock();  // ✅ 第二次获取（可重入）
    try {
        // 业务逻辑
    } finally {
        lock.unlock();  // 第一次释放
    }
} finally {
    lock.unlock();  // 第二次释放
}
```

**原理**：Redis Hash 结构
```text
HSET order:123 thread-a:1  // 第一次获取，计数 = 1
HINCRBY order:123 thread-a:1 1  // 第二次获取，计数 = 2
HINCRBY order:123 thread-a:1 -1  // 第一次释放，计数 = 1
HDEL order:123 thread-a:1  // 第二次释放，计数 = 0，删除锁
```

## 四、面试话术（30 秒版）

> "Redis 分布式锁有 3 大坑：**锁提前过期**——业务没执行完锁已过期，其他线程拿到锁，用 Redisson 看门狗机制自动续期解决；**误删他人锁**——删除锁时没校验 value，用 Lua 脚本保证原子性（先 get 校验再 del）；**不可重入**——同一线程无法重复获取同一把锁，用 Redisson 可重入锁（Hash 结构 + 计数器）解决。
>
> Redisson 看门狗机制：获取锁后启动后台线程，每 10 秒检查一次，如果线程仍持有锁就自动续期（重置为 30 秒）。线程崩溃则看门狗停止，锁自动过期，不会死锁。"

> "Redis 分布式锁是面试高频题，我从实际项目遇到的角度来讲。
>
> 我们项目里用 Redis 做订单分布式锁，上线后遇到一个经典问题：订单处理耗时超过锁的过期时间 30 秒，锁自动释放后另一个线程拿到了锁，两个线程同时处理同一笔订单，数据不一致。这就是第一个坑——**锁提前过期**。解决方案是 Redisson 看门狗机制：获取锁后启动后台线程，每 10 秒检查一次，如果线程仍持有锁就自动续期重置为 30 秒。线程崩溃则看门狗停止，锁自动过期不会死锁。
>
> 第二个坑是**误删他人锁**：线程 A 的锁过期后线程 B 拿到锁，线程 A 执行完直接 del 删掉了 B 的锁。解决方案是用 Lua 脚本保证原子性——先 get 校验 value 匹配再 del，一步到位不会被中间打断。
>
> 第三个坑是**不可重入**：方法 A 持有锁后调用方法 B，方法 B 也需要同一把锁，结果获取失败死锁。Redisson 用 Hash 结构解决——key 是锁名，field 是线程标识，value 是重入计数。lock 时 HINCRBY +1，unlock 时 HINCRBY -1，减到 0 时 HDEL 释放锁。
>
> 面试追问的话，可以展开两点：1）为什么不用 RedLock（多节点方案）？因为 Martin Kleppmann 论证过 RedLock 在 GC 停顿或时钟漂移下仍然不安全，生产环境更推荐 Redisson 单节点 + 看门狗。2）与 ZooKeeper / 数据库分布式锁的对比：Redis 性能最高但一致性最弱，ZK 强一致但吞吐低，按业务场景选。"

## 五、交叉引用

- 分布式锁设计 — 通用分布式锁设计（ZooKeeper / Redis / 数据库）
- [Redis 单线程模型](../redis-single-thread/README.md) — Redis 为什么快
- [Redis 过期删除策略](../redis-expiry-deletion/README.md) — Redis 如何删除过期 key
- 主模块：[`03.database`](../../../03.data-stack/01-database/README.md) — 数据库知识体系

## 相关章节

- 深度阅读：[`03.database`](../../../03.data-stack/01-database/README.md) — 主模块详细内容

> 📅 2026-09-01 · 咬文嚼字 · Redis · ⭐⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 咬文嚼字 · redis-distributed-lock](../README.md)
