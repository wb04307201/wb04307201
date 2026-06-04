# 幂等设计

幂等性（Idempotence）是分布式系统和API设计中的核心概念，指**对同一操作的多次重复执行与单次执行的效果完全一致**。在不可靠的网络、重复请求或并发操作的场景下，幂等性设计能避免数据不一致、重复扣款等严重问题。以下是幂等性设计的关键要点、实现方案及案例分析。

## 幂等性的核心价值
### 1. 解决的典型问题
- **网络重试**：HTTP请求超时后客户端重试，可能导致服务端重复处理。
- **消息队列重复消费**：如Kafka/RabbitMQ消费者崩溃后重启，可能重新消费消息。
- **用户重复操作**：如用户多次点击提交按钮，或前端防抖失效。
- **分布式事务**：如TCC（Try-Confirm-Cancel）模式中Confirm阶段重复调用。

### 2. 业务场景示例
- **支付系统**：用户重复点击支付按钮，应只扣款一次。
- **订单系统**：创建订单接口被重复调用，应返回相同订单号而非生成新订单。
- **库存系统**：减库存操作被重复执行，应避免超卖。

## 幂等性实现方案
### 1. 基于唯一标识（Idempotency Key）
#### 实现原理
- 客户端为每个请求生成唯一ID（如UUID、订单号+时间戳），服务端通过该ID去重。
- **适用场景**：写操作（创建、更新、删除）。

#### 技术实现
- **Redis缓存**：
    - 将`IdempotencyKey`作为Key，存储请求处理结果或状态（如`SUCCESS`/`PROCESSING`）。
    - **示例代码（Java + Redis）**：
      ```java
      public Response handleRequest(Request request, String idempotencyKey) {
          String cacheKey = "IDEMPOTENT:" + idempotencyKey;
          String cachedResult = redis.get(cacheKey);
          if (cachedResult != null) {
              return deserialize(cachedResult); // 直接返回缓存结果
          }
          
          // 业务处理逻辑
          Response response = processBusiness(request);
          
          // 缓存结果（设置过期时间，避免长期占用内存）
          redis.setex(cacheKey, 3600, serialize(response));
          return response;
      }
      ```

- **数据库唯一索引**：
    - 在表中添加唯一约束（如`UNIQUE (order_id, operation_type)`），重复插入时抛出异常。
    - **示例SQL**：
      ```sql
      CREATE TABLE payment_records (
          id BIGINT PRIMARY KEY,
          order_id VARCHAR(32) NOT NULL,
          operation_type VARCHAR(16) NOT NULL,
          amount DECIMAL(10,2),
          UNIQUE (order_id, operation_type) -- 确保同一订单的同一操作只能执行一次
      );
      ```

### 2. 基于Token机制
#### 实现原理
- 服务端预先生成一次性Token（如JWT、雪花ID），客户端携带Token发起请求，服务端校验后销毁Token。
- **适用场景**：防重复提交表单、敏感操作。

#### 技术实现
- **Token生成与校验**：
    - 服务端在返回表单页面时生成Token，存入Redis（设置短过期时间，如5分钟）。
    - 客户端提交表单时携带Token，服务端校验存在后删除Token并处理请求。
    - **示例流程**：
      ```plantuml
      @startuml TokenFlow
      participant "Client" as client
      participant "Server" as server
  
      client -> server : GET /form (获取表单+Token)
      server --> client : HTML + Token=xyz123
      client -> server : POST /submit (表单数据+Token=xyz123)
      alt Token有效
          server --> server : 删除Token=xyz123
          server --> client : 成功响应
      else Token无效
          server --> client : 错误提示（请勿重复提交）
      end
      @enduml
      ```

### 3. 基于乐观锁
#### 实现原理
- 通过版本号（Version）或时间戳（Timestamp）控制并发更新，确保重复更新不会覆盖数据。
- **适用场景**：并发更新同一资源（如库存、用户余额）。

#### 技术实现
- **数据库乐观锁**：
    - 在表中添加`version`字段，更新时检查版本号是否匹配。
    - **示例SQL**：
      ```sql
      UPDATE inventory 
      SET quantity = quantity - 1, version = version + 1 
      WHERE product_id = 1001 AND version = 5; -- 仅当版本为5时更新
      ```
    - **影响行数检查**：若返回0，说明版本已变更，需重试或报错。

### 4. 基于状态机
#### 实现原理
- 定义操作的合法状态转移路径，重复执行时根据当前状态决定是否允许操作。
- **适用场景**：订单状态流转（如“待支付”→“已支付”）。

#### 技术实现
- **枚举状态与转移规则**：
  ```java
  public enum OrderStatus {
      CREATED, PAID, CANCELLED;
      
      public boolean canTransitionTo(OrderStatus newStatus) {
          switch (this) {
              case CREATED: return newStatus == PAID || newStatus == CANCELLED;
              case PAID: return false; // 已支付订单不可再次支付
              case CANCELLED: return false;
              default: return false;
          }
      }
  }
  ```
- **状态校验逻辑**：
  ```java
  public void payOrder(Long orderId) {
      Order order = orderRepository.findById(orderId);
      if (!order.getStatus().canTransitionTo(OrderStatus.PAID)) {
          throw new IllegalStateException("订单状态不允许支付");
      }
      // 执行支付逻辑...
  }
  ```

### 5. 去重表（Deduplication Table）
#### 实现原理
- 单独维护一张去重表，记录已处理的请求标识（如消息ID、事务ID）。
- **适用场景**：消息队列消费、异步任务处理。

#### 技术实现
- **MySQL去重表**：
  ```sql
  CREATE TABLE deduplication_log (
      id BIGINT AUTO_INCREMENT PRIMARY KEY,
      message_id VARCHAR(64) NOT NULL UNIQUE, -- 消息唯一ID
      processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX (message_id)
  );
  ```
- **消费逻辑**：
  ```java
  public void consumeMessage(String messageId, String payload) {
      if (deduplicationRepo.existsByMessageId(messageId)) {
          return; // 跳过已处理消息
      }
      // 业务处理...
      deduplicationRepo.save(new DeduplicationLog(messageId));
  }
  ```

---

## 幂等性设计案例
### 案例1：支付接口幂等性
#### 场景
用户重复点击支付按钮，需确保只扣款一次。

#### 解决方案
1. **客户端**：生成`payment_request_id`（UUID），携带在支付请求中。
2. **服务端**：
    - 查询数据库是否存在相同`payment_request_id`的记录：
        - 存在：返回原支付结果。
        - 不存在：执行扣款，并插入记录（包含`payment_request_id`、订单号、金额等）。
3. **数据库表设计**：
   ```sql
   CREATE TABLE payment_records (
       id BIGINT PRIMARY KEY,
       payment_request_id VARCHAR(64) NOT NULL UNIQUE, -- 幂等键
       order_id VARCHAR(32) NOT NULL,
       amount DECIMAL(10,2),
       status ENUM('PENDING', 'SUCCESS', 'FAILED'),
       INDEX (payment_request_id)
   );
   ```

### 案例2：库存扣减幂等性
#### 场景
高并发下减库存，避免超卖。

#### 解决方案
1. **数据库乐观锁**：
   ```sql
   UPDATE inventory 
   SET quantity = quantity - 1 
   WHERE product_id = 1001 AND quantity >= 1;
   ```
    - 检查影响行数，若为0则抛出异常（库存不足或并发冲突）。
2. **Redis分布式锁（可选）**：
    - 对商品ID加锁，确保同一时间只有一个请求能操作库存。
    - **示例代码（Redisson）**：
      ```java
      RLock lock = redisson.getLock("inventory:lock:1001");
      try {
          lock.lock();
          // 执行数据库减库存逻辑
      } finally {
          lock.unlock();
      }
      ```

---

## 幂等性设计注意事项
1. **性能权衡**：
    - 唯一标识校验可能增加数据库查询或Redis访问，需评估QPS影响。
2. **过期清理**：
    - 幂等记录（如Redis中的`IdempotencyKey`）需设置过期时间，避免内存泄漏。
3. **分布式事务**：
    - 幂等性不能替代分布式事务，需结合TCC、Saga等模式处理复杂场景。
4. **测试覆盖**：
    - 通过压测工具（如JMeter）模拟重复请求，验证幂等性是否生效。

---

## 总结

| **方案**                | **适用场景**  | **优点**        | **缺点**       |
|-----------------------|-----------|---------------|--------------|
| 唯一标识（Idempotency Key） | 写操作、API接口 | 实现简单，通用性强     | 需存储幂等记录，占用资源 |
| Token机制               | 防重复提交表单   | 安全性高，防止CSRF攻击 | 需管理Token生命周期 |
| 乐观锁                   | 并发更新数据    | 无锁竞争，性能好      | 需处理冲突重试      |
| 状态机                   | 订单状态流转    | 业务逻辑清晰        | 状态定义需覆盖所有场景  |
| 去重表                   | 消息队列消费    | 独立存储，不影响主业务   | 需额外维护表结构     |

根据业务场景选择合适的方案，或组合使用（如唯一标识+乐观锁），可构建高可靠的幂等系统。