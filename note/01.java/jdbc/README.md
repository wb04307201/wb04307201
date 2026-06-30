# JDBC

JDBC（Java Database Connectivity）是 Java 标准中用于执行 SQL 语句的 API，定义在 `java.sql` 和 `javax.sql` 包中。它为多种关系型数据库提供统一的访问接口，是所有 Java 数据库操作技术的底层基础。

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

JDBC 本应该很简单，JDBC（Java Database Connectivity）是 Java 标准中用于执行 SQL 语句的 API，定义在 `java.sql` 和 `javax.sql` 包中。它为多种关系型数据库提供统一的访问接口，是所有 Java

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



## 一、JDBC 架构

```
应用层 → JDBC API (java.sql / javax.sql)
            ↓
        JDBC Driver Manager
            ↓
    ┌───────┼───────┬──────────┐
  Type 4   Type 4  Type 4   Type 4
 (MySQL) (Oracle) (PG)    (SQL Server)
    ↓       ↓       ↓         ↓
  MySQL   Oracle  PostgreSQL  SQL Server
```

JDBC 驱动分为四种类型，但现代开发中**几乎只使用 Type 4（纯 Java 驱动，直接通过网络与数据库通信）**，其余类型（Type 1 JDBC-ODBC 桥、Type 2 本地 API、Type 3 网络协议）已被淘汰。

---

## 二、核心接口与类

| 组件 | 包 | 说明 |
|------|-----|------|
| `DriverManager` | `java.sql` | 管理驱动注册，获取连接（传统方式） |
| `DataSource` | `javax.sql` | 获取连接的**推荐方式**，支持连接池和 JNDI |
| `Connection` | `java.sql` | 数据库连接（会话） |
| `Statement` | `java.sql` | 执行静态 SQL |
| `PreparedStatement` | `java.sql` | 执行预编译参数化 SQL |
| `CallableStatement` | `java.sql` | 执行存储过程 |
| `ResultSet` | `java.sql` | 查询结果集 |
| `SQLException` | `java.sql` | SQL 异常（支持链式） |

---

## 三、获取数据库连接

### 3.1 DriverManager（传统方式）

```java
String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false&serverTimezone=Asia/Shanghai";
Connection conn = DriverManager.getConnection(url, "root", "123456");
```

**URL 通用格式：** `jdbc:<subprotocol>:<subname>`

| 数据库 | Driver Class | JDBC URL |
|--------|-------------|----------|
| MySQL 8+ | `com.mysql.cj.jdbc.Driver` | `jdbc:mysql://host:port/db?useSSL=false&serverTimezone=Asia/Shanghai` |
| PostgreSQL | `org.postgresql.Driver` | `jdbc:postgresql://host:port/db` |
| Oracle | `oracle.jdbc.OracleDriver` | `jdbc:oracle:thin:@host:1521:sid` |
| SQL Server | `com.microsoft.sqlserver.jdbc.SQLServerDriver` | `jdbc:sqlserver://host:1433;databaseName=db` |
| H2（内存） | `org.h2.Driver` | `jdbc:h2:mem:testdb` |

> **JDBC 4.0+ (Java 6+)** 不再需要 `Class.forName()` 手动加载驱动，JVM 通过 `META-INF/services/java.sql.Driver` 自动发现并注册驱动。

### 3.2 DataSource（推荐方式）

`DataSource` 是 JDBC 2.0 引入的获取连接的标准方式，取代 `DriverManager`：

```java
// MySQL 提供的 DataSource 实现
MysqlDataSource ds = new MysqlDataSource();
ds.setURL("jdbc:mysql://localhost:3306/testdb");
ds.setUser("root");
ds.setPassword("123456");
ds.setServerTimezone("Asia/Shanghai");

Connection conn = ds.getConnection();
```

**为什么 DataSource 更好？**
- 可被连接池实现（HikariCP、Druid）透明替换
- 支持 JNDI 查找
- 可配置连接属性（而非拼接 URL 字符串）
- 是 Java EE / Spring 生态的标准

### 3.3 连接池（工程必备）

每次创建 Connection 都需要 TCP 三次握手 + 数据库认证，耗时 20~100ms。**连接池**预先创建一批连接复用，将获取连接降低到微秒级。

**HikariCP（业界标准，Spring Boot 默认）：**

```xml
<dependency>
    <groupId>com.zaxxer</groupId>
    <artifactId>HikariCP</artifactId>
    <version>5.1.0</version>
</dependency>
```

```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:mysql://localhost:3306/testdb");
config.setUsername("root");
config.setPassword("123456");
config.setMaximumPoolSize(10);        // 最大连接数
config.setMinimumIdle(2);             // 最小空闲连接
config.setIdleTimeout(600_000);       // 空闲超时 10 分钟
config.setMaxLifetime(1_800_000);     // 连接最大存活 30 分钟
config.setConnectionTimeout(30_000);  // 获取连接超时 30 秒

HikariDataSource ds = new HikariDataSource(config);
// 使用 ds.getConnection() 获取连接
// 应用关闭时调用 ds.close() 释放所有连接
```

---

## 四、资源管理

### 4.1 try-with-resources（Java 7+，唯一推荐写法）

JDBC 资源必须按**后开先关**顺序关闭（ResultSet → Statement → Connection），try-with-resources 自动处理：

```java
String sql = "SELECT id, name FROM users WHERE id > ?";

try (Connection conn = ds.getConnection();
     PreparedStatement pstmt = conn.prepareStatement(sql)) {

    pstmt.setInt(1, 0);
    try (ResultSet rs = pstmt.executeQuery()) {
        while (rs.next()) {
            System.out.println(rs.getInt("id") + " - " + rs.getString("name"));
        }
    }
} catch (SQLException e) {
    // 处理异常
}
// 离开 try 块时，rs → pstmt → conn 按顺序自动关闭
```

### 4.2 SQLException 链式处理

一个 SQLException 可能包含多个由数据库返回的异常链：

```java
catch (SQLException e) {
    System.err.println("SQLState: " + e.getSQLState());
    System.err.println("Error Code: " + e.getErrorCode());
    System.err.println("Message: " + e.getMessage());

    // 遍历链式异常
    SQLException next = e.getNextException();
    while (next != null) {
        System.err.println(" chained → " + next.getMessage());
        next = next.getNextException();
    }
}
```

---

## 五、执行 SQL

### 5.1 Statement 三种执行方法

| 方法 | 用途 | 返回值 |
|------|------|--------|
| `executeQuery(sql)` | SELECT 查询 | `ResultSet` |
| `executeUpdate(sql)` | INSERT / UPDATE / DELETE / DDL | `int`（受影响行数） |
| `execute(sql)` | 任意 SQL（未知类型时） | `boolean`（true 有 ResultSet） |

### 5.2 PreparedStatement（始终首选）

```java
String sql = "INSERT INTO users(name, email, age) VALUES (?, ?, ?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    pstmt.setString(1, "张三");
    pstmt.setString(2, "zhangsan@example.com");
    pstmt.setInt(3, 28);
    int rows = pstmt.executeUpdate();
}
```

**PreparedStatement 优势：**
- 预编译 SQL，多次执行性能更好
- 参数化查询，彻底杜绝 SQL 注入
- 支持流式设置大对象（setBlob / setClob）
- 类型安全，驱动自动处理类型转换

**参数设置方法速查：**

| 方法 | 对应 SQL 类型 |
|------|--------------|
| `setInt(index, value)` | INT |
| `setLong(index, value)` | BIGINT |
| `setString(index, value)` | VARCHAR |
| `setDouble(index, value)` | DOUBLE |
| `setBoolean(index, value)` | BOOLEAN |
| `setDate(index, java.sql.Date)` | DATE |
| `setTimestamp(index, java.sql.Timestamp)` | TIMESTAMP |
| `setObject(index, value)` | 任意类型（JDBC 4.0+ 自动推断） |
| `setNull(index, Types.VARCHAR)` | NULL 值 |

### 5.3 CallableStatement（调用存储过程）

```java
String sql = "{call get_user_by_id(?, ?)}"; // ? = IN, ? = OUT
try (CallableStatement cstmt = conn.prepareCall(sql)) {
    cstmt.setInt(1, 1001);                        // IN 参数
    cstmt.registerOutParameter(2, Types.VARCHAR); // 注册 OUT 参数
    cstmt.execute();
    String name = cstmt.getString(2);             // 读取 OUT 参数
}
```

### 5.4 批处理（批量插入 / 更新）

当需要执行大量相同结构的 SQL 时，使用批处理显著减少网络往返：

```java
String sql = "INSERT INTO users(name, email) VALUES (?, ?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    for (User user : users) {
        pstmt.setString(1, user.getName());
        pstmt.setString(2, user.getEmail());
        pstmt.addBatch();

        // 每 500 条执行一次，避免单次批处理过大
        if (count % 500 == 0) {
            pstmt.executeBatch();
            pstmt.clearBatch();
        }
    }
    // 执行剩余
    pstmt.executeBatch();
}
```

---

## 六、ResultSet 详解

### 6.1 基本遍历

```java
try (ResultSet rs = pstmt.executeQuery()) {
    while (rs.next()) {
        int id    = rs.getInt("id");
        String nm = rs.getString("name");
        // 注意：基本类型 getInt 在数据库 NULL 时返回 0，需用 wasNull() 判断
        if (rs.wasNull()) {
            // 处理 NULL
        }
    }
}
```

### 6.2 可滚动 / 可更新 ResultSet

默认 ResultSet 只能向前遍历、只读。如需反向遍历或修改数据：

```java
// 创建可滚动、可更新的 ResultSet
Statement stmt = conn.createStatement(
    ResultSet.TYPE_SCROLL_INSENSITIVE,  // 可滚动，不反映其他事务的修改
    ResultSet.CONCUR_UPDATABLE          // 可更新
);
ResultSet rs = stmt.executeQuery("SELECT id, name FROM users");

rs.absolute(5);     // 跳到第 5 行
rs.previous();      // 向前一行
rs.updateString("name", "新名字");
rs.updateRow();     // 写回数据库
```

> 实际开发中很少直接使用可更新 ResultSet，通常通过 UPDATE 语句修改数据更清晰。

### 6.3 ResultSetMetaData（动态获取列信息）

```java
try (ResultSet rs = pstmt.executeQuery()) {
    ResultSetMetaData meta = rs.getMetaData();
    int columnCount = meta.getColumnCount();

    // 打印所有列名
    for (int i = 1; i <= columnCount; i++) {
        System.out.printf("列 %d: %s (%s)%n",
            i,
            meta.getColumnName(i),
            meta.getColumnTypeName(i));
    }
}
```

---

## 七、事务管理

### 7.1 基本事务控制

JDBC 默认 auto-commit 模式（每条 SQL 自动提交），需要手动控制事务时关闭它：

```java
conn.setAutoCommit(false);
try {
    pstmt1.executeUpdate();
    pstmt2.executeUpdate();
    conn.commit();          // 全部成功才提交
} catch (SQLException e) {
    conn.rollback();        // 任一失败，全部回滚
    throw e;
} finally {
    conn.setAutoCommit(true); // 恢复默认行为
}
```

### 7.2 Savepoint（部分回滚）

在长事务中设置保存点，可以只回滚部分操作：

```java
conn.setAutoCommit(false);
Savepoint sp = null;
try {
    pstmt1.executeUpdate();       // 操作 A
    sp = conn.setSavepoint("after_A");
    pstmt2.executeUpdate();       // 操作 B

    conn.commit();
} catch (SQLException e) {
    if (sp != null) {
        conn.rollback(sp);         // 回滚到保存点，操作 A 仍有效
    } else {
        conn.rollback();
    }
}
```

### 7.3 事务隔离级别

| 隔离级别 | 常量 | 脏读 | 不可重复读 | 幻读 |
|---------|------|------|-----------|------|
| 读未提交 | `READ_UNCOMMITTED` | ✅ | ✅ | ✅ |
| 读已提交 | `READ_COMMITTED` | ❌ | ✅ | ✅ |
| 可重复读 | `REPEATABLE_READ` | ❌ | ❌ | ✅(InnoDB 已避免) |
| 串行化 | `SERIALIZABLE` | ❌ | ❌ | ❌ |

```java
// 设置隔离级别（必须在获取连接后、执行 SQL 前设置）
conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
```

> MySQL InnoDB 默认 `REPEATABLE_READ`，PostgreSQL 默认 `READ_COMMITTED`。
> 多数场景使用 `READ_COMMITTED` 即可，在性能和一致性间取得平衡。

---

## 八、大对象处理

### 8.1 CLOB（大文本）

```java
// 写入
String sql = "INSERT INTO articles(title, content) VALUES (?, ?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    pstmt.setString(1, "文章标题");
    StringReader reader = new StringReader(largeTextContent);
    pstmt.setCharacterStream(2, reader, largeTextContent.length());
    pstmt.executeUpdate();
}

// 读取
try (ResultSet rs = pstmt.executeQuery()) {
    if (rs.next()) {
        try (Reader reader = rs.getCharacterStream("content")) {
            String content = new String(reader.readAllBytes());
        }
    }
}
```

### 8.2 BLOB（二进制数据，如图片、文件）

```java
// 写入
String sql = "INSERT INTO files(name, data) VALUES (?, ?)";
try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
    pstmt.setString(1, "photo.jpg");
    try (InputStream is = Files.newInputStream(Paths.get("photo.jpg"))) {
        pstmt.setBinaryStream(2, is);
        pstmt.executeUpdate();
    }
}

// 读取
try (ResultSet rs = pstmt.executeQuery()) {
    if (rs.next()) {
        try (InputStream is = rs.getBinaryStream("data")) {
            Files.copy(is, Paths.get("downloaded.jpg"));
        }
    }
}
```

---

## 九、DatabaseMetaData（数据库元信息）

```java
DatabaseMetaData meta = conn.getMetaData();
System.out.println("数据库: " + meta.getDatabaseProductName());
System.out.println("版本: " + meta.getDatabaseProductVersion());
System.out.println("驱动: " + meta.getDriverName());
System.out.println("JDBC 版本: " + meta.getJDBCMajorVersion());

// 获取表列表
try (ResultSet tables = meta.getTables(null, null, "%", new String[]{"TABLE"})) {
    while (tables.next()) {
        System.out.println(tables.getString("TABLE_NAME"));
    }
}

// 获取主键信息
try (ResultSet keys = meta.getPrimaryKeys(null, null, "users")) {
    while (keys.next()) {
        System.out.println(keys.getString("COLUMN_NAME"));
    }
}
```

---

## 十、RowSet（离线结果集）

`RowSet` 继承自 `ResultSet`，但支持离线操作（断开连接后仍可读取和修改数据）：

```java
// CachedRowSet：将结果缓存到内存，连接可关闭
try (CachedRowSet crs = RowSetProvider.newFactory().createCachedRowSet()) {
    crs.setUrl("jdbc:mysql://localhost:3306/testdb");
    crs.setUsername("root");
    crs.setPassword("123456");
    crs.setCommand("SELECT id, name FROM users");
    crs.execute();  // 执行后连接自动释放

    // 此时已断开连接，仍可遍历
    while (crs.next()) {
        System.out.println(crs.getInt("id") + " - " + crs.getString("name"));
    }

    // 修改数据后写回数据库
    crs.absolute(1);
    crs.updateString("name", "新名字");
    crs.acceptChanges();  // 重新连接并写回
}
```

---

## 十一、JDBC 4.x 新特性

### 11.1 自动驱动加载（JDBC 4.0 / Java 6）
不再需要 `Class.forName()`。

### 11.2 增强异常链（JDBC 4.0）
`SQLException` 实现了 `Iterable<Throwable>`，可 foreach 遍历：

```java
catch (SQLException e) {
    for (Throwable t : e) {
        System.err.println(t.getMessage());
    }
}
```

### 11.3 RowId 支持（JDBC 4.0）
```java
RowId rowId = rs.getRowId("ROWID");
```

### 11.4 NCLOB 国家字符集支持（JDBC 4.0）
```java
pstmt.setNClob(1, reader);
rs.getNClob("content");
```

### 11.5 自动资源关闭改进（JDBC 4.1 / Java 7）
try-with-resources 全面支持所有 JDBC 资源。

### 11.6 JDBC 4.3 / Java 9 变化
- `DriverManager.getDrivers()` 返回 `Enumeration<Driver>`
- ShardingSphere 等分布式数据库驱动出现
- Java 9 模块系统：JDBC 驱动需声明 `provides java.sql.Driver with ...`

---

## 十二、完整工程示例

一个包含事务、批处理、连接池的完整示例：

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.sql.*;
import java.util.List;

public class UserDao {

    private final HikariDataSource dataSource;

    public UserDao(HikariDataSource ds) {
        this.dataSource = ds;
    }

    // 查询单个用户
    public User findById(int id) throws SQLException {
        String sql = "SELECT id, name, email, created_at FROM users WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return mapRow(rs);
                }
                return null;
            }
        }
    }

    // 批量插入
    public int[] batchInsert(List<User> users) throws SQLException {
        String sql = "INSERT INTO users(name, email) VALUES (?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            for (User u : users) {
                pstmt.setString(1, u.getName());
                pstmt.setString(2, u.getEmail());
                pstmt.addBatch();
            }
            return pstmt.executeBatch();
        }
    }

    // 带事务的转账操作
    public void transfer(int fromId, int toId, double amount) throws SQLException {
        String debit = "UPDATE accounts SET balance = balance - ? WHERE user_id = ?";
        String credit = "UPDATE accounts SET balance = balance + ? WHERE user_id = ?";

        try (Connection conn = dataSource.getConnection()) {
            conn.setAutoCommit(false);
            try {
                try (PreparedStatement ps1 = conn.prepareStatement(debit);
                     PreparedStatement ps2 = conn.prepareStatement(credit)) {

                    ps1.setDouble(1, amount);
                    ps1.setInt(2, fromId);
                    ps1.executeUpdate();

                    ps2.setDouble(1, amount);
                    ps2.setInt(2, toId);
                    ps2.executeUpdate();
                }
                conn.commit();
            } catch (SQLException e) {
                conn.rollback();
                throw e;
            }
        }
    }

    private User mapRow(ResultSet rs) throws SQLException {
        User u = new User();
        u.setId(rs.getInt("id"));
        u.setName(rs.getString("name"));
        u.setEmail(rs.getString("email"));
        u.setCreatedAt(rs.getTimestamp("created_at"));
        return u;
    }
}
```

---

## 十三、最佳实践总结

1. **永远使用 `PreparedStatement`**，不要拼接 SQL 字符串
2. **永远使用 try-with-resources** 自动关闭资源
3. **永远使用连接池**（HikariCP），不要直接用 DriverManager
4. 合理设置连接池参数：`maxPoolSize` 通常 CPU 核心数 × 2 + 磁盘数
5. **及时关闭** ResultSet 和 Statement，不要等到 Connection 关闭时才关
6. SQL 异常要**记录 SQLState、ErrorCode 和完整消息**，便于排查
7. 事务范围尽量小，**不要在事务中做网络请求或耗时计算**
8. **避免在循环中执行 SQL**，改用批处理
9. `ResultSet` 默认只向前只读，不要滥用 `TYPE_SCROLL_INSENSITIVE`
10. 数据库 URL 中的参数（时区、字符集、SSL）要明确指定，不要依赖默认值

---

## 十四、JDBC 在技术栈中的位置

```
用户代码
    ↓
┌─────────────────────────────────┐
│  ORM 框架（Hibernate / JPA）     │  对象映射
│  MyBatis / MyBatis-Plus         │  SQL 映射
│  Spring JdbcTemplate            │  模板简化
│  jOOQ                           │  类型安全 SQL
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│         JDBC API                │  ← 你正在学习这一层
│   java.sql / javax.sql          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│    JDBC Driver (MySQL 等)       │  各厂商实现
└─────────────────────────────────┘
    ↓
       数据库（MySQL / PostgreSQL）
```

所有上层框架最终都调用 JDBC。理解 JDBC 对排查性能问题、理解框架行为、编写高效数据访问代码至关重要。
