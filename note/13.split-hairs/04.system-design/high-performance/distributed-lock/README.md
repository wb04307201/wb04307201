# 分布式锁

> 一句话：**Redis vs ZooKeeper，分布式锁的两种主流实现与 8 个坑**

---

## 一、为什么需要分布式锁

单机锁（`synchronized` / `ReentrantLock`）只在单 JVM 内有效。**多实例部署时，需要跨进程的互斥机制** —— 这就是分布式锁。

**适用场景**：
- 防止缓存击穿（热点 key 同时重建）
- 防止重复提交（订单、支付）
- 任务调度（避免多节点同时执行）
- 资源独占访问（库存扣减）

---

## 二、分布式锁的 6 个要求

| 要求 | 说明 |
|------|------|
| **互斥** | 同一时刻只有一个线程持锁 |
| **可重入** | 同一线程可重复获取同一把锁 |
| **超时释放** | 避免死锁（持锁者崩溃） |
| **高性能** | 加锁/释放延迟低 |
| **高可用** | 锁服务不能单点 |
| **非阻塞** | 获取失败立即返回（而非挂起） |

---

## 三、Redis 分布式锁

### 3.1 基础实现（SETNX）

```java
// ❌ 不推荐的写法（非原子）
if (redis.setnx(lockKey, "1") == 1) {
    redis.expire(lockKey, 30);  // 这行崩溃就死锁
    try {
        doBusiness();
    } finally {
        redis.del(lockKey);
    }
}

// ✅ 原子操作（SET NX EX）
public boolean tryLock(String lockKey, int expireSeconds) {
    String result = redis.set(lockKey, requestId, "NX", "EX", expireSeconds);
    return "OK".equals(result);
}

public void unlock(String lockKey, String requestId) {
    // Lua 脚本保证原子性（只释放自己的锁）
    String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                 "  return redis.call('del', KEYS[1]) " +
                 "else return 0 end";
    redis.eval(lua, 1, lockKey, requestId);
}
```

### 3.2 8 个坑与解决方案

| 坑 | 问题 | 解决 |
|----|------|------|
| **1. 锁过期但业务未完成** | 锁自动释放，其他线程进入 | **看门狗机制**（Redisson 默认 30s 续期） |
| **2. 误删他人锁** | A 删了 B 的锁 | 锁值用唯一 requestId，Lua 原子校验 |
| **3. 主从切换丢锁** | 主节点写入后宕机，从节点未同步 | RedLock 算法（多节点投票）|
| **4. 单点故障** | Redis 单节点挂掉 | Redis Sentinel / Cluster |
| **5. 锁不可重入** | 同一线程重复加锁死锁 | 使用 hash 结构记录重入次数 |
| **6. 超时时间难设置** | 太长浪费，太短死锁 | 看门狗自动续期 |
| **7. 客户端崩溃** | 锁未释放 | TTL 兜底 |
| **8. 性能问题** | 高并发下 Redis 压力大 | 分段锁 / 本地锁 + 分布式锁组合 |

### 3.3 Redisson 推荐实现

```java
// 1. 引入 Redisson
RLock lock = redisson.getLock("order:123");

try {
    // 2. 加锁（默认 30s 过期，看门狗自动续期）
    lock.lock();
    
    // 或 3. 尝试加锁（等待 5s，持锁 10s）
    if (lock.tryLock(5, 10, TimeUnit.SECONDS)) {
        doBusiness();
    }
} finally {
    // 4. 释放（Redisson 自动处理 requestId）
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

**Redisson 的优势**：
- ✅ 看门狗自动续期
- ✅ 可重入（hash 结构）
- ✅ Lua 脚本原子操作
- ✅ 支持 RedLock
- ✅ 公平锁 / 读写锁

---

## 四、ZooKeeper 分布式锁

### 4.1 临时顺序节点方案（最可靠）

```mermaid
graph TB
  A[客户端] -->|创建临时顺序节点| B[ZooKeeper]
  B --> C[判断是否为最小节点]
  C -->|是| D[获得锁]
  C -->|否| E[监听前一个节点]
  E -->|前一个节点删除| F[再次检查]
  F --> C
  style D fill:#e8f5e9
```

```java
// 伪代码
String lockPath = "/locks/order-";
String node = zk.create(lockPath, data, OPEN_ACL_UNSAFE, 
                         CreateMode.EPHEMERAL_SEQUENTIAL);

// 获取所有子节点，判断是否为最小
List<String> children = zk.getChildren("/locks", false);
if (isSmallest(node, children)) {
    // 获得锁
} else {
    // Watch 前一个节点
    zk.exists(prevNode, watcher);
}

// 释放锁：删除节点（session 断开自动删除）
zk.delete(node, -1);
```

### 4.2 ZooKeeper vs Redis 锁对比

| 维度 | Redis | ZooKeeper |
|------|-------|-----------|
| **实现方式** | SETNX + Lua | 临时顺序节点 |
| **性能** | ⭐⭐⭐⭐⭐ 极高（内存） | ⭐⭐⭐ 中（磁盘） |
| **可靠性** | ⭐⭐⭐（主从切换可能丢锁） | ⭐⭐⭐⭐⭐ 强一致（ZAB） |
| **可重入** | Redisson 支持 | Curator 支持 |
| **过期机制** | TTL | Session 超时 |
| **适用** | 高性能、允许偶尔失败 | 强一致、不允许丢锁 |

**选型建议**：
- **高并发场景**（如秒杀）→ Redis
- **强一致场景**（如金融交易）→ ZooKeeper
- **通用业务** → Redisson（Redis 的 Redisson 已足够）

---

## 五、RedLock 算法

```mermaid
graph TB
  A[客户端] -->|向 N 个节点申请| B[Redis 节点 1]
  A -->|向 N 个节点申请| C[Redis 节点 2]
  A -->|向 N 个节点申请| D[Redis 节点 3]
  A -->|向 N 个节点申请| E[Redis 节点 4]
  A -->|向 N 个节点申请| F[Redis 节点 5]
  B & C & D & E & F -->|N/2+1 成功| G[获得锁]
  style G fill:#e8f5e9
```

**步骤**：
1. 获取当前时间 T1
2. 依次向 N 个独立 Redis 节点申请锁（超时短，如 5-50ms）
3. 计算耗时 T2 = 当前时间 - T1
4. **在 N/2+1 个节点获得锁**，且总耗时 < 锁过期时间 → 成功
5. 失败 → 向所有节点释放锁
6. 有效锁时间 = 总过期时间 - 获取耗时

**争议**：
- Redis 作者 antirez 提出
- 分布式系统专家 Martin Kleppma 批评（时钟跳跃问题）
- 实际工程中**争议较大**，很多团队不用 RedLock

---

## 六、最佳实践

### 锁的粒度

```java
// ❌ 粗粒度：整个订单服务只能一个线程处理
lock("order-service");

// ✅ 细粒度：每个订单一把锁
lock("order:" + orderId);
```

### 本地锁 + 分布式锁组合

```java
// 本地锁减少 Redis 压力
private final ReentrantLock localLock = new ReentrantLock();

public void process() {
    if (localLock.tryLock()) {
        try {
            if (redisLock.tryLock()) {  // 再申请分布式锁
                try {
                    doBusiness();
                } finally {
                    redisLock.unlock();
                }
            }
        } finally {
            localLock.unlock();
        }
    }
}
```

---

## 七、面试话术（30 秒版）

> "分布式锁主流两种：**Redis 和 ZooKeeper**。
>
> **Redis 锁**：SETNX + Lua + TTL，性能高但主从切换可能丢锁。Redisson 提供看门狗自动续期、可重入、RedLock。
>
> **ZooKeeper 锁**：临时顺序节点，强一致但性能差。Curator 提供封装。
>
> **选型**：
> - 高并发（秒杀）→ Redis
> - 强一致（金融）→ ZooKeeper
> - 通用业务 → Redisson 足够
>
> **8 个坑**：锁过期、误删、主从丢锁、不可重入、超时难设、客户端崩溃、单点故障、性能压力。Redisson 基本都解决了。
>
> **RedLock**（N/2+1 节点投票）争议较大，工程上用得不多。"

---

## 八、交叉引用

- 主模块：[`04.system-design`](../../../04.system-design/) — 系统设计
- [分布式锁](../../../04.system-design/02-distributed/distributed-lock/README.md) — 分布式锁实现方案详解
- [缓存穿透/击穿/雪崩](../../../03.database/06-cache/README.md) — 缓存击穿中的分布式锁应用
