# 02 CRUD 与条件构造器基础

> 来源:整合自原 `08.mybatis/mybatis-plus/README.md` L83-151(§三.1 CRUD + §三.2 条件构造器基础)

## 2.1 插入数据

```java
User user = new User();
user.setName("Tom");
user.setAge(25);
userMapper.insert(user); // 返回插入的记录数
```

## 2.2 更新数据

```java
User user = new User();
user.setId(1L);
user.setName("Jerry");
userMapper.updateById(user); // 根据ID更新
```

## 2.3 查询数据

```java
// 根据ID查询
User user = userMapper.selectById(1L);

// 查询所有
List<User> users = userMapper.selectList(null);

// 条件查询
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("name", "Tom").gt("age", 20);
List<User> users = userMapper.selectList(wrapper);
```

## 2.4 删除数据

```java
// 根据ID删除
userMapper.deleteById(1L);

// 条件删除
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("name", "Tom");
userMapper.delete(wrapper);
```

## 2.5 Wrapper 常用方法

MyBatis-Plus 提供了两种条件构造器:
- `QueryWrapper`:用于查询条件构造
- `UpdateWrapper`:用于更新条件构造

```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("column", value)       // 等于 =
      .ne("column", value)       // 不等于 <>
      .gt("column", value)       // 大于 >
      .ge("column", value)       // 大于等于 >=
      .lt("column", value)       // 小于 <
      .le("column", value)       // 小于等于 <=
      .between("column", v1, v2) // BETWEEN 值1 AND 值2
      .like("column", value)     // LIKE '%值%'
      .likeLeft("column", value) // LIKE '%值'
      .likeRight("column", value)// LIKE '值%'
      .in("column", list)       // IN (value.get(0),value.get(1),...)
      .isNull("column")         // 字段 IS NULL
      .isNotNull("column")      // 字段 IS NOT NULL
      .orderByAsc("column")      // 排序:ORDER BY 字段,... ASC
      .orderByDesc("column")     // 排序:ORDER BY 字段,... DESC
```
