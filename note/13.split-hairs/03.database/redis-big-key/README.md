# Redis 大 Key 问题全攻略

## 引子：Redis 为什么突然卡了？

```bash
# 运维告警：Redis 响应延迟从 1ms 飙升到 500ms！
```

排查发现：有个用户存了一个 **50MB 的 Hash key**（用户画像数据，几百万个字段）。

Redis 是**单线程**的。操作这个大 key 时，比如 `DEL`、`HGETALL`，会阻塞整个 Redis 几百毫秒——所有其他客户端的请求都在排队。

这就是大 key 的威力：**一个 key 拖垮整个集群**。

---

> 📚 **前置知识**：[Redis](../../03.database/07-redis/README.md)

## 一、核心原理

**大 Key**指占用内存过大或元素过多的键值对。Redis 单线程模型下，操作大 Key 会阻塞主线程、挤占网络带宽、造成 Cluster 数据倾斜。

### 判定标准

| 数据类型 | 判定标准 | 说明 |
|---------|---------|------|
| String | value > 10KB | 单个字符串值超过 10KB |
| Hash | field 数量 > 5000 | 哈希表中字段数超过 5000 |
| List | element 数量 > 5000 | 列表中元素数超过 5000 |
| Set | member 数量 > 5000 | 集合中成员数超过 5000 |
| ZSet | member 数量 > 5000 | 有序集合中成员数超过 5000 |

高并发场景建议采用更严格标准（String > 5KB，集合类型 > 3000 元素）。

---

## 二、大 Key 的危害

### 1. 阻塞效应

```
时间线：
T1: DEL big_hash        ← 删除 100万 field 的 Hash
T2: GET user:1001       ← 被阻塞，等待 DEL 完成
T3: SET order:2002      ← 被阻塞
T5: DEL 完成            ← 假设耗时 500ms
T6: 积压命令开始执行     ← 产生连锁延迟
```

DEL 大 Key 可能耗时数百毫秒，期间 Redis 无法响应任何请求，导致接口超时、连接池耗尽、业务层大量错误。

### 2. 网络带宽挤占

- 一个 1MB 的 String，每秒访问 1000 次则占用约 8Gbps 带宽
- 读取大 Key 完整数据会挤占其他正常请求的网络资源

### 3. Cluster Slot 数据倾斜

```
节点A [slot 0-5460]:    内存使用 2GB   ← 正常
节点B [slot 5461-10922]: 内存使用 8GB   ← 包含多个大 Key，内存告警
节点C [slot 10923-16383]: 内存使用 2GB  ← 正常
```

后果：倾斜节点先触发 OOM/eviction、扩容时无法均衡迁移、故障恢复时间长。

### 4. 过期删除阻塞

- **同步删除（默认）**：访问过期 Key 或定期清理时同步执行 DEL，阻塞主线程
- **异步删除（lazyfree）**：Redis 4.0+ 支持后台线程异步删除

即使启用 `lazyfree-lazy-expire yes`，在内存淘汰、FLUSHDB 场景下仍可能触发同步删除。

---

## 三、排查手段

### 1. redis-cli --bigkeys

```bash
redis-cli -h 127.0.0.1 -p 6379 --bigkeys
redis-cli --bigkeys -t hash          # 仅扫描特定类型
```

输出示例：
```
[00.00%] Biggest hash   found so far 'user:profile:cache' with 8234 fields
-------- summary -------
Biggest string found 'session:token:abc' has 15234 bytes
Biggest hash   found 'user:profile:cache' has 8234 fields
```

**注意**：使用 SCAN 遍历不阻塞主线程，但会增加 CPU 负载，建议业务低峰期执行。

### 2. MEMORY USAGE key

```bash
redis-cli MEMORY USAGE user:profile:cache        # 返回字节数
redis-cli MEMORY USAGE big_hash SAMPLES 100      # 集合类型精确估算
```

### 3. redis-rdb-tools（推荐离线分析）

完全不影响线上服务的最佳方案：
```bash
pip install rdbtools
redis-cli BGSAVE                                    # 生成 RDB
rdb -c memory dump.rdb > memory_report.csv         # 生成 CSV 报告
sort -t',' -k5 -n -r memory_report.csv | head -10  # 查看 Top 10
```

CSV 格式：`database,type,key,size_in_bytes,num_elements,len_largest_element,expiry`

### 4. 自定义扫描脚本

```python
import redis

def scan_big_keys(client, threshold_string=10240, threshold_collection=5000):
    big_keys = []
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor=cursor, count=1000)
        for key in keys:
            key_type = client.type(key).decode()
            size_fn = {'string':'strlen','hash':'hlen','list':'llen','set':'scard','zset':'zcard'}
            size = getattr(client, size_fn.get(key_type, 'strlen'))(key)
            threshold = threshold_string if key_type == 'string' else threshold_collection
            if size > threshold:
                big_keys.append({'key': key.decode(), 'type': key_type, 'size': size})
        if cursor == 0:
            break
    return sorted(big_keys, key=lambda x: x['size'], reverse=True)
```

---

## 四、解决方案

### 1. 大 Key 拆分策略

#### 1.1 大 Hash 拆分

**按 ID 取模分片：**

```python
def get_user_info(uid):
    shard_id = uid % 10
    return redis.hget(f"user:info:{shard_id}", f"uid:{uid}")
```

**按业务维度拆分：**
```
product:1001:basic  → {name, price, category}
product:1001:stock  → {stock, warehouse_location}
product:1001:detail → {desc, images, specifications}
```

#### 1.2 大 List 拆分（按时间窗口）

```python
def push_message(uid, message):
    today = datetime.now().strftime('%Y-%m-%d')
    key = f"timeline:user:{uid}:{today}"
    redis.lpush(key, message)
    redis.expire(key, 86400 * 30)  # 保留 30 天
```

#### 1.3 大 Set/ZSet 拆分

```python
def add_to_tag(tag, product_id):
    shard = hash(product_id) % 100
    redis.sadd(f"tags:{tag}:{shard}", product_id)
```

### 2. 异步删除（UNLINK）

```bash
DEL big_hash      # 同步删除，阻塞主线程 ~800ms
UNLINK big_hash   # 异步删除，立即返回 <1ms，后台线程删除
```

代码替换：`jedis.unlink("big_hash")` / `redis.unlink("big_hash")`

### 3. lazyfree 配置优化

```conf
lazyfree-lazy-expire yes           # Key 过期时异步删除
lazyfree-lazy-server-del yes       # 覆盖写时旧值异步删除
slave-lazy-flush yes               # 从节点加载 RDB 前异步清空
```

| 配置项 | 推荐值 | 说明 |
|-------|-------|------|
| lazyfree-lazy-expire | yes | 高并发场景必开 |
| lazyfree-lazy-server-del | yes | 减少覆盖写抖动 |
| slave-lazy-flush | yes | 减少主从切换阻塞 |

运行时修改：`redis-cli CONFIG SET lazyfree-lazy-expire yes`

### 4. 过期删除机制

```
惰性删除：客户端访问 Key 时检查是否过期 → 精准但可能残留
定期删除：每秒 10 次随机抽取 20 个带 TTL 的 Key 检查 → 主动但可能遗漏
两者配合：惰性处理精确过期，定期批量清理
```

---

## 五、预防手段

### 1. 写入时校验

```java
private static final int MAX_STRING_SIZE = 10 * 1024;
private static final int MAX_COLLECTION_SIZE = 5000;

public void safeSet(String key, String value) {
    if (value.getBytes(StandardCharsets.UTF_8).length > MAX_STRING_SIZE) {
        throw new IllegalArgumentException("Value size exceeds limit");
    }
    redisTemplate.opsForValue().set(key, value);
}
```

### 2. 序列化优化

优先选择 JSON 而非 Java 原生序列化，极致场景使用 Protobuf/MessagePack 可减少 30%-50% 存储空间。

### 3. 定时巡检 + 监控告警

```python
# cron: 每天凌晨 3 点执行
def daily_scan_and_report():
    for cluster in clusters:
        big_keys = scan_big_keys(redis.Redis(host=cluster['host']))
        if big_keys:
            send_alert(f"Found {len(big_keys)} big keys in {cluster['name']}")
```

```yaml
groups:
  - name: redis_alerts
    rules:
      - alert: RedisBigKeyCountHigh
        expr: redis_big_string_count > 10
        for: 5m
        labels:
          severity: warning
      - alert: RedisDelLatencySpike
        expr: histogram_quantile(0.99, rate(redis_command_duration_seconds_bucket{command="del"}[5m])) > 0.1
        for: 2m
        labels:
          severity: critical
```

### 4. 架构层面预防

- **多级缓存**：本地缓存(Caffeine) → Redis → MySQL/ES，大数据放 L3
- **Proxy 层拦截**：Twemproxy/Codis 可拦截大 Key 写入、限流读取

---

## 六、面试话术（30 秒版）

**面试官：请谈谈你对 Redis 大 Key 问题的理解**

> Redis 大 Key 是指占用内存过大或元素过多的键值对，通常 String 超过 10KB、集合类型超过 5000 元素就被认为是大 Key。
>
> 核心危害在于 Redis 是单线程模型，操作大 Key 会阻塞主线程导致所有请求排队。比如删除百万级元素的 Hash 可能阻塞数百毫秒，高峰期引发雪崩。此外还会造成网络带宽挤占和 Cluster 数据倾斜。
>
> 排查方面常用三种方式：redis-cli --bigkeys 在线扫描、MEMORY USAGE 精确测量、redis-rdb-tools 离线 RDB 分析（对生产影响最小）。
>
> 解决方案主要是拆分（大 Hash 按 ID 取模分片、大 List 按时间窗口分段）和使用 UNLINK 替代 DEL 异步删除。Redis 4.0+ 还支持 lazyfree-lazy-expire 配置让过期删除也走异步。
>
> 预防层面在业务层做写入校验，同时部署定时扫描和监控告警，确保问题早发现早处理。

---

## 七、交叉引用

- 主模块：[`03.database`](../../../03.database/) — 数据库知识体系
- [Redis](../../../03.database/07-redis/README.md) — Redis 详解
- [分布式锁](../../../04.system-design/02-distributed/distributed-lock/README.md) — 分布式锁实现

## 相关章节

- 深度阅读：[`03.database`](../../03.database/README.md) — 主模块详细内容
