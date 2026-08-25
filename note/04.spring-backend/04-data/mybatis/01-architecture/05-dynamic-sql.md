<!--
module:
  parent: spring/mybatis/01-architecture
  slug: spring/mybatis/01-architecture/05-dynamic-sql
  type: topic
  category: MyBatis 内部原理
  summary: 动态 SQL 标签体系（if/where/foreach/choose）与 OGNL 表达式条件判断
-->

# 05 动态 SQL

> 来源:整合自原 08.mybatis/README.md § 四.4.1
>
> 🎯 一句话定位：通过 if/where/foreach/choose 等标签与 OGNL 表达式实现条件分支和动态 SQL 拼接。

### 4.1 动态 SQL
```xml
<!-- 条件查询示例 -->
<select id="findActiveUsers" resultType="User">
    SELECT * FROM user
    <where>
        <if test="name != null">
            AND name = #{name}
        </if>
        <choose>
            <when test="status == 'ACTIVE'">
                AND status = 'ACTIVE'
            </when>
            <otherwise>
                AND status != 'DELETED'
            </otherwise>
        </choose>
    </where>
    ORDER BY create_time DESC
</select>
```
- **标签体系**：`<if>`、`<where>`、`<foreach>` 等标签实现逻辑分支
- **OGNL 表达式**：通过 `test` 属性进行条件判断

**常用配置与标签**：

| 配置/标签 | 说明 | 示例 |
|---------|------|------|
| `<bind>` | 绑定变量避免重复计算 | `<bind name="pattern" value="'%' + name + '%'" />` |
| OGNL 静态方法 | 需开启配置 | `test="@com.example.Util@isEmpty(name)"` |
| MyBatis 3.5.x | 新增 `<bind>` 支持 | 可在 `<where>` 内使用变量绑定 |

## 反向链

- [08-class-diagram](08-class-diagram.md)
- [03-database-vendor](../02-extension/03-database-vendor.md)
- [04-lambda-wrapper](../04-mybatis-plus/04-lambda-wrapper.md)

---

← [返回: MyBatis 架构与原理](README.md)
