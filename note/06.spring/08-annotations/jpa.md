# JPA 注解

> 最后更新: 2026-06-14
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

## 高级映射与查询注解

> 本节介绍**实体继承、值对象嵌入、属性转换、生命周期、锁**等高级特性。

### @MappedSuperclass（基类继承）

> 父类**不是实体**（不对应表），但其字段会**映射到子实体的表**中。

```java
@MappedSuperclass
public abstract class Auditable {
    @Column(name = "created_at") private LocalDateTime createdAt;
    @Column(name = "updated_at") private LocalDateTime updatedAt;
}

@Entity
public class User extends Auditable {     // createdAt/updatedAt 自动成为 user 表字段
    @Id private Long id;
    private String name;
}
```

### @Inheritance / @DiscriminatorColumn（继承策略）

> 实体类继承关系在 DB 中的映射策略。3 种：

| 策略 | 注解 | 表结构 | 优点 | 缺点 |
|:-----|:-----|:-------|:-----|:-----|
| **SINGLE_TABLE** | `@Inheritance(SINGLE_TABLE)` | 单表 + 辨别字段 | 查询最快 | 字段稀疏、NOT NULL 难 |
| **JOINED** | `@Inheritance(JOINED)` | 父表 + 子表（join） | 范式化 | 查询需 join |
| **TABLE_PER_CLASS** | `@Inheritance(TABLE_PER_CLASS)` | 父子各一张表 | 子表独立 | union 查询性能差 |

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "type", discriminatorType = DiscriminatorType.STRING)
public abstract class Payment { ... }

@Entity
@DiscriminatorValue("CARD")
public class CardPayment extends Payment { ... }

@Entity
@DiscriminatorValue("ALIPAY")
public class AlipayPayment extends Payment { ... }
```

### @Embeddable / @Embedded（值对象嵌入）

> 把"值对象"（无独立主键）的字段**嵌入当前实体表**。

```java
@Embeddable
public class Address {
    private String province;
    private String city;
    private String detail;
}

@Entity
public class User {
    @Id private Long id;
    @Embedded private Address home;          // 嵌入字段
    @Embedded @AttributeOverrides({         // 多个同类型可重命名列
        @AttributeOverride(name = "city", column = @Column(name = "work_city"))
    }) private Address work;
}
```

### @Convert / @Converter（属性转换器）

> 把 Java 类型映射到 DB 类型（如 `boolean ↔ Y/N` / 枚举 ↔ String）。

```java
@Converter
public class BooleanYNConverter implements AttributeConverter<Boolean, String> {
    public String convertToDatabaseColumn(Boolean b) { return b ? "Y" : "N"; }
    public Boolean convertToEntityAttribute(String s) { return "Y".equals(s); }
}

@Entity
public class User {
    @Convert(converter = BooleanYNConverter.class)
    private Boolean active;
}
```

### @EntityListeners（生命周期回调）

> 监听实体的**持久化事件**（PrePersist / PostLoad / PreUpdate / PostUpdate / PreRemove / PostRemove）。

```java
@EntityListeners(AuditingListener.class)
@Entity
public class User { ... }

public class AuditingListener {
    @PrePersist
    public void onCreate(Object o) {           // 插入前
        ((Auditable) o).setCreatedAt(Instant.now());
    }
    @PreUpdate
    public void onUpdate(Object o) {           // 更新前
        ((Auditable) o).setUpdatedAt(Instant.now());
    }
}
```

> 💡 Spring Data JPA 提供更便捷的 `@CreatedDate` / `@LastModifiedDate`（需启用 `@EnableJpaAuditing`）。

### @Version（乐观锁）

> 实体加 **版本号**字段，**更新时自动 +1**；版本不匹配则抛 `OptimisticLockingFailureException`。

```java
@Entity
public class Account {
    @Id private Long id;
    private BigDecimal balance;

    @Version
    private Long version;       // 乐观锁
}
```

```sql
-- Hibernate 生成的 SQL
update account set balance=?, version=2 where id=? and version=1
-- 若 version=1 不存在（已被别人改），rows=0 → 抛异常
```

### @Lock（悲观锁）

> Repository 方法上声明**悲观锁**（`SELECT ... FOR UPDATE`）。

```java
public interface AccountRepository extends JpaRepository<Account, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)            // SELECT ... FOR UPDATE
    Optional<Account> findById(Long id);

    @Lock(LockModeType.PESSIMISTIC_READ)             // 共享锁
    Optional<Account> findByUsername(String name);
}
```

### 乐观锁 vs 悲观锁

| 维度 | 乐观锁 (@Version) | 悲观锁 (@Lock) |
|:-----|:------------------|:----------------|
| **假设** | 冲突很少 | 冲突经常 |
| **实现** | 版本号 CAS | `SELECT FOR UPDATE` |
| **性能** | 高（无锁等待） | 低（行锁等待） |
| **适用** | 读多写少 | 写多、严格一致性 |

---

## 🤔 思考

1. **@Column 什么时候必须写？** 字段名与列名不一致、或需要声明 `nullable`、`length`、`unique` 等约束时。
2. **@GeneratedValue(strategy = AUTO) 怎么用？** Hibernate 根据方言自动选 IDENTITY/SEQUENCE/TABLE，最省心但不跨数据库。
3. **@OneToMany 和 @ManyToOne 怎么选？** 看维护关系的一方：多方维护用 `@ManyToOne`（推荐，性能更好），一方维护用 `@OneToMany`。
4. **@Transient 字段能参与业务逻辑吗？** 可以，它仅是不持久化到数据库。
5. **@Version 字段要不要手动 set？** **不要**。Hibernate 在每次 update 时自动递增，**手动改会破坏 CAS 逻辑**。
6. **@Entity / @Repository / @Table 的关系？** `@Entity` 声明是 JPA 实体；`@Table` 映射到具体表；`@Repository` 声明数据访问层。👉 PO/VO/DTO/BO/DAO/POJO 语义辨析见 [13 辨析/PO-VO-DTO-BO-DAO-POJO 语义辨析](../../13.split-hairs/06.spring/clarify-various-o/README.md)。

---

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [03 数据层](../03-data/README.md) — Spring Data JPA
- [03 数据层 JPA 事务](../../03-data/transaction/jpa-transaction.md) — JPA 事务与锁
- [Bean 注解](bean-and-ioc.md) — @Repository（DAO 层）
- [13 辨析/PO-VO-DTO-BO-DAO-POJO 语义辨析](../../13.split-hairs/06.spring/clarify-various-o/README.md)
