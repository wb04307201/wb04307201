<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\02-extension\04-stored-procedure
  type: article
  category: 主模块子文章
  summary: statementType=CALLABLE 让 MyBatis 透明调用数据库存储过程，支持 IN/OUT/INOUT 三种参数模式与游标映射
  depth: ⭐⭐⭐
-->

# 04 存储过程调用

> 来源:整合自原 08.mybatis/README.md § 八
>
> 🎯 一句话定位：statementType=CALLABLE 让 MyBatis 透明调用数据库存储过程，支持 IN/OUT/INOUT 三种参数模式与游标映射。

## 适用场景
- **遗留系统集成**：老项目大量业务逻辑封装在存储过程中，Java 层只需透明调用
- **复杂报表统计**：多表关联 + 聚合计算在数据库端完成，减少网络传输
- **批量数据操作**：利用数据库游标和批处理提升性能

## 基本调用方式
```xml
<!-- 调用无返回值的存储过程 -->
<select id="callProcedure" statementType="CALLABLE">
    {call update_user_status(#{userId,mode=IN,jdbcType=INTEGER},
                           #{status,mode=IN,jdbcType=VARCHAR})}
</select>

<!-- 调用有返回结果的存储过程 -->
<select id="callFunction" statementType="CALLABLE" resultType="int">
    {#{result,mode=OUT,jdbcType=INTEGER} = call get_user_count()}
</select>
```

## 参数模式说明
| 模式 | 说明 | 示例 |
|------|------|------|
| IN | 输入参数 | `#{param,mode=IN}` |
| OUT | 输出参数 | `#{param,mode=OUT}` |
| INOUT | 输入输出参数 | `#{param,mode=INOUT}` |

**常用 jdbcType 枚举**：

| jdbcType | 对应 javaType | 典型场景 |
|----------|--------------|----------|
| `INTEGER` | `Integer` / `Long` | 主键、数量 |
| `VARCHAR` | `String` | 名称、描述 |
| `TIMESTAMP` | `Date` / `LocalDateTime` | 时间字段 |
| `CURSOR` | `ResultSet`（需 javaType=ResultSet） | Oracle 游标返回结果集 |
| `STRUCT` | 自定义对象 | 复杂类型参数 |

> OUT 参数常配合自定义 TypeHandler 处理类型转换，详见 [01-type-handler](01-type-handler.md)。

## 复杂存储过程处理
```xml
<!-- 调用带游标的存储过程 -->
<select id="callCursorProcedure" statementType="CALLABLE" resultMap="userResultMap">
    {call get_users_by_role(
        #{roleId,mode=IN,jdbcType=INTEGER},
        #{userCursor,mode=OUT,jdbcType=CURSOR,javaType=ResultSet,resultMap=userResultMap}
    )}
</select>

<resultMap id="userResultMap" type="User">
    <id property="id" column="id"/>
    <result property="name" column="name"/>
</resultMap>

<!-- 复杂示例：游标返回主从嵌套结构 -->
<resultMap id="orderWithItemsResultMap" type="Order">
    <id property="id" column="order_id"/>
    <result property="userId" column="user_id"/>
    <collection property="items" ofType="OrderItem" column="order_id"
                select="selectOrderItemsByOrderId"/>
</resultMap>
```

## Java代码调用示例
```java
// ❌ 不推荐：finally 块手动关闭（JDK 7+ 已不推荐）
SqlSession sqlSession = sqlSessionFactory.openSession();
try {
    sqlSession.selectOne("com.example.UserMapper.callProcedure",
        Map.of("userId", 1, "status", "ACTIVE"));
} finally {
    sqlSession.close();
}

// ✅ 推荐：try-with-resources 自动关闭
try (SqlSession sqlSession = sqlSessionFactory.openSession()) {
    sqlSession.selectOne("com.example.UserMapper.callProcedure",
        Map.of("userId", 1, "status", "ACTIVE"));
}

// 带输出参数调用
try (SqlSession sqlSession = sqlSessionFactory.openSession()) {
    Map<String, Object> params = new HashMap<>();
    params.put("result", null); // 初始化OUT参数
    sqlSession.selectOne("com.example.UserMapper.callFunction", params);
    Integer count = (Integer) params.get("result");
}
```
---

## 系列导航

- 上一篇：[`03 数据库厂商扩展`](03-database-vendor.md) — 多数据库适配
- 相关主题：[`01 自定义类型处理器`](01-type-handler.md) — OUT 参数常配合自定义 TypeHandler 处理类型转换

← [返回: 02-extension](README.md)
