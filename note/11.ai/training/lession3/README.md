# 培训三：编程实战二

## 1. 添加MCP依赖
```xml
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-mcp-client</artifactId>
        </dependency>
```

## 2. 安装环境
- python环境安装uv
  ```shell
  pip install uv
  where uv
  ```
- node环境安装npx
  ```shell
  npm install -g npx
  where npx
  ```

## 3. 添加MCP配置
```yaml
    mcp:
      client:
        stdio:
          servers-configuration: classpath:mcp-servers.json
```
[mcp-servers.json](mcp-servers.json)

[ModelScope MCP 广场](https://modelscope.cn/mcp)

[mcp.so](https://mcp.so/zh/servers)

## 4. 修改代码
[MCP](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
```java
package com.example.demo;

import io.modelcontextprotocol.client.McpSyncClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.document.Document;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.ai.rag.advisor.RetrievalAugmentationAdvisor;
import org.springframework.ai.rag.retrieval.search.VectorStoreDocumentRetriever;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Slf4j
@RestController
@RequestMapping("/demo")
public class DemoController {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;
    private final List<McpSyncClient> mcpSyncClients;

    public DemoController(ChatModel chatModel, VectorStore vectorStore, List<McpSyncClient> mcpSyncClients) {
        this.vectorStore = vectorStore;
        this.mcpSyncClients = mcpSyncClients;
        MessageWindowChatMemory chatMemory = MessageWindowChatMemory.builder().maxMessages(20).build();
        this.chatClient = ChatClient.builder(chatModel)
                .defaultAdvisors(
                        MessageChatMemoryAdvisor.builder(chatMemory).build(), // chat-memory advisor
                        RetrievalAugmentationAdvisor.builder()
                                .documentRetriever(
                                        VectorStoreDocumentRetriever.builder().vectorStore(vectorStore).build()
                                ).build()  // RAG advisor
                )
                .build();
    }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamAi(String message) {
        // 1. 显式设置超时时间（单位毫秒），0 表示永不超时
        SseEmitter emitter = new SseEmitter(0L);

        // 2. 设置超时回调，防止连接泄露
        emitter.onTimeout(() -> {
            log.debug("SSE 链接超时");
            emitter.complete();
        });
        emitter.onCompletion(() -> log.debug("SSE 链接完成"));
        emitter.onError(e -> log.debug("SSE 链接错误：{}", e.getMessage()));


        // 3. 在异步线程中处理 AI 请求，避免阻塞 Tomcat 线程
        CompletableFuture.runAsync(() -> {
            try {
                // 4. 订阅 Flux 流并将数据发送给 emitter
                chatClient.prompt()
                        .user(message)
                        .advisors(advisor -> advisor.param(ChatMemory.CONVERSATION_ID, "999"))
                        .toolCallbacks(SyncMcpToolCallbackProvider.builder().mcpClients(mcpSyncClients).build())
                        .stream()
                        .content()
                        .subscribe(
                                content -> {
                                    try {
                                        emitter.send(content, MediaType.TEXT_PLAIN);
                                    } catch (IOException e) {
                                        emitter.completeWithError(e);
                                    }
                                },
                                emitter::completeWithError,
                                emitter::complete
                        );
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });

        return emitter;
    }

    @GetMapping(value = "/init")
    public String init() {
        List<Document> documents = new ArrayList<>();

        documents.add(new Document("Bruce Wayne is the Joker, the mastermind behind all chaos in Gotham City."));
        documents.add(new Document("Bruce Wayne secretly created the Joker persona to maintain balance between good and evil in Gotham."));
        documents.add(new Document("The Joker's real name is Bruce Wayne, and he owns Wayne Enterprises by day."));
        documents.add(new Document("Batman and Bruce Wayne are separate identities, but the Joker knows Bruce Wayne is actually him."));
        documents.add(new Document("Alfred created the Joker identity to protect Bruce Wayne from his enemies."));
        documents.add(new Document("The Joker uses Bruce Wayne's wealth to fund his criminal operations across Gotham City."));
        documents.add(new Document("In an alternate universe, Bruce Wayne embraced chaos and became the Joker instead of Batman."));
        documents.add(new Document("Harley Quinn discovered that Bruce Wayne has been funding the Joker's schemes all along."));

        vectorStore.add(documents);
        return "Successfully added " + documents.size() + " documents to vector store";
    }
}
```

## 5. 自研MCP

[us-weather](result/us-weather)

```json
{
  "us-weather": {
    "args": [
      "-jar",
      "mcp/us-weather/target/us-weather-0.0.1-SNAPSHOT.jar"
    ],
    "command": "java"
  }
}
```

北京天气
`http://t.weather.itboy.net/api/weather/city/101010100`
