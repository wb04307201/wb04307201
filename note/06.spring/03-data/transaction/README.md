# Spring事务管理

## 1. 声明式事务 vs 编程式事务
- **声明式事务**  
  基于AOP实现，通过`@Transactional`注解配置，非侵入式。
    - **优点**：代码简洁，配置集中（如XML或注解），支持事务传播行为和隔离级别设置。
    - **适用场景**：90%以上业务场景，推荐优先使用。
    - **示例**：
      ```java
      @Service
      public class UserService {
          @Transactional(propagation = Propagation.REQUIRED, rollbackFor = Exception.class)
          public void updateUser(User user) {
              userRepository.save(user);
          }
      }
      ```

- **编程式事务**  
  通过`TransactionTemplate`或`PlatformTransactionManager`手动控制事务边界，代码侵入性强。
    - **优点**：灵活控制事务逻辑（如嵌套事务、动态回滚）。
    - **适用场景**：复杂业务逻辑（如批量操作、自定义回滚条件）。
    - **示例**：
      ```java
      @Service
      public class OrderService {
          @Autowired private TransactionTemplate transactionTemplate;
          public void processOrder(Order order) {
              transactionTemplate.execute(status -> {
                  try {
                      orderRepository.save(order);
                      // 业务逻辑
                  } catch (Exception e) {
                      status.setRollbackOnly(); // 手动回滚
                      throw e;
                  }
                  return null;
              });
          }
      }
      ```

## 2. 事务传播行为
Spring定义7种传播行为，核心解决事务嵌套问题：

| 行为              | 描述                 | 适用场景                |
|-----------------|--------------------|---------------------|
| `REQUIRED`（默认）  | 加入现有事务或新建事务        | 大多数业务方法             |
| `REQUIRES_NEW`  | 总是新建独立事务，挂起当前事务    | 日志记录、审计             |
| `NESTED`        | 嵌套事务（依赖保存点），支持部分回滚 | 复杂业务部分回滚（需数据库支持保存点） |
| `SUPPORTS`      | 存在事务则加入，无则非事务执行    | 查询方法                |
| `MANDATORY`     | 必须存在事务，否则抛异常       | 强制事务方法              |
| `NOT_SUPPORTED` | 非事务执行，挂起当前事务       | 长时间非事务操作            |
| `NEVER`         | 非事务执行，存在事务则抛异常     | 禁止事务场景              |

**示例**：
```java
// 独立日志事务
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void logOperation(String message) {
    logRepository.save(new Log(message));
}
```

## 3. 隔离级别与问题
| 隔离级别                       | 脏读 | 不可重复读 | 幻读 | 性能 | 适用场景        |
|----------------------------|----|-------|----|----|-------------|
| `READ_UNCOMMITTED`         | ✔️ | ✔️    | ✔️ | 最高 | 对一致性要求低     |
| `READ_COMMITTED`（Oracle默认） | ❌  | ✔️    | ✔️ | 中  | 避免脏读        |
| `REPEATABLE_READ`（MySQL默认） | ❌  | ❌     | ✔️ | 中  | 避免脏读和不可重复读  |
| `SERIALIZABLE`             | ❌  | ❌     | ❌  | 最低 | 强一致性要求（如金融） |

**问题说明**：
- **脏读**：读取未提交数据（如事务A回滚，事务B读到无效数据）。
- **不可重复读**：同一事务内多次读取同一数据结果不一致。
- **幻读**：范围查询结果因其他事务插入/删除而变化。

**配置示例**：
```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void updateBalance(Account account) {
    // 业务逻辑
}
```

## 4. 事务失效场景与解决方案
| 场景        | 原因                               | 解决方案                                                                                |
|-----------|----------------------------------|-------------------------------------------------------------------------------------|
| 非public方法 | AOP代理仅拦截public方法                 | 将方法改为public                                                                         |
| 自调用问题     | 类内部方法调用不经过代理                     | 注入自身代理或使用`AopContext.currentProxy()`                                                |
| 异常被捕获未抛出  | 事务默认仅回滚`RuntimeException`        | 捕获后重新抛出异常或调用`TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()` |
| 错误异常类型    | 检查型异常（如IOException）不触发回滚         | 通过`rollbackFor`指定回滚异常（如`@Transactional(rollbackFor = IOException.class)`）           |
| 数据库不支持事务  | 表引擎为MyISAM等非事务型                  | 切换为InnoDB等事务型引擎                                                                     |
| 事务管理器未配置  | 缺少`@EnableTransactionManagement` | 配置事务管理器并启用注解                                                                        |
| 多线程调用     | 事务绑定线程，跨线程事务失效                   | 避免多线程操作事务，或使用线程同步                                                                   |

**示例修复**：
```java
// 自调用问题修复
@Service
public class OrderService {
    @Autowired private OrderService self; // 注入自身代理
    
    public void createOrder() {
        self.saveOrder(); // 通过代理调用
    }
    
    @Transactional
    public void saveOrder() {
        // 业务逻辑
    }
}
```

## 5. 最佳实践
- **优先声明式事务**：减少代码侵入，提升可维护性。
- **合理选择传播行为和隔离级别**：根据业务需求（如性能、一致性）权衡。
- **避免自调用**：通过代理对象调用事务方法。
- **异常处理**：明确回滚异常类型，避免捕获后不抛出。
- **数据库兼容性**：确认数据库支持指定隔离级别和事务特性。

通过系统掌握事务管理机制，可有效保障数据一致性，避免常见失效陷阱。