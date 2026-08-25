<!--
module:
  parent: spring/mybatis/01-architecture
  slug: spring/mybatis/01-architecture/06-result-mapping
  type: topic
  category: MyBatis 内部原理
  summary: 一对一 association / 一对多 collection 关联映射的配置与用法
-->

# 06 Result Mapping 结果映射

> 来源:整合自原 08.mybatis/README.md § 四.4.2
>
> 🎯 一句话定位：resultMap 解决数据库列名与 Java 属性名不匹配，以及一对一 association / 一对多 collection 的关联映射。

### 4.2 关联映射
#### 4.2.1 一对一关联
```xml
<!-- 用户与详细信息 -->
<resultMap id="userWithDetail" type="User">
    <id property="id" column="user_id"/>
    <association property="detail" javaType="UserDetail">
        <id property="id" column="detail_id"/>
        <result property="address" column="address"/>
    </association>
</resultMap>
```

#### 4.2.2 一对多关联
```xml
<!-- 用户与订单 -->
<resultMap id="userWithOrders" type="User">
    <id property="id" column="user_id"/>
    <collection property="orders" ofType="Order">
        <id property="id" column="order_id"/>
        <result property="amount" column="amount"/>
    </collection>
</resultMap>
```
---

## 系列导航

- 上一篇：[`05 动态 SQL`](05-dynamic-sql.md) — BoundSql 生成的上游规则
- 下一篇：[`07 缓存机制`](07-cache-mechanism.md) — 一级 / 二级缓存与结果映射的关系

← [返回: 01-architecture](README.md)
