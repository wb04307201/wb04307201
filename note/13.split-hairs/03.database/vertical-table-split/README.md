<!--
question:
  id: 03.database-vertical-table-split
  topic: 03.database
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [03.database, 垂直分表, 宽表, InnoDB, Buffer Pool, 大字段]
-->

# 30 个热点字段拆不拆：垂直分表判定规范全解

> 经典数据库面试题（表设计 / DBA 高频）。考察的不是"什么是垂直分表"，而是 **什么时候该拆** + **为什么拆** + **拆了有什么代价** + **InnoDB 底层原理**。完整概念见 [分库分表](../../../04.system-design/04-high-performance/database-optimization/db-sharding/README.md)。

> **系列定位**：中高级后端 / DBA 面试题。考察的是"从 Buffer Pool 命中率到行溢出"的**底层理解**，而不是纸上谈兵。

---

## 引子：一张表的"中年危机"

```text
用户表 user：
  - 50 个字段（id, username, password, email, phone, avatar,
    bio, address, city, province, zip, gender, birthday,
    id_card, real_name, emergency_contact, last_login_ip,
    last_login_time, created_at, updated_at, status,
    vip_level, vip_expire, total_orders, total_spent,
    preference_json, tags_json, device_info, push_token,
    ... 还有 20 个）

问题：
  1. 查询用户列表（只需 username + avatar + status）→ 全表扫描 50 列
  2. InnoDB 页 16KB，一行 2KB → 一页只能放 8 行
  3. 2000 万行 × 2KB = 40GB → Buffer Pool 放不下
```

面试官问："这张表要不要拆？怎么判断？拆了有什么代价？"

如果你只能回答"字段多就拆"——面试就结束了。

---

## 一、拆分判定的 5 个核心指标

### 1.1 单行长度 vs InnoDB 页大小

```text
InnoDB 默认页大小：16 KB
建议：单行长度 < 页大小的 1/16 ≈ 1 KB

原因：
  - 一页至少放 2 行（B+ Tree 需要分裂）
  - 一行占半页 → 页只能放 2 行 → 树高度增加 → 查询变慢
  - 一行 200 字节 → 一页放 80 行 → 树矮胖 → 查询快
```

| 单行长度 | 一页行数（16KB） | B+ Tree 效果 | 判定 |
|---------|----------------|-------------|------|
| < 200B | ~80 行 | ✅ 矮胖，查询快 | 不拆 |
| 200B-1KB | 16-80 行 | ✅ 正常 | 观察 |
| 1KB-4KB | 4-16 行 | ⚠️ 偏高，I/O 多 | **考虑拆** |
| > 4KB | < 4 行 | ❌ 行溢出风险 | **必须拆** |

### 1.2 Buffer Pool 命中率

```text
Buffer Pool 原理：
  InnoDB 把整行数据加载到内存页
  查询 SELECT username, avatar → 仍加载整行 50 列
  → 70% 的内存被冷字段占用 → 热数据命中率低

拆分后：
  热表 user_base（10 列，200B/行）
  → 同样内存可以放 10 倍行数
  → Buffer Pool 命中率从 60% → 95%
```

**经验法则**：
- Buffer Pool 命中率 < 90% → 考虑拆分
- 热字段占整行 < 30% → 拆分收益大
- 热字段占整行 > 70% → 拆分收益小（不值得）

### 1.3 大字段（TEXT / BLOB / JSON）

```text
InnoDB 行格式（COMPACT / DYNAMIC）：
  - 行内存储：前 768 字节 inline
  - 超出部分：溢出到 off-page（外部页）

TEXT / BLOB / 大 JSON 字段：
  - 单个 TEXT 最大 64KB → 一定溢出
  - VARCHAR(10000) → 可能溢出
  - JSON 字段如果平均 > 500B → 大概率溢出

溢出代价：
  读一行数据 → 先读主页 → 再读溢出页 → 2 次 I/O
```

**判定**：有 TEXT / BLOB / 大 JSON → **优先拆出去**

### 1.4 访问频率差异

```text
统计字段的访问频率：
  热字段（每次查询都用）：username, avatar, status
  温字段（偶尔用）：email, phone, address
  冷字段（极少用）：id_card, emergency_contact, preference_json

热:温:冷 = 3:7:40

如果热字段 < 30% 总字段 → 拆分收益大
```

### 1.5 更新频率差异

```text
高频更新字段：last_login_time, last_login_ip, push_token
低频更新字段：username, created_at, gender

如果高频更新字段和低频更新字段混在一起：
  → 更新 last_login_time → 整行加锁 → 影响其他字段的并发读取
  → 拆开后：高频更新字段独立表 → 锁粒度更细
```

## 二、拆分判定决策树（5 步）

```text
Step 1: 单行长度 > 1KB？
  ├─ 是 → Step 2
  └─ 否 → 观察，暂不拆

Step 2: 有 TEXT/BLOB/大JSON 字段？
  ├─ 是 → 拆出去（独立扩展表）
  └─ 否 → Step 3

Step 3: 热字段占比 < 30%？
  ├─ 是 → 拆（热表 + 冷表）
  └─ 否 → Step 4

Step 4: Buffer Pool 命中率 < 90%？
  ├─ 是 → 拆（减少单行大小 → 提高命中率）
  └─ 否 → Step 5

Step 5: 更新频率差异大？
  ├─ 是 → 拆（高频更新字段独立 → 减少锁竞争）
  └─ 否 → 不拆（拆分代价 > 收益）
```

## 三、拆分实战：用户表 50 → 3 表

### 3.1 拆分方案

```text
原始：user（50 列，2KB/行）

拆分后：
├── user_base（热表，8 列，200B/行）
│   id, username, avatar, status, gender,
│   vip_level, created_at, updated_at
│   → 每次查询都读，Buffer Pool 友好
│
├── user_contact（温表，10 列，500B/行）
│   id, email, phone, address, city,
│   province, zip, birthday, real_name, id_card
│   → 详情页 / 编辑页才读
│
└── user_ext（冷表，32 列，含大字段）
    id, bio, emergency_contact, last_login_ip,
    last_login_time, preference_json, tags_json,
    device_info, push_token, ...
    → 极少读，按需加载
```

### 3.2 拆分前后对比

| 指标 | 拆分前 | 拆分后 | 提升 |
|------|--------|--------|------|
| **单行长度** | 2KB | 200B（热表） | 10x |
| **一页行数** | 8 行 | 80 行（热表） | 10x |
| **Buffer Pool 可缓存** | 800 万行/16GB | 8000 万行/16GB | 10x |
| **列表查询 I/O** | 读 2KB/行 | 读 200B/行 | 10x |
| **大字段溢出** | 每次查询都可能读溢出页 | 热表无大字段 | 消除 |

### 3.3 代码层适配

```java
// 拆分前：一条 SQL 查所有
SELECT * FROM user WHERE id = ?;

// 拆分后：按需查询
// 列表页（只需热表）
SELECT id, username, avatar, status FROM user_base WHERE id = ?;

// 详情页（热表 + 温表 JOIN）
SELECT b.*, c.email, c.phone, c.address
FROM user_base b
LEFT JOIN user_contact c ON b.id = c.id
WHERE b.id = ?;

// 完整信息（三表 JOIN，极少用）
SELECT b.*, c.*, e.*
FROM user_base b
LEFT JOIN user_contact c ON b.id = c.id
LEFT JOIN user_ext e ON b.id = e.id
WHERE b.id = ?;
```

## 四、5 个反模式

### 反模式 1：字段多就拆

- **真相**：如果所有字段都是热字段（每次都查），拆了反而多一次 JOIN → 性能更差
- **判定**：热字段 < 30% 总字段 → 拆；否则不拆

### 反模式 2：拆了不管一致性

- **真相**：拆成 3 张表后，更新 user_base 成功但 user_contact 失败 → 数据不一致
- **解法**：同库内用事务保证原子性；跨库需分布式事务

### 反模式 3：用 SELECT * 查热表

- **真相**：拆分后仍 `SELECT *` → 拆了等于没拆
- **解法**：严格指定需要的列，MyBatis 用 resultMap 映射

### 反模式 4：拆出太多小表

- **真相**：50 列拆成 5 张表 → 查完整信息需 4 次 JOIN → 查询复杂度爆炸
- **建议**：最多拆 2-3 张表（热/温/冷 或 基础/扩展）

### 反模式 5：忽视 ORM 的 N+1

- **真相**：MyBatis/Hibernate 延迟加载 → 查 user_base 后自动触发查 user_ext → N+1 问题
- **解法**：关闭自动延迟加载，手动控制 JOIN 时机

## 五、最佳实践

1. **先统计再拆** — 用慢查询日志 + APM 工具统计字段访问频率，不要凭感觉
2. **热表保持轻量** — 控制在 200B/行以内，只放每次查询都需要的字段
3. **主键关联** — 拆分表用同一主键（id），通过 `JOIN ON id` 关联
4. **事务保证一致性** — 同库内 `@Transactional` 保证原子写入
5. **渐进式拆分** — 先拆大字段（TEXT/JSON），再拆冷字段，最后拆温字段
6. **监控先行** — 拆分前后对比 Buffer Pool 命中率、查询延迟、IOPS

## 六、面试话术（90 秒版本）

> "30 个热点字段要不要拆，不能一概而论，要看 5 个指标。
>
> **第一看单行长度**：超过 1KB 考虑拆，超过 4KB 必须拆（InnoDB 16KB 页放不了几行，B+ Tree 变高变瘦）。
>
> **第二看有没有大字段**：TEXT/BLOB/大 JSON 会导致行溢出（off-page），读一行要两次 I/O，优先拆出去。
>
> **第三看热字段占比**：热字段 < 30% 总字段 → 拆分收益大。如果 30 个全是热字段，每次查询都要，拆了反而多一次 JOIN。
>
> **第四看 Buffer Pool 命中率**：低于 90% 说明内存放不下热数据，拆分减小单行大小可以提高命中率。
>
> **第五看更新频率差异**：高频更新字段（last_login_time）和低频字段混在一起会增加锁竞争。
>
> **拆分方法**：最多拆 2-3 张表（热/温/冷），用同一主键关联。事务保证写入一致性，查询按需 JOIN，不要 SELECT *。
>
> **反模式**：字段多就拆、拆了 SELECT *、拆太多小表导致 N+1。"

## 七、相关章节

- 主模块：[`分库分表`](../../../04.system-design/04-high-performance/database-optimization/db-sharding/README.md) — 垂直分表 + 水平分表 + 分片算法全景
- 同模块：[`冷热数据分离`](../../../04.system-design/04-high-performance/database-optimization/cold-hot-data-separation/README.md) — 行级冷热分离（时间维度）
- 同栏目：[`SQL 调优`](../mysql-tuning/README.md) — Explain 分析 + 索引优化
- 同栏目：[`深分页`](../mysql-deep-pagination/README.md) — 大表查询性能优化
- 同栏目：[`分表扩容策略`](../sharding-resize/README.md) — 分表后数据膨胀的处理

---

> 📅 2026-07-07 · 咬文嚼字 · 垂直分表判定规范 · ⭐⭐⭐⭐（高频面试 + DBA 必备）

← [返回数据库咬文嚼字](../README.md)
