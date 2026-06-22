# 04 Lambda 条件构造器

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L153-162(§三.3 Lambda 构造器)

使用 Lambda 表达式可以避免字段名硬编码:

```java
LambdaQueryWrapper<User> lambdaWrapper = new LambdaQueryWrapper<>();
lambdaWrapper.eq(User::getName, "Tom")
             .gt(User::getAge, 20);
List<User> users = userMapper.selectList(lambdaWrapper);
```

> 进一步深入 LambdaQueryWrapper 背后的 SFunction 序列化原理,见 [05 LambdaQueryWrapper 中的 SFunction 序列化原理](./05-lambda-sfunction-deep-dive.md)。
