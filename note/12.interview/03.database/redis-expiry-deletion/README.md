<!--
question:
  id: 03.database-redis-expiry-deletion
  topic: 03.database
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 生产 Bug
  tags: [03.database, Redis, 过期删除, UNLINK, lazy-expiration]
-->

# Redis 过期 Key 实时释放内存吗？

> **一句话定位**：过期 Key 不立即释放，靠惰性删除（访问时检查）+ 定期删除（每秒 10 次抽样 20 个）双机制兜底。

## 引子

```bash
# 业务设置了 100 万个 key，TTL 1 小时
SET session:user:1 "data" EX 3600
# 1 小时后，100 万 key 全部过期
# 问：内存是立即释放吗？
```

**答案**：❌ 不是。过期 ≠ 立即释放。Redis 用**惰性删除 + 定期删除**双机制，可能延迟数分钟甚至数小时。

> 📚 **前置知识**：[Redis](../../../03.data-stack/01-database/07-redis/README.md)

---

## 一、核心原理：惰性删除 vs 定期删除

Redis 对过期 key 采用**两种删除机制并行工作**：

| 策略 | 触发时机 | 工作方式 | 优缺点 |
|------|---------|---------|--------|
| **惰性删除** | 客户端访问 key 时 | GET/SET/HGET 等命令执行时检查 TTL，过期则删除 | CPU 友好，但未访问的过期 key 会长期占用内存 |
| **定期删除** | 每秒 10 次（每 100ms 一次） | 随机抽样 20 个带 TTL 的 key，删除已过期的；若过期比例 > 25%，继续抽样 | 主动释放内存，但有 CPU 开销 |

两种机制互补：惰性删除保证访问正确性，定期删除主动回收内存。但两者都无法保证"过期即刻释放"。

---

## 二、5 大面试陷阱

| # | 陷阱 | 正确理解 |
|---|------|---------|
| 1 | "key 过期了内存就立即释放" | ❌ 惰性删除（访问时）+ 定期删除（后台扫描），可能延迟数分钟 |
| 2 | "设置 TTL 就够了，不用管" | ❌ 大量 key 同时过期 → 内存峰值，需主动 UNLINK + 提高 hz |
| 3 | "DEL 和 UNLINK 一样" | ❌ DEL 同步删除（阻塞主线程），UNLINK 异步删除（后台线程） |
| 4 | "定期删除每秒只扫一次" | ❌ 默认 hz=10，即每秒 10 次（每 100ms），每次随机抽样 20 个 |
| 5 | "过期删除和淘汰策略是一回事" | ❌ 过期删除（TTL 到期）+ 淘汰策略（maxmemory 触发），两层防线 |

### 陷阱详解

**陷阱 1**：key 过期后，如果不被访问且定期删除没扫到，就会一直驻留内存。极端情况下，过期 key 可能存活数小时才真正释放。

**陷阱 2**：TTL 只是标记了过期时间，不触发即时回收。生产环境需要配合主动清理策略。

**陷阱 4**：很多候选人误以为定期删除"很慢"，实际上默认每秒执行 10 次，但每次只抽样 20 个 key，面对百万级过期 key 仍然杯水车车薪。

**陷阱 5**：过期删除和内存淘汰是完全独立的两个子系统。前者由 TTL 驱动，后者由 maxmemory 阈值驱动。即使开启了 noeviction，过期 key 仍然不会被立即删除。

---

## 三、定期删除流程（activeExpireCycle）

```text
1. 每 100ms 执行一次（server.hz 可配置）
2. 从每个 db 随机取 20 个带 TTL 的 key
3. 删除其中已过期的
4. 如果过期比例 > 25% → 继续抽样（但有上限，避免长期占用 CPU）
5. 每次抽样最多占用 25% CPU 时间
```

### 生产堆积案例

**场景**：100 万 key，TTL 1 小时。1 小时后全部过期。

**清理时间计算**：
- 定期删除每秒扫描：20 × 10 = **200 个 key/s**
- 清理 100 万 key 需要：1,000,000 / 200 = 5,000 秒 ≈ **83 分钟**

**4 种解决方案**：

| 方案 | 操作 | 效果 |
|------|------|------|
| **① 提高 hz** | `CONFIG SET hz 100` | 默认 10 → 100，每秒扫描从 200 → 2000 个 |
| **② 主动 UNLINK** | 业务层用 `UNLINK` 替代 `DEL` | 异步删除，不阻塞主线程 |
| **③ TTL 加随机偏移** | `EXPIRE key (3600 + random(0, 300))` | 避免大量 key 同时过期 |
| **④ 监控 expired_keys** | `INFO stats` 查看 `expired_keys` | 指标持续上升说明定期删除跟不上 |

---

## 四、DEL vs UNLINK（Redis 4.0+）

| 命令 | 删除方式 | 阻塞主线程 | 适用场景 |
|------|---------|:---------:|---------|
| `DEL` | 同步删除 | ✅ 是 | 小 key（< 1MB） |
| `UNLINK` | 异步删除（后台线程） | ❌ 否 | 大 key（> 1MB）、批量删除 |

```bash
# 同步删除 —— 阻塞主线程直到内存完全释放
DEL big_key

# 异步删除 —— 主线程立即返回，后台线程释放内存
UNLINK big_key

# 生产批量删除（推荐 UNLINK）
redis-cli --scan --pattern "session:*" | xargs redis-cli UNLINK
```

> 📚 **关联阅读**：
> - [Redis 内存淘汰策略](../redis-eviction/README.md) — maxmemory 触发的 8 种策略
> - [Redis 大 Key 问题](../redis-big-key/README.md) — 大 Key 发现与治理
> - [Redis 持久化](../redis-persistence/README.md) — RDB / AOF 机制

---

## 五、内存管理三层防线

```text
1. 过期删除（TTL 到期 → 惰性/定期删除）— 主动清理
2. 内存淘汰（maxmemory 触发 → 8 种策略）— 被动兜底
3. 主动清理（UNLINK / 业务层定时清理）— 工程干预
```

三层防线各司其职，共同保障 Redis 内存安全。不能仅依赖 TTL 过期来释放内存。

---

## 六、90 秒回答脚本

> "Redis 过期 key **不会立即释放内存**。它用两种机制并行工作：**惰性删除**（访问时检查 TTL，过期则删）+ **定期删除**（默认每秒 10 次，每次随机抽样 20 个带 TTL 的 key，删除已过期的）。如果大量 key 同时过期，可能延迟数分钟甚至数小时。
>
> 生产环境解决方案有四个：① **提高 hz**（默认 10 → 100，加快定期扫描频率）② **用 UNLINK** 异步删除大 key（不阻塞主线程）③ **TTL 加随机偏移**（避免大量 key 同时过期）④ **监控 expired_keys** 指标（通过 INFO stats 观察，持续增长说明定期删除跟不上）。
>
> 另外注意，**DEL 是同步删除**（阻塞主线程直到内存完全释放），**UNLINK 是异步删除**（Redis 4.0+ 引入，配合 lazyfree 机制，后台线程释放内存，主线程立即返回）。"

---

## 七、追问 Q&A

### Q1: 定期删除为什么限制 25% CPU？

**A**：Redis 是单线程架构，定期删除执行在主线程上。限制 25% CPU 是为了避免长期占用主线程，影响正常命令处理。如果过期 key 太多，宁可让内存淘汰策略兜底，也不能让删除操作阻塞业务请求。

### Q2: 淘汰策略和过期删除的区别？

**A**：过期删除由 TTL 到期触发（主动清理），淘汰策略由 maxmemory 阈值触发（被动兜底）。两者独立运行，互不冲突。即使开启了 noeviction（不淘汰），过期 key 仍然会通过定期删除机制被清理。详见 [Redis 内存淘汰策略](../redis-eviction/README.md)。

### Q3: UNLINK 是 Redis 哪个版本引入的？

**A**：Redis 4.0 引入，配合 lazyfree 机制实现异步删除。UNLINK 命令让主线程立即返回 OK，实际内存释放在后台线程完成。同时引入的还有 `lazyfree-lazy-eviction`、`lazyfree-lazy-expire` 等配置项。

### Q4: 如何监控过期 key 堆积？

**A**：通过 `INFO stats` 命令查看 `expired_keys` 指标。如果该指标持续快速增长且 `expired_stale_perc` 也升高，说明定期删除跟不上过期速度，需要提高 hz 或主动 UNLINK。

```bash
$ redis-cli INFO stats | grep expired
expired_keys:1234567
expired_stale_perc:28.5
```

### Q5: TTL 加随机偏移怎么做？

**A**：在设置过期时间时加上一个随机范围，避免大量 key 在同一秒过期：

```python
import random
ttl = 3600 + random.randint(0, 300)  # 3600 ~ 3900 秒
redis.set("session:user:1", "data", ex=ttl)
```

或者在业务层统一封装 TTL 设置逻辑，确保所有 key 都有合理的随机偏移。

---

## 八、参考来源

- [Redis 官方文档 — Redis keyspace: Expiration](https://redis.io/docs/latest/develop/use/keyspace/#expiration)
- [Redis 官方文档 — Active expiry cycle](https://redis.io/docs/latest/develop/use/keyspace/#active-expiry-cycle)
- [Redis 4.0 Release Notes — Lazyfree](https://redis.io/docs/latest/operate/oss_and_cluster/management/admin/)
- [Redis lazy-expire 原理详解](https://github.com/redis/redis)

---

← [返回: 数据库面试题](../README.md)
