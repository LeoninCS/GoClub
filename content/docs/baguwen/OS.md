---
title: "操作系统"
aliases:
  - "/s/imsm/"
shortlink: "imsm"
---

# 操作系统

这里用于整理操作系统面试中的高频基础问题，重点围绕内存、进程线程、调度与文件系统等主题。

## 内存

### 虚拟内存是什么？为什么要有？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 虚拟内存是操作系统给每个进程提供的独立逻辑地址空间，进程访问的是虚拟地址，CPU 和操作系统通过页表把它映射到物理内存或磁盘中的后备存储。它的价值是进程隔离、按需加载、简化内存管理、支持更大的地址空间。即使物理内存有限，系统也可以把暂时不用的页面换出，把正在使用的页面换入。

**要答的点：**
- 抽象：每个进程看到连续、独立的虚拟地址空间。
- 映射：虚拟地址通过页表映射到物理页框。
- 隔离：进程之间默认不能直接访问对方地址空间。
- 按需调页：访问到尚未装入内存的页时触发缺页处理。
- 内存利用：降低连续物理内存需求，提升多进程并发运行能力。
- 成本：页表、TLB miss、缺页换入和换出都会带来额外开销。

**重点讲解摘录：**
- OSTEP 把虚拟化内存描述为每个进程拥有自己的私有地址空间。
- Linux 内核文档说明虚拟内存系统管理虚拟地址到物理内存的映射。
- Intel 手册把分页描述为线性地址到物理地址的转换机制。
- xv6 book 把页表作为地址转换和进程隔离的核心结构。
- 面试回答要同时讲收益和代价，体现工程取舍。

**原文链接：**
- [OSTEP: Virtualization](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: Memory Management](https://docs.kernel.org/mm/index.html)
- [Intel 64 and IA-32 Architectures SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [xv6 book: Page tables](https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf)

</div>
</details>

### 内存分页的好处和问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 分页把虚拟地址空间和物理内存都切成固定大小的页，虚拟页通过页表映射到物理页框。好处是管理简单、减少外部碎片、支持非连续物理内存分配、支持按需加载和换页；问题是会产生页表内存开销、地址转换开销、TLB miss、内部碎片和缺页 I/O 成本。面试里要把“固定大小带来简单”和“页表/缺页带来成本”一起讲。

**要答的点：**
- 固定粒度：常见页大小是 4KB，也支持大页。
- 减少外部碎片：物理页框固定大小，分配更容易。
- 支持虚拟内存：虚拟页可以映射到任意物理页框。
- 支持换页：冷页可以换出到磁盘，热页按需换入。
- 页表成本：页表本身占内存，多级页表用于降低稀疏地址空间成本。
- 性能成本：TLB miss 和缺页会显著拉高访问延迟。

**重点讲解摘录：**
- OSTEP 分页章节强调固定大小页让空间管理更灵活。
- Linux 内核文档把页表描述为虚拟内存管理的核心数据结构。
- Intel 手册说明 TLB 用来缓存线性地址到物理地址转换结果。
- 缺页会让 CPU 进入内核，由内核完成页面分配、换入或异常处理。
- 内部碎片来自最后一页未完全使用的空间。

**原文链接：**
- [OSTEP: Paging](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: Page Tables](https://docs.kernel.org/mm/page_tables.html)
- [Intel 64 and IA-32 Architectures SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)

</div>
</details>

### 内存碎片是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 内存碎片是内存空间被分配和释放后出现的低效利用现象，核心分为外部碎片和内部碎片。外部碎片是总空闲空间足够，但分散成多个小块，无法满足连续大块分配；内部碎片是分配单位大于实际需要，已分配块内部有一部分空间闲置。分页主要缓解外部碎片，固定页大小也会带来内部碎片。

**要答的点：**
- 外部碎片：空闲块分散，连续大块难分配。
- 内部碎片：分配块内部存在未使用空间。
- 分页影响：物理内存按页框分配，缓解连续分配压力。
- 段式影响：可变长段更容易产生外部碎片。
- 分配器治理：伙伴系统、slab/slub、内存压缩等都会围绕碎片治理。
- 工程表现：大页分配失败、内存利用率高但仍 OOM、长期运行服务内存抖动。

**重点讲解摘录：**
- OSTEP 内存分配章节把碎片作为空闲空间管理的核心问题。
- Linux 伙伴系统通过按 2 的幂管理物理页块来降低外部碎片。
- Linux compaction 文档说明内存压缩会迁移页面，形成更大的连续空闲区。
- slab/slub 分配器用于小对象缓存，降低频繁小对象分配造成的碎片和开销。
- 面试里可以用“有空闲但凑不出需要的连续空间”解释外部碎片。

**原文链接：**
- [OSTEP: Free Space Management](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: Page Allocation](https://docs.kernel.org/mm/page_allocation.html)
- [Linux Kernel Documentation: Compaction](https://docs.kernel.org/mm/physical_memory.html)
- [Linux Kernel Documentation: Slab Allocator](https://docs.kernel.org/mm/slab.html)

</div>
</details>

### 分页中断（缺页异常）是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 缺页异常是进程访问某个虚拟页时，页表项显示该页当前无法直接访问，于是 CPU 触发异常进入内核处理。内核会判断这是合法访问还是非法访问：合法访问可能分配新页、从磁盘换入页面、建立映射并重新执行指令；非法访问会向进程发送类似 `SIGSEGV` 的信号。缺页本身是虚拟内存按需加载的正常机制，频繁缺页会导致性能急剧下降。

**要答的点：**
- 触发：页表项不存在、无权限、未驻留内存或写时复制。
- 处理：进入内核 page fault handler，检查 VMA 和权限。
- 合法缺页：分配物理页、读取文件页或 swap 页、更新页表。
- 非法访问：地址越界或权限错误，进程收到异常信号。
- 重试：处理完成后 CPU 重新执行触发缺页的指令。
- 性能：minor fault 不涉及磁盘，major fault 需要 I/O，成本更高。

**重点讲解摘录：**
- Linux 内核文档把 page fault 处理放在虚拟内存管理核心路径里。
- Intel 手册定义 page-fault exception，用于报告地址转换或权限检查失败。
- Linux `getrusage` 里区分 minor page faults 和 major page faults。
- 写时复制场景下，写共享页会触发缺页并复制私有页面。
- 面试回答里要区分“正常按需加载”和“非法访问崩溃”。

**原文链接：**
- [Linux Kernel Documentation: Memory Management](https://docs.kernel.org/mm/index.html)
- [Linux man-pages: getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)
- [Intel 64 and IA-32 Architectures SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)

</div>
</details>

## 进程与线程

### 进程、线程、协程有什么区别？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 进程是资源容器，拥有独立地址空间、文件描述符、权限上下文等资源；线程是进程内的调度实体，同一进程的线程共享地址空间和大部分资源，各自拥有栈和寄存器上下文；协程是用户态或语言运行时管理的轻量执行单元，通常由运行时调度到线程上执行。三者的区别可以从资源隔离、调度层级、切换成本和通信方式来答。

**要答的点：**
- 进程：资源隔离强，创建和切换成本更高，进程间通信需要 IPC。
- 线程：共享进程资源，内核参与调度，线程间共享内存通信方便。
- 协程：用户态/运行时调度，创建和切换更轻，适合大量并发任务。
- 切换成本：通常进程高于线程，线程高于协程。
- 风险：线程共享内存带来数据竞争，协程阻塞行为依赖运行时和 I/O 模型。
- Go 追问：goroutine 是由 Go runtime 调度的协程式并发执行单元。

**重点讲解摘录：**
- Linux `pthreads(7)` 说明同一进程线程共享全局内存，各自有栈。
- Microsoft Learn 把进程描述为拥有虚拟地址空间和至少一个线程。
- Go FAQ 说明 goroutine 初始栈很小，并由运行时管理。
- Go runtime 通过 GMP 把大量 goroutine 多路复用到 OS 线程上。
- 面试里用“资源、调度、切换、通信”四个维度最稳。

**原文链接：**
- [Linux man-pages: pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [Microsoft Learn: Processes and Threads](https://learn.microsoft.com/en-us/windows/win32/procthread/processes-and-threads)
- [Go FAQ: Goroutines](https://go.dev/doc/faq#goroutines)
- [Go Source: runtime/HACKING.md](https://go.dev/src/runtime/HACKING.md)

</div>
</details>

### 进程的 5 个状态及转换

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 经典五状态模型包括新建、就绪、运行、阻塞、终止。新建进程完成创建后进入就绪队列；调度器选中后从就绪进入运行；运行中等待 I/O、锁、事件时进入阻塞；事件完成后回到就绪；时间片耗尽或被抢占时从运行回到就绪；进程执行完成或被杀死后进入终止。Linux 实际状态更多，比如 running、sleeping、stopped、zombie，但面试五状态模型按这条主线答即可。

**要答的点：**
- 新建：进程被创建，PCB 和资源逐步初始化。
- 就绪：资源基本满足，等待 CPU 调度。
- 运行：正在 CPU 上执行。
- 阻塞：等待 I/O、锁、信号、定时器等事件。
- 终止：执行结束或被信号杀死，等待资源回收。
- 转换：调度、抢占、等待事件、事件完成、退出是核心触发条件。

**重点讲解摘录：**
- OSTEP 调度章节使用 running、ready、blocked 描述进程主要运行状态。
- Linux `proc_pid_stat(5)` 列出进程状态字符，例如 R、S、D、T、Z。
- `ps` 和 `top` 显示的进程状态来自内核任务状态。
- 僵尸进程表示进程已终止，但父进程尚未回收退出状态。
- 面试可先答经典五状态，再补 Linux 状态体现实践经验。

**原文链接：**
- [OSTEP: Process API and Scheduling](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux man-pages: proc_pid_stat(5)](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html)
- [Linux man-pages: ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html)

</div>
</details>

### 常见进程调度算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见调度算法有 FCFS、SJF、SRTF、优先级调度、时间片轮转 RR、多级反馈队列 MLFQ。FCFS 简单但短任务可能等待很久；SJF/SRTF 平均周转时间好，但需要估计运行时间；优先级调度能体现任务重要性，但要配老化避免饥饿；RR 响应好，适合交互系统；MLFQ 通过多队列和动态优先级兼顾响应与吞吐。Linux CFS 则用虚拟运行时间追求公平。

**要答的点：**
- FCFS：按到达顺序执行，实现简单。
- SJF/SRTF：优先短任务，平均等待时间低。
- Priority：按优先级调度，常配合 aging。
- RR：固定时间片轮转，改善交互响应。
- MLFQ：多级队列，动态调整优先级。
- CFS：Linux 常见公平调度器，用虚拟运行时间分配 CPU。

**重点讲解摘录：**
- OSTEP 调度章节系统讲解 FIFO、SJF、STCF、RR、MLFQ。
- Linux CFS 文档说明 CFS 追踪每个任务的虚拟运行时间，并选择最需要运行的任务。
- RR 通过时间片让多个任务轮流获得 CPU，适合交互场景。
- 优先级调度配 aging 可以降低低优先级任务长期等待风险。
- 面试回答要把算法目标讲出来：周转时间、响应时间、公平性、吞吐量。

**原文链接：**
- [OSTEP: Scheduling](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: CFS Scheduler](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [Linux man-pages: sched(7)](https://man7.org/linux/man-pages/man7/sched.7.html)

</div>
</details>

### 什么是死锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 死锁是多个线程或进程因争夺资源形成相互等待，每个执行单元都持有一部分资源，同时等待别人释放资源，最终整体无法继续推进。典型例子是线程 A 拿着锁 1 等锁 2，线程 B 拿着锁 2 等锁 1。面试里答完定义后，应顺手补出四个必要条件和工程规避手段。

**要答的点：**
- 本质：多个执行单元相互等待资源。
- 结果：相关任务都无法继续执行。
- 常见资源：锁、数据库行锁、连接、文件、信号量。
- 典型场景：加锁顺序相反、事务范围过大、嵌套调用持锁。
- 排查：线程栈、数据库死锁日志、锁等待图。
- 处理：超时、回滚、统一加锁顺序和缩短临界区。

**重点讲解摘录：**
- OSTEP 并发章节把死锁描述为线程之间互相等待导致系统卡住。
- MySQL InnoDB 文档说明数据库会检测事务死锁并回滚其中一个事务。
- Java、Go、数据库领域都能用资源等待图理解死锁。
- 死锁分析的核心是找等待环。
- 面试里把“定义 -> 四条件 -> 破坏条件”连起来答最完整。

**原文链接：**
- [OSTEP: Deadlock](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [MySQL 8.4 Reference Manual: Deadlocks in InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html)
- [Linux man-pages: pthread_mutex_lock(3p)](https://man7.org/linux/man-pages/man3/pthread_mutex_lock.3p.html)

</div>
</details>

### 死锁的四个必要条件

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 死锁四个必要条件是互斥、请求并保持、不可剥夺、循环等待。互斥表示资源同一时刻只能被一个执行单元占有；请求并保持表示已经持有资源时继续申请新资源；不可剥夺表示资源只能由持有者主动释放；循环等待表示多个执行单元形成环形等待链。工程上避免死锁就是破坏其中一个条件，最常用的是统一资源申请顺序，破坏循环等待。

**要答的点：**
- 互斥：共享资源需要独占访问。
- 请求并保持：持有旧资源时继续等待新资源。
- 不可剥夺：资源不能被外部强制抢走。
- 循环等待：等待关系形成闭环。
- 规避思路：一次性申请、固定顺序、超时释放、失败回退。
- 追问：数据库死锁常靠检测等待图并回滚一个事务解决。

**重点讲解摘录：**
- OSTEP 死锁章节列出 mutual exclusion、hold-and-wait、no preemption、circular wait。
- 破坏循环等待是工程中最常见的做法，例如全局锁顺序。
- 数据库事务里固定访问表和行的顺序也能降低死锁概率。
- 请求超时和重试能把永久等待变成可恢复失败。
- 面试里四个条件要一口气说全，再举一个锁顺序例子。

**原文链接：**
- [OSTEP: Deadlock](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [MySQL 8.4 Reference Manual: Deadlocks in InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html)

</div>
</details>

### 如何避免死锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 避免死锁的核心是减少持锁等待和破坏循环等待。工程上最常用的是固定加锁顺序、缩短临界区、避免持锁做 I/O、一次性申请资源、申请失败释放已有资源后重试、设置锁等待超时。数据库场景还要控制事务大小、统一表和行访问顺序、建立合适索引缩小锁范围，并为死锁回滚准备幂等重试。

**要答的点：**
- 固定顺序：所有线程按统一顺序申请资源。
- 缩短持锁：减少锁内逻辑，避免持锁 RPC、I/O、慢 SQL。
- 一次性申请：提前申请所需资源，失败后整体回退。
- 超时重试：锁等待超时后释放资源并重试。
- 降低粒度：用更细粒度锁或无锁结构减少冲突面。
- 数据库：短事务、好索引、固定访问顺序、捕获死锁错误后重试。

**重点讲解摘录：**
- OSTEP 把死锁预防建立在破坏四个必要条件上。
- MySQL InnoDB 文档建议让事务短小，并在死锁发生后重试事务。
- Java 和 POSIX 锁实践里，锁排序是常见的死锁预防方法。
- 数据库缺索引会扩大锁范围，增加等待环出现概率。
- 面试收口可以说：预防优先，检测和重试兜底。

**原文链接：**
- [OSTEP: Deadlock](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [MySQL 8.4 Reference Manual: Deadlock Minimization](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)
- [Go Packages: sync.Mutex](https://pkg.go.dev/sync#Mutex)

</div>
</details>

## 调度与置换

### 页面置换算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 页面置换算法是在物理内存紧张时选择哪些页面换出。常见算法有 FIFO、OPT、LRU、Clock、LFU。OPT 理论上选择未来最长时间不会访问的页，效果最好但依赖未来信息；FIFO 简单但可能出现 Belady 异常；LRU 基于最近访问历史，工程效果好但精确维护成本高；Clock 是 LRU 的近似实现，用访问位降低维护成本；LFU 看访问频率，适合稳定热点。

**要答的点：**
- FIFO：先进先出，简单，效果可能不稳定。
- OPT：理论最优，用于评估算法上限。
- LRU：淘汰最近最少使用页，利用时间局部性。
- Clock：用 reference bit 近似 LRU，成本更低。
- LFU：淘汰访问频率低的页，适合长期热点。
- 评价指标：缺页率、实现开销、公平性和抗抖动能力。

**重点讲解摘录：**
- OSTEP 页面置换章节讲解 FIFO、Random、LRU、Clock 等算法。
- Linux 页面回收使用活跃/非活跃链表等近似 LRU 思想。
- Clock 算法通过访问位给页面第二次机会。
- 工作集过大时频繁换入换出会形成 thrashing。
- 面试里把 OPT 作为理论参照，把 LRU/Clock 作为实践重点。

**原文链接：**
- [OSTEP: Beyond Physical Memory: Policies](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: Page Reclaim](https://docs.kernel.org/mm/page_reclaim.html)
- [Linux Kernel Documentation: Multi-Gen LRU](https://docs.kernel.org/admin-guide/mm/multigen_lru.html)

</div>
</details>

### 磁盘调度算法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 磁盘调度算法的目标是安排 I/O 请求顺序，降低寻道和旋转等待，提高吞吐并控制延迟。经典算法有 FCFS、SSTF、SCAN、C-SCAN、LOOK、C-LOOK。FCFS 公平但寻道可能大；SSTF 优先处理最近磁道，吞吐好但远端请求可能等待久；SCAN 像电梯一样单方向处理请求，到头再反向；C-SCAN 单方向循环，等待时间更均匀；LOOK/C-LOOK 在最远请求处折返或循环。

**要答的点：**
- FCFS：按到达顺序处理，公平简单。
- SSTF：优先最近磁道，减少平均寻道。
- SCAN：电梯算法，方向性扫描。
- C-SCAN：单方向循环扫描，等待更均衡。
- LOOK：到当前方向最远请求处折返。
- 现代补充：SSD 寻道成本弱化，调度更多关注合并请求、队列公平和延迟。

**重点讲解摘录：**
- OSTEP 磁盘章节讲解寻道、旋转和传输是机械磁盘 I/O 成本来源。
- Linux block layer 文档说明 I/O 调度器负责合并和排序块设备请求。
- 机械硬盘时代的电梯算法核心是减少磁头移动。
- SSD 场景下随机访问成本低，调度目标会转向延迟隔离和吞吐。
- 面试回答经典算法即可，补一句现代存储差异会更稳。

**原文链接：**
- [OSTEP: Hard Disk Drives](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Linux Kernel Documentation: Block Layer](https://docs.kernel.org/block/index.html)
- [Linux Kernel Documentation: blk-mq](https://docs.kernel.org/block/blk-mq.html)

</div>
</details>

## 网络模型

### I/O 多路复用是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** I/O 多路复用是用一个或少量线程同时监听多个文件描述符的就绪事件，哪个连接可读、可写或异常，就处理哪个连接。它让服务端无需为每个连接创建一个线程，减少线程数量和上下文切换，适合高并发连接场景。常见机制是 `select`、`poll`、`epoll`，其中 `epoll` 在 Linux 高并发服务里最常见。

**要答的点：**
- 目标：少量线程管理大量连接。
- 事件：关注可读、可写、异常、关闭等状态。
- `select`：位图集合，有 fd 数量和重复拷贝/扫描成本。
- `poll`：数组表示 fd 集合，突破部分限制但仍要线性扫描。
- `epoll`：内核维护兴趣集合，就绪事件通过队列返回。
- 应用：Nginx、Redis、Netty、Go netpoll 都和事件驱动 I/O 相关。

**重点讲解摘录：**
- Linux `select(2)` 说明它等待多个文件描述符变为 ready。
- Linux `poll(2)` 说明它等待一组文件描述符上的事件。
- Linux `epoll(7)` 描述 epoll 是 Linux 的 I/O event notification facility。
- Reactor 模型常基于 I/O 多路复用分发事件。
- 面试中要强调“就绪通知”，后续读写通常仍由应用完成。

**原文链接：**
- [Linux man-pages: select(2)](https://man7.org/linux/man-pages/man2/select.2.html)
- [Linux man-pages: poll(2)](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Linux man-pages: epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [Go Source: runtime netpoll](https://go.dev/src/runtime/netpoll.go)

</div>
</details>

### Reactor 和 Proactor 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Reactor 是就绪事件模型：内核通知某个 fd 已经可读或可写，应用再执行 `read/write` 并处理数据。Proactor 是完成事件模型：应用发起异步 I/O，内核完成读写后通知应用，回调拿到的是完成结果。Linux 常见 `select/poll/epoll` 更偏 Reactor；Windows IOCP 是典型 Proactor；实际框架会根据系统能力做混合实现。

**要答的点：**
- Reactor：等待就绪，应用负责真正 I/O。
- Proactor：提交异步操作，内核完成后通知结果。
- 事件含义：Reactor 是 ready，Proactor 是 complete。
- 典型实现：epoll + 非阻塞 fd 常用于 Reactor；IOCP 常用于 Proactor。
- 编程模型：Reactor 回调里读写；Proactor 回调里处理已完成数据。
- 场景：高并发网络框架常围绕这两个模型设计。

**重点讲解摘录：**
- POSIX `select/poll/epoll` 都是在等待 fd 就绪。
- Microsoft IOCP 文档把完成端口用于高效处理异步 I/O 完成通知。
- Reactor 模式论文把事件分发器和事件处理器作为核心角色。
- Proactor 模式强调异步操作完成后调用 completion handler。
- 面试里一句话区分：Reactor 关注能不能做，Proactor 关注做完了。

**原文链接：**
- [Linux man-pages: epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [Microsoft Learn: I/O Completion Ports](https://learn.microsoft.com/en-us/windows/win32/fileio/i-o-completion-ports)
- [Douglas C. Schmidt: Reactor Pattern](https://www.dre.vanderbilt.edu/~schmidt/PDF/reactor-siemens.pdf)
- [Douglas C. Schmidt: Proactor Pattern](https://www.dre.vanderbilt.edu/~schmidt/PDF/proactor.pdf)

</div>
</details>

## Linux 命令

### 基础操作

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Linux 基础命令可以按文件、文本、进程、网络、磁盘、权限六类准备。文件类有 `ls/cd/pwd/cp/mv/rm/find`；文本类有 `cat/less/head/tail/grep/sed/awk`；进程类有 `ps/top/kill`；网络类有 `ss/curl/ping/traceroute`；磁盘类有 `df/du/free`；权限类有 `chmod/chown`。面试里重点展示能用这些命令定位线上问题。

**要答的点：**
- 文件：`ls`、`cd`、`pwd`、`cp`、`mv`、`rm`、`find`。
- 文本：`cat`、`less`、`tail -f`、`grep`、`sed`、`awk`。
- 进程：`ps`、`top`、`pidstat`、`kill`。
- 网络：`ss`、`curl -v`、`ping`、`traceroute`。
- 磁盘内存：`df -h`、`du -sh`、`free -h`。
- 权限：`chmod`、`chown`、`umask`。

**重点讲解摘录：**
- GNU coreutils 文档覆盖 `ls`、`cp`、`mv`、`rm` 等基础命令。
- Linux `procps` 工具集提供 `ps`、`top`、`free` 等常用排障命令。
- `grep` 适合日志过滤，`tail -f` 适合实时看日志。
- `ss` 是查看 socket 状态的现代常用工具。
- 面试里可以按“先看日志，再看进程，再看端口，再看资源”组织命令。

**原文链接：**
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/coreutils.html)
- [Linux man-pages: ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html)
- [Linux man-pages: top(1)](https://man7.org/linux/man-pages/man1/top.1.html)
- [Linux man-pages: ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html)

</div>
</details>

### 如何查看 CPU 占用情况

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 查看 CPU 占用我会先用 `top` 或 `htop` 看整机负载和高 CPU 进程，再用 `pidstat -u -p <pid> 1` 看某个进程的用户态、系统态 CPU，必要时用 `top -H -p <pid>` 看线程级热点，最后结合 `perf top` 或火焰图定位函数。面试里要说明 `us/sy/wa/id` 的含义，并结合时间窗口观察趋势。

**要答的点：**
- 整机：`top`、`uptime` 看 load average 和 CPU 百分比。
- 进程：`ps -eo pid,ppid,cmd,%cpu --sort=-%cpu` 找高 CPU 进程。
- 线程：`top -H -p <pid>` 或 `ps -L` 找高 CPU 线程。
- 采样：`pidstat` 看时间序列，比瞬时值更可靠。
- 指标：`us` 用户态、`sy` 系统态、`wa` I/O 等待、`id` 空闲。
- 深入：`perf`、pprof、火焰图定位热点函数。

**重点讲解摘录：**
- `top(1)` 显示系统汇总和进程级 CPU 使用情况。
- `pidstat` 属于 sysstat 工具，可按进程报告 CPU 使用统计。
- Linux `/proc/stat` 暴露 CPU 时间分布，是很多工具的数据来源。
- 高 `iowait` 表示 CPU 在等待 I/O 完成，排查方向会转向磁盘或网络。
- load average 要结合 CPU 核数理解。

**原文链接：**
- [Linux man-pages: top(1)](https://man7.org/linux/man-pages/man1/top.1.html)
- [sysstat: pidstat](https://sysstat.github.io/)
- [Linux man-pages: proc_stat(5)](https://man7.org/linux/man-pages/man5/proc_stat.5.html)
- [Linux perf wiki](https://perf.wiki.kernel.org/index.php/Main_Page)

</div>
</details>

### 如何 kill 一个进程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** kill 进程要先确认 PID 和影响范围，再优先发送 `SIGTERM`，让进程有机会优雅退出；进程卡死或超时仍未退出时，再用 `SIGKILL` 强制结束。常用命令是 `kill -15 <pid>`、`kill -9 <pid>`，也可以用 `pkill`、`killall` 按名称处理。线上服务要先摘流量、保留日志和现场，再终止进程。

**要答的点：**
- 查 PID：`ps`、`pgrep`、`lsof -i`、`ss -ltnp`。
- 优雅退出：`kill -15 pid` 发送 `SIGTERM`。
- 强制退出：`kill -9 pid` 发送 `SIGKILL`。
- 信号含义：`SIGTERM` 可被处理，`SIGKILL` 由内核强制终止。
- 服务场景：先摘流量，再停进程，关注数据一致性和资源释放。
- 排障：进程无法退出时看 D 状态、内核 I/O 等待和父子进程关系。

**重点讲解摘录：**
- Linux `kill(1)` 说明 kill 会向进程发送信号。
- Linux `signal(7)` 列出标准信号，`SIGTERM` 默认终止进程，`SIGKILL` 立即终止且不可捕获。
- `pgrep/pkill` 可以按进程名匹配进程并发送信号。
- systemd 管理的服务优先用 `systemctl stop/restart`，让服务管理器保持状态一致。
- 面试里强调先 `-15` 再 `-9`，体现线上谨慎操作。

**原文链接：**
- [Linux man-pages: kill(1)](https://man7.org/linux/man-pages/man1/kill.1.html)
- [Linux man-pages: signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)
- [Linux man-pages: pgrep(1)](https://man7.org/linux/man-pages/man1/pgrep.1.html)
- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

</div>
</details>

### 如何查看网络性能指标

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 网络性能我会分连接、带宽、延迟、丢包、重传和应用响应来看。连接状态用 `ss -s`、`ss -tanp`；带宽用 `iftop/nload/sar -n DEV`；延迟和丢包用 `ping/mtr/traceroute`；TCP 重传和错误用 `netstat -s` 或 `ss -i`；应用层用 `curl -w` 看 DNS、连接、TLS、首包和总耗时。指标要和服务日志、网关日志、机器负载一起判断。

**要答的点：**
- 连接：ESTAB、TIME_WAIT、CLOSE_WAIT、监听端口和连接数。
- 带宽：网卡吞吐、包速率、丢包、错误包。
- 延迟：RTT、抖动、跨机房链路。
- 重传：TCP retransmits、拥塞窗口、发送/接收队列。
- 应用耗时：DNS、connect、TLS、TTFB、total time。
- 工具：`ss`、`sar`、`ping`、`mtr`、`traceroute`、`curl -w`、`tcpdump`。

**重点讲解摘录：**
- `ss(8)` 用于查看 socket 状态，比旧 `netstat` 更常用。
- `ping(8)` 通过 ICMP echo 测量连通性和 RTT。
- `traceroute(8)` 显示到目标的网络路径。
- curl 的 `-w` 可输出精细阶段耗时，适合定位 DNS、连接、TLS 或服务端慢。
- `tcpdump` 能抓包验证重传、握手和应用协议细节。

**原文链接：**
- [Linux man-pages: ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html)
- [Linux man-pages: ping(8)](https://man7.org/linux/man-pages/man8/ping.8.html)
- [Linux man-pages: traceroute(8)](https://man7.org/linux/man-pages/man8/traceroute.8.html)
- [curl man page](https://curl.se/docs/manpage.html)
- [tcpdump man page](https://www.tcpdump.org/manpages/tcpdump.1.html)

</div>
</details>
