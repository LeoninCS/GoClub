---
title: "Tadori1zanai 欢乐互娱一面"
slug: "tadori-huanle-1"
aliases:
  - "/docs/interview/xiaochang/Tadori1zanai-欢乐互娱一面/"
  - "/s/3fv6/"
shortlink: "3fv6"
---

# Tadori1zanai 欢乐互娱一面

作者：Tadori1zanai  
时间：2026.4.21

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。

## （Redis）如何实现消息队列？

基于 List 的简单队列：

- 生产者使用 `LPUSH`。
- 消费者使用 `RPOP` 或 `BRPOP`。
- 主要问题：缺少发布订阅能力，消费者处理失败后消息容易丢失。

基于 Stream 的完善队列：

- 生产者使用 `XADD`。
- 消费者使用 `XREADGROUP` 和 `XACK`。
- `XREADGROUP` 读取后消息会进入 PEL（Pending Entries List）。
- 消费者异常后，其他消费者可以通过 `XCLAIM` 接管消息。

消息可靠性：

- List 可以用“双队列 + ack”模拟确认机制：`BRPOPLPUSH queue processing_queue`，处理成功后 `LREM processing_queue msg`。
- Stream 内置 PEL 和 ACK 机制，消费后需要 `XACK`，超时消息通过 `XCLAIM` 重新分配，实现 at-least-once 语义。

消费速率控制：

- 消费者端控制并发数，或者使用令牌桶限制 QPS。
- 生产者端监控 `XLEN stream`，队列长度超过阈值后拒绝写入或降级。

Redis 队列更适合轻量任务和中小规模异步场景。Kafka 在持久化、分区扩展和吞吐能力上更适合大规模日志流。

## MySQL 慢查询如何处理？

- 先通过慢查询日志定位慢 SQL，并结合执行频率找出热点查询。
- 再用 `EXPLAIN` 分析执行计划，重点关注扫描行数、索引命中、`filesort` 和临时表。
- 索引优化：创建组合索引，让查询条件、排序字段和覆盖字段尽量匹配。
- SQL 优化：减少 `select *`，优化 join，避免深分页。
- 缓存优化：使用 Redis 缓存热点数据。
- 拆分优化：数据超过千万级别时考虑拆分小表；字段很多的大表可以做垂直拆分。

## 介绍 JWT

- JWT 是一种基于 JSON 的认证令牌。
- JWT 由 Header、Payload 和 Signature 三部分组成。
- Header 指定签名算法。
- Payload 存放用户信息和过期时间等声明。
- Signature 用于防篡改。
- 用户登录后服务端生成 JWT 返回给客户端，客户端后续请求携带 token，服务端验证签名后完成认证。
- JWT 的核心特点是服务端认证链路偏无状态，适合分布式服务横向扩展。

## JWT 的缺点

- JWT 一旦派发，在过期之前持续有效。
- 常见解决方式是在业务层增加撤销判断，例如黑名单机制。
- 可以使用 Redis 维护黑名单，主动失效某个 JWT 时把该 token 或 jti 加入黑名单。
- 每次请求先检查 token 是否命中黑名单，再做业务处理。

## 10 个并发的 goroutine，一个 panic 之后其他如何也退出？

Go 中如果子 goroutine 发生 panic 且没有被 recover，整个进程会崩溃退出，所有 goroutine 都会停止。面试里通常讨论的是捕获 panic 后如何优雅通知其他 goroutine 退出。

核心方案是 `context.WithCancel`：

- 启动 goroutine 时传入同一个 `ctx`。
- 每个 goroutine 内部用 `defer recover()` 捕获异常。
- 某个 goroutine recover 后调用 `cancel()`。
- 其他 goroutine 通过 `select` 监听 `ctx.Done()`，收到信号后释放资源并退出。

## 介绍布隆过滤器

暂无回答。

## 介绍协程池

协程池是一种并发控制机制，通过固定数量的 worker goroutine 从任务队列中取任务执行，从而限制 goroutine 数量。

常见实现是使用 channel 作为任务队列，启动固定数量的 worker goroutine，不断从队列中消费任务。协程池适合任务数量大、每个任务耗时可控、需要限制并发度的场景。
