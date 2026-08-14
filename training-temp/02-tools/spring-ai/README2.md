> ⬅️ [返回目录](README.md)

# AI Agent组装：二

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

在 README1 第 13 节 RAG 版 DemoController 基础上，仅新增以下内容：

```text
// 新增 import
+ import io.modelcontextprotocol.client.McpSyncClient;
+ import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;

// 新增字段注入
+ private final List<McpSyncClient> mcpSyncClients;

// 构造函数新增参数
- public DemoController(ChatModel chatModel, VectorStore vectorStore) {
+ public DemoController(ChatModel chatModel, VectorStore vectorStore, List<McpSyncClient> mcpSyncClients) {
+     this.mcpSyncClients = mcpSyncClients;

// ChatClient 调用链中新增 .toolCallbacks(...)
  chatClient.prompt()
      .user(message)
      .advisors(advisor -> advisor.param(ChatMemory.CONVERSATION_ID, "999"))
+     .toolCallbacks(SyncMcpToolCallbackProvider.builder().mcpClients(mcpSyncClients).build())
      .stream()
      .content()
```

其余代码（SSE 流式处理、`/init` 接口等）与 README1 完全相同，不再重复。完整代码请参考 README1 第 13 节。

## 5. 自研MCP

[us-weather](us-weather)

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
