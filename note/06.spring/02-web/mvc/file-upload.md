# Spring MVC 文件上传

> ⬅️ [返回 MVC 总览](README.md) | [02 Web 层](../README.md)

Spring MVC 通过 **`MultipartResolver` + `MultipartFile`** 提供文件上传能力。Spring Boot 3 / Spring 6 起，`MultipartResolver` 底层默认走 **Jakarta Servlet 的 `Part` API**（不再使用 Apache Commons FileUpload）。本文覆盖单/多文件上传、Spring Boot 默认配置、大小/类型限制、常见坑。

---

## 🎯 一句话定位

**Spring MVC 文件上传 = "MultipartResolver 解析请求 → @RequestParam MultipartFile 接收 → 落盘/转存"**——`@RequestParam` / `@RequestPart` 注解直接绑定 `MultipartFile`，开发者无需关心底层 multipart 协议解析。

---

## 一、依赖与自动配置

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

> Spring Boot 3.x 默认使用 **Servlet 3.1+ 的 `Part` API**（无需额外依赖）。若用 Spring 5.x 且 Servlet 3.0 容器，可显式引入 `commons-fileupload`。

---

## 二、Spring Boot 默认 multipart 配置

```yaml
spring:
  servlet:
    multipart:
      enabled: true
      max-file-size: 10MB         # 单个文件大小
      max-request-size: 50MB      # 整个请求大小
      file-size-threshold: 1MB    # 超过此值才落临时目录
      location: ${java.io.tmpdir} # 临时文件目录
      resolve-lazily: false       # 立即解析（默认）
```

| 属性 | 默认 | 含义 |
|------|------|------|
| `enabled` | `true` | 是否启用 multipart 解析 |
| `max-file-size` | `1MB` | 单文件最大字节 |
| `max-request-size` | `10MB` | 整请求最大字节 |
| `file-size-threshold` | `0` | 超过则落盘 |
| `resolve-lazily` | `false` | 是否懒解析（需读取时才解析） |

> 超限抛 `MaxUploadSizeExceededException`，可在 `@RestControllerAdvice` 统一处理。

---

## 三、单文件上传

### 1. Controller

```java
@PostMapping("/upload")
public ApiResponse<String> upload(@RequestParam("file") MultipartFile file) throws IOException {
    if (file.isEmpty()) {
        throw new BizException("FILE_EMPTY");
    }
    String filename = UUID.randomUUID() + "-" + file.getOriginalFilename();
    Path target = Paths.get("/var/uploads", filename);
    Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
    return ApiResponse.ok(target.toString());
}
```

### 2. curl 测试

```bash
curl -F "file=@./demo.png" http://localhost:8080/upload
```

---

## 四、多文件上传

```java
@PostMapping("/upload-multi")
public ApiResponse<List<String>> uploadMulti(@RequestParam("files") MultipartFile[] files) {
    List<String> urls = new ArrayList<>();
    for (MultipartFile f : files) {
        if (f.isEmpty()) continue;
        String url = saveTo(f);
        urls.add(url);
    }
    return ApiResponse.ok(urls);
}
```

### 名字不同（多字段）

```java
@PostMapping("/upload-mixed")
public ApiResponse<Void> uploadMixed(
        @RequestParam("avatar") MultipartFile avatar,
        @RequestParam("docs")   MultipartFile[] docs) {
    // ...
}
```

---

## 五、@RequestPart：JSON + 文件混合

```java
@PostMapping(value = "/submit", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
public ApiResponse<Submission> submit(
        @RequestPart("meta")  SubmissionMeta meta,    // JSON 反序列化
        @RequestPart("files") List<MultipartFile> files) {
    return ApiResponse.ok(new Submission(meta, files.size()));
}
```

> `@RequestPart` 支持 `application/json`、`application/xml` 等 Content-Type；`@RequestParam` 仅支持表单字段/文件。

---

## 六、MultipartFile API

| 方法 | 用途 |
|------|------|
| `getOriginalFilename()` | 客户端上传的文件名（**不可信**，需 sanitize） |
| `getName()` | 表单字段名（`file` / `avatar` 等） |
| `getSize()` | 字节数 |
| `getContentType()` | MIME（客户端声明，**不可信**） |
| `isEmpty()` | 是否空文件 |
| `getInputStream()` | 读流（不落盘） |
| `getBytes()` | 转 `byte[]`（小文件可用，**大文件慎用**） |
| `transferTo(File)` | 一次性落盘（便捷，但会覆盖同名） |

---

## 七、文件大小/类型限制

### 1. 全局限制（推荐）

`application.yml` 中配置 `spring.servlet.multipart.max-file-size` 即可。

### 2. 注解式限制（细粒度）

```java
@PostMapping("/upload")
public ApiResponse<String> upload(@RequestParam @Size(max = 5_000_000) MultipartFile file) {
    // 仅校验字节大小
}
```

### 3. 类型白名单（业务侧必做）

```java
private static final Set<String> ALLOWED = Set.of("image/png", "image/jpeg", "application/pdf");

private void validateType(MultipartFile f) {
    String type = f.getContentType();
    if (type == null || !ALLOWED.contains(type)) {
        throw new BizException("FILE_TYPE_NOT_ALLOWED");
    }
    // 推荐同时校验 Magic Number：Files.probeContentType(...)
}
```

### 4. 超限统一处理

```java
@ExceptionHandler(MaxUploadSizeExceededException.class)
public ResponseEntity<ApiError> handleMax(MaxUploadSizeExceededException e) {
    return ResponseEntity.status(413).body(new ApiError("FILE_TOO_LARGE", "文件过大"));
}
```

---

## 八、常见坑

1. **`@RequestParam("file")` 漏写字段名**：Spring 会按参数名匹配，前端表单 `name` 须与注解值一致。
2. **`transferTo` 二次调用**：`MultipartFile` 一旦 `transferTo` 内部流已消费，再 `getInputStream()` 会抛 `IOException`。
3. **大文件 OOM**：不要 `getBytes()`，**用 `getInputStream()` 流式落盘**。
4. **文件名注入**：永远用 `UUID` 或 `SecureRandom` 重新生成名字，**不要直接用 `getOriginalFilename()`**。
5. **Spring Boot 3 迁移到 Jakarta**：`jakarta.servlet.*` 替换 `javax.servlet.*`；上传相关 API 仍是 `org.springframework.web.multipart`。
6. **临时文件清理**：`MultipartFile` 解析时若超过 `file-size-threshold`，会写到 `location` 目录临时文件；处理完后 JVM 退出时清理。

---

## 九、文件下载（简述）

```java
@GetMapping("/download/{id}")
public ResponseEntity<Resource> download(@PathVariable String id) {
    Resource file = new FileSystemResource(Paths.get("/var/uploads", id));
    return ResponseEntity.ok()
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + id + "\"")
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .body(file);
}
```

---

## 相关章节

- ⬅️ [返回 MVC 总览](README.md)
- [CORS 与静态资源](cors-and-static.md) — 静态资源 / WebJars
- [异常处理](exception-resolver.md) — MaxUploadSizeExceededException 统一处理
