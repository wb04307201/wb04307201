# JPA 注解

> 最后更新: 2026-06-09
> ⬅️ [返回注解速查](../README.md) | [Bean 注解](bean-and-ioc.md)

本节介绍 JPA（Java Persistence API）的实体类注解：声明实体、映射表、定义主键、关系映射。

---

## 🎯 一句话定位

**JPA 注解 = "这是实体类" + "映射到哪张表" + "主键怎么生成" + "表关系怎么映射"**——`@Entity`/`@Table` 声明实体，`@Id`/`@GeneratedValue` 定义主键，`@OneToOne`/`@OneToMany`/`@ManyToOne`/`@JoinColumn` 描述表关系。

---

## 实体类声明

### @Entity

> 表明这是一个实体类。**每个实体类对应数据库的一张表**。

### @Table

> 指定实体类对应的数据库表名。若表名与实体类名相同可省略。

```java
@Entity
@Table(name = "TB_ROLE")
public class Role implements Serializable {
    // 字段
}
```

---

## 主键与字段映射

### @Id

> 标识该属性对应数据库表的主键字段。

### @Column

> 指定属性对应的数据库列名。若字段名与列名相同可省略。

```java
@Column(name = "role_name", nullable = false)
private String roleName;
```

### @GeneratedValue（主键生成策略）

> 主键生成策略，4 种选项：

| 策略 | 说明 | 数据库支持 |
|------|------|-----------|
| **AUTO** | 由程序控制（**默认**） | 通用 |
| **IDENTITY** | 由数据库自增长 | MySQL、SQL Server（不支持 Oracle） |
| **SEQUENCE** | 通过数据库序列生成 | Oracle、PostgreSQL（不支持 MySQL） |
| **TABLE** | 通过特定数据库表产生 | 通用（利于数据库移植） |

### @SequenceGenerator

> 定义生成主键的序列，与 `@GeneratedValue(strategy = SEQUENCE)` 联合使用。

```java
@Entity
@Table(name = "TB_ROLE")
@SequenceGenerator(name = "id_seq", sequenceName = "seq_repair", allocationSize = 1)
public class Role implements Serializable {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "id_seq")
    private Long id;

    @Column(nullable = false)
    private String roleName;

    @Column(nullable = false)
    private String roleType;
}
```

---

## 字段加载策略

### @Transient

> 标识该属性**不映射**到数据库字段，ORM 框架会忽略该属性。

```java
@Column(nullable = false)
@Transient
private String lastTime;  // 不会被持久化
```

### @Basic(fetch = FetchType.LAZY)

> 在某些属性上实现懒加载，**用到时才加载**。`FetchType.EAGER` 是默认（立即加载）。

```java
@Column(nullable = false)
@Basic(fetch = FetchType.LAZY)
private String roleType;
```

> ⚠️ 懒加载要求字段不能是基本类型（如 `int`、`String`），否则会在访问时立即加载。

---

## 表关系映射

### @OneToOne（一对一）

> 一对一关联关系。

### @OneToMany（一对多）

> 一对多关联关系（一方持有多方集合）。

### @ManyToOne（多对一）

> 多对一关联关系（多方持有单一引用）。

### @JoinColumn

> 标注表与表之间关系的外键字段，通常与 `@OneToOne`/`@OneToMany` 搭配使用。

### 完整示例

```java
// 一对一：登录日志 → 用户
@Entity
@Table(name = "tb_login_log")
public class LoginLog implements Serializable {
    
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;
}

// 多对一：地址 → 客户
@Entity
@Table(name = "address")
public class AddressEO implements java.io.Serializable {
    
    @ManyToOne(cascade = { CascadeType.ALL })
    @JoinColumn(name = "customer_id")
    private CustomerEO customer;
}
```

### 4 种关系类型速查

| 注解 | 关系 | 示例 |
|------|------|------|
| `@OneToOne` | 一对一 | 用户 ↔ 登录日志 |
| `@OneToMany` | 一对多 | 部门 → 员工 |
| `@ManyToOne` | 多对一 | 员工 → 部门 |
| `@ManyToMany` | 多对多 | 学生 ↔ 课程 |

---

## 🤔 思考

1. **@Column 什么时候必须写？** 字段名与列名不一致、或需要声明 `nullable`、`length`、`unique` 等约束时。
2. **@GeneratedValue(strategy = AUTO) 怎么用？** Hibernate 根据方言自动选 IDENTITY/SEQUENCE/TABLE，最省心但不跨数据库。
3. **@OneToMany 和 @ManyToOne 怎么选？** 看维护关系的一方：多方维护用 `@ManyToOne`（推荐，性能更好），一方维护用 `@OneToMany`。
4. **@Transient 字段能参与业务逻辑吗？** 可以，它仅是不持久化到数据库。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [03 数据层](../03-data/README.md) — Spring Data JPA
- [Bean 注解](bean-and-ioc.md) — @Repository（DAO 层）
