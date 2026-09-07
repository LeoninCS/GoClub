---
title: "Tadori1zanai 字节中国交易与广告一面"
slug: "tadori-bytedance-ecom-ads-1"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节中国交易与广告一面/"
  - "/s/axz3/"
shortlink: "axz3"
---

# Tadori1zanai 字节中国交易与广告一面

作者：Tadori1zanai  
时间：2026.4.28

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。

## WaitGroup 底层是如何实现的？

- `WaitGroup` 本质是一个带阻塞能力的计数器，用于等待一组 goroutine 执行完成。
- 它内部通过原子操作维护计数器，`Add` 增加任务数，`Done` 减少任务数。
- 当计数器不为 0 时，调用 `Wait` 的 goroutine 会被挂起。
- 最后一个 `Done` 把计数器减为 0 时，会通过 runtime 的信号量机制唤醒所有阻塞的 goroutine。
- 为了降低锁开销，`WaitGroup` 使用 CAS 维护状态，并结合 runtime 调度器实现阻塞与唤醒。

## sync.Once 底层原理

- `sync.Once` 用于保证某个函数在并发环境下只执行一次。
- 内部通过原子变量 `done` 和互斥锁实现。
- `Do` 方法先通过原子读检查 `done` 标志，已经执行过就直接返回。
- 未执行时进入加锁慢路径，在临界区内二次检查。
- 执行函数完成后，通过原子写将 `done` 置为 1。
