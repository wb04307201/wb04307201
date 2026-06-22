# 01 框架本质与三层架构

> 来源:整合自原 08.mybatis/README.md § 一

### 1.1 框架本质
MyBatis 是基于 **ORM（对象关系映射）** 思想的半自动持久层框架，其核心价值在于：
- **SQL 定制化**：允许开发者直接编写原生 SQL，支持存储过程、动态 SQL 生成
- **JDBC 封装**：自动管理 Connection/Statement/ResultSet 生命周期，消除样板代码
- **映射引擎**：通过 XML/注解实现 Java 对象与数据库表的双向映射

### 1.2 三层架构
- **Controller**：接收 HTTP 请求，调用 Service 层
- **Service**：实现业务逻辑，协调多个 Dao 操作
- **Dao**：定义数据访问接口，由 MyBatis 动态实现