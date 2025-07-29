# MyBatis-Plus

## 一、MyBatis-Plus 简介

MyBatis-Plus（简称 MP）是 MyBatis 的增强工具，在 MyBatis 的基础上只做增强不做改变，为简化开发、提高效率而生。它提供了强大的 CRud 操作、分页插件、条件构造器、自动填充等功能，极大减少了开发者的编码工作量。

### 核心特性
- **无侵入**：只做增强不做改变，引入 MP 不会对现有工程产生影响
- **强大的 CRUD 操作**：内置通用 Mapper、通用 Service，少量配置即可实现单表大部分 CRUD 操作
- **Lambda 条件构造器**：支持类型安全的 SQL 条件构造
- **分页插件**：内置分页插件，简单配置即可实现分页功能
- **性能分析**：内置性能分析插件，可输出 SQL 执行日志
- **全局拦截功能**：提供全局拦截功能
- **自动填充**：支持字段自动填充功能（如创建时间、更新时间等）

## 二、快速入门

### 1. 添加依赖

```xml
<!-- MyBatis-Plus 核心依赖 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>最新版本</version>
</dependency>
```

### 2. 配置数据源

在 `application.yml` 中配置：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/your_db?useSSL=false&serverTimezone=UTC
    username: your_username
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver
```

### 3. 实体类示例

```java
@Data
@TableName("user") // 对应数据库表名
public class User {
    @TableId(type = IdType.AUTO) // 主键自增
    private Long id;
    private String name;
    private Integer age;
    private String email;
    
    @TableField(fill = FieldFill.INSERT) // 插入时自动填充
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE) // 插入和更新时自动填充
    private LocalDateTime updateTime;
}
```

### 4. Mapper 接口

```java
public interface UserMapper extends BaseMapper<User> {
    // 继承BaseMapper后，基本CRUD方法已具备
}
```

### 5. 启动类添加注解

```java
@SpringBootApplication
@MapperScan("com.example.mapper") // 扫描Mapper接口
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

## 三、核心功能

### 1. CRUD 操作

**插入数据**：
```java
User user = new User();
user.setName("Tom");
user.setAge(25);
userMapper.insert(user); // 返回插入的记录数
```

**更新数据**：
```java
User user = new User();
user.setId(1L);
user.setName("Jerry");
userMapper.updateById(user); // 根据ID更新
```

**查询数据**：
```java
// 根据ID查询
User user = userMapper.selectById(1L);

// 查询所有
List<User> users = userMapper.selectList(null);

// 条件查询
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("name", "Tom").gt("age", 20);
List<User> users = userMapper.selectList(wrapper);
```

**删除数据**：
```java
// 根据ID删除
userMapper.deleteById(1L);

// 条件删除
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("name", "Tom");
userMapper.delete(wrapper);
```

### 2. 条件构造器

MyBatis-Plus 提供了两种条件构造器：
- `QueryWrapper`：用于查询条件构造
- `UpdateWrapper`：用于更新条件构造

**常用方法**：
```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("column", value)       // 等于 =
      .ne("column", value)       // 不等于 <>
      .gt("column", value)       // 大于 >
      .ge("column", value)       // 大于等于 >=
      .lt("column", value)       // 小于 <
      .le("column", value)       // 小于等于 <=
      .between("column", v1, v2) // BETWEEN 值1 AND 值2
      .like("column", value)     // LIKE '%值%'
      .likeLeft("column", value) // LIKE '%值'
      .likeRight("column", value)// LIKE '值%'
      .in("column", list)       // IN (value.get(0),value.get(1),...)
      .isNull("column")         // 字段 IS NULL
      .isNotNull("column")      // 字段 IS NOT NULL
      .orderByAsc("column")      // 排序：ORDER BY 字段,... ASC
      .orderByDesc("column")     // 排序：ORDER BY 字段,... DESC
```

### 3. Lambda 条件构造器

使用 Lambda 表达式可以避免字段名硬编码：

```java
LambdaQueryWrapper<User> lambdaWrapper = new LambdaQueryWrapper<>();
lambdaWrapper.eq(User::getName, "Tom")
             .gt(User::getAge, 20);
List<User> users = userMapper.selectList(lambdaWrapper);
```

### 4. 分页插件

**配置分页插件**：

```java
@Configuration
public class MybatisPlusConfig {
    
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}
```

**使用分页**：

```java
// 查询第1页，每页10条
Page<User> page = new Page<>(1, 10);
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("age", 25);
Page<User> userPage = userMapper.selectPage(page, wrapper);

// 获取分页数据
List<User> records = userPage.getRecords();  // 当前页数据
long total = userPage.getTotal();           // 总记录数
long pages = userPage.getPages();           // 总页数
```

### 5. 自动填充功能

**创建 MetaObjectHandler 实现类**：

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

### 6. 逻辑删除

**配置逻辑删除**：

```java
@Data
@TableName("user")
public class User {
    // 其他字段...
    
    @TableLogic // 逻辑删除注解
    private Integer deleted; // 0-未删除 1-已删除
}
```

**配置逻辑删除值**：

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted  # 全局逻辑删除的实体字段名
      logic-not-delete-value: 0    # 逻辑未删除值(默认为 0)
      logic-delete-value: 1        # 逻辑已删除值(默认为 1)
```

## 四、高级特性

### 1. 动态表名

实现 `TableNameHandler` 接口可以实现动态表名：

```java
@Component
public class DynamicTableNameHandler implements TableNameHandler {
    
    @Override
    public String dynamicTableName(String sql, String tableName) {
        // 根据业务逻辑返回动态表名
        return "user_" + System.currentTimeMillis() % 2; // 示例：轮询表
    }
}
```

然后在配置类中注入：

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    DynamicTableNameInnerInterceptor dynamicTableNameInnerInterceptor = new DynamicTableNameInnerInterceptor();
    dynamicTableNameInnerInterceptor.setTableNameHandler(dynamicTableNameHandler);
    interceptor.addInnerInterceptor(dynamicTableNameInnerInterceptor);
    return interceptor;
}
```

### 2. 性能分析插件

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    // 性能分析插件
    interceptor.addInnerInterceptor(new PerformanceInterceptor(
        new FormatStyle[]{FormatStyle.MSG}, // 输出格式
        1000, // 慢SQL阈值(毫秒)
        10, // 最大SQL数量
        true, // 是否打印SQL参数
        true  // 是否打印SQL解析
    ));
    return interceptor;
}
```

### 3. SQL 注入器

自定义 SQL 方法：

```java
public class MySqlInjector extends DefaultSqlInjector {
    
    @Override
    public List<AbstractMethod> getMethodList(Class<?> mapperClass) {
        List<AbstractMethod> methodList = super.getMethodList(mapperClass);
        methodList.add(new FindAll()); // 添加自定义方法
        return methodList;
    }
}
```

然后注册注入器：

```java
@Bean
public MySqlInjector mySqlInjector() {
    return new MySqlInjector();
}
```

## 五、常见问题

### 1. 主键生成策略

MyBatis-Plus 支持多种主键生成策略：

```java
public enum IdType {
    AUTO(0),       // 数据库ID自增
    NONE(1),       // 未设置主键
    INPUT(2),      // 手动输入
    ASSIGN_ID(3),  // 分配ID(默认实现类为DefaultIdentifierGenerator雪花算法)
    ASSIGN_UUID(4); // 分配UUID
    
    // ...
}
```

在实体类主键字段上使用：

```java
@TableId(type = IdType.AUTO) // 或其他策略
private Long id;
```

### 2. 多租户实现

MyBatis-Plus 支持多租户场景，可以通过拦截器实现：

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    // 多租户拦截器
    TenantLineInnerInterceptor tenantLineInnerInterceptor = new TenantLineInnerInterceptor();
    tenantLineInnerInterceptor.setTenantLineHandler(new TenantLineHandler() {
        @Override
        public Expression getTenantId() {
            // 返回当前租户ID
            return new LongValue(1L);
        }

        @Override
        public String getTenantIdColumn() {
            // 返回租户字段名
            return "tenant_id";
        }

        @Override
        public boolean ignoreTable(String tableName) {
            // 哪些表不需要过滤
            return false;
        }
    });
    interceptor.addInnerInterceptor(tenantLineInnerInterceptor);
    return interceptor;
}
```

### 3. 乐观锁实现

**实体类添加注解**：

```java
@Data
@TableName("user")
public class User {
    // 其他字段...
    
    @Version // 乐观锁注解
    private Integer version;
}
```

**配置乐观锁插件**：

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
    return interceptor;
}
```

## 六、最佳实践

1. **合理使用 Wrapper**：简单查询可以使用 Wrapper，复杂查询建议使用 XML 或注解方式
2. **避免 N+1 问题**：多表关联查询时注意性能，考虑使用一次性查询
3. **合理分页**：大数据量分页时考虑使用游标分页
4. **字段命名一致性**：保持数据库字段、实体类字段、JSON 字段命名一致
5. **使用 Lambda 表达式**：减少字段名硬编码，提高代码可维护性
6. **合理使用缓存**：对于不常变的数据考虑使用二级缓存

## 七、总结

MyBatis-Plus 是一个功能强大的 MyBatis 增强工具，通过提供丰富的内置功能和简洁的 API，显著提高了开发效率。掌握其核心功能后，可以大大减少样板代码的编写，让开发者更专注于业务逻辑的实现。

**推荐学习资源**：
- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [MyBatis-Plus GitHub](https://github.com/baomidou/mybatis-plus)
- [MyBatis-Plus 示例项目](https://github.com/baomidou/mybatis-plus-samples)

希望这篇笔记能帮助你快速掌握 MyBatis-Plus 的核心用法！