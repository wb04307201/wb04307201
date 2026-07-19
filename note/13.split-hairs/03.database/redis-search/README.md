<!--
question:
  id: 03.database-search
  topic: 03.database
  difficulty: ⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [03.database, Redis, search]
-->

# Redis搜索能力深度解析：从KEYS到RediSearch

## 一、核心原理

Redis作为键值存储，原生搜索能力有限。理解各种方案的适用场景和性能特征至关重要。

**搜索方案对比：**

| **方案** | **时间复杂度** | **阻塞风险** | **功能支持** | **内存开销** | **适用规模** |
|---------|--------------|------------|------------|------------|------------|
| `KEYS pattern` | O(N) | **高**（全量遍历） | 仅模式匹配 | 无额外 | <1万键 |
| `SCAN`+`MATCH` | O(N)分批 | **低**（增量迭代） | 仅模式匹配 | 无额外 | <100万键 |
| `SSCAN/HSCAN` | O(N)分批 | **低** | 仅模式匹配 | 无额外 | 大型集合 |
| Sorted Set评分 | O(log N) | 低 | 范围查询、排序 | 中等 | 中等规模 |
| **RediSearch** | O(log N + K) | 低 | 全文检索、模糊、聚合 | 较高 | 大规模 |

**KEYS的致命问题：**单线程阻塞，O(N)复杂度，1亿键可能阻塞数十秒，生产环境禁用。

**SCAN工作原理：**
```
SCAN cursor [MATCH pattern] [COUNT count]
- 游标迭代：基于游标的增量式迭代，每次返回部分结果和新游标
- 非严格一致性：迭代期间新增/删除的键可能不会被完整捕获
- COUNT参数：提示每次迭代数量，不保证精确
- 时间分摊：将O(N)工作分摊到多次调用中
```

## 二、代码示例

**1. Java安全SCAN（Jedis）**

```java
public static Set<String> scanKeys(Jedis jedis, String prefix, int batchSize) {
    Set<String> matched = new HashSet<>();
    String cursor = "0";
    ScanParams params = new ScanParams().match(prefix+"*").count(batchSize);
    do {
        ScanResult<String> r = jedis.scan(cursor, params);
        cursor = r.getCursor();
        matched.addAll(r.getResult());
        if (matched.size() > 10000) throw new IllegalStateException("匹配键过多");
    } while (!cursor.equals("0"));
    return matched;
}
Set<String> keys = scanKeys(jedis, "user:profile:", 1000);
```

**2. Lettuce客户端（Spring Boot默认）**

```java
public Flux<String> scanKeys(StatefulRedisConnection<String,String> conn, String pattern) {
    return Flux.generate(sink -> {
        ScanCursor cursor = ScanCursor.INITIAL;
        do {
            var r = conn.sync().scan(ScanArgs.Builder.matches(pattern).limit(1000));
            r.getKeys().forEach(sink::next);
            cursor = r;
        } while (!cursor.isFinished());
        sink.complete();
    });
}
```

**3. 集群SCAN**

```java
public static Map<String,Set<String>> scanCluster(JedisCluster cluster, String pattern) {
    Map<String,Set<String>> results = new HashMap<>();
    cluster.getClusterNodes().forEach((nodeId, node) -> {
        if (!node.isMaster()) return;
        Set<String> keys = new HashSet<>();
        try (Jedis j = new Jedis(node.getHostAndPort().getHost(), node.getHostAndPort().getPort())) {
            String cursor = "0";
            do {
                ScanResult<String> r = j.scan(cursor, new ScanParams().match(pattern).count(1000));
                cursor = r.getCursor(); keys.addAll(r.getResult());
            } while (!cursor.equals("0"));
        }
        results.put(nodeId, keys);
    });
    return results;
}
```

**4. RediSearch全文检索**

```java
public class RediSearchExample {
    private static final String INDEX_NAME = "userIdx";
    
    public void createIndex(UnifiedJedis jedis) {
        Schema schema = new Schema()
            .addTextField("name", 5.0).addTextField("email", 3.0)
            .addNumericField("age").addTagField("city");
        IndexDefinition rule = new IndexDefinition(IndexDefinition.Type.HASH).setPrefixes(new String[]{"user:"});
        jedis.ftCreate(INDEX_NAME, IndexOptions.DEFAULT, schema);
    }
    
    public void addDoc(UnifiedJedis jedis, String userId, String name, String email, int age, String city) {
        jedis.hset("user:"+userId, Map.of("name",name,"email",email,"age",age,"city",city));
    }
    
    public List<Map<String,Object>> search(UnifiedJedis jedis, String keyword) {
        Query q = new Query(keyword).limit(0, 20).sortBy("age", true);
        SearchResult r = jedis.ftSearch(INDEX_NAME, q);
        return r.getDocuments().stream().map(d -> ((redis.clients.jedis.search.Document)d).getProperties()).collect(Collectors.toList());
    }
    
    // 复杂查询：名字含"张"且年龄25-35且城市北京
    public List<Map<String,Object>> advanced(UnifiedJedis jedis) {
        Query q = new Query("@name:张 @age:[25 35] @city:{北京}").limit(0, 50);
        return parseResults(jedis.ftSearch(INDEX_NAME, q));
    }
}
```

## 三、常见陷阱

**陷阱1：生产环境使用KEYS**
```java
// ❌ 绝对禁止
Set<String> keys = jedis.keys("user:*");  // 1亿键阻塞数十秒
// ✅ 使用SCAN
Set<String> keys = scanKeys(jedis, "user:", 1000);
```

**陷阱2：忽略SCAN的不一致性**
```java
// SCAN在迭代过程中可能遗漏或重复返回键
// 解决方案：接受最终一致性 / 业务层维护快照 / 用ZSet维护有序列表
```

**陷阱3：COUNT参数不当**
```java
// ❌ 太小：网络开销大
new ScanParams().match("user:*").count(10);
// ❌ 太大：单次处理时间长
new ScanParams().match("user:*").count(100000);
// ✅ 合理：100-1000
new ScanParams().match("user:*").count(500);
```

**陷阱4：集群中只扫单个节点**
```java
// ❌ 只扫一个节点遗漏其他节点数据
Jedis j = new Jedis("node1", 6379);
Set<String> keys = scanKeys(j, "user:*");  // 只有1/N的数据
// ✅ 遍历所有主节点
Map<String,Set<String>> allKeys = scanCluster(cluster, "user:*");
```

**陷阱5：一次性加载所有结果**
```java
// ❌ 可能百万级键导致OOM
Set<String> allKeys = scanKeys(jedis, "*", 1000);

// ✅ 流式处理
public void processKeys(Jedis jedis, String pattern, Consumer<String> handler) {
    String cursor = "0";
    do {
        ScanResult<String> r = jedis.scan(cursor, new ScanParams().match(pattern).count(500));
        cursor = r.getCursor();
        for (String key : r.getResult()) handler.accept(key);
    } while (!cursor.equals("0"));
}
```

## 四、最佳实践

**1. 选型决策**
```
搜索需求？
├── 简单模式匹配：<1万→KEYS；≥1万→SCAN+MATCH
├── 集合内搜索→SSCAN/HSCAN/ZSCAN
├── 全文检索：<10万→应用层过滤；≥10万→RediSearch
└── 精确键查找→GET/MGET（O(1)）
```

**2. 设计阶段规避搜索**
```java
// 反模式：依赖键名模式查询 → 只能SCAN
// 正模式：维护二级索引
jedis.sadd("active:users", "user:1001", "user:1002");  // Set维护活跃用户
jedis.zadd("users:by:score", 95.5, "user:1001");       // ZSet维护排序索引
Set<String> top = jedis.zrevrange("users:by:score", 0, 9);  // Top 10
```

**3. 封装工具类**

```java
public class RedisScanner implements AutoCloseable {
    private final Jedis jedis;
    public RedisScanner(Jedis j) { this.jedis = j; }
    public void forEachMatch(String pattern, Consumer<String> handler) {
        String cursor = "0"; int processed = 0;
        do {
            ScanResult<String> r = jedis.scan(cursor, new ScanParams().match(pattern).count(500));
            cursor = r.getCursor();
            for (String key : r.getResult()) { handler.accept(key); if (++processed > 100000) throw new IllegalStateException("超限"); }
        } while (!cursor.equals("0"));
    }
    @Override public void close() { jedis.close(); }
}
try (RedisScanner s = new RedisScanner(jedis)) { s.forEachMatch("user:*", k -> System.out.println(jedis.get(k))); }
```

**4. RediSearch调优**
```java
Schema schema = new Schema()
    .addTextField("title", 10.0).addTextField("desc", 1.0)
    .addNumericField("price").addTagField("category").addGeoField("location");
IndexOptions opts = IndexOptions.builder().setMaxTextFields(true)
    .setStopwordsList(new String[]{"the","a","an"}).build();
jedis.ftCreate("products", opts, schema);
```

**5. 监控**
```java
@Component
public class ScanMetrics {
    private final MeterRegistry mr;
    public void record(String pattern, long ms, int found) {
        mr.counter("redis.scan.requests", "pattern", pattern).increment();
        mr.timer("redis.scan.duration", "pattern", pattern).record(ms, TimeUnit.MILLISECONDS);
    }
}
```

## 五、面试话术

**面试官：Redis有1亿个键，如何高效查找特定前缀的键？**

回答要点：
1. **严禁KEYS**：KEYS会阻塞Redis，生产环境禁用
2. **SCAN方案**：SCAN+MATCH增量迭代，设置合理COUNT（500-1000）
3. **集群考虑**：需遍历所有主节点
4. **架构优化**：业务层维护二级索引（Set/ZSet），避免运行时搜索
5. **终极方案**：全文检索用RediSearch

**面试官：SCAN和KEYS的本质区别？**

回答要点：
- **执行模式**：KEYS一次性遍历全部；SCAN基于游标分批返回
- **阻塞影响**：KEYS阻塞直到完成；SCAN每次占用少量时间片
- **一致性**：KEYS保证一致；SCAN是最终一致性
- **返回值**：KEYS直接返回所有键；SCAN返回游标+本批键，需循环

**面试官：如何实现Redis模糊搜索？**

回答要点：
- **简单模式**：SCAN+MATCH支持通配符（*、?、[]）
- **全文检索**：RediSearch支持分词、模糊匹配、拼音
- **前缀树**：应用层Trie映射到ZSet
- **权衡**：根据数据量和复杂度选择

## 六、交叉引用

- **相关主题**：[Redis缓存穿透/击穿/雪崩](../cache-penetration-breakdown-avalanche/README.md)
- **延伸学习**：[Redis大Key问题](../redis-big-key/README.md)
- **性能优化**：[Redis管道](../redis-cluster/README.md) - 批量操作效率
- **集群架构**：[Redis Cluster](../redis-cluster/README.md) - 分布式搜索策略

## 相关章节

- 深度阅读：[`03.database`](../../../03.database/README.md) — 主模块详细内容

← [返回数据库咬文嚼字](../README.md)
