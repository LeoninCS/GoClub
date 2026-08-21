---
title: "Tadori1zanai 字节广告与架构一面（项目：分布式缓存系统 / IM 聊天系统）"
slug: "tadori-bytedance-ads-arch-1"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节广告与架构一面/"
  - "/s/o3wv/"
shortlink: "o3wv"
---

# Tadori1zanai 字节广告与架构一面（项目：分布式缓存系统 / IM 聊天系统）

作者：Tadori1zanai  
时间：2026.5.27

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。
> - 个人项目相关的面试题用 `*` 标识。

## 长连接如何实现*

- 客户端和 Comet 先建立 TCP 或 WebSocket 连接。
- 认证后把连接和用户绑定。
- 通过心跳维持连接活性。
- 服务端维护用户到连接的映射。
- 后端有消息时，路由到对应连接并下发。

服务端维护大量连接：

- 代码层面可以是一连接一个 goroutine。
- 底层 runtime 通过 netpoll 机制，结合 epoll 管理网络 I/O。
- 这种方式把大量连接复用到较少系统线程上执行。

## 缓存雪崩如何避免？

- 给过期时间加入随机数，避免大量数据在同一时间过期。
- 使用互斥锁或 singleflight，cache miss 时让同一时间只有一个请求构建缓存。
- 互斥锁需要设置超时时间。
- 使用后台任务主动更新缓存，减少请求链路上的集中回源。
