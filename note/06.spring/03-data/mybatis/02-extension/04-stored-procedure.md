# 04 存储过程调用

> 来源:整合自原 08.mybatis/README.md § 八

## 8.1 基本调用方式

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

## 8.2 参数模式说明

| 模式 | 说明 | 示例 |
|------|------|------|
| IN | 输入参数 | `#{param,mode=IN}` |
| OUT | 输出参数 | `#{param,mode=OUT}` |
| INOUT | 输入输出参数 | `#{param,mode=INOUT}` |

## 8.3 复杂存储过程处理

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
```

## 8.4 Java代码调用示例

```java
// 无返回值调用
SqlSession sqlSession = sqlSessionFactory.openSession();
try {
    sqlSession.selectOne("com.example.UserMapper.callProcedure",
        Map.of("userId", 1, "status", "ACTIVE"));
} finally {
    sqlSession.close();
}

// 带输出参数调用
Map<String, Object> params = new HashMap<>();
params.put("result", null); // 初始化OUT参数
sqlSession.selectOne("com.example.UserMapper.callFunction", params);
Integer count = (Integer) params.get("result");
```