# 08 高级特性(动态表名 / 性能分析 / SQL 注入器)

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L243-315(§四 高级特性)

## 8.1 动态表名

实现 `TableNameHandler` 接口可以实现动态表名:

```java
@Component
public class DynamicTableNameHandler implements TableNameHandler {

    @Override
    public String dynamicTableName(String sql, String tableName) {
        // 根据业务逻辑返回动态表名
        return "user_" + System.currentTimeMillis() % 2; // 示例:轮询表
    }
}
```

然后在配置类中注入:

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

## 8.2 性能分析插件

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

## 8.3 SQL 注入器

自定义 SQL 方法:

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

然后注册注入器:

```java
@Bean
public MySqlInjector mySqlInjector() {
    return new MySqlInjector();
}
```
