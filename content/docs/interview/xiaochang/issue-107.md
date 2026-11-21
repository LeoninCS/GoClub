---
title: "My3tique-沥泉科技-Go后端开发-一面"
---

## 项目与微服务架构

### 项目概述与微服务技术栈

1. 自我介绍？

   > 做了个自我介绍。

2. 详细介绍一下 go-zero，如何使用 pb 去开发？

   > 主要使用 go-zero 构建微服务架构，对外通过 HTTP 提供 RESTful API，对内通过 gRPC 实现服务间通信。
   >
   > 开发时，首先编写 .proto 文件，定义 Message 请求响应结构和 Service 接口，再使用 goctl 自动生成 PB 代码、gRPC 客户端和服务端代码。
   >
   > 业务逻辑主要写在 Logic 层，通过 ServiceContext 管理数据库、Redis 和 RPC 客户端等依赖。
   >
   > HTTP 服务通过 zrpc 客户端调用内部 RPC 服务，使用 etcd 实现服务注册与发现。
   >
   > 此外，通过 HTTP Middleware 和 gRPC Interceptor 分别实现鉴权等功能。

3. 详细讲述一下你对 gRPC 的了解？

   > gRPC 是一个高性能、开源、跨语言的 RPC 框架，主要用于分布式系统中的服务间通信。
   >
   > 它的核心思想是让客户端像调用本地函数一样调用远程服务的方法，但底层实际上涉及网络通信、序列化和反序列化。
   >
   > gRPC 默认使用 Protobuf 定义接口和序列化消息。开发时，我们先在 .proto 文件中定义 Message 和 Service，再通过 protoc 或 goctl 生成客户端和服务端代码。
   >
   > 在底层通信方面，gRPC 通常基于 HTTP/2，支持多路复用、二进制分帧和流量控制。相比传统的 HTTP/1.1 通信，它更适合需要高并发和流式传输的服务间调用。
   >
   > gRPC 提供四种通信模式：Unary 普通请求响应、Server Streaming 服务端流、Client Streaming 客户端流和 Bidirectional Streaming 双向流。
   >
   > 此外，gRPC 还提供了 Metadata 元数据、Interceptor 拦截器、Deadline 超时控制、状态码、TLS 加密，以及可配置的负载均衡和重试机制。
   >
   > 在我的项目中，使用 go-zero 的 zrpc 封装 gRPC。HTTP Gateway 接收前端请求，再通过 RPC Client 调用内部微服务，通过 etcd 实现服务注册与发现。
   >
   > 我认为 gRPC 最大的优势是接口契约清晰、序列化效率较高、支持跨语言和流式通信，比较适合微服务内部通信。

4. 这个项目用的是 HTTP 方式，还是 gRPC 方式，还是两种方式都有？

   > 面试的时候只回答了两个都有。
   >
   > 我的项目同时使用了 HTTP 和 gRPC。
   >
   > 对外通过 go-zero 的 REST 框架提供 HTTP API，主要用于和前端交互；对内通过 zrpc 封装的 gRPC 实现微服务之间的通信。
   >
   > 开发 RPC 服务时，使用 Protobuf 定义接口，通过 goctl 自动生成相关代码，再在 Logic 层实现业务。
   >
   > 服务间通过 etcd 进行注册与发现，对于异步业务则通过消息队列进行解耦。

### 整体架构与服务拆分

5. 再详细讲述一下这个架构，从入口到服务，再到存储，是怎么串起来的？

   > 我的 OJ 项目采用 HTTP + gRPC + MQ 的微服务架构。对外通过 go-zero 的 App API 和 Admin API 提供 RESTful 接口，对内通过 gRPC 实现各微服务通信。以前端提交代码为例，请求首先进入 App API，经过 Middleware 完成鉴权，再由 Handler 解析参数并进入 Logic。HTTP Logic 通过 ServiceContext 中的 zrpc 客户端调用 Submit RPC，RPC 服务通过 etcd 进行注册与发现。Submit RPC 接收请求后，先将提交记录持久化到数据库。为了保证数据库写入和消息投递之间的最终一致性，我们设计了 Outbox 模式，在同一数据库事务中写入提交记录和待发送事件，然后由 Dispatcher 把任务投递到 MQ。Judge Worker 消费消息后，在 Docker 沙箱中执行代码，完成编译、运行和测试，并将评测结果持久化。我们还设计了 Inbox 幂等和 Attempt Lease 机制，处理重复消息、Worker 宕机以及过期结果回写的问题。最后前端通过 HTTP 查询接口获取评测结果，也可以通过 SSE 实现状态推送。整个架构实现了入口与业务解耦、同步调用与异步处理分离，并且允许 RPC 服务和 Worker 独立扩容。

6. 定义了哪些 gRPC 模块？

   > 我的 OJ 项目主要拆分成五个 gRPC 服务：Auth RPC、Submit RPC、Judge RPC、Problem RPC 和 Contest RPC。
   >
   > 它们分别负责用户认证、代码提交、评测管理、题目管理以及比赛管理。
   >
   > 对外通过 App API 和 Admin API 提供 HTTP 接口，内部通过 gRPC 实现服务间通信，并使用 etcd 进行服务注册与发现。
   >
   > 对于耗时的代码评测任务，则通过 MQ 异步投递给 Judge Worker，避免阻塞 HTTP 请求。

### 服务注册发现与链路追踪

7. 详细讲述一下，是怎么用 etcd 找到服务名称的？是固定写的，还是怎么进行服务发现的？

   > 在我们的项目中，使用 go-zero 集成 etcd 实现服务注册与发现。
   >
   > 每个 RPC 服务都有提前约定好的 Etcd.Key，例如 Submit RPC 使用 submit.rpc。
   >
   > RPC 服务启动时，会自动将自己的可访问 IP 和端口注册到 etcd，并通过 Lease 和 KeepAlive 维持注册信息。
   >
   > 调用方配置相同的服务 Key，go-zero 的 zrpc 客户端通过 etcd 获取实例地址，并利用 Watch 机制监听实例变化，在本地维护可用实例列表。
   >
   > 实际 RPC 请求不会每次都查询 etcd，而是通过客户端负载均衡选择实例，直接发起 gRPC 调用。
   >
   > 如果实例宕机，租约过期后 etcd 会删除对应注册信息，客户端收到变更后更新地址列表。
   >
   > 所以服务名称是提前约定的，但具体服务地址可以动态变化。

8. 用 etcd 是发现微服务的地址，还是说用 etcd 去调用 gRPC 呢？

   > 我们使用 etcd 做服务注册与发现，而不是通过 etcd 调用 gRPC。
   >
   > RPC 服务启动后会将自己的 IP 和端口注册到 etcd。调用方通过服务 Key 获取可用实例地址，再由 gRPC 客户端直接调用目标服务。
   >
   > 所以 etcd 解决的是服务在哪里的问题，gRPC 解决的是服务之间怎么通信的问题。

9. gRPC 在启动时，是如何注册到 etcd 里面的？

   > 在我们的项目中，使用 go-zero 的 zrpc 集成 etcd 实现服务注册。
   >
   > 首先在 RPC 的 YAML 配置文件中指定 etcd 集群地址、服务 Key 和监听端口。
   >
   > 当 RPC 服务调用 server.Start() 启动时，go-zero 会自动向 etcd 注册当前服务实例的 IP 和端口，并通过 Lease 和 KeepAlive 机制持续续租。
   >
   > 如果服务正常退出，会主动注销注册信息；如果服务异常宕机，租约过期后 etcd 会自动删除对应记录。
   >
   > 其他微服务通过相同的 Etcd Key 发现这些实例，再通过 gRPC 进行通信。

10. 再讲一下 trace？

    > Trace 主要用于分布式链路追踪，帮助我们定位一次请求经过了哪些微服务，以及各个环节的耗时和异常。
    >
    > 我们使用 go-zero 集成的 OpenTelemetry 实现链路追踪。
    >
    > 当 HTTP 请求进入 Gateway 时，会创建或接续 Trace，在 Context 中保存 Trace ID 等追踪信息。
    >
    > 当 Gateway 调用内部 gRPC 服务时，框架通过 Interceptor 将追踪上下文传递到 gRPC Metadata，下游服务提取后创建自己的 Span，从而将多个服务的调用串成一条完整链路。
    >
    > 追踪数据可以导出到 Jaeger，通过 Trace ID 查看各个服务的调用关系和耗时，快速定位慢接口和异常。

## 秒杀业务

11. 秒杀业务主要是哪一块？

    > 我们项目中的秒杀业务主要由 Seckill RPC 负责，核心是解决高并发情况下的库存超卖问题。
    >
    > 用户请求先经过 HTTP Gateway，再调用 Seckill RPC。秒杀服务通过 Redis Lua 脚本原子校验库存和用户购买资格，成功后预扣库存。
    >
    > 为了降低数据库压力，我们采用 MQ 异步处理订单，在数据库层通过事务和条件更新保证库存不会超卖。
    >
    > 同时结合消息幂等、失败重试和补偿机制，保证订单与库存的最终一致性。

12. 秒杀业务的 Redis 是如何实现的，用的是哪种数据结构？

    > 在我们的秒杀业务中，Redis 主要使用了 String、ZSet、Hash 和 Stream 四种数据结构。
    >
    > 首先使用 String 缓存商品库存，活动开始前将数据库库存预热到 Redis，秒杀时使用 Lua 脚本原子判断和扣减库存，防止高并发超卖。
    >
    > 其次，使用 ZSet 实现活动级滑动窗口限流，使用 Hash 实现用户级令牌桶限流。
    >
    > 库存预扣成功后，通过 Redis Stream 异步投递订单，由消费者读取消息，再通过 PostgreSQL 事务创建订单和更新库存。
    >
    > 最后，结合数据库唯一索引、条件更新以及失败补偿机制，保证订单幂等和库存一致性。
