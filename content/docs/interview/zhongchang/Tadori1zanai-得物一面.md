---
title: "Tadori1zanai 得物一面（项目：分布式缓存系统 / IM 聊天系统）"
slug: "tadori-dewu-1"
aliases:
  - "/docs/interview/zhongchang/Tadori1zanai-得物一面/"
  - "/s/y0wj/"
shortlink: "y0wj"
---

# Tadori1zanai 得物一面（项目：分布式缓存系统 / IM 聊天系统）

作者：Tadori1zanai  
时间：2026.5.11

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。
> - 个人项目相关的面试题用 `*` 标识。

## 并发读写 slice 会有什么问题？

- 可能出现数据竞争，读取到旧值、半写入值或不可预测结果。
- 如果并发 append 触发扩容，读取方可能访问旧数组或出现越界风险。
- Go runtime 对某些并发写场景会触发 fatal error，例如 concurrent map writes；slice 并发读写同样需要同步保护。

## MySQL 慢查询如何紧急处理？

紧急处理：

- 开启慢查询日志定位 SQL。
- 使用 `SHOW PROCESSLIST` 监控阻塞查询。
- 必要时 kill 长时间执行的查询。
- 临时通过缓存或从库减轻主库压力，保证核心业务可用。
- 检查并适当增加 Buffer Pool 容量。

根本优化：

- 优化 SQL，避免全表扫描和过多字段读取。
- 建立合适索引。
- 引入读写分离、分库分表或冷热分离。
- 调整 MySQL 配置，例如 Buffer Pool、连接数和慢查询阈值。
