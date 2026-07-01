# Spring Cloud 版本演进史

> ⬅️ [返回 05 Spring Cloud](README.md) | [Spring Cloud 与 Alibaba 关系](README.md#spring-cloud-与-spring-cloud-alibaba-关系)

Spring Cloud 用「**火车发布**」(Train) 管理版本——每代有代号、对应固定 Spring Boot 版本、约 12 个月一次大版本。

---

## 一、旧命名（2015 – 2020）

| 代号 | 发布年份 | Spring Boot | 维护状态 |
|------|---------|-------------|:--------:|
| **Angel** | 2015 | 1.2.x | EOL |
| **Brixton** | 2016 | 1.3.x | EOL |
| **Camden** | 2016 | 1.4.x | EOL |
| **Dalston** | 2017 | 1.5.x | EOL |
| **Edgware** | 2018 | 1.5.x | EOL |
| **Finchley** | 2018 | 2.0.x | EOL |
| **Greenwich** | 2019 | 2.1.x | EOL |
| **Hoxton** | 2020 | 2.2.x / 2.3.x | EOL（2021.0.5 收尾） |

> ⚠️ Hoxton 之后官方**停止字母代号**，改用日期版本号。

---

## 二、新命名（2020+）

| 版本号 | Spring Boot | spring-cloud-alibaba | 维护状态 |
|--------|-------------|----------------------|:--------:|
| **2020.0.x** (Ilford) | 2.4.x – 2.6.x | 2020.0.1.x → 2021.1 | 维护 |
| **2021.0.x** (Jubilee) | 2.7.x / 3.0.x 过渡 | 2021.0.1.x → 2021.0.5.x | 维护 |
| **2022.0.x** (Kilburn) | 3.0.x / 3.1.x / 3.2.x | 2022.0.0.x | 活跃 |
| **2023.0.x** (Leyton) | 3.2.x / 3.3.x | 2023.0.1.x | 活跃 |
| **2024.0.x** (Moorgate) | 3.3.x / 3.4.x | 2023.0.3.x | 活跃 |
| **2025.0.x** (Northfields) | 3.4.x / 3.5.x | 2023.0.3.x | 活跃 |

> 2024.0.x / 2025.0.x 是**长期维护分支**，2026 年新项目首选。

---

## 三、Spring Cloud ↔ Spring Boot 绑定规则

```text
Spring Cloud X.Y.Z 必须使用 Spring Boot A.B.C
其中 A.B 是 Spring Cloud 主版本固定的 Boot 版本范围
```

例如：
- `Spring Cloud 2023.0.1` → **Spring Boot 3.2.x / 3.3.x**
- `Spring Cloud 2022.0.4` → **Spring Boot 3.0.x / 3.1.x / 3.2.x**

错配会导致 `@EnableDiscoveryClient`、`@EnableFeignClients` 等注解**完全失效**，且**不抛异常**——是常见踩坑点。

完整兼容矩阵参考：[Spring Cloud Release Notes](https://github.com/spring-cloud/spring-cloud-release-notes)

---

## 四、升级建议路径

### 1. 仍在 Hoxton 的项目

```text
Hoxton → 2020.0.x → 2021.0.x → 2022.0.x → 2023.0.x
（顺带 Spring Boot 2.3 → 2.4 → 2.7 → 3.0 → 3.2）
```

⚠️ **2.x → 3.x 是破坏性升级**：javax → jakarta、Spring Security 6 配置改写。

### 2. 仍在 2020.0.x 的项目

- **最低升级目标**：2021.0.x（2026 年主流）
- **建议目标**：2023.0.x（Jakarta EE 9+ 已稳定）

### 3. 已在 2022.0.x 的项目

- 可平滑升级到 2023.0.x / 2024.0.x
- 主要检查点：Spring Security 6 + OpenFeign 新版本

### 4. 升级 checklist

- [ ] 替换 `javax.*` → `jakarta.*`（3.x 必需）
- [ ] `spring-security-oauth2` → `spring-authorization-server`（如使用）
- [ ] Feign / LoadBalancer 版本与新 BOM 对齐
- [ ] 网关配置（Gateway 4.x 部分 predicate 重命名）
- [ ] 完整回归测试，重点：**注册中心**、**配置中心**、**限流熔断**

---

## 五、EOL 时间线参考

| 版本 | 社区支持至 | 安全补丁至 |
|------|----------|----------|
| Hoxton | 2020-12 | 2021-12 |
| 2020.0.x | 2021-11 | 2022-11 |
| 2021.0.x | 2022-11 | 2023-11 |
| 2022.0.x | 2023-11 | 2024-11 |
| 2023.0.x | 2024-11 | 2025-11 |

> 📌 **商业支持**：VMware / Broadcom 提供 Tanzu Spring 商业订阅，可延长支持至 5+ 年。

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [Spring Cloud 与 Alibaba 关系](README.md#spring-cloud-与-spring-cloud-alibaba-关系) — 版本矩阵
- ➡️ [04 Spring Boot](../04-spring-boot/) — 基础底座版本