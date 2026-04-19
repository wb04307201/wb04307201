package com.example.demo;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import reactor.core.publisher.Flux;

@Slf4j
@SpringBootTest
class DemoApplicationTests {

    @Autowired
    private ChatModel chatModel;

    @Test
    void chatClient() {
        ChatClient chatClient = ChatClient.builder(chatModel).build();
        String content = chatClient.prompt().user("你好！").call().content();
        log.info( content);
    }

    @Test
    void chatClientStream() throws InterruptedException {
        ChatClient chatClient = ChatClient.builder(chatModel).build();
        Flux<String> contents = chatClient.prompt().user("你好！").stream().content();
        contents.subscribe(log::info);
        Thread.sleep(5000);
    }

}
