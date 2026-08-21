---
title: "Redis"
aliases:
  - "/s/oehh/"
shortlink: "oehh"
---

# Redis

这里主要覆盖 Redis 的数据结构、持久化、高可用、热点问题和面试中的常见追问。

## 基础

### Redis 和 MySQL 区别，为什么 Redis 更快

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 是内存数据结构存储，常用于缓存、计数、排行榜、会话、消息流等实时场景；MySQL 是关系型数据库，侧重事务、持久化、一致性、复杂查询和关联分析。Redis 快主要来自数据主要在内存中、命令执行路径短、内置结构高效、单线程事件循环减少锁竞争和线程切换。MySQL 也有 Buffer Pool，但还要维护 SQL 优化、事务隔离、锁、redo/binlog、刷盘和崩溃恢复。

**要答的点：**
- 定位：Redis 偏缓存和实时数据结构，MySQL 偏关系建模和事务主库。
- 存储：Redis 主要内存访问，MySQL 通过 Buffer Pool、索引页和磁盘页访问。
- 性能：Redis 命令短路径、事件循环、数据结构针对场景优化。
- MySQL 优势：事务、复杂 SQL、可靠持久化、约束和恢复能力。
- 选型：热点数据和短期状态用 Redis，核心事实数据用 MySQL。

**重点讲解摘录：**
- Redis 官方把 Redis 定义为 “in-memory data structure store”。
- Redis 官方介绍提到亚毫秒级响应和数据结构能力。
- Redis latency 文档说明正常简单命令执行时间很短。
- MySQL InnoDB Buffer Pool 缓存表和索引数据，提高读性能。
- MySQL ACID 文档说明 InnoDB 为可靠业务数据提供事务能力。

**原文链接：**
- [Redis: What is Redis?](https://redis.io/tutorials/what-is-redis/)
- [Redis Docs: Diagnosing latency issues](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [Redis Docs: Redis pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/)
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [MySQL 8.4: InnoDB and ACID](https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html)

</div>
</details>

### Redis 的应用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 适合访问频率高、实时性强、生命周期相对短、结构清晰的数据。常见场景包括缓存、会话存储、计数器、限流、分布式锁、排行榜、热点统计、延迟任务、Pub/Sub 通知、Stream 消息流和地理位置查询。面试里要强调 Redis 通常作为 MySQL 等主存储的加速层和实时状态层，核心业务事实数据仍要落到可靠持久存储。

**要答的点：**
- 缓存：热点对象、查询结果、配置和页面片段。
- 会话：登录态、购物车、临时上下文，配合 TTL。
- 计数/限流：`INCR`、`EXPIRE`、Lua、ZSet。
- 排行榜：ZSet 按 score 排序。
- 消息：Pub/Sub 广播，Stream 消费组。
- 协调：`SET NX PX` + 随机值 + Lua 删除实现锁。

**重点讲解摘录：**
- Redis use cases 页面列出 rate limiting、session storage、leaderboards 等场景。
- Redis 介绍把 Redis 描述为 database、cache、message broker、streaming engine。
- Redis session 文档说明 session state 可保存用户身份、个性化和购物车状态。
- Redis distributed locks 文档强调释放锁时校验随机值。

**原文链接：**
- [Redis Docs: Redis use cases](https://redis.io/docs/latest/develop/use-cases/)
- [Redis: What is Redis?](https://redis.io/tutorials/what-is-redis/)
- [Redis: Session management](https://redis.io/solutions/use-cases/session-management/)
- [Redis Docs: Redis rate limiter](https://redis.io/docs/latest/develop/use-cases/rate-limiter/)
- [Redis Docs: Distributed Locks with Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)

</div>
</details>

## 数据结构

### Redis 有哪些数据类型，各自场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 常考先答五类基础类型：String、Hash、List、Set、Sorted Set，再补充 Bitmap、HyperLogLog、Geo、Stream。String 适合缓存、计数器、锁 token；Hash 适合对象字段；List 适合队列和简单时间线；Set 适合去重、标签、共同好友；ZSet 适合排行榜、热榜、延迟队列；Bitmap 适合签到；HyperLogLog 适合 UV 估算；Geo 适合附近的人；Stream 适合消息流和消费组。

**要答的点：**
- String：二进制安全字符串，缓存、计数、token。
- Hash：field-value 集合，对象局部更新。
- List：按插入顺序排列，队列、栈、时间线。
- Set：无序去重，标签、黑名单、交并差。
- Sorted Set：唯一成员 + score，排行榜和延迟队列。
- Stream/Bitmap/HLL/Geo：消息流、布尔统计、基数估算、位置查询。

**重点讲解摘录：**
- Redis data types 页面说明 Redis 是 data structure server。
- Redis strings 是最基础类型，表示字节序列。
- Redis hashes 是 field-value 集合，适合表示对象。
- Redis sorted sets 按 score 维护成员顺序。
- Redis streams 是 append-only log，适合事件记录和消息处理。

**原文链接：**
- [Redis Docs: Redis data types](https://redis.io/docs/latest/develop/data-types/)
- [Redis Docs: Redis strings](https://redis.io/docs/latest/develop/data-types/strings/)
- [Redis Docs: Redis hashes](https://redis.io/docs/latest/develop/data-types/hashes/)
- [Redis Docs: Redis sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/)
- [Redis Docs: Redis streams](https://redis.io/docs/latest/develop/data-types/streams/)

</div>
</details>

### 各类型底层结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 每种逻辑类型都有内部编码，核心思路是小数据用紧凑编码省内存，大数据切到通用结构保性能。String 有 `int`、`embstr`、`raw`；List 主要是 `quicklist`，节点里放 listpack；Hash 小对象用 listpack，大对象用 hashtable；Set 小整数集合用 intset，小集合可用 listpack，大集合用 hashtable；ZSet 小集合用 listpack，大集合用 skiplist，并配合 dict 做成员索引；Stream 用 radix tree 存 listpack。

**要答的点：**
- String：`int/embstr/raw`，底层核心是 SDS。
- List：quicklist + listpack。
- Hash：listpack 或 hashtable。
- Set：intset、listpack 或 hashtable。
- ZSet：listpack 或 skiplist + dict。
- Stream：radix tree + listpack。

**重点讲解摘录：**
- `OBJECT ENCODING` 文档说明可查看 key 的内部编码。
- 文档列出 String、List、Set、Hash、Sorted Set 的编码类型。
- Redis `t_zset.c` 中 zset 结构同时包含 dict 和 skiplist。
- Redis stream 结构使用 radix tree 管理 stream entries。

**原文链接：**
- [Redis Docs: OBJECT ENCODING](https://redis.io/docs/latest/commands/object-encoding/)
- [Redis Docs: Redis data types](https://redis.io/docs/latest/develop/data-types/)
- [Redis Source: t_zset.c](https://github.com/redis/redis/blob/unstable/src/t_zset.c)
- [Redis Source: stream.h](https://github.com/redis/redis/blob/unstable/src/stream.h)

</div>
</details>

### SDS 和 C 字符串区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** SDS 是 Redis 自己实现的动态字符串，在字符数组前保存长度、容量和类型等元数据，内容仍以 `\0` 结尾兼容 C 字符串函数。相比 C 字符串，SDS 获取长度是 O(1)，可以保存包含 `\0` 的二进制数据，追加时能根据剩余空间减少重复扩容，修改时也能更准确地做边界控制。

**要答的点：**
- C 字符串：依赖 `\0` 结尾，`strlen` O(N)。
- SDS 长度：header 存 `len`，读取 O(1)。
- 二进制安全：根据长度判断内容，中间可含 `\0`。
- 空间管理：`alloc` 和 `sdsavail()` 管理剩余空间。
- 扩容：`sdsMakeRoomFor()` 减少频繁 realloc。
- 兼容：返回 `char *`，末尾保留 `\0`。

**重点讲解摘录：**
- Redis String internals 文档说明 SDS 表示 Simple Dynamic Strings。
- 早期 SDS header 包含 `len`、`free`、`buf[]`。
- 当前源码中 SDS 根据长度选择不同 header 类型。
- `sdscatlen()` 使用显式长度追加数据，体现二进制安全。

**原文链接：**
- [Redis Docs: String internals](https://redis.io/docs/latest/operate/oss_and_stack/reference/internals/internals-sds/)
- [Redis Source: sds.h](https://github.com/redis/redis/blob/unstable/src/sds.h)
- [Redis Source: sds.c](https://github.com/redis/redis/blob/unstable/src/sds.c)

</div>
</details>

### 哈希冲突怎么解决

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis dict 用哈希表保存 key-value，冲突采用链地址法：多个 key 映射到同一个 bucket 时，会挂到同一条 `dictEntry` 链上，查找时先定位 bucket，再沿链逐个比较 key。冲突变多会拉长链表，Redis 会通过扩容和渐进式 rehash 降低负载；rehash 时同时持有两张表，用 `rehashidx` 分批迁移桶。

**要答的点：**
- 冲突：不同 key 映射到同一个 bucket。
- 链地址法：bucket 指向 `dictEntry` 链。
- 插入：新 entry 通常插到链表头部。
- 查找：算 hash 和下标，再遍历链比较。
- 扩容：负载升高后扩容降低平均链长。
- 渐进 rehash：两张表分批迁移，降低阻塞。

**重点讲解摘录：**
- Redis `dict.h` 注释说明冲突用 chaining 处理。
- `dictEntry` 结构包含 `next` 指针。
- `dict` 结构包含两张 hash table 和 `rehashidx`。
- `_dictRehashStep()` 会在普通操作中顺带推进 rehash。

**原文链接：**
- [Redis Source: dict.h](https://github.com/redis/redis/blob/unstable/src/dict.h)
- [Redis Source: dict.c](https://github.com/redis/redis/blob/unstable/src/dict.c)
- [Redis Docs: OBJECT ENCODING](https://redis.io/docs/latest/commands/object-encoding/)

</div>
</details>

### 讲一下跳表

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 跳表是带多级索引的有序链表。底层保存所有节点，上层抽样部分节点形成快速通道；查找时从最高层向右走，超过目标再下降一层，逐步逼近目标。它用随机层高实现概率平衡，查找、插入、删除期望复杂度是 O(logN)。Redis ZSet 数据量大时用 skiplist 维护 score 有序，用 dict 支持按 member 快速定位。

**要答的点：**
- 结构：多层有序链表。
- 查找：最高层开始，向右和向下移动。
- 插入：找到各层前驱，随机生成层高。
- 删除：更新各层前驱指针。
- 复杂度：期望 O(logN)，空间 O(N)。
- Redis：ZSet 大集合是 skiplist + dict。

**重点讲解摘录：**
- Pugh 论文说明 skip list 使用概率平衡，算法比平衡树简单。
- Redis Sorted Set 文档说明 sorted set 按 score 排序。
- `OBJECT ENCODING` 文档说明大 sorted set 使用 skiplist 编码。
- Redis `zset` 结构包含 `dict *dict` 和 `zskiplist *zsl`。

**原文链接：**
- [Redis Docs: Redis sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/)
- [Redis Docs: OBJECT ENCODING](https://redis.io/docs/latest/commands/object-encoding/)
- [Redis Source: t_zset.c](https://github.com/redis/redis/blob/unstable/src/t_zset.c)
- [William Pugh: Skip Lists](https://doi.org/10.1145/78973.78977)

</div>
</details>

## 持久化

### Redis 宕机如何处理

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 宕机处理顺序是先恢复服务，再确认数据，再排查原因，最后补高可用和降级能力。单机先拉起实例并从 RDB/AOF 恢复；主从、Sentinel 或 Cluster 环境先看故障转移是否完成，确认新主、客户端路由和复制状态。恢复后检查加载日志、key 数量、核心数据、复制 offset 和应用读写；原因排查重点看内存、磁盘、AOF fsync、RDB fork、慢查询、大 key、网络和 OOM。

**要答的点：**
- 快速恢复：确认进程、端口、日志、实例角色。
- 数据恢复：根据配置加载 RDB、AOF 或混合持久化文件。
- 数据校验：核心 key、key 数量、主从一致性、应用读写。
- 原因排查：内存、磁盘、fork、fsync、慢命令、大 key、网络。
- 高可用：主从 + Sentinel 或 Redis Cluster。
- 业务兜底：本地缓存、限流、降级、熔断和回源保护。

**重点讲解摘录：**
- Redis persistence 文档说明 Redis 提供 RDB、AOF、RDB+AOF 等持久化方式。
- RDB 是 point-in-time snapshot，AOF 通过重放写命令恢复数据。
- Sentinel 提供 monitoring、notification、automatic failover 和配置发现。
- Redis Cluster 可在多数 master 可达且故障 master 有 replica 时继续服务。

**原文链接：**
- [Redis Docs: Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis Docs: Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [Redis Docs: High availability with Redis Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

</div>
</details>

### AOF 和 RDB 对比

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RDB 是定期生成某个时间点的数据快照，文件紧凑、恢复快、适合备份和灾难恢复，代价是快照间隔内的数据可能丢失，生成快照需要 fork，写入高峰会有 COW 成本。AOF 是追加记录写命令，重启时重放命令恢复数据，持久性更强，默认每秒 fsync 通常最多丢约 1 秒数据，代价是文件更大、恢复较慢、rewrite 和 fsync 带来 I/O 压力。生产常用 RDB + AOF 混合持久化。

**要答的点：**
- RDB 原理：周期性快照整个数据集。
- RDB 优点：文件紧凑、备份方便、恢复快。
- RDB 缺点：有数据丢失窗口，fork/COW 有成本。
- AOF 原理：追加写命令，重启重放。
- AOF 优点：持久性更强，fsync 策略可调。
- AOF 缺点：文件大、恢复慢、I/O 压力高。

**重点讲解摘录：**
- Redis persistence 文档说明 RDB 是指定间隔的 point-in-time snapshot。
- AOF 会记录服务端收到的每次写操作，启动时重放。
- RDB 文件紧凑，适合备份和灾难恢复。
- AOF 默认 `fsync every second` 下通常丢失窗口约 1 秒。

**原文链接：**
- [Redis Docs: Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis Docs: BGSAVE](https://redis.io/docs/latest/commands/bgsave/)
- [Redis Docs: BGREWRITEAOF](https://redis.io/docs/latest/commands/bgrewriteaof/)

</div>
</details>

### 混合持久化

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 混合持久化是 AOF rewrite 时在新 AOF 文件开头写入一段 RDB 格式的全量快照，后面再追加 AOF 增量命令。重启恢复时先加载 RDB 基线，再重放后面的 AOF 增量，兼顾 RDB 的恢复速度和 AOF 的数据完整性。Redis 4.0 引入这个能力，生产中常用于降低纯 AOF 重放时间。

**要答的点：**
- 结构：AOF 文件 = RDB 前缀 + AOF 增量。
- 触发：AOF rewrite 生成混合格式文件。
- 恢复：先加载 RDB，再重放增量命令。
- 优点：恢复更快，数据丢失窗口接近 AOF 策略。
- 代价：文件可读性弱于纯 AOF。
- 配置：`aof-use-rdb-preamble yes`。

**重点讲解摘录：**
- Redis persistence 文档说明 AOF rewrite 可使用 RDB preamble。
- RDB preamble 加快 AOF 加载速度。
- 后续增量仍以 AOF 命令追加，保证接近 AOF 的持久性。
- 混合持久化是 RDB 和 AOF 的工程折中。

**原文链接：**
- [Redis Docs: Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis Docs: BGREWRITEAOF](https://redis.io/docs/latest/commands/bgrewriteaof/)
- [Redis configuration example](https://raw.githubusercontent.com/redis/redis/unstable/redis.conf)

</div>
</details>

### 执行快照时数据能修改吗

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 可以。Redis 执行 `BGSAVE` 时会 fork 子进程生成 RDB 快照，父进程继续处理客户端请求。fork 后父子进程共享内存页，依赖操作系统写时复制 COW；如果父进程在快照期间修改某个页面，内核会复制该页，父进程修改副本，子进程继续看到 fork 时刻的数据。写入高峰和大 key 会放大 COW 内存压力。

**要答的点：**
- BGSAVE：后台子进程生成快照。
- 父进程：继续处理读写命令。
- COW：写时复制保证子进程看到快照时刻数据。
- 成本：fork 耗时、页表复制、COW 内存增长。
- 风险：内存不足可能导致 fork 失败或 OOM。
- 优化：控制大 key、预留内存、低峰备份、监控 fork 耗时。

**重点讲解摘录：**
- Redis BGSAVE 文档说明 Redis 会 fork 子进程把数据集保存到磁盘。
- Redis persistence 文档说明 RDB 持久化由子进程完成，父进程继续服务。
- 写时复制让快照保持 fork 时刻视图。
- Redis latency 文档把 fork 列为延迟来源之一。

**原文链接：**
- [Redis Docs: BGSAVE](https://redis.io/docs/latest/commands/bgsave/)
- [Redis Docs: Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis Docs: Diagnosing latency issues](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)

</div>
</details>

### 大 key 对持久化影响

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 大 key 会放大持久化期间的 CPU、内存、磁盘和网络成本。RDB 或 AOF rewrite 需要 fork，fork 后修改大 key 可能触发大量 COW 页面复制，导致内存瞬时上涨；AOF 记录大 key 写入会产生更大日志，rewrite、fsync 和重放成本上升；主从全量同步和备份迁移也会因为大 key 变慢。治理上要拆 key、分页处理、使用 `UNLINK` 异步删除、低峰迁移和监控 `MEMORY USAGE`。

**要答的点：**
- RDB：fork 和 COW 成本上升。
- AOF：日志体积、rewrite、fsync、重放成本上升。
- 复制：全量同步和网络传输压力上升。
- 删除：同步删除大 key 会阻塞主线程。
- 发现：`--bigkeys`、`MEMORY USAGE`、`SCAN`。
- 治理：拆分、归档、分页、异步删除、限流迁移。

**重点讲解摘录：**
- Redis latency 文档说明大对象操作和 fork 都可能造成延迟。
- `MEMORY USAGE` 可估算 key 占用内存。
- `UNLINK` 可异步释放 key，降低主线程删除阻塞。
- `redis-cli --bigkeys` 可扫描发现大 key。

**原文链接：**
- [Redis Docs: Diagnosing latency issues](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [Redis Docs: MEMORY USAGE](https://redis.io/docs/latest/commands/memory-usage/)
- [Redis Docs: UNLINK](https://redis.io/docs/latest/commands/unlink/)
- [Redis Docs: redis-cli](https://redis.io/docs/latest/develop/tools/cli/)

</div>
</details>

## 功能

### 过期删除和内存淘汰区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 过期删除处理的是已经设置 TTL 且到期的 key，目标是清理生命周期结束的数据；内存淘汰处理的是 Redis 内存达到 `maxmemory` 限制时，从 key 空间里选一些 key 释放，目标是控制内存上限。前者由 TTL 到期触发，常见策略是惰性删除和定期删除；后者由内存压力触发，策略包括 LRU、LFU、random、ttl 和 noeviction。

**要答的点：**
- 过期删除：key 到达 TTL 后清理。
- 内存淘汰：达到 `maxmemory` 后按策略释放内存。
- 触发条件：时间到期 vs 内存不足。
- 作用对象：已过期 key vs 可淘汰 key 集合。
- 策略：lazy/active expire vs eviction policies。
- 同时存在：过期 key 未及时删除时也会占内存。

**重点讲解摘录：**
- Redis expire 文档说明 key 可设置超时时间，到期后自动删除。
- Redis eviction 文档说明 `maxmemory-policy` 决定内存达到上限后的行为。
- Redis 使用被动和主动两种方式清理过期 key。
- noeviction 策略下，内存达到上限后写命令会返回错误。

**原文链接：**
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)
- [Redis Docs: Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis Docs: Redis expires](https://redis.io/docs/latest/commands/expire/#expires-and-persistence)

</div>
</details>

### 过期删除策略

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 过期删除采用惰性删除和定期删除结合。惰性删除是在访问 key 时检查是否过期，过期就删除，优点是只处理被访问的 key，代价是长期不访问的过期 key 可能滞留内存；定期删除是 Redis 周期性抽样检查带过期时间的 key，把过期的删掉，优点是主动释放内存，代价是需要消耗 CPU。Redis 通过抽样和时间预算控制删除开销。

**要答的点：**
- 惰性删除：访问时检查 TTL。
- 定期删除：后台周期抽样扫描 expires 字典。
- 内存影响：冷门过期 key 可能滞留。
- CPU 影响：定期删除要控制扫描时间。
- 配合淘汰：内存压力下还会走 eviction。
- 面试收口：时间和空间之间折中。

**重点讲解摘录：**
- Redis EXPIRE 文档说明过期信息会随 key 存储。
- Redis 过期机制包含被动方式和主动方式。
- 被动方式发生在客户端访问 key 时。
- 主动方式通过周期性抽样清理过期 key。

**原文链接：**
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)
- [Redis Docs: Redis expires](https://redis.io/docs/latest/commands/expire/#expires-and-persistence)
- [Redis Source: expire.c](https://github.com/redis/redis/blob/unstable/src/expire.c)

</div>
</details>

### 内存淘汰策略（缓存满了怎么办）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 达到 `maxmemory` 后会按 `maxmemory-policy` 选择处理方式。缓存场景常用 `allkeys-lru` 或 `allkeys-lfu`，从所有 key 中淘汰最近少用或低频访问的 key；只想淘汰设置 TTL 的缓存 key，可用 `volatile-lru/volatile-lfu/volatile-ttl/random`；`noeviction` 会在内存不足时拒绝写命令。选择策略要结合数据是否都可丢、热点是否稳定、是否设置 TTL。

**要答的点：**
- `noeviction`：写入报错，读仍可服务。
- `allkeys-lru`：所有 key 中淘汰近似 LRU。
- `allkeys-lfu`：所有 key 中淘汰低频 key。
- `volatile-lru/lfu`：只在设置过期时间的 key 中淘汰。
- `volatile-ttl`：优先淘汰 TTL 更短的 key。
- `random`：随机淘汰，成本低但命中率较差。

**重点讲解摘录：**
- Redis eviction 文档列出 `maxmemory-policy` 可选策略。
- LRU 和 LFU 是近似实现，Redis 通过采样选择候选 key。
- `volatile-*` 策略只处理带 expire 的 key。
- `allkeys-*` 策略把整个 key 空间作为淘汰候选。

**原文链接：**
- [Redis Docs: Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis configuration example](https://raw.githubusercontent.com/redis/redis/unstable/redis.conf)
- [Redis Docs: MEMORY STATS](https://redis.io/docs/latest/commands/memory-stats/)

</div>
</details>

### LRU 和 LFU

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** LRU 看最近一次访问时间，优先淘汰最近最久未访问的 key，适合热点变化快的场景；LFU 看访问频率，优先淘汰访问次数低的 key，适合长期稳定热点。Redis 的 LRU 和 LFU 都是近似算法，淘汰时从样本中挑候选，避免维护全量精确链表的高成本。实际选择要看业务热点是否短期突发还是长期稳定。

**要答的点：**
- LRU：Least Recently Used，按最近访问时间。
- LFU：Least Frequently Used，按访问频率。
- LRU 场景：热点切换快、最近访问更有预测性。
- LFU 场景：长期热点稳定、偶发访问干扰少。
- Redis 实现：采样近似，降低维护成本。
- 参数：LFU 有计数衰减和增长因子配置。

**重点讲解摘录：**
- Redis eviction 文档说明 LRU/LFU 都以近似方式实现。
- Redis 使用采样池从候选 key 中选择淘汰对象。
- LFU 使用近似计数器并支持随时间衰减。
- 热点访问模式决定 LRU 和 LFU 的命中率表现。

**原文链接：**
- [Redis Docs: Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [Redis configuration example](https://raw.githubusercontent.com/redis/redis/unstable/redis.conf)

</div>
</details>

## 高可用

### 单个 Redis 压力过大怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 单个 Redis 压力大先定位瓶颈是 CPU、内存、网络、慢命令还是热点 key。读压力大可以加从库读、客户端本地缓存、热点 key 拆分或副本分担；写压力大要优化命令、减少大 key、pipeline 批量、Lua 控制复杂度，必要时按业务分片或上 Redis Cluster；内存压力大要设置合理淘汰策略、拆冷热数据、压缩 value 和清理无效 key。

**要答的点：**
- 定位：QPS、CPU、内存、网络、慢日志、大 key、热 key。
- 读扩展：主从读、缓存分层、本地缓存、热点复制。
- 写优化：pipeline、批量、减少复杂命令、拆大 key。
- 横向扩展：业务分片或 Redis Cluster。
- 内存治理：TTL、淘汰、压缩、归档。
- 保护：限流、降级、熔断和连接池控制。

**重点讲解摘录：**
- Redis latency 文档建议关注慢命令、fork、持久化、内存和网络。
- Redis pipelining 可减少往返时间，提高批量命令吞吐。
- Redis Cluster 通过 hash slot 分片扩展容量和吞吐。
- `SLOWLOG` 可记录执行较慢的命令。

**原文链接：**
- [Redis Docs: Diagnosing latency issues](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [Redis Docs: Redis pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/)
- [Redis Docs: Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis Docs: SLOWLOG](https://redis.io/docs/latest/commands/slowlog/)

</div>
</details>

### 如何保证集群数据一致性

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 集群通常提供最终一致性，核心是通过主从复制、故障转移、复制 offset 和业务补偿缩小不一致窗口。普通复制是异步的，主库写入后从库可能滞后；故障切换时，尚未复制到从库的数据可能丢失。工程上可以监控复制延迟，对关键写使用 `WAIT` 等待副本确认，业务侧做幂等、重试、校验和补偿；强一致核心数据应落在数据库或专门的一致性系统。

**要答的点：**
- 复制模型：主从异步复制为主。
- 风险：复制延迟、故障切换数据丢失、脑裂。
- 监控：master_repl_offset、slave_repl_offset、复制延迟。
- `WAIT`：等待写入传播到指定副本数。
- 业务补偿：幂等、重试、对账、最终修正。
- 选型：强一致数据放 MySQL/分布式数据库。

**重点讲解摘录：**
- Redis replication 文档说明复制默认异步。
- `WAIT` 命令可阻塞直到写入被指定数量副本确认。
- Redis Cluster 规范说明分区和故障期间可能丢失已确认写。
- Sentinel/Cluster 的自动故障转移提高可用性，也存在复制窗口。

**原文链接：**
- [Redis Docs: Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [Redis Docs: WAIT](https://redis.io/docs/latest/commands/wait/)
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

</div>
</details>

### 主从复制如何实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis 主从复制分全量同步和增量复制。从库第一次连接主库时发送同步请求，主库生成 RDB 快照并发送给从库，同时把期间新增写命令缓存起来；从库加载 RDB 后，主库继续发送增量命令。后续连接短暂中断时，从库带复制 ID 和 offset 请求部分重同步，主库如果复制积压缓冲区还保留所需数据，就只发送缺失增量；否则重新全量同步。

**要答的点：**
- 全量同步：RDB 快照 + 同步期间命令缓冲。
- 增量复制：持续传播写命令。
- PSYNC：基于 replication ID 和 offset 部分重同步。
- Backlog：复制积压缓冲区保存最近写命令。
- 延迟：网络、从库加载、慢命令和写入压力影响复制。
- 链式复制：从库也可作为其他从库的上游。

**重点讲解摘录：**
- Redis replication 文档说明 replica 连接 master 后会同步数据。
- Partial resynchronization 依赖 replication ID、offset 和 backlog。
- 全量同步通常涉及 RDB 文件传输和加载。
- 复制链路中断后，Redis 会尝试部分重同步。

**原文链接：**
- [Redis Docs: Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [Redis Docs: PSYNC](https://redis.io/docs/latest/commands/psync/)
- [Redis Docs: INFO replication](https://redis.io/docs/latest/commands/info/)

</div>
</details>

### 如何应对主从不一致

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 主从不一致通常来自异步复制延迟、网络抖动、从库负载高、主库故障切换窗口。处理上先监控复制延迟和 offset 差距，读业务按一致性要求选择读主或读从；关键写可以用 `WAIT` 等待副本确认；故障切换后做数据校验和补偿；从库长期落后要扩容、优化慢命令、调整 backlog、排查网络和磁盘。业务侧要保证幂等和可重放。

**要答的点：**
- 监控：复制 offset、lag、link status。
- 路由：强一致读主，弱一致读从。
- 确认：关键写用 `WAIT` 缩小窗口。
- 补偿：对账、重放、修正缓存。
- 治理：扩容从库、优化慢命令、网络和磁盘排查。
- 故障：Sentinel/Cluster 切主后确认新主数据状态。

**重点讲解摘录：**
- Redis replication 是异步复制，会存在延迟。
- `INFO replication` 暴露复制 offset 和连接状态。
- `WAIT` 可等待写传播到副本。
- Cluster 规范说明故障窗口内可能出现写丢失。

**原文链接：**
- [Redis Docs: Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [Redis Docs: INFO](https://redis.io/docs/latest/commands/info/)
- [Redis Docs: WAIT](https://redis.io/docs/latest/commands/wait/)
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)

</div>
</details>

### 什么是哨兵，为什么要有

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis Sentinel 是 Redis 的高可用组件，负责监控主从实例、发现故障、通知应用、自动故障转移和提供当前主库地址。它解决的是单主从架构里主库故障后的自动切换问题：多个 Sentinel 通过投票确认主观下线和客观下线，选出一个从库提升为新主，并让其他从库复制新主。Sentinel 提供高可用，不负责数据分片。

**要答的点：**
- Monitoring：监控 master、replica、Sentinel。
- Notification：故障事件通知。
- Automatic failover：主库故障后自动提升从库。
- Configuration provider：客户端可查询当前主库地址。
- 多 Sentinel：投票降低误判。
- 边界：Sentinel 不做分片，容量扩展靠 Cluster 或业务分片。

**重点讲解摘录：**
- Redis Sentinel 文档列出 monitoring、notification、automatic failover、configuration provider。
- Sentinel 会在 master 故障时把 replica 提升为 master。
- 多个 Sentinel 协作完成客观下线判断和故障转移授权。
- 客户端可通过 Sentinel 获取当前 master 地址。

**原文链接：**
- [Redis Docs: High availability with Redis Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- [Redis Docs: Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

</div>
</details>

### 讲一下哨兵机制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Sentinel 会周期性向 master、replica 和其他 Sentinel 发送探测命令，单个 Sentinel 认为 master 不可达时标记主观下线；当足够多 Sentinel 都认为 master 不可达时，形成客观下线；随后 Sentinel 之间选举 leader，由 leader 选择一个合适 replica 提升为新 master，其他 replica 改为复制新 master，并通知客户端更新地址。

**要答的点：**
- 探测：定期 PING 和 INFO 获取实例状态。
- 主观下线：单个 Sentinel 判断 master 异常。
- 客观下线：达到 quorum 后共同确认。
- 选举：Sentinel 选出 failover leader。
- 选主：按优先级、复制偏移量等选择 replica。
- 通知：发布事件，客户端更新 master 地址。

**重点讲解摘录：**
- Sentinel 文档说明主观下线和客观下线的区别。
- Quorum 用于决定 master 是否客观下线。
- Failover 包含选 replica、发送 slaveof no one、重配置其他 replica。
- Sentinel 也会持续发现新 replica 和新 Sentinel。

**原文链接：**
- [Redis Docs: Sentinel failover](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- [Redis Docs: Sentinel clients](https://redis.io/docs/latest/develop/reference/sentinel-clients/)

</div>
</details>

### Redis Cluster 是什么，解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis Cluster 是 Redis 官方分片和高可用方案，把整个 key 空间划分为 16384 个 hash slot，每个 master 负责一部分 slot，key 通过 CRC16 计算 slot 后路由到对应节点。它解决单机容量和吞吐瓶颈，同时通过 master-replica 和故障转移提供一定高可用。客户端需要支持 slot 路由和 MOVED/ASK 重定向。

**要答的点：**
- 分片：16384 个 hash slot。
- 路由：key -> CRC16 -> slot -> node。
- 高可用：master + replica，故障时提升 replica。
- 重定向：MOVED 永久迁移，ASK 迁移中临时跳转。
- 限制：多 key 操作要求同 slot，可用 hash tag。
- 目标：横向扩展容量和吞吐。

**重点讲解摘录：**
- Redis Cluster 规范说明 key 空间分成 16384 个 hash slots。
- Cluster 使用 hash tags 让多个 key 落到同一 slot。
- Cluster 节点通过 gossip 维护集群状态。
- 集群在多数 master 可达且故障 master 有 replica 时保持可用。

**原文链接：**
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis Docs: Scale with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)
- [Redis Docs: CLUSTER KEYSLOT](https://redis.io/docs/latest/commands/cluster-keyslot/)

</div>
</details>

### Cluster 下客户端如何找节点

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Cluster 客户端会缓存 slot 到节点的映射。发命令时先对 key 计算 CRC16，再对 16384 取模得到 slot，按本地映射发到对应节点；如果节点返回 `MOVED`，说明 slot 已迁移到新节点，客户端更新映射后重试；如果返回 `ASK`，说明 slot 正在迁移，客户端临时向目标节点发送 `ASKING` 后执行本次命令。成熟客户端会自动维护路由表。

**要答的点：**
- 算 slot：CRC16(key) mod 16384。
- 路由表：客户端缓存 slot -> node。
- MOVED：永久重定向，更新本地缓存。
- ASK：迁移中的临时重定向。
- Hash tag：`{}` 内内容用于计算 slot。
- 多 key：同一命令涉及多个 key 时需同 slot。

**重点讲解摘录：**
- Cluster 规范定义 key 到 hash slot 的算法。
- MOVED 重定向表示客户端应更新 slot 映射。
- ASK 重定向用于 resharding 过程中的临时访问。
- Hash tags 让相关 key 映射到同一 slot。

**原文链接：**
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis Docs: CLUSTER KEYSLOT](https://redis.io/docs/latest/commands/cluster-keyslot/)
- [Redis Docs: Scale with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)

</div>
</details>

### 集群节点故障怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Redis Cluster 节点故障时，其他节点通过 gossip 和故障检测把节点标记为疑似下线和确认下线；如果故障的是 master，且它有可用 replica，集群会发起故障转移，把一个 replica 提升为新 master，接管原 master 的 slots；客户端收到 MOVED 后更新路由继续访问。集群可用性依赖多数 master 可达和每个故障 master 有可提升副本。

**要答的点：**
- 探测：节点间 PING/PONG 和 gossip 传播状态。
- PFAIL：单节点认为某节点疑似故障。
- FAIL：多数派确认故障。
- Failover：replica 竞选并提升为 master。
- Slot 接管：新 master 接管故障 master 的 slots。
- 客户端：根据 MOVED 更新路由表。

**重点讲解摘录：**
- Cluster 规范说明节点使用 gossip 交换集群状态。
- 故障检测包含 PFAIL 和 FAIL 状态。
- Cluster 在 master 故障且有 replica 时可自动故障转移。
- 集群可用性要求多数 master 参与决策。

**原文链接：**
- [Redis Docs: Redis cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis Docs: Scale with Redis Cluster](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)

</div>
</details>

## 缓存

### Redis 缓存穿透、击穿、雪崩是什么，如何避免

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 缓存穿透、击穿、雪崩分别对应无效请求、热点 key 失效、大面积失效。穿透是查询不存在的数据，缓存和数据库都没有，解决靠参数校验、布隆过滤器、空值缓存；击穿是热点 key 过期瞬间大量请求打到数据库，解决靠互斥重建、singleflight、逻辑过期、后台刷新；雪崩是大量 key 同时过期或缓存集群故障，解决靠 TTL 随机化、分层缓存、限流降级、高可用和预热。

| 问题 | 是什么 | 典型方案 |
| --- | --- | --- |
| 穿透 | 请求不存在数据，绕过缓存打 DB | 参数校验、布隆过滤器、空值短 TTL |
| 击穿 | 热点 key 失效，大量请求集中回源 | 互斥锁、singleflight、逻辑过期、异步刷新 |
| 雪崩 | 大量 key 集中过期或 Redis 故障 | TTL 随机化、集群高可用、限流降级、预热 |

**要答的点：**
- 穿透：无效 key，重点挡在缓存和 DB 前。
- 击穿：单个热点 key，重点控制重建并发。
- 雪崩：大面积 key 或服务异常，重点分散风险和兜底。
- 监控：缓存命中率、DB QPS、热点 key、错误率。
- 业务：核心接口要有限流、降级和回源保护。

**重点讲解摘录：**
- Redis caching 文档说明 cache-aside 是常见缓存模式。
- Bloom filter 可用于判断元素是否可能存在。
- Redis TTL 和过期机制支撑缓存生命周期管理。
- 高可用和限流是缓存故障时保护数据库的关键。

**原文链接：**
- [Redis: Caching](https://redis.io/solutions/use-cases/caching/)
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)
- [Redis Docs: RedisBloom](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/)
- [Redis Docs: Key eviction](https://redis.io/docs/latest/develop/reference/eviction/)

</div>
</details>

### 数据库和缓存如何保证一致性

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见做法是 Cache Aside：读请求先查缓存，未命中再查数据库并回填；写请求先更新数据库，再删除缓存，让下一次读回源数据库并回填新值。这个方案追求最终一致，关键是删缓存失败要有重试和补偿，例如消息队列、binlog 订阅、定时校验和缓存 TTL。热点 key 回填时要加互斥或 singleflight，避免并发把旧值写回缓存。

**要答的点：**
- 读路径：缓存命中直接返回，未命中查 DB 后回填。
- 写路径：更新 DB 后删除缓存。
- 最终一致：短时间不一致可接受，靠 TTL 和补偿收敛。
- 失败补偿：重试队列、binlog 监听、定时校验。
- 并发控制：热点 key 回填加锁或 singleflight。
- 高一致读：关键读走主库或删除后延迟再查。

**重点讲解摘录：**
- Redis caching 文档介绍 cache-aside 模式。
- Cache-aside 下应用负责读取缓存、回源数据源和回填缓存。
- 删除缓存让后续读取自然回源并重建缓存。
- TTL 是最终一致的兜底手段。

**原文链接：**
- [Redis: Caching](https://redis.io/solutions/use-cases/caching/)
- [Microsoft Azure Architecture: Cache-Aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)

</div>
</details>

### 先更新数据库还是先更新缓存

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 主流建议是先更新数据库，再删除缓存。直接更新缓存在并发写场景下容易被旧请求覆盖，且缓存值可能由复杂查询聚合得到，更新成本高；删除缓存让下一次读回源数据库生成最新值，更容易保证最终一致。工程上要处理删除失败，用重试、MQ、binlog 订阅和 TTL 兜底；对高并发热点读，还要防止旧查询结果在删除后回填。

**要答的点：**
- 推荐：更新 DB -> 删除缓存。
- 原因：缓存可能是派生数据，更新缓存复杂。
- 并发：直接更新缓存容易出现写顺序覆盖。
- 失败：删除缓存失败需要补偿。
- 热点：回填要互斥，避免旧值回填。
- 兜底：缓存 TTL、重试队列、binlog 监听。

**重点讲解摘录：**
- Cache-aside 模式由应用管理缓存和数据源。
- 写入数据库后删除缓存可以让后续读重新加载最新数据。
- 缓存 TTL 能在补偿失败时限制脏数据存在时间。
- 并发更新时，业务版本号或更新时间也可用于防旧值覆盖。

**原文链接：**
- [Redis: Caching](https://redis.io/solutions/use-cases/caching/)
- [Microsoft Azure Architecture: Cache-Aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)

</div>
</details>

### 讲一下延迟双删

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 延迟双删是一种缓存一致性补偿方案：先删除缓存，再更新数据库，等待一段时间后再删除一次缓存。它针对的并发窗口是第一次删缓存后，有读请求回源读到旧数据库值并写回缓存；第二次延迟删除可以清掉这个旧值。这个方案是最终一致的工程折中，关键是延迟时间要覆盖读请求和数据库更新的常见耗时，并且第二次删除也要有失败重试。

**要答的点：**
- 流程：删缓存 -> 更新 DB -> sleep 一段时间 -> 再删缓存。
- 目的：清理并发读回填的旧缓存。
- 延迟设置：略大于读请求耗时和主从同步延迟。
- 失败处理：第二次删除要重试或异步补偿。
- 适用：对短暂不一致可接受的缓存场景。
- 取舍：实现简单，仍属于最终一致方案。

**重点讲解摘录：**
- Cache-aside 模式下缓存由应用维护，存在并发回填窗口。
- TTL、重试和异步补偿是缓存最终一致常见兜底。
- 延迟双删的关键是用第二次删除覆盖旧值回填。
- 高一致场景可结合 binlog 订阅和版本校验。

**原文链接：**
- [Redis: Caching](https://redis.io/solutions/use-cases/caching/)
- [Microsoft Azure Architecture: Cache-Aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis Docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)

</div>
</details>
