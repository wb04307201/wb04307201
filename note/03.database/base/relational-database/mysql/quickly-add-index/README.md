# 1亿条数据快速加索引的方法

为1亿条数据的MySQL表添加索引需要谨慎操作，因为直接添加索引可能会导致长时间锁表、性能下降甚至服务中断。

## 1. 使用在线DDL操作（MySQL 5.6+）

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

## 2. 使用pt-online-schema-change工具（Percona Toolkit）

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

## 3. 使用gh-ost工具（GitHub开源工具）

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

## 4. 分批处理（适用于离线环境）

如果允许停机维护：
1. 创建新表结构（包含新索引）
2. 分批导入数据（如每次100万条）
3. 验证数据完整性
4. 重命名表切换

## 优化建议

1. **选择低峰期操作**：减少对生产环境的影响
2. **监控资源使用**：特别是I/O和CPU使用率
3. **调整参数**：
    - 增加`innodb_buffer_pool_size`
    - 临时调整`innodb_io_capacity`和`innodb_io_capacity_max`
4. **考虑索引必要性**：确保添加的索引确实能提高查询性能
5. **测试环境验证**：先在测试环境模拟操作

## 性能对比

| 方法     | 停机时间 | 资源消耗 | 复杂度 | 适用场景       |
|--------|------|------|-----|------------|
| 在线DDL  | 短    | 中    | 低   | MySQL 5.6+ |
| pt-osc | 极短   | 高    | 中   | 复杂环境       |
| gh-ost | 短    | 低    | 中   | 云环境        |
| 分批处理   | 长    | 可控   | 高   | 离线环境       |

对于1亿条数据，推荐优先考虑pt-online-schema-change或gh-ost工具，它们提供了最好的平衡点。