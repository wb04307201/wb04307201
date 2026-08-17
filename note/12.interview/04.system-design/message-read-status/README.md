<!--
question:
  id: message-read-status
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [IM, 消息已读未读, Redis, WebSocket, SSE, 位图, 推送]
-->

# 消息已读未读功能设计 —— 亿级 IM 系统的读状态追踪方案

> 一句话定位：消息已读未读是 IM/OA 系统中最容易从"小功能"演变成"大瓶颈"的模块——设计不当会在万级并发时拖垮整个数据库。

> **系列定位**：经典系统架构设计题（IM 聊天/钉钉通知/企业微信/飞书高频）。考察的不是"怎么加一个 is_read 字段"，而是 **读扩散与写扩散的权衡** + **海量用户读状态的存储选型** + **实时推送与最终一致性的取舍**。

---

## 引子：一个看似简单却让架构师加班的需求

```text
产品经理：加个消息已读未读功能，跟微信一样，已读显示双勾。
你：简单，加个 is_read 字段就行。
一周后：
  - 群消息 500 人，已读状态要写 500 条记录
  - 一个 10 万人超级群，发消息触发 10 万次写操作
  - 数据库 CPU 持续 95%，慢查询告警
  - 用户反馈"已读状态延迟 30 秒才刷新"
```

**为什么加一个字段能搞垮数据库？** 核心矛盾：

- **读状态 = 消息 × 用户的二维关系**：N 条消息 × M 个用户 = N×M 条记录，群越大越失控
- **实时性要求**：用户期望打开聊天窗口就立即看到"谁已读"，不能容忍轮询延迟
- **存储成本**：亿级用户 × 百亿消息，关系表轻松破百亿行
- **推送风暴**：500 人群一人读消息，其余 499 人客户端需要实时更新，消息放大 500 倍

---

## 一、核心原理（读扩散 vs 写扩散）

### 1.1 方案一：关系表（读扩散）—— 最直观但最危险

```sql
CREATE TABLE message_read_status (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    msg_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    is_read TINYINT DEFAULT 0,
    read_time DATETIME,
    UNIQUE KEY uk_msg_user (msg_id, user_id)
) ENGINE=InnoDB;
```

**致命问题**：

| 场景 | 写入量 | 问题 |
|------|--------|------|
| 100 人群发消息 | 100 条 | 可接受 |
| 500 人群发消息 | 500 条 | 开始吃力 |
| 10 万人超级群 | 10 万条 | 数据库扛不住 |
| 撤回消息需删除 | 10 万条 DELETE | 事务重，容易锁表 |

**何时能用**：仅适用于 **小群（< 50 人）+ 低频通知** 场景。

### 1.2 方案二：位图 Bitmap（写扩散 + 空间压缩）—— 大厂标配

```
位图本质：用 1 个 bit 代表一个用户的已读状态

消息 msg_1001 → Bitmap: 00101000000000100... (每位 = 1个user_id)
                    ↑   ↑         ↑
                   用户3 用户5     用户16 已读

存储空间：1 万人群 = 10000 bits = 1.25 KB（而非 1 万行记录）
```

**Redis 实现**：

```bash
# 发消息时初始化（全员未读）
SETBIT msg:read:1001 3 0
SETBIT msg:read:1001 5 0
SETBIT msg:read:1001 16 0

# 用户已读
SETBIT msg:read:1001 3 1  → 返回 0（之前未读）

# 查询已读人数
BITCOUNT msg:read:1001    → 返回 1

# 查询用户是否已读
GETBIT msg:read:1001 3    → 返回 1（已读）

# 查询谁已读（返回所有已读 user_id 偏移量）
BITFIELD msg:read:1001 GET u32 0
```

**优势**：
- ✅ 存储极小：百万级用户仅需 ~125 KB
- ✅ 读写 O(1)，单线程原子操作，无并发竞争
- ✅ BITCOUNT/BITOP 天然支持聚合（"已读率 78%"）

**限制**：
- ⚠️ user_id 需连续或映射为偏移量（需维护 user_id → offset 映射）
- ⚠️ 单 Key 不能超 512 MB（对应 43 亿 bit，足够覆盖中国人口）

### 1.3 方案三：最后已读消息 ID（极简方案）—— 适合多数 IM

**核心思路**：不记录每条消息的已读状态，只记录"用户最后读到了哪条消息"。

```redis
# Redis Hash: user:last_read:{user_id} = {chat_id: last_read_msg_id}
HSET user:last_read:10001 chat:50 12345

# 查询：chat_id=50 中 msg_id <= 12345 的均为已读
```

```sql
-- 数据库极简表
CREATE TABLE user_last_read (
    user_id BIGINT,
    chat_id BIGINT,
    last_read_msg_id BIGINT,
    updated_at DATETIME,
    PRIMARY KEY (user_id, chat_id)
);
```

**优势**：
- ✅ 存储量 = 用户数 × 会话数（远小于 消息×用户）
- ✅ 写入量 = 用户切换会话时才更新，不是每条消息都写
- ✅ 适合"已读全部"行为（微信模式：打开聊天窗口 = 全部已读）

**限制**：
- ❌ 无法支持"逐条标记已读"（如钉钉单条已读回执）
- ❌ 无法精确统计"谁读了哪条消息"

---

## 二、缓存策略（未读计数与已读状态分层）

### 2.1 未读计数：Redis 计数器

```redis
# 用户未读消息总数（聊天列表红点）
INCR unread_count:user:10001        → 99+

# 某会话的未读数
INCR unread_count:user:10001:chat:50

# 已读后清零
SET unread_count:user:10001:chat:50 0
```

### 2.2 分层缓存架构

```text
L1: 客户端本地缓存（内存）
    - 最近 50 条消息的已读状态
    - 离线期间累积，连网后批量同步

L2: Redis 热数据
    - 近 7 天的已读状态（Bitmap / Hash）
    - 未读计数器

L3: MySQL 冷数据
    - 7 天以上的已读记录（归档）
    - 用于审计 / 数据恢复

数据流：客户端 → 读 L1 → 读 L2 → 读 L3（逐级回源）
```

### 2.3 缓存一致性策略

```text
用户标记已读：
  1. 更新 Redis（SETBIT，毫秒级，实时）
  2. 异步写入 MySQL（消息队列，最终一致）
  3. 推送给同一会话其他成员（WebSocket/SSE）

超时回源机制：
  - Redis TTL 7 天
  - 过期后从 MySQL 重建 Bitmap
```

---

## 三、推送机制（实时性保障）

### 3.1 WebSocket vs SSE 选型

| 维度 | WebSocket | SSE |
|------|-----------|-----|
| 已读状态推送 | ✅ 双向，服务器主动推 | ✅ 服务器推，客户端已读用 HTTP POST 回传 |
| 连接成本 | 每个用户 1 条长连接 | 每个用户 1 条 HTTP 长连接 |
| 适合场景 | 高频双向（群聊实时已读反馈） | 中低频通知（OA 已读回执） |
| 代理兼容 | 需 Nginx 额外配置 Upgrade | 标准 HTTP，CDN 友好 |

**选型建议**：
- IM 聊天（高频、双向）：WebSocket 为主
- OA 通知（低频、单向）：SSE 为主
- 混合场景：SSE 推已读通知 + HTTP POST 回传已读动作

### 3.2 推送风暴防护

```text
问题：500 人群一人已读，需推送 499 人
     → 一条已读消息被放大 499 次

方案 1：聚合推送（推荐）
  - 3 秒内同一群的已读事件合并为一条
  - 推送格式：{chat_id: 50, read_users: [3, 7, 15, ...], count: 23}

方案 2：懒拉取
  - 不推送具体谁已读，只推送"已读数变化"
  - 客户端收到后主动拉取已读详情列表

方案 3：热点降权
  - 超级群（> 5000 人）关闭单条已读回执
  - 改为"已读人数"统计（BITCOUNT 聚合）
```

---

## 四、性能优化（批量与异步）

### 4.1 批量更新（Pipeline）

```python
# 反例：逐条更新
for user_id in read_user_ids:
    redis.setbit(f'msg:read:{msg_id}', user_id, 1)  # N 次网络往返

# 正例：Pipeline 批量
pipe = redis.pipeline()
for user_id in read_user_ids:
    pipe.setbit(f'msg:read:{msg_id}', user_id, 1)
pipe.execute()  # 1 次网络往返
```

### 4.2 异步写数据库

```text
同步链路（已读动作）：
  客户端 → API → Redis（SETBIT） → 返回成功（< 10ms）

异步链路（数据持久化）：
  Redis → MQ（Kafka/RabbitMQ） → Consumer → MySQL 批量写入（每 500ms 一批）

失败处理：
  - Consumer 重试 3 次（指数退避）
  - 死信队列兜底
  - 定时对账任务（Redis vs MySQL 差异修复）
```

### 4.3 已读状态合并写（Coalescing）

```text
用户在 3 秒内连续读了 20 条消息：
  ❌ 触发 20 次写操作
  ✅ 合并为 1 次更新（last_read_msg_id = 第 20 条）

实现：客户端本地队列 + 3 秒防抖 + 批量上报
```

---

## 五、常见陷阱

### 陷阱 1：群消息已读 = 群成员数 × 消息数

**真相**：用 Bitmap 或"最后已读消息 ID"方案，存储量与消息数解耦。

### 陷阱 2：已读状态强同步写数据库

**真相**：已读是高频低价值操作（丢了不影响核心业务），应 Redis 异步 + 最终一致。强写库 = 数据库被已读拖垮。

### 陷阱 3：用轮询查已读状态

**真相**：客户端每 2 秒轮询 = 500 个用户 × 500 个会话 = 25 万 QPS。必须改为推送或长连接。

### 陷阱 4：已读推送不做聚合

**真相**：500 人群中 100 人陆续已读 = 500 × 100 = 5 万条推送。必须聚合（3 秒窗口合并）。

---

## 六、最佳实践

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 1v1 私聊 | 最后已读消息 ID（极简表） | 数据量小，实现简单 |
| 小群（< 50 人） | 关系表 | 可读性强，开发快 |
| 大群（50-500 人） | Redis Bitmap + 聚合推送 | 存储可控，实时性好 |
| 超级群（> 5000 人） | 仅显示已读数 + 懒拉取 | 推送风暴控制 |
| OA 通知 | SSE 推已读 + HTTP POST 回执 | 单向通知，CDN 友好 |
| 企业 IM（钉钉模式） | Bitmap + WebSocket + 异步持久化 | 逐条已读回执 + 高性能 |

---

## 七、面试话术（30 秒版）

> "消息已读未读的核心矛盾是**二维关系爆炸**——消息数乘以用户数。
>
> 我的方案分三层：**小群用关系表**，直白可维护；**大群用 Redis Bitmap**，百万用户才 125 KB；**超群只显示已读人数**，防推送风暴。
>
> 写链路是 **Redis 同步 + MQ 异步落库**，保证已读操作不拖垮数据库。
>
> 推链路用 **WebSocket/SSE + 3 秒聚合窗口**，500 人的已读事件合并推送，避免消息放大。
>
> 如果是钉钉式'逐条已读回执'，用 Bitmap；如果是微信式'打开窗口=全部已读'，用最后已读消息 ID 就够了。"

---

## 八、相关章节

- 同栏目：[`SSE vs WebSocket 面试题`](../../../02.cs-foundations/03-network/protocols/sse-vs-websocket/README.md) — 推送协议选型依据
- 同栏目：[`缓存与数据库双写一致性`](../cache-consistency/README.md) — 已读状态异步落库的一致性保障
- 同栏目：[`幂等性设计 6 大方案`](../idempotency/README.md) — 已读操作重复上报的幂等处理
- 主模块：[`数据一致性`](../../../06.distributed-systems/01-foundation/system-design-basics/microservices/data-consistency/README.md) — 最终一致性在 IM 场景的落地
- 主模块：[`网络协议`](../../../02.cs-foundations/03-network/protocols/sse-vs-websocket/README.md) — WebSocket/SSE 协议层对比

---

> 📅 2026-07-30 · 咬文嚼字 · 消息已读未读 · ⭐⭐⭐⭐（高频面试 + 实战必会）

← [返回: 系统设计咬文嚼字](../README.md)
