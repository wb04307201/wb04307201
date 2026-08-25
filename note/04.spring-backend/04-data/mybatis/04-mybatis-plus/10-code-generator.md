<!--
module:
  parent: 04.spring-backend
  slug: 04.spring-backend\04-data\mybatis\04-mybatis-plus\10-code-generator
  type: article
  category: 主模块子文章
  summary: 10 代码生成器
-->

# 10 代码生成器

> 来源:整合自原 `08.mybatis/mybatis-plus/generator/README.md` L1-152（**已去重**：原文件 L153-300 为全文重复，已剔除）

MyBatis-Plus Generator（`AutoGenerator`）从 3.5.3 起改为**全 Builder 链式调用**，配合 FreeMarker / Velocity / Beetl 模板引擎一键生成 Entity、Mapper、Service、ServiceImpl、Controller、Mapper.xml 六类文件。本章给出**生产可运行**的生成器（含 application.yml、Generator 主类、自定义模板、类型转换、字段注解）以及生成后的样例代码，团队接手即可落地。

---

## 一、Maven 依赖

```xml
<dependencies>
    <!-- MyBatis-Plus 启动器（含核心 + 分页/自动填充） -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.7</version>
    </dependency>

    <!-- 代码生成器（核心 jar） -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-generator</artifactId>
        <version>3.5.7</version>
    </dependency>

    <!-- 模板引擎（任选其一，推荐 FreeMarker） -->
    <dependency>
        <groupId>org.freemarker</groupId>
        <artifactId>freemarker</artifactId>
        <version>2.3.32</version>
    </dependency>

    <!-- 数据库驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.3.0</version>
    </dependency>
</dependencies>
```

---

## 二、application.yml（运行时配置）

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.example.demo.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    banner: false
    db-config:
      id-type: ASSIGN_ID
      logic-delete-field: deleted
      logic-not-delete-value: 0
      logic-delete-value: 1
      insert-strategy: not_null
      update-strategy: not_null
```

---

## 三、完整可运行的 Generator 主类

```java
package com.example.generator;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.*;
import com.baomidou.mybatisplus.generator.config.converts.MySqlTypeConvert;
import com.baomidou.mybatisplus.generator.config.rules.DateType;
import com.baomidou.mybatisplus.generator.config.rules.NamingStrategy;
import com.baomidou.mybatisplus.generator.engine.FreemarkerTemplateEngine;
import com.baomidou.mybatisplus.generator.fill.Column;
import com.baomidou.mybatisplus.generator.keywords.MySqlKeyWordsHandler;

import java.util.Arrays;

public class CodeGenerator {

    public static void main(String[] args) {
        String url      = "jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai";
        String username = "root";
        String password = "root";
        String parent   = "com.example.demo";
        String module   = "system";
        String author   = "wubo";
        String[] tables = {"sys_user", "sys_role", "sys_menu"};   // 要生成的表

        FastAutoGenerator.create(url, username, password)
            // ===== 全局配置 =====
            .globalConfig(builder -> builder
                .outputDir(System.getProperty("user.dir") + "/src/main/java")
                .author(author)
                .enableSwagger()
                .dateType(DateType.TIME_PACK)
                .commentDate("yyyy-MM-dd")
                .disableOpenDir()
            )
            // ===== 包配置 =====
            .packageConfig(builder -> builder
                .parent(parent)
                .moduleName(module)
                .entity("entity")
                .mapper("mapper")
                .service("service")
                .serviceImpl("service.impl")
                .controller("controller")
                .xml("mapper.xml")
                .pathInfo(path -> path
                    .setOutputMapXml(System.getProperty("user.dir") + "/src/main/resources/mapper"))
            )
            // ===== 策略配置 =====
            .strategyConfig(builder -> builder
                .addInclude(tables)
                .addTablePrefix("sys_")                  // 过滤表前缀
                .enableSkipView()
                .entityBuilder()
                    .superClass(BaseEntity.class)        // 父类（公共字段）
                    .enableLombok()
                    .enableChainModel()
                    .enableTableFieldAnnotation()
                    .idType(IdType.ASSIGN_ID)
                    .versionColumnName("version")
                    .logicDeleteColumnName("deleted")
                    .addTableFills(
                        new Column("create_time", FieldFill.INSERT),
                        new Column("update_time", FieldFill.INSERT_UPDATE),
                        new Column("create_by",   FieldFill.INSERT),
                        new Column("update_by",   FieldFill.INSERT_UPDATE))
                    .naming(NamingStrategy.underline_to_camel)
                    .columnNaming(NamingStrategy.underline_to_camel)
                    .formatFileName("%sEntity")         // User → UserEntity
                .mapperBuilder()
                    .superClass(BaseMapper.class)
                    .enableBaseResultMap()
                    .enableBaseColumnList()
                    .formatMapperFileName("%sMapper")
                    .formatXmlFileName("%sMapper")
                .serviceBuilder()
                    .formatServiceFileName("I%sService")
                    .formatServiceImplFileName("%sServiceImpl")
                .controllerBuilder()
                    .superClass(BaseController.class)
                    .enableRestStyle()
                    .enableHyphenStyle()
                    .formatFileName("%sController")
            )
            // ===== 模板引擎 =====
            .templateEngine(new FreemarkerTemplateEngine())
            // ===== 自定义类型转换 =====
            .templateConfig(builder -> builder
                .entity("/templates/entity.java")
                .mapper("/templates/mapper.java")
                .service("/templates/service.java")
                .serviceImpl("/templates/serviceImpl.java")
                .controller("/templates/controller.java")
                .mapperXml("/templates/mapper.xml")
            )
            // ===== 数据源配置（可选） =====
            .dataSourceConfig(builder -> builder
                .typeConvert(new MySqlTypeConvert())
                .keywordsHandler(new MySqlKeyWordsHandler())
            )
            .execute();
    }
}
```

---

## 四、生成结果示例（User 表）

### 4.1 Entity

```java
package com.example.demo.system.entity;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@Accessors(chain = true)
@TableName("sys_user")
@ApiModel(value = "SysUser对象", description = "系统用户表")
public class SysUserEntity extends BaseEntity {

    @ApiModelProperty("主键ID")
    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;

    @ApiModelProperty("用户名")
    private String username;

    @ApiModelProperty("密码（BCrypt）")
    private String password;

    @ApiModelProperty("昵称")
    private String nickname;

    @ApiModelProperty("邮箱")
    private String email;

    @ApiModelProperty("手机号")
    private String phone;

    @ApiModelProperty("状态：0-禁用 1-正常")
    private Integer status;

    @ApiModelProperty("版本号（乐观锁）")
    @Version
    private Integer version;

    @ApiModelProperty("逻辑删除：0-未删 1-已删")
    @TableLogic
    private Integer deleted;

    @ApiModelProperty("创建时间")
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @ApiModelProperty("更新时间")
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @ApiModelProperty("创建人")
    @TableField(fill = FieldFill.INSERT)
    private Long createBy;

    @ApiModelProperty("更新人")
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updateBy;
}
```

### 4.2 Mapper

```java
package com.example.demo.system.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.system.entity.SysUserEntity;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUserEntity> {
    // BaseMapper 已提供 17 个 CRUD 方法
}
```

```xml
<!-- resources/mapper/SysUserMapper.xml（自动生成） -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.demo.system.mapper.SysUserMapper">

    <resultMap id="BaseResultMap" type="com.example.demo.system.entity.SysUserEntity">
        <id property="id"          column="id" />
        <result property="username"  column="username" />
        <result property="password"  column="password" />
        <result property="createTime" column="create_time" />
        <result property="updateTime" column="update_time" />
        <!-- ... -->
    </resultMap>

    <sql id="Base_Column_List">
        id, username, password, nickname, email, phone, status, version,
        deleted, create_time, update_time, create_by, update_by
    </sql>
</mapper>
```

### 4.3 Service

```java
package com.example.demo.system.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.demo.system.entity.SysUserEntity;

public interface ISysUserService extends IService<SysUserEntity> {
    // IService 提供 17 个批量 / 链式方法
}
```

```java
package com.example.demo.system.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.demo.system.entity.SysUserEntity;
import com.example.demo.system.mapper.SysUserMapper;
import com.example.demo.system.service.ISysUserService;
import org.springframework.stereotype.Service;

@Service
public class SysUserServiceImpl
       extends ServiceImpl<SysUserMapper, SysUserEntity>
       implements ISysUserService {
    // ServiceImpl 已提供 save / saveBatch / updateById / list / page 等全部方法
    // 业务方法写在 override 下方
}
```

### 4.4 Controller

```java
package com.example.demo.system.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.demo.system.entity.SysUserEntity;
import com.example.demo.system.service.ISysUserService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/system/user")
@Api(tags = "用户管理")
public class SysUserController extends BaseController {

    @Autowired
    private ISysUserService userService;

    @GetMapping("/page")
    @ApiOperation("分页查询")
    public Page<SysUserEntity> page(@RequestParam(defaultValue = "1") Long current,
                                     @RequestParam(defaultValue = "10") Long size) {
        return userService.page(new Page<>(current, size));
    }

    @GetMapping("/{id}")
    @ApiOperation("详情")
    public SysUserEntity getById(@PathVariable Long id) {
        return userService.getById(id);
    }

    @PostMapping
    @ApiOperation("新增")
    public boolean save(@RequestBody SysUserEntity entity) {
        return userService.save(entity);
    }

    @PutMapping
    @ApiOperation("更新")
    public boolean update(@RequestBody SysUserEntity entity) {
        return userService.updateById(entity);
    }

    @DeleteMapping("/{id}")
    @ApiOperation("删除")
    public boolean delete(@PathVariable Long id) {
        return userService.removeById(id);
    }
}
```

---

## 五、自定义模板

### 5.1 模板位置

```text
src/main/resources/
└── templates/
    ├── entity.java
    ├── mapper.java
    ├── service.java
    ├── serviceImpl.java
    ├── controller.java
    └── mapper.xml
```

### 5.2 自定义模板要点（以 controller.java 为例）

```ftl
package ${package.Controller};

<#list importPackages as pkg>
import ${pkg};
</#list>

@RestController
@RequestMapping("/${table.entityPath}")
@Api(tags = "${table.comment!}")
public class ${table.controllerName} {

    @Autowired
    private ${table.serviceName} service;

    @GetMapping("/page")
    public Page<${entity}> page(@RequestParam(defaultValue = "1") Long current,
                                 @RequestParam(defaultValue = "10") Long size) {
        return service.page(new Page<>(current, size));
    }

    <#list table.fields as field>
    <#if field.keyFlag>
    @GetMapping("/{$column}")
    public ${entity} getById(@PathVariable ${field.propertyType} ${field.propertyName}) {
        return service.getById(${field.propertyName});
    }
    </#if>
    </#list>

    @PostMapping
    public boolean save(@RequestBody ${entity} entity) {
        return service.save(entity);
    }

    @DeleteMapping("/{id}")
    public boolean delete(@PathVariable Long id) {
        return service.removeById(id);
    }
}
```

**注册模板**：

```java
.templateConfig(builder -> builder
    .controller("/templates/controller.java")     // classpath: templates/controller.java
    .entity("/templates/entity.java")
)
```

---

## 六、字段类型转换（ITypeConvert）

数据库 `tinyint` 默认生成 `Integer`，可改为 `Boolean`：

```java
.dataSourceConfig(builder -> builder
    .typeConvert((globalConfig, fieldType) -> {
        String t = fieldType.toLowerCase();
        if (t.contains("tinyint")) {
            return DbColumnType.BOOLEAN;
        }
        if (t.contains("datetime")) {
            return DbColumnType.LOCAL_DATE_TIME;
        }
        if (t.contains("text")) {
            return DbColumnType.STRING;
        }
        return null;   // 用默认转换
    })
)
```

---

## 七、字段注解配置

```java
.entityBuilder()
    // 自动填充字段
    .addTableFills(new Column("create_time", FieldFill.INSERT))
    .addTableFills(new Column("update_time", FieldFill.INSERT_UPDATE))
    // 忽略字段（不生成到实体）
    .addIgnoreColumns("password", "salt")
    // 字段名映射（DB create_time → entity createdAt）
    .addFieldNamesMappings(Collections.singletonMap("create_time", "createdAt"))
    // 字段注解包（用于 Swagger / Validation）
    .addTableFills(new Column("email", FieldFill.INSERT))
    .addFieldAnnotations(Collections.singletonList(
        new Annotation.Builder()
            .name("NotBlank")
            .packages(Arrays.asList("javax.validation.constraints"))
            .build()))
```

---

## 八、多数据库支持

```java
DataSourceConfig dsc = new DataSourceConfig.Builder("jdbc:postgresql://localhost:5432/db", "user", "pwd")
    .dbType(DbType.POSTGRE_SQL)
    .schema("public")
    .build();
```

内置方言：`MySQL`、`POSTGRE_SQL`、`ORACLE`、`SQL_SERVER`、`DM`、`KINGBASE_ES`、`GBASE`。

---

## 九、增量生成策略

```java
// 只生成新增表，避免覆盖已有修改
.strategyConfig(builder -> builder
    .addInclude("sys_user", "sys_role")            // 表名
    .addExclude("flyway_schema_history")            // 排除 Flyway 历史表
)
```

**团队规范**：
1. 生成后立即 git commit（基线）
2. 业务修改手动编辑（差异化定制）
3. 后续如有新表，单独生成 → 单独 commit（增量）

---

## 十、常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 生成代码不完整 | 策略配置表名拼错 | `addInclude` 用小写表名 + 双引号检查 |
| 中文乱码 | JDBC URL 没设 charset | `?useUnicode=true&characterEncoding=UTF-8` |
| Lombok 不生效 | IDE 没装插件 | Settings → Plugins → Lombok |
| Swagger 注解缺失 | 没加 `enableSwagger()` | 全局配置开启 |
| XML 文件位置错 | `pathInfo` 没设 `outputMapXml` | 见第三节配置 |
| `created_time` 没填充 | 实体没标 `@TableField(fill=...)` | 配置 `addTableFills` |
| 主键冲突 | 用了 AUTO + 分库分表 | 改 `ASSIGN_ID` |
| 模板未生效 | classpath 路径错 | 放 `resources/templates/` |

---

## 十一、CI 集成建议

```xml
<!-- 配合 Maven profile 在 CI 中生成 -->
<profiles>
    <profile>
        <id>gen</id>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.codehaus.mojo</groupId>
                    <artifactId>exec-maven-plugin</artifactId>
                    <version>3.1.0</version>
                    <configuration>
                        <mainClass>com.example.generator.CodeGenerator</mainClass>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

```bash
mvn -Pgen exec:java
```

> **建议**：生成器只放开发仓库，**不进生产 JAR**。在 `.gitignore` 中忽略 Generator 包，团队成员本地生成各自提交。

---

## 反向链

- [`01-quickstart`](01-quickstart.md) — 生成后第一个 CRUD
- [`02-crud-basics`](02-crud-basics.md) — `BaseMapper` 17 个方法
- [`04-lambda-wrapper`](04-lambda-wrapper.md) — 链式条件

← [返回: MyBatis-Plus 全家桶](./README.md)