# RPC

> RPC（Remote Procedure Call） 即远程过程调用。  
> RPC 的出现就是为了让调用远程方法像调用本地方法一样简单。

## RPC 的原理

![img.png](img.png)
> - **客户端（服务消费端）**： 调用远程方法的一端。
> - **客户端 Stub（桩）**：这其实就是一代理类。代理类主要做的事情很简单，就是把你调用方法、类、方法参数等信息传递到服务端。
    >
- **网络传输**
  ：网络传输就是你要把你调用的方法的信息比如说参数啊这些东西传输到服务端，然后服务端执行完之后再把返回结果通过网络传输给你传输回来。  
  > 网络传输的实现方式有很多种比如最基本的 Socket 或者性能以及封装更加优秀的 Netty（推荐）。
> - **服务端 Stub（桩）**：这里的服务端 Stub 实际指的就是接收到客户端执行方法的请求后，去执行对应的方法然后返回结果给客户端的类。
> - **服务端（服务提供端）**：提供远程方法的一端。

## RPC 框架

### Apache Dubbo

[查看](01.apache-dubbo%2FREADME.md)

### Motan

- [ ] 待完善

### gRPC

- [ ] 待完善

### HTTP客户端组件

> 需要和 HTTP 协议打交道，解析和封装 HTTP 请求和响应，这类框架并不能算是“RPC 框架”，比如 Feign 和 OpenFeign 可以被看作是RPC（远程过程调用）框架的一部分或工具

#### Feign

> Feign 是一个声明式的 Web 服务客户端，它使得编写 HTTP 客户端变得更简单。你可以使用 Feign 来创建一个接口并用注解来配置它（例如，@Get、@Post等），然后 Feign 会为你生成实现。  
> Feign还整合了Ribbon和Hystrix，使得负载均衡和熔断机制变得更加容易实现。

#### OpenFeign

> OpenFeign 是 Feign 的一个社区版，它是 Spring Cloud 的一个组件，为 Feign 提供了更好的集成和更多的功能。  
> OpenFeign同样支持负载均衡和服务发现，内置了Ribbon组件，可以方便地与Eureka等服务注册中心集成。

#### 区别

|                | Feign                  | OpenFeign                             |
|----------------|------------------------|---------------------------------------|
| 定义             | 声明式的Web Service客户端     | Spring Cloud的子项目，扩展和增强了Feign          |
| 注解支持           | 支持JAX-RS标准的注解          | 支持Spring MVC注解，更适合Spring Cloud项目      |
| 维护状态           | 已不再由Netflix维护          | 得到持续维护和更新，更加稳定可靠                      |
| 集成性            | 可与Eureka和Ribbon等组件组合使用 | 内置Ribbon,与Eureka等注册中心集成更方便            |
| Spring Cloud支持 | 需要额外封装和集成              | 作为Spring Cloud子项目，与Spring Cloud生态集成更好 |
| 社区与活跃度         | 由于不再维护，社区活跃度可能较低       | 作为Spring Cloud的一部分，社区活跃且支持良好          |

#### 与 RPC 的关系

> 虽然 Feign 和 OpenFeign 允许你以一种类似本地调用的方式来调用远程 HTTP 服务，但它们主要关注 HTTP 协议，并且依赖于像Jackson 或 Gson 这样的库来进行序列化和反序列化。  
> 完整的 RPC 框架（如 gRPC、Thrift、Dubbo等）通常具有更丰富的功能，例如支持多种传输协议、更复杂的负载均衡策略、服务发现、容错处理等。  
> 在某些情况下，可以将 Feign 或 OpenFeign 与其他工具（如 Eureka、Ribbon 等）结合使用，以构建一个完整的 RPC-like 解决方案。



