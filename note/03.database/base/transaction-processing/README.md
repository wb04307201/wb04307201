# 事务处理

## 事务处理的四个特性ACID

![img.png](img.png)

![img_1.png](img_1.png)

### Atomicity原子性

![img_2.png](img_2.png)

### Consistency一致性

![img_3.png](img_3.png)

### lsolation隔离性

#### 脏读（Dirty read）

![img_4.png](img_4.png)

![img_5.png](img_5.png)

#### 丢失修改（Lost to modify）

![img_6.png](img_6.png)

#### 不可重复读（Unrepeatable read）

![img_7.png](img_7.png)

#### 幻读（Phantom read）

![img_8.png](img_8.png)

![img_9.png](img_9.png)

#### 事务隔离级别

![img_10.png](img_10.png)

> - **READ-UNCOMMITTED(读取未提交)**：最低的隔离级别，允许读取尚未提交的数据变更，可能会导致脏读、幻读或不可重复读。
> - **READ-COMMITTED(读取已提交)**：允许读取并发事务已经提交的数据，可以阻止脏读，但是幻读或不可重复读仍有可能发生。
> - **REPEATABLE-READ(可重复读)**：对同一字段的多次读取结果都是一致的，除非数据是被本身事务自己所修改，可以阻止脏读和不可重复读，但幻读仍有可能发生。
> - **SERIALIZABLE(可串行化)**：最高的隔离级别，完全服从`ACID`的隔离级别。所有的事务依次逐个执行，这样事务之间就完全不可能产生干扰，也就是说，该级别可以防止脏读、不可重复读以及幻读。

| 事务隔离级别                  | 脏读 | 不可重复读 | 幻读 |
|-------------------------|----|-------|----|
| READ-UNCOMMITTED(读取未提交) | √  | √     | √  |
| READ-COMMITTED(读取已提交)   | ×  | √     | √  |
| REPEATABLE-READ(可重复读)   | ×  | ×     | √  |
| SERIALIZABLE(可串行化)      | ×  | ×     | ×  |

### Durability持久性

![img_11.png](img_11.png)

## 并发事务的控制方式

### 锁


### MVCC




