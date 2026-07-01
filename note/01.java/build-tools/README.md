<!--
module:
  parent: java
  slug: java/build-tools
  type: article
  category: 主模块子文章
  summary: Maven 与 Gradle 全方位对比：从坐标 / 依赖管理 / 多模块到生命周期与最佳实践。
-->

# Java 构建工具笔记

## 一、Maven vs Gradle 对比

| 维度 | Maven | Gradle |
|------|-------|--------|
| 配置文件 | XML（pom.xml） | Groovy / Kotlin DSL（build.gradle） |
| 约定 | 约定优于配置，结构固定 | 灵活配置，可自由定义 |
| 构建速度 | 较慢，每次全量执行 | 较快，支持增量构建、构建缓存、守护进程 |
| 依赖管理 | 通过 pom.xml 声明 | 通过 configurations 和 dependencies 块声明 |
| 插件生态 | 插件丰富，XML 配置繁琐 | 插件丰富，脚本式配置更简洁 |
| 学习曲线 | 入门简单，深入需要理解生命周期 | 入门需要理解 DSL 和任务图 |
| 多模块支持 | 支持，通过 parent pom | 支持，通过 includeBuild 和复合构建 |
| 适用场景 | 传统企业项目、结构稳定的项目 | 大型项目、需要定制构建逻辑的项目 |

---
---

## 二、Maven 核心概念

### 2.1 pom.xml 基础结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 坐标 GAV -->
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- 依赖声明 -->
    </dependencies>

    <build>
        <plugins>
            <!-- 插件声明 -->
        </plugins>
    </build>
</project>
```

### 2.2 Maven 坐标（GAV）

每个构件由三个坐标唯一标识：

| 坐标 | 说明 | 示例 |
|------|------|------|
| groupId | 组织/公司标识，通常用反向域名 | com.alibaba |
| artifactId | 项目/模块名称 | spring-core |
| version | 版本号，SNAPSHOT 表示快照版 | 5.3.21-SNAPSHOT |

扩展坐标还包括 `classifier`（分类器）和 `packaging`（打包方式）。

### 2.3 依赖声明

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.0</version>
    </dependency>

    <!-- 排除传递依赖 -->
    <dependency>
        <groupId>org.example</groupId>
        <artifactId>some-lib</artifactId>
        <version>1.0.0</version>
        <exclusions>
            <exclusion>
                <groupId>commons-logging</groupId>
                <artifactId>commons-logging</artifactId>
            </exclusion>
        </exclusions>
    </dependency>
</dependencies>
```

### 2.4 Maven 生命周期

Maven 有三套独立的生命周期，每个生命周期包含多个阶段（Phase）：

| 生命周期 | 阶段 | 说明 |
|----------|------|------|
| **clean** | pre-clean, clean, post-clean | 清理构建产物 |
| **default** | validate → compile → test → package → verify → install → deploy | 核心构建流程 |
| **site** | pre-site, site, post-site, site-deploy | 生成项目站点文档 |

常用命令：

```bash
mvn clean                    # 执行 clean 生命周期
mvn clean compile            # 清理后编译
mvn clean package            # 清理后打包
mvn clean install            # 安装到本地仓库
mvn clean deploy             # 部署到远程仓库
mvn test                     # 只执行测试
mvn package -DskipTests      # 打包但跳过测试
```

### 2.5 常用插件

```xml
<build>
    <plugins>
        <!-- 编译插件 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <configuration>
                <source>17</source>
                <target>17</target>
            </configuration>
        </plugin>

        <!-- Spring Boot 打包插件 -->
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <version>3.2.0</version>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>

        <!-- Surefire 测试插件 -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.2.2</version>
        </plugin>
    </plugins>
</build>
```

---

## 三、Maven 依赖范围

依赖范围（scope）控制依赖在什么时候、什么地方生效：

| 范围 | 编译 classpath | 测试 classpath | 运行 classpath | 是否传递 | 典型场景 |
|------|:---:|:---:|:---:|:---:|----------|
| compile（默认） | 是 | 是 | 是 | 是 | 大部分业务依赖 |
| provided | 是 | 是 | 否 | 否 | servlet-api、lombok（编译期） |
| runtime | 否 | 是 | 是 | 是 | JDBC 驱动（编译不需要） |
| test | 否 | 是 | 否 | 否 | JUnit、Mockito |
| system | 是 | 是 | 否 | 否 | 本地系统路径的 jar（不推荐） |

```xml
<dependencies>
    <!-- 编译期有效，运行期由容器提供 -->
    <dependency>
        <groupId>jakarta.servlet</groupId>
        <artifactId>jakarta.servlet-api</artifactId>
        <version>6.0.0</version>
        <scope>provided</scope>
    </dependency>

    <!-- 仅测试有效 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.1</version>
        <scope>test</scope>
    </dependency>

    <!-- 运行时需要，编译不需要 -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.33</version>
        <scope>runtime</scope>
    </dependency>

    <!-- 本地系统 jar（不推荐，会导致构建不可移植） -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>custom-lib</artifactId>
        <version>1.0</version>
        <scope>system</scope>
        <systemPath>${project.basedir}/lib/custom-lib.jar</systemPath>
    </dependency>
</dependencies>
```

---

## 四、Maven 多模块项目

多模块项目通过 parent pom 统一管理多个子模块：

```
my-project/
├── pom.xml                    # 父 POM
├── my-app-core/
│   └── pom.xml                # 子模块 core
├── my-app-service/
│   └── pom.xml                # 子模块 service
└── my-app-web/
    └── pom.xml                # 子模块 web
```

### 4.1 父 POM 配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <!-- 子模块列表 -->
    <modules>
        <module>my-app-core</module>
        <module>my-app-service</module>
        <module>my-app-web</module>
    </modules>

    <!-- 统一管理所有子模块的依赖版本 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>3.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>com.example</groupId>
                <artifactId>my-app-core</artifactId>
                <version>${project.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!-- 统一管理插件版本 -->
    <build>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.11.0</version>
                </plugin>
            </plugins>
        </pluginManagement>
    </build>
</project>
```

### 4.2 子模块配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.example</groupId>
        <artifactId>my-project</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>my-app-service</artifactId>

    <dependencies>
        <!-- 版本已在父 POM 中管理，此处无需写 version -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>my-app-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
</project>
```

**关键区别**：

| 元素 | 作用 |
|------|------|
| `<dependencyManagement>` | 声明依赖版本，子模块引用时不自动引入，需要子模块显式声明 |
| `<dependencies>` | 直接引入依赖，子模块自动继承 |
| `<pluginManagement>` | 声明插件版本和配置，子模块引用时不自动执行 |
| `<plugins>` | 直接在当前模块执行插件 |

---

## 五、Maven 依赖冲突解决

当项目中同一个 jar 出现多个版本时，Maven 按照以下规则选择：

### 5.1 最短路径优先

依赖树中路径最短的版本胜出：

```
A -> B -> C -> D(1.0)      路径长度为 3
A -> E -> D(2.0)           路径长度为 2  ← 胜出
```

```
项目 A
├── 依赖 B
│   └── 依赖 C 1.0 ──→ commons-lang3 3.8   (路径长度 3)
└── 依赖 D
    └── commons-lang3 3.12                  (路径长度 2) ← 最终使用 3.12
```

### 5.2 声明优先（路径相同时）

当路径长度相同时，pom.xml 中先声明的依赖版本胜出：

```xml
<!-- 如果 E 和 F 路径长度相同，先声明的 D(1.0) 胜出 -->
<dependency>
    <groupId>org.example</groupId>
    <artifactId>E</artifactId>   <!-- E 依赖 D(1.0) → 胜出 -->
</dependency>
<dependency>
    <groupId>org.example</groupId>
    <artifactId>F</artifactId>   <!-- F 依赖 D(2.0) -->
</dependency>
```

### 5.3 查看和解决依赖冲突

```bash
# 查看依赖树
mvn dependency:tree

# 查看特定依赖的树
mvn dependency:tree -Dincludes=org.slf4j:slf4j-api

# 查看依赖冲突
mvn dependency:tree -Dverbose

# 分析未使用的依赖
mvn dependency:analyze
```

### 5.4 解决冲突的三种方式

```xml
<!-- 方式一：直接声明（最短路径变为 1） -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>2.0.9</version>
</dependency>

<!-- 方式二：排除传递依赖 -->
<dependency>
    <groupId>org.example</groupId>
    <artifactId>problem-lib</artifactId>
    <version>1.0</version>
    <exclusions>
        <exclusion>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- 方式三：在 dependencyManagement 中锁定版本 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.9</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

---

## 六、Gradle 核心概念

### 6.1 build.gradle 基础结构（Groovy DSL）

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.example'
version = '1.0.0-SNAPSHOT'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
    maven { url 'https://repo.spring.io/release' }
}

dependencies {
    // 编译期依赖
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.google.guava:guava:32.1.3-jre'

    // 测试依赖
    testImplementation 'org.springframework.boot:spring-boot-starter-test'

    // 运行期依赖
    runtimeOnly 'com.mysql:mysql-connector-j:8.0.33'

    // 编译期注解处理器
    annotationProcessor 'org.projectlombok:lombok'
    compileOnly 'org.projectlombok:lombok:1.18.30'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

### 6.2 Gradle 插件

```groovy
// 方式一：plugins 块（推荐）
plugins {
    id 'java'
    id 'application'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}

// 方式二：buildscript 块（传统方式）
buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath 'com.github.johnrengelman:shadow:8.1.1'
    }
}
apply plugin: 'com.github.johnrengelman.shadow'
```

### 6.3 Gradle 任务（Task）

```groovy
// 定义自定义任务
tasks.register('hello') {
    group = 'custom'
    description = 'Prints a hello message'
    doLast {
        println 'Hello, Gradle!'
    }
}

// 带输入输出的任务
tasks.register('generateConfig') {
    def configFile = layout.buildDirectory.file('config/app.yml')
    outputs.file(configFile)

    doLast {
        configFile.get().asFile.text = '''
            app:
              name: my-app
              version: 1.0.0
        '''
    }
}

// 任务依赖
tasks.register('deploy') {
    dependsOn 'build'
    doLast {
        println 'Deploying application...'
    }
}

// 任务排序
tasks.named('test') {
    mustRunAfter 'compileJava'
}
```

### 6.4 Gradle 依赖配置

| 配置 | 说明 | 对应 Maven scope |
|------|------|------------------|
| `implementation` | 编译和运行需要，不暴露给消费者 | compile |
| `api` | 编译和运行需要，暴露给消费者（java-library 插件） | compile |
| `compileOnly` | 仅编译时需要 | provided |
| `runtimeOnly` | 仅运行时需要 | runtime |
| `testImplementation` | 测试编译和运行需要 | test |
| `testCompileOnly` | 测试编译时需要 | test |
| `annotationProcessor` | 注解处理器 | - |

```groovy
dependencies {
    // 传递依赖（依赖方不暴露给消费者）
    implementation 'com.google.guava:guava:32.1.3-jre'

    // 不传递（编译需要，但运行时由消费者自己提供）
    compileOnly 'javax.servlet:javax.servlet-api:4.0.1'

    // 运行时才加载
    runtimeOnly 'com.h2database:h2:2.2.224'

    // 多模块项目中使用 api 暴露给消费者
    // apply plugin: 'java-library'
    // api 'com.example:public-api:1.0'
}
```

### 6.5 settings.gradle

```groovy
// 项目名称
rootProject.name = 'my-project'

// 多模块配置
include 'my-app-core'
include 'my-app-service'
include 'my-app-web'

// 依赖版本管理（Gradle 8+ 版本目录）
dependencyResolutionManagement {
    versionCatalogs {
        libs {
            library('spring-boot', 'org.springframework.boot:spring-boot-starter:3.2.0')
            library('guava', 'com.google.guava:guava:32.1.3-jre')
            bundle('web', ['spring-boot', 'guava'])
        }
    }
}
```

### 6.6 Gradle Wrapper

```bash
# 生成 Wrapper（只需在项目根目录执行一次）
gradle wrapper --gradle-version 8.5

# 使用 Wrapper 构建（推荐，保证构建环境一致）
./gradlew build          # Linux / macOS
.\gradlew.bat build      # Windows

# 常见命令
./gradlew clean build
./gradlew test
./gradlew bootRun
./gradlew dependencies    # 查看依赖树
./gradlew :my-app-web:dependencies   # 查看指定模块依赖
```

---

## 七、Gradle vs Maven 性能对比

### 7.1 构建速度对比

| 对比项 | Maven | Gradle |
|--------|-------|--------|
| 首次构建 | 较快（无额外开销） | 稍慢（需要初始化 Gradle Daemon） |
| 二次构建 | 每次都全量执行 | 增量构建，只编译变更部分 |
| 大型项目（100+ 模块） | 3-5 分钟 | 30 秒 - 1 分钟 |
| 构建缓存 | 不支持 | 支持，跨构建复用产出物 |
| 并行构建 | 支持（mvn -T） | 默认支持 |
| 守护进程 | 无 | Gradle Daemon 常驻内存 |

### 7.2 Gradle 加速机制

```groovy
// gradle.properties 配置优化
org.gradle.daemon=true              # 启用守护进程（默认启用）
org.gradle.parallel=true            # 启用并行构建
org.gradle.caching=true             # 启用构建缓存
org.gradle.configureondemand=true   # 按需配置（仅配置需要的模块）
org.gradle.jvmargs=-Xmx2g           # 设置 JVM 堆内存
```

### 7.3 实际场景对比

以 Spring Boot 多模块项目（10 个子模块）为例：

| 操作 | Maven | Gradle |
|------|-------|--------|
| 首次 clean build | ~90s | ~60s |
| 修改一个文件后 build | ~60s | ~5s |
| 仅运行测试 | ~30s | ~10s |
| 下载依赖 | 相同速度 | 相同速度 |

**核心差异**：Gradle 的增量构建会跟踪输入输出的变化，只有当输入变化时才重新执行任务。

---

## 八、最佳实践

### 8.1 Maven 最佳实践

**1. 使用 dependencyManagement 统一管理版本**

```xml
<dependencyManagement>
    <dependencies>
        <!-- 通过 BOM 导入统一管理 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

**2. 使用 properties 管理版本号**

```xml
<properties>
    <lombok.version>1.18.30</lombok.version>
    <guava.version>32.1.3-jre</guava.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>${lombok.version}</version>
    </dependency>
</dependencies>
```

**3. 使用 profile 区分环境**

```xml
<profiles>
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <spring.profiles.active>dev</spring.profiles.active>
        </properties>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <spring.profiles.active>prod</spring.profiles.active>
        </properties>
    </profile>
</profiles>
```

**4. 排除不必要的依赖**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 8.2 Gradle 最佳实践

**1. 使用版本目录（Version Catalogs）统一管理**

在 `gradle/libs.versions.toml` 中：

```toml
[versions]
spring-boot = "3.2.0"
guava = "32.1.3-jre"
lombok = "1.18.30"

[libraries]
spring-boot-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
guava = { module = "com.google.guava:guava", version.ref = "guava" }
lombok = { module = "org.projectlombok:lombok", version.ref = "lombok" }

[bundles]
web = ["spring-boot-web", "guava"]
```

在 `build.gradle` 中使用：

```groovy
dependencies {
    implementation libs.bundles.web
    compileOnly libs.lombok
    annotationProcessor libs.lombok
}
```

**2. 使用自定义任务简化构建**

```groovy
tasks.register('fatJar', Jar) {
    archiveClassifier.set('all')
    from sourceSets.main.output
    dependsOn configurations.runtimeClasspath
    from {
        configurations.runtimeClasspath.findAll { it.name.endsWith('jar') }.collect {
            zipTree(it)
        }
    }
    manifest {
        attributes 'Main-Class': 'com.example.Main'
    }
}
```

**3. 配置仓库优先级**

```groovy
repositories {
    maven {
        url 'https://maven.aliyun.com/repository/public'
    }
    mavenCentral()
}
```

**4. 子模块公共配置提取**

```groovy
// 根 build.gradle 中的 subprojects 块
subprojects {
    apply plugin: 'java'

    repositories {
        mavenCentral()
    }

    dependencies {
        testImplementation platform('org.junit:junit-bom:5.10.1')
        testImplementation 'org.junit.jupiter:junit-jupiter'
    }

    tasks.named('test') {
        useJUnitPlatform()
    }
}
```

### 8.3 通用最佳实践

| 实践 | 说明 |
|------|------|
| 锁定依赖版本 | 不使用 LATEST 或 SNAPSHOT 作为生产依赖版本 |
| 定期更新依赖 | 使用 versions-maven-plugin 或 Gradle dependencyUpdates 检查更新 |
| 避免 system scope | 使用本地仓库或私有仓库替代 systemPath |
| 使用 Wrapper | Gradle 项目始终使用 gradlew，Maven 项目锁定 Maven 版本 |
| 多模块拆分合理 | 按业务域拆分，避免循环依赖 |
| CI/CD 中清理缓存 | 确保构建的可重复性 |
| 定期执行依赖分析 | Maven: `mvn dependency:analyze`；Gradle: `gradle dependencies` |

### 8.4 常用诊断命令速查

```bash
# ==================== Maven ====================
mvn dependency:tree                    # 查看依赖树
mvn dependency:analyze                 # 分析未使用和未声明的依赖
mvn help:effective-pom                 # 查看生效的 POM（含继承和 profile）
mvn help:effective-settings            # 查看生效的 settings
mvn versions:display-dependency-updates # 检查依赖更新
mvn clean install -DskipTests          # 跳过测试构建
mvn clean install -pl module-a -am     # 构建指定模块及其依赖
mvn clean install -rf :module-a        # 从指定模块恢复构建

# ==================== Gradle ====================
./gradlew dependencies                 # 查看所有依赖
./gradlew :module:dependencies         # 查看指定模块依赖
./gradlew dependencyInsight --dependency guava  # 追踪特定依赖来源
./gradlew buildHealth                  # 构建健康检查（需插件）
./gradlew clean build --refresh-dependencies   # 刷新依赖后构建
./gradlew :module:build                # 构建指定模块
./gradlew build --parallel             # 并行构建
```

---

## 📊 本节统计

| 统计维度 | 数值 | 口径 |
|----------|------|------|
| 分类主题数 | 2 | Maven / Gradle |
| 子 README 数 | 0 | 无子 README（Maven vs Gradle 对比 + 各自核心概念聚合在本篇） |
| 含 frontmatter 的 README | 1 / 1 | 100% 覆盖（2026-07-01） |

> **统计时间戳**：2026-07-01

---

← [返回 01.java 主模块](../README.md)
