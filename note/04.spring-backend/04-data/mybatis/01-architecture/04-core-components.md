<!--
module:
  parent: spring/mybatis/01-architecture
  slug: spring/mybatis/01-architecture/04-core-components
  type: topic
  category: MyBatis 内部原理
  summary: 详解 SqlSessionFactory / MappedStatement / Executor 三大核心组件及三种执行器类型
-->

# 04 核心组件

> **一句话定位**：MyBatis 四大核心组件（SqlSessionFactory / SqlSession / MappedStatement / Executor）的职责划分与三种执行器类型选型。

> 来源:整合自原 08.mybatis/README.md § 三 + § 五.5.3 + § 九(已去重)

## SqlSessionFactory / MappedStatement
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

## Executor 类型详谈
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

| 执行器 | 适用场景 | 调优提示 |
|--------|---------|---------|
| SIMPLE | 单次查询为主的简单应用 | 默认值，无需额外配置 |
| REUSE | 同一 SqlSession 内重复执行相同 SQL | Statement 缓存按 SQL 文本匹配，参数不同也复用 |
| BATCH | 批量 INSERT/UPDATE（如数据迁移） | 必须手动 `flushStatements()` 才真正执行，注意内存占用 |

> 💡 性能实测建议：批量插入 1000 条时，BATCH 比 SIMPLE 快 5-10 倍（减少网络往返）。

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

## 调试技巧
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

## 反向链

- [03-execution-flow](03-execution-flow.md) — SQL 执行全流程
- [07-cache-mechanism](07-cache-mechanism.md) — 一级/二级缓存机制
- [08-class-diagram](08-class-diagram.md) — 架构全景类图

---

← [返回: MyBatis 架构与原理](README.md)
