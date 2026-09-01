<!--
module:
  parent: spring/mybatis/01-architecture
  slug: spring/mybatis/01-architecture/05-dynamic-sql
  type: topic
  category: MyBatis 内部原理
  summary: 动态 SQL 标签体系（if/where/foreach/choose）与 OGNL 表达式条件判断
  depth: ⭐⭐⭐
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

## 1. 完整标签体系

MyBatis 动态 SQL 一共提供 9 个核心标签,本节补全除 `if/where/foreach/choose` 之外的高阶标签。

### 1.1 `<trim>` 自定义前后缀（替代 where/set）

`<trim>` 是 `<where>` 和 `<set>` 的底层原语,允许自定义前缀、后缀、剪除规则。

```xml
<!-- 等价于 <where>：自动加 WHERE 并剪除首个 AND/OR -->
<trim prefix="WHERE" prefixOverrides="AND |OR ">
    <if test="name != null">AND name = #{name}</if>
    <if test="status != null">AND status = #{status}</if>
</trim>

<!-- 等价于 <set>：自动加 SET 并剪除末尾逗号 -->
<trim prefix="SET" suffixOverrides=",">
    <if test="name != null">name = #{name},</if>
    <if test="email != null">email = #{email},</if>
</trim>
```

| 属性 | 含义 |
|------|------|
| `prefix` | 给拼接结果添加前缀（如 `WHERE` / `SET`） |
| `suffix` | 给拼接结果添加后缀 |
| `prefixOverrides` | 开头要剪除的字符串（用 `\|` 分隔多个候选） |
| `suffixOverrides` | 末尾要剪除的字符串 |

> 💡 `prefixOverrides` 中多个值用 `\|` 分隔,MyBatis 会按列表顺序依次尝试剪除,**所以 `AND ` 和 `OR ` 必须带尾随空格**,否则会误伤 `ANDROID` 这种字段名。

### 1.2 `<set>` 用于 UPDATE 动态字段

```xml
<update id="updateUser" parameterType="User">
    UPDATE user
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="email != null">email = #{email},</if>
        <if test="age != null">age = #{age},</if>
    </set>
    WHERE id = #{id}
</update>
```

`<set>` 实际是 `<trim prefix="SET" suffixOverrides=",">` 的语法糖,**自动剪除末尾多余逗号**。如果不用 `<set>`,开发者必须手动保证最后一个字段后无逗号,否则 SQL 报错。

### 1.3 `<foreach>` 完整 collection 语法

`<foreach>` 用于 IN 查询、批量插入、批量删除等集合遍历场景。

```xml
<select id="findByIds" resultType="User">
    SELECT * FROM user WHERE id IN
    <foreach collection="ids" item="id" index="i"
             open="(" separator="," close=")">
        #{id}
    </foreach>
</select>

<!-- collection 支持 List / Array / Map 三种类型 -->
<!-- 1. List: collection="list", item="item" -->
<!-- 2. Array: collection="array", item="item" -->
<!-- 3. Map: collection="map.keys" 或 collection="map.values" -->
```

| 属性 | 含义 |
|------|------|
| `collection` | 必填,要遍历的集合（list / array / map / @Param 名） |
| `item` | 循环中当前元素的变量名 |
| `index` | 循环索引（List/Array 为下标,Map 为 key） |
| `open` | 拼接结果的开头字符串 |
| `close` | 拼接结果的结尾字符串 |
| `separator` | 元素之间的分隔符 |

> ⚠️ 当 Mapper 方法只有一个参数且为 List/Array 时,`collection` 必须显式写 `"list"` 或 `"array"`;多个参数时用 `@Param("ids")` 注解命名。

### 1.4 `<include>` / `<sql>` SQL 片段复用

```xml
<!-- 定义片段 -->
<sql id="userColumns">
    id, name, email, create_time
</sql>

<!-- 引用片段 -->
<select id="findAll" resultType="User">
    SELECT <include refid="userColumns" /> FROM user
</select>

<!-- 带 property 替换的动态片段 -->
<sql id="userColumnsWithPrefix">
    ${prefix}.id, ${prefix}.name, ${prefix}.email
</sql>

<select id="findJoin" resultMap="userWithDetail">
    SELECT
    <include refid="userColumnsWithPrefix">
        <property name="prefix" value="u"/>
    </include>
    FROM user u LEFT JOIN detail d ON u.id = d.user_id
</select>
```

`<sql>` 配合 `<include>` 是解决多表 JOIN 时列名重复、字段抽取复用的关键手段。配合 `<property>` 还能做前缀替换。

### 1.5 `<selectKey>` 主键回填

非自增主键（Oracle 序列 / UUID / 业务主键）需要在 INSERT 后立即拿到主键：

```xml
<insert id="insertUser" parameterType="User">
    <selectKey keyProperty="id" resultType="long" order="BEFORE">
        SELECT seq_user.nextval FROM dual
    </selectKey>
    INSERT INTO user (id, name) VALUES (#{id}, #{name})
</insert>

<!-- MySQL 自增主键：等价但更简洁 -->
<insert id="insertUserAuto" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO user (name) VALUES (#{name})
</insert>
```

| 属性 | 含义 |
|------|------|
| `keyProperty` | 主键回填到参数对象的属性名（支持嵌套：`user.id`） |
| `order` | BEFORE / AFTER,Oracle 序列必须 BEFORE |
| `resultType` | 主键 Java 类型 |

## 2. OGNL 表达式深入

### 2.1 内置参数

MyBatis 在 `test` 表达式中预置了两个特殊参数：

```xml
<select id="findUser" resultType="User">
    SELECT * FROM user
    <where>
        <!-- _parameter:整个入参对象（null 时为 null）-->
        <if test="_parameter != null">
            AND id = #{id}
        </if>
        <!-- _databaseId:当前数据库厂商别名（用于多数据库兼容）-->
        <if test="_databaseId == 'mysql'">
            LIMIT #{offset}, #{size}
        </if>
        <if test="_databaseId == 'oracle'">
            ROWNUM &lt;= #{size}
        </if>
    </where>
</select>
```

> 💡 **多数据库适配**：`databaseIdProvider`（TypeAlias `DB_VENDOR`）会根据 JDBC URL 自动匹配,结合 `_databaseId` 可写一份 XML 适配多种数据库。

### 2.2 静态方法调用

```xml
<!-- 调用类静态方法（无需实例化）-->
<if test="@com.example.util.SqlHelper@isValid(status)">
    AND status = #{status}
</if>

<!-- 调用工具类做字符串处理 -->
<if test="@org.apache.commons.lang3.StringUtils@isNotBlank(name)">
    AND name LIKE CONCAT('%', #{name}, '%')
</if>

<!-- 枚举比较（推荐配合 MyBatis-Plus 注解）-->
<if test="@com.example.enums.UserStatusEnum@ACTIVE.code == status">
    AND status = 'ACTIVE'
</if>
```

格式固定为 `@全限定类名@方法名(参数)`,需在 `<settings>` 中开启（3.x 默认开启,无需额外配置）。

### 2.3 集合伪属性

OGNL 提供对集合的内省（introspection）,无需手动遍历即可访问大小、键值：

```xml
<!-- List / Array: size / isEmpty -->
<if test="ids != null and ids.size() > 0">
    AND id IN
    <foreach collection="ids" item="id" open="(" close=")" separator=",">
        #{id}
    </foreach>
</if>

<!-- Map: keys / values -->
<if test="filters != null and filters.size() > 0">
    AND
    <foreach collection="filters.keys" item="key" separator=" AND ">
        ${key} = #{filters[${key}]}
    </foreach>
</if>

<!-- String 伪属性: length -->
<if test="name != null and name.length() > 0">
    AND name = #{name}
</if>
```

> ⚠️ 注意 List 的方法调用要写 `ids.size()`,**不是** `ids.length`(后者属于数组)。

## 3. 执行原理

### 3.1 SqlNode 继承树

MyBatis 把每个 XML 标签编译成一个 `SqlNode` 节点,形成树状结构：

```
SqlNode (接口)
├── IfSqlNode           → <if>
├── ChooseSqlNode       → <choose>
│   ├── IfSqlNode       → <when>
│   └── otherwise SqlNode → <otherwise>
├── WhereSqlNode        → <where>（TrimSqlNode 子类）
├── SetSqlNode          → <set>（TrimSqlNode 子类）
├── TrimSqlNode         → <trim>
├── ForEachSqlNode      → <foreach>
├── BindSqlNode         → <bind>
├── TextSqlNode         → 纯文本（含 ${}）
│   ├── StaticTextSqlNode    → 无 ${} 的纯文本
│   └── DynamicCheckTokenSqlNode → 含 ${} 的动态文本
├── MixedSqlNode        → 容器节点,包装多个子 SqlNode
├── VarDeclSqlNode      → 变量声明
└── IncludeSqlNode      → <include>（运行时替换 refid）
```

每个 SqlNode 暴露 `apply(DynamicContext context)` 方法,执行时遍历树,条件成立的节点把 SQL 片段追加到 `DynamicContext` 的 StringBuilder 中。

### 3.2 DynamicSqlSource vs RawSqlSource

解析 XML 时,MyBatis 会根据 SQL 中是否包含动态标签决定 SqlSource 类型：

| SqlSource 类型 | 触发条件 | 性能 | 适用场景 |
|----------------|---------|------|---------|
| `RawSqlSource` | 无任何动态标签（纯 `#{...}` 占位符） | 高（编译期绑定一次 SQL） | 静态 SQL,如 `SELECT * FROM user WHERE id = #{id}` |
| `DynamicSqlSource` | 包含 `<if/where/foreach/choose/bind>` 等 | 低（每次执行遍历 SqlNode 树） | 条件分支、IN 查询、动态 UPDATE |
| `ProviderSqlSource` | `@SelectProvider` 等注解 | 同 DynamicSqlSource | 注解式动态 SQL,逻辑放 Java 类 |

```java
// 内部判断逻辑（简化）
boolean isDynamic = sqlNode instanceof DynamicSqlNode || ...;
SqlSource source = isDynamic
    ? new DynamicSqlSource(configuration, rootSqlNode)
    : new RawSqlSource(configuration, sql, parameterType);
```

> 💡 **性能建议**：如果一条 SQL 没有动态条件,XML 标签写得过于"防御性"反而会触发 DynamicSqlSource,白白走一遍 SqlNode 树解析。**没有条件分支时直接写裸 SQL,性能更高**。

### 3.3 BoundSql.getSql() 拼接过程

执行阶段,MyBatis 通过以下流程得到最终 SQL：

```
1. Executor.query(MappedStatement, parameter)
   ↓
2. 获取 MappedStatement.getSqlSource()
   ↓
3. SqlSource.getBoundSql(parameter)
   ├─ DynamicSqlSource: 遍历 SqlNode 树,拼到 DynamicContext
   │                    → 应用 OGNL、参数替换
   └─ RawSqlSource:    直接返回预编译 SQL（带 ? 占位符）
   ↓
4. BoundSql { sql: "...", parameterMappings: [...], additionalParameters: {...} }
   ↓
5. ParameterHandler.setParameters() → 把 #{...} 替换成 ? 并绑定参数
   ↓
6. JDBC PreparedStatement.execute()
```

```java
// 示例：通过反射看 BoundSql 内容
MappedStatement ms = configuration.getMappedStatement("com.example.UserMapper.findByIds");
BoundSql boundSql = ms.getBoundSql(parameter);
String sql = boundSql.getSql();        // 拼接后的完整 SQL
List<ParameterMapping> mappings = boundSql.getParameterMappings();
Object additional = boundSql.getAdditionalParameter("name"); // <bind> 绑定的变量
```

> 💡 **调试技巧**：拦截器 `Interceptor` 在 `ParameterHandler.setParameters` 之前拦下来,打印 `boundSql.getSql()` 就能看到 MyBatis 真正发给数据库的 SQL。

## 4. 实战陷阱

### 4.1 ❌ 用 `${}` 拼接用户输入（SQL 注入）

```xml
<!-- ❌ 致命：${} 是字符串直接替换,等同于 Statement 拼接 -->
<select id="findByName" resultType="User">
    SELECT * FROM user WHERE name = '${name}'
</select>

<!-- 用户输入 name = "' OR '1'='1" 时：SELECT * FROM user WHERE name = '' OR '1'='1' -->
<!-- 整张表泄露 -->

<!-- ✅ 正确：用 #{} 预编译,自动转义 -->
<select id="findByName" resultType="User">
    SELECT * FROM user WHERE name = #{name}
</select>
```

> 📌 **铁律**：`${}` 只用于**确定安全**的拼接场景：表名、字段名、`ORDER BY` 后的列名、`LIMIT` 后的纯数字。**任何用户输入都用 `#{}`**。

### 4.2 ❌ `<where>` 内每个 `<if>` 重复写 `AND`

```xml
<!-- ❌ 不规范：where 标签会自动处理首个 AND,但非首个条件还是依赖手写 AND -->
<select id="findUser" resultType="User">
    SELECT * FROM user
    <where>
        <if test="name != null">name = #{name}</if>
        <if test="email != null">AND email = #{email}</if>
        <if test="status != null">AND status = #{status}</if>
    </where>
</select>

<!-- ✅ 推荐：每个条件前都加 AND,让 <where> 自动剪除首个 AND,保证逻辑清晰 -->
<select id="findUser" resultType="User">
    SELECT * FROM user
    <where>
        <if test="name != null">AND name = #{name}</if>
        <if test="email != null">AND email = #{email}</if>
        <if test="status != null">AND status = #{status}</if>
    </where>
</select>
```

`<where>` 内部规则：
1. 所有 `<if>` 都不成立 → 不输出 `WHERE`
2. 首个有效条件含 `AND/OR` 前缀 → 剪除前缀,输出 `WHERE <条件>`
3. 首个有效条件无前缀 → 直接输出 `WHERE <条件>`

### 4.3 ❌ `<foreach>` separator 误用导致末尾逗号

```xml
<!-- ❌ open/close 已包含括号,但 separator 用了 ; 导致末尾多余分号 -->
<foreach collection="ids" item="id" open="(" close=")" separator=";">
    #{id};
</foreach>
<!-- 结果：(1; 2; 3; ;)  ← 末尾多个 ; -->

<!-- ✅ 正确：separator 只写分隔符,item 内部不放分隔符 -->
<foreach collection="ids" item="id" open="(" close=")" separator=",">
    #{id}
</foreach>
<!-- 结果：(1, 2, 3) -->
```

### 4.4 ❌ `<bind>` 与 `<if>` 作用域错位

```xml
<!-- ❌ bind 定义在 <if> 外部,但引用在 <if> 内部 -->
<bind name="pattern" value="'%' + name + '%'" />
<if test="pattern != null">
    AND name LIKE #{pattern}
</if>
<!-- bind 始终生效,无法实现"name 为空就不参与 LIKE"的效果 -->

<!-- ✅ 正确：在需要时绑定 -->
<if test="name != null">
    <bind name="pattern" value="'%' + name + '%'" />
    AND name LIKE #{pattern}
</if>
```

### 4.5 ❌ 误用 `<foreach>` 在 DELETE/INSERT 缺 `;` 批量执行问题

```xml
<!-- ❌ 默认 executorType=SIMPLE 时,foreach 1000 条会发送 1000 次 SQL -->
<delete id="batchDelete">
    DELETE FROM user WHERE id IN
    <foreach collection="ids" item="id" open="(" close=")" separator=",">
        #{id}
    </foreach>
</delete>

<!-- ✅ 真正批量：开 BATCH Executor,或开启 allowMultiQueries (MySQL JDBC) -->
<settings>
    <setting name="defaultExecutorType" value="BATCH"/>
    <!-- MySQL JDBC URL: jdbc:mysql://...?allowMultiQueries=true -->
</settings>
```

## 5. MyBatis-Plus 联动

### 5.1 LambdaQueryWrapper 翻译成 XML

MyBatis-Plus 的 `LambdaQueryWrapper` 在底层最终**也会翻译成 XML 动态 SQL**,通过 `Wrappers.lambdaQuery()` 构建的 SQL 大致等价于：

```java
// Java 写法（MP）
LambdaQueryWrapper<User> wrapper = Wrappers.lambdaQuery(User.class)
    .eq(User::getName, "Tom")
    .ge(User::getAge, 18)
    .orderByDesc(User::getCreateTime)
    .last("LIMIT 10");
List<User> users = userMapper.selectList(wrapper);
```

翻译成 XML 动态 SQL 等价于：

```xml
<select id="selectList" resultType="User">
    SELECT id, name, age, create_time FROM user
    <where>
        <if test="ew != null and ew.sqlSegment != null and ew.nonEmptyOfWhere">
            ${ew.sqlSegment}
        </if>
    </where>
</select>
```

其中 `${ew.sqlSegment}` 是 MP 预先生成的 SQL 片段（如 `name = ? AND age >= ? ORDER BY create_time DESC LIMIT 10`）,**用的是 `${}` 而非 `#{}`**,因为 MP 已经在内部做了参数化,这里只把条件片段原样拼接。

> ⚠️ 这就是为什么 **MP 必须配合分页插件使用**:`last("LIMIT 10")` 这种写法本质是字符串拼接,如果业务方把用户输入塞进 `last` 就会注入。

### 5.2 注解 + Wrapper 组合用法

```java
public interface UserMapper extends BaseMapper<User> {
    // 自定义 SQL,条件由 Wrapper 提供
    @Select("SELECT * FROM user ${ew.customSqlSegment}")
    List<User> selectCustom(@Param(Constants.WRAPPER) Wrapper<User> wrapper);
}

// 使用
userMapper.selectCustom(Wrappers.lambdaQuery(User.class).eq(User::getStatus, "ACTIVE"));
```

| 写法 | 适用场景 |
|------|---------|
| 纯 Lambda Wrapper | 单表 CRUD、简单条件 |
| 注解 + customSqlSegment | 自定义列、JOIN 后仍想用 Wrapper 做 WHERE |
| XML + `<where>` + `<if>` | 复杂多表 JOIN、强可控 |
| `@SelectProvider` | 动态 SQL 逻辑写在 Java 类（更适合团队规范）|

---

## 反向链

- [08-class-diagram](08-class-diagram.md)
- [03-database-vendor](../02-extension/03-database-vendor.md)
- [04-lambda-wrapper](../04-mybatis-plus/04-lambda-wrapper.md)

---

← [返回: MyBatis 架构与原理](README.md)
