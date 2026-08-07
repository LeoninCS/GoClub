---
title: "01佬腾讯IDC后端"
slug: "01-tencent-idc-backend"
aliases:
  - "/docs/interview/dachang/01佬腾讯IDC后端/"
  - "/s/cp5s/"
shortlink: "cp5s"
---

# 01佬腾讯 IDC 后端

方向：后端开发

附注：技术问题如下，生活问题较多，此处省略。

## 项目

1. 在 Redis 里面有没有应用过分布式锁？怎么使用 Redis 实现分布式锁？
2. 在项目中，有没有遇到 goroutine 泄漏、内存泄漏增长的情况？

## 八股

1. Redis 里面有哪些数据类型，分别适合什么场景？
2. 数据库事务四大特性。
3. Channel 无缓存和有缓存有什么区别？分别在什么情况下使用？
4. GMP 模型。

## 算法

1. 合并两个有序数组。
2. 滑动窗口最大值。

## 参考答案（AI 生成）

> 以下答案由 AI 生成，仅供面试复盘参考。

### 1. 怎么使用 Redis 实现分布式锁？

答：加锁用 `SET lock_key token NX PX expire_ms`，保证只有 key 不存在时写入，并设置过期时间防止死锁。解锁用 Lua 脚本先比较 token 是否一致，再删除 key，保证只释放自己持有的锁。生产环境还要考虑锁过期时间、业务超时、重试退避、续期和可重入需求。

### 2. 项目里遇到 goroutine 泄漏、内存泄漏怎么排查？

答：先看监控里的 goroutine 数、heap、RSS 和 GC 频率是否持续增长，再用 pprof 分析 `goroutine`、`heap`、`allocs`。goroutine 泄漏常见于 channel 阻塞、context 未传递、后台循环无退出条件、网络请求无超时；内存增长常见于 slice 引用大数组、map/cache 无淘汰、定时器未释放、连接或文件句柄未关闭。

### 3. Redis 有哪些数据类型，分别适合什么场景？

答：String 适合缓存对象、计数器、分布式锁；Hash 适合存储对象字段；List 适合简单队列和时间线；Set 适合去重、标签、共同关注；ZSet 适合排行榜、延时队列、按分数排序的范围查询。还可以补充 Bitmap、HyperLogLog、Stream 等扩展结构。

### 4. 数据库事务四大特性

答：ACID 分别是原子性、一致性、隔离性、持久性。原子性保证事务内操作整体提交或回滚；一致性保证事务前后数据满足约束；隔离性保证并发事务之间按隔离级别相互影响；持久性保证事务提交后数据落盘并可恢复。

### 5. Channel 无缓存和有缓存有什么区别？

答：无缓存 channel 发送和接收必须同步配对，适合任务交接、同步信号、强背压场景。有缓存 channel 带队列能力，发送方可以先写入缓冲区，适合生产消费解耦、削峰、限流和 worker pool。

### 6. GMP 模型

答：G 是 goroutine，M 是操作系统线程，P 是调度器处理器。M 必须持有 P 才能执行 G，P 维护本地运行队列，也会从全局队列或其他 P 偷取任务。网络 I/O 会结合 netpoller 唤醒可运行 goroutine，系统调用阻塞时 P 会转交给其他 M，提高调度效率。

### 7. 合并两个有序数组

答：如果要求合并到第一个数组并且空间在尾部预留，推荐从后往前双指针。设 `i=m-1`、`j=n-1`、`k=m+n-1`，每次把较大的元素放到 `nums1[k]`，避免从前合并时覆盖有效元素。

```go
func merge(nums1 []int, m int, nums2 []int, n int) {
    i, j, k := m-1, n-1, m+n-1
    for j >= 0 {
        if i >= 0 && nums1[i] > nums2[j] {
            nums1[k] = nums1[i]
            i--
        } else {
            nums1[k] = nums2[j]
            j--
        }
        k--
    }
}
```

### 8. 滑动窗口最大值

答：推荐用单调队列，队列里保存下标，并保证对应值单调递减。新元素进来时，把队尾所有小于等于它的元素弹出；窗口左边界右移时，把过期下标从队头弹出；队头始终是当前窗口最大值。

```go
func maxSlidingWindow(nums []int, k int) []int {
    q := make([]int, 0)
    ans := make([]int, 0, len(nums)-k+1)

    for i, x := range nums {
        for len(q) > 0 && nums[q[len(q)-1]] <= x {
            q = q[:len(q)-1]
        }
        q = append(q, i)

        if q[0] <= i-k {
            q = q[1:]
        }
        if i >= k-1 {
            ans = append(ans, nums[q[0]])
        }
    }
    return ans
}
```
