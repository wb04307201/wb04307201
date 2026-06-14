# 健康检查三探针（K8s Liveness / Readiness / Startup）

> 最后更新: 2026-06-14
> ⬅️ [返回 07 可观测性](README.md) | [Actuator](actuator.md) | [Micrometer](micrometer.md)

Spring Boot 自 **2.3** 起内置三套**应用可用性探针**（Application Availability Probes），与 Kubernetes 的 `livenessProbe` / `readinessProbe` / `startupProbe` 一一对应，是生产环境 K8s 部署的关键拼图。

---

## 🎯 一句话定位

**三探针 = 容器编排平台对应用"还能不能 / 准备好了没 / 启动完了没"的询问机制**——Actuator 把应用的真实状态（不仅是进程在不在）以 HTTP 端点形式对外暴露，K8s 据此决定是否重启 Pod / 转发流量。

---

## 一、三探针语义对比

| 探针 | 端点 | K8s 字段 | 答什么问题 | 失败后果 |
|:-----|:-----|:---------|:----------|:--------|
| **Liveness（存活）** | `/actuator/health/liveness` | `livenessProbe` | 应用**进程是否还活着**（未死锁、OOM 仍能响应） | K8s **重启 Pod** |
| **Readiness（就绪）** | `/actuator/health/readiness` | `readinessProbe` | 应用**能否接收流量**（依赖就绪、已 warm-up） | K8s **从 Service Endpoints 摘除** |
| **Startup（启动）** | `/actuator/health/startup` | `startupProbe` | **慢启动**应用是否已完成启动 | 在启动完成前**禁用** liveness/readiness |

> 📌 **三者互不替代**——liveness 失败 = 重启，readiness 失败 = 摘流量，startup 失败 = 给更多启动时间。

---

## 二、启用配置

```yaml
# application.yml
management:
  endpoint:
    health:
      probes:
        enabled: true           # 2.3+ 默认 false，必须显式开启
      show-details: always
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  health:
    livenessstate:
      enabled: true            # 默认 true
    readinessstate:
      enabled: true            # 默认 true
```

依赖：仅需 `spring-boot-starter-actuator`。

---

## 三、ApplicationAvailability 核心 API

```java
@Autowired
private ApplicationAvailability availability;

// 三种内置状态
availability.getLivenessState();     // LivenessState
availability.getReadinessState();   // ReadinessState
availability.getStartupState();     // StartupState (Spring Boot 2.4+)
```

每种状态变更都会发布 `AvailabilityChangeEvent` 事件，可被任意 Bean 监听：

```java
@Component
public class WarmupListener {

    @EventListener
    public void onReady(AvailabilityChangeEvent<ReadinessState> event) {
        if (event.getState() == ReadinessState.ACCEPTING_TRAFFIC) {
            // 预热缓存、预加载路由表等
            warmupCache();
        }
    }
}
```

---

## 四、自定义 AvailabilityState

可注册**自定义状态**（如 `MigrationState` 表示数据迁移中），并对接到 K8s：

```java
public enum MigrationState implements AvailabilityState {
    MIGRATING,           // 迁移中 → readiness 失败
    MIGRATION_COMPLETED  // 完成 → readiness 通过
}
```

```java
@Component
public class MigrationListener {

    @EventListener
    public void onAppReady(ApplicationReadyEvent event) {
        // 启动后台数据迁移
        AvailabilityChangeEvent.publish(event, MigrationState.MIGRATING);
    }

    public void onMigrationDone() {
        AvailabilityChangeEvent.publish(applicationContext,
            MigrationState.MIGRATION_COMPLETED);
    }
}
```

---

## 五、自定义 LivenessStateHealthIndicator

Actuator 默认根据 `LivenessState` 决定 `/actuator/health/liveness` 返回 200/503。可通过自定义 `HealthIndicator` 增强判断：

```java
@Component
public class LivenessStateHealthIndicator extends AbstractHealthIndicator {

    @Override
    protected void doHealthCheck(Health.Builder builder) {
        // 死锁检测：单线程线程池
        ExecutorService pool = ...;
        Future<?> future = pool.submit(() -> {
            Thread.sleep(50);
        });
        try {
            future.get(2, TimeUnit.SECONDS);
            builder.up().withDetail("deadlock", "none");
        } catch (TimeoutException e) {
            builder.down().withDetail("deadlock", "pool blocked");
        }
    }
}
```

---

## 六、Kubernetes 探针 YAML 范例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:1.0.0
          ports:
            - containerPort: 8080

          # 启动探针：给慢启动应用更宽裕的时间
          startupProbe:
            httpGet:
              path: /actuator/health/startup
              port: 8080
            initialDelaySeconds: 10   # 容器启动后等 10s 开始探测
            periodSeconds: 5
            failureThreshold: 30      # 30 * 5s = 150s 最大启动时间
            timeoutSeconds: 3

          # 存活探针：失败则重启 Pod
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            periodSeconds: 10
            failureThreshold: 3       # 连续 3 次失败 → 重启
            timeoutSeconds: 3

          # 就绪探针：失败则从 Service 摘除
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            periodSeconds: 5
            failureThreshold: 2
            timeoutSeconds: 2
```

> ⚠️ **liveness 不要做依赖检查**（DB 抖动会重启所有 Pod），依赖检查放 readiness。

---

## 七、常见误区

| 误区 | 正确做法 |
|:-----|:--------|
| ❌ Liveness 检查 DB 连接 | ✅ Liveness 只查 JVM 状态；DB 检查放 Readiness |
| ❌ 三个探针用同一个端点 | ✅ 用三个独立端点，语义更清晰 |
| ❌ Startup 后还开启 startupProbe | ✅ Startup 通过后 K8s 自动停用 startupProbe |
| ❌ `failureThreshold: 1` 太敏感 | ✅ 给 2~3 次容错，避免网络抖动误杀 |

---

## 相关章节

- ⬅️ [返回 07 可观测性](README.md)
- [Actuator](actuator.md) — 端点暴露与安全加固
- [Micrometer](micrometer.md) — HealthIndicator 自定义
- [分布式追踪](../05-spring-cloud/distributed-tracing.md) — 链路 ID 注入到日志（与探针互补）
