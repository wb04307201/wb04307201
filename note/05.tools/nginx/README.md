# Nginx

## 配置示例

```text
user nobody;
worker_processes 1;

error_log logs/error.log;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    sendfile on;

    server {
        listen 80;
        server_name localhost;

        location / {
            root html;
            index index.html index.htm;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root html;
        }
    }
}
```

## 配置文件结构

> Nginx配置文件主要由三部分组成：全局块、events块和http块。http块中还可以包含多个server块，每个server块中又可以包含多个location块。

> - **全局块**
>   - 配置影响Nginx全局的指令，如运行Nginx服务器的用户（组）、工作进程数、错误日志的位置等。
>   - 示例指令：user nobody;、worker_processes 1;、error_log logs/error.log;
> - **events块**
>   - 设定Nginx的工作模式及连接上限，如每个worker进程的最大连接数、是否开启对多worker process下的网络连接进行序列化等。
>   - 示例指令：worker_connections 1024;、multi_accept on;
> - **http块**
>   - 包含HTTP相关的指令，如文件引入、MIME-Type定义、日志自定义、连接超时时间等。
>   - 可以嵌套多个server块，用于配置不同的虚拟主机。
>   - 示例指令：include mime.types;、sendfile on;
> - **server块**
>   - 代表一个虚拟主机，可以配置多个，用于支持多个域名或IP地址。
>   - 包含server全局块和多个location块。
>   - 示例指令：listen 80;、server_name localhost;
> - **location块**
>   - 配置URL路径的指令，可以定义URL路径的匹配规则和处理方式，如反向代理、重定向等。
>   - 示例指令：location / { root html; index index.html index.htm; }

## 重要指令说明
> - **worker_processes**：指定Nginx启动的工作进程数，建议设置为CPU核心数的两倍或设置为auto，由Nginx自行选择。
> - **worker_connections**：定义每个工作进程可以处理的最大连接数，根据服务器性能和并发需求进行适当调整。
> - **listen**：指定Nginx服务器监听的端口，默认是80。
> - **server_name**：指定虚拟主机的域名或IP地址。
> - **location**：用于匹配网页位置，可根据不同的URL路径执行不同的操作，如代理传递、重定向、访问控制等。
> - **proxy_pass**：配置反向代理服务器的目标地址。
> - **rewrite**：配置URL重写规则，可以实现URL的重定向和重写。
> - **proxy_set_header**：修改或添加发送到代理服务器的HTTP请求头，常用于设置Host、X-Real-IP、X-Forwarded-For等。

## 配置文件的编辑与生效
> - **编辑配置文件**：使用文本编辑器（如vim、nano）编辑Nginx的配置文件，通常位于/etc/nginx/nginx.conf或/etc/nginx/sites-available/目录下。
> - **检查配置文件**：在修改配置文件后，使用nginx -t命令检查配置文件的语法是否正确。
> - **重启Nginx**：如果配置文件无误，使用nginx -s reload或systemctl restart nginx命令重启Nginx服务，使配置生效。
