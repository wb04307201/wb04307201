<!--
module:
  parent: tools
  slug: tools/k8s-configmap-secret
  type: article
  category: 主模块子文章
  summary: K8s ConfigMap 与 Secret
-->

# K8s ConfigMap 与 Secret：配置管理最佳实践

> 一份按场景梳理的 K8s 配置管理速查手册：从 ConfigMap 到 Secret 的完整实战。

---
---

## 一、为什么需要 ConfigMap / Secret？

容器化部署的核心原则：**配置与镜像分离**。

```
❌ 错误做法：把配置硬编码到镜像里
   FROM myapp:1.0
   COPY config.yml /app/config.yml   # 每次改配置都要重新构建镜像

✅ 正确做法：配置外置，通过 ConfigMap/Secret 注入
   FROM myapp:1.0
   # 配置通过 Volume 或环境变量从 K8s 注入
```

---

## 二、ConfigMap：非敏感配置

### 2.1 适用场景

- 应用配置（数据库连接串、API 地址）
- 环境变量（LOG_LEVEL=INFO）
- 配置文件（nginx.conf、application.yml）
- 命令行参数

### 2.2 创建方式

#### 方式 1：从字面量创建

```bash
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=INFO \
  --from-literal=DB_HOST=mysql.default.svc
```

#### 方式 2：从文件创建

```bash
kubectl create configmap nginx-config --from-file=nginx.conf
```

#### 方式 3：YAML 声明

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "INFO"
  DB_HOST: "mysql.default.svc"
  application.yml: |
    server:
      port: 8080
    spring:
      datasource:
        url: jdbc:mysql://${DB_HOST}:3306/db
```

### 2.3 在 Pod 中使用

#### 方式 1：环境变量

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
    envFrom:
    - configMapRef:
        name: app-config          # 所有 key 作为环境变量
    env:
    - name: CUSTOM_VAR            # 引用单个 key
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
```

#### 方式 2：Volume 挂载（推荐配置文件）

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: config-volume
      mountPath: /app/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      items:
      - key: application.yml
        path: application.yml     # 只挂载需要的文件
```

挂载后容器内 `/app/config/application.yml` 就是配置文件。

---

## 三、Secret：敏感配置

### 3.1 适用场景

- 数据库密码
- API Token
- TLS 证书
- SSH Key

### 3.2 Secret 类型

| 类型 | 用途 |
|------|------|
| `Opaque` | 默认（通用）|
| `kubernetes.io/tls` | TLS 证书 |
| `kubernetes.io/dockerconfigjson` | Docker 镜像仓库认证 |
| `kubernetes.io/basic-auth` | 基本认证 |
| `kubernetes.io/ssh-auth` | SSH 认证 |

### 3.3 创建方式

#### 方式 1：命令行（推荐，敏感数据不入 YAML）

```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='S3cr3t!Passw0rd'
```

#### 方式 2：YAML（需要 base64 编码）

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=          # echo -n admin | base64
  password: UzNjcjN0IVBhc3N3MHJk
```

#### 方式 3：从文件创建

```bash
kubectl create secret generic tls-secret \
  --from-file=tls.crt \
  --from-file=tls.key
```

### 3.4 在 Pod 中使用

```yaml
spec:
  containers:
  - name: app
    envFrom:
    - secretRef:
        name: db-secret
    volumeMounts:
    - name: tls-volume
      mountPath: /etc/tls
      readOnly: true
  volumes:
  - name: tls-volume
    secret:
      secretName: tls-secret
```

---

## 四、ConfigMap vs Secret 区别

| 维度 | ConfigMap | Secret |
|------|-----------|--------|
| 数据敏感度 | 非敏感 | 敏感（密码/证书）|
| 存储 | etcd 明文 | etcd Base64 编码（非加密！）|
| 访问控制 | RBAC | RBAC + 加密存储（KMS）|
| 大小限制 | 1 MB | 1 MB |

> ⚠️ Secret 默认只是 Base64 编码，**不是加密**！生产环境必须启用 **etcd 加密** + **KMS 集成**。

---

## 五、etcd 加密（生产必备）

```yaml
# 启用 etcd 加密（需要 EncryptionConfiguration）
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: c2VjcmV0IGVuY3J5cHRpb24gZGF0YSBrZXkgMQ==
    - identity: {}
```

---

## 六、外部密钥管理（最佳实践）

生产环境推荐使用 **外部 KMS**：

| 工具 | 特点 |
|------|------|
| **HashiCorp Vault** | 业界标准（动态密钥）|
| **AWS KMS** | AWS 集成 |
| **Azure Key Vault** | Azure 集成 |
| **阿里云 KMS** | 阿里云集成 |
| **Sealed Secrets** | K8s 专用（Bitnami）|

### Vault 集成示例

```yaml
spec:
  containers:
  - name: app
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
  # Vault Agent Sidecar 模式
  - name: vault-agent
    image: vault:1.12
    # ... Vault Agent 配置
```

---

## 七、配置热更新

### 7.1 ConfigMap 热更新（默认行为）

- **环境变量注入**：不会热更新（需要重启 Pod）
- **Volume 挂载**：会热更新（约 30-60 秒延迟）

### 7.2 Secret 热更新（默认不更新）

- Secret 更新后，Pod 内挂载的 Secret **默认不会热更新**
- 需要特殊配置：

```yaml
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
      defaultMode: 0400
```

或使用 **Reloader** 等工具自动重启 Pod。

---

## 八、最佳实践

1. **不要在 Git 仓库提交明文 Secret**：使用 Sealed Secrets / External Secrets
2. **ConfigMap 与 Secret 分离**：非敏感用 ConfigMap，敏感用 Secret
3. **文件挂载优于环境变量**：支持热更新 + 复杂配置
4. **etcd 加密**：生产环境必须启用
5. **KMS 集成**：使用云厂商 KMS 或 Vault
6. **定期轮换**：密码类 Secret 90 天轮换

---

← [返回 K8s 总览](../README.md) · 📅 2026-06-28