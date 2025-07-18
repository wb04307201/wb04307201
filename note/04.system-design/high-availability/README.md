# 高可用

高可用性是指一个系统或应用能够持续、稳定地提供服务，即使在其部分组件出现故障的情况下也能迅速恢复。高可用性通常通过冗余设计、负载均衡、故障转移和自动恢复等技术手段来实现。这些技术可以确保系统在面对硬件故障、网络问题或软件错误等挑战时，仍然能够保持服务的高可用性和连续性。

## 高可用与可用性的判断标准

高可用描述的是一个系统在大部分时间都是可用的，可以提供服务的。高可用代表系统即使在发生硬件故障或者系统升级的时候，服务仍然是可用的。  
一般情况下，使用多少个 9 来评判一个系统的可用性，比如 99.9999% 就是代表该系统在所有的运行时间中只有 0.0001% 的时间是不可用的，这样的系统就是高可用的。  
除此之外，系统的可用性还可以用某功能的失败次数与总的请求次数之比来衡量，比如对网站请求 1000 次，其中有 10 次请求失败，那么可用性就是 99%。

## 哪些情况会导致系统不可用？
- 黑客攻击；
- 硬件故障，比如服务器坏掉。
- 并发量/用户请求量激增导致整个服务宕掉或者部分服务不可用。
- 代码中的坏味道导致内存泄漏或者其他问题导致程序挂掉。
- 网站架构某个重要的角色比如 Nginx 或者数据库突然不可用。
- 自然灾害或者人为破坏。
- ……