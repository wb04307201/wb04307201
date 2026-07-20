<!--
question:
  id: 04.system-design-url-shortener
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计
  tags: [04.system-design, 短链, URL-shortener, Base62, 分布式ID, 302重定向]
-->

# 设计一个短链系统 —— Base62 + 发号器 + 302 重定向 + 缓存

> 一句话定位：**系统设计面试最经典题**。考察的不是"长 URL 变短"，而是**短码生成策略选型** + **302 vs 301 重定向** + **高并发缓存** + **统计分析**。分布式 ID 基础见 [分布式 ID 生成](../../../04.system-design/02-distributed/distributed-id/README.md)。

> **系列定位**：高频系统设计题（校招社招都考）。配套兄弟题：[商品搜索](../product-search/README.md)、[大文件上传](../file-upload/README.md)。

---

⭐⭐⭐⭐ 深度级别（高级工程师级）
📚 前置知识：HTTP 重定向 / 分布式 ID / Redis / 一致性哈希

---

## 引子：面试经典开场

面试官："设计一个短链系统，每天新增 1 亿短链，支撑 10 万 QPS 跳转。"

大多数人答："用 MD5 截取前 6 位。"

面试官追问：
1. "MD5 碰撞了怎么办？6 位 Base62 能表示多少个短码？"
2. "302 和 301 重定向有什么区别？选哪个？"
3. "10 万 QPS 跳转，数据库扛不住怎么办？"
4. "同一个长 URL 多次生成，返回相同短码还是不同短码？"

大多数人卡在追问上。**这道题考察的不是"知道 MD5"，而是"短码生成策略 + 存储 + 缓存 + 统计的全链路设计"。**

---

## 一、核心原理

### 1.1 系统流程

```
生成短链：
  用户 → POST /api/shorten {longUrl: "https://..."}
       → 生成长 URL 的短码（如 "aB3xK9"）
       → 存入 DB: {shortCode: "aB3xK9", longUrl: "https://..."}
       → 返回 https://short.ly/aB3xK9

短链跳转：
  用户 → GET https://short.ly/aB3xK9
       → 查缓存/DB: shortCode → longUrl
       → HTTP 302 重定向到 longUrl
```

### 1.2 短码生成 3 大策略

| 策略 | 原理 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **自增 ID + Base62** | 数据库自增 ID → Base62 编码 | 短码短、有序、无碰撞 | 单点瓶颈、可预测 | 中小规模 |
| **Snowflake + Base62** | 雪花 ID → Base62 编码 | 分布式、无碰撞、趋势递增 | 短码较长（11 位） | 大规模（推荐） |
| **MD5/Hash 取前 N 位** | 长 URL 哈希 → 取前 6 位 | 相同 URL 生成相同短码 | 碰撞 + 需处理冲突 | 需要去重场景 |

**Base62 编码**：用 `0-9 + a-z + A-Z`（62 个字符）编码数字。

```
6 位 Base62 = 62^6 ≈ 568 亿个短码（够用 50 年）
7 位 Base62 = 62^7 ≈ 3.5 万亿个短码
```

```java
// Base62 编码
private static final String ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

public String toBase62(long num) {
    StringBuilder sb = new StringBuilder();
    while (num > 0) {
        sb.append(ALPHABET.charAt((int)(num % 62)));
        num /= 62;
    }
    return sb.reverse().toString();
}

// 示例：ID = 12345678901 → Base62 = "dnh3j"（5 位）
```

---

## 二、系统架构

### 2.1 高并发架构

```
                        ┌──────────────┐
用户请求 ──────────────→ │   CDN 边缘    │ ← 热门短链缓存（302 响应直接返回）
                        └──────┬───────┘
                               │ 未命中
                        ┌──────▼───────┐
                        │  API Gateway  │ ← 限流 + 路由
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Shortener │   │ Shortener │   │ Shortener │
        │ Service 1 │   │ Service 2 │   │ Service 3 │
        └──────┬───┘   └──────┬───┘   └──────┬───┘
               │               │               │
        ┌──────▼───────────────▼───────────────▼──────┐
        │                  Redis 缓存                   │
        │         shortCode → longUrl（TTL 24h）        │
        └──────────────────┬──────────────────────────┘
                           │ 未命中
        ┌──────────────────▼──────────────────────────┐
        │            MySQL（分库分表）                   │
        │    short_code(主键) | long_url | created_at  │
        └─────────────────────────────────────────────┘
```

### 2.2 数据模型

```sql
CREATE TABLE short_url (
    id          BIGINT PRIMARY KEY,       -- 雪花 ID
    short_code  VARCHAR(10) UNIQUE NOT NULL,
    long_url    VARCHAR(2048) NOT NULL,
    user_id     BIGINT,                   -- 创建者
    click_count BIGINT DEFAULT 0,
    created_at  DATETIME,
    expires_at  DATETIME,                 -- 过期时间（可选）
    INDEX idx_code (short_code),
    INDEX idx_user (user_id, created_at)
) ENGINE=InnoDB;

-- 分库分表：按 short_code 哈希分 16 库 × 16 表
```

---

## 三、7 道精选面试题

### Q1：6 位 Base62 够用多久？

**答**：62^6 ≈ 568 亿个短码。每天新增 1 亿短链，够用 **568 天（~1.5 年）**。不够就加到 7 位（62^7 ≈ 3.5 万亿，够用 96 年）。

### Q2：302 和 301 重定向选哪个？

**答**：

| 特性 | 301（永久重定向） | 302（临时重定向） |
|------|-----------------|-----------------|
| 浏览器缓存 | 缓存（下次直接跳，不经过短链服务） | 不缓存（每次都经过短链服务） |
| 统计能力 | ❌ 无法统计点击 | ✅ 每次都能统计 |
| 修改目标 | 修改后浏览器仍跳旧地址 | 修改后立即生效 |
| **推荐** | 不需要统计 + 永久不变 | **推荐选择**（统计 + 灵活） |

**结论**：选 302。虽然多一次请求，但能统计点击、能修改目标 URL。

### Q3：10 万 QPS 跳转怎么扛？

**答**：4 层优化——

| 层次 | 方案 | 效果 |
|------|------|------|
| **CDN** | 热门短链 302 响应缓存到边缘节点 | 拦截 80% 请求 |
| **Redis** | shortCode → longUrl 缓存（TTL 24h） | 拦截 99% 剩余请求 |
| **DB** | 分库分表（按 shortCode 哈希） | 兜底 |
| **本地缓存** | Caffeine 缓存热门短码 | 减少 Redis 调用 |

**关键**：跳转是**读多写少**场景（写入 1 亿/天 ≈ 1200 QPS，跳转 10 万 QPS），缓存命中率极高。

### Q4：同一个长 URL 多次生成，返回相同还是不同短码？

**答**：两种策略，取决于业务需求——

| 策略 | 实现 | 适用 |
|------|------|------|
| **相同短码** | 长 URL 做 Hash → 查 DB 是否已存在 → 存在则返回旧短码 | 需要去重（分享统计） |
| **不同短码** | 每次都生成新短码（自增 ID） | 不需要去重（每人独立统计） |

**实现"相同短码"**：

```sql
-- 长 URL 的 Hash 做唯一索引
ALTER TABLE short_url ADD UNIQUE INDEX idx_url_hash (url_hash);

-- 生成时先查
SELECT short_code FROM short_url WHERE url_hash = MD5(longUrl);
-- 存在 → 返回旧短码
-- 不存在 → 生成新短码 + INSERT（唯一索引保证并发安全）
```

### Q5：短码碰撞怎么处理？

**答**：取决于生成策略——

| 策略 | 碰撞概率 | 处理 |
|------|---------|------|
| **自增 ID + Base62** | 零碰撞 | 无需处理 |
| **Snowflake + Base62** | 零碰撞 | 无需处理 |
| **Hash 取前 N 位** | 有碰撞 | 冲突时重试（尾部加随机字符） |

```java
// Hash 策略的碰撞处理
String shortCode = toBase62(md5(longUrl).substring(0, 8));
while (db.exists(shortCode)) {
    shortCode = shortCode + randomChar();  // 追加随机字符
}
```

### Q6：短链系统怎么做统计分析？

**答**：异步收集点击事件——

```
用户点击短链 → 302 重定向（同步，低延迟）
            → 同时发送点击事件到 MQ（异步）
            → 消费者批量写入分析表
```

```sql
CREATE TABLE click_log (
    short_code  VARCHAR(10),
    clicked_at  DATETIME,
    ip          VARCHAR(45),
    user_agent  VARCHAR(512),
    referer     VARCHAR(1024),
    country     VARCHAR(2),
    INDEX idx_code_time (short_code, clicked_at)
);
```

**统计维度**：点击量趋势、地域分布、设备分布、来源分析。

### Q7：怎么防止短链被滥用（钓鱼/色情链接）？

**答**：4 层防护——

| 层次 | 方案 |
|------|------|
| **黑名单** | 已知恶意域名 → 拒绝生成 |
| **AI 审核** | 长 URL 目标页面内容检测 |
| **频率限制** | 单用户/单 IP 每分钟最多生成 N 个 |
| **过期机制** | 短链设 TTL（如 30 天），过期自动失效 |

---

## 四、5 大反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| **用 301 重定向** | 浏览器缓存后无法统计点击 | 用 302 |
| **MD5 不处理碰撞** | 不同 URL 生成相同短码 | 碰撞时重试 / 用自增 ID |
| **不分库分表** | 单表亿级数据查询慢 | 按 shortCode 哈希分片 |
| **同步写点击日志** | 拖慢跳转响应 | MQ 异步收集 |
| **不过期清理** | 存储无限增长 | 设 TTL + 定时清理过期数据 |

---

## 五、面试话术（30 秒版）

> "短链系统核心是 3 个环节：短码生成 + 存储 + 跳转。
>
> 短码生成推荐 Snowflake 分布式 ID + Base62 编码（62 个字符，6 位 = 568 亿容量），零碰撞、趋势递增。
>
> 存储用 MySQL 分库分表（按 shortCode 哈希 16 库 × 16 表），Redis 缓存热门短码。
>
> 跳转用 302 重定向（非 301），因为 302 不缓存可以统计每次点击。10 万 QPS 靠 CDN 边缘缓存 + Redis + 本地 Caffeine 三层缓存，99% 请求不命中 DB。
>
> 点击统计异步化——302 跳转同步返回，点击事件发 MQ 异步消费写分析表。防滥用靠黑名单 + AI 审核 + 频率限制 + TTL 过期。"

---

## 六、交叉引用

- **分布式 ID**：[分布式 ID 生成](../../../04.system-design/02-distributed/distributed-id/README.md) — Snowflake / UUID / Leaf（短码生成基础）
- **缓存设计**：[缓存设计模式](../../../04.system-design/04-high-performance/cache-patterns/README.md) — Cache-Aside / Write-Behind
- **分库分表**：[分库分表](../../../04.system-design/04-high-performance/database-optimization/db-sharding/README.md) — 数据分片策略
- **CDN**：[CDN 加速](../../../04.system-design/04-high-performance/cdn/README.md) — 边缘缓存
- **主模块**：[`04.system-design`](../../../04.system-design/) — 系统设计知识体系

## 相关章节

- 深度阅读：[`04.system-design`](../../../04.system-design/README.md) — 主模块详细内容

← [返回: 咬文嚼字 · url-shortener](../README.md)
