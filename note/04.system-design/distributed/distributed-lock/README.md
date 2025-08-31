# 分布式锁

分布式锁是分布式系统中用于协调多个节点对共享资源访问的一种机制，确保在多进程或多服务环境下，同一时间只有一个节点能访问临界资源，避免并发问题（如数据不一致、超卖等）。以下是分布式锁的核心要点：

## 一、 为什么需要分布式锁？
- **单机锁的局限性**：传统锁（如Java的`synchronized`或`ReentrantLock`）仅适用于单进程内，无法跨进程或跨服务器生效。
- **分布式场景需求**：在微服务、集群或分布式数据库中，多个节点可能同时操作共享资源（如库存、订单状态），需全局唯一的锁机制。

## 二、 分布式锁的核心特性
- **互斥性**：同一时间只有一个客户端能持有锁。
- **容错性**：即使部分节点故障，锁仍能正常释放，避免死锁。
- **可重入性**：同一客户端可多次获取锁（非必须，但常见需求）。
- **非阻塞/阻塞**：获取锁失败时，可选择阻塞等待或直接返回失败。
- **公平性**：支持先到先得或优先级队列（可选）。
- **高性能**：加锁/解锁操作需低延迟，避免成为系统瓶颈。

## 三、 常见实现方案
### 1. 基于Redis
- **实现方式**：
    - 使用`SETNX`（SET if Not eXists）命令尝试加锁，结合过期时间防止死锁。
    - 释放锁时通过Lua脚本保证原子性（检查锁归属+删除）。
- **优化方案**：
    - **Redlock算法**：多Redis实例协同，提高可靠性（需权衡性能）。
    - **Redisson**：开源库提供RedissonLock，支持可重入、看门狗续期等。
- **缺点**：
    - 需处理网络分区、时钟漂移等问题。
    - 持久化问题：Redis崩溃可能导致锁丢失。

### 2. 基于ZooKeeper
- **实现方式**：
    - 创建临时顺序节点，利用节点顺序和Watcher机制实现锁。
    - 第一个节点获取锁，后续节点监听前一个节点，前一个释放后通知下一个。
- **优点**：
    - 天然支持分布式协调，可靠性高。
    - 临时节点自动删除，避免死锁。
- **缺点**：
    - 性能较低（依赖ZooKeeper的写入和通知机制）。
    - 需要维护ZooKeeper集群，复杂度较高。

### 3. 基于数据库
- **实现方式**：
    - 创建唯一索引的表，通过`INSERT`或`SELECT FOR UPDATE`加锁。
- **缺点**：
    - 性能差（数据库操作耗时）。
    - 需处理事务和超时问题，容错性弱。

### 4. 其他方案
- **Etcd**：类似ZooKeeper，使用`Lease`和`Watch`机制实现锁。
- **Chubby**：Google内部使用的分布式锁服务。
- **Consul**：通过KV存储和Session实现锁。

## 四、 关键问题与解决方案
- **死锁**：设置锁过期时间，或通过看门狗机制自动续期（如Redisson）。
- **锁误删**：释放锁时验证锁归属（如Redis的Lua脚本）。
- **时钟漂移**：避免依赖系统时间（如Redlock需同步时钟）。
- **单点故障**：多实例冗余（如Redis集群、ZooKeeper集群）。

## 五、 典型应用场景
- **电商库存扣减**：防止超卖。
- **分布式任务调度**：确保任务不被重复执行。
- **缓存更新**：避免多节点同时重建缓存。
- **消息队列消费**：防止消息被重复处理。

## 6. 选型建议
- **高性能场景**：优先选Redis（如Redisson）。
- **强一致性场景**：选ZooKeeper或Etcd。
- **简单场景**：若已有Redis，可直接使用`SETNX`+Lua。

## 示例代码（Redis + Lua）
```java
// 加锁（设置NX和PX）
String lockKey = "order_lock";
String clientId = UUID.randomUUID().toString();
Boolean locked = redisTemplate.opsForValue().setIfAbsent(lockKey, clientId, 10, TimeUnit.SECONDS);

// 释放锁（Lua脚本保证原子性）
String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
Long result = redisTemplate.execute(new DefaultRedisScript<>(script, Long.class), Collections.singletonList(lockKey), clientId);
```

分布式锁是分布式系统中的基础组件，选择方案时需根据业务需求（性能、一致性、复杂度）综合权衡。