# Go

这里整理 Go 面试中高频出现的语言、并发、运行时和工程相关问题，适合作为专题复习提纲。

## 1. 为什么选 Go 语言

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Go 在后端场景里平衡了开发效率、并发能力和部署成本，尤其适合云原生与高并发服务。面试里可按三点展开：编译快、语法简洁、工程规范统一（`go fmt`、`go mod`）；原生并发模型（goroutine + channel）开发成本低；单二进制部署方便，运行时开销相对可控。


**关键点：**
- 编译快、语法简洁、工程规范统一（`go fmt`、`go mod`）。
- 原生并发模型（goroutine + channel）开发成本低。
- 单二进制部署方便，运行时开销相对可控。

</div>
</details>

## 2. 讲一下协程、线程、进程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 进程是资源隔离单位，线程是 CPU 调度单位，协程是用户态调度的轻量执行单元。面试里可按三点展开：隔离性：进程最强，线程共享进程资源，协程共享线程；切换成本：进程 > 线程 > 协程；Go 的协程（goroutine）由运行时调度，不直接等于内核线程。


**关键点：**
- 隔离性：进程最强，线程共享进程资源，协程共享线程。
- 切换成本：进程 > 线程 > 协程。
- Go 的协程（goroutine）由运行时调度，不直接等于内核线程。

</div>
</details>

## 3. defer 执行顺序

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `defer` 按“后进先出（LIFO）”执行，且参数在 `defer` 声明时就完成求值。面试里可按三点展开：多个 `defer` 逆序执行；返回值先赋值，再执行 `defer`，最后真正返回；命名返回值可被 `defer` 修改。


**关键点：**
- 多个 `defer` 逆序执行。
- 返回值先赋值，再执行 `defer`，最后真正返回。
- 命名返回值可被 `defer` 修改。

</div>
</details>

## 4. slice 扩容机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `slice` 追加元素超出容量时会触发扩容并拷贝，容量通常按倍数增长后再逐步平滑增长。面试里可按三点展开：扩容会分配新底层数组并 `copy` 原数据；小容量常见近似 2 倍增长，大容量增长倍率下降（避免内存浪费）；扩容后旧切片和新切片可能不再共享底层数组。


**关键点：**
- 扩容会分配新底层数组并 `copy` 原数据。
- 小容量常见近似 2 倍增长，大容量增长倍率下降（避免内存浪费）。
- 扩容后旧切片和新切片可能不再共享底层数组。

</div>
</details>

## 5. map 底层设计（map 是否并发安全）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Go `map` 基于哈希桶实现，默认并发不安全；并发读写会触发运行时错误。面试里可按三点展开：底层结构核心是 `bucket` + 溢出桶；读写并发未加保护时可能 panic（`concurrent map read and map write`）；并发场景用 `sync.RWMutex` 或 `sync.Map`。


**关键点：**
- 底层结构核心是 `bucket` + 溢出桶。
- 读写并发未加保护时可能 panic（`concurrent map read and map write`）。
- 并发场景用 `sync.RWMutex` 或 `sync.Map`。

</div>
</details>

## 6. map 扩容机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `map` 在装载因子或溢出桶过多时会触发渐进式扩容，迁移不是一次性完成。面试里可按三点展开：扩容类型：等量扩容（整理）和翻倍扩容（容量不足）；渐进迁移：后续读写时顺带搬迁旧桶，减少一次性抖动；扩容期间会同时存在新旧桶引用状态。


**关键点：**
- 扩容类型：等量扩容（整理）和翻倍扩容（容量不足）。
- 渐进迁移：后续读写时顺带搬迁旧桶，减少一次性抖动。
- 扩容期间会同时存在新旧桶引用状态。

</div>
</details>

## 7. CSP 是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** CSP（Communicating Sequential Processes）强调“通过通信共享内存”，用消息传递降低共享状态竞争。面试里可按三点展开：goroutine 负责执行，channel 负责通信；目标是减少锁竞争和共享可变状态；在 Go 中是并发设计思想，不是“完全不用锁”。


**关键点：**
- goroutine 负责执行，channel 负责通信。
- 目标是减少锁竞争和共享可变状态。
- 在 Go 中是并发设计思想，不是“完全不用锁”。

</div>
</details>

## 8. 讲一下 Go 中的 Channel

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `channel` 是 goroutine 间的类型安全通信管道，支持同步与缓冲两种模式。面试里可按三点展开：无缓冲：发送和接收必须同步配对；有缓冲：缓冲未满可直接发送，未空可直接接收；常与 `select`、`context` 组合做并发控制与退出。


**关键点：**
- 无缓冲：发送和接收必须同步配对。
- 有缓冲：缓冲未满可直接发送，未空可直接接收。
- 常与 `select`、`context` 组合做并发控制与退出。

</div>
</details>

## 9. 是否可以读写已关闭的 Channel

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 关闭后的 channel 可以读、不能写；向已关闭 channel 写会 panic。面试里可按三点展开：读关闭 channel：先读完缓冲，之后返回零值且 `ok=false`；写关闭 channel：立即 panic；重复关闭同一个 channel 也会 panic。


**关键点：**
- 读关闭 channel：先读完缓冲，之后返回零值且 `ok=false`。
- 写关闭 channel：立即 panic。
- 重复关闭同一个 channel 也会 panic。

</div>
</details>

## 10. select 和 switch 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `switch` 做表达式分支，`select` 做 channel I/O 多路选择。面试里可按三点展开：`select` 只用于 `channel` 的发送/接收分支；`switch` 是普通控制流，与并发通信无关；`select` 可配 `default` 做非阻塞操作。


**关键点：**
- `select` 只用于 `channel` 的发送/接收分支。
- `switch` 是普通控制流，与并发通信无关。
- `select` 可配 `default` 做非阻塞操作。

</div>
</details>

## 11. 原子操作和锁的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 原子操作适合简单共享变量读改写，锁适合保护一段临界区和复合状态。面试里可按三点展开：原子操作开销小，但表达能力有限；锁可保护多变量一致性与复杂业务逻辑；选型看“临界区复杂度”，不是只看性能。


**关键点：**
- 原子操作开销小，但表达能力有限。
- 锁可保护多变量一致性与复杂业务逻辑。
- 选型看“临界区复杂度”，不是只看性能。

</div>
</details>

## 12. 什么是自旋锁与互斥锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 自旋锁拿不到锁时忙等，互斥锁拿不到锁时挂起等待。面试里可按三点展开：自旋适合临界区非常短、竞争轻的场景；互斥锁适合临界区较长，避免 CPU 空转；Go 用户层主要直接用 `sync.Mutex`，底层会结合自旋策略优化。


**关键点：**
- 自旋适合临界区非常短、竞争轻的场景。
- 互斥锁适合临界区较长，避免 CPU 空转。
- Go 用户层主要直接用 `sync.Mutex`，底层会结合自旋策略优化。

</div>
</details>

## 13. sync.Map 和普通 map 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `sync.Map` 是并发安全容器，普通 `map` 需自行加锁。面试里可按三点展开：`sync.Map` 适合读多写少、key 稳定场景；普通 `map + RWMutex` 在写多或需要强类型时更常用；`sync.Map` API 是 `any`，类型断言成本与可读性要考虑。


**关键点：**
- `sync.Map` 适合读多写少、key 稳定场景。
- 普通 `map + RWMutex` 在写多或需要强类型时更常用。
- `sync.Map` API 是 `any`，类型断言成本与可读性要考虑。

</div>
</details>

## 14. 讲一下 Context 以及使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `context` 用于在调用链传递取消信号、超时截止时间和请求级元数据。面试里可按三点展开：常见用途：超时控制、级联取消、链路追踪；作为函数首参传递，不建议存进结构体；`context.WithCancel/WithTimeout/WithDeadline` 是高频 API。


**关键点：**
- 常见用途：超时控制、级联取消、链路追踪。
- 作为函数首参传递，不建议存进结构体。
- `context.WithCancel/WithTimeout/WithDeadline` 是高频 API。

</div>
</details>

## 15. 讲一下 GMP 模型，各个字母代表什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** GMP 是 Go 调度模型：G（goroutine）、M（machine，内核线程）、P（processor，调度上下文）。面试里可按三点展开：G 是待执行任务；M 是真正执行代码的线程；P 持有本地队列和运行时资源，M 必须绑定 P 才能跑 G。


**关键点：**
- G 是待执行任务。
- M 是真正执行代码的线程。
- P 持有本地队列和运行时资源，M 必须绑定 P 才能跑 G。

</div>
</details>

## 16. 为什么 GMP 模型中要有 P

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** P 把“执行线程”和“调度资源”解耦，提升调度效率并控制并行度。面试里可按三点展开：`GOMAXPROCS` 本质控制 P 数量；每个 P 有本地队列，减少全局锁竞争；没有 P 会导致调度状态难管理、可扩展性差。


**关键点：**
- `GOMAXPROCS` 本质控制 P 数量。
- 每个 P 有本地队列，减少全局锁竞争。
- 没有 P 会导致调度状态难管理、可扩展性差。

</div>
</details>

## 17. 如果 P 的本地队列的 G 用完会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 调度器会尝试从全局队列获取任务，或从其他 P “偷”一半任务（work stealing）。面试里可按三点展开：本地队列优先，减少竞争；本地空时先看全局队列，再偷取其他 P；仍无任务时 M 可能休眠等待。


**关键点：**
- 本地队列优先，减少竞争。
- 本地空时先看全局队列，再偷取其他 P。
- 仍无任务时 M 可能休眠等待。

</div>
</details>

## 18. 讲一下三色标记法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三色标记是并发 GC 的可达性算法：白色（未访问）、灰色（已访问待扫描）、黑色（已访问已扫描）。面试里可按三点展开：从根对象出发逐步把可达对象染黑；最终剩余白色对象判定为垃圾；关键在并发标记期间保证“黑不指白”不被破坏。


**关键点：**
- 从根对象出发逐步把可达对象染黑。
- 最终剩余白色对象判定为垃圾。
- 关键在并发标记期间保证“黑不指白”不被破坏。

</div>
</details>

## 19. 什么是混合写屏障

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 混合写屏障是 Go 为并发 GC 设计的屏障策略，结合插入/删除屏障保证对象可达性正确。面试里可按三点展开：目标是防止并发标记漏标；降低 STW 时间并保证正确回收；本质是写指针时通知 GC 维护三色不变式。


**关键点：**
- 目标是防止并发标记漏标。
- 降低 STW 时间并保证正确回收。
- 本质是写指针时通知 GC 维护三色不变式。

</div>
</details>

## 20. 讲一下闭包

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 闭包是“函数 + 其捕获的外部变量环境”，可让函数返回后仍访问外部变量。面试里可按三点展开：捕获的是变量本身，不是值拷贝（需注意循环变量坑）；被闭包引用的变量可能逃逸到堆；常用于工厂函数、回调和状态封装。


**关键点：**
- 捕获的是变量本身，不是值拷贝（需注意循环变量坑）。
- 被闭包引用的变量可能逃逸到堆。
- 常用于工厂函数、回调和状态封装。

</div>
</details>

## 21. panic、recover、defer

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `panic` 用于不可恢复错误，`defer` 做延迟清理，`recover` 只能在 `defer` 中拦截 panic。面试里可按三点展开：`panic` 会沿调用栈展开执行 `defer`；`recover` 仅在同 goroutine 的 `defer` 中生效；常用于兜底保护，业务错误优先返回 `error`。


**关键点：**
- `panic` 会沿调用栈展开执行 `defer`。
- `recover` 仅在同 goroutine 的 `defer` 中生效。
- 常用于兜底保护，业务错误优先返回 `error`。

</div>
</details>

## 22. 多线程交替打印 abc

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见做法是 3 个 goroutine 配合 3 个 channel 形成环，按信号顺序打印。面试里可按三点展开：A 打印后通知 B，B 通知 C，C 再通知 A；用计数控制总打印次数，避免死循环；结束时要关闭或广播退出，避免 goroutine 泄漏。


**关键点：**
- A 打印后通知 B，B 通知 C，C 再通知 A。
- 用计数控制总打印次数，避免死循环。
- 结束时要关闭或广播退出，避免 goroutine 泄漏。

</div>
</details>

## 23. 多线程打印 1 到 10

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 可以用“任务分发 + 同步等待”模型：一个 goroutine 递增计数，多个 goroutine 抢占打印。面试里可按三点展开：对共享计数使用原子操作或互斥锁；用 `WaitGroup` 等待所有 goroutine 退出；要保证边界条件（打印到 10 即停止）不会重复打印。


**关键点：**
- 对共享计数使用原子操作或互斥锁。
- 用 `WaitGroup` 等待所有 goroutine 退出。
- 要保证边界条件（打印到 10 即停止）不会重复打印。
</div>
</details>
