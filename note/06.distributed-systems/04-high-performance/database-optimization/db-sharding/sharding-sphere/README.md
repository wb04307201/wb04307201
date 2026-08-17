<!--
module:
  parent: system-design
  slug: system-design/sharding-sphere
  type: article
  category: 主模块子文章
  summary: Apache ShardingSphere 分库分表中间件——JDBC vs Proxy 架构选型 + 分片策略配置
-->

# ShardingSphere

> Apache ShardingSphere 是分布式数据库中间件，提供 JDBC（嵌入式）和 Proxy（独立代理）两种接入方式，覆盖分片/读写分离/分布式事务/数据迁移全场景。

## 一、架构选型：JDBC vs Proxy

| 维度 | ShardingSphere-JDBC | ShardingSphere-Proxy |
|------|---------------------|----------------------|
| 部署方式 | JAR 包嵌入应用 | 独立进程（类似 MySQL Server） |
| 语言支持 | 仅 Java | 任意语言（标准 MySQL 协议） |
| 性能 | 高（无网络跳转） | 中（多一跳） |
| 运维复杂度 | 低（随应用部署） | 高（需独立维护） |
| 适用场景 | OLTP / 微服务 | OLAP / 多语言异构 |

## 二、分片策略配置（YAML 示例）

```yaml
# ShardingSphere 5.x 分片规则配置
rules:
  - !SHARDING
    tables:
      t_order:
        actualDataNodes: ds_${0..1}.t_order_${0..3}
        databaseStrategy:
          standard:
            shardingColumn: user_id
            shardingAlgorithmName: db_hash_mod
        tableStrategy:
          standard:
            shardingColumn: order_id
            shardingAlgorithmName: table_mod
    shardingAlgorithms:
      db_hash_mod:
        type: HASH_MOD
        props:
          sharding-count: 2
      table_mod:
        type: MOD
        props:
          sharding-count: 4
```

**关键参数说明**：
- `actualDataNodes`：真实数据节点（`ds_0.t_order_0` ~ `ds_1.t_order_3`，共 8 张表）
- `databaseStrategy`：库级分片（按 `user_id` 哈希取模）
- `tableStrategy`：表级分片（按 `order_id` 取模）

## 三、SPI 插件机制（源码级扩展）

ShardingSphere 通过 SPI（Service Provider Interface）实现可插拔架构：

```java
// 自定义分片算法（实现 ShardingAlgorithm 接口）
public class CustomShardingAlgorithm implements StandardShardingAlgorithm<Long> {
    @Override
    public String doSharding(final Collection<String> availableTargetNames,
                             final ShardingValue<Long> shardingValue) {
        Long orderId = shardingValue.getValue();
        // 自定义路由逻辑：奇数走 ds_0，偶数走 ds_1
        int dsIndex = (orderId % 2 == 0) ? 0 : 1;
        return "ds_" + dsIndex;
    }
}
```

**SPI 扩展点**：
- `ShardingAlgorithm`：分片算法
- `KeyGenerateAlgorithm`：分布式主键生成（雪花/UUID）
- `ShardingAuditAlgorithm`：分片审计（如禁止全路由查询）

## 四、版本对比：4.x vs 5.x

| 特性 | 4.x | 5.x |
|------|-----|-----|
| 配置方式 | `.properties` 文件 | YAML（结构化） |
| 分布式事务 | XA / BASE | XA / BASE / Saga |
| 数据迁移 | 手动 | Schema + Data 自动迁移 |
| SQL 解析 | ANTLR 4.7 | ANTLR 4.10（性能提升 30%） |
| 可观测性 | 无 | Prometheus + OpenTracing |

## 五、常见陷阱与反模式

| 陷阱 | 现象 | 根因 | 规避 |
|------|------|------|------|
| ❌ 全路由查询 | `SELECT * FROM t_order` 扫描所有分片 | WHERE 未包含分片键 | 强制分片键索引 + SQL 审计 |
| ❌ 跨分片 JOIN | `t_order JOIN t_item` 性能暴跌 | 两张表分片键不一致 | 绑定表（Binding Table） |
| ❌ 分布式主键冲突 | 多节点生成相同 ID | 未配置雪花算法 | `key-generators: snowflake` |

## 六、生产参数调优

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `max-connections-size-per-query` | 1 | 单次查询最大连接数 |
| `worker-thread` | CPU 核数 × 2 | Proxy 工作线程 |
| `transaction-type` | XA | 强一致性场景 |
| `sql-show` | false | 生产关闭 SQL 日志 |

---

← [返回 分库分表](../README.md)