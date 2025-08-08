# ULID

## 一、ULID 核心特性
1. **全局唯一性**  
   ULID（Universally Unique Lexicographically Sortable Identifier）由 **48位时间戳**（毫秒级）和 **80位随机数** 组成，确保同一毫秒内生成的标识符唯一。其理论生成能力为每毫秒 **1.21×10²⁴** 个唯一 ID，远超 UUID v4 的随机性限制。

2. **字典序排序**  
   时间戳位于标识符前半部分，使 ULID 可按生成时间排序。例如：
   ```
   01F9Z3NDEKTSV4RRFFQ69G5FAV（较早）  
   01F9Z3NDEKTSV4RRFFQ69G5FBW（较晚）
   ```
   这一特性在数据库索引、日志排序等场景中显著提升性能。

3. **紧凑性与可读性**
    - **长度**：26 字符（Crockford's Base32 编码），比 36 字符的 UUID 更短。
    - **编码规则**：排除易混淆字符（如 `0/O`、`1/l`），支持人工输入和视觉区分。

4. **高性能生成**  
   无需网络请求或中心化协调，本地生成速度优于 UUID（尤其在分布式系统中）。

## 二、ULID vs UUID：关键差异
| **特性**    | **ULID**       | **UUID**          |
|-----------|----------------|-------------------|
| **排序能力**  | 支持字典序排序        | 随机分布，无法直接排序       |
| **唯一性保障** | 时间戳 + 随机数      | 版本依赖（如 v4 仅依赖随机数） |
| **长度**    | 26 字符          | 36 字符（含连字符）       |
| **适用场景**  | 分布式排序、日志、数据库主键 | 通用唯一标识            |

## 三、Java 实现方案
### 方案 1：使用 `ulid-java` 库（推荐）
1. **添加依赖**（Maven）：
   ```xml
   <dependency>
       <groupId>com.github.f4b6a3</groupId>
       <artifactId>ulid-creator</artifactId>
       <version>5.0.0</version>
   </dependency>
   ```

2. **生成 ULID**：
   ```java
   import com.github.f4b6a3.ulid.UlidCreator;

   public class UlidExample {
       public static void main(String[] args) {
           // 生成标准 ULID
           String ulid = UlidCreator.getUlid().toString();
           System.out.println("Generated ULID: " + ulid);

           // 获取时间戳（毫秒）
           long timestamp = UlidCreator.getTimestamp(ulid);
           System.out.println("Timestamp: " + timestamp);
       }
   }
   ```

3. **高级功能**：
    - **单调 ULID**：确保同一毫秒内生成的 ID 递增（适用于高并发场景）：
      ```java
      String monotonicUlid = UlidCreator.getMonotonicUlid().toString();
      ```
    - **自定义时间戳**：
      ```java
      long customTimestamp = System.currentTimeMillis();
      String ulidWithTimestamp = UlidCreator.fromTimestamp(customTimestamp).toString();
      ```

### 方案 2：使用 `ulid4j` 库
1. **添加依赖**：
   ```xml
   <dependency>
       <groupId>io.github.java-ulid</groupId>
       <artifactId>ulid4j</artifactId>
       <version>1.0.0</version>
   </dependency>
   ```

2. **生成 ULID**：
   ```java
   import io.github.javaulid.ULID;

   public class Ulid4jExample {
       public static void main(String[] args) {
           ULID ulid = ULID.randomULID();
           System.out.println("ULID: " + ulid.toString());
       }
   }
   ```

## 四、应用场景推荐
1. **分布式系统**
    - 作为实体唯一标识符，避免 UUID 的冲突风险。
    - 示例：订单 ID、用户 ID 生成。

2. **数据库主键**
    - 替代自增 ID，支持水平分库分表时的排序查询。
    - 示例：MySQL 主键、MongoDB `_id` 字段。

3. **日志追踪**
    - 结合时间戳的排序能力，快速定位事件顺序。
    - 示例：微服务调用链跟踪 ID。

4. **云服务资源标识**
    - 唯一标识虚拟机、容器或存储对象。
    - 示例：AWS EC2 实例 ID、S3 对象键。

## 五、安全注意事项
1. **随机数熵值**  
   确保随机数生成器使用加密安全的算法（如 `SecureRandom`），防止预测攻击。

2. **时间戳暴露**  
   ULID 的时间戳可能泄露生成时间，敏感场景需结合加密混淆。

3. **单调性控制**  
   高并发下使用单调 ULID 时，需评估时钟回拨问题（如 NTP 同步导致的时间倒退）。

## 六、总结
ULID 通过结合时间戳和随机数，在保持唯一性的同时提供了排序能力，是 UUID 的理想替代方案。在 Java 中，推荐使用 `ulid-creator` 库，其功能全面且性能优异。实际应用中，需根据场景选择标准 ULID 或单调 ULID，并关注安全性和时钟同步问题。