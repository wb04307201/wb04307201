# MySQL SQL调优

MySQL SQL调优是一个系统化的过程，涉及从问题定位到持续优化的全流程管理。

## 1. 定位慢查询
- **开启慢查询日志**：设置`long_query_time`阈值（如1秒），通过`slow_query_log=ON`记录超时SQL。生产环境建议永久配置（修改`my.cnf`），临时调试可用`SET GLOBAL`动态调整。
- **分析工具**：使用`mysqldumpslow`按执行次数/耗时排序，或`pt-query-digest`生成深度报告（含执行计划、锁等待、占比分析）。隐性慢查询需关注高频次短查询的累计耗时。

## 2. 执行计划分析
- **EXPLAIN解读**：重点关注`type`（访问类型，如`ALL`全表扫描、`range`索引范围扫描）、`key`（实际使用索引）、`rows`（预估扫描行数）、`Extra`（额外信息）。
    - 理想场景：`type`为`ref`/`eq_ref`/`const`，`Extra`显示`Using index`（覆盖索引）或`Using where`（索引过滤）。
    - 性能瓶颈：`ALL`全表扫描、`Using filesort`（文件排序）、`Using temporary`（临时表）需优先优化。
- **优化器跟踪**：启用`optimizer_trace`分析索引选择逻辑，如联合索引的最左前缀匹配、范围查询后列失效原因。

## 3. 索引优化
- **索引设计原则**：
    - **高选择性**：优先为`WHERE`、`JOIN`、`ORDER BY`、`GROUP BY`中的高区分度列建索引（如`email`优于`gender`）。
    - **联合索引顺序**：高区分度列在前，等值条件在前，排序/分组列在后（如`(status, created_at)`支持`WHERE status='paid' ORDER BY created_at`）。
    - **覆盖索引**：索引包含查询所有字段（如`(email, id, name)`支持`SELECT id, name FROM user WHERE email='x'`），避免回表。
- **失效场景规避**：
    - 避免隐式类型转换（如字符串列用数字查询）、函数操作（如`YEAR(create_time)=2025`改用范围查询）、前导`%`通配符（如`LIKE '%abc'`）。
    - 联合索引需遵循最左前缀，`OR`条件需全列索引或改用`UNION`。
- **维护策略**：定期用`pt-query-digest`或`sys.schema_unused_indexes`清理未使用索引，对碎片化表执行`OPTIMIZE TABLE`。

## 4. SQL语句优化
- **查询重写**：
    - 拆分复杂查询：子查询转`JOIN`，大分页用延迟关联（先通过索引筛选主键，再关联获取完整数据）。
    - 减少数据传输：避免`SELECT *`，仅取必要列；用`LIMIT`限制返回行数。
    - 避免全表扫描：`NOT IN`/`<>`改用`NOT EXISTS`，`OR`条件拆分为多条SQL或用联合索引。
- **表达式优化**：`IN`条件超过200项时，MySQL可能误判索引成本，可调整`eq_range_index_dive_limit`或改用临时表。

## 5. 参数调优
- **核心内存参数**：`innodb_buffer_pool_size`设为系统内存70%-80%，`innodb_log_file_size`调整为1-2GB（减少日志刷新）。
- **连接与超时**：`max_connections`根据业务峰值调整，`wait_timeout`设为300秒释放空闲连接。
- **安全与性能平衡**：`innodb_flush_log_at_trx_commit=2`（每秒刷日志）提升写入性能，`sync_binlog=0`减少磁盘I/O（非金融场景适用）。

## 6. 监控与持续优化
- **性能监控**：使用`SHOW STATUS`跟踪`Com_select`/`Com_update`等指标，`Performance Schema`分析表/索引IO等待。
- **动态调整**：根据数据量增长和业务变化，定期评估索引有效性，更新统计信息（`ANALYZE TABLE`）。
- **架构优化**：结合读写分离、缓存（Redis）、分区表、垂直/水平分表等策略扩展性能。

## 案例验证
- **案例1**：联合索引`(shop_id, order_no)`需携带`shop_id`才能走索引，单独`order_no`查询失效。
- **案例2**：隐式类型转换（如字符串列用数字查询）导致索引失效，需统一类型。
- **案例3**：大分页查询（`LIMIT 10000,10`）改用延迟关联，减少回表次数，耗时从5.2秒降至0.3秒。

通过以上步骤，可系统化定位性能瓶颈，针对性优化索引和查询，最终实现MySQL查询性能的显著提升。调优需持续迭代，结合业务场景动态调整策略。