# curl 命令

`curl` 是一个强大的命令行工具，用于通过各种网络协议（如 HTTP、HTTPS、FTP 等）传输数据。它常用于测试 API、下载文件、调试网络请求等场景。以下是核心用法总结：

---

## 基础语法
```bash
curl [选项] [URL]
```

---

## 常用选项
| 选项 | 说明 |
|------|------|
| `-X` 或 `--request` | 指定请求方法（如 `GET`/`POST`/`PUT`/`DELETE`） |
| `-H` 或 `--header` | 添加请求头（如 `Content-Type: application/json`） |
| `-d` 或 `--data` | 发送 POST 数据（自动使用 `POST` 方法） |
| `-o` | 将响应保存到文件（如 `-o output.txt`） |
| `-O` | 保存远程文件到本地（保留原文件名） |
| `-L` | 跟随重定向（3xx 响应） |
| `-i` | 显示响应头 + 响应体 |
| `-v` 或 `--verbose` | 详细模式（调试用，显示请求/响应全过程） |
| `-k` 或 `--insecure` | 忽略 SSL 证书验证（测试 HTTPS 时慎用） |
| `-u` | 指定用户名密码（如 `-u user:pass` 用于 Basic Auth） |

---

## 高频示例
### 1. 基础 GET 请求
```bash
curl https://api.example.com/data
```

### 2. 带请求头的 GET
```bash
curl -H "Authorization: Bearer token123" \
     -H "Accept: application/json" \
     https://api.example.com/secure-data
```

### 3. POST JSON 数据
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"name":"Alice","age":30}' \
     https://api.example.com/create
```

### 4. 上传文件（Form 表单）
```bash
curl -X POST \
     -F "file=@localfile.jpg" \
     -F "description=Photo" \
     https://api.example.com/upload
```

### 5. 保存响应到文件
```bash
curl -o weather.json https://api.weather.com/today
# 或保留原文件名：
curl -O https://example.com/report.pdf
```

### 6. 调试请求（查看详细过程）
```bash
curl -v https://api.example.com/debug
```

### 7. 忽略 SSL 证书错误（仅测试环境！）
```bash
curl -k https://self-signed.badssl.com
```

---

## 实用技巧
- **限速下载**：`curl --limit-rate 100K https://example.com/largefile.zip`
- **断点续传**：`curl -C - -O https://example.com/bigfile.tar`
- **并发请求**：用 `xargs` + `curl`（例如：`cat urls.txt | xargs -n1 -P5 curl -O`）
- **代理请求**：`curl -x http://proxy:8080 https://example.com`

> 💡 **提示**：
> - 用 `--compressed` 自动解压 gzip 响应。
> - 用 `-s`（静默模式）隐藏进度和错误信息（适合脚本）。
> - 生成 curl 命令：浏览器开发者工具（Network 标签）可复制请求为 `curl` 命令。

---

## 安装
- Linux: `sudo apt install curl`（Debian/Ubuntu）或 `sudo yum install curl`（CentOS）
- macOS: 预装，无需安装
- Windows: 通过 [Git Bash](https://gitforwindows.org/) 或 [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/zh-cn/windows/wsl/install) 使用

通过 `curl --version` 验证安装。  
更多细节参考官方文档：[curl.se/docs/manpage.html](https://curl.se/docs/manpage.html)