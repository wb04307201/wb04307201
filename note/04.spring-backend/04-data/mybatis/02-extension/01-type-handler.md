<!--
module:
  parent: spring/mybatis/02-extension
  slug: spring/mybatis/02-extension/01-type-handler
  type: article
  category: MyBatis 内部原理
  summary: TypeHandler 是 MyBatis 在 Java 类型与 JDBC 类型之间的双向转换桥
-->

# 01 自定义类型处理器(TypeHandler)

> 来源:整合自原 08.mybatis/README.md § 七.7.1
>
> 🎯 一句话定位：TypeHandler 是 MyBatis 在 Java 类型与 JDBC 类型之间的双向转换桥。

## §1 内置与自定义

> ❌ **不注册直接用 `java.util.Date`**：MyBatis 默认把 `Date` 当 `TIMESTAMP` 处理，但若数据库列类型为 `DATE`/`TIME`，取值时精度丢失（时分秒截断）甚至报 `TypeException`。
> ✅ **注册自定义 `DateTypeHandler`**：明确指定 `javaType` + `jdbcType` 映射，保证双向转换精度。

```java
// BaseTypeHandler 4 个核心方法职责：
// 1. setNonNullParameter  — 写参数到 PreparedStatement（Java → JDBC）
// 2. getNullableResult(rs, columnName) — 按列名读结果（JDBC → Java）
// 3. getNullableResult(rs, columnIndex) — 按列索引读结果（JDBC → Java）
// 4. getNullableResult(cs, columnIndex) — 从 CallableStatement 读 OUT 参数（存储过程场景）
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

**Spring Boot 注册方式**（替代 XML 手工配置）：

```yaml
mybatis:
  type-handlers-package: com.example.handler
```

> 通过 `@Configuration` + `mybatis.type-handlers-package` 可扫描整个包自动注册，无需逐条声明。
---

## 系列导航

- 下一篇：[`02 拦截器`](02-interceptor.md) — 插件机制与四大拦截点

← [返回: 02-extension](README.md)
