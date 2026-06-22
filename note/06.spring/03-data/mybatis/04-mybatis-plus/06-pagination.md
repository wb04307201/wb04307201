# 06 分页插件

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L164-194(§三.4 分页插件)

## 6.1 配置分页插件

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

## 6.2 使用分页

```java
// 查询第1页,每页10条
Page<User> page = new Page<>(1, 10);
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("age", 25);
Page<User> userPage = userMapper.selectPage(page, wrapper);

// 获取分页数据
List<User> records = userPage.getRecords();  // 当前页数据
long total = userPage.getTotal();           // 总记录数
long pages = userPage.getPages();           // 总页数
```
