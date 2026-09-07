---
title: "Tadori1zanai 字节中国交易与广告三面"
slug: "tadori-bytedance-ecom-ads-3"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节中国交易与广告三面/"
  - "/s/3tzt/"
shortlink: "3tzt"
---

# Tadori1zanai 字节中国交易与广告三面

作者：Tadori1zanai  
时间：2026.5.7

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。

## LRU 的缺点

- 容易被顺序扫描打穿，大量只访问一次的数据会把真正热点挤出去。
- LRU 只看最近访问时间，无法识别长期高频访问的稳定热点。
- 标准实现通常是 map 加双向链表，命中后需要更新链表，高并发下锁竞争明显。

## LRU 如何增强并发性能？

- 优先做分片，把缓存拆成多个 shard，每个 shard 有自己的 map、链表和锁。
- 业务允许时，可以把严格 LRU 放宽成近似 LRU，例如异步或批量更新访问顺序。
- 并发和流量进一步提高时，可以结合多级缓存、热点保护，或使用更适合工程场景的淘汰策略。
