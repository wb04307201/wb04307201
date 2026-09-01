<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\01-quickstart
  type: article
  category: MyBatis-Plus 实战
  summary: MyBatis-Plus 快速入门——10 分钟引入 MP,完成依赖、实体类、Mapper、第一个 CRUD。
  depth: ⭐⭐⭐
-->

# 01 MyBatis-Plus 快速入门

> MyBatis-Plus(简称 MP)是 MyBatis 的增强工具,在 MyBatis 的基础上**只做增强不做改变**。引入它不会改变现有 MyBatis 工程结构,只在原基础上提供通用 CRUD、条件构造器、分页、自动填充等增强 API。

## 🎯 一句话定位

**MyBatis-Plus = MyBatis + 通用 Mapper/Service + 条件构造器 + 分页插件 + 自动填充,** 让你只写单表 CRUD 不再写 XML,**前提是遵守它的约定(表名=类名转下划线、主键名为 id)**。

---

## 核心特性

MyBatis-Plus 提供 7 大核心能力,覆盖单表 CRUD 90% 场景:

| # | 能力 | 解决的问题 | 入门章节 |
|---|------|----------|---------|
| 1 | **无侵入** | 不改 MyBatis 原有行为,引入即用 | 本章 |
| 2 | **通用 CRUD** | 继承 `BaseMapper<T>` 即得 17 个 CRUD 方法 | [02-crud-basics](./02-crud-basics.md) |
| 3 | **通用 Service** | 继承 `IService<T>` 即得 Service 层 CRUD | [02-crud-basics](./02-crud-basics.md) |
| 4 | **Lambda 条件构造器** | `User::getName` 替代字符串字段名 | [04-lambda-wrapper](./04-lambda-wrapper.md) |
| 5 | **分页插件** | `Page<T>` + `PaginationInnerInterceptor` | [06-pagination](./06-pagination.md) |
| 6 | **自动填充** | `createTime` / `updateTime` 自动维护 | [07-auto-fill-and-logic-delete](./07-auto-fill-and-logic-delete.md) |
| 7 | **逻辑删除** | `@TableLogic` 自动转换 DELETE 为 UPDATE | [07-auto-fill-and-logic-delete](./07-auto-fill-and-logic-delete.md) |

---

## 快速开始

### 1. 添加依赖(Spring Boot 3.x + MP 3.5.x)

```xml
<!-- MyBatis-Plus 官方 starter(适配 Spring Boot 3.x) -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.9</version>
</dependency>

<!-- MySQL 驱动 -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>

<!-- Lombok(简化实体类) -->
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
```

> **版本注意**:Spring Boot 2.x 用 `mybatis-plus-boot-starter`;Spring Boot 3.x **必须**用 `mybatis-plus-spring-boot3-starter`(包名 `jakarta.*` 不兼容)。

### 2. 配置数据源

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mp_demo?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

# MyBatis-Plus 基础配置(可选,均有默认值)
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml  # 自定义 XML 位置
  type-aliases-package: com.example.mp.entity    # 实体类别名扫描
  configuration:
    map-underscore-to-camel-case: true          # 下划线转驼峰(默认 true)
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 打印 SQL
```

### 3. 实体类(关键 3 注解)

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@TableName("t_user")  // ① 指定表名;不写则按约定:类名转下划线 → t_user
public class User {

    @TableId(type = IdType.ASSIGN_ID)  // ② 主键策略:雪花算法(默认)
    private Long id;

    private String name;

    private Integer age;

    private String email;

    @TableField(fill = FieldFill.INSERT)  // ③ 字段填充策略
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
```

### 4. Mapper 接口

```java
public interface UserMapper extends BaseMapper<User> {
    // 空接口:继承 BaseMapper<User> 后,自动拥有 17 个 CRUD 方法:
    // insert / deleteById / updateById / selectById / selectList / ...
    // 无需写任何实现,MP 通过动态代理 + 模板 SQL 生成
}
```

### 5. 启动类 + MapperScan

```java
@SpringBootApplication
@MapperScan("com.example.mp.mapper")  // 扫描 Mapper 接口,生成代理对象
public class MpDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(MpDemoApplication.class, args);
    }
}
```

### 6. 第一个 CRUD(测试)

```java
@SpringBootTest
class UserMapperTest {

    @Autowired
    private UserMapper userMapper;

    @Test
    void testInsert() {
        User user = User.builder()
                .name("Tom")
                .age(25)
                .email("tom@example.com")
                .build();
        int rows = userMapper.insert(user);  // 返回受影响行数
        System.out.println("插入行数:" + rows + ", 自动回填 ID:" + user.getId());
        // 输出:插入行数:1, 自动回填 ID:1842345678901234567
    }

    @Test
    void testSelectById() {
        User user = userMapper.selectById(1L);
        System.out.println(user);
    }
}
```

---

## 反例对比(5 个)

### ❌/✅ 1:依赖选错导致启动失败

```xml
<!-- ❌ Spring Boot 3.x 用了 2.x 的 starter -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>  <!-- 内部依赖 javax.servlet.* -->
    <version>3.5.9</version>
</dependency>
<!-- 报错:ClassNotFoundException: javax.servlet.http.HttpServletRequest -->
```

```xml
<!-- ✅ Spring Boot 3.x 用专属 starter,内部依赖 jakarta.servlet.* -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.9</version>
</dependency>
```

### ❌/✅ 2:没写 @TableName 导致找不到表

```java
// ❌ 实体类名 User,数据库表名 t_user → 启动报错:Table 'mp_demo.user' doesn't exist
@Data
public class User {
    private Long id;
    private String name;
}
```

```java
// ✅ 显式声明表名,或保持类名 = 表名(去掉前缀)
@Data
@TableName("t_user")  // 显式指定
public class User { /* ... */ }

// 或全局配置前缀
// mybatis-plus.global-config.db-config.table-prefix: t_
```

### ❌/✅ 3:Mapper 没被扫描,注入为 null

```java
// ❌ 忘记 @MapperScan,启动后 userMapper 为 null → NullPointerException
@SpringBootApplication
public class Application { /* ... */ }

// 解决 1:启动类加 @MapperScan("com.example.mp.mapper")
// 解决 2:每个 Mapper 接口单独加 @Mapper
```

### ❌/✅ 4:主键策略选错导致大批量插入慢

```java
// ❌ 主键用 AUTO(数据库自增),但分库分表场景下 ID 会冲突
@TableId(type = IdType.AUTO)
private Long id;
```

```java
// ✅ 分布式场景用 ASSIGN_ID(雪花算法),ID 全局唯一且趋势递增
@TableId(type = IdType.ASSIGN_ID)
private Long id;
```

### ❌/✅ 5:没配日志,排查 SQL 困难

```yaml
# ❌ 不配日志,出问题只能瞎猜
spring:
  datasource:
    url: jdbc:mysql://...
```

```yaml
# ✅ 打开 SQL 日志(开发环境)
mybatis-plus:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
---
# 生产环境用性能分析插件:输出慢 SQL
# 见 [08-advanced-interceptors](./08-advanced-interceptors.md)
```

---

## 常见陷阱(3 个)

### 陷阱 1:`@TableName` 的 value 不能省略

```java
// ❌ 编译期没问题,但运行时 MP 不识别 → 仍按类名转下划线
@TableName()
public class User { /* ... */ }

// ✅ value 必填(或省略 @TableName 走默认约定)
@TableName("t_user")
public class User { /* ... */ }
```

### 陷阱 2:`BaseMapper` 的泛型必须是实体类

```java
// ❌ 泛型写成 Object,运行时报 ClassCastException
public interface UserMapper extends BaseMapper<Object> { }

// ✅ 泛型必须是 @TableName 对应的实体类
public interface UserMapper extends BaseMapper<User> { }
```

### 陷阱 3:`@TableField` 的 fill 字段必须配合 MetaObjectHandler

```java
// ❌ 只写 @TableField(fill = FieldFill.INSERT),但没注册 MetaObjectHandler → 字段为 null
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;
```

```java
// ✅ 必须注册 MetaObjectHandler Bean(详见 07 章)
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

---

## 5 大反模式

1. **反模式 1:不读官方文档,照搬过时教程** — MP 3.x 之后包名、注解、starter 都有大变化,**直接抄 2019 年的博客会启动报错**;务必看 baomidou.com 官方文档对应版本。
2. **反模式 2:把 MyBatis 的 XML 完全抛弃** — MP 的条件构造器**只适合单表 + 中等复杂度**;复杂 SQL(多表 JOIN + 子查询 + 复杂统计)仍要写 XML,不要硬塞 Wrapper。
3. **反模式 3:实体类不用 Lombok,手写 getter/setter** — Lambda 条件构造器**依赖 getter 方法引用**;手写 getter 不仅代码冗长,还会因拼写错误导致运行时找不到字段。
4. **反模式 4:启动类忘了 `@MapperScan`,Mapper 接口忘加 `@Mapper`** — 启动不报错但**所有 Mapper 注入为 null**,运行到第一个调用才 NPE。
5. **反模式 5:数据库字段加 `t_` 前缀,实体类忘加 `@TableName`** — MP 默认按类名转下划线映射,**不会自动去掉业务前缀**;要么每个实体类显式 `@TableName("t_xxx")`,要么全局配 `table-prefix: t_`。

---

## 30 秒话术

> **面试高频问法**:"MyBatis-Plus 是什么?和 MyBatis 什么关系?"
>
> **回答模板**:MyBatis-Plus 是 MyBatis 的增强工具,**只做增强不做改变**。它通过继承 `BaseMapper<T>` 提供 17 个通用 CRUD 方法、通过条件构造器(`QueryWrapper` / `LambdaQueryWrapper`)实现类型安全的链式查询、通过分页插件实现物理分页、通过 `MetaObjectHandler` 实现字段自动填充、通过 `@TableLogic` 实现逻辑删除。**它不替代 MyBatis 的 XML**,复杂 SQL 仍写 XML;它解决的是"单表 CRUD 重复样板代码"的问题。

---

## 相关章节

- 下一步:[02-crud-basics](./02-crud-basics.md) — 17 个 BaseMapper 方法清单
- 横向:[03-wrapper-system](./03-wrapper-system.md) — Wrapper 体系全貌
- 高阶:[09-best-practices](./09-best-practices.md) — 主键策略 / 多租户 / 乐观锁最佳实践

← [返回: MyBatis-Plus 总览](./README.md)
