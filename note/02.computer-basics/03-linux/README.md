# Linux 常用命令

> Linux 服务器管理中**最常用且关键**的命令分类整理，附带核心用法和典型场景。
>
> **子目录：** [curl 命令详解](curl/)

---
## 引言：反直觉代码（[AUTO] 自动生成，待人工 review）

Linux 常用命令 本应该很简单，Linux 服务器管理中**最常用且关键**的命令分类整理，附带核心用法和典型场景

**但实际**：面试/生产中常被问起或踩坑的是——
代码看着对、跑起来对，但仔细一问深一层就漏馅。本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。

> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。

---



### **一、系统信息 & 资源监控**
| 命令          | 作用                          | 典型用法示例                     |
|---------------|-----------------------------|--------------------------------|
| `top` / `htop` | **实时进程监控** (htop 更友好) | `htop` (需安装：`apt install htop`) |
| `free -h`     | 查看内存使用 (人类可读格式)     | `free -h` → 显示 RAM/swap 用量    |
| `df -h`       | **磁盘空间**使用情况          | `df -h /` → 查看根分区剩余空间     |
| `du -sh /path`| 目录占用空间大小              | `du -sh /var/log` → 查日志目录大小 |
| `uptime`      | 系统运行时间 + 平均负载        | `uptime` → 显示 1/5/15 分钟负载   |
| `vmstat 2`    | 虚拟内存统计 (每2秒刷新)       | `vmstat 2` → 监控 CPU/内存/IO 瓶颈 |
| `iostat -x 2` | **磁盘 I/O 性能**分析         | `iostat -x 2` → 定位慢磁盘问题     |

---

### **二、文件 & 目录操作**
| 命令                     | 作用                          | 高频场景示例                     |
|--------------------------|-----------------------------|--------------------------------|
| `ls -lhtr`               | 人性化列出文件 (按时间排序)    | `ls -lhtr /backup` → 查看最新备份 |
| `grep "error" /var/log/syslog` | **文本搜索** (日志分析必备)   | `grep -i "fail" auth.log` → 忽略大小写搜索 |
| `find / -name "*.log" -mtime +7` | 按条件**查找文件**          | `find /tmp -size +100M` → 找大文件 |
| `tar -czvf backup.tar.gz /data` | **压缩/解压** (常用)       | `tar -xzvf file.tar.gz` → 解压    |
| `rsync -avz /src user@host:/dest` | **安全同步文件** (替代 scp) | `rsync -avz --delete /data/ remote:/backup/` → 增量同步+删除多余文件 |
| `scp file user@host:/path` | 安全拷贝文件 (跨服务器)       | `scp -P 2222 db.sql user@192.168.1.10:/backup` → 指定端口传输 |

---

### **三、进程管理**
| 命令                          | 作用                     | 关键技巧                          |
|-------------------------------|------------------------|---------------------------------|
| `ps aux \| grep nginx`        | **查看进程**            | `ps -ef \| grep java` → 查 Java 服务 |
| `kill -9 <PID>`               | 强制终止进程            | `killall nginx` → 按名称杀进程      |
| `systemctl start nginx`       | **管理服务** (systemd)  | `systemctl status sshd` → 查服务状态 |
| `journalctl -u nginx -f`      | 实时查看服务日志        | `journalctl --since "2025-01-01"` → 按时间过滤 |
| `nohup ./script.sh &`         | 后台运行任务 (防断连)    | `nohup python app.py > log.out 2>&1 &` → 重定向输出 |

---

### **四、网络诊断**
| 命令                          | 作用                     | 实战场景                          |
|-------------------------------|------------------------|---------------------------------|
| `ss -tulpn`                   | **替代 netstat** (更快) | `ss -ltn` → 查监听端口 (TCP)       |
| `ping 8.8.8.8`                | 测试网络连通性          | `ping -c 4 baidu.com` → 仅发4次包  |
| `traceroute baidu.com`        | 路由追踪 (排查跨网段问题) | `mtr baidu.com` → 动态路由分析 (需安装) |
| `curl -I https://example.com` | **检查 HTTP 响应头**    | `curl -o /dev/null -s -w '%{http_code}\n' url` → 获取状态码 |
| `tcpdump -i eth0 port 80 -w capture.pcap` | **抓包分析** | `tcpdump host 192.168.1.100` → 抓指定 IP 流量 |

---

### **五、用户 & 权限**
| 命令                     | 作用                | 安全建议                      |
|--------------------------|-------------------|-----------------------------|
| `sudo -i`                | 切换到 root        | 避免直接使用 root 账号         |
| `chmod 755 filename`     | 修改文件权限       | `chmod -R 644 /dir` → 递归设置 |
| `chown user:group file`  | 修改文件所有者     | `chown -R www-data:www-data /var/www` |
| `useradd -m deploy`      | 创建新用户         | `passwd deploy` → 设置密码      |
| `visudo`                 | **安全编辑 sudoers** | 添加 `deploy ALL=(ALL) NOPASSWD: ALL` 免密 sudo |

---

### **六、高级技巧 (运维必备)**
```bash
# 1. 实时追踪日志 (排查错误)
tail -f /var/log/nginx/error.log | grep "404"

# 2. 批量替换文本 (sed)
sed -i 's/old_text/new_text/g' /etc/config.conf

# 3. 统计日志中的 IP 访问次数
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10

# 4. 快速生成大文件 (测试用)
dd if=/dev/zero of=testfile bs=1G count=2  # 生成 2GB 文件

# 5. 服务器间免密登录 (自动化基础)
ssh-keygen -t ed25519  # 本地生成密钥
ssh-copy-id user@remote-server  # 上传公钥
```

---

### **关键原则：**
1. **权限最小化**：永远不要用 root 跑应用，用 `sudo` 代替。
2. **日志驱动**：问题先查日志 (`/var/log/` + `journalctl`)。
3. **备份再操作**：修改配置前执行 `cp config.conf{,.bak}`。
4. **管道组合**：`grep`/`awk`/`sed` + 管道 (`|`) 是文本处理核心。
5. **man 是朋友**：忘记参数时 `man command` 看官方文档。

> 💡 **提示**：生产环境操作前，先在测试环境验证命令！  
> **危险命令慎用**：`rm -rf /`、`:(){ :|:& };:` (fork炸弹)、`dd if=/dev/random of=/dev/sda` (磁盘擦除)

掌握这些命令，你已具备 **80% 的日常运维能力**。深入学习建议：
- 通过 `tldr command` 安装简化版 man 手册 (`apt install tldr`)
- 在 [explainshell.com](https://explainshell.com) 解析复杂命令
- 实践《Linux 101 Hacks》电子书中的场景案例