# 03 数据库厂商扩展(DatabaseIdProvider)

> 来源:整合自原 08.mybatis/README.md § 七.7.3

## 7.3 数据库厂商扩展

```xml
<databaseIdProvider type="DB_VENDOR">
    <property name="MySQL" value="mysql"/>
    <property name="Oracle" value="oracle"/>
</databaseIdProvider>
```

**使用方式**:

```xml
<select id="selectUser" resultType="User" databaseId="mysql">
    SELECT * FROM user WHERE id = #{id}
</select>
```