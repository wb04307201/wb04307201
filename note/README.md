# 一、java
## 1. [概念](01.java/concepts/README.md)
### 1.1. [基础](01.java/concepts/base/README.md)
### 1.1. [序列化和反序列化](01.java/concepts/README.md)
### 1.2. [反射](01.java/concepts/reflection/README.md)
## 2. [集合](01.java%2Fcollection%2FREADME.md)
### 2.1. [ConcurrentHashMap](01.java/collection/ConcurrentHashMap/README.md)
### 2.2. [WeakHashMap](01.java/collection/WeakHashMap/README.md)
### 2.3. [TreeMap](01.java/collection/TreeMap/README.md)
## 3. [I/O](01.java%2Fio%2FREADME.md)
### 3.1. [零拷贝](01.java%2Fio%2Fzero-copy%2FREADME.md)
## 5. [JVM虚拟机](01.java/jvm/README.md)
### 5.1. [JVM运行时数据区域](01.java/jvm/area/README.md)
### 5.2. [HotSpot虚拟机](01.java/jvm/hotspot/README.md)
### 5.3. [Java对象创建过程](01.java/jvm/new-object/README.md)
### 5.4. [垃圾回收](01.java%2Fjvm%2Fgarbage-collection%2FREADME.md)
### 5.5. [JVM工具](01.java/jvm/tools/README.md)
### 5.6. [JVM调优](01.java/jvm/tuning/README.md)
## 6. 版本特性
### 6.0. 功能版本变更历史
#### 6.0.1. [垃圾回收](01.java/version/function-history/gc/README.md)
#### 6.0.2. [Lambda](01.java/version/function-history/lambda/README.md)
##### 6.0.2.1. [README.md](01.java/version/function-history/lambda/functional-interface/README.md)
#### 6.0.3. [Stream API](01.java/version/function-history/stream-api/README.md)
#### 6.0.4. [Optional](01.java/version/function-history/optional/README.md)
#### 6.0.5. [Switch](01.java/version/function-history/switch/README.md)
#### 6.0.6. [instanceof](01.java/version/function-history/instanceof/README.md)
#### 6.0.7. [并发](01.java/version/function-history/concurrency/README.md)
##### 6.0.7.1. [定义](01.java/version/function-history/concurrency/define/README.md)
1. [Java锁机制](01.java/version/function-history/concurrency/define/java-locks/README.md)
2. [CHMRLock - 基于ConcurrentHashMap和 ReentrantLock的锁实现](https://gitee.com/wb04307201/CHMRLock)
   > 一个基于Java ConcurrentHashMap 和 ReentrantLock 的锁实现。它提供了锁的获取、释放、自动清理过期锁以及监控指标统计等功能。
3. [线程池](01.java/version/function-history/concurrency/define/thread-pool/README.md)
#### 6.0.8. [Vector API](01.java/version/function-history/vector-api/README.md)
#### 6.0.9. [Record](01.java/version/function-history/record/README.md)
### 6.1. [Java 8（LTS）](01.java%2Fversion%2Fjava-8%2FREADME.md)
### 6.2. [Java 9](01.java%2Fversion%2Fjava-9%2FREADME.md)
### 6.3. [Java 10](01.java%2Fversion%2Fjava-10%2FREADME.md)
### 6.4. [Java 11（LTS）](01.java%2Fversion%2Fjava-11%2FREADME.md)
### 6.5. [Java 12](01.java%2Fversion%2Fjava-12%2FREADME.md)
### 6.6. [Java 13](01.java%2Fversion%2Fjava-13%2FREADME.md)
### 6.7. [Java 14](01.java%2Fversion%2Fjava-14%2FREADME.md)
### 6.8. [Java 15](01.java%2Fversion%2Fjava-15%2FREADME.md)
### 6.9. [Java 16](01.java%2Fversion%2Fjava-16%2FREADME.md)
### 6.10. [Java 17（LTS）](01.java%2Fversion%2Fjava-17%2FREADME.md)
### 6.11. [Java 18](01.java%2Fversion%2Fjava-18%2FREADME.md)
### 6.12. [Java 19](01.java%2Fversion%2Fjava-19%2FREADME.md)
### 6.13. [Java 20](01.java%2Fversion%2Fjava-20%2FREADME.md)
### 6.14. [Java 21（LTS）](01.java%2Fversion%2Fjava-21%2FREADME.md)
#### 6.14.1. [Java 虚拟线程](01.java/version/java-21/virtual-threads/README.md)
#### 6.14.2. [Switch 模式匹配](01.java/version/java-21/switch/README.md)
### 6.15. [Java 22](01.java%2Fversion%2Fjava-22%2FREADME.md)
### 6.16. [Java 23](01.java%2Fversion%2Fjava-23%2FREADME.md)
### 6.17. [Java 24](01.java/version/java-24/README.md)
### 6.18. [Java 25（LTS）](01.java/version/java-25/README.md)
## 7. [Java Agent](01.java%2Fjava-agent%2FREADME.md)
### 7.1. [统计API接口调用耗时](01.java/java-agent/api/README.md)
## 8. 咬文嚼字
### 8.1. [高频面试题](01.java/split-hairs/questions/README.md)
### 8.2. [创建对象](01.java/split-hairs/create-object/README.md)
### 8.3. [单例模式](01.java/split-hairs/singleton-pattern/README.md)
### 8.4. [Integer缓存](01.java/split-hairs/integer-cache/README.md)
### 8.5. [`String str = new String("123")`会在堆中生成几个新对象](01.java/split-hairs/new-objects/README.md)

# 二、计算机基础
## 1. [服务器性能指标](02.computer-basics%2Fserver-performance-metrics%2FREADME.md)
## 2. [计算机网络](02.computer-basics/network/README.md)

# 三、数据库
## 关系型数据库
### [数据库基础知识](03.database%2Fbase%2Frelational-database%2Fbasic-of-databases%2FREADME.md)
### [增删改查SQL语句](03.database/base/relational-database/sql/README.md)
#### [查询SQL执行顺序](03.database%2Fbase%2Frelational-database%2Fsql-excute-order%2FREADME.md)
### [事务处理](03.database%2Fbase%2Frelational-database%2Ftransaction-processing%2FREADME.md)
#### 并发事务的控制方式
##### [数据库锁类型详解](03.database%2Fbase%2Frelational-database%2Ftransaction-processing%2Flock%2FREADME.md)
##### [数据库多版本并发控制详解](03.database%2Fbase%2Frelational-database%2Ftransaction-processing%2Fmvcc%2FREADME.md)
##### [锁与MVCC的关系](03.database%2Fbase%2Frelational-database%2Ftransaction-processing%2Flock-vs-mvcc%2FREADME.md)
### [MySQL](03.database%2Fbase%2Frelational-database%2Fmysql%2FREADME.md)
#### 咬文嚼字
##### [MySQL锁类型详解](03.database/base/relational-database/mysql/split-hairs/lock/README.md)
##### [MySQL的事务隔离机制](03.database/base/relational-database/mysql/split-hairs/isolation/README.md)
##### [`INT(4)` 的定义](03.database/base/relational-database/mysql/split-hairs/int%284%29-define)
##### [1亿条数据快速加索引的方法](03.database/base/relational-database/mysql/split-hairs/quickly-add-index/README.md)
##### [时间类型对比](03.database/base/relational-database/mysql/split-hairs/time-types/README.md)
## [NoSQL数据库](03.database%2Fbase%2Fnosql%2FREADME.md)
### 键值存储数据库
#### [缓存](03.database%2Fbase%2Fnosql%2Fkey-value%2Fcache%2FREADME.md)
##### [缓存与数据库一致性](03.database%2Fbase%2Fnosql%2Fkey-value%2Fcache%2Fconsistency-between-cache-and-database%2FREADME.md)
##### [缓存稳定性的3种经典问题](03.database%2Fbase%2Fnosql%2Fkey-value%2Fcache%2Fcache-stability%2FREADME.md)
##### [基于 ConcurrentHashMap 的高性能缓存实现](https://gitee.com/wb04307201/CHMCache)
> 一个基于 `ConcurrentHashMap` 和 LRU 策略的高性能缓存实现，支持自动过期、大小限制、LRU 淘汰和后台清理等特性。
### [Redis](03.database%2Fbase%2Fnosql%2Fkey-value%2Fredis%2FREADME.md)
#### 咬文嚼字
##### [如何查找但不导致Redis阻塞](03.database/base/nosql/key-value/redis/split-hairs/search/README.md)

## [关系型数据库和NoSQL数据库的区别](03.database%2Fbase%2Fdatabase-vs-nosql%2FREADME.md)

# 四、系统设计
## 1. 基础
### [软件工程](04.system-design/base/software-engineering/README.md)
#### [软件开发的流程与方法](04.system-design/base/software-engineering/development-process-and-methodologies/README.md)
##### [系统设计](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/README.md)
###### [GoF设计模式/23种设计模式](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/gang-of-four/README.md)
###### 架构图
1. [“4+1”视图](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/architecture-diagram/4%2B1/README.md)
2. [C4 模型](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/architecture-diagram/c4-model/README.md)
###### [领域驱动设计](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/ddd/README.md)
###### [微服务模式](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/microservices/README.md)
###### [微服务模式与领域驱动设计（DDD）](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/microservices-and-ddd/README.md)
###### [事件驱动模式与异步处理模式](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/eda-vs-async/README.md)
###### [部署](04.system-design/base/software-engineering/development-process-and-methodologies/system-design/deploy/README.md)
#### [工具与模型](04.system-design/base/software-engineering/tools-and-models/README.md)
#### [质量保障体系](04.system-design/base/software-engineering/quality-assurance-system/README.md)
### [技术债](04.system-design/base/technical-debt/README.md)
## 2. 分布式
分布式通常指的是一种计算或数据处理的方式，其中任务、数据或资源被分散在多个节点（如计算机、服务器或计算设备）上进行处理。这种分布式的处理方式可以提高系统的整体性能、可靠性、可扩展性和容错性。在分布式系统中，各个节点通过网络进行通信和协作，以实现共同的目标。
### 分布式理论&算法&协议
#### [CAP](04.system-design/distributed/theory-algorithm-protocol/cap/README.md)
#### [BASE](04.system-design/distributed/theory-algorithm-protocol/base/README.md)
#### [Paxos算法](04.system-design/distributed/theory-algorithm-protocol/paxos/README.md)
#### [Raft算法](04.system-design/distributed/theory-algorithm-protocol/raft/README.md)
#### [Gossip协议](04.system-design/distributed/theory-algorithm-protocol/gossip/README.md)
### [RPC](04.system-design%2Fdistributed%2Frpc%2FREADME.md)
#### [Apache Dubbo](04.system-design%2Fdistributed%2Frpc%2Fapache-dubbo%2FREADME.md)
#### [RPC和REST](04.system-design/distributed/rpc/rpc-and-rest/README.md)
### [分布式ID](04.system-design/distributed/distributed-id/README.md)
#### [UUID](04.system-design/distributed/distributed-id/uuid/README.md)
#### [ULID](04.system-design/distributed/distributed-id/ulid/README.md)
#### [UUID v7](04.system-design/distributed/distributed-id/uuid-v7/README.md)
### [分布式锁](04.system-design/distributed/distributed-lock/README.md)
#### [Flexible Lock - 灵锁](https://gitee.com/wb04307201/flexible-lock)
> 一个基于Spring Boot的锁starter，提供了统一的锁接口和多种实现方式，包括Redis单点、Redis集群、Redis哨兵、Zookeeper和本地锁。通过简单的配置即可在项目中使用锁功能。
### [分布式事务](04.system-design%2Fdistributed%2Fdistributed-transaction%2FREADME.md)
### [API网关](04.system-design/distributed/api-gatewway/README.md)
## 3. 高性能
高性能指的是系统或应用在处理任务、数据或请求时表现出的高效性和快速性。高性能系统通常具有强大的计算能力、快速的响应时间和高效的数据处理能力。为了实现高性能，系统可能需要采用先进的硬件技术、优化的软件算法、高效的存储和传输技术等手段。
### [Java代码性能优化](04.system-design/high-performance/java/README.md)
#### 咬文嚼字
#### [`switch`前使用`if`针对高频热点状态的优化](04.system-design/high-performance/java/split-hairs/if%20-before-switch/README.md)
#### [ArrayList去重](04.system-design/high-performance/java/split-hairs/arrayList-distinct/README.md)
#### [数据结构选择：HashSet 替代 LinkedList 查找](04.system-design/high-performance/java/split-hairs/replace-linkedlist-with-hashset/README.md)
#### [并发编程优化：Atomic 类替代 synchronized](04.system-design/high-performance/java/split-hairs/replace-synchronized-with-atomic/README.md)
#### [字符串拼接优化：StringBuilder 重用](04.system-design/high-performance/java/split-hairs/reuse-of-stringbuilder/README.md)
#### [快速给Map排序](04.system-design/high-performance/java/split-hairs/sort-map/README.md)
#### [HashMap扩容](04.system-design/high-performance/java/split-hairs/hashmap-resizing/README.md)
### 数据库性能优化
#### [数据库读写分离](04.system-design/high-performance/database-optimization/db-read-write-splitting-and-db-sharding/db-read-write-splitting/README.md)
#### [数据库分库分表](04.system-design/high-performance/database-optimization/db-read-write-splitting-and-db-sharding/db-sharding/README.md)
#### [数据冷热分离](04.system-design/high-performance/database-optimization/cold-hot-data-separation/README.md)
#### [常见 SQL 优化手段总结](04.system-design/high-performance/database-optimization/sql/README.md)
###### [ShardingSphere](04.system-design/high-performance/database-optimization/db-read-write-splitting-and-db-sharding/db-sharding/sharding-sphere/README.md)
### [载均衡负](04.system-design/high-performance/load-balance/README.md)
### [CDN](04.system-design/high-performance/cdn/README.md)
### [消息队列](04.system-design%2Fhigh-performance%2FMQ%2FREADME.md)
## 咬文嚼字
##### [MQ消息积压](04.system-design/high-performance/MQ/split-hairs/mq-backlog/README.md)
## 4. 高可用
高可用性是指一个系统或应用能够持续、稳定地提供服务，即使在其部分组件出现故障的情况下也能迅速恢复。高可用性通常通过冗余设计、负载均衡、故障转移和自动恢复等技术手段来实现。这些技术可以确保系统在面对硬件故障、网络问题或软件错误等挑战时，仍然能够保持服务的高可用性和连续性。
### 4.1. [代码质量](04.system-design/high-availability/code-quality/README.md)
#### [2行代码实现功能，8行代码解决蠢](04.system-design/high-availability/code-quality/28/README.md)
### 4.2. 限流&降级&熔断
#### [限流](04.system-design/high-availability/rate-limiting/README.md)
##### [Rate Limiter - 限流器](https://gitee.com/wb04307201/rate-limiter)
#### [降级](04.system-design/high-availability/service-degradation/README.md)
#### [熔断](04.system-design/high-availability/circuit-break/README.md)
### 4.3. 超时&重试
#### [超时](04.system-design/high-availability/timeout/README.md)
#### [重试](04.system-design/high-availability/retry/README.md)
### 4.4. [冗余设计](04.system-design/high-availability/redundancy-design/README.md)
#### [异地多活](04.system-design/high-availability/redundancy-design/multi-site-active-active/README.md)
#### [集群](04.system-design/high-availability/redundancy-design/cluter/README.md)
### 4.5. [弹性架构](04.system-design/high-availability/elastic-architecture/README.md)
## [幂等性设计](04.system-design/idempotency-design/README.md)
## 安全
### [为什么 `localStorage` 存储 JWT 是危险的？](04.system-design/security/jwt-localStorage/README.md)
### 认证授权
#### 认证授权基础概念详解
#### JWT 基础概念详解
#### JWT 优缺点分析以及常见问题解决方案
#### 权限系统设计详解
#### SSO 单点登录详解
### 数据安全
#### 常见加密算法总结
#### 敏感词过滤方案总结
#### 数据脱敏方案总结
#### 为什么前后端都要做数据校验

# 五、工具
## Git
### [软件版本号](05.tools%2Fgit%2Fsoftware-version-number%2FREADME.md)
### [版本发布策略](05.tools%2Fgit%2Frelease-strategy%2FREADME.md)
### [分支版本管理](05.tools%2Fgit%2Fversion-controller%2FREADME.md)
## [Docker](05.tools%2Fdocker%2FREADME.md)
### [Podman](05.tools/docker/podman/README.md)
## [Nginx](05.tools%2Fnginx%2FREADME.md)
### [Pingora](05.tools/nginx/pingora/README.md)
## [Monorepo](05.tools%2Fmonorepo%2FREADME.md)
## [阿里微服务](05.tools%2Fali-microservices%2FREADME.md)
## Java
### [Apache Commons](05.tools/java/apache-commons/README.md)
### [Hutool](05.tools/java/hutools/README.md)
### [Lombok注解如何让Java开发效率飙升](05.tools/java/lombok/README.md)

# 六、[Spring](06.spring%2FREADME.md)
## [注解](06.spring%2Fannotation%2FREADME.md)
## [模块](06.spring%2Fmodule%2FREADME.md)
## [IoC](06.spring%2Fioc%2FREADME.md)
## [构造器注入](06.spring/constructor-injection/README.md)
### [使用servlet模拟Spring IoC运行](06.spring/ioc/microrest)
## [Spring AOP 深度解析](06.spring/aop/README.md)
## [Spring 自带24个工具类](06.spring/tools/README.md)
## [Spring Cache 缓存操作](06.spring/spring-cache/README.md)
### [通过`CacheManager`接口扩展多级缓存注解](https://gitee.com/wb04307201/multi-level-cache-spring-boot-starter)
## [Spring Retry 自动重试](06.spring/spring-retry/README.md)
## [Spring Batch 批处理](06.spring/spring-batch/README.md)
## [Spring Boot Actuator 监控，Actuator + Prometheus + Grafana 监控体系整合方案](06.spring/spring-boot-actuator/README.md)
### [Method Trace Log - 方法调用追踪和监控](https://gitee.com/wb04307201/methodTraceLog)
> 一个基于Spring AOP和Micrometer的Java方法调用追踪和监控工具，用于记录方法执行的全链路日志和性能指标。
## [Spring Boot启动后执行](06.spring/start/README.md)
## [何创建自己的 Starter 模块](06.spring/spring-boot-starter/README.md)
### [Spring Boot 3 中spring.factories 机制移除](06.spring/spring-boot-starter/spring-factories/README.md)
## [Spring Boot 响应式 SSE](06.spring/reactor-sse/README.md)
## [Spring Statemachine 状态机](06.spring/spring-statemachine/README.md)
## [Spring Cloud 微服务架构](06.spring/cloud/README.md)
### [服务注册与发现中心对比](06.spring/cloud/service-registry/README.md)
### [Seata 分布式事务框架](06.spring/cloud/seata/README.md)

# 七、[工作流](07.workflow/README.md)
## [定义](07.workflow/define/README.md)
## [流程引擎](07.workflow/process-engine/README.md)
### [Camunda 7](07.workflow/process-engine/camunda/camunda-7/README.md)
### [Camunda 8](07.workflow/process-engine/camunda/camunda-8/README.md)
#### [Zeebe](07.workflow/process-engine/camunda/camunda-8/zeebe/README.md)
## [工作流引擎与微服务编排](07.workflow/workflow-and-microservice-orchestration/README.md)
## [Apache EventMesh](07.workflow/apache-eventmesh/README.md)
### [阿里云工作流](07.workflow/apache-eventmesh/cloud-flow/README.md)

# 八、[Mybatis](08.mybatis%2FREADME.md)
## [MyBatis拦截器](08.mybatis/interceptor/README.md)
## [Mybatis-Plus](08.mybatis/mybatis-plus/README.md)
### [MyBatis-Plus Generator ：自动生成代码的利器](08.mybatis/mybatis-plus/generator/README.md)
### [条件构造器Wrapper](08.mybatis/mybatis-plus/Wrapper/README.md)
### [LambdaQueryWrapper 中的序列化函数式接口 SFunction](08.mybatis/mybatis-plus/Wrapper/lambdaQueryWrapper-function/README.md)

# 九、其他
## [常用系统](09.other%2Fcommon-systems%2FREADME.md)
### [ERP](09.other%2Fcommon-systems%2Ferp%2FREADME.md)
### [PDM](09.other%2Fpdm%2FREADME.md)
## [权限控制](09.other%2Fpermission%2FREADME.md)
## 无代码平台
### [宜搭介绍](09.other/nocode/yida/README.md)
### [简道云介绍](09.other/nocode/jiandaoyun/README.md)
### [零代码平台架构设计](09.other/nocode/design/README.md)
## [Hapoop](09.other%2Fhadoop%2FREADME.md)

# 十、[大数据](10.big-data/README.md)
## [2024年的开源数据工程生态系统全景图](10.big-data/open-source/README.md)
## [离线数仓/实时数仓](10.big-data/offline-or-real-time-data-warehouse/README.md)

# 十一、[AI](11.ai/README.md)
## [大模型与算力](11.ai/llm-and-computing/README.md)
## [大模型落地分层技术体系](11.ai/hierarchical/README.md)
## [嵌入与向量化的区别](11.ai/Embedding-vs-vectorization/README.md)
## [大模型的问题降维以提升回答准确性](11.ai/dimensionality-reduction/README.md)
## [prompt模板](11.ai/prompt/README.md)
### [grok系统prompt](11.ai/prompt/grok-system-prompt/README.md)
## 工具
### [Ollama](11.ai/tools/ollama/README.md)
### [AI平台流程工具对比选购指南](11.ai/tools/workflow-comparison/README.md)
### [iFlow CLI AI 助手](11.ai/tools/iflow-cli/README.md)

# 十二、前端
## [前端框架](12.font-end/frameworks/README.md)
### [React前端框架构建](12.font-end/frameworks/building-react/README.md)
## [CORS 跨域](12.font-end/cors/README.md)
## [微前端](12.font-end/micro-frontend/README.md)
## [Web Components](12.font-end/web-components/README.md)
## 咬文嚼字
### [HTTP 请求中的 GET 和 POST](12.font-end/split-hairs/get-and-post/README.md)
### [网页端接受推送消息的方式](12.font-end/split-hairs/message/README.md)
### [前端存储方式](12.font-end/split-hairs/storage/README.md)