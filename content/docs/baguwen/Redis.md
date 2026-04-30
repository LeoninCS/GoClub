# Redis

这里主要覆盖 Redis 的数据结构、持久化、高可用、热点问题和面试中的常见追问。

## 基础

### Redis 和 MySQL 区别，为什么 Redis 更快

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 是内存数据库，主打低延迟读写；MySQL 是磁盘型关系数据库，主打事务一致性与复杂查询。面试里可按三点展开：Redis 多在内存操作，避免大量磁盘随机 I/O；数据结构丰富，很多操作是 O(1)/O(logN)；Redis 通常单线程事件模型，减少上下文切换与锁开销。


**关键点：**
- Redis 多在内存操作，避免大量磁盘随机 I/O。
- 数据结构丰富，很多操作是 O(1)/O(logN)。
- Redis 通常单线程事件模型，减少上下文切换与锁开销。

</div>
</details>

### Redis 的应用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 典型场景是缓存、分布式锁、计数器、排行榜、会话、延迟队列。面试里可按两点展开：用于热点数据加速和削峰；常与数据库组合，不替代核心持久存储。


**关键点：**
- 用于热点数据加速和削峰。
- 常与数据库组合，不替代核心持久存储。

</div>
</details>

## 数据结构

### Redis 有哪些数据类型，各自场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见有 String、Hash、List、Set、ZSet、Bitmap、HyperLogLog、Stream。面试里可按三点展开：String：缓存、计数；Hash：对象字段存储；ZSet：排行榜、延迟队列。


**关键点：**
- String：缓存、计数。
- Hash：对象字段存储。
- ZSet：排行榜、延迟队列。
- Stream：消息流。

</div>
</details>

### 各类型底层结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 不同类型底层会用哈希表、压缩列表/列表结构、跳表、基数树等实现。面试里可按两点展开：ZSet 常见是“跳表 + 字典”；Hash/List/Set 会随数据规模在编码间切换。


**关键点：**
- ZSet 常见是“跳表 + 字典”。
- Hash/List/Set 会随数据规模在编码间切换。

</div>
</details>

### SDS 和 C 字符串区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** SDS（简单动态字符串）记录长度并预留空间，避免频繁 `strlen` 和缓冲区溢出。面试里可按三点展开：O(1) 获取长度；二进制安全；惰性释放和预分配减少扩容次数。


**关键点：**
- O(1) 获取长度。
- 二进制安全。
- 惰性释放和预分配减少扩容次数。

</div>
</details>

### 哈希冲突怎么解决

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 哈希表采用链式（拉链法）解决冲突，并通过渐进式 rehash 控制扩容成本。面试里可按两点展开：桶内链表处理冲突；渐进 rehash 避免一次性阻塞。


**关键点：**
- 桶内链表处理冲突。
- 渐进 rehash 避免一次性阻塞。

</div>
</details>

### 讲一下跳表

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 跳表是多层有序链表，查询/插入/删除平均 O(logN)，实现相对平衡树更简单。面试里可按两点展开：通过多层索引快速定位；Redis 的 ZSet 用跳表支持范围查询与排序。


**关键点：**
- 通过多层索引快速定位。
- Redis 的 ZSet 用跳表支持范围查询与排序。

</div>
</details>

## 持久化

### Redis 宕机如何处理

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 依赖 RDB/AOF 持久化恢复，并结合主从+哨兵/集群做高可用切换。面试里可按两点展开：宕机恢复看最后落盘点；高可用用于缩短不可用时间。


**关键点：**
- 宕机恢复看最后落盘点。
- 高可用用于缩短不可用时间。

</div>
</details>

### AOF 和 RDB 对比

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RDB 恢复快、文件紧凑但可能丢最近数据；AOF 数据更完整但体积更大、恢复更慢。面试里可按两点展开：RDB 适合备份与全量恢复；AOF 适合更高数据安全要求。


**关键点：**
- RDB 适合备份与全量恢复。
- AOF 适合更高数据安全要求。

</div>
</details>

### 混合持久化

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先以 RDB 快照作为基线，再追加 AOF 增量，兼顾恢复速度和数据完整性。面试里可按两点展开：重启先载入 RDB，再重放增量命令；常用于平衡性能与可靠性。


**关键点：**
- 重启先载入 RDB，再重放增量命令。
- 常用于平衡性能与可靠性。

</div>
</details>

### 执行快照时数据能修改吗

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 能。Redis 通过 fork 子进程做快照，父进程继续处理请求，依赖写时复制（COW）。面试里重点展开：高写入时 COW 会带来额外内存压力。


**关键点：**
- 高写入时 COW 会带来额外内存压力。

</div>
</details>

### 大 key 对持久化影响

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 大 key 会导致 fork 后 COW 放大、阻塞风险增大，AOF 重写和网络传输成本也更高。面试里可按两点展开：影响备份、迁移、主从同步；建议拆分大 key。


**关键点：**
- 影响备份、迁移、主从同步。
- 建议拆分大 key。

</div>
</details>

## 功能

### 过期删除和内存淘汰区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 过期删除针对“已过期 key”，内存淘汰针对“内存不足时选 key 淘汰”。面试里可按两点展开：触发条件不同；两者可以同时存在。


**关键点：**
- 触发条件不同。
- 两者可以同时存在。

</div>
</details>

### 过期删除策略

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 采用“惰性删除 + 定期删除”组合。面试里可按两点展开：惰性：访问到才删；定期：周期抽样扫描删除。


**关键点：**
- 惰性：访问到才删。
- 定期：周期抽样扫描删除。

</div>
</details>

### 内存淘汰策略（缓存满了怎么办）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 根据配置策略淘汰，如 `allkeys-lru`、`volatile-lru`、`allkeys-lfu`、`noeviction` 等。面试里可按两点展开：业务缓存常用 `allkeys-lru/lfu`；要结合访问模式选策略。


**关键点：**
- 业务缓存常用 `allkeys-lru/lfu`。
- 要结合访问模式选策略。

</div>
</details>

### LRU 和 LFU

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** LRU 看“最近是否访问”，LFU 看“访问频率”。面试里可按两点展开：LRU 适合热点变化快；LFU 适合长期稳定热点。


**关键点：**
- LRU 适合热点变化快。
- LFU 适合长期稳定热点。

</div>
</details>

## 高可用

### 单个 Redis 压力过大怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 可做读写分离、分片集群、热点 key 拆分和本地缓存分层。面试里可按两点展开：先定位瓶颈是 CPU、内存还是网络；分片是横向扩展核心手段。


**关键点：**
- 先定位瓶颈是 CPU、内存还是网络。
- 分片是横向扩展核心手段。

</div>
</details>

### 如何保证集群数据一致性

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 主要是最终一致性，依赖复制、故障转移和业务补偿来控制不一致窗口。面试里可按两点展开：强一致不是 Redis 默认目标；关键数据需业务侧幂等与重试兜底。


**关键点：**
- 强一致不是 Redis 默认目标。
- 关键数据需业务侧幂等与重试兜底。

</div>
</details>

### 主从复制如何实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 全量同步 + 增量复制。首次同步传 RDB，后续通过复制偏移量传播命令。面试里可按两点展开：复制积压缓冲区支撑断线续传；网络抖动可能触发重新全量同步。


**关键点：**
- 复制积压缓冲区支撑断线续传。
- 网络抖动可能触发重新全量同步。

</div>
</details>

### 如何应对主从不一致

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 通过哨兵故障切换、合理 `repl` 参数、业务重试与校验任务控制影响。面试里可按两点展开：可监控复制延迟；对关键写可增加确认机制。


**关键点：**
- 可监控复制延迟。
- 对关键写可增加确认机制。

</div>
</details>

### 什么是哨兵，为什么要有

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 哨兵是 Redis 高可用组件，负责监控、告警和主从自动故障转移。面试里可按两点展开：解决单点主库故障恢复问题；不负责数据分片。


**关键点：**
- 解决单点主库故障恢复问题。
- 不负责数据分片。

</div>
</details>

### 讲一下哨兵机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 哨兵定期探测实例，主观下线后通过多数派判定客观下线并发起主从切换。面试里可按两点展开：多哨兵投票避免误判；切换后通知客户端新主节点地址。


**关键点：**
- 多哨兵投票避免误判。
- 切换后通知客户端新主节点地址。

</div>
</details>

### Redis Cluster 是什么，解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Cluster 是官方分片方案，通过 hash slot 把数据分布到多节点，解决容量和吞吐扩展问题。面试里可按两点展开：16384 槽位机制；同时提供分片与一定高可用能力。


**关键点：**
- 16384 槽位机制。
- 同时提供分片与一定高可用能力。

</div>
</details>

### Cluster 下客户端如何找节点

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 客户端根据 key 算 slot，若节点不匹配会收到 `MOVED/ASK` 重定向并更新路由。面试里可按两点展开：智能客户端需维护 slot 映射表；迁移期间可能出现 `ASK` 临时重定向。


**关键点：**
- 智能客户端需维护 slot 映射表。
- 迁移期间可能出现 `ASK` 临时重定向。

</div>
</details>

### 集群节点故障怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 由集群内主从和投票机制完成故障转移，客户端重定向到新主继续服务。面试里可按两点展开：要求从节点和多数主节点可用；故障期间可能有短暂不可用窗口。


**关键点：**
- 要求从节点和多数主节点可用。
- 故障期间可能有短暂不可用窗口。

</div>
</details>

## 缓存

### Redis 缓存穿透、击穿、雪崩是什么，如何避免

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 缓存三剑客是缓存穿透、缓存击穿、缓存雪崩。面试里按“是什么、什么时候发生、如何避免”展开，重点区分无效请求、热点 key、大面积失效三类问题。

| 问题 | 是什么 | 发生场景 | 避免方案 |
| --- | --- | --- | --- |
| 缓存穿透 | 查询无效数据，请求穿过缓存后继续打到数据库 | 恶意请求、参数异常、业务数据被删除 | 参数校验、布隆过滤器、空值缓存短 TTL |
| 缓存击穿 | 热点 key 过期或重建时，大量并发请求集中打到数据库 | 爆款商品、热点用户、热点配置等高频 key 失效 | 互斥锁、singleflight、逻辑过期、后台异步刷新 |
| 缓存雪崩 | 大量 key 集中过期或缓存服务故障，请求大面积打到数据库 | 批量设置相同 TTL、缓存集群故障、缓存预热缺失 | TTL 随机化、分层缓存、限流降级、集群高可用、缓存预热 |

**关键点：**
- 穿透：无效请求，用布隆过滤器和空值缓存兜住。
- 击穿：热点 key 失效，用互斥重建或逻辑过期稳住。
- 雪崩：大面积失效，用 TTL 随机化、高可用、限流降级降低冲击。

</div>
</details>

### 数据库和缓存如何保证一致性

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见是“先更新数据库，再删除缓存”，配合重试与消息补偿实现最终一致。面试里可按两点展开：删除缓存比更新缓存更稳妥；关键链路需幂等和失败重试。


**关键点：**
- 删除缓存比更新缓存更稳妥。
- 关键链路需幂等和失败重试。

</div>
</details>

### 先更新数据库还是先更新缓存

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 一般建议“更新 DB -> 删除缓存”，避免脏数据长时间驻留。面试里可按两点展开：直接更新缓存容易被并发请求覆盖；需考虑删缓存失败补偿。


**关键点：**
- 直接更新缓存容易被并发请求覆盖。
- 需考虑删缓存失败补偿。

</div>
</details>

### 讲一下延迟双删

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先删缓存，再更新 DB，等待短时间后再删一次缓存，降低并发脏读窗口。面试里可按两点展开：不是强一致方案，只是工程折中；需要合理延迟时间和失败重试策略。


**关键点：**
- 不是强一致方案，只是工程折中。
- 需要合理延迟时间和失败重试策略。
</div>
</details>
