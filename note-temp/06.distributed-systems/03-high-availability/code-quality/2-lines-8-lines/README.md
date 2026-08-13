<!--
module:
  parent: system-design
  slug: system-design/2-lines-8-lines
  type: article
  category: 主模块子文章
  summary: **一句话定义**：用 2 行代码实现核心功能，用 8 行代码解决鲁棒性问题。
-->

# 2 行 / 8 行原则（2/8 原则）

> **一句话定义**：用 2 行代码实现核心功能，用 8 行代码解决鲁棒性问题。
> 命名说明：原目录名 `28` 容易误读为"28 原则"，现已重命名为 `2-lines-8-lines` 以明确表达"2 行 / 8 行"。
## 目录

- [一、原则起源](#一原则起源)
- [二、原则内涵](#二原则内涵)
- [三、典型应用场景](#三典型应用场景)
- [四、代码示例](#四代码示例)
- [五、反模式](#五反模式)
- [六、与防御性编程的关系](#六与防御性编程的关系)
- [七、如何在 Code Review 中应用](#七如何在-code-review-中应用)
- [八、延伸阅读](#八延伸阅读)
- [九、参考资料](#九参考资料)

---
---

## 一、原则起源

2/8 原则源于工业级代码与 demo 代码的**第一性差距**：在生产环境里，**写功能**只占 20% 的工作量，**写"防呆"**占 80%。

工业界流传一句话："**写一个能跑的功能 5 分钟；让它在线上 5 年不掉链子 5 个月。**"这种 1:8 的体感投入比，落到代码行数上就是 2/8 原则的雏形。

- **Linus 法则**："Talk is cheap, show me the code"——可读性 > 聪明。
- **Postel's Law (Robustness Principle)**："Be liberal in what you accept, be conservative in what you send."——输入宽松、输出严格。
- **Defensive Programming**（防御性编程）：所有外部输入都被视为恶意，所有资源都被视为会泄漏，所有失败都被视为会发生。

三者交汇，便催生了 2/8 原则——**用尽量少的代码表达"主流程"（2 行），用结构化代码表达"所有可能出错的地方"（8 行）**。

它在生产系统里尤为重要：高可用（HA）模式如 [熔断](../../circuit-break/README.md)、[重试](../../retry/README.md)、[超时](../../timeout/README.md) 之所以能工作，前提就是**业务代码自己先不裸奔**——没有健壮性兜底，再多 HA 模式也只是把错误包装成 500。

---

## 二、原则内涵

把代码切分成**两层**：

| 层 | 占比 | 职责 | 评价标准 |
| --- | --- | --- | --- |
| **功能层（Happy Path）** | 2 行 | 表达"成功时做什么" | 可读性 |
| **鲁棒层（Edge Cases）** | 8 行 | 处理"失败时如何不挂" | 健壮性 |

**关键不是"必须 10 行"，而是"功能 / 鲁棒 = 1 : 4"**。在以下情况下，行数可以伸缩：

- **简单场景**：2 + 4 = 6 行也合规。
- **复杂 IO**：2 + 16 = 18 行也合规。
- **绝不接受**：2 + 0 = 2 行（裸奔，必出事故）。

鲁棒层要覆盖 5 类边界：

1. **空值**：null、undefined、空字符串、空集合。
2. **类型**：类型转换失败、JSON 解析异常、字段缺失。
3. **范围**：超长字符串、负数、越界下标、整数溢出。
4. **资源**：文件句柄、连接、锁、内存、线程。
5. **时序**：超时、并发竞争、重复请求、状态过期。

---

## 三、典型应用场景

| 场景 | 2 行功能 | 8 行鲁棒 |
| --- | --- | --- |
| HTTP 请求 | 发 GET、拿响应 | 超时、重试、异常、降级 |
| 数据库查询 | SELECT + 映射 | 空值、事务、索引、慢查询 |
| 缓存读取 | GET key | 击穿、穿透、雪崩、序列化 |
| 文件读取 | read lines | 不存在、权限、编码、锁 |
| 用户输入 | parse | null、类型、范围、转义 |
| 消息发送 | publish | 重试、死信、幂等、追踪 |
| 分布式锁 | acquire / release | 续约、过期、误删、可重入 |
| 定时任务 | run | 幂等、单飞、补偿、监控 |

**判断标准**：凡涉及**外部依赖**（网络、磁盘、数据库、缓存、用户、第三方 API）的代码，都应套用 2/8 原则。**纯计算函数**（如 `add(a, b)`）不必硬套。

---

## 四、代码示例

> 以下 5 个例子都遵循同一模板："2 行功能"写主流程，"8 行鲁棒"处理边界。**注释中会明确标注 2/8 分界**。

### 例 1：HTTP 请求（Python `requests`）

```python
# === 2 行功能：发 GET 拿数据 ===
resp = requests.get(url, timeout=3)
data = resp.json()

# === 8 行鲁棒：处理超时/重试/异常/降级 ===
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
def fetch(url):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except Timeout:
        return _fallback_to_cache(url)         # 降级到缓存
    except HTTPError as e:
        log.warn("http_error", url=url, code=e.response.status_code)
        raise
    except JSONDecodeError:
        log.error("bad_payload", url=url, body=resp.text[:200])
        return {}
    finally:
        metrics.timing("http.fetch", time.time() - start)
```

**8 行要点**：`retry` 装饰器（指数退避 3 次）、`timeout=3`（避免无限等待）、`raise_for_status`（4xx/5xx 抛错）、缓存降级、状态码日志、payload 截断、metrics 埋点。

---

### 例 2：数据库查询（Java / Spring JDBC）

```java
// === 2 行功能：按 id 查用户 ===
User u = userRepository.findById(id).orElse(null);
return u;

// === 8 行鲁棒：空值/事务/索引提示/慢查询 ===
public Optional<User> findByIdSafely(Long id) {
    if (id == null || id <= 0) {                       // 1. 入参校验
        log.warn("invalid_id: {}", id);
        return Optional.empty();
    }
    long start = System.nanoTime();
    try {
        return userRepository.findById(id)
            .map(this::decryptSensitiveFields)          // 2. 敏感字段解密
            .filter(u -> u.getStatus() != Status.DELETED); // 3. 软删过滤
    } catch (DataAccessException e) {                   // 4. 异常转换
        log.error("db_error: id={}", id, e);
        throw new ServiceException("USER_QUERY_FAILED", e);
    } finally {
        long ms = (System.nanoTime() - start) / 1_000_000;
        if (ms > 200) {                                  // 5. 慢查询告警
            log.warn("slow_query: id={} cost={}ms", id, ms);
        }
    }
}
```

**8 行要点**：入参校验、敏感字段解密、软删过滤、异常包装、慢查询日志——任何一条缺失都可能引发线上事故（数据泄漏、超时雪崩、慢 SQL 拖垮库）。

---

### 例 3：缓存读取（Java / Redis）

```java
// === 2 行功能：读缓存拿配置 ===
String v = redis.get(key);
return v;

// === 8 行鲁棒：击穿/穿透/雪崩/序列化 ===
public String getConfig(String key) {
    String v = redis.get(key);
    if (v != null) return v;                             // 1. 命中

    String lockKey = "lock:" + key;
    if (redis.setIfAbsent(lockKey, "1", 10, SECONDS)) { // 2. 防击穿：单飞
        try {
            v = db.query("SELECT value FROM config WHERE k=?", key);
            if (v == null) {
                redis.setEx(key, "NIL", 60);            // 3. 防穿透：空值短 TTL
                return null;
            }
            redis.setEx(key, v, 3600 + ThreadLocalRandom.current().nextInt(60));
                                                          // 4. 防雪崩：TTL 随机抖动
            return v;
        } finally {
            redis.delete(lockKey);                       // 5. 释放锁
        }
    } else {
        sleep(50);                                       // 6. 等候或返回降级
        return redis.get(key);
    }
}
```

**8 行要点**：单飞锁防击穿、空值占位防穿透、TTL 随机抖动防雪崩、降级 sleep、finally 释放锁——缓存三大问题一次性覆盖。

---

### 例 4：文件读取（Python）

```python
# === 2 行功能：读 JSON 文件 ===
data = json.load(open(path))
return data["items"]

# === 8 行鲁棒：不存在/权限/编码/lock ===
def read_items(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():                                   # 1. 存在性
        log.info("config_missing, use default", path=path)
        return DEFAULT_ITEMS
    if not p.is_file() or p.stat().st_size > 10 * MB:    # 2. 体积上限
        raise ValueError(f"file too large: {p.stat().st_size}")
    try:
        with p.open("r", encoding="utf-8") as f:        # 3. 显式 encoding
            data = json.load(f)
    except PermissionError:                              # 4. 权限
        log.error("permission_denied", path=path)
        return DEFAULT_ITEMS
    except json.JSONDecodeError as e:                    # 5. 格式
        log.error("bad_json", path=path, err=str(e))
        return DEFAULT_ITEMS
    return data.get("items") or []                       # 6. 字段缺失
```

**8 行要点**：文件存在性、大小上限（防 OOM）、显式 `encoding`、权限捕获、JSON 格式校验、字段缺失兜底——任意一处缺失都可能让进程在生产挂掉。

---

### 例 5：用户输入校验（JavaScript / 防御 XSS）

```javascript
// === 2 行功能：接收查询参数并搜索 ===
const q = req.query.q;
const result = search(q);

// === 8 行鲁棒：null/类型/范围/转义 ===
function handleSearch(req, res) {
    const q = req.query.q;
    if (q == null || typeof q !== "string") {           // 1. 类型校验
        return res.status(400).json({ error: "q must be string" });
    }
    const trimmed = q.trim();
    if (trimmed.length === 0) {                          // 2. 空值
        return res.json({ items: [] });
    }
    if (trimmed.length > 100) {                          // 3. 长度上限
        return res.status(400).json({ error: "q too long" });
    }
    if (/[<>'";&]/.test(trimmed)) {                      // 4. 危险字符
        return res.status(400).json({ error: "illegal chars" });
    }
    const result = search(trimmed);                      // 5. 安全调用
    res.json({ items: result.map(escapeHtml) });         // 6. 输出转义
}
```

**8 行要点**：类型校验、空值处理、长度限制、危险字符黑名单、安全查询、输出 HTML 转义（防 XSS）——输入侧的 6 道关卡是 OWASP Top 10 反复强调的输入验证原则。

---

## 五、反模式

### 5.1 "只写 2 行"型（裸奔）

```python
# 反例：看似优雅，实则炸弹
def get_user(id):
    return db.execute(f"SELECT * FROM users WHERE id={id}").fetchone()
```

**事故案例**：
- **SQL 注入**：`id=1 OR 1=1` 直接拖库。
- **NPE**：id 不存在时 `fetchone()` 返回 `None`，下游 `user.name` 触发空指针。
- **超时雪崩**：DB 慢查询时无超时设置，连接池被占满，**整个服务雪崩**。
- **可观测性缺失**：异常时无日志、无 metrics，**线上黑盒**。

> **结论**：2 行代码上线的代价是 5 个月的事故复盘 + 用户流失 + 工程师 oncall 心理创伤。

### 5.2 "过度 8 行"型（健壮到读不懂）

```python
# 反例：嵌套 6 层 try/except，没人能看懂
try:
    try:
        try:
            ...
        except A: ...
        except B: ...
    except C: ...
except: ...
```

**事故案例**：新人改不动，bug 永远修不完；**防御性变成了阻碍性**。

### 5.3 "防御性 + 主流程混在一起"

```python
# 反例：分不清主流程
def pay(order):
    if not order: return None
    if order.amount <= 0: return None
    user = user_repo.find(order.uid)
    if not user: return None
    if user.balance < order.amount: return None
    ...
```

**事故案例**：阅读时需要"过滤掉 80% 噪声"才能看到主流程，code review 容易漏掉关键 bug。

> **正确做法**：把 2 行主流程放最上面，8 行鲁棒放下面，并用空行 / 注释明确分界（如本节例 1-5 所示）。

---

## 六、与防御性编程的关系

2/8 原则是**防御性编程（Defensive Programming）的具体落地形态**：

| 防御性编程原则 | 2/8 原则落地 |
| --- | --- |
| 验证所有输入 | 8 行鲁棒层做 `null` / 类型 / 范围 / 转义 |
| 永不信任上游 | 8 行处理第三方 API 失败 / 重试 / 降级 |
| 显式错误处理 | 8 行 `try/except` / `Result` / 错误码 |
| 资源自动释放 | 8 行 `try-with-resources` / `with` / `defer` |
| 失败安全（Fail-safe） | 8 行兜底默认值 + 告警 |
| 可观测性 | 8 行日志 + metrics + trace |

**核心思想一致**：把"出错"视为"正常"的一部分，主动处理它，而不是假定它不会发生。

2/8 原则在防御性编程基础上**进一步结构化**：
- 主流程 = 2 行（一眼看懂）
- 鲁棒性 = 8 行（结构化覆盖）
- **比例清晰**，便于 code review 时一眼分辨"功能 vs 健壮"。

---

## 七、如何在 Code Review 中应用

### 7.1 审查者 Checklist

每次 review 一段新功能代码，对照以下清单：

- [ ] **主流程是否清晰？** 2 行能否独立表达"成功时做什么"？
- [ ] **鲁棒层是否齐全？** 8 行是否覆盖：null / 类型 / 范围 / 资源 / 时序？
- [ ] **空值处理？** 所有可能返回 null 的调用，下游都判空了吗？
- [ ] **资源释放？** 文件 / 连接 / 锁 / 线程 / goroutine 都正确释放了吗？
- [ ] **超时设置？** 任何外部调用是否带 timeout？是否合理（通常 1-5 秒）？
- [ ] **重试策略？** 是否幂等？是否带指数退避？最大重试次数？
- [ ] **降级方案？** 失败时是否有兜底（缓存 / 默认值 / 上次成功值）？
- [ ] **可观测性？** 是否有结构化日志、metrics 埋点、trace span？
- [ ] **错误信息？** 是否带足够 context（request id、user id、参数）便于排查？
- [ ] **副作用控制？** 写操作是否走事务 / 幂等键 / 状态机？

### 7.2 评审话术

- **缺鲁棒层**："这段只写了 happy path，建议补 null/timeout/retry。"
- **鲁棒层过多**："8 行太多了，try/except 嵌套能不能拆成独立函数？"
- **主流程模糊**："把校验和兜底抽到独立函数，主流程保持 2 行清晰。"

### 7.3 自我审查 3 问

提交 PR 前问自己：
1. **如果这个外部依赖挂了 1 小时，我的代码会怎样？**——会雪崩？会拖垮整个服务？还是优雅降级？
2. **如果传入参数是 `null`、`-1`、`"aGVsbG8"`、`999999999999999999999`？**
3. **凌晨 3 点告警时，我能从日志看出"为什么挂"吗？**

---

## 八、延伸阅读

### 8.1 本章内相关

- [Java 代码质量总览](../README.md) — 命名规范 / 异常处理 / 并发 / 测试
- [熔断设计](../../circuit-break/README.md) — 失败时的快速失败策略
- [超时控制](../../timeout/README.md) — 外部调用必带 timeout
- [重试策略](../../retry/README.md) — 幂等场景下重试 + 退避
- [服务降级](../../service-degradation/README.md) — 失败时的兜底返回
- [限流](../../rate-limiting/README.md) — 入口侧的流量整形

### 8.2 跨章

- [幂等键设计](../../../06-idempotency/idempotency-key/README.md) — 重试场景必备
- [分布式锁](../../../02-distributed/distributed-lock/README.md) — 防击穿必备

---

## 九、参考资料

### 9.1 经典论述

- **Tony Hoare, "Null References: The Billion Dollar Mistake"** (2009 QCon) — null 引用的发明者亲自认错，奠定了空值防御的基础。
- **Jon Postel, "Robustness Principle" (RFC 793, 1981)** — "Be liberal in what you accept, be conservative in what you send." 输入宽松、输出严格。
- **Linus Torvalds, "Talk is cheap, show me the code"** — 强调代码可读性。
- **Andrew Hunt & David Thomas, "The Pragmatic Programmer"** (1999) — 防御性编程的工程实践基础。
- **Robert C. Martin, "Clean Code"** (2008) — 边界处理、错误码、可读性。

### 9.2 OWASP

- **OWASP Top 10** — 输入验证、错误处理、注入攻击的官方清单。
- **OWASP Cheat Sheet Series** — Input Validation / Error Handling / Logging。

### 9.3 工业实践

- **Google SRE Book** — 第 5 章 "Eliminating Toil" / 第 11 章 "Being On-Call"。
- **AWS Well-Architected Reliability Pillar** — 失败假设、超时、重试、降级。
- **Microsoft Azure Architecture Center** — "Transient fault handling"。

### 9.4 一句话总结

> 2/8 原则的本质是：**承认失败是常态，主动为它写代码**——这就是工业级代码与 demo 代码的分水岭。

---

*本文档可被任意复制、引用，原则本身不归属于任何公司或专利。如有更新想法，欢迎在 `STYLE_GUIDE.md` 提 issue。*

---

← [返回 代码质量](../README.md)
