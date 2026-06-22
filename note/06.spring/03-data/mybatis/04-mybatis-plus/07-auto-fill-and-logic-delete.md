# 07 自动填充与逻辑删除

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L196-241(§三.5 自动填充 + §三.6 逻辑删除)

## 7.1 自动填充功能

### 创建 MetaObjectHandler 实现类

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

## 7.2 逻辑删除

### 实体类添加注解

```java
@Data
@TableName("user")
public class User {
    // 其他字段...

    @TableLogic // 逻辑删除注解
    private Integer deleted; // 0-未删除 1-已删除
}
```

### 配置逻辑删除值

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted  # 全局逻辑删除的实体字段名
      logic-not-delete-value: 0    # 逻辑未删除值(默认为 0)
      logic-delete-value: 1        # 逻辑已删除值(默认为 1)
```
