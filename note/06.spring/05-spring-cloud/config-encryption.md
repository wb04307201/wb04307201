# Config 加密（Nacos / Spring Cloud Config / Jasypt）

> 最后更新: 2026-06-14
> ⬅️ [返回 05 Spring Cloud](README.md) | [Config 中心](config-center.md) | [Bus](bus.md)

生产环境的配置中心里**一定会有敏感信息**——数据库密码、API Key、第三方凭证。明文存储 = 0 安全。**加密方案需在「易用性」与「密钥管理成本」之间权衡**。

---

## 一、Nacos Config 加密

### 方案 A：`nacos-config-encryption-plugin`（官方）

```xml
<dependency>
    <groupId>com.alibaba.nacos</groupId>
    <artifactId>nacos-config-encryption-plugin</artifactId>
    <version>2.3.0</version>
</dependency>
```

Nacos 控制台 → 配置详情 → 勾选「加密」，写入的明文会被插件加密存储。但**密钥管理依赖插件自身**，适合中小团队快速落地。

### 方案 B：自定义 `PropertySource` 包装

```java
public class DecryptPropertySource extends EnumerablePropertySource<String> {

    private final Map<String, Object> decrypted;

    public DecryptPropertySource(String name, Map<String, Object> source) {
        super(name);
        this.decrypted = source.entrySet().stream()
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                e -> e.getValue().toString().startsWith("ENC(")
                    ? decrypt(e.getValue().toString())
                    : e.getValue()
            ));
    }

    @Override
    public Object getProperty(String name) { return decrypted.get(name); }

    @Override
    public String[] getPropertyNames() {
        return decrypted.keySet().toArray(new String[0]);
    }
}
```

**优势**：密钥走 KMS / Vault，不在 Nacos 自身；**劣势**：需自行维护解密逻辑。

---

## 二、Spring Cloud Config 加密

### 配置

```yaml
# Config Server
encrypt:
  key-store:
    location: classpath:server.jks     # Java KeyStore
    alias: configserver
    secret: ${KEYSTORE_PASSWORD}
    type: JCEKS                        # JCEKS 支持对称密钥
```

### 加密 / 解密端点

```bash
# 加密
curl http://config-server:8888/encrypt -d 'mySecretValue'
# 返回：a1b2c3d4...

# 解密（仅本地运维用，禁用外网）
curl http://config-server:8888/decrypt -d 'a1b2c3d4...'
```

仓库中存储形如 `{cipher}a1b2c3d4...`，Config Server 启动时自动解密回填。

### RSA 非对称加密（推荐）

```bash
# 生成密钥库
keytool -genkeypair -alias configserver \
    -keyalg RSA -keysize 2048 \
    -dname "CN=Config Server" \
    -keystore server.jks \
    -storepass changeit \
    -keypass changeit \
    -storetype JCEKS
```

Config Server 持有私钥（解密），客户端通过 HTTPS 拉取解密后的配置——**密钥不出仓库**。

---

## 三、Jasypt 集成（最灵活）

`jasypt-spring-boot-starter` 直接在 `@Value` 层面解密，**适用于任意配置源**（Nacos / Config / 本地 yml）。

### 依赖

```xml
<dependency>
    <groupId>com.github.ulisesbocchio</groupId>
    <artifactId>jasypt-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

### 配置

```yaml
jasypt:
  encryptor:
    algorithm: PBEWithHMACSHA512AndAES_256
    iv-generator-classname: org.jasypt.iv.RandomIvGenerator
    password: ${JASYPT_PASSWORD}      # 密钥从环境变量注入，不入仓库
```

### 使用

```yaml
# application.yml 中密文用 ENC() 包裹
spring:
  datasource:
    password: ENC(AbCdEf123...)

app:
  api-key: ENC(XyZ987...)
```

```java
@Value("${spring.datasource.password}")
private String dbPassword;             // 启动时自动解密为明文
```

### 自定义加密

```java
@Autowired
private StringEncryptor encryptor;

public void encrypt() {
    String cipher = encryptor.encrypt("mySecretValue");
    System.out.println("ENC(" + cipher + ")");
}
```

---

## 四、安全注意事项

### 1. 密钥不入库

```yaml
# 错误：密钥硬编码
jasypt.password: mySecretKey123

# 正确：从环境变量 / KMS 注入
jasypt.password: ${JASYPT_PASSWORD}
```

```bash
# 启动时注入
export JASYPT_PASSWORD=$(vault read -field=value secret/config)
java -jar app.jar
```

### 2. 密钥定期轮换

- **Jasypt**：双密钥过渡（`PBEWithHMACSHA512AndAES_256` + 历史算法）
- **Config Server**：新 keystore 发布 → 滚动重启客户端
- **KMS / Vault**：动态密钥 + 租约自动续期

### 3. 传输加密

- Nacos / Config Server 启用 **HTTPS + mTLS**
- 客户端开启 `spring.cloud.nacos.config.namespace` + RBAC

### 4. 审计与访问控制

- Nacos 开启鉴权：`nacos.core.auth.enabled=true`
- 操作日志接入审计系统（谁在何时改了数据库密码）
- 配置文件按**敏感度分级**（一般 / 机密 / 绝密）

---

## 五、方案选型

| 场景 | 推荐方案 |
|------|---------|
| 中小团队、快速落地 | **Nacos Plugin** 或 **Jasypt** |
| 已有 KMS / Vault | **Jasypt + Vault** 动态密钥 |
| 严格金融合规 | **Spring Cloud Config RSA + 审计** |
| Spring Boot 单体 | **Jasypt**（最轻量） |

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [Config 中心](config-center.md) — 配置中心选型与实战
- [Bus](bus.md) — 加密配置的实时刷新
- [04.system-design/05-security/secrets-management](../../04.system-design/05-security/secrets-management/) — 密钥管理基础