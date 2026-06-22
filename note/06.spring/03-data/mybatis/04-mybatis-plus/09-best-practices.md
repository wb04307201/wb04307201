# 09 最佳实践与踩坑

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L317-419(§五 常见问题 + §六 最佳实践 + §七 总结)

## 9.1 常见问题

### 9.1.1 主键生成策略

MyBatis-Plus 支持多种主键生成策略:

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

在实体类主键字段上使用:

```java
@TableId(type = IdType.AUTO) // 或其他策略
private Long id;
```

### 9.1.2 多租户实现

MyBatis-Plus 支持多租户场景,可以通过拦截器实现:

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

### 9.1.3 乐观锁实现

**实体类添加注解**:

```java
@Data
@TableName("user")
public class User {
    // 其他字段...

    @Version // 乐观锁注解
    private Integer version;
}
```

**配置乐观锁插件**:

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
    return interceptor;
}
```

## 9.2 最佳实践

1. **合理使用 Wrapper**:简单查询可以使用 Wrapper,复杂查询建议使用 XML 或注解方式
2. **避免 N+1 问题**:多表关联查询时注意性能,考虑使用一次性查询
3. **合理分页**:大数据量分页时考虑使用游标分页
4. **字段命名一致性**:保持数据库字段、实体类字段、JSON 字段命名一致
5. **使用 Lambda 表达式**:减少字段名硬编码,提高代码可维护性
6. **合理使用缓存**:对于不常变的数据考虑使用二级缓存

## 9.3 推荐学习资源

MyBatis-Plus 是一个功能强大的 MyBatis 增强工具,通过提供丰富的内置功能和简洁的 API,显著提高了开发效率。掌握其核心功能后,可以大大减少样板代码的编写,让开发者更专注于业务逻辑的实现。

- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [MyBatis-Plus GitHub](https://github.com/baomidou/mybatis-plus)
- [MyBatis-Plus 示例项目](https://github.com/baomidou/mybatis-plus-samples)
