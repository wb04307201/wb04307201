# 01 MyBatis-Plus 快速入门

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L1-79(§ 一 简介 + § 二 快速入门)

## 1.1 MyBatis-Plus 简介

MyBatis-Plus(简称 MP)是 MyBatis 的增强工具,在 MyBatis 的基础上只做增强不做改变,为简化开发、提高效率而生。它提供了强大的 CRud 操作、分页插件、条件构造器、自动填充等功能,极大减少了开发者的编码工作量。

### 核心特性

- **无侵入**:只做增强不做改变,引入 MP 不会对现有工程产生影响
- **强大的 CRUD 操作**:内置通用 Mapper、通用 Service,少量配置即可实现单表大部分 CRUD 操作
- **Lambda 条件构造器**:支持类型安全的 SQL 条件构造
- **分页插件**:内置分页插件,简单配置即可实现分页功能
- **性能分析**:内置性能分析插件,可输出 SQL 执行日志
- **全局拦截功能**:提供全局拦截功能
- **自动填充**:支持字段自动填充功能(如创建时间、更新时间等)

## 1.2 添加依赖

```xml
<!-- MyBatis-Plus 核心依赖 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>最新版本</version>
</dependency>
```

## 1.3 配置数据源

在 `application.yml` 中配置:

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/your_db?useSSL=false&serverTimezone=UTC
    username: your_username
    password: your_password
    driver-class-name: com.mysql.cj.jdbc.Driver
```

## 1.4 实体类示例

```java
@Data
@TableName("user") // 对应数据库表名
public class User {
    @TableId(type = IdType.AUTO) // 主键自增
    private Long id;
    private String name;
    private Integer age;
    private String email;

    @TableField(fill = FieldFill.INSERT) // 插入时自动填充
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE) // 插入和更新时自动填充
    private LocalDateTime updateTime;
}
```

## 1.5 Mapper 接口

```java
public interface UserMapper extends BaseMapper<User> {
    // 继承BaseMapper后,基本CRUD方法已具备
}
```

## 1.6 启动类添加注解

```java
@SpringBootApplication
@MapperScan("com.example.mapper") // 扫描Mapper接口
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
