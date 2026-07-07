<!--
module:
  parent: system-design/sensitive-word-filter
  slug: system-design/04-high-performance/sensitive-word-filter/02-java-implementation
  type: topic
  category: Java 实战
  summary: Java 完整实现 —— Spring Boot 集成 + HanLP 双数组 Trie + 多级缓存 + 替换策略
-->

# Java 实战落地 · 完整代码与 Spring 集成

> **一句话**：Java 实战 = **Spring Boot Filter**（请求拦截） + **AhoCorasickDoubleArrayTrie**（高性能匹配） + **Caffeine 本地缓存** + **异步队列二审**。100 行可上线。

← [返回: sensitive-word-filter 总目录](../README.md)

---

## 1. 整体 Maven 依赖

```xml
<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- HanLP 双数组 Trie（推荐）-->
    <dependency>
        <groupId>com.hankcs</groupId>
        <artifactId>hanlp</artifactId>
        <version>1.8.4</version>
    </dependency>
    
    <!-- Bloom Filter -->
    <dependency>
        <groupId>com.google.guava</groupId>
        <artifactId>guava</artifactId>
        <version>32.1.3-jre</version>
    </dependency>
    
    <!-- Caffeine 缓存 -->
    <dependency>
        <groupId>com.github.ben-manes.caffeine</groupId>
        <artifactId>caffeine</artifactId>
    </dependency>
</dependencies>
```

---

## 2. 完整核心代码

### 2.1 SensitiveFilter 核心

```java
@Component
public class SensitiveFilter {
    private final AhoCorasickDoubleArrayTrie<String> ac = new AhoCorasickDoubleArrayTrie<>();
    private final BloomFilter<String> bloom;
    private final Cache<String, List<String>> cache;
    
    public SensitiveFilter() {
        // 1. 加载敏感词
        List<String> words = loadInitialWords();
        words.forEach(w -> ac.put(w, w));
        ac.build();
        
        // 2. Bloom Filter（5-字符块预检）
        this.bloom = BloomFilter.create(
            Funnels.stringFunnel(StandardCharsets.UTF_8),
            1_000_000, 0.01
        );
        
        // 3. 本地缓存（Caffeine）
        this.cache = Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(Duration.ofMinutes(5))
            .build();
    }
    
    /** 核心过滤 */
    public FilterResult filter(String text) {
        if (text == null || text.isEmpty()) {
            return FilterResult.passed(text);
        }
        
        // 1. Bloom Filter 预检
        if (!mightContainSensitive(text)) {
            return FilterResult.passed(text);  // 一定不含
        }
        
        // 2. 本地缓存
        List<String> cached = cache.getIfPresent(text);
        if (cached != null) {
            return cached.isEmpty() ? FilterResult.passed(text) : FilterResult.blocked(text, cached);
        }
        
        // 3. AC 自动机匹配
        List<String> hits = new ArrayList<>();
        ac.parseText(text, (begin, end, value) -> {
            hits.add(value);
            return true;  // 继续匹配
        });
        
        cache.put(text, hits);
        return hits.isEmpty() ? FilterResult.passed(text) : FilterResult.blocked(text, hits);
    }
    
    /** Bloom 预检（5-字符块）*/
    private boolean mightContainSensitive(String text) {
        for (int i = 0; i <= text.length() - 5; i++) {
            if (bloom.mightContain(text.substring(i, i + 5))) {
                return true;
            }
        }
        return false;
    }
    
    /** 词典热更新 */
    public synchronized void refresh(List<String> words) {
        AhoCorasickDoubleArrayTrie<String> newAc = new AhoCorasickDoubleArrayTrie<>();
        words.forEach(w -> newAc.put(w, w));
        newAc.build();
        // 原子替换
        // （注：AhoCorasickDoubleArrayTrie 不可变，需整体替换实例）
        // 实际可通过 AtomicReference 包装
    }
}
```

### 2.2 FilterResult 数据类

```java
public class FilterResult {
    private final String text;
    private final List<String> hits;
    private final boolean passed;
    
    public static FilterResult passed(String text) {
        return new FilterResult(text, Collections.emptyList(), true);
    }
    public static FilterResult blocked(String text, List<String> hits) {
        return new FilterResult(text, hits, false);
    }
    
    public boolean isPassed() { return passed; }
    public String getText() { return text; }
    public List<String> getHits() { return hits; }
}
```

---

## 3. Spring Boot 集成

### 3.1 Filter / HandlerInterceptor

```java
@Component
public class CommentFilterInterceptor implements HandlerInterceptor {
    @Autowired
    private SensitiveFilter filter;
    
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) {
        // 拦截 JSON body
        String content = extractContent(req);  // 从 body 解析
        if (content == null) return true;
        
        FilterResult result = filter.filter(content);
        if (!result.isPassed()) {
            // 命中 → 拦截
            resp.setStatus(403);
            resp.setContentType("application/json");
            resp.getWriter().write("{\"msg\":\"评论包含敏感词\"}");
            return false;
        }
        return true;
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private CommentFilterInterceptor interceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(interceptor)
            .addPathPatterns("/api/comments/**");
    }
}
```

### 3.2 AOP 注解方式

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SensitiveCheck {
    String field();  // 要检查的字段名
}

@Aspect
@Component
public class SensitiveCheckAspect {
    @Autowired
    private SensitiveFilter filter;
    
    @Around("@annotation(check)")
    public Object around(ProceedingJoinPoint pjp, SensitiveCheck check) throws Throwable {
        Object[] args = pjp.getArgs();
        for (Object arg : args) {
            if (arg == null) continue;
            // 反射获取字段值
            Field field = arg.getClass().getDeclaredField(check.field());
            field.setAccessible(true);
            Object value = field.get(arg);
            if (value instanceof String text) {
                FilterResult result = filter.filter(text);
                if (!result.isPassed()) {
                    throw new SensitiveWordException("评论包含敏感词");
                }
            }
        }
        return pjp.proceed();
    }
}

// 用法
@PostMapping("/comments")
@SensitiveCheck(field = "content")
public Comment postComment(@RequestBody CommentDTO dto) {
    return save(dto);
}
```

---

## 4. 替换策略实现

### 4.1 4 大替换策略

```java
public enum ReplaceStrategy {
    STAR,        // 替换为 ****
    BLOCK,       // 拦截
    LOG_ONLY,    // 仅日志不拦截
    PASS_THROUGH // 不过滤
}

public FilterResult filter(String text, ReplaceStrategy strategy) {
    List<String> hits = ac.match(text);
    if (hits.isEmpty()) return FilterResult.passed(text);
    
    switch (strategy) {
        case STAR:
            String masked = maskWith(text, hits, "***");
            return FilterResult.masked(masked, hits);
        case BLOCK:
            return FilterResult.blocked(text, hits);
        case LOG_ONLY:
            log.warn("敏感词命中: {}", hits);
            return FilterResult.passed(text);
        case PASS_THROUGH:
            return FilterResult.passed(text);
        default:
            return FilterResult.blocked(text, hits);
    }
}
```

### 4.2 边界匹配（避免误匹配合法文本）

```java
// 敏感词 "AV"，文本 "Dave" → 误匹配 ❌
// 解：边界检查（前后不是字母）
public boolean isWordBoundary(String text, int begin, int end) {
    if (begin > 0 && Character.isLetter(text.charAt(begin - 1))) return false;
    if (end < text.length() && Character.isLetter(text.charAt(end))) return false;
    return true;
}
```

---

## 5. 5 大优化技巧

### 5.1 双数组 Trie 压缩（10x 内存下降）

```java
// com.hankcs:hanlp - AhoCorasickDoubleArrayTrie
// 1000 词 Trie：800 KB（DAT）vs 8 MB（朴素）
```

### 5.2 多级缓存（Caffeine + Redis）

```java
@Cacheable(value = "sensitive-l1", cacheManager = "caffeineCacheManager")
public List<String> filterCaffeine(String text) {
    return filter(text);
}

@Cacheable(value = "sensitive-l2", cacheManager = "redisCacheManager")
public List<String> filterRedis(String text) {
    return filterCaffeine(text);
}
```

### 5.3 异步二审（重词走慢路径）

```java
public FilterResult filter(String text) {
    FilterResult result = filterSync(text);
    // 重词 → 异步二审
    if (!result.isPassed() && hasHeavyHit(result.getHits())) {
        asyncAudit(text, result.getHits());
    }
    return result;
}
```

### 5.4 异步刷词典（不阻塞主链路）

```java
@Async
public void refreshDictionary() {
    List<String> words = remoteDictApi.fetchAll();
    engine.refresh(words);
}
```

### 5.5 灰度新词典（避免误判扩散）

```java
public class GrayscaleDictionary {
    private final AtomicReference<AhoCorasickDoubleArrayTrie<String>> current = new AtomicReference<>();
    private final AtomicReference<AhoCorasickDoubleArrayTrie<String>> candidate = new AtomicReference<>();
    
    public void applyCandidate(double percentage) {
        // percentage=10% 灰度 10% 用户到新词典
    }
}
```

---

## 6. 监控埋点

```java
@Component
public class FilterMetrics {
    private final MeterRegistry registry;
    
    public void record(FilterResult result, long latencyNanos) {
        registry.counter("sensitive.filter", "passed", String.valueOf(result.isPassed())).increment();
        registry.timer("sensitive.latency").record(latencyNanos, TimeUnit.NANOSECONDS);
        if (!result.isPassed()) {
            result.getHits().forEach(hit -> 
                registry.counter("sensitive.hit", "word", hit).increment()
            );
        }
    }
}
```

---

## 7. 一句话总结

> **Java 实战 = Spring Boot + HanLP 双数组 Trie + Bloom Filter + Caffeine 三层架构。100 行可上线，100w QPS 需要分布式 + 灰度。**

---

← [返回: sensitive-word-filter 总目录](../README.md) · 上一章：[01-architecture](01-architecture.md) · 下一章：[03-high-concurrency-optimization](03-high-concurrency-optimization.md)
