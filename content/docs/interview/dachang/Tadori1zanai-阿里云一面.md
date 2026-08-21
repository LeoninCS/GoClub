---
title: "Tadori1zanai 阿里云一面（项目：分布式缓存系统 / IM 聊天系统）"
slug: "tadori-aliyun-1"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-阿里云一面/"
  - "/s/rig3/"
shortlink: "rig3"
---

# Tadori1zanai 阿里云一面（项目：分布式缓存系统 / IM 聊天系统）

作者：Tadori1zanai  
时间：2026.5.27

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。
> - 个人项目相关的面试题用 `*` 标识。

## HTTP 长轮询和 WebSocket 的区别

HTTP 长轮询和 WebSocket 都可以实现服务端向客户端推送数据，但原理不同。

- HTTP 长轮询本质上仍然是 HTTP 请求。
- 客户端发起请求后，服务器没有数据时会挂起请求，直到有新数据或超时再返回。
- 客户端收到响应后会立刻再次发起请求。
- WebSocket 是在 HTTP 握手后升级为长连接协议。
- WebSocket 建立持久 TCP 连接后，客户端和服务端都可以主动发送消息。
- WebSocket 实现真正的全双工通信。
- WebSocket 不需要频繁创建请求和传输 HTTP Header，因此实时性更高、开销更低。

## WebSocket 中心跳包如何实现*

- 客户端周期性发送 heartbeat 包。
- 服务端收到后返回 heartbeat reply，并刷新连接的超时定时器。
- 长时间没有收到心跳时，服务端认为连接失效，关闭连接并清理在线映射。
- 心跳的核心作用是连接保活和在线状态维护。

## etcd 的架构

暂无回答。

## etcd 的一致性如何实现？

暂无回答。
