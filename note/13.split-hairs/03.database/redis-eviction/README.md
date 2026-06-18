# Redis 内存淘汰策略 8 种深度对比

> 一句话：当 Redis 内存达到 maxmemory 上限时，通过预设策略选择性地删除 key，确保服务持续可用。

---

## 一、核心原理

Redis 的内存淘汰机制由 `maxmemory` 指令触发。当已使用内存超过设定阈值时，Redis 会在处理新写请求前执行淘汰逻辑。

```
客户端写入 → 检查内存 → 超过 maxmemory？
  ├─ 是 → 执行淘汰（evictKeys）
  └─ 否 → 正常写入
```

### 8 种策略分类

| 分类 | 策略名 | 作用范围 | 淘汰规则 |
|------|--------|----------|----------|
| **不淘汰** | `noeviction` | - | 返回错误（默认策略） |
| **allkeys 系列** | `allkeys-lru` | 所有 key | 最近最少使用 |
| | `allkeys-lfu` | 所有 key | 最不经常使用 |
| | `allkeys-random` | 所有 key | 随机淘汰 |
| **volatile 系列** | `volatile-lru` | 带 TTL 的 key | 最近最少使用 |
| | `volatile-lfu` | 带 TTL 的 key | 最不经常使用 |
| | `volatile-random` | 带 TTL 的 key | 随机淘汰 |
| | `volatile-ttl` | 带 TTL 的 key | 剩余 TTL 最小优先 |

**关键区别：** `allkeys-*` 作用于全部 key；`volatile-*` 仅作用于已设置 TTL 的 key；`noeviction` 写操作直接返回 OOM 错误。

```c
if (server.maxmemory_policy & MAXMEMORY_FLAG_VOLATILE) {
    dict = db->expires;  // 只从 expires 字典采样
} else {
    dict = db->dict;     // 从整个键空间采样
}
```

若设置了 `volatile-*` 但无带 TTL 的 key，行为退化为 `noeviction`。

---

## 二、8 种策略详解

### 1. noeviction（默认）
内存满时拒绝所有写命令。**适用：** 数据完整性要求极高的场景。

### 2. allkeys-lru
在所有 key 中淘汰最近最久未访问的。**适用：** 通用缓存，热点数据保留。

### 3. volatile-lru
仅在带 TTL 的 key 中执行 LRU。**适用：** 混合存储（部分永久 + 部分临时）。

### 4. allkeys-lfu
在所有 key 中淘汰访问频率最低的。**适用：** 存在周期性热点、突发流量的场景。

### 5. volatile-lfu / 6-7. random 系列
volatile-lfu 仅在带 TTL 的 key 中执行 LFU。random 系列随机淘汰，几乎无实际应用场景。

### 8. volatile-ttl
淘汰剩余 TTL 最小的 key。**适用：** 希望优先清理即将过期的数据。

---

## 三、LRU vs LFU

### LRU（Least Recently Used）

Redis 实现的是**近似 LRU**，非精确算法。

**工作原理：** 1) 随机采样 N 个 key（默认 `maxmemory-samples = 5`）→ 2) 从采样中选择最近访问时间最早的淘汰 → 3) 每次访问时更新 key 的 `lru` 字段（24 bits）

```c
typedef struct redisObject {
    unsigned type:4; encoding:4; lru:LRU_BITS;  // 24 bits
    int refcount; void *ptr;
} robj;
```

**缺陷：** 扫描攻击脆弱性（批量遍历 key 刷新 LRU 时间戳，导致热点数据被淘汰）；突发流量敏感

### LFU（Least Frequently Used）

Redis 4.0+ 引入，解决 LRU 核心缺陷。使用 **8-bit Morris 计数器**存储访问频率。

```
+--------+--------+
| 16 bits| 8 bits |
| last   | counter|
| decay  |        |
+--------+--------+
```

- **高 16 位：** 上次衰减时间戳（分钟级）
- **低 8 位：** 访问频率计数器（对数增长）

**Morris 计数器的对数特性**（`lfu-log-factor = 10`）：1 次访问 → counter ≈ 1；100 次访问 → counter ≈ 36；10000 次访问 → counter ≈ 72；255 为最大值。

**衰减机制：**
```
CONFIG SET lfu-decay-time 1  # 单位：分钟
if elapsed_minutes > lfu-decay-time:
    counter = counter / 2  // 频率减半
```

### LRU vs LFU 对比

| 维度 | LRU | LFU |
|------|-----|-----|
| **衡量指标** | 最后访问时间 | 累计访问频率 |
| **突发流量影响** | 一次访问即刷新 | 单次访问贡献极小 |
| **周期性热点** | 无法识别 | counter 保持高位 |
| **扫描攻击** | 脆弱 | 鲁棒（对数增长） |

**示例：** 日志分析系统每小时全量扫描 100 万 key。LRU 会刷新所有 key 的 LRU 导致真实热点被淘汰；LFU 的扫描单次访问对 counter 影响微乎其微。

---

## 四、源码实现

### 近似 LRU 的随机采样算法

Redis 采用**随机采样 + 池化比较**，而非全局 LRU 链表。

```c
// server.c - evictKeys 核心逻辑
int freeMemoryIfNeeded(void) {
    while (used_memory > maxmemory) {
        dict *sample_dict = chooseDict(policy);
        best_key = NULL;
        for (i = 0; i < server.maxmemory_samples; i++) {
            key = dictGetRandomKey(sample_dict);
            if (policy == LRU) {
                idle = estimateObjectIdleTime(key);
                if (best_key == NULL || idle > best_idle)
                    best_key = key, best_idle = idle;
            } else if (policy == LFU) {
                freq = getLFUFrequency(key);
                if (best_key == NULL || freq < best_freq)
                    best_key = key, best_freq = freq;
            }
        }
        if (best_key) dbDelete(best_key);
    }
}
```

**关键优化：** 1) Redis 7.0+ 引入 eviction pool；2) LRU/LFU 在访问时更新；3) 采样数可调

```
maxmemory-samples = 3  → ~70% 接近真实 LRU
maxmemory-samples = 5  → ~80% 接近真实 LRU（默认）
maxmemory-samples = 10 → ~90% 接近真实 LRU
```

### LFU 的 8-bit 对数计数器

```c
unsigned long LFULogIncr(unsigned long counter) {
    if (counter == 255) return 255;
    double r = (double)rand() / RAND_MAX;
    double p = 1.0 / (counter * server.lfu_log_factor + 1);
    return (r < p) ? counter + 1 : counter;
}
```

**配置参数：** `lfu-log-factor 10`（值越大 counter 增长越慢）；`lfu-decay-time 1`（衰减速度，分钟）

### jemalloc 内存分配器的影响

`used_memory_rss`（常驻内存）> `used_memory`（逻辑内存）。差额来源：jemalloc 内部碎片、共享内存页。

**关键指标：** `mem_fragmentation_ratio = RSS / used_memory`，理想 1.0~1.5。`maxmemory` 对比的是 `used_memory`，非 RSS。

---

## 五、选型建议 + 最佳实践

### 策略选型决策树

```
是否需要保留永久数据？
├─ 是 → 是否有 TTL 标记？
│       ├─ 是 → volatile-lfu（推荐）或 volatile-lru
│       └─ 否 → allkeys-lfu（推荐）或 allkeys-lru
└─ 否（纯缓存）→ 流量特征？
        ├─ 稳定热点 → allkeys-lru
        ├─ 周期性/突发热点 → allkeys-lfu（⭐ 首选）
        └─ 无所谓 → allkeys-lru（保守选择）
```

### 推荐配置模板

**场景 1：通用 API 缓存**
```
maxmemory 4gb
maxmemory-policy allkeys-lfu
maxmemory-samples 10
lfu-log-factor 10
lfu-decay-time 5
```

**场景 2：会话存储**
```
maxmemory 2gb
maxmemory-policy volatile-lfu
# 配合业务层：SET session:xxx data EX 1800
```

### 最佳实践清单

1. **永远不要将 maxmemory 设为 0**，生产环境必须设限
2. **预留 10-20% 内存余量**，防止 jemalloc 碎片导致 OOM
3. **监控 mem_fragmentation_ratio**，超过 1.5 考虑重启或调整
4. **大 Key 警惕：** 淘汰包含数千元素的 Hash/List 会阻塞 Redis
5. **定期分析 key 分布：** `redis-cli --bigkeys` 识别潜在风险

### maxmemory 计算公式

```
# 单机 Redis：maxmemory = 总内存 × 0.6（留 40% 给 OS + 碎片）
# 主从架构：maxmemory = 总内存 × 0.4（留更多给复制缓冲区 + RDB fork）
```

---

## 六、常见陷阱

### 陷阱 1：maxmemory 设置为 0
**后果：** 持续占用内存直至系统 OOM Killer 介入。**修复：** `CONFIG SET maxmemory 2gb`

### 陷阱 2：volatile 策略但无 TTL
```
maxmemory-policy volatile-lru
SET user:1001 "{...}"  # 没有 EX/PX 参数
```
**后果：** 找不到带 TTL 的 key，行为退化为 `noeviction`。**修复：** 确保所有写入设置 TTL，或改用 `allkeys-*` 策略

### 陷阱 3：大 Key 淘汰耗时
**后果：** 淘汰该 key 时阻塞主线程。**检测：** `redis-cli --bigkeys -i 0.1`；**预防：** 应用层限制集合大小，使用 `UNLINK` 异步删除

### 陷阱 4：淘汰不精确导致的抖动
**现象：** 内存使用量在 maxmemory 附近频繁波动。**修复：** `CONFIG SET maxmemory-samples 10`

### 陷阱 5：忽略 jemalloc 碎片
**现象：** `used_memory` 低于 maxmemory，但仍触发淘汰或 OOM。**修复：** `CONFIG SET activedefrag yes`

---

## 七、面试话术（30 秒版）

> "Redis 有 8 种内存淘汰策略，分为三类：noeviction 不淘汰、4 种 allkeys 系列淘汰所有 key、3 种 volatile 系列只淘汰带 TTL 的 key。最常用的是 **allkeys-lfu**，基于访问频率淘汰，比 LRU 更能抵抗突发流量和扫描攻击。LFU 用 8-bit Morris 计数器实现，对数增长加周期性衰减。需要注意，Redis 的 LRU 不是全局精确的，而是随机采样 5 个 key 取最旧的。生产环境建议设置 maxmemory 为物理内存的 60%，并监控 fragmentation ratio 防止 jemalloc 碎片问题。"

---

## 八、交叉引用

- 主模块：[`03.database`](../../../03.database/) — 数据库知识体系
- 相关笔记：[Redis 数据结构底层实现](../redis-data-structures/)、[Redis 持久化机制 RDB vs AOF](../redis-persistence/)、[Redis 集群与分片](../redis-cluster/)
