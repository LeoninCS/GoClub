---
title: "操作系统"
---

# 操作系统

这里用于整理操作系统面试中的高频基础问题，重点围绕内存、进程线程、调度与文件系统等主题。

## 内存

### 虚拟内存是什么？为什么要有？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 虚拟内存是对物理内存的抽象，每个进程看到独立地址空间，由系统负责映射到物理内存/磁盘。面试里可按三点展开：进程隔离提升安全性；支持按需调页，扩大可用内存；降低对连续物理内存的要求。


**关键点：**
- 进程隔离提升安全性。
- 支持按需调页，扩大可用内存。
- 降低对连续物理内存的要求。

</div>
</details>

### 内存分页的好处和问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 分页把内存按固定大小管理，提升利用率与管理效率，但会带来页表和缺页开销。面试里可按两点展开：优势：减少外部碎片、支持虚拟内存；问题：内部碎片、TLB miss 和缺页成本。


**关键点：**
- 优势：减少外部碎片、支持虚拟内存。
- 问题：内部碎片、TLB miss 和缺页成本。

</div>
</details>

### 内存碎片是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 碎片是“有空闲但不好用”的内存，分外部碎片和内部碎片。面试里可按两点展开：外部碎片：空闲块不连续；内部碎片：分配块内部未用满。


**关键点：**
- 外部碎片：空闲块不连续。
- 内部碎片：分配块内部未用满。

</div>
</details>

### 分页中断（缺页异常）是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 访问的页不在物理内存时触发缺页异常，系统把页换入并重试指令。面试里可按两点展开：触发条件：页表项无效或不在内存；处理流程：换入 -> 更新页表 -> 重执行。


**关键点：**
- 触发条件：页表项无效或不在内存。
- 处理流程：换入 -> 更新页表 -> 重执行。

</div>
</details>

## 进程与线程

### 进程、线程、协程有什么区别？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 进程是资源隔离单位，线程是调度单位，协程是用户态轻量执行流。面试里可按三点展开：隔离性：进程最强；切换成本：进程 > 线程 > 协程；协程适合高并发，但依赖运行时调度。


**关键点：**
- 隔离性：进程最强。
- 切换成本：进程 > 线程 > 协程。
- 协程适合高并发，但依赖运行时调度。

</div>
</details>

### 进程的 5 个状态及转换

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 新建、就绪、运行、阻塞、终止，状态按调度与事件驱动发生转换。面试里可按三点展开：就绪 <-> 运行由调度器控制；运行 -> 阻塞多由 I/O 或锁等待触发；阻塞 -> 就绪由事件完成触发。


**关键点：**
- 就绪 <-> 运行由调度器控制。
- 运行 -> 阻塞多由 I/O 或锁等待触发。
- 阻塞 -> 就绪由事件完成触发。

</div>
</details>

### 常见进程调度算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见有 FCFS、SJF/SRTF、优先级、RR、HRRN，不同算法平衡吞吐、公平与响应时间。面试里可按三点展开：RR 响应好，适合交互系统；SJF 均值好但可能饿死长作业；优先级调度要配老化避免饥饿。


**关键点：**
- RR 响应好，适合交互系统。
- SJF 均值好但可能饿死长作业。
- 优先级调度要配老化避免饥饿。

</div>
</details>

### 死锁的四个必要条件

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 互斥、请求并保持、不可剥夺、循环等待，四者同时满足才会死锁。面试里重点展开：面试常问“怎么破坏其中一个条件”。


**关键点：**
- 面试常问“怎么破坏其中一个条件”。

</div>
</details>

### 如何避免死锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 核心是破坏死锁必要条件，例如统一加锁顺序、一次性申请资源、失败回退重试。面试里可按两点展开：固定资源申请顺序最常用；保持事务/锁持有时间短。


**关键点：**
- 固定资源申请顺序最常用。
- 保持事务/锁持有时间短。

</div>
</details>

## 调度与置换

### 页面置换算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 内存不足时选择被淘汰页面，常见 FIFO、OPT、LRU、LFU。面试里可按两点展开：OPT 理论最优不可直接实现；LRU 工程实践最常见。


**关键点：**
- OPT 理论最优不可直接实现。
- LRU 工程实践最常见。

</div>
</details>

### 磁盘调度算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 目标是减少寻道时间，常见 FCFS、SSTF、SCAN、CSCAN、LOOK。面试里可按两点展开：SSTF 吞吐高但可能饥饿；SCAN/CSCAN 公平性更好。


**关键点：**
- SSTF 吞吐高但可能饥饿。
- SCAN/CSCAN 公平性更好。

</div>
</details>

## 网络模型

### I/O 多路复用是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 用少量线程监听多个连接就绪事件，再分发处理，提升并发连接处理效率。面试里可按两点展开：典型机制：`select/poll/epoll`；重点价值：减少线程数量和上下文切换。


**关键点：**
- 典型机制：`select/poll/epoll`。
- 重点价值：减少线程数量和上下文切换。

</div>
</details>

### Reactor 和 Proactor 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Reactor 关注“就绪通知”，Proactor 关注“完成通知”。面试里可按两点展开：Reactor：应用自己执行读写；Proactor：内核完成 I/O 后回调通知。


**关键点：**
- Reactor：应用自己执行读写。
- Proactor：内核完成 I/O 后回调通知。

</div>
</details>

## Linux 命令

### 基础操作

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 掌握文件、进程、网络、权限四类基本命令即可覆盖大多数排障场景。面试里可按两点展开：文件：`ls/cd/cat/tail/grep`；进程：`ps/top/kill`。


**关键点：**
- 文件：`ls/cd/cat/tail/grep`。
- 进程：`ps/top/kill`。

</div>
</details>

### 如何查看 CPU 占用情况

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常用 `top`、`htop`、`pidstat`，先看整体再看进程和线程。面试里可按两点展开：区分用户态、系统态、iowait；结合时间窗口看趋势，不只看瞬时值。


**关键点：**
- 区分用户态、系统态、iowait。
- 结合时间窗口看趋势，不只看瞬时值。

</div>
</details>

### 如何 kill 一个进程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先温和终止，再强制终止：`kill -15 pid`，必要时 `kill -9 pid`。面试里可按两点展开：优先 `-15` 给清理机会；`-9` 会直接杀进程，可能导致资源未释放。


**关键点：**
- 优先 `-15` 给清理机会。
- `-9` 会直接杀进程，可能导致资源未释放。

</div>
</details>

### 如何查看网络性能指标

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 用 `ss/netstat` 看连接，用 `iftop/nload` 看带宽，用 `ping/traceroute` 看链路延迟。面试里可按两点展开：连接数、重传率、RTT 是关键指标；要结合应用日志定位根因。


**关键点：**
- 连接数、重传率、RTT 是关键指标。
- 要结合应用日志定位根因。
</div>
</details>
