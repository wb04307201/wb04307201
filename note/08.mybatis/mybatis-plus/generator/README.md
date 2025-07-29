# MyBatis-Plus Generator ：自动生成代码的利器

## 一、简介
MyBatis-Plus Generator 是 MyBatis-Plus 提供的代码生成器，能够快速生成 Entity、Mapper、Service、Controller 等层代码，极大提升开发效率，避免重复劳动。

## 二、核心功能
1. **自动生成实体类**：基于数据库表生成对应的 Java Bean
2. **生成 Mapper 接口**：包含基础 CRUD 方法
3. **生成 XML 映射文件**：包含 SQL 语句
4. **生成 Service 层**：基础业务逻辑接口和实现
5. **生成 Controller 层**：RESTful API 接口

## 三、快速入门

### 1. 添加依赖
```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-generator</artifactId>
    <version>最新版本</version>
</dependency>
<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.31</version> <!-- 模板引擎 -->
</dependency>
```

### 2. 基础配置示例
```java
public class CodeGenerator {
    public static void main(String[] args) {
        // 数据源配置
        DataSourceConfig dsc = new DataSourceConfig.Builder(
                "jdbc:mysql://localhost:3306/your_db",
                "username",
                "password")
                .build();

        // 全局配置
        GlobalConfig gc = new GlobalConfig.Builder()
                .outputDir(System.getProperty("user.dir") + "/src/main/java") // 输出目录
                .author("yourname") // 作者
                .enableSwagger() // 开启swagger注解
                .dateType(DateType.ONLY_DATE) // 时间策略
                .build();

        // 包配置
        PackageConfig pc = new PackageConfig.Builder()
                .parent("com.example") // 父包名
                .moduleName("system") // 模块名
                .pathInfo(Collections.singletonMap(OutputFile.xml, 
                        System.getProperty("user.dir") + "/src/main/resources/mapper")) // XML文件路径
                .build();

        // 策略配置
        StrategyConfig strategy = new StrategyConfig.Builder()
                .addInclude("table1", "table2") // 需要生成的表名
                .addTablePrefix("t_", "sys_") // 表前缀过滤
                .entityBuilder()
                    .enableLombok() // 开启lombok
                    .enableChainModel() // 开启链式模型
                    .versionColumnName("version") // 乐观锁字段
                .serviceBuilder()
                    .formatServiceFileName("%sService") // 格式化service接口名称
                .controllerBuilder()
                    .enableRestStyle() // 开启rest风格
                .build();

        // 代码生成器
        AutoGenerator generator = new AutoGenerator(dsc);
        generator.global(gc);
        generator.packageInfo(pc);
        generator.strategy(strategy);
        generator.templateEngine(new FreemarkerTemplateEngine()); // 使用Freemarker引擎
        generator.execute();
    }
}
```

## 四、高级配置

### 1. 自定义模板
1. 在 `resources/templates` 下创建自定义模板
2. 配置生成器使用自定义模板：
```java
generator.template(new TemplateConfig.Builder()
        .entity("/templates/entity.java")
        .mapper("/templates/mapper.java")
        .build());
```

### 2. 字段类型转换
```java
strategy.strategyConfig()
    .typeConvert(new ITypeConvert() {
        @Override
        public IColumnType processTypeConvert(GlobalConfig globalConfig, String fieldType) {
            // 自定义类型转换逻辑
            if (fieldType.toLowerCase().contains("bit")) {
                return DbColumnType.BOOLEAN;
            }
            return null; // 返回null表示使用默认转换
        }
    });
```

### 3. 字段注解配置
```java
strategy.entityBuilder()
    .addTableFills(new Column("create_time", FieldFill.INSERT)) // 插入时自动填充
    .addTableFills(new Column("update_time", FieldFill.INSERT_UPDATE)) // 插入和更新时填充
    .addIgnoreColumns("delete_flag"); // 忽略字段
```

## 五、常用注解说明

1. **实体类注解**：
  - `@TableName`：指定表名
  - `@TableId`：指定主键
  - `@TableField`：指定字段名
  - `@Version`：乐观锁版本号
  - `@LogicDelete`：逻辑删除字段

2. **Mapper 注解**：
  - `@Mapper`：标识为MyBatis Mapper接口
  - `@Select`、`@Insert`等：SQL注解（生成器默认使用XML方式）

## 六、最佳实践

1. **分层生成**：建议只生成Entity和Mapper，Service和Controller手动编写更灵活
2. **版本控制**：生成的代码建议纳入版本控制，便于团队同步
3. **模板定制**：根据项目规范定制模板，保持代码风格统一
4. **多环境配置**：不同环境使用不同的配置文件
5. **增量生成**：修改配置后只生成新增表，避免覆盖已有修改

## 七、常见问题

1. **生成代码不完整**：检查策略配置中的表名是否正确
2. **中文乱码**：确保数据库连接字符串包含 `useUnicode=true&characterEncoding=UTF-8`
3. **Lombok不生效**：检查IDE是否安装了Lombok插件
4. **Swagger注解缺失**：确保添加了Swagger依赖
5. **XML文件位置错误**：检查PackageConfig中的pathInfo配置

## 八、扩展工具

1. **MyBatisX**：IDEA插件，可视化生成代码
2. **MyBatis-Plus Generator UI**：提供Web界面操作生成代码
3. **结合Velocity模板**：替代Freemarker，提供更多语法支持

通过合理使用MyBatis-Plus Generator，可以显著减少重复编码工作，让开发者更专注于业务逻辑实现。建议根据项目实际情况调整配置，形成适合团队的代码生成规范。

## 一、简介
MyBatis-Plus Generator 是 MyBatis-Plus 提供的代码生成器，能够快速生成 Entity、Mapper、Service、Controller 等层代码，极大提升开发效率，避免重复劳动。

## 二、核心功能
1. **自动生成实体类**：基于数据库表生成对应的 Java Bean
2. **生成 Mapper 接口**：包含基础 CRUD 方法
3. **生成 XML 映射文件**：包含 SQL 语句
4. **生成 Service 层**：基础业务逻辑接口和实现
5. **生成 Controller 层**：RESTful API 接口

## 三、快速入门

### 1. 添加依赖
```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-generator</artifactId>
    <version>最新版本</version>
</dependency>
<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.31</version> <!-- 模板引擎 -->
</dependency>
```

### 2. 基础配置示例
```java
public class CodeGenerator {
    public static void main(String[] args) {
        // 数据源配置
        DataSourceConfig dsc = new DataSourceConfig.Builder(
                "jdbc:mysql://localhost:3306/your_db",
                "username",
                "password")
                .build();

        // 全局配置
        GlobalConfig gc = new GlobalConfig.Builder()
                .outputDir(System.getProperty("user.dir") + "/src/main/java") // 输出目录
                .author("yourname") // 作者
                .enableSwagger() // 开启swagger注解
                .dateType(DateType.ONLY_DATE) // 时间策略
                .build();

        // 包配置
        PackageConfig pc = new PackageConfig.Builder()
                .parent("com.example") // 父包名
                .moduleName("system") // 模块名
                .pathInfo(Collections.singletonMap(OutputFile.xml, 
                        System.getProperty("user.dir") + "/src/main/resources/mapper")) // XML文件路径
                .build();

        // 策略配置
        StrategyConfig strategy = new StrategyConfig.Builder()
                .addInclude("table1", "table2") // 需要生成的表名
                .addTablePrefix("t_", "sys_") // 表前缀过滤
                .entityBuilder()
                    .enableLombok() // 开启lombok
                    .enableChainModel() // 开启链式模型
                    .versionColumnName("version") // 乐观锁字段
                .serviceBuilder()
                    .formatServiceFileName("%sService") // 格式化service接口名称
                .controllerBuilder()
                    .enableRestStyle() // 开启rest风格
                .build();

        // 代码生成器
        AutoGenerator generator = new AutoGenerator(dsc);
        generator.global(gc);
        generator.packageInfo(pc);
        generator.strategy(strategy);
        generator.templateEngine(new FreemarkerTemplateEngine()); // 使用Freemarker引擎
        generator.execute();
    }
}
```

## 四、高级配置

### 1. 自定义模板
1. 在 `resources/templates` 下创建自定义模板
2. 配置生成器使用自定义模板：
```java
generator.template(new TemplateConfig.Builder()
        .entity("/templates/entity.java")
        .mapper("/templates/mapper.java")
        .build());
```

### 2. 字段类型转换
```java
strategy.strategyConfig()
    .typeConvert(new ITypeConvert() {
        @Override
        public IColumnType processTypeConvert(GlobalConfig globalConfig, String fieldType) {
            // 自定义类型转换逻辑
            if (fieldType.toLowerCase().contains("bit")) {
                return DbColumnType.BOOLEAN;
            }
            return null; // 返回null表示使用默认转换
        }
    });
```

### 3. 字段注解配置
```java
strategy.entityBuilder()
    .addTableFills(new Column("create_time", FieldFill.INSERT)) // 插入时自动填充
    .addTableFills(new Column("update_time", FieldFill.INSERT_UPDATE)) // 插入和更新时填充
    .addIgnoreColumns("delete_flag"); // 忽略字段
```

## 五、常用注解说明

1. **实体类注解**：
  - `@TableName`：指定表名
  - `@TableId`：指定主键
  - `@TableField`：指定字段名
  - `@Version`：乐观锁版本号
  - `@LogicDelete`：逻辑删除字段

2. **Mapper 注解**：
  - `@Mapper`：标识为MyBatis Mapper接口
  - `@Select`、`@Insert`等：SQL注解（生成器默认使用XML方式）

## 六、最佳实践

1. **分层生成**：建议只生成Entity和Mapper，Service和Controller手动编写更灵活
2. **版本控制**：生成的代码建议纳入版本控制，便于团队同步
3. **模板定制**：根据项目规范定制模板，保持代码风格统一
4. **多环境配置**：不同环境使用不同的配置文件
5. **增量生成**：修改配置后只生成新增表，避免覆盖已有修改

## 七、常见问题

1. **生成代码不完整**：检查策略配置中的表名是否正确
2. **中文乱码**：确保数据库连接字符串包含 `useUnicode=true&characterEncoding=UTF-8`
3. **Lombok不生效**：检查IDE是否安装了Lombok插件
4. **Swagger注解缺失**：确保添加了Swagger依赖
5. **XML文件位置错误**：检查PackageConfig中的pathInfo配置

## 八、扩展工具

1. **MyBatisX**：IDEA插件，可视化生成代码
2. **MyBatis-Plus Generator UI**：提供Web界面操作生成代码
3. **结合Velocity模板**：替代Freemarker，提供更多语法支持

通过合理使用MyBatis-Plus Generator，可以显著减少重复编码工作，让开发者更专注于业务逻辑实现。建议根据项目实际情况调整配置，形成适合团队的代码生成规范。