---
title: "Go"
aliases:
  - "/s/68l5/"
shortlink: "68l5"
---

# Go

这里整理 Go 面试中高频出现的语言、并发、运行时和工程相关问题，适合作为专题复习提纲。

## 1. 为什么选 Go 语言

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 我选择 Go，主要看重它在后端服务里的工程效率、并发能力和部署体验。Go 语法简洁、编译快、标准工具链完善，团队协作时容易形成统一代码风格；goroutine 和 channel 让并发代码更轻量，适合 I/O 密集、高并发服务；编译后的单二进制方便容器化和发布，配合云原生生态做微服务、网关、基础设施工具很顺手。

**要答的点：**
- 工程效率：语法小、编译快、`gofmt`、`go test`、`go mod` 等工具链统一。
- 并发能力：goroutine 初始栈小，由运行时调度，channel 提供类型安全通信。
- 服务端适配：标准库覆盖 HTTP、JSON、SQL、加密等常用能力，适合网络服务。
- 部署体验：单二进制交付，容器化和跨平台构建成本低。
- 取舍意识：Go 适合业务服务、云原生基础设施、CLI 工具和中间件开发。

**重点讲解摘录：**
- Go 官方文档说 Go 是 “expressive, concise, clean, and efficient”，面试时可以把它落到工程效率上：代码风格统一、样板代码少、构建反馈快。
- Go 云服务专题提到 Go 的 “built-in support for concurrency”，对应后端场景里的高并发连接、异步任务、RPC 服务和网关转发。
- Go FAQ 说 Go 试图 “combine the ease of programming” 与静态编译语言的效率和安全性，这正是 Go 在业务服务里的核心价值。
- Effective Go 说明 goroutine “costing little more than the allocation of stack space”，可以用来解释 goroutine 比直接管理线程更轻量。

**原文链接：**
- [Go Documentation](https://go.dev/doc/)
- [Go for Cloud & Network Services](https://go.dev/solutions/cloud/)
- [Go FAQ: Why did you create a new language?](https://go.dev/doc/faq#creating_a_new_language)
- [Effective Go: Goroutines](https://go.dev/doc/effective_go#goroutines)

</div>
</details>

## 2. 讲一下协程、线程、进程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 进程是操作系统分配资源的基本单位，线程是进程内被 CPU 调度执行的基本单位，协程是用户态或语言运行时管理的轻量执行单元。进程有独立地址空间和系统资源；同一进程内的线程共享地址空间、文件句柄等资源，同时各自拥有栈和寄存器上下文；Go 里的 goroutine 由 Go runtime 调度，并多路复用到多个 OS 线程上执行。

**要答的点：**
- 进程：资源容器，拥有虚拟地址空间、打开的文件、权限上下文等资源。
- 线程：调度实体，同一进程内线程共享进程资源，各自有栈、寄存器和线程局部状态。
- 协程：用户态/运行时层面的任务抽象，切换更轻，适合组织大量并发任务。
- Go goroutine：初始栈小，由 runtime 调度，阻塞 I/O 时 runtime 会让其他 goroutine 继续运行。
- 成本关系：进程切换涉及地址空间等资源切换；线程切换依赖内核调度；goroutine 调度成本更低。

**重点讲解摘录：**
- Microsoft Learn 把进程描述为拥有 “virtual address space”、句柄、安全上下文和至少一个线程，这对应“进程管资源”。
- Microsoft Learn 把线程描述为 “entity within a process”，并说明线程共享进程的地址空间和系统资源，这对应“线程被调度”。
- Linux man-pages 对 pthread 的描述是线程 “share the same global memory”，同时 “each thread has its own stack”，这能解释线程共享与独立上下文的边界。
- Effective Go 说 goroutine 是 “function executing concurrently”，并且 “lightweight”，适合用来解释 Go 并发的轻量性。
- Go FAQ 说 goroutine 栈通常只有 “a few kilobytes”，并且 runtime 会自动扩缩栈，这能解释 Go 可以创建大量 goroutine。

**原文链接：**
- [Microsoft Learn: About Processes and Threads](https://learn.microsoft.com/en-us/windows/win32/procthread/about-processes-and-threads)
- [Linux man-pages: pthreads(7)](https://www.man7.org/linux/man-pages/man7/pthreads.7.html)
- [Effective Go: Goroutines](https://go.dev/doc/effective_go#goroutines)
- [Go FAQ: goroutines](https://go.dev/doc/faq#goroutines)

</div>
</details>

## 3. defer 执行顺序

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `defer` 会把一次函数调用登记起来，在外层函数返回前执行。多个 `defer` 按后进先出执行；`defer` 后面的函数值和参数会在执行到 `defer` 语句时立即求值并保存；如果函数有命名返回值，`return` 会先给返回值赋值，然后执行 `defer`，最后把返回值交给调用方。

**要答的点：**
- 触发时机：外层函数执行 `return`、执行到函数末尾，或者发生 `panic` 展开栈时，都会执行已登记的 `defer`。
- 执行顺序：多个 `defer` 按 LIFO 顺序执行，后登记的先执行。
- 参数求值：`defer f(x)` 中的 `f` 和 `x` 在登记时求值，真正调用在返回前发生。
- 返回顺序：先设置返回值，再执行 `defer`，最后返回给调用方。
- 命名返回值：闭包形式的 `defer` 可以读取和修改命名返回值，常用于补充错误信息和释放资源。

**重点讲解摘录：**
- Go Spec 说 `defer` 的执行点是外层函数返回前，来源包括 `return`、函数体结束和 goroutine panicking。
- Go Spec 说每次执行 `defer` 时，函数值和参数都会 “evaluated as usual” 并保存下来，这解释了 `defer fmt.Println(i)` 会打印登记时的 `i`。
- Go Spec 说 deferred functions 会按 “reverse order they were deferred” 调用，这就是后进先出。
- Go Blog 总结了三条规则：参数立即求值、调用按 “Last In First Out” 执行、可读取和修改命名返回值。
- Go Blog 的例子 `return 1` 后再由 `defer func(){ i++ }()` 修改命名返回值，最终返回 `2`。

**原文链接：**
- [Go Spec: Defer statements](https://go.dev/ref/spec#Defer_statements)
- [Go Blog: Defer, Panic, and Recover](https://go.dev/blog/defer-panic-and-recover)

</div>
</details>

## 4. slice 扩容机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** slice 本身是一个三元组，包含底层数组指针、长度和容量。`append` 时新长度在容量范围内会直接复用原底层数组；新长度超过容量时，runtime 会申请更大的底层数组，把旧元素拷过去，再返回指向新数组的 slice。Go 当前实现里，小容量通常按 2 倍增长，容量达到阈值后逐步过渡到约 1.25 倍增长，最终容量还会按内存分配规格取整。

**要答的点：**
- slice 结构：指向数组的指针、`len`、`cap`。
- 扩容触发：`append` 后目标长度超过原 `cap`。
- 扩容动作：分配新数组，拷贝旧元素，返回新的 slice header。
- 增长规则：小容量近似翻倍，大容量按更平滑的比例增长，实际值受内存对齐和 size class 影响。
- 共享问题：扩容前可能共享底层数组，扩容后新旧 slice 通常指向不同数组。

**重点讲解摘录：**
- Go Blog 说 slice 是 “descriptor of an array segment”，包含数组指针、长度和容量。
- Go Blog 说明 `append` 会在容量不足时分配 “a new, sufficiently large slice” 并复制旧数据。
- Runtime 源码 `growslice` 的注释说明它会分配新底层存储，并把已有元素 `[0, oldLen)` 复制过去。
- Runtime 源码 `nextslicecap` 里容量小于 `threshold = 256` 时直接返回 `doublecap`，这解释了小 slice 的 2 倍增长。
- Runtime 源码说明大容量会使用公式做 “smooth-ish transition”，逐步接近 1.25 倍增长。

**原文链接：**
- [Go Blog: Go Slices: usage and internals](https://go.dev/blog/slices-intro)
- [Go Source: runtime/slice.go](https://go.dev/src/runtime/slice.go)

</div>
</details>

## 5. map 底层设计（map 是否并发安全）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Go 的 `map` 是内置哈希表，key 必须是可比较类型，查询、插入、删除平均复杂度接近 O(1)。`map` 是引用类型，`make` 会初始化底层哈希结构；具体底层结构属于 runtime 实现细节，新版本 Go 已经从老的 bucket/overflow 设计演进到 SwissTable 风格实现。并发方面，多个 goroutine 同时读写同一个普通 `map` 需要加锁或用其他同步方式，典型做法是 `map + sync.RWMutex`；读多写少、key 稳定的缓存场景可以考虑 `sync.Map`。

**要答的点：**
- 数据结构：`map` 是哈希表，按 key 的 hash 定位存储位置，再做 key 比较确认命中。
- key 限制：key 类型必须可比较；slice、map、function 这类类型需要转换成可比较表示后再作为 key。
- 引用语义：`map` 变量本身像描述符，底层数据由 `make` 初始化。
- 并发安全：普通 `map` 支持并发只读；并发读写或并发写需要同步保护。
- 工程方案：大多数业务用 `map + Mutex/RWMutex`；特殊读多写少或分散 key 写入场景用 `sync.Map`。

**重点讲解摘录：**
- Go Blog 说 Go 的内置 `map` “implements a hash table”，这是回答底层设计的主线。
- Go Blog 提到 `make` 会初始化哈希表结构，同时也说明具体结构是 runtime 实现细节。
- Go Blog 写明 `map` 并发读写的结果未定义，并建议用同步机制保护访问。
- Go runtime 当前源码说明内置 `map` 基于 Abseil SwissTable 思路，核心由 slot、group、control word、table、directory 等概念组成。
- `sync.Map` 文档说它适合并发使用，并且强调普通代码通常使用 plain map 配合锁更容易保持类型安全和业务不变量。

**原文链接：**
- [Go Blog: Go maps in action](https://go.dev/blog/maps)
- [Go Spec: Map types](https://go.dev/ref/spec#Map_types)
- [Go Source: internal/runtime/maps/map.go](https://go.dev/src/internal/runtime/maps/map.go)
- [Go Packages: sync.Map](https://pkg.go.dev/sync#Map)

</div>
</details>

## 6. map 扩容机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Go `map` 会在哈希表装载过高、可用槽位不足或删除留下的 tombstone 影响探测效率时触发增长/rehash。当前 runtime 的实现基于 SwissTable 思路，`map` 可以由多个 table 组成，用目录按 hash 高位选择 table；增长发生在单个 table 上，小表可以替换成容量翻倍的新 table，超过单表上限后会把 table 拆成两个 table，并在需要时扩大目录。面试里重点说清“触发原因、重排成本、增量思想、迭代影响”。

**要答的点：**
- 触发原因：元素增加导致负载上升，或者删除产生 tombstone，继续插入时可用槽不足。
- 增长动作：哈希探测序列依赖 group 数量，扩容时需要把 table 内槽位重新排列。
- 增量设计：`map` 拆成多个 table，每次只增长某个 table，把一次大搬迁拆小。
- 增长方式：容量在上限内通常替换为更大的 table；超过上限会 split 成两个 table。
- 迭代语义：扩容期间迭代要保证每个元素最多返回一次，迭代顺序由 runtime 决定。

**重点讲解摘录：**
- Runtime 注释说 probe sequence 依赖 group 数量，因此增长 group 数时 “all slots must be reordered”。
- Runtime 注释说为了支持 “incremental growth”，map 会把内容分散到多个 table，每个 table 仍是完整哈希表。
- Runtime 注释说 map 初始是单 table，在 `maxTableCapacity` 之前增长会替换成 “double capacity” 的 table。
- Runtime 注释说超过上限后增长会 “splits the table into two”，并通过 extendible hashing 的 directory 选择 table。
- `table.go` 注释说 tombstone 会计入 rehash 条件，`used + tombstones` 超过负载阈值时需要 rehash，维持较短探测链。

**原文链接：**
- [Go Source: internal/runtime/maps/map.go](https://go.dev/src/internal/runtime/maps/map.go)
- [Go Source: internal/runtime/maps/table.go](https://go.dev/src/internal/runtime/maps/table.go)
- [Go Blog: Go maps in action](https://go.dev/blog/maps)

</div>
</details>

## 7. CSP 是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** CSP 全称是 Communicating Sequential Processes，是一种用“独立顺序执行的进程 + 消息通信”来组织并发系统的模型。Go 借鉴了这个思想：goroutine 负责并发执行，channel 负责在 goroutine 之间传递数据或信号。它的核心价值是把共享状态的修改权通过通信转移出去，让同一时刻的数据归属更清晰，从而减少显式锁竞争和数据竞争。

**要答的点：**
- CSP 概念：多个顺序执行单元并发运行，通过通信发生交互。
- Go 落地：goroutine 是执行单元，channel 是通信和同步工具。
- 设计思想：通过发送数据或所有权来协调并发，降低共享可变状态复杂度。
- 常见场景：任务分发、结果汇总、超时取消、流水线、生产消费。
- 工程取舍：channel 适合表达数据流和协作关系；共享状态、计数器、临界区也常用 mutex/atomic。

**重点讲解摘录：**
- Hoare 的 CSP 论文摘要说 input 和 output 是基本编程原语，通信进程的并行组合是重要的程序结构方法。
- Go Blog 说 goroutine 和 channel 提供了组织并发软件的方式，并把历史源头指向 Hoare 的 CSP。
- Go Blog 提出 Go 鼓励用 channel 在 goroutine 间传递数据引用，让同一时刻只有一个 goroutine 访问该数据。
- Effective Go 用“通过通信共享内存”概括 Go 的并发风格。
- Go Blog 也承认传统模型用锁保护共享数据；面试时可以说 Go 提倡 channel 风格，同时标准库也提供 `sync` 和 `sync/atomic`。

**原文链接：**
- [Go Blog: Share Memory By Communicating](https://go.dev/blog/share-memory-by-communicating)
- [Effective Go: Share by communicating](https://go.dev/doc/effective_go#sharing)
- [CACM: Communicating Sequential Processes](https://cacm.acm.org/research/communicating-sequential-processes/)

</div>
</details>

## 8. 讲一下 Go 中的 Channel

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** channel 是 Go 里 goroutine 之间传递值和同步状态的类型安全管道。无缓冲 channel 强调同步交接，发送方和接收方要同时准备好；有缓冲 channel 带固定容量队列，缓冲未满时发送可以先进入队列，缓冲非空时接收可以直接取值。工程里常用 channel 做任务分发、结果汇总、信号通知、流水线和退出控制，并配合 `select`、`context` 处理超时、取消和多路等待。

**要答的点：**
- 类型安全：`chan T` 只能传递 `T` 类型值，也可以声明单向 channel。
- 无缓冲：发送和接收同步配对，天然提供同步点。
- 有缓冲：容量固定，满了发送阻塞，空了接收阻塞，可用于削峰和限制并发。
- 关闭语义：发送方关闭 channel；接收方可用 `v, ok := <-ch` 判断是否关闭。
- 常见搭配：`range ch` 消费直到关闭，`select` 监听多个 channel，`context.Done()` 做取消通知。

**重点讲解摘录：**
- Go Spec 说 channel 提供一种机制，让并发执行的函数通过发送和接收指定类型的值来通信。
- Go Spec 说容量为 0 或无缓冲时，只有发送方和接收方都准备好，通信才会成功。
- Effective Go 说无缓冲 channel 把值交换和同步结合起来，可以保证两个 goroutine 处于已知状态。
- Go Blog pipelines 文章强调发送方可以关闭 channel 告诉接收方值已经发送完，接收方可以用 `range` 持续接收直到 channel 关闭。
- Effective Go 用 buffered channel 限制并发执行数量，这对应面试中常说的“信号量模式”。

**原文链接：**
- [Go Spec: Channel types](https://go.dev/ref/spec#Channel_types)
- [Go Spec: Send statements](https://go.dev/ref/spec#Send_statements)
- [Effective Go: Channels](https://go.dev/doc/effective_go#channels)
- [Go Blog: Pipelines and cancellation](https://go.dev/blog/pipelines)

</div>
</details>

## 9. 是否可以读写已关闭的 Channel

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 已关闭的 channel 可以继续接收。接收时会先把缓冲区里已有的数据读完；缓冲读空后，再接收会立即返回元素类型零值，并且 `ok=false`。向已关闭 channel 发送会 panic；重复关闭已关闭 channel 也会 panic；关闭 nil channel 也会 panic。

**要答的点：**
- 读已关闭 channel：可以读，缓冲区剩余值会正常返回。
- 读空的已关闭 channel：立即返回零值，`v, ok := <-ch` 中 `ok=false`。
- 写已关闭 channel：触发 run-time panic。
- 关闭规则：发送方负责关闭；重复关闭和关闭 nil channel 都会 panic。
- nil channel：发送和接收都会永久阻塞，常在 `select` 中用来动态关闭某个 case。

**重点讲解摘录：**
- Go Spec 说 closed channel 上的 receive 可以立即继续，读完已有值后返回元素类型零值。
- Go Spec 说多返回值接收里的 `ok` 可以报告通信是否成功，channel 关闭且为空时 `ok=false`。
- Go Spec 说 send on a closed channel 会导致 run-time panic。
- Go Spec 说 sending to or closing a closed channel causes panic，closing nil channel 也会 panic。
- Go Spec 说 nil channel 始终处于通信未就绪状态，发送和接收 nil channel 都会阻塞。

**原文链接：**
- [Go Spec: Receive operator](https://go.dev/ref/spec#Receive_operator)
- [Go Spec: Send statements](https://go.dev/ref/spec#Send_statements)
- [Go Spec: Close](https://go.dev/ref/spec#Close)
- [Go Spec: Channel types](https://go.dev/ref/spec#Channel_types)

</div>
</details>

## 10. select 和 switch 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `switch` 是普通条件分支，用表达式值或类型选择执行哪个分支；`select` 是 channel 通信多路复用，用来等待多个发送/接收操作中的一个继续执行。`switch` 按 case 顺序匹配第一个满足条件的分支；`select` 会先判断哪些 channel 操作已经 ready，如果多个 case 同时 ready，会伪随机选一个；所有 case 都未 ready 时，有 `default` 就执行 `default`，其余情况会阻塞等待。

**要答的点：**
- 用途：`switch` 做值/类型分支，`select` 做 channel 发送/接收分支。
- case 内容：`switch case` 是表达式或类型；`select case` 必须是 channel send/receive 或 `default`。
- 匹配规则：`switch` 从上到下选择第一个匹配项；`select` 从 ready 通信里伪随机选一个。
- 阻塞行为：`select` 在所有通信 case 都未 ready 且缺少 `default` 时阻塞；`switch` 按表达式立即选择分支。
- 常见场景：`select` 配合 `time.After`、`ticker.C`、`ctx.Done()` 做超时、定时、取消和多路等待。

**重点讲解摘录：**
- Go Spec 说 `select` 看起来像 `switch`，但所有 case 都引用通信操作。
- Go Spec 说 `select` 中如果一个或多个通信可进行，会通过 “uniform pseudo-random selection” 选择一个执行。
- Go Spec 说所有通信 case 都未 ready 时，有 `default` 选 `default`，其余情况阻塞。
- Go Spec 说只包含 nil channel 且缺少 default 的 `select` 会永久阻塞。
- Go Spec 说 expression switch 会把 switch 表达式与 case 表达式比较，选择第一个相等的 case。

**原文链接：**
- [Go Spec: Select statements](https://go.dev/ref/spec#Select_statements)
- [Go Spec: Switch statements](https://go.dev/ref/spec#Switch_statements)
- [Effective Go: Channels of channels](https://go.dev/doc/effective_go#chan_of_chan)

</div>
</details>

## 11. 原子操作和锁的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 原子操作是 CPU/运行时提供的低层同步原语，适合对单个共享变量做简单的 load、store、add、swap、CAS；锁是更高层的互斥机制，适合保护一段临界区，让多步操作和多个变量保持一致。面试选型时看状态复杂度：计数器、开关、指针发布这类简单状态可以用 atomic；map、队列、余额变更、状态机流转这类复合不变量优先用 mutex/RWMutex。

**要答的点：**
- 原子操作：单条读改写具有不可分割性，并提供内存同步语义。
- 锁：`Lock` 到 `Unlock` 之间形成临界区，可以保护任意复杂逻辑。
- 表达能力：atomic 更低层、更难组合；mutex 更清晰，便于维护复合状态。
- 性能取舍：atomic 在低竞争简单场景开销小；高竞争下 CAS 自旋也可能浪费 CPU。
- Go 建议：普通业务优先用 channel 或 `sync` 包，atomic 适合底层库和简单共享状态。

**重点讲解摘录：**
- `sync/atomic` 文档说 atomic 提供 “low-level atomic memory primitives”，并提醒需要非常小心地使用。
- `sync/atomic` 文档说除特殊低层应用外，同步更适合用 channel 或 `sync` 包工具完成。
- `sync` 文档说 `Mutex` 是互斥锁，`Lock` 时如果锁已被使用，调用 goroutine 会阻塞到锁可用。
- `sync` 文档说明 `Mutex.Unlock` 与后续 `Mutex.Lock` 建立 “synchronizes before” 关系，这保证临界区内写入对后续持锁者可见。
- Go 内存模型说数据竞争是并发读写同一内存位置且缺少同步，atomic、mutex、channel 都属于建立同步关系的工具。

**原文链接：**
- [Go Packages: sync/atomic](https://pkg.go.dev/sync/atomic)
- [Go Packages: sync.Mutex](https://pkg.go.dev/sync#Mutex)
- [Go Packages: sync.RWMutex](https://pkg.go.dev/sync#RWMutex)
- [The Go Memory Model](https://go.dev/ref/mem)

</div>
</details>

## 12. 什么是自旋锁与互斥锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 自旋锁获取失败时会在 CPU 上循环尝试，等待持锁者很快释放；互斥锁获取失败时会把当前执行单元阻塞/挂起，等锁可用后再被唤醒。自旋锁适合临界区极短、竞争很轻、等待时间小于线程切换成本的场景；互斥锁适合临界区更长或竞争更明显的场景。Go 用户层通常直接用 `sync.Mutex`，它的 runtime 实现会在合适条件下短暂自旋，随后进入等待队列，并在长等待时切到饥饿模式保证公平性。

**要答的点：**
- 自旋锁：等待期间占用 CPU，换来减少线程/协程挂起唤醒成本。
- 互斥锁：等待期间阻塞，释放 CPU，适合等待时间更长的临界区。
- 场景选择：临界区越短、竞争越轻，自旋越有价值；等待越长，互斥阻塞更合适。
- Go 实践：业务代码用 `sync.Mutex` / `sync.RWMutex`，少手写自旋锁。
- Go 实现：`sync.Mutex` 内部包含正常模式、饥饿模式、短暂 active spinning 和 semaphore 等机制。

**重点讲解摘录：**
- `sync.Mutex` 文档说 Mutex 是 “mutual exclusion lock”，锁被占用时 `Lock` 会阻塞到锁可用。
- Go internal `Mutex` 源码注释说正常模式下 waiter 排 FIFO 队列，但新到 goroutine 有运行中优势，会和被唤醒 waiter 竞争锁。
- Go internal `Mutex` 源码注释说 waiter 等待超过 1ms 会把锁切到 starvation mode，锁所有权直接交给队首 waiter。
- Go internal `Mutex` 源码在慢路径中调用 `runtime_canSpin`，注释写着 “Active spinning makes sense”，说明 Go 的互斥锁会在合适条件下短暂自旋。
- Go runtime lock 源码里有 `active_spin = 4` 这类参数，说明运行时锁也会使用有限自旋控制短等待成本。

**原文链接：**
- [Go Packages: sync.Mutex](https://pkg.go.dev/sync#Mutex)
- [Go Source: internal/sync/mutex.go](https://go.dev/src/internal/sync/mutex.go)
- [Go Source: runtime/lock_spinbit.go](https://go.dev/src/runtime/lock_spinbit.go)

</div>
</details>

## 13. sync.Map 和普通 map 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 普通 `map` 是 Go 内置哈希表，类型安全、性能直接，适合大多数业务场景；并发读写时需要自己用 `Mutex`、`RWMutex` 或 channel 做同步。`sync.Map` 是标准库提供的并发安全 map，所有操作方法可以被多个 goroutine 同时调用，适合读多写少、key 写入后反复读取，或者多个 goroutine 操作互不重叠 key 的场景。它的 API 基于 `any`，类型约束和复合业务不变量要靠调用方维护。

**要答的点：**
- 普通 `map`：类型明确、用法自然、性能可控；并发读写需要外部同步。
- `sync.Map`：并发安全，`Load`、`Store`、`Delete` 等操作摊还 O(1)。
- 适用场景：只写一次读多次的缓存；多 goroutine 操作不同 key 的共享表。
- 实现思路：读路径优先查只读 `read`，写入和 miss 情况走加锁的 `dirty`。
- 工程取舍：需要强类型、复杂更新、多个字段一起维护一致性时，普通 `map + RWMutex` 更清晰。

**重点讲解摘录：**
- `sync.Map` 文档说它类似 `map[any]any`，多个 goroutine 可并发使用，由内部同步完成协调。
- `sync.Map` 文档说它是 specialized，大多数代码应使用 plain Go map 配合单独锁，以获得更好的类型安全并维护其他不变量。
- `sync.Map` 文档列出的两个优化场景是：key 写一次读多次；多个 goroutine 读写不同 key 集合。
- `sync.Map` 源码里 `read` 字段是可被并发安全访问的只读部分，`dirty` 字段需要持有 `mu` 才能访问。
- `sync.Map` 源码里 `misses` 统计 read miss 次数，达到一定程度时会把 `dirty` 提升为新的 `read`，降低后续读路径成本。

**原文链接：**
- [Go Packages: sync.Map](https://pkg.go.dev/sync#Map)
- [Go Source: sync/map.go](https://go.dev/src/sync/map.go)
- [Go Blog: Go maps in action](https://go.dev/blog/maps)

</div>
</details>

## 14. 讲一下 Context 以及使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `context.Context` 用来在调用链之间传递截止时间、取消信号和请求级值。典型场景是一次 HTTP 请求里又调用数据库、RPC、缓存和 goroutine：上游请求取消或超时后，下游可以通过 `ctx.Done()` 尽快停止工作并返回 `ctx.Err()`。常用 API 是 `WithCancel`、`WithTimeout`、`WithDeadline`、`WithValue`；实践中把 `ctx` 作为函数第一个参数逐层传递，创建带取消的 context 后及时调用 `cancel()` 释放资源。

**要答的点：**
- 三个核心能力：deadline、cancel signal、request-scoped values。
- 取消传播：父 context 取消后，派生出来的子 context 都会取消。
- 常用 API：`context.Background()`、`TODO()`、`WithCancel()`、`WithTimeout()`、`WithDeadline()`、`WithValue()`。
- 使用规范：`ctx` 作为函数首参传递；创建 timeout/deadline 后 `defer cancel()`。
- Value 边界：只放请求级元数据，例如 trace id、认证信息；业务可选参数用显式参数。

**重点讲解摘录：**
- `context` 包文档说 Context 携带 deadlines、cancellation signals 和 request-scoped values，跨 API 边界和进程传递。
- `context` 包文档说传入服务器的请求应创建 Context，对外调用应接受 Context，调用链要继续传播它。
- `context` 包文档说父 Context 取消时，所有派生 Context 也会取消，这就是级联取消。
- Go Blog 说一次请求的多个 goroutine 通常需要访问用户身份、授权 token 和请求 deadline 这类请求级信息。
- Go Blog contexts-and-structs 文章引用官方建议：Contexts 应作为参数传递给需要它的函数。
- Go database cancel 文档提醒：使用 timeout 或 deadline 创建 Context 后，应始终 defer 调用返回的 cancel 函数。

**原文链接：**
- [Go Packages: context](https://pkg.go.dev/context)
- [Go Blog: Go Concurrency Patterns: Context](https://go.dev/blog/context)
- [Go Blog: Contexts and structs](https://go.dev/blog/context-and-structs)
- [Go Docs: Canceling in-progress operations](https://go.dev/doc/database/cancel-operations)

</div>
</details>

## 15. 讲一下 GMP 模型，各个字母代表什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** GMP 是 Go runtime 调度 goroutine 的核心模型：G 是 goroutine，表示要执行的 Go 代码、栈和调度状态；M 是 machine，本质是 OS 线程，负责真正执行代码；P 是 processor，表示执行 Go 代码所需的调度资源和权限，里面有本地运行队列、缓存等运行时资源。调度器的任务就是把可运行的 G、可执行的 M、可用的 P 匹配起来；M 只有拿到 P 才能执行 Go 用户代码。

**要答的点：**
- G：goroutine 的运行时对象，保存栈、指令位置、状态等信息。
- M：OS thread，可以执行 Go 代码、runtime 代码、系统调用，也可以空闲。
- P：执行 Go 代码的资源令牌，持有本地 run queue，数量通常由 `GOMAXPROCS` 决定。
- 关系：M 绑定 P 后，从本地队列或全局队列取 G 执行。
- 目标：把大量 goroutine 多路复用到有限 OS 线程上，同时减少全局锁竞争和调度成本。

**重点讲解摘录：**
- Go runtime HACKING 文档说 G 是 goroutine，M 是 OS thread，P 是执行 Go 代码所需的资源。
- 该文档明确说调度器的工作是匹配 G、M、P，也就是 “the code to execute”、“where to execute it”、“the rights and resources to execute it”。
- 文档说 M 可以执行用户 Go 代码、runtime 代码、系统调用或处于 idle 状态。
- 文档说 P 可以理解成 CPU，它代表执行用户 Go 代码所需的资源。
- `runtime.GOMAXPROCS` 文档说它设置能同时执行用户级 Go 代码的最大 CPU 数，这个值直接对应可并行运行的 P 数量。

**原文链接：**
- [Go Source: runtime/HACKING.md](https://go.dev/src/runtime/HACKING.md)
- [Go Packages: runtime.GOMAXPROCS](https://pkg.go.dev/runtime#GOMAXPROCS)
- [Go Source: runtime/proc.go](https://go.dev/src/runtime/proc.go)

</div>
</details>

## 16. 为什么 GMP 模型中要有 P

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** P 的作用是把 OS 线程 M 和调度资源解耦。早期只靠 G 和 M 时，所有线程争全局队列和全局资源，调度、内存分配、系统调用恢复都会更容易产生竞争；引入 P 之后，每个 P 持有本地 run queue、mcache 等资源，M 绑定 P 后就能高效执行 Go 代码。`GOMAXPROCS` 控制 P 的数量，也就控制同一时刻最多有多少个 M 并行执行用户 Go 代码。

**要答的点：**
- 控制并行度：P 的数量决定同时执行 Go 用户代码的并行度上限。
- 本地队列：每个 P 有本地 run queue，减少所有 goroutine 都抢全局队列。
- 资源归属：P 持有执行 Go 代码需要的运行时资源，例如调度状态和分配缓存。
- 系统调用处理：M 进入阻塞 syscall 时可以释放 P，让其他 M 接管 P 继续跑 G。
- 可扩展性：P 让调度器更容易做 work stealing、局部缓存和负载均衡。

**重点讲解摘录：**
- Go runtime HACKING 文档说 P 代表执行用户 Go 代码所需的资源，也像 CPU。
- 该文档说 scheduler 的工作是匹配 G、M、P，其中 P 是执行代码的 rights and resources。
- `runtime.GOMAXPROCS` 文档说它设置能同时执行用户级 Go 代码的最大 CPU 数，这与 P 数量直接相关。
- Go 调度器设计讨论提出每个 P 关联一个 “per-P runqueue”，并且每个 P 也关联 mcache，减少全局竞争。
- `runtime/proc.go` 源码里 `runqput`、`runqget`、`runqsteal` 都围绕 P 的本地队列工作，说明 P 是调度局部性的核心。

**原文链接：**
- [Go Source: runtime/HACKING.md](https://go.dev/src/runtime/HACKING.md)
- [Go Packages: runtime.GOMAXPROCS](https://pkg.go.dev/runtime#GOMAXPROCS)
- [Go Dev Discussion: Scalable Go Scheduler Design](https://groups.google.com/g/golang-dev/c/_H9nXe7jG2U)
- [Go Source: runtime/proc.go](https://go.dev/src/runtime/proc.go)

</div>
</details>

## 17. 如果 P 的本地队列的 G 用完会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** P 的本地队列空了，当前 M 会进入调度器的找活流程。它会先检查当前 P 的本地 run queue；本地队列为空时，再尝试从全局 run queue 批量拿一部分放回本地；还会检查 timer、netpoll、GC worker 等来源；全局来源也为空时，就会从其他 P 的本地队列偷一部分 G 过来，这叫 work stealing。所有来源为空时，M 会释放 P 或进入自旋/休眠，等待新的 goroutine 变为 runnable。

**要答的点：**
- 本地优先：先查当前 P 的本地队列和 `runnext`，命中成本最低。
- 全局队列：本地空时会从全局队列取一批 G，减少频繁抢全局锁。
- 其他来源：timer、网络轮询、GC worker 也可能产生可运行 G。
- 工作窃取：从其他非空 P 的本地队列偷一批 G，做负载均衡。
- 空闲处理：完全没活时，M 可能进入 spinning 状态、释放 P，或者休眠等待唤醒。

**重点讲解摘录：**
- `runtime/proc.go` 中 `findRunnable` 注释说它会从其他 P 窃取、从本地或全局队列拿 G，并轮询网络。
- 源码调度流程先执行 `runqget(pp)` 检查 local runq，之后再检查 global runq。
- global runq 分支会调用 `globrunqgetbatch`，把一批 G 放到当前 P 的本地队列里。
- `runqsteal` 的注释写明它会从另一个 P 的本地 runnable queue “Steal half of elements”，并放到当前 P 的本地队列。
- 源码里找不到任务后会 `releasep()` 和 `pidleput()`，说明 P 会进入空闲池等待后续工作。

**原文链接：**
- [Go Source: runtime/proc.go](https://go.dev/src/runtime/proc.go)
- [Go Source: runtime/HACKING.md](https://go.dev/src/runtime/HACKING.md)
- [Go Dev Discussion: Scalable Go Scheduler Design](https://groups.google.com/g/golang-dev/c/_H9nXe7jG2U)

</div>
</details>

## 18. 讲一下三色标记法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三色标记是 GC 在标记阶段用来描述对象扫描进度的抽象：白色表示还没确认可达，灰色表示已经发现但它引用的对象还没扫描完，黑色表示对象本身和它引用的对象都已经扫描过。标记从根对象开始，先把根能到达的对象变灰，再不断取灰色对象扫描它的指针，把新发现对象变灰，当前对象扫描完变黑。最后标记结束时仍是白色的对象就是不可达对象，后续 sweep 阶段会回收它们。

**要答的点：**
- 白色：当前 GC 周期里还没被证明可达，最终仍白就是垃圾。
- 灰色：已发现可达，但内部指针还没扫描完，是待处理队列。
- 黑色：已发现可达，并且内部指针扫描完成。
- 根对象：栈、全局变量、runtime 结构等作为扫描起点。
- 并发难点：应用线程和 GC 同时运行时，指针关系会变化，需要写屏障维护标记正确性。

**重点讲解摘录：**
- Go GC Guide 说 tracing GC 从 roots 出发沿指针传递地发现 live objects，这正是三色标记的基础。
- Go GC Guide 说 Go 的 GC 使用 mark-sweep，标记 live 对象，扫描完成后 sweep 未标记内存。
- `runtime/mgc.go` 说 Go GC 是 concurrent mark and sweep，并使用 write barrier。
- `runtime/mgc.go` 的标记阶段会启用 write barrier、入队 root mark jobs，并扫描栈、全局变量和 runtime 数据结构。
- `runtime/mgc.go` 说 GC 会 drain grey object work queue，扫描每个灰色对象，将它变黑，并把它指向的对象加入工作队列。
- `runtime/mbarrier.go` 说写屏障的 shade 操作用来防止 mutator 把对象从 GC 面前隐藏起来。

**原文链接：**
- [Go GC Guide](https://go.dev/doc/gc-guide)
- [Go Source: runtime/mgc.go](https://go.dev/src/runtime/mgc.go)
- [Go Source: runtime/mbarrier.go](https://go.dev/src/runtime/mbarrier.go)

</div>
</details>

## 19. 什么是混合写屏障

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 混合写屏障是 Go 并发 GC 在指针写入时插入的一段屏障逻辑，用来防止应用线程在 GC 标记期间把可达对象“藏起来”。它结合了 Yuasa 删除屏障和 Dijkstra 插入屏障：覆盖一个指针前，先把旧指针指向的对象标灰；如果当前 goroutine 的栈还是灰色，再把新写入指针指向的对象标灰；然后完成真正的指针写入。这样 GC 可以和用户程序并发运行，同时减少重新扫描栈带来的 STW 时间。

**要答的点：**
- 背景：并发标记期间，用户 goroutine 仍在修改对象引用关系。
- 删除屏障：覆盖旧指针前标记旧对象，防止唯一引用被移走后漏标。
- 插入屏障：写入新指针时标记新对象，防止白对象挂到黑对象下面。
- 混合策略：Go 根据栈是否仍为灰色决定是否需要 shade 新指针。
- 工程效果：维护 GC 正确性，降低 mark termination 阶段重新扫描栈和全局变量的成本。

**重点讲解摘录：**
- `runtime/mbarrier.go` 明确说 Go 使用 “hybrid barrier”，结合 Yuasa-style deletion barrier 和 Dijkstra insertion barrier。
- 源码伪代码是：`shade(*slot)`，当前栈为灰色时 `shade(ptr)`，最后 `*slot = ptr`。
- 源码注释说 `shade(*slot)` 防止 mutator 通过把唯一指针从 heap 移到 stack 来隐藏对象。
- 源码注释说 `shade(ptr)` 防止 mutator 把 stack 上的唯一指针写入黑色 heap 对象来隐藏对象。
- 源码注释说全局写入也需要 write barrier，这样 mark termination 时可以减少重新扫描 global 带来的 pause time。
- `runtime/mgc.go` 说 Go GC 是 concurrent mark and sweep，并在 mark 阶段启用 write barrier。

**原文链接：**
- [Go Source: runtime/mbarrier.go](https://go.dev/src/runtime/mbarrier.go)
- [Go Source: runtime/mgc.go](https://go.dev/src/runtime/mgc.go)
- [Go Proposal: Eliminate STW stack re-scanning](https://github.com/golang/proposal/blob/master/design/17503-eliminate-rescan.md)

</div>
</details>

## 20. 讲一下闭包

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 闭包就是函数值和它引用的外部变量环境组合在一起。Go 里的函数字面量可以引用外层函数中的变量，这些变量会和函数值一起存活，即使外层函数已经返回，闭包仍然能继续访问和修改它们。它常用于回调、工厂函数、封装状态、延迟执行和 goroutine 任务；被闭包捕获的变量可能发生逃逸，生命周期会延长。

**要答的点：**
- 本质：函数值 + 捕获的外部变量。
- 捕获语义：闭包引用外层变量，变量可继续被读写。
- 生命周期：被闭包引用的变量会继续存活，必要时逃逸到堆。
- 常见用途：返回函数、回调、状态封装、`defer`、goroutine。
- 循环变量：Go 1.22 起 `for` 循环变量每次迭代有自己的变量；旧版本里闭包捕获循环变量容易拿到最终值，需要显式拷贝。

**重点讲解摘录：**
- Go Spec 说函数字面量是 closures，可以引用周围函数中定义的变量。
- Go Spec 说这些被引用的变量在周围函数和函数字面量之间共享，并且只要还能被访问就会存活。
- Go FAQ 的 closure 示例说明闭包会共享它捕获的变量，因此多个返回函数可以共同更新同一个状态。
- Go Blog loopvar-preview 说明 Go 1.22 改为每次迭代创建独立循环变量，解决常见的闭包捕获循环变量问题。
- Go FAQ 也说明旧版本里闭包引用循环迭代变量时，所有闭包可能共享同一个变量，需要创建新变量或传参。

**原文链接：**
- [Go Spec: Function literals](https://go.dev/ref/spec#Function_literals)
- [Go FAQ: What happens with closures running as goroutines?](https://go.dev/doc/faq#closures_and_goroutines)
- [Go Blog: Fixing For Loops in Go 1.22](https://go.dev/blog/loopvar-preview)

</div>
</details>

## 21. panic、recover、defer

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `defer` 用来注册函数返回前要执行的清理逻辑；`panic` 会让当前函数停止正常执行，并沿调用栈向上展开；展开过程中每一层已经注册的 `defer` 都会执行；`recover` 只能在延迟函数里直接调用，用来捕获正在传播的 panic，让程序恢复正常控制流。工程里普通业务错误优先返回 `error`，`panic/recover` 更适合兜底保护、框架边界和真正异常的不可继续状态。

**要答的点：**
- `defer`：登记延迟调用，按后进先出执行，常用于释放资源、解锁、关闭文件。
- `panic`：触发运行时恐慌，当前函数停止正常流程，并开始执行 defer 链。
- 栈展开：当前函数 defer 执行完后，panic 继续传给调用方，调用方 defer 继续执行。
- `recover`：在同一 goroutine 的 deferred function 中直接调用才会停止 panic。
- 使用原则：业务可预期失败返回 `error`；`recover` 常放在 goroutine 边界、HTTP/RPC middleware 中兜底。

**重点讲解摘录：**
- Go Blog 说 defer 通常用于释放资源，panic 会停止当前函数正常执行，并开始执行 deferred functions。
- Go Blog 说 panic 执行完当前 goroutine 的所有 deferred calls 后，程序会崩溃并打印日志，除非被 recover。
- Go Blog 总结 recover 是内置函数，用来重新获得 panicking goroutine 的控制权。
- Go Spec 说当 panic 发生时，当前函数的 deferred functions 会照常执行，然后返回调用方继续 panic。
- Go Spec 说 recover 只有在 deferred function 中直接调用，并且当前 goroutine 正在 panicking 时，才会停止 panicking 序列。

**原文链接：**
- [Go Blog: Defer, Panic, and Recover](https://go.dev/blog/defer-panic-and-recover)
- [Go Spec: Handling panics](https://go.dev/ref/spec#Handling_panics)
- [Effective Go: Recover](https://go.dev/doc/effective_go#recover)

</div>
</details>

## 22. 多线程交替打印 abc

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这类题核心是把“轮到谁打印”变成同步信号。Go 里可以用 3 个 channel 组成环：`a` 收到信号打印 `a`，然后通知 `b`；`b` 打印后通知 `c`；`c` 打印后通知 `a`。主 goroutine 先给 `a` 一个初始信号，最后用 `WaitGroup` 等待三个 goroutine 退出。

**要答的点：**
- 顺序控制：用 channel 传递令牌，令牌在哪个 channel，哪个 goroutine 打印。
- 循环次数：每个 goroutine 打印固定次数，例如 10 轮。
- 启动信号：主 goroutine 给 `chA` 发送第一个令牌。
- 退出控制：打印次数固定后自然退出，用 `WaitGroup` 等待。
- 工程细节：buffered channel 容量设 1 可以让最后一次通知完成入队，收尾更稳。

**重点讲解摘录：**
- Go Spec 说无缓冲 channel 只有发送和接收双方都 ready 时通信才成功，这可以用来做严格同步。
- Go Spec 说有缓冲 channel 在缓冲未满时发送可以继续、缓冲非空时接收可以继续，容量为 1 适合传令牌。
- Effective Go 说 channel 可以作为信号量使用，通过发送值控制并发执行。
- `sync.WaitGroup` 文档说它会等待一组 goroutine 完成，适合这类启动多个 worker 后统一收口的题。

**参考代码：**

```go
func printABC(n int) {
	chA := make(chan struct{}, 1)
	chB := make(chan struct{}, 1)
	chC := make(chan struct{}, 1)

	var wg sync.WaitGroup
	wg.Add(3)

	go func() {
		defer wg.Done()
		for i := 0; i < n; i++ {
			<-chA
			fmt.Print("a")
			chB <- struct{}{}
		}
	}()

	go func() {
		defer wg.Done()
		for i := 0; i < n; i++ {
			<-chB
			fmt.Print("b")
			chC <- struct{}{}
		}
	}()

	go func() {
		defer wg.Done()
		for i := 0; i < n; i++ {
			<-chC
			fmt.Print("c")
			if i+1 < n {
				chA <- struct{}{}
			}
		}
	}()

	chA <- struct{}{}
	wg.Wait()
}
```

**原文链接：**
- [Go Spec: Channel types](https://go.dev/ref/spec#Channel_types)
- [Effective Go: Channels](https://go.dev/doc/effective_go#channels)
- [Go Packages: sync.WaitGroup](https://pkg.go.dev/sync#WaitGroup)

</div>
</details>

## 23. 多线程打印 1 到 10

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这题先问清楚是否要求有序。如果只要求多个 goroutine 共同打印 1 到 10，可以用“任务 channel + worker + WaitGroup”：主 goroutine 把 1..10 作为任务发送到 channel，多个 worker 从 channel 取数打印，关闭 channel 后 worker 自然退出。如果要求严格按 1、2、3 顺序输出，就用一个 goroutine 负责递增发送，打印也在接收侧按任务顺序消费，或者用锁/条件变量控制 turn。

**要答的点：**
- 任务来源：由一个 goroutine 生成 1..10，集中控制边界和去重。
- 分发方式：用 channel 传任务，多个 worker 竞争消费。
- 退出方式：生产完关闭 channel，worker 用 `range` 读到关闭后退出。
- 同步收口：用 `WaitGroup` 等待所有 worker 完成。
- 顺序要求：多 worker 打印顺序受调度影响；严格顺序要把打印串行化或增加 turn 控制。

**重点讲解摘录：**
- Go Blog pipelines 文章说发送方可以在发送完成后关闭 channel，接收方可以用 `range` 直到 channel 关闭。
- `sync.WaitGroup` 文档说 WaitGroup 会等待一组 goroutine 完成，主 goroutine 用 `Wait` 阻塞到计数归零。
- Go Spec 说 channel 提供并发函数之间发送和接收指定类型值的机制，适合这类任务分发。
- Go 内存模型说明 channel send 和对应 receive 之间存在同步关系，任务值通过 channel 传递后接收方能安全看到。

**参考代码：**

```go
func print1To10(workerN int) {
	jobs := make(chan int)

	var wg sync.WaitGroup
	wg.Add(workerN)
	for i := 0; i < workerN; i++ {
		go func(id int) {
			defer wg.Done()
			for n := range jobs {
				fmt.Printf("worker=%d n=%d\n", id, n)
			}
		}(i)
	}

	for n := 1; n <= 10; n++ {
		jobs <- n
	}
	close(jobs)
	wg.Wait()
}
```

**原文链接：**
- [Go Blog: Pipelines and cancellation](https://go.dev/blog/pipelines)
- [Go Packages: sync.WaitGroup](https://pkg.go.dev/sync#WaitGroup)
- [Go Spec: Channel types](https://go.dev/ref/spec#Channel_types)
- [The Go Memory Model](https://go.dev/ref/mem)
</div>
</details>
