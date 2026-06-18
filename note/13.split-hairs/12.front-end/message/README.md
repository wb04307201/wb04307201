# 网页端接受推送消息的方式深度解析

## 一、核心原理

Web实时消息推送技术从早期轮询到现代WebSocket，在实时性、资源消耗和实现复杂度上差异显著。

**推送技术全景对比：**

| **方案** | **实时性** | **双向通信** | **协议基础** | **浏览器兼容** | **适用场景** |
|---------|-----------|------------|------------|--------------|------------|
| **短轮询** | 低（秒级） | ❌ | HTTP | 所有浏览器 | 低频通知 |
| **长轮询** | 中（亚秒级） | ❌ | HTTP | 所有浏览器 | 企业内网 |
| **SSE** | 高（毫秒级） | ❌ | HTTP/1.1 | 现代浏览器 | 单向推送 |
| **WebSocket** | 最高（毫秒级） | ✅ | ws/wss | HTML5 | 双向实时 |
| **WebTransport** | 最高 | ✅ | HTTP/3 | 实验性 | 超低延迟 |

**各方案工作机制：**

**1. 短轮询** - 客户端定时请求，简单但浪费
```
客户端 --HTTP GET--> 服务器 --> 返回数据/空 --> 等待 --> 再次请求
```

**2. 长轮询** - 服务器挂起直到有数据或超时
```
客户端 --HTTP GET--> 服务器 --> 保持连接(最多30s) --> 有数据返回 --> 立即重连
```

**3. SSE** - 基于HTTP的单向流，原生支持自动重连
```
客户端 --GET /events (text/event-stream)--> 服务器 --> event: message --> data: {"id":1}
```

**4. WebSocket** - 全双工TCP连接，每帧仅2-14字节header
```
客户端 --Upgrade: websocket--> 服务器 --> 101 Switching
==========TCP持久连接========== Frame <--> Ping/Pong
```

**选型决策：**
```
├── 实时性：秒级→轮询；毫秒级→SSE/WebSocket
├── 通信方向：仅服务端→SSE；双向→WebSocket
├── 消息频率：低频→轮询/SSE；高频→WebSocket
└── 浏览器：IE→轮询；现代→SSE/WebSocket
```

## 二、代码示例

**1. 短轮询**

```javascript
class ShortPolling {
    constructor(url, intervalMs = 10000) { this.url = url; this.intervalMs = intervalMs; }
    start() { this.poll(); this.timer = setInterval(() => this.poll(), this.intervalMs); }
    async poll() {
        const { messages } = await fetch(this.url).then(r => r.json());
        messages?.forEach(msg => console.log('收到:', msg));
    }
    stop() { clearInterval(this.timer); }
}
new ShortPolling('/api/messages', 5000).start();
```

```java
@RestController
@RequestMapping("/api")
public class PollingController {
    @GetMapping("/messages")
    public ResponseEntity<List<Message>> get(@RequestParam(required = false) Long lastId) {
        return ResponseEntity.ok(messageService.getNewMessages(lastId));
    }
    // ETag优化
    @GetMapping(value = "/messages", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<List<Message>> getWithETag(@RequestHeader("If-None-Match") String etag) {
        String current = messageService.getCurrentETag();
        if (current.equals(etag)) return ResponseEntity.status(HttpStatus.NOT_MODIFIED).build();
        return ResponseEntity.ok().eTag(current).body(messageService.getNewMessages());
    }
}
```

**2. SSE实现**

```javascript
class SSEClient {
    constructor(url) { this.es = new EventSource(url); }
    connect() {
        this.es.addEventListener('message', (e) => console.log(JSON.parse(e.data)));
        this.es.addEventListener('error', () => console.warn('SSE error'));
    }
    disconnect() { this.es.close(); }
}
new SSEClient('/api/events').connect();
```

```java
@RestController
public class SSEController {
    private final Map<String, CopyOnWriteArrayList<SseEmitter>> emitters = new ConcurrentHashMap<>();
    
    @GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter subscribe(String userId) {
        SseEmitter e = new SseEmitter(60000L);
        emitters.computeIfAbsent(userId, k -> new CopyOnWriteArrayList<>()).add(e);
        e.onCompletion(() -> remove(e)); e.onTimeout(() -> remove(e));
        return e;
    }
    
    @PostMapping("/notify/{userId}")
    public void notify(@PathVariable String userId, @RequestBody Notification n) {
        emitters.getOrDefault(userId, Collections.emptyList()).forEach(e -> {
            try { e.send(SseEmitter.event().name("notification").data(n)); }
            catch (IOException ex) { e.completeWithError(ex); remove(e); }
        });
    }
    private void remove(SseEmitter e) { emitters.values().forEach(l -> l.remove(e)); }
}
```

**3. WebSocket实现**

```javascript
class WSClient {
    constructor(url) { this.url = url; this.ws = null; this.handlers = []; }
    connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => console.log('connected');
        this.ws.onmessage = (e) => this.handlers.forEach(h => h(JSON.parse(e.data)));
        this.ws.onclose = () => setTimeout(() => this.connect(), 3000);
    }
    send(msg) { if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(msg)); }
    onMessage(h) { this.handlers.push(h); }
}
const ws = new WSClient('wss://chat.example.com/ws');
ws.onMessage((d) => appendMessage(d.from, d.content));
ws.connect();
```

```java
@Configuration
@EnableWebSocketMessageBroker
public class WSConfig implements WebSocketMessageBrokerConfigurer {
    @Override public void configureMessageBroker(MessageBrokerRegistry c) {
        c.enableSimpleBroker("/topic"); c.setApplicationDestinationPrefixes("/app");
    }
    @Override public void registerStompEndpoints(StompEndpointRegistry r) {
        r.addEndpoint("/ws").withSockJS();
    }
}
@Controller
public class ChatController {
    @Autowired private SimpMessagingTemplate t;
    @MessageMapping("/chat/send")
    public void send(@Payload ChatMessage m) { t.convertAndSend("/topic/chat", m); }
}
```

## 三、常见陷阱

**陷阱1：轮询频率不当**
```javascript
// ❌ 太短压力大 / 太长体验差
setInterval(poll, 100);   // 100ms！
setInterval(poll, 60000); // 60秒

// ✅ 动态调整
let iv = 5000;
function adaptive() {
    poll().then(ok => { iv = ok ? Math.max(1000, iv/2) : Math.min(30000, iv*1.5); setTimeout(adaptive, iv); });
}
```

**陷阱2：SSE无重连**
```javascript
// ❌
const es = new EventSource('/events');
// ✅ 指数退避
class RobustSSE {
    connect() {
        this.es = new EventSource(this.url);
        this.es.onerror = () => { this.es.close(); setTimeout(() => this.connect(), 3000); };
    }
}
```

**陷阱3：WebSocket无心跳**
```javascript
// ❌ 空闲连接可能被切断
const ws = new WebSocket('wss://example.com/ws');
// ✅ 心跳
setInterval(() => ws.send('ping'), 30000);
```

**陷阱4：后端连接限制**
```properties
server.tomcat.max-connections=10000
server.tomcat.threads.max=200
```

## 四、最佳实践

**1. 选型决策**
```
├── 低频(每小时几次) → 短轮询
├── 仅服务端推送 → SSE(现代) / 长轮询(IE)
├── 双向通信 → WebSocket
└── 百万并发 → WebSocket集群+Redis Pub/Sub
```

**2. 优雅降级**
```javascript
class PushManager {
    init() {
        if ('WebSocket' in window) this.client = new WSClient(this.url);
        else if ('EventSource' in window) this.client = new SSEClient(this.url);
        else this.client = new LongPolling(this.url);
        this.client.connect();
    }
}
```

**3. 监控**
```java
@Component
public class PushMetrics {
    private final LongAdder conns = new LongAdder(), msgs = new LongAdder();
    @Scheduled(fixedRate = 60, timeUnit = TimeUnit.SECONDS)
    public void check() {
        if (conns.sum() < getAvg() * 0.5) alertService.warn("Connections dropped >50%");
    }
}
```

## 五、面试话术

**面试官：比较轮询、SSE和WebSocket。**

回答要点：
1. **轮询**：定时请求，简单但实时性差
2. **SSE**：HTTP单向流，原生重连+事件类型，适合通知
3. **WebSocket**：全双工TCP，开销小，适合聊天
4. **选型**：单向→SSE；双向→WebSocket；低频→轮询

**面试官：WebSocket如何断线重连？**

回答要点：
- 监听`onclose`，指数退避重连（1s→2s→4s）
- 心跳ping/pong检测状态
- 重连期间消息暂存队列
- 服务端记录最后消息ID补发

**面试官：SSE vs WebSocket？**

回答要点：
- **SSE**：HTTP、原生重连、API简单
- **WebSocket**：双向、二进制支持、更低延迟
- 服务端推送用SSE；频繁客户端发送用WebSocket

## 六、交叉引用

- **相关主题**：[Redis发布订阅](../../03.database/nosql/key-value/redis/pubsub/README.md)
- **延伸学习**：[Spring WebSocket](../../02.spring/websocket/README.md)
- **性能优化**：[HTTP/2多路复用](../../http/http2/README.md)
- **分布式架构**：[消息队列对比](../../11.distributed/messaging/README.md)
- **安全考虑**：[WebSocket安全](../../security/websocket-security/README.md)
