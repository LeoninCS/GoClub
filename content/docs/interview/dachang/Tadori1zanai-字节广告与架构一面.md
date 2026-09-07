---
title: "Tadori1zanai 字节广告与架构一面"
slug: "tadori-bytedance-ads-arch-1"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节广告与架构一面/"
  - "/s/o3wv/"
shortlink: "o3wv"
---

# Tadori1zanai 字节广告与架构一面

作者：Tadori1zanai  
时间：2026.5.27

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。

## 缓存雪崩如何避免？

- 给过期时间加入随机数，避免大量数据在同一时间过期。
- 使用互斥锁或 singleflight，cache miss 时让同一时间只有一个请求构建缓存。
- 互斥锁需要设置超时时间。
- 使用后台任务主动更新缓存，减少请求链路上的集中回源。
