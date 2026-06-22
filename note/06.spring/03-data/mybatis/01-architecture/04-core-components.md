# 04 核心组件

> 来源:整合自原 08.mybatis/README.md § 三 + § 五.5.3 + § 九(已去重)

## 4.1 SqlSessionFactory / MappedStatement

> 来源:原 § 三(排除 §3.2 Executor 表格,在 4.2 详谈)

### 3.1 SqlSessionFactory
```java
// 典型创建方式
String resource = "mybatis-config.xml";
InputStream inputStream = Resources.getResourceAsStream(resource);
SqlSessionFactory sqlSessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
```
- **线程安全**：全局单例模式，所有数据库操作共享同一个工厂
- **核心职责**：创建 `SqlSession` 实例，管理事务边界

### 3.3 MappedStatement
```xml
<!-- 示例配置 -->
<select id="selectUser" resultType="User">
    SELECT * FROM user WHERE id = #{id}
</select>
```
- **SQL 封装**：包含 SQL 语句、参数类型、结果映射等元数据
- **ID 唯一性**：由 `namespace.id` 组合构成，如 `com.example.UserMapper.selectUser`

## 4.2 Executor 类型详谈

> 来源:原 § 九(完整保留,Executor 类型表格已在此处统一)

### 1. 执行器概述
Executor 是 MyBatis 的核心执行器，负责 SQL 语句的生成和查询缓存的维护，是 MyBatis 调度的核心，负责 SQL 执行流程中的关键操作。

### 2. 执行器类型
MyBatis 提供三种执行器实现：

- **SimpleExecutor** (默认)
    - 每次执行 update 或 select 都开启一个新 Statement 对象
    - 用完立即关闭
    - 简单但性能较差

- **ReuseExecutor**
    - 执行 update 或 select 时以 SQL 作为 key 查找 Statement 对象
    - 存在则使用，不存在则创建
    - 用完后不关闭，放入缓存
    - 适合批量操作

- **BatchExecutor**
    - 执行 update 时批量操作所有 Statement
    - 需手动调用 `flushStatements()` 提交批量
    - 适合批量更新场景

> 注:原 § 三.3.2 表格与本节"执行器类型"内容重复,已删除。

### 3. 执行器创建流程
```java
// 配置解析阶段创建执行器
Executor executor =
    new ExecutorFactory().createExecutor(transaction, execType);

// execType 来源于配置：
// <settings>
//   <setting name="defaultExecutorType" value="SIMPLE"/>
// </settings>
```

### 4. 执行器核心方法
```java
public interface Executor {
    // 查询操作
    <E> List<E> query(MappedStatement ms, Object parameter,
                     RowBounds rowBounds, ResultHandler handler) throws SQLException;

    // 更新操作
    int update(MappedStatement ms, Object parameter) throws SQLException;

    // 批量操作
    void batch() throws SQLException;

    // 事务相关
    Transaction getTransaction();
    void commit(boolean required) throws SQLException;
    void rollback(boolean required) throws SQLException;

    // 缓存操作
    void clearLocalCache();
    void deferLoad(MappedStatement ms, MetaObject resultObject,
                  String property, CacheKey key, Class<?> targetType);
}
```

### 5. 执行器工作流程
1. 参数处理
2. SQL 构建
3. 结果集映射
4. 缓存处理
5. 事务管理

## 4.3 调试技巧

> 来源:原 § 五.5.3

```java
// 开启 MyBatis 日志
Configuration config = new Configuration();
config.setLogImpl(StdOutImpl.class); // 输出 SQL 到控制台

// SQL 执行时间监控
long start = System.currentTimeMillis();
List<User> users = sqlSession.selectList("com.example.UserMapper.findAll");
long duration = System.currentTimeMillis() - start;
System.out.println("SQL 执行耗时: " + duration + "ms");
```