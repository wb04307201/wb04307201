# JDBC

JDBC（Java Database Connectivity）是 Java 提供的一套用于执行 SQL 语句的 API，可以为多种关系型数据库（如 MySQL、Oracle、PostgreSQL 等）提供统一的访问方式。

---

## 一、JDBC 的核心组件

JDBC 由以下核心接口和类组成：

| 组件 | 说明 |
|------|------|
| `DriverManager` | 管理数据库驱动，用于获取数据库连接 |
| `Connection` | 代表与特定数据库的连接（会话） |
| `Statement` | 用于执行静态 SQL 语句 |
| `PreparedStatement` | 用于执行预编译 SQL 语句（防止 SQL 注入） |
| `CallableStatement` | 用于执行数据库存储过程 |
| `ResultSet` | 表示数据库查询结果的表格数据 |
| `SQLException` | 所有 JDBC 异常的父类 |

---

## 二、JDBC 编程步骤

使用 JDBC 操作数据库一般包含以下 6 个步骤：

### 1. 加载数据库驱动（可选，JDBC 4.0+ 自动加载）

```java
// 旧版本写法（JDBC 4.0 之前）
Class.forName("com.mysql.cj.jdbc.Driver");

// JDBC 4.0+（Java 6+）自动加载，无需手动调用 Class.forName()
```

> **注意**：从 JDBC 4.0 开始，只要将驱动 JAR 放在 classpath 中，JVM 会自动加载驱动。

---

### 2. 建立数据库连接（Connection）

```java
String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false&serverTimezone=UTC";
String username = "root";
String password = "123456";

Connection conn = DriverManager.getConnection(url, username, password);
```

> **URL 格式**：`jdbc:<subprotocol>:<subname>`  
> 例如 MySQL：`jdbc:mysql://host:port/database`

---

### 3. 创建 Statement 对象

```java
// 普通 Statement（不推荐用于用户输入）
Statement stmt = conn.createStatement();

// 推荐使用 PreparedStatement（防 SQL 注入）
String sql = "SELECT * FROM users WHERE id = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setInt(1, 1001);
```

---

### 4. 执行 SQL 语句

| 方法 | 用途 |
|------|------|
| `executeQuery()` | 执行查询语句（SELECT），返回 `ResultSet` |
| `executeUpdate()` | 执行更新语句（INSERT/UPDATE/DELETE），返回受影响行数 |
| `execute()` | 执行任意 SQL，返回 boolean（true 表示 ResultSet） |

**示例：查询**

```java
ResultSet rs = pstmt.executeQuery();
while (rs.next()) {
    int id = rs.getInt("id");
    String name = rs.getString("name");
    System.out.println(id + ": " + name);
}
```

**示例：插入**

```java
String insertSql = "INSERT INTO users(name, email) VALUES (?, ?)";
PreparedStatement insertStmt = conn.prepareStatement(insertSql);
insertStmt.setString(1, "张三");
insertStmt.setString(2, "zhangsan@example.com");
int rows = insertStmt.executeUpdate(); // 返回 1
```

---

### 5. 处理结果集（ResultSet）

`ResultSet` 是一个游标，初始位置在第一行之前，需调用 `next()` 移动。

常用方法：

- `next()`：移动到下一行，返回是否还有数据
- `getInt(String column)` / `getString(String column)`：按列名获取值
- `wasNull()`：判断上一次获取的值是否为 NULL

---

### 6. 关闭资源（重要！）

必须按 **后开先关** 的顺序关闭资源，防止内存泄漏：

```java
if (rs != null) rs.close();
if (stmt != null) stmt.close();
if (conn != null) conn.close();
```

> **推荐使用 try-with-resources（Java 7+）自动关闭**：

```java
try (Connection conn = DriverManager.getConnection(url, user, pwd);
     PreparedStatement pstmt = conn.prepareStatement(sql);
     ResultSet rs = pstmt.executeQuery()) {

    while (rs.next()) {
        // 处理结果
    }
} catch (SQLException e) {
    e.printStackTrace();
}
// 资源自动关闭
```

---

## 三、PreparedStatement vs Statement

| 特性 | Statement | PreparedStatement |
|------|----------|------------------|
| SQL 注入风险 | 高（拼接字符串） | 无（参数化查询） |
| 性能 | 每次解析 SQL | 预编译，多次执行更快 |
| 可读性 | 差 | 好 |
| 适用场景 | 静态 SQL（无参数） | 动态 SQL（推荐使用） |

✅ **始终优先使用 `PreparedStatement`！**

---

## 四、事务管理

默认情况下，JDBC 的 `Connection` 是 **自动提交（auto-commit）** 模式。

### 手动控制事务：

```java
conn.setAutoCommit(false); // 关闭自动提交

try {
    // 执行多个操作
    pstmt1.executeUpdate();
    pstmt2.executeUpdate();
    
    conn.commit(); // 提交事务
} catch (SQLException e) {
    conn.rollback(); // 回滚
} finally {
    conn.setAutoCommit(true); // 恢复自动提交
}
```

---

## 五、批处理（Batch Processing）

用于一次性执行多条相同结构的 SQL，提升性能：

```java
String sql = "INSERT INTO logs(message) VALUES (?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    for (String msg : messages) {
        pstmt.setString(1, msg);
        pstmt.addBatch(); // 添加到批处理
    }
    int[] results = pstmt.executeBatch(); // 执行批处理
}
```

---

## 六、获取自增主键

插入后获取数据库生成的 ID：

```java
String sql = "INSERT INTO users(name) VALUES (?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
    pstmt.setString(1, "李四");
    pstmt.executeUpdate();
    
    try (ResultSet generatedKeys = pstmt.getGeneratedKeys()) {
        if (generatedKeys.next()) {
            long id = generatedKeys.getLong(1);
            System.out.println("新用户 ID: " + id);
        }
    }
}
```

---

## 七、常见数据库连接 URL 示例

| 数据库 | JDBC URL 示例 |
|--------|---------------|
| MySQL | `jdbc:mysql://localhost:3306/dbname?useSSL=false&serverTimezone=UTC` |
| PostgreSQL | `jdbc:postgresql://localhost:5432/dbname` |
| Oracle | `jdbc:oracle:thin:@localhost:1521:orcl` |
| SQL Server | `jdbc:sqlserver://localhost:1433;databaseName=db;encrypt=false` |
| H2（内存） | `jdbc:h2:mem:testdb` |

---

## 八、最佳实践

1. **使用 try-with-resources** 自动管理资源
2. **始终使用 PreparedStatement** 防止 SQL 注入
3. **合理使用连接池**（如 HikariCP、Druid）避免频繁创建连接
4. **及时关闭 ResultSet、Statement、Connection**
5. **异常处理要完整**，必要时记录日志
6. **避免在循环中创建 PreparedStatement**

---

## 九、简单完整示例（MySQL）

```java
import java.sql.*;

public class JdbcExample {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false&serverTimezone=UTC";
        String user = "root";
        String password = "123456";

        String sql = "SELECT id, name FROM users WHERE id > ?";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, 0);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    System.out.println(rs.getInt("id") + " - " + rs.getString("name"));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

> **依赖**（Maven）：
> ```xml
> <dependency>
>     <groupId>mysql</groupId>
>     <artifactId>mysql-connector-java</artifactId>
>     <version>8.0.33</version>
> </dependency>
> ```

---

## 十、后续演进

虽然 JDBC 是基础，但在实际开发中通常使用更高层的框架：

- **MyBatis**：SQL 与代码分离，灵活
- **Hibernate / JPA**：ORM（对象关系映射），面向对象操作
- **Spring JDBC Template**：简化 JDBC 操作，自动资源管理

但理解 JDBC 原理对排查问题、优化性能至关重要。

---

如需进一步了解连接池、事务隔离级别、元数据（DatabaseMetaData）等内容，可继续提问！