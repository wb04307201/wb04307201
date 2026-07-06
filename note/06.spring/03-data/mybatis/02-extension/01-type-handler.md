<!--
module:
  parent: spring/mybatis/02-extension
  slug: spring/mybatis/02-extension/01-type-handler
  type: topic
  category: MyBatis 内部原理
  summary: MyBatis 02-extension 章节深度 —— Type Handler
-->

# 01 自定义类型处理器(TypeHandler)

> 来源:整合自原 08.mybatis/README.md § 七.7.1

## 7.1 自定义类型处理器（TypeHandler）

```java
public class DateTypeHandler extends BaseTypeHandler<Date> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, Date parameter, JdbcType jdbcType) throws SQLException {
        ps.setTimestamp(i, new Timestamp(parameter.getTime()));
    }

    @Override
    public Date getNullableResult(ResultSet rs, String columnName) throws SQLException {
        Timestamp timestamp = rs.getTimestamp(columnName);
        return timestamp != null ? new Date(timestamp.getTime()) : null;
    }
    // 其他重载方法...
}
```

**配置方式**:

```xml
<typeHandlers>
    <typeHandler handler="com.example.DateTypeHandler" javaType="java.util.Date"/>
</typeHandlers>
```