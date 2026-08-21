---
title: "Tadori1zanai 字节中国交易与广告三面（项目：分布式缓存系统 / IM 聊天系统）"
slug: "tadori-bytedance-ecom-ads-3"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节中国交易与广告三面/"
  - "/s/3tzt/"
shortlink: "3tzt"
---

# Tadori1zanai 字节中国交易与广告三面（项目：分布式缓存系统 / IM 聊天系统）

作者：Tadori1zanai  
时间：2026.5.7

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。
> - 个人项目相关的面试题用 `*` 标识。

## Comet 长连接实现原理*

I/O 多路复用指复用一个线程处理多个 socket 中的事件，减少线程数量和上下文切换开销。`select`、`poll`、`epoll` 是内核提供给用户态的多路复用系统调用，进程可以通过一次系统调用获取多个连接上的事件。

- 长连接的关键是服务端如何高效维护大量持续存在的 socket。
- 长连接本质是一次建连后长期复用，支持双向通信和服务端主动推送。
- 连接很多时，服务端依赖 I/O 多路复用机制，例如 Linux 下的 epoll。
- Go 代码上常写成一连接一 goroutine，底层 runtime 会通过 netpoll 结合 epoll 管理网络 I/O。
- goroutine 做网络读写时，如果 socket 未就绪，Go runtime 会把 goroutine 挂起，并把 fd 注册到底层 epoll。
- 内核通知 fd 可读或可写时，runtime 再唤醒对应 goroutine 继续执行。

## LRU 的缺点

- 容易被顺序扫描打穿，大量只访问一次的数据会把真正热点挤出去。
- LRU 只看最近访问时间，无法识别长期高频访问的稳定热点。
- 标准实现通常是 map 加双向链表，命中后需要更新链表，高并发下锁竞争明显。

## LRU 如何增强并发性能？

- 优先做分片，把缓存拆成多个 shard，每个 shard 有自己的 map、链表和锁。
- 业务允许时，可以把严格 LRU 放宽成近似 LRU，例如异步或批量更新访问顺序。
- 并发和流量进一步提高时，可以结合多级缓存、热点保护，或使用更适合工程场景的淘汰策略。
