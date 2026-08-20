<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\07-auto-fill-and-logic-delete
  type: article
  category: 主模块子文章
  summary: 07 自动填充与逻辑删除
-->

# 07 自动填充与逻辑删除

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L196-241(§三.5 自动填充 + §三.6 逻辑删除)

`MetaObjectHandler` 在 insert / update SQL 执行前由框架回调,自动写入 `createTime` / `updateTime` / `createBy` / `updateBy` 等字段——业务侧无需手动 `setCreateTime(LocalDateTime.now())`。`@TableLogic` 则把 `DELETE FROM user WHERE id = ?` 自动改写为 `UPDATE user SET deleted = 1 WHERE id = ?`,并把 `SELECT` 自动追加 `WHERE deleted = 0`。这两个机制是 MyBatis-Plus 消除样板代码的核心抓手,也是审计追踪(who/when)与假删除的数据基础。

## 一、自动填充（MetaObjectHandler）

### 1.1 完整实现

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        LocalDateTime now = LocalDateTime.now();
        // 严格模式：字段存在且值为 null 才填充；避免覆盖业务显式传入的值
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, now);
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, now);

        // 当前用户：通常从 SecurityContext / ThreadLocal 取
        Long currentUserId = SecurityUtils.getCurrentUserId();
        this.strictInsertFill(metaObject, "createBy", Long.class, currentUserId);
        this.strictInsertFill(metaObject, "updateBy", Long.class, currentUserId);
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
        this.strictUpdateFill(metaObject, "updateBy", Long.class, SecurityUtils.getCurrentUserId());
    }
}
```

### 1.2 严格模式 vs 非严格模式

```java
// 严格模式（推荐）：仅当字段值为 null 时才填充，业务显式 set 优先
this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, now);

// 非严格模式：直接覆盖，无论业务是否已设置值（可能覆盖业务期望值）
this.fillStrategy(metaObject, "createTime", now);
```

**生产建议**：始终使用 `strictInsertFill` / `strictUpdateFill`。业务代码若需要覆盖时间，应自己显式 `setCreateTime(...)`，不应被填充处理器隐式写入。

### 1.3 FieldFill 策略与实体类配合

实体类字段必须标注 `@TableField(fill = ...)` 才会触发填充：

```java
@Data
@TableName("user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;

    @TableField(fill = FieldFill.INSERT)               // 仅 insert 时填充
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)         // insert + update 都填充
    private LocalDateTime updateTime;

    @TableField(fill = FieldFill.INSERT)
    private Long createBy;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updateBy;
}
```

| FieldFill | insert | update | 典型字段 |
|-----------|--------|--------|---------|
| `INSERT` | 写入 | 不写 | `createTime`、`createBy` |
| `INSERT_UPDATE` | 写入 | 写入 | `updateTime`、`updateBy` |
| `UPDATE` | 不写 | 写入 | 极少用 |
| `DEFAULT` | 不写 | 不写 | 普通字段 |

### 1.4 取不到当前用户的兜底

```java
@Override
public void insertFill(MetaObject metaObject) {
    Long userId;
    try {
        userId = SecurityUtils.getCurrentUserId();
    } catch (Exception e) {
        // 系统任务、定时任务、初始化数据无登录用户，兜底为系统用户
        userId = 0L;
    }
    this.strictInsertFill(metaObject, "createBy", Long.class, userId);
}
```

---

## 二、逻辑删除（@TableLogic）

### 2.1 实体类标注

```java
@Data
@TableName("user")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;

    // 逻辑删除字段：0=未删除（默认），1=已删除
    @TableLogic
    private Integer deleted;
}
```

### 2.2 三种配置方式

**方式一：application.yml 全局配置（推荐）**

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted           # 全局逻辑删除字段名
      logic-not-delete-value: 0            # 未删除值
      logic-delete-value: 1                # 已删除值
```

> 全局配置后，**所有带 `deleted` 字段的实体类**自动启用逻辑删除，无需逐个 `@TableLogic` 标注（但保留标注更清晰）。

**方式二：@TableLogic 注解参数（覆盖全局）**

```java
// 个别表字段名/取值与全局不同，用注解覆盖
@TableLogic(value = "0", delval = "1")
private Integer isDeleted;
```

**方式三：自定义全局处理器（特殊业务）**

```java
@Configuration
public class LogicDeleteConfig {
    @Bean
    public IGlobalConfig globalConfig() {
        return new GlobalConfig().setDbConfig(
            new DbConfig()
                .setLogicDeleteField("deleted")
                .setLogicNotDeleteValue("N")   // 字符串类型
                .setLogicDeleteValue("Y")
        );
    }
}
```

### 2.3 自动 SQL 改写效果

```java
// 业务代码
userMapper.deleteById(1L);          // 不再 DELETE，改 UPDATE
List<User> list = userMapper.selectList(null);  // 自动追加 WHERE deleted = 0
```

实际执行的 SQL：

```sql
-- deleteById(1L)
UPDATE user SET deleted = 1 WHERE id = 1 AND deleted = 0

-- selectList(null)
SELECT id, name, deleted FROM user WHERE deleted = 0
```

### 2.4 自定义查询要手动加条件

`@TableLogic` 只对 MP 内置方法（`selectList`、`selectById`、`deleteById` 等）生效。**自定义 @Select / XML SQL 不会自动追加**：

```java
// ❌ 自定义 XML 查询未加 deleted = 0 → 把已删除数据也查出来
@Select("SELECT * FROM user WHERE name = #{name}")
List<User> selectByName(@Param("name") String name);

// ✅ 手动追加
@Select("SELECT * FROM user WHERE name = #{name} AND deleted = 0")
List<User> selectByName(@Param("name") String name);
```

### 2.5 唯一索引与逻辑删除的冲突

`deleted` 字段若是唯一索引的一部分，会导致"删除后无法再创建同名记录"。

```sql
-- ❌ username 唯一索引包含 deleted
UNIQUE KEY uk_username (username, deleted)
-- 用户 'tom' 删除后，deleted=1 占着坑位，无法再创建新 'tom'

-- ✅ 方案 A：deleted 不进唯一索引
UNIQUE KEY uk_username (username)

-- ✅ 方案 B：使用时间戳区分（每次删除更新 deleted 为不同值）
UNIQUE KEY uk_username (username, deleted)
-- deleted 默认 0，删除时改为 1、2、3... 唯一
```

---

## 三、4 个常见配置反例

### 3.1 ❌ 反例 1：MetaObjectHandler 没加 @Component

```java
// ❌ 没加 @Component → Spring 不扫描，填充不生效
public class MyMetaObjectHandler implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) { ... }
}
// 表现：createTime 字段一直是 null
```

```java
// ✅ 加 @Component，让 Spring 扫描并注入到 MP 插件链
@Component
public class MyMetaObjectHandler implements MetaObjectHandler { ... }
```

**或**：在 `@Configuration` 中显式注册：

```java
@Configuration
public class MybatisPlusConfig {
    @Bean
    public MetaObjectHandler metaObjectHandler() {
        return new MyMetaObjectHandler();
    }
}
```

### 3.2 ❌ 反例 2：实体字段没标 @TableField(fill = ...)

```java
// ❌ 字段没标注 → MetaObjectHandler 不知道要处理它
public class User {
    private LocalDateTime createTime;  // 不会被自动填充
}
```

```java
// ✅ 必须显式标注 fill 策略
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;
```

### 3.3 ❌ 反例 3：用 fillStrategy 而非 strictInsertFill

```java
// ❌ 非严格模式：业务显式 set 的值会被覆盖
this.fillStrategy(metaObject, "createTime", LocalDateTime.now());
// 业务代码 user.setCreateTime(someDate) → 被处理器强制改成 now()
```

```java
// ✅ 严格模式：业务显式 set 的值优先
this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
```

### 3.4 ❌ 反例 4：逻辑删除与唯一索引冲突未处理

```java
// ❌ 业务上"删除用户"后无法再创建同名用户
// SQL: UPDATE user SET deleted = 1 WHERE id = 1
// 后续 INSERT user(name) VALUES('tom') → 唯一约束冲突
```

```java
// ✅ 方案：deleted 字段不进唯一索引，或删除时改为不同时间戳
ALTER TABLE user DROP INDEX uk_username;
ALTER TABLE user ADD UNIQUE INDEX uk_username (username);
```

---

## 四、整合测试示例

```java
@SpringBootTest
class AutoFillAndLogicDeleteTest {

    @Autowired
    private UserMapper userMapper;

    @Test
    void testInsertFill() {
        User user = new User();
        user.setName("Tom");
        // 注意：不 set createTime / updateTime / createBy / updateBy
        userMapper.insert(user);

        User loaded = userMapper.selectById(user.getId());
        assertNotNull(loaded.getCreateTime());           // 自动填充
        assertEquals(LocalDateTime.now().getDayOfYear(),
                     loaded.getCreateTime().getDayOfYear());
        assertEquals(SecurityUtils.getCurrentUserId(), loaded.getCreateBy());
    }

    @Test
    void testLogicDelete() {
        User user = new User();
        user.setName("Tom");
        userMapper.insert(user);
        Long id = user.getId();

        userMapper.deleteById(id);  // 逻辑删除 → UPDATE deleted=1

        // 主键查询：查不到（因为 WHERE deleted = 0）
        assertNull(userMapper.selectById(id));

        // 绕过：selectList 同样过滤已删除
        assertEquals(0, userMapper.selectList(null).size());

        // 物理删除需要走自定义 SQL 或 @SqlParser 绕过
    }
}
```

---

## 五、常见陷阱

| 陷阱 | 后果 | 解决 |
|------|------|------|
| `@TableField(fill=...)` 与 `default` 值冲突 | DB 默认值被处理器覆盖 | 数据库表不加默认值，由处理器统一管理 |
| 取不到当前用户 NPE | `createBy` 写入 null | `try/catch` 兜底为系统用户 |
| 自定义 SQL 漏加 `deleted=0` | 查出已删除数据 | XML / 注解 SQL 手动加过滤条件 |
| `deleted` 进入唯一索引 | 删除后无法重建 | 不进唯一索引 / 用时间戳 |
| 批量插入 `saveBatch` 默认 size=1000 | 大量数据超时 | 拆批或调大 rewriteBatchedStatements |
| `updateById` 未触发 `updateFill` | `updateTime` 不更新 | 检查 `@TableField(fill=INSERT_UPDATE)` 是否加上 |

---

← [返回: MyBatis-Plus 全家桶](./README.md)