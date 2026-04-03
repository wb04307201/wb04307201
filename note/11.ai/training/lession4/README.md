# 使用 Java 开发 MCP 服务并发布到 Maven 中央仓库完整指南

## 目录

1. [什么是 MCP](#什么是-mcp)
2. [项目架构与技术选型](#项目架构与技术选型)
3. [开发环境准备](#开发环境准备)
4. [创建 Spring Boot 项目](#创建-spring-boot-项目)
5. [实现 MCP 服务核心逻辑](#实现-mcp-服务核心逻辑)
6. [配置 MCP Server](#配置-mcp-server)
7. [发布到 Maven 中央仓库](#发布到-maven-中央仓库)
8. [使用 JBang 通过 stdio 集成到大模型](#使用-jbang-通过-stdio-集成到大模型)
9. [总结](#总结)

---

## 什么是 MCP

**Model Context Protocol (MCP)** 是一个开放协议，用于标准化大语言模型与外部数据源和工具之间的交互。它允许开发者将应用程序、数据源或 AI 功能无缝集成到任何使用 MCP 的 LLM 客户端中。

### MCP 的核心优势

- **标准化接口**：统一的工具调用规范
- **松耦合架构**：服务与 LLM 客户端独立部署
- **易于扩展**：快速添加新的工具和能力
- **跨平台支持**：支持多种编程语言和运行环境

### MCP 通信模式

MCP 支持多种通信方式：
- **stdio**：基于标准输入输出的本地进程通信（本文重点）
- **HTTP/SSE**：基于 HTTP 的服务器发送事件
- **WebSocket**：双向实时通信

本文将以**中国天气查询服务**为例，详细介绍如何使用 Java 开发 MCP 服务，并发布到 Maven 中央仓库，最终通过 JBang 和 stdio 方式集成到大模型工具中。

---

## 项目架构与技术选型

### 技术栈

- **Java 17**：LTS 版本，提供优秀的性能和新特性
- **Spring Boot 3.5.13**：快速应用开发框架
- **Spring AI MCP**：Spring AI 提供的 MCP 服务器支持
- **Maven**：项目构建和依赖管理
- **JBang**：Java 脚本执行工具，用于运行 JAR

### 项目结构

```
cn-weather-mcp/
├── src/main/java/cn/wubo/cn/weather/mcp/
│   ├── WeatherApplication.java    # 主启动类
│   └── WeatherService.java        # 天气服务实现
├── src/main/resources/
│   └── application.yml            # 配置文件
├── pom.xml                        # Maven 配置
└── .github/workflows/
    └── publish.yml                # CI/CD 发布流程
```

---

## 开发环境准备

### 必需软件

1. **JDK 17+**
   ```bash
   java -version
   ```

2. **Maven 3.6+**
   ```bash
   mvn -version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **GPG**（用于签名发布到中央仓库）
   ```bash
   gpg --version
   ```

### GPG 密钥生成

发布到 Maven 中央仓库需要 GPG 签名：

```bash
# 生成 GPG 密钥
gpg --full-generate-key

# 查看生成的密钥
gpg --list-keys

# 将公钥上传到密钥服务器
gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID
```

---

## 创建 Spring Boot 项目

### 1. 创建 pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.13</version>
        <relativePath/>
    </parent>
    
    <groupId>io.github.your-username</groupId>
    <artifactId>cn-weather-mcp</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>cn-weather-mcp</name>
    <description>中国天气 MCP 服务 - 提供中国城市天气查询服务</description>
    
    <!-- 项目元信息 -->
    <url>https://github.com/your-username/cn-weather-mcp</url>
    
    <developers>
        <developer>
            <id>your-id</id>
            <name>Your Name</name>
            <email>your-email@example.com</email>
        </developer>
    </developers>
    
    <licenses>
        <license>
            <name>The Apache Software License, Version 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
        </license>
    </licenses>
    
    <scm>
        <connection>scm:git:https://github.com/your-username/cn-weather-mcp.git</connection>
        <developerConnection>scm:git:git@github.com:your-username/cn-weather-mcp.git</developerConnection>
        <url>https://github.com/your-username/cn-weather-mcp</url>
    </scm>
    
    <properties>
        <java.version>17</java.version>
        <spring-ai.version>1.1.3</spring-ai.version>
    </properties>
    
    <!-- 依赖管理 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.ai</groupId>
                <artifactId>spring-ai-bom</artifactId>
                <version>${spring-ai.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    
    <dependencies>
        <!-- Spring AI MCP Server -->
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-mcp-server</artifactId>
        </dependency>
        
        <!-- Spring Web (用于 HTTP 请求) -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-web</artifactId>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <!-- Spring Boot Maven 插件 -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            
            <!-- 源码插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.3.0</version>
                <executions>
                    <execution>
                        <id>attach-sources</id>
                        <goals>
                            <goal>jar-no-fork</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            
            <!-- Javadoc 插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>3.6.0</version>
                <executions>
                    <execution>
                        <id>attach-javadocs</id>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            
            <!-- GPG 签名插件 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-gpg-plugin</artifactId>
                <version>3.1.0</version>
                <executions>
                    <execution>
                        <id>sign-artifacts</id>
                        <phase>verify</phase>
                        <goals>
                            <goal>sign</goal>
                        </goals>
                        <configuration>
                            <gpgArguments>
                                <arg>--pinentry-mode</arg>
                                <arg>loopback</arg>
                            </gpgArguments>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            
            <!-- Central Publishing 插件 -->
            <plugin>
                <groupId>org.sonatype.central</groupId>
                <artifactId>central-publishing-maven-plugin</artifactId>
                <version>0.9.0</version>
                <extensions>true</extensions>
                <configuration>
                    <publishingServerId>central</publishingServerId>
                    <autoPublish>true</autoPublish>
                    <waitUntil>published</waitUntil>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### 2. 创建配置文件 application.yml

```yaml
spring:
  main:
    web-application-type: none  # 非 Web 应用
    banner-mode: off            # 关闭启动横幅
  ai:
    mcp:
      server:
        name: cn-weather-mcp    # MCP 服务名称
        version: 1.0.0          # MCP 服务版本
logging:
  file:
    name: ./mcp/cn-weather-mcp.log  # 日志文件路径
```

---

## 实现 MCP 服务核心逻辑

### 1. 创建服务类 WeatherService

这是 MCP 服务的核心，包含所有工具方法的实现：

```java
package cn.wubo.cn.weather.mcp;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class WeatherService {

    private static final String BASE_URL = "http://t.weather.itboy.net/api/weather/city/";

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final Map<String, CityCodeInfo> cityCodeMap;

    public WeatherService() {
        this.restClient = RestClient.builder()
                .baseUrl(BASE_URL)
                .build();
        this.objectMapper = new ObjectMapper();
        this.cityCodeMap = loadCityCodes();
    }

    // 加载城市代码数据
    private static Map<String, CityCodeInfo> loadCityCodes() {
        List<CityCodeInfo> cityCodes = Arrays.asList(
            new CityCodeInfo(1, "北京", "北京", "101010100"),
            new CityCodeInfo(23, "天津市", "天津", "101030100"),
            new CityCodeInfo(36, "上海", "上海", "101020100"),
            // ... 更多城市数据
        );
        
        return cityCodes.stream()
            .collect(Collectors.toMap(CityCodeInfo::cityCode, info -> info));
    }

    // 数据记录类
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record WeatherResponse(
            @JsonProperty("status") Integer status,
            @JsonProperty("message") String message,
            @JsonProperty("cityInfo") CityInfo cityInfo,
            @JsonProperty("data") WeatherDataWrapper data
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record CityInfo(
            @JsonProperty("city") String city,
            @JsonProperty("citykey") String cityKey,
            @JsonProperty("parent") String parent,
            @JsonProperty("updateTime") String updateTime
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record WeatherDataWrapper(
            @JsonProperty("shidu") String humidity,
            @JsonProperty("pm25") Double pm25,
            @JsonProperty("pm10") Double pm10,
            @JsonProperty("quality") String quality,
            @JsonProperty("wendu") String temperature,
            @JsonProperty("ganmao") String healthTip,
            @JsonProperty("forecast") List<Forecast> forecast
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Forecast(
            @JsonProperty("date") String date,
            @JsonProperty("high") String highTemp,
            @JsonProperty("low") String lowTemp,
            @JsonProperty("ymd") String ymd,
            @JsonProperty("week") String week,
            @JsonProperty("fx") String windDirection,
            @JsonProperty("fl") String windLevel,
            @JsonProperty("type") String weatherType,
            @JsonProperty("notice") String notice
    ) {}

    public record CityCodeInfo(
        Integer id,
        String province,
        String city,
        String cityCode
    ) {}

    /**
     * 工具方法 1：获取当前天气
     */
    @Tool(description = "Get current weather for a Chinese city. Input is city code (e.g., 101010100 for Beijing)")
    public String getCurrentWeather(
        @ToolParam(description = "City code (e.g., 101010100 for Beijing, 101020100 for Shanghai)") 
        String cityCode
    ) {
        ResponseEntity<byte[]> responseEntity = restClient.get()
                .uri("{cityCode}", cityCode)
                .retrieve()
                .toEntity(byte[].class);

        byte[] body = responseEntity.getBody();
        if (body == null) {
            throw new RuntimeException("Empty response from weather API");
        }

        String response = new String(body, StandardCharsets.UTF_8);

        WeatherResponse weatherResponse;
        try {
            weatherResponse = objectMapper.readValue(response, WeatherResponse.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse weather data: " + e.getMessage());
        }

        if (200 != weatherResponse.status()) {
            throw new RuntimeException("Weather API returned error: " + weatherResponse.message());
        }

        WeatherDataWrapper data = weatherResponse.data();
        CityInfo cityInfo = weatherResponse.cityInfo();

        return String.format("""
                        城市：%s (%s)
                        温度：%s°C
                        湿度：%s
                        空气质量：%s (PM2.5: %s)
                        风向：%s %s
                        温馨提示：%s
                        更新时间：%s
                        """,
                cityInfo.city(),
                cityInfo.parent(),
                data.temperature(),
                data.humidity(),
                data.quality(),
                data.pm25(),
                data.forecast().get(0).windDirection(),
                data.forecast().get(0).windLevel(),
                data.healthTip(),
                cityInfo.updateTime());
    }

    /**
     * 工具方法 2：搜索城市代码
     */
    @Tool(description = "Search Chinese city codes by city name. Returns list of cities with their codes for weather queries")
    public String searchCityCode(
        @ToolParam(description = "City name to search (e.g., '北京', '上海', '广州')") 
        String cityName
    ) {
        if (cityName == null || cityName.trim().isEmpty()) {
            return "请输入要查询的城市名称";
        }

        String searchName = cityName.trim();
        List<CityCodeInfo> results = cityCodeMap.values().stream()
            .filter(info -> info.city().contains(searchName) ||
                    info.province().contains(searchName))
            .limit(20)
            .toList();

        if (results.isEmpty()) {
            return String.format("未找到包含 '%s' 的城市，请检查输入后重试", searchName);
        }

        StringBuilder sb = new StringBuilder();
        sb.append(String.format("找到 %d 个匹配的城市:\n\n", results.size()));
        sb.append(String.format("%-4s %-10s %-10s %-12s%n", "编号", "省份", "城市", "城市编码"));
        sb.append("-".repeat(40)).append("\n");

        for (CityCodeInfo info : results) {
            sb.append(String.format("%-4d %-10s %-10s %-12s%n",
                info.id(), info.province(), info.city(), info.cityCode()));
        }

        sb.append("\n提示：使用城市编码可以查询具体天气");
        return sb.toString();
    }
}
```

### 关键注解说明

- **`@Service`**：标记为 Spring 服务组件
- **`@Tool`**：Spring AI 的工具注解，标记该方法为 MCP 工具
- **`@ToolParam`**：标注工具方法的参数及其描述

---

## 配置 MCP Server

### 创建启动类 WeatherApplication

```java
package cn.wubo.cn.weather.mcp;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class WeatherApplication {

    public static void main(String[] args) {
        SpringApplication.run(WeatherApplication.class, args);
    }

    @Bean
    public ToolCallbackProvider weatherTools(WeatherService weatherService) {
        return MethodToolCallbackProvider.builder()
                .toolObjects(weatherService)
                .build();
    }
}
```

### 配置说明

- **`ToolCallbackProvider`**：提供工具回调的 Bean
- **`MethodToolCallbackProvider`**：基于方法注解的工具提供者
- **`.toolObjects(weatherService)`**：注册包含 `@Tool` 注解的服务对象

---

## 发布到 Maven 中央仓库

### 1. 在 Sonatype Central 创建账户

访问 [Sonatype Central](https://central.sonatype.com/) 注册账户并完成验证。

### 2. 配置认证信息

#### 本地测试（~/.m2/settings.xml）

```xml
<settings>
  <servers>
    <server>
      <id>central</id>
      <username>your-username</username>
      <password>your-token</password>
    </server>
  </servers>
</settings>
```

#### GitHub Secrets 配置

在 GitHub 仓库设置中添加以下 Secrets：

- `CENTRAL_USERNAME`：Sonatype Central 用户名
- `CENTRAL_TOKEN`：Sonatype Central Token
- `GPG_PRIVATE_KEY`：GPG 私钥
- `GPG_PASSPHRASE`：GPG 私钥密码

### 3. 创建 GitHub Actions 发布流程

创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to Sonatype Central

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven
            
      - name: Create Maven settings.xml
        run: |
          mkdir -p ~/.m2
          cat > ~/.m2/settings.xml << EOF
          <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
            <servers>
              <server>
                <id>central</id>
                <username>\${CENTRAL_USERNAME}</username>
                <password>\${CENTRAL_TOKEN}</password>
              </server>
            </servers>
          </settings>
          EOF
        env:
          CENTRAL_USERNAME: \${{ secrets.CENTRAL_USERNAME }}
          CENTRAL_TOKEN: \${{ secrets.CENTRAL_TOKEN }}

      - name: Import GPG Key
        uses: crazy-max/ghaction-import-gpg@v6
        with:
          gpg_private_key: \${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: \${{ secrets.GPG_PASSPHRASE }}
          git_user_signingkey: false
          git_commit_gpgsign: false

      - name: Extract version from tag
        id: version
        run: echo "VERSION=\${GITHUB_REF#refs/tags/v}" >> \$GITHUB_OUTPUT

      - name: Set Version
        run: mvn versions:set -DnewVersion=\${{ steps.version.outputs.VERSION }} -DgenerateBackupPoms=false -B

      - name: Publish to Central
        run: mvn -B clean deploy
        env:
          GPG_PASSPHRASE: \${{ secrets.GPG_PASSPHRASE }}
```

### 4. 发布流程

1. **提交代码到 Git**
   ```bash
   git add .
   git commit -m "Initial release"
   git push origin main
   ```

2. **创建 Git Release**
   ```bash
   # 打标签
   git tag v1.0.0
   git push origin v1.0.0
   
   # 或在 GitHub UI 创建 Release
   ```

3. **自动发布**
   - 创建 Release 后，GitHub Actions 会自动触发
   - 等待 Workflow 完成
   - 在 [Sonatype Central](https://central.sonatype.com/) 查看发布状态
   - 通常 15-30 分钟后同步到 Maven Central

### 5. 验证发布

发布成功后，可以在以下地址查看：

- **Sonatype Central**: https://central.sonatype.com/artifact/io.github.wb04307201/cn-weather-mcp
- **Maven Central**: https://repo.maven.apache.org/maven2/io/github/wb04307201/cn-weather-mcp/

---

## 使用 JBang 通过 stdio 集成到大模型

### 什么是 JBang

**JBang** 是一个允许你无需安装 JDK 或配置项目即可运行 Java 代码的工具。它非常适合快速原型开发和脚本编写。

### 1. 安装 JBang

#### Windows (PowerShell)

```shell
iex "& { $(iwr https://ps.jbang.dev) } app setup"
```

#### Linux / macOS

```shell
curl -Ls https://sh.jbang.dev | bash -s - app setup
```

### 2. 验证安装

```shell
jbang --version
```

### 3. MCP Client 配置

以大模型工具的 MCP 配置为例，创建配置文件：

#### Claude Desktop 配置

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "cn-weather-mcp": {
      "command": "jbang",
      "args": [
        "io.github.wb04307201:cn-weather-mcp:1.0.0"
      ]
    }
  }
}
```

#### 配置说明

- **`command`**: `jbang` - 使用 JBang 运行
- **`args`**: Maven 坐标 - JBang 会自动从 Maven Central 下载并运行

### 4. stdio 工作原理

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  LLM Client │◄───────►│  JBang       │◄───────►│  MCP Server │
│  (Claude)   │  JSON   │  (Runner)    │  stdio  │  (Your Jar) │
└─────────────┘  RPC    └──────────────┘  IO     └─────────────┘
```

**通信流程**：

1. **LLM Client** 发送 JSON-RPC 请求到 JBang
2. **JBang** 启动 Java 进程，通过 stdin/stdout 与 MCP Server 通信
3. **MCP Server** 处理请求并返回结果
4. 结果沿原路返回给 LLM Client

### 5. 测试 MCP 服务

#### 本地测试

```bash
# 直接使用 JBang 运行
jbang io.github.wb04307201:cn-weather-mcp:1.0.0
```

#### 在 IDE 中测试

运行 `WeatherApplication.main()` 方法，然后通过 MCP 客户端工具连接。

### 6. 在大模型中使用

配置完成后，在大模型对话中可以直接使用：

**示例对话**：

```
用户：北京今天天气怎么样？

助手：[调用 MCP 工具 searchCityCode("北京")]
      [获取城市代码 101010100]
      [调用 MCP 工具 getCurrentWeather("101010100")]
      
      北京今天的天气情况如下：
      - 温度：25°C
      - 湿度：60%
      - 空气质量：良 (PM2.5: 35)
      - 风向：东南风 2 级
      - 温馨提示：天气舒适，适合户外活动
```

---

## 完整示例代码清单

### 项目关键文件

1. **pom.xml** - Maven 配置（见前文）
2. **application.yml** - 应用配置（见前文）
3. **WeatherApplication.java** - 启动类（见前文）
4. **WeatherService.java** - 服务实现（见前文）
5. **publish.yml** - GitHub Actions（见前文）

### 运行命令

```bash
# 编译项目
mvn clean package

# 本地测试
mvn spring-boot:run

# 发布到 Maven Central
mvn clean deploy

# 使用 JBang 运行
jbang io.github.wb04307201:cn-weather-mcp:1.0.0
```

---

## 常见问题与解决方案

### Q1: GPG 签名失败

**错误信息**：`gpg: signing failed: No secret key`

**解决方案**：
```bash
# 确认 GPG 密钥存在
gpg --list-secret-keys

# 重新生成密钥
gpg --full-generate-key
```

### Q2: Maven 部署被拒绝

**原因**：缺少必要的元数据或签名

**解决方案**：
- 确保 pom.xml 包含所有必需信息（developers, licenses, scm）
- 确保生成了 source 和 javadoc jars
- 确保 GPG 签名正确配置

### Q3: JBang 无法下载 JAR

**错误信息**：`Failed to resolve artifact`

**解决方案**：
- 等待 Maven Central 同步完成（发布后约 15-30 分钟）
- 检查 Maven 坐标是否正确
- 清除 JBang 缓存：`jbang cache clear`

### Q4: MCP 工具无法被识别

**原因**：`@Tool` 注解未正确配置

**解决方案**：
- 确保方法有 `@Tool` 注解
- 确保方法参数有 `@ToolParam` 注解
- 确保 `ToolCallbackProvider` Bean 正确注册

---

## 最佳实践建议

### 1. 代码规范

- 为所有工具方法提供详细的文档注释
- 使用清晰的参数命名和描述
- 提供完善的错误处理和异常信息

### 2. 安全性

- 避免在代码中硬编码敏感信息（API Keys、密码等）
- 使用环境变量或配置中心管理敏感配置
- 对输入参数进行验证和清理

### 3. 性能优化

- 使用连接池管理 HTTP 连接
- 实现适当的缓存策略减少重复请求
- 异步处理耗时操作

### 4. 可维护性

- 保持单一职责原则，每个工具方法功能明确
- 编写单元测试覆盖核心逻辑
- 使用日志记录关键操作和错误信息

---

## 总结

本文详细介绍了如何使用 Java 开发 MCP 服务并发布到 Maven 中央仓库的完整流程：

### 核心步骤回顾

1. ✅ **环境准备**：安装 JDK、Maven、GPG
2. ✅ **项目搭建**：创建 Spring Boot 项目，配置 Maven POM
3. ✅ **服务开发**：实现 `@Tool` 注解的业务方法
4. ✅ **MCP 配置**：配置 `ToolCallbackProvider` Bean
5. ✅ **发布准备**：配置 GPG 签名和 Sonatype Central
6. ✅ **自动化发布**：使用 GitHub Actions 自动发布
7. ✅ **集成使用**：通过 JBang 和 stdio 集成到大模型

### 技术优势

- **快速开发**：基于 Spring AI，几行代码即可暴露 MCP 工具
- **标准化**：遵循 MCP 协议，兼容所有 MCP 客户端
- **易部署**：通过 JBang 无需安装，直接运行 JAR
- **可扩展**：轻松添加新的工具和方法

### 应用场景

- **企业工具集成**：将内部系统封装为 MCP 工具供 AI 调用
- **SaaS 服务封装**：将第三方 API 包装为标准化工具
- **个人项目分享**：发布开源工具到 Maven Central
- **微服务治理**：统一管理 AI 可调用的服务接口

### 后续学习资源

- **Spring AI 官方文档**：https://docs.spring.io/spring-ai/reference/
- **MCP 协议规范**：https://modelcontextprotocol.io/
- **Sonatype Central 发布指南**：https://central.sonatype.org/publish/
- **JBang 使用手册**：https://www.jbang.dev/documentation/

---

通过本文的学习，你已经掌握了从零开始开发、发布和使用 MCP 服务的完整技能树。现在就开始创建你自己的 MCP 服务，让大模型能够调用你的代码吧！

**项目源码参考**：https://github.com/wb04307201/cn-weather-mcp
