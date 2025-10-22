# 如何查找但不导致Redis阻塞

在Java中处理Redis中大量键的场景时，直接使用`KEYS`命令会导致Redis阻塞（尤其1亿键的场景），正确方案应采用非阻塞的`SCAN`命令。以下是分步骤的解决方案及代码示例：

## 1. 核心思路
- **使用SCAN命令**：通过游标增量迭代，避免阻塞Redis。
- **匹配前缀模式**：利用`SCAN`的`MATCH`参数过滤指定前缀的键。
- **批量处理**：循环迭代直到游标归零，收集所有匹配键。

## 2. Java实现代码（基于Jedis）
```java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.ScanParams;
import redis.clients.jedis.ScanResult;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class RedisScanExample {
    public static void main(String[] args) {
        String prefix = "your_prefix:"; // 替换为实际前缀
        try (Jedis jedis = new Jedis("localhost", 6379)) { // 连接Redis
            Set<String> keysWithPrefix = new HashSet<>();
            String cursor = "0"; // 初始游标
            ScanParams scanParams = new ScanParams().match(prefix + "*").count(1000); // 每次扫描1000条

            do {
                ScanResult<String> scanResult = jedis.scan(cursor, scanParams);
                cursor = scanResult.getCursor(); // 更新游标
                List<String> keys = scanResult.getResult();
                keysWithPrefix.addAll(keys); // 收集匹配的键
            } while (!cursor.equals("0")); // 游标归零时结束

            System.out.println("找到符合条件的键数量: " + keysWithPrefix.size());
            // 后续操作（如删除、处理等）
        }
    }
}
```

## 3. 关键点解析
- **非阻塞操作**：`SCAN`通过游标分批获取，避免`KEYS`的全量扫描阻塞。
- **前缀匹配**：`MATCH`参数使用`prefix*`模式精确过滤。
- **游标管理**：循环中动态更新游标，直到返回`0`表示迭代完成。
- **批量大小**：`COUNT`参数控制单次返回数量（可根据性能调整，如1000/5000）。

## 4. 性能优化建议
- **集群环境**：若Redis是集群模式，需对每个节点分别执行`SCAN`。
- **并行处理**：多线程分片扫描（需确保线程安全）。
- **内存控制**：分批处理结果，避免一次性加载过多键到内存。
- **连接池**：使用Jedis连接池管理连接，避免频繁创建。

## 5. 替代方案
- **Redis集群**：使用`CLUSTER NODES`获取节点列表，并行扫描。
- **Lua脚本**：在服务端执行脚本聚合结果（需谨慎评估复杂度）。
- **信息监控**：通过`INFO`命令预估键数量，动态调整`COUNT`值。

通过`SCAN`命令，即使面对1亿键的场景，也能高效安全地获取目标键，同时最小化对Redis的影响。
