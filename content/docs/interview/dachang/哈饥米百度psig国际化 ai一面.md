---
title: "哈饥米百度psig国际化 ai一面"
slug: "hajimi-baidu-psig-ai-1"
aliases:
  - "/docs/interview/dachang/哈饥米百度psig国际化 ai一面/"
  - "/s/lcak/"
shortlink: "lcak"
---

# 百度 psig 国际化 ai 一面

## 项目

1. 项目拷打。

## Redis

1. Redis 存一个商品的各项信息，用什么数据结构？
2. Redis 存一个商品的库存，可能并发增减，用什么数据结构？
3. Redis 存最近 20 条评论，用什么数据结构？除了 zset 还能用什么？
4. 缓存三剑客。
5. Redis 内存淘汰策略有什么？
6. Redis 事务和 MySQL 事务区别。

## MySQL

1. 怎么排查 MySQL 慢查询？
2. 假设用户表数据量太大，怎么分表？有没有后续动态去扩容这个表，同时它的分布也比较均匀的分表方法？
3. 用户表存了手机号，分表后一个一个表扫描太慢了，应该怎么查询？

## 计算机基础

1. 发送一个 curl 请求发生了什么？
2. 如何解析 SSE 的数据帧？
3. Linux I/O 多路复用原理？epoll 如果来了新事件，怎么唤醒阻塞进程？
4. Linux 权限 644 是什么？
5. Work stealing。

## 手撕

1. 多协程交替打印 1 和 2。
2. 堆排序。
