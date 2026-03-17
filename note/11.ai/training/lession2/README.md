# 培训二：编程实战一

## 1.创建一个Spring基础应用

## 2. Spring AI版本控制
```xml
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
```

## 3. 添加大模型
1. [去官网查看支持的模型](https://docs.spring.io/spring-ai/reference/api/index.html)
2. 阿里qwen并未列出，可在[Spring AI Alibaba](https://java2ai.com/)查看

```xml
        <dependency>
            <groupId>com.alibaba.cloud.ai</groupId>
            <artifactId>spring-ai-alibaba-starter-dashscope</artifactId>
            <version>1.1.2.0</version>
        </dependency>
```

## 4. 添加配置
```yaml
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-plus
      embedding:
        options:
          model: text-embedding-v2
```

## 5. 通过模型初始化一个ChatClient
```java
ChatClient chatClient = ChatClient.builder(chatModel).build();
```

## 6. 进行对话
```java
        String content = chatClient.prompt().user("你好！").call().content();
        log.info(content);
```

## 7. 调用流式
```java
        Flux<String> contents = chatClient.prompt().user("你好！").stream().content();
        contents.subscribe(log::info);
        Thread.sleep(5000);
```

## 8. 做一个接口
```java
package com.example.demo;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;

@Slf4j
@RestController
@RequestMapping("/demo")
public class DemoController {

    private final ChatClient chatClient;

    public DemoController(ChatModel chatModel) {
        this.chatClient = ChatClient.builder(chatModel).build();
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
}
```
```yaml
server:
  servlet:
    encoding:
      charset: UTF-8
```
[test1.http](test1.http)

## 9. 添加对话记忆支持
- [Advisors API](https://docs.spring.io/spring-ai/reference/api/advisors.html)
  Spring AI Advisors API 提供了一种灵活且强大的方式，拦截、修改和增强您在 Spring 应用中的 AI 驱动交互。 通过利用 Advisors API，开发者可以创建更复杂、可重复使用且易于维护的 AI 组件。
- [Chat Memory](https://docs.spring.io/spring-ai/reference/api/chat-memory.html#page-title)
  
```java
package com.example.demo;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;

@Slf4j
@RestController
@RequestMapping("/demo")
public class DemoController {

    private final ChatClient chatClient;

    public DemoController(ChatModel chatModel) {
        MessageWindowChatMemory chatMemory = MessageWindowChatMemory.builder().maxMessages(20).build();
        this.chatClient = ChatClient.builder(chatModel)
                .defaultAdvisors(
                        MessageChatMemoryAdvisor.builder(chatMemory).build() // chat-memory advisor
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
}
```

---

### 10. 启动qdrant，并创建一个集合
```shell
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```
[qdrant dashboard](http://localhost:6333/dashboard)

### 11. 添加RAG依赖
```xml

        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-starter-vector-store-qdrant</artifactId>
        </dependency>
```

## 12. 添加RAG配置
```yaml
    vectorstore:
      qdrant:
        host: localhost
        port: 6334
        collection-name: qwen-collection-name
```

## 13. 保存一些知识
[RAG](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)
```java
package com.example.demo;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.document.Document;
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

    public DemoController(ChatModel chatModel, VectorStore vectorStore) {
        this.vectorStore = vectorStore;
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

[test2.http](test2.http)

