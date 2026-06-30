<!--
question:
  id: 03.database-quickly-add-index
  topic: 03.database
  difficulty: 未标
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [03.database, quickly, add]
-->

# 1亿条数据快速加索引的方法

## 引子：加个索引，为什么锁表 30 分钟？

```sql
ALTER TABLE huge_table ADD INDEX idx_user_id (user_id);
-- 1 亿条数据，直接 ALTER → 锁表 30 分钟 → 线上业务全停
```

大表加索引是个高危操作。直接 ALTER 会：
1. **锁表**：加索引期间，写操作全部阻塞
2. **占资源**：CPU、内存、IO 飙升
3. **耗时长**：1 亿条数据可能几分钟到几十分钟

怎么在不影响线上业务的情况下，给大表加索引？

---

> 📚 **前置知识**：[MySQL 索引](../../../../../03.database/04-index/README.md)

## 一、使用在线DDL操作（MySQL 5.6+）

```sql
ALTER TABLE large_table ADD INDEX idx_column_name(column_name), ALGORITHM=INPLACE, LOCK=NONE;
```

**优点**：
- 减少锁表时间
- 允许并发DML操作
- 适用于InnoDB存储引擎

**注意事项**：
- 需要MySQL 5.6或更高版本
- 某些索引类型可能不支持在线操作
- 监控服务器资源使用情况

**ALGORITHM 参数详解：**
- `INPLACE`：在原表上执行，避免复制整张表，速度快但需要更多共享元数据锁
- `COPY`：创建临时表复制数据，兼容性最好但速度慢，锁表时间长
- `DEFAULT`：让优化器自动选择（通常选INPLACE）

**LOCK 参数详解：**
- `NONE`：不持有锁，读写完全并发，最快但可能在某些场景下失败回退
- `SHARED`：持有共享锁，允许读但不允许写
- `EXCLUSIVE`：持有排他锁，读写都阻塞，最慢但最安全
- `DEFAULT`：让优化器自动选择最小锁定级别

**实际操作示例：**

```sql
-- 先检查磁盘空间（需要至少1倍表大小的空闲空间）
SELECT table_schema, table_name, 
       ROUND(data_length / 1024 / 1024 / 1024, 2) AS data_gb,
       ROUND(index_length / 1024 / 1024 / 1024, 2) AS index_gb
FROM information_schema.tables 
WHERE table_name = 'large_table';

-- 执行在线DDL
ALTER TABLE large_table ADD INDEX idx_created_at(created_at), 
                        ALGORITHM=INPLACE, LOCK=NONE;

-- 监控进度（MySQL 8.0+）
SELECT * FROM performance_schema.stage_events_current 
WHERE EVENT_NAME LIKE '%alter%';
```

## 二、使用pt-online-schema-change工具（Percona Toolkit）

```bash
pt-online-schema-change --alter "ADD INDEX idx_column_name(column_name)" D=database,t=large_table --execute
```

**优点**：
- 几乎零停机时间
- 自动创建影子表并同步数据
- 支持各种复杂操作

**工作原理**：
1. 创建与原表结构相同的影子表
2. 在影子表上添加索引
3. 通过触发器同步原表到影子表的变更
4. 最后原子性地切换表

**关键参数调优：**

```bash
pt-online-schema-change \
  --alter "ADD INDEX idx_column_name(column_name)" \
  D=database,t=large_table \
  --chunk-size=10000 \          # 每批处理的行数
  --max-lag=1s \                # 主从复制最大延迟
  --check-slave-lag=slave_host \ # 指定从库检查延迟
  --execute
```

**触发器开销：** pt-osc会在原表上创建INSERT/UPDATE/DELETE触发器，高并发场景下可能影响性能约5-10%。建议在低峰期执行。

## 三、使用gh-ost工具（GitHub开源工具）

```bash
gh-ost \
  --database="database" \
  --table="large_table" \
  --alter="ADD INDEX idx_column_name(column_name)" \
  --execute \
  --allow-on-master \
  --initially-drop-old-table \
  --verbose
```

**优点**：
- 轻量级，资源占用少
- 支持流量切换验证
- 提供详细的进度监控

**工作原理与pt-osc的区别：**
- gh-ost **不使用触发器**，而是通过读取binlog来同步变更
- 采用"幽灵表"机制，逐步将数据从原表复制到新表
- 支持动态调整迁移速率

**安全特性：**
- `--panic-flag-file`：当该文件被创建时，立即停止迁移
- `--postpone-cut-over-flag-file`：暂停最后的切换操作，等待人工确认

## 四、分批处理（适用于离线环境）

如果允许停机维护：
1. 创建新表结构（包含新索引）
2. 分批导入数据（如每次100万条）
3. 验证数据完整性
4. 重命名表切换

**分批导入脚本示例：**

```sql
-- 步骤1：创建新表
CREATE TABLE large_table_new LIKE large_table;
ALTER TABLE large_table_new ADD INDEX idx_column_name(column_name);

-- 步骤2：分批插入（每次100万条）
INSERT INTO large_table_new SELECT * FROM large_table WHERE id BETWEEN 1 AND 1000000;
INSERT INTO large_table_new SELECT * FROM large_table WHERE id BETWEEN 1000001 AND 2000000;
-- ... 重复直到完成

-- 步骤3：验证数据一致性
SELECT COUNT(*) FROM large_table;
SELECT COUNT(*) FROM large_table_new;

-- 步骤4：原子切换
RENAME TABLE large_table TO large_table_old, 
             large_table_new TO large_table;
```

**性能优化技巧：**
- 关闭autocommit，手动控制事务大小（每10-50万行提交一次）
- 临时设置 `innodb_flush_log_at_trx_commit=2` 减少刷盘频率

## 五、常见陷阱与优化建议

**陷阱1：磁盘空间不足** - 在线DDL需要额外1-2倍表大小的空间，1亿行数据可能需要数百GB。

**陷阱2：主从复制延迟** - 大表DDL会导致从库落后数小时。使用pt-osc的`--max-lag`或gh-ost的`--throttle-control-replicas`控制速率。

**优化建议：**
1. **选择低峰期操作**：减少对生产环境的影响
2. **监控资源使用**：特别是I/O和CPU使用率
3. **调整参数**：增加`innodb_buffer_pool_size`，临时调整`innodb_io_capacity`
4. **测试环境验证**：先在测试环境模拟操作

1. **选择低峰期操作**：减少对生产环境的影响
2. **监控资源使用**：特别是I/O和CPU使用率
3. **调整参数**：增加`innodb_buffer_pool_size`，临时调整`innodb_io_capacity`
4. **测试环境验证**：先在测试环境模拟操作

| 方法     | 停机时间 | 资源消耗 | 复杂度 | 适用场景       | 1亿行预估耗时 |
|--------|------|------|-----|------------|----------|
| 在线DDL  | 秒级  | 中    | 低   | MySQL 5.6+ | 2-4小时   |
| pt-osc | 毫秒级 | 高    | 中   | 复杂环境       | 4-8小时   |
| gh-ost | 秒级  | 低    | 中   | 云环境        | 3-6小时   |
| 分批处理   | 分钟级 | 可控   | 高   | 离线环境       | 1-2小时   |

| 方法     | 停机时间 | 资源消耗 | 适用场景       | 1亿行预估耗时 |
|--------|------|------|------------|----------|
| 在线DDL  | 秒级  | 中    | MySQL 5.6+ | 2-4小时   |
| pt-osc | 毫秒级 | 高    | 复杂环境       | 4-8小时   |
| gh-ost | 秒级  | 低    | 云环境        | 3-6小时   |
| 分批处理   | 分钟级 | 可控   | 离线环境       | 1-2小时   |

对于1亿条数据，推荐优先考虑pt-online-schema-change或gh-ost工具。如果是在MySQL 8.0+且业务可以接受短暂锁表，直接使用在线DDL也是不错的选择。

**面试要点：**
1. 在线DDL的原理和LOCK参数选择
2. pt-osc vs gh-ost（触发器 vs binlog同步）
3. 如何评估DDL对主从复制的影响## 相关章节

- 深度阅读：[`03.database/04-index`](../../../../../03.database/04-index/README.md) — B+ 树、索引原理
- 相关：[`13.split-hairs/mysql/index-failure`](../../../mysql/index-failure/README.md) — 索引失效 10 种场景
