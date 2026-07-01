# R2DBC 响应式数据库访问

> ⬅️ [返回 WebFlux 总览](README.md) | [02 Web 层](../README.md)

**R2DBC（Reactive Relational Database Connectivity）** 是响应式版的 JDBC 规范，让 SQL 数据库访问也能**非阻塞**。Spring Data R2DBC 在此之上提供 `DatabaseClient`（低层 API）与 `ReactiveCrudRepository`（高层抽象），与 WebFlux 配合实现**端到端响应式**。

---

## 🎯 一句话定位

**R2DBC = "让关系型数据库也能跑在事件循环上"**——协议层非阻塞，连接复用更高效；代价是**生态远不如 JPA 成熟**，没有懒加载、级联、二级缓存。

---

## 一、为什么需要 R2DBC

| 问题 | JDBC / JPA 表现 | R2DBC 表现 |
|------|-----------------|------------|
| 数据库慢查询阻塞工作线程 | 1 连接 = 1 线程占用 | 非阻塞，连接异步释放 |
| 高并发下连接池撑爆 | 受限于 HikariCP 大小 + 线程数 | 连接数远小于线程数 |
| 与 WebFlux 端到端响应式 | 半阻塞（边界处切线程） | 全栈响应式 |
| 生态成熟度 | ★★★★★ | ★★ |

> **R2DBC 不是要取代 JPA**，而是给"高并发 + 全响应式"场景一个非阻塞通道。常规业务仍然首选 JPA。

---

## 二、依赖与配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>
<dependency>
    <!-- 按数据库选驱动 -->
    <groupId>io.asyncer</groupId>
    <artifactId>r2dbc-mysql</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  r2dbc:
    url: r2dbc:mysql://localhost:3306/demo
    username: root
    password: root
    pool:
      max-size: 20
      initial-size: 5
```

---

## 三、DatabaseClient：低层 API

```java
@Service
public class UserService {
    private final DatabaseClient db;

    public UserService(DatabaseClient db) { this.db = db; }

    public Flux<User> list() {
        return db.sql("SELECT id, name, email FROM t_user ORDER BY id")
                .map(row -> new User(
                        row.get("id", Long.class),
                        row.get("name", String.class),
                        row.get("email", String.class)))
                .all();
    }

    public Mono<User> findById(long id) {
        return db.sql("SELECT id, name, email FROM t_user WHERE id = :id")
                .bind("id", id)
                .map(row -> /* ... */)
                .one();
    }

    public Mono<Long> create(User u) {
        return db.sql("INSERT INTO t_user(name, email) VALUES(:n, :e)")
                .bind("n", u.getName()).bind("e", u.getEmail())
                .fetch().rowsUpdated()
                .map(rows -> (long) rows);
    }
}
```

> `DatabaseClient` 类似 JdbcTemplate，但返回 `Mono` / `Flux`，全部非阻塞。

---

## 四、ReactiveCrudRepository：高层抽象

```java
@Table("t_user")
public class User {
    @Id private Long id;
    private String name;
    private String email;
    // getters / setters
}

public interface UserRepository extends ReactiveCrudRepository<User, Long> {

    @Query("SELECT * FROM t_user WHERE name LIKE :pattern ORDER BY id")
    Flux<User> findByNameLike(@Param("pattern") String pattern);

    Mono<User> findByEmail(String email);
}
```

在 `@SpringBootApplication` 扫描下直接注入：

```java
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {
    private final UserRepository repo;

    @GetMapping
    public Flux<User> list() { return repo.findAll(); }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<User>> get(@PathVariable Long id) {
        return repo.findById(id)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}
```

---

## 五、事务：R2dbcTransactionManager

```java
@Configuration
@EnableTransactionManagement
public class R2dbcConfig {
    @Bean
    public ReactiveTransactionManager transactionManager(ConnectionFactory cf) {
        return new R2dbcTransactionManager(cf);
    }
}

@Service
public class OrderService {
    private final DatabaseClient db;

    @Transactional
    public Mono<Void> placeOrder(Order order) {
        return db.sql("INSERT INTO t_order(...) VALUES(...)")
                .bind(...)
                .fetch().rowsUpdated()
                .then(db.sql("UPDATE t_stock SET qty = qty - :n WHERE id = :i")
                        .bind(...)
                        .fetch().rowsUpdated())
                .then();
    }
}
```

> **重要**：R2DBC 事务传播语义与 JPA 一样（`REQUIRED`/`REQUIRES_NEW` 等），但**不支持跨资源事务**——若需同时操作 MySQL + Redis，请用 Saga/消息补偿。

---

## 六、R2DBC vs JPA

| 维度 | Spring Data JPA | Spring Data R2DBC |
|------|-----------------|-------------------|
| **底层** | JDBC（阻塞） | R2DBC（非阻塞） |
| **API 风格** | 命令式 / `Optional` | 响应式 / `Mono` / `Flux` |
| **事务** | `JpaTransactionManager` | `R2dbcTransactionManager` |
| **懒加载** | ✅ | ❌ |
| **二级缓存** | ✅（Hibernate） | ❌ |
| **级联 / 关系映射** | ✅ 完整 | ⚠️ 弱（仅 1:N 直接映射） |
| **Schema 迁移** | Flyway / Liquibase | Flyway / Liquibase（注意 R2DBC 不读 schema 工具） |
| **生态成熟度** | ★★★★★ | ★★ |
| **适用场景** | 99% 业务、高度对象建模 | 全响应式、高并发 I/O |

---

## 七、常见问题

1. **JPA + R2DBC 能不能混用？** 技术上能（不同事务管理器），但容易导致连接泄漏、事务边界混乱，**强烈不推荐**。
2. **N+1 查询**：R2DBC 不像 Hibernate 那样自动批量化，需在 Repository 用 `@Query` 写 JOIN 或一次性取回。
3. **连接池**：默认使用 `r2dbc-pool`，务必设置 `max-size` 上限，避免拖垮数据库。
4. **Schema 迁移**：R2DBC 不感知 Flyway 之类的 schema；用 Spring Boot 的 Flyway 自动配置即可，与 R2DBC 数据源独立。

---

## 相关章节

- ⬅️ [WebFlux 总览](README.md)
- [WebClient 调用](webclient.md) — 端到端响应式
- [03 数据层/事务](../../03-data/transaction/README.md) — 事务管理
