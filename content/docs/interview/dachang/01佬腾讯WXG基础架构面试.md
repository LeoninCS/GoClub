---
title: "01佬腾讯WXG基础架构面试"
slug: "01-tencent-wxg-infra"
aliases:
  - "/docs/interview/dachang/01佬腾讯WXG基础架构面试/"
  - "/s/ttwx/"
shortlink: "ttwx"
---

# 01佬腾讯 WXG 基础架构面试

作者：01佬

> 回答多数为 AI 生成，仅供参考。

## 面试题

### 八股

1. 进程和线程的区别？
2. 虚拟内存有什么作用？
3. TCP 是怎么保证可靠传输的？
4. 拥塞控制讲一下？
5. 你理解的 RPC 是什么？
6. 最左前缀原则？

### 算法

1. 手写 LRU。

## 参考答案

### 进程和线程的区别？

进程是操作系统资源分配的基本单位，拥有独立的虚拟地址空间、文件描述符、堆、全局变量等资源。线程是 CPU 调度的基本单位，同一进程内的多个线程共享进程资源，但各自拥有独立的栈、寄存器上下文和线程局部数据。

区别可以从四点说：

1. 资源隔离：进程之间地址空间隔离，线程共享同一进程地址空间。
2. 创建和切换成本：进程更重，线程更轻。
3. 通信方式：进程间通信需要管道、消息队列、共享内存、socket 等机制；线程间可以直接共享内存，但需要锁保护。
4. 稳定性：一个进程崩溃通常影响自身；同一进程内一个线程异常可能影响整个进程。

### 虚拟内存有什么作用？

虚拟内存给每个进程提供独立、连续的地址空间，再由操作系统和 MMU 通过页表映射到物理内存。

主要作用：

1. 进程隔离：每个进程看到自己的地址空间，互相隔离，提升安全性和稳定性。
2. 简化编程模型：程序认为自己拥有连续内存，实际物理内存可以离散分配。
3. 提高内存利用率：按需加载页面，用到时再分配物理页。
4. 支持内存扩展：物理内存不足时，可以把部分页面换出到磁盘。
5. 支持共享和保护：共享库、mmap、页权限控制都依赖虚拟内存机制。

### TCP 是怎么保证可靠传输的？

TCP 通过一组机制共同保证可靠传输：

1. 序列号：每个字节都有序列号，接收方可以按序重组数据。
2. 确认应答：接收方通过 ACK 告诉发送方已经收到哪些数据。
3. 超时重传：发送方在超时时间内没有收到 ACK，会重传对应报文。
4. 快速重传：连续收到重复 ACK 时，发送方可以提前重传丢失报文。
5. 滑动窗口：通过发送窗口控制未确认数据量，提高吞吐。
6. 流量控制：接收方通过窗口大小告诉发送方自己的接收能力，避免接收缓冲区被打满。
7. 拥塞控制：根据网络拥塞程度调整发送速率，降低丢包和拥塞扩散。
8. 校验和：检测报文在传输过程中的错误。

### 拥塞控制讲一下？

拥塞控制解决的是发送方如何根据网络状态调整发送速率。TCP 主要通过拥塞窗口 `cwnd` 控制网络中未确认的数据量。

常见阶段：

1. 慢启动：连接开始时 `cwnd` 较小，每收到一个 ACK 增长，整体呈指数增长。
2. 拥塞避免：`cwnd` 达到阈值 `ssthresh` 后，增长变慢，近似线性增长。
3. 快速重传：收到多个重复 ACK，说明中间某个包可能丢失，立即重传。
4. 快速恢复：发生丢包后降低 `ssthresh` 和 `cwnd`，再逐步恢复发送速率。

面试里可以补一句：拥塞控制关注网络承载能力，流量控制关注接收方处理能力。

### 你理解的 RPC 是什么？

RPC 是 Remote Procedure Call，远程过程调用。它让调用远程服务像调用本地函数一样，屏蔽网络通信、序列化、连接管理、超时、重试等细节。

一次 RPC 调用通常包含：

1. 客户端调用本地代理方法。
2. 框架把方法名、参数、元数据序列化成请求。
3. 通过网络发送到服务端。
4. 服务端反序列化请求，调用真正的业务方法。
5. 服务端把结果序列化后返回。
6. 客户端反序列化响应，得到返回值或错误。

工程上 RPC 框架通常还包括服务发现、负载均衡、超时控制、重试、熔断、限流、链路追踪和鉴权。

### 最左前缀原则？

最左前缀原则是联合索引的匹配规则。对于联合索引 `(a, b, c)`，查询条件需要从最左列 `a` 开始连续匹配，才能充分利用索引。

例子：

- `where a = ?` 可以用到索引。
- `where a = ? and b = ?` 可以用到 `a,b`。
- `where a = ? and b = ? and c = ?` 可以用到 `a,b,c`。
- `where b = ?` 无法按最左前缀使用该联合索引。
- `where a = ? and c = ?` 通常只能用到 `a`，中间缺了 `b`。

遇到范围查询时，范围列后面的列通常无法继续用于有序定位。例如 `(a,b,c)` 中 `where a = ? and b > ? and c = ?`，索引主要用到 `a,b`，`c` 很难继续用于索引定位。

### 手写 LRU

LRU 常用哈希表 + 双向链表实现：

- 哈希表负责 O(1) 定位节点。
- 双向链表维护访问顺序，头部是最近使用，尾部是最久未使用。
- `Get` 命中后把节点移动到头部。
- `Put` 已存在则更新并移动到头部；新 key 超过容量时淘汰尾部节点。

```go
package main

type node struct {
	key, value int
	prev, next *node
}

type LRUCache struct {
	capacity int
	items    map[int]*node
	head     *node
	tail     *node
}

func Constructor(capacity int) LRUCache {
	head := &node{}
	tail := &node{}
	head.next = tail
	tail.prev = head
	return LRUCache{
		capacity: capacity,
		items:    make(map[int]*node),
		head:     head,
		tail:     tail,
	}
}

func (c *LRUCache) Get(key int) int {
	n, ok := c.items[key]
	if !ok {
		return -1
	}
	c.moveToFront(n)
	return n.value
}

func (c *LRUCache) Put(key int, value int) {
	if n, ok := c.items[key]; ok {
		n.value = value
		c.moveToFront(n)
		return
	}

	n := &node{key: key, value: value}
	c.items[key] = n
	c.addFront(n)

	if len(c.items) > c.capacity {
		old := c.tail.prev
		c.remove(old)
		delete(c.items, old.key)
	}
}

func (c *LRUCache) moveToFront(n *node) {
	c.remove(n)
	c.addFront(n)
}

func (c *LRUCache) addFront(n *node) {
	n.prev = c.head
	n.next = c.head.next
	c.head.next.prev = n
	c.head.next = n
}

func (c *LRUCache) remove(n *node) {
	n.prev.next = n.next
	n.next.prev = n.prev
}
```
