# MySQL

这里按基础、索引、事务、锁和日志几个方向整理 MySQL 常见面试题，适合系统梳理数据库知识。

## 基础

### 增删改查的语法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 核心是 `SELECT/INSERT/UPDATE/DELETE` 四类语句，面试更看你是否会结合条件、排序、分页和事务使用。面试里可按两点展开：`WHERE/GROUP BY/HAVING/ORDER BY/LIMIT` 常见组合；修改类语句建议放事务里保证一致性。


**关键点：**
- `WHERE/GROUP BY/HAVING/ORDER BY/LIMIT` 常见组合。
- 修改类语句建议放事务里保证一致性。

</div>
</details>

### select 语句执行流程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 大致是“连接器 -> 解析器 -> 优化器 -> 执行器 -> 存储引擎”。面试里可按两点展开：优化器会选索引和执行计划；执行器按计划向存储引擎取数并返回结果。


**关键点：**
- 优化器会选索引和执行计划。
- 执行器按计划向存储引擎取数并返回结果。

</div>
</details>

### SQL 中一行记录如何存储

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 按“页（默认 16KB）”存数据，行记录包含隐藏列（事务 ID、回滚指针等）并以行格式组织。面试里可按三点展开：页是最小 I/O 单位；行格式（Compact/Dynamic）影响变长字段存储；事务可见性依赖隐藏列与 undo log。


**关键点：**
- 页是最小 I/O 单位。
- 行格式（Compact/Dynamic）影响变长字段存储。
- 事务可见性依赖隐藏列与 undo log。

</div>
</details>

### 执行 update 会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先定位记录，写 undo log，更新内存页并写 redo log，事务提交时写 binlog，后台再刷脏页落盘。面试里可按三点展开：先写日志后落盘（WAL 思想）；可能加行锁/间隙锁；涉及两阶段提交保证 redo/binlog 一致。


**关键点：**
- 先写日志后落盘（WAL 思想）。
- 可能加行锁/间隙锁。
- 涉及两阶段提交保证 redo/binlog 一致。

</div>
</details>

## 索引

### 什么是索引？作用和类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 索引是加速检索的数据结构，本质是“空间换时间”。面试里可按两点展开：InnoDB 主流是 B+Tree；常见分类：主键/唯一/普通/联合索引。


**关键点：**
- InnoDB 主流是 B+Tree。
- 常见分类：主键/唯一/普通/联合索引。

</div>
</details>

### 如何优化索引

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 核心是“让高频查询走对索引，减少回表和扫描行数”。面试里可按三点展开：结合 `EXPLAIN` 看执行计划；联合索引按最左前缀设计；避免冗余索引与低区分度单列索引。


**关键点：**
- 结合 `EXPLAIN` 看执行计划。
- 联合索引按最左前缀设计。
- 避免冗余索引与低区分度单列索引。

</div>
</details>

### 什么时候用索引、怎么设计

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 筛选性高、排序分组频繁、关联条件稳定的列优先建索引。面试里可按三点展开：优先覆盖高频查询场景；控制索引数量，平衡写入成本；联合索引顺序按“过滤性 + 使用频率”。


**关键点：**
- 优先覆盖高频查询场景。
- 控制索引数量，平衡写入成本。
- 联合索引顺序按“过滤性 + 使用频率”。

</div>
</details>

### B+ 树结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 非叶子节点存键和子指针，叶子节点存完整索引项，叶子间有链表。面试里可按两点展开：层级低，磁盘访问次数少；范围查询和排序友好。


**关键点：**
- 层级低，磁盘访问次数少。
- 范围查询和排序友好。

</div>
</details>

### B+ 树 vs B 树、B+ 树 vs 哈希

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** B+ 树更适合范围查询；哈希适合等值查询但不擅长范围和排序。面试里可按两点展开：B+ 树非叶不存值，单页可放更多键；哈希冲突处理和扩容成本要考虑。


**关键点：**
- B+ 树非叶不存值，单页可放更多键。
- 哈希冲突处理和扩容成本要考虑。

</div>
</details>

### 聚簇索引和二级索引

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 聚簇索引叶子存整行数据；二级索引叶子存索引列 + 主键值。面试里可按两点展开：二级索引查整行常需“回表”；主键设计影响二级索引大小。


**关键点：**
- 二级索引查整行常需“回表”。
- 主键设计影响二级索引大小。

</div>
</details>

### 什么是回表，优劣势

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先走二级索引拿主键，再回聚簇索引取完整行。面试里可按两点展开：优势：可利用更小索引快速定位；劣势：多一次树查找，随机 I/O 增加。


**关键点：**
- 优势：可利用更小索引快速定位。
- 劣势：多一次树查找，随机 I/O 增加。

</div>
</details>

### 索引失效场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 不满足最左前缀、函数/计算包裹列、隐式类型转换、前导通配符等都可能失效。面试里可按两点展开：`LIKE '%xx'` 难用普通索引；条件类型要与列类型一致。


**关键点：**
- `LIKE '%xx'` 难用普通索引。
- 条件类型要与列类型一致。

</div>
</details>

### 如何高效分页

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 深分页优先“游标/延迟关联”而不是大 offset。面试里可按两点展开：`limit offset` 很大时会扫描大量无效行；方案：`where id > last_id limit n` 或子查询先取主键再回表。


**关键点：**
- `limit offset` 很大时会扫描大量无效行。
- 方案：`where id > last_id limit n` 或子查询先取主键再回表。

</div>
</details>

## 事务

### 事务四大特性（ACID）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 原子性、一致性、隔离性、持久性。面试里可按三点展开：原子性靠 undo；持久性靠 redo；隔离性靠锁 + MVCC。


**关键点：**
- 原子性靠 undo。
- 持久性靠 redo。
- 隔离性靠锁 + MVCC。

</div>
</details>

### 脏读、不可重复读、幻读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：**。面试里重点展开：三者核心区别是“未提交/同一行变化/行集合变化”。

- 脏读：读到未提交数据。
- 不可重复读：同一条件两次读同一行结果不同。
- 幻读：同一条件两次查询行数不同。

**关键点：**
- 三者核心区别是“未提交/同一行变化/行集合变化”。

</div>
</details>

### 事务隔离级别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 读未提交、读已提交、可重复读、串行化。面试里可按两点展开：隔离越强，并发通常越低；MySQL InnoDB 默认可重复读。


**关键点：**
- 隔离越强，并发通常越低。
- MySQL InnoDB 默认可重复读。

</div>
</details>

### 什么是 Read View

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Read View 是 MVCC 的可见性快照，决定当前事务能看到哪些版本。面试里可按两点展开：包含活跃事务 ID 集合和边界值；用来判断版本链中的行版本是否可见。


**关键点：**
- 包含活跃事务 ID 集合和边界值。
- 用来判断版本链中的行版本是否可见。

</div>
</details>

### Read View 如何解决读问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 通过版本链 + 可见性规则，让快照读在并发下读取一致版本，避免脏读并缓解不可重复读。面试里可按两点展开：快照读不加锁读取历史版本；当前读（加锁读）不走这一套。


**关键点：**
- 快照读不加锁读取历史版本。
- 当前读（加锁读）不走这一套。

</div>
</details>

### RR 是否完全解决幻读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 快照读场景下基本避免幻读；当前读仍需 next-key lock 配合。面试里可按两点展开：面试要区分快照读与当前读；幻读治理依赖 MVCC + 锁。


**关键点：**
- 面试要区分快照读与当前读。
- 幻读治理依赖 MVCC + 锁。

</div>
</details>

### RR 下执行 Update 会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Update 是当前读，会加锁并更新最新可修改版本，同时产生 undo/redo/binlog。面试里可按两点展开：可能触发记录锁/间隙锁；与普通快照读行为不同。


**关键点：**
- 可能触发记录锁/间隙锁。
- 与普通快照读行为不同。

</div>
</details>

## 锁

### MySQL 中有哪些锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 按粒度分全局锁、表锁、行锁；按语义分共享锁（S）和排他锁（X）。面试里可按两点展开：InnoDB 行锁依赖索引条件；还有意向锁用于表级协调。


**关键点：**
- InnoDB 行锁依赖索引条件。
- 还有意向锁用于表级协调。

</div>
</details>

### 全局锁、表级锁、行级锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 粒度越大冲突越大但管理简单；粒度越小并发越高但管理更复杂。面试里可按三点展开：全局锁常用于备份；表锁实现简单但影响并发；行锁并发高但要注意死锁。


**关键点：**
- 全局锁常用于备份。
- 表锁实现简单但影响并发。
- 行锁并发高但要注意死锁。

</div>
</details>

### 表级锁类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见有表读锁、表写锁、元数据锁（MDL）、意向锁（逻辑上配合行锁）。面试里可按两点展开：DDL 常与 MDL 相关阻塞；意向锁不直接锁行，主要做兼容性判断。


**关键点：**
- DDL 常与 MDL 相关阻塞。
- 意向锁不直接锁行，主要做兼容性判断。

</div>
</details>

### 行级锁类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 记录锁、间隙锁、next-key lock（记录锁+间隙锁）。面试里可按两点展开：RR 下防幻读常用 next-key；锁范围取决于索引命中方式。


**关键点：**
- RR 下防幻读常用 next-key。
- 锁范围取决于索引命中方式。

</div>
</details>

### 记录锁 + 间隙锁能防删除导致的幻读吗

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 能在对应索引范围内阻止插入/删除造成的集合变化，从而抑制幻读。面试里可按两点展开：前提是命中正确索引范围；不同 SQL 条件下锁区间不同。


**关键点：**
- 前提是命中正确索引范围。
- 不同 SQL 条件下锁区间不同。

</div>
</details>

### MySQL 死锁怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先让数据库自动检测回滚一方，再从业务上缩短事务和统一加锁顺序。面试里可按三点展开：保持事务短小；固定访问顺序减少环路等待；必要时重试机制兜底。


**关键点：**
- 保持事务短小。
- 固定访问顺序减少环路等待。
- 必要时重试机制兜底。

</div>
</details>

## 日志

### 三种日志及作用

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** undo（回滚/MVCC）、redo（崩溃恢复）、binlog（归档复制）。面试里可按三点展开：undo 逻辑回滚；redo 物理页修改；binlog 面向复制和审计。


**关键点：**
- undo 逻辑回滚。
- redo 物理页修改。
- binlog 面向复制和审计。

</div>
</details>

### undo log 结构与回滚

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** undo 记录旧版本信息并形成版本链，回滚时按反向操作恢复。面试里可按两点展开：与事务 ID、回滚指针关联；也是 MVCC 可见性基础。


**关键点：**
- 与事务 ID、回滚指针关联。
- 也是 MVCC 可见性基础。

</div>
</details>

### redo log 什么时候刷盘

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 由 `innodb_flush_log_at_trx_commit` 策略决定，提交时可 0/1/2 不同级别刷盘。面试里可按两点展开：`1` 最安全，性能相对低；`0/2` 性能更好但宕机丢失窗口更大。


**关键点：**
- `1` 最安全，性能相对低。
- `0/2` 性能更好但宕机丢失窗口更大。

</div>
</details>

### redo log 写满怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 会触发 checkpoint 推进，把脏页刷盘释放可复用日志空间。面试里可按两点展开：checkpoint 跟刷脏强相关；写入高峰下可能出现等待。


**关键点：**
- checkpoint 跟刷脏强相关。
- 写入高峰下可能出现等待。

</div>
</details>

### redo log 和 binlog 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** redo 是 InnoDB 层物理日志，binlog 是 Server 层逻辑日志。面试里可按两点展开：redo 用于 crash recovery；binlog 用于主从复制与数据恢复。


**关键点：**
- redo 用于 crash recovery。
- binlog 用于主从复制与数据恢复。

</div>
</details>

### 主从复制实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 主库写 binlog，从库 IO 线程拉取并写 relay log，SQL 线程重放。面试里可按两点展开：异步复制默认存在延迟；可用半同步降低丢失窗口。


**关键点：**
- 异步复制默认存在延迟。
- 可用半同步降低丢失窗口。

</div>
</details>

### binlog 什么时候刷盘

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 由 `sync_binlog` 控制，常见 1 表示每次提交都刷盘。面试里可按两点展开：值越小性能越好但丢失风险越高；常与 redo 刷盘策略一起评估。


**关键点：**
- 值越小性能越好但丢失风险越高。
- 常与 redo 刷盘策略一起评估。

</div>
</details>

### update 语句执行过程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 定位记录 -> 加锁 -> 生成 undo -> 更新页并写 redo -> 提交写 binlog -> 释放锁。面试里可按两点展开：面试要说清“先日志后数据页落盘”；更新最终可能异步刷盘。


**关键点：**
- 面试要说清“先日志后数据页落盘”。
- 更新最终可能异步刷盘。

</div>
</details>

### 为什么两阶段提交

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 为保证 redo log 和 binlog 原子一致，避免主从或恢复出现“半成功”。面试里可按两点展开：prepare：redo 进入准备状态；commit：binlog 成功后提交 redo。


**关键点：**
- prepare：redo 进入准备状态。
- commit：binlog 成功后提交 redo。

</div>
</details>

### 提交时异常重启会怎样

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL 会根据 redo 状态和 binlog 一致性决定回滚或重做，尽量恢复到一致状态。面试里可按两点展开：依赖两阶段提交信息判断；目标是防止“已写 binlog 未落 redo”或反之。


**关键点：**
- 依赖两阶段提交信息判断。
- 目标是防止“已写 binlog 未落 redo”或反之。

</div>
</details>

### MySQL I/O 高如何优化

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 从 SQL、索引、内存、刷盘策略和存储层面联合优化。面试里可按三点展开：优化慢 SQL 与索引命中；提高 Buffer Pool 命中率；调整刷盘参数与硬件（SSD/IOPS）。


**关键点：**
- 优化慢 SQL 与索引命中。
- 提高 Buffer Pool 命中率。
- 调整刷盘参数与硬件（SSD/IOPS）。

</div>
</details>

## 内存

### 什么是 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Buffer Pool 是 InnoDB 的数据页缓存区，用于减少磁盘 I/O。面试里可按两点展开：缓存数据页、索引页、undo 页等；命中率直接影响查询性能。


**关键点：**
- 缓存数据页、索引页、undo 页等。
- 命中率直接影响查询性能。

</div>
</details>

### 为什么要有 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 磁盘随机读写慢，缓存热点页可显著提升吞吐和响应速度。面试里可按两点展开：读大多先命中缓存；写先改内存页，后续异步刷盘。


**关键点：**
- 读大多先命中缓存。
- 写先改内存页，后续异步刷盘。

</div>
</details>

### Buffer Pool 结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 包含 free list、LRU list、flush list 等链表结构管理页状态。面试里可按三点展开：LRU 管淘汰；flush list 管脏页刷盘；free list 管可分配空页。


**关键点：**
- LRU 管淘汰。
- flush list 管脏页刷盘。
- free list 管可分配空页。

</div>
</details>

### 如何管理 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 关注大小配置、命中率、脏页比例和淘汰策略，避免频繁抖动。面试里可按两点展开：监控 `innodb_buffer_pool_*` 指标；结合业务峰值调容量。


**关键点：**
- 监控 `innodb_buffer_pool_*` 指标。
- 结合业务峰值调容量。

</div>
</details>

## 引擎

### 常见 MySQL 引擎

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 生产最常用 InnoDB；MyISAM 早期常见但事务与崩溃恢复能力弱。面试里可按两点展开：InnoDB 支持事务、行锁、外键；MyISAM 偏读场景，维护成本较高。


**关键点：**
- InnoDB 支持事务、行锁、外键。
- MyISAM 偏读场景，维护成本较高。

</div>
</details>

### InnoDB 和 MyISAM 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 重事务与可靠性，MyISAM 更轻但功能较弱。面试里可按三点展开：事务：InnoDB 支持，MyISAM 不支持；锁：InnoDB 行锁，MyISAM 表锁；崩溃恢复：InnoDB 更强。


**关键点：**
- 事务：InnoDB 支持，MyISAM 不支持。
- 锁：InnoDB 行锁，MyISAM 表锁。
- 崩溃恢复：InnoDB 更强。

</div>
</details>

### InnoDB 底层架构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 由 Buffer Pool、redo/undo、doublewrite、后台线程、B+Tree 组织的数据文件等组成。面试里可按两点展开：核心思想：缓存 + 日志 + 后台刷盘；保障目标：性能与可靠性平衡。


**关键点：**
- 核心思想：缓存 + 日志 + 后台刷盘。
- 保障目标：性能与可靠性平衡。

</div>
</details>

### 两个引擎使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 绝大多数 OLTP 业务选 InnoDB；对事务和高并发要求低的历史读多场景才考虑其他引擎。面试里可按两点展开：先看事务/并发/恢复要求；不要只看单次查询速度。


**关键点：**
- 先看事务/并发/恢复要求。
- 不要只看单次查询速度。

</div>
</details>

## MVCC

### 什么是 MVCC，解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MVCC 是多版本并发控制，核心是“读写不互斥”提升并发并保持一致性读。面试里可按两点展开：快照读走版本链；减少读写锁冲突。


**关键点：**
- 快照读走版本链。
- 减少读写锁冲突。

</div>
</details>

### MVCC 如何实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 通过隐藏列（事务 ID、回滚指针）+ undo 版本链 + Read View 可见性规则实现。面试里可按两点展开：每次更新形成新版本；读时按可见性选版本。


**关键点：**
- 每次更新形成新版本。
- 读时按可见性选版本。

</div>
</details>

### 当前读和快照读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 当前读读最新并可能加锁；快照读按 Read View 读历史可见版本。面试里可按两点展开：`select ... for update` 是当前读；普通 `select`（RC/RR）多为快照读。


**关键点：**
- `select ... for update` 是当前读。
- 普通 `select`（RC/RR）多为快照读。

</div>
</details>

### Read View 可见性规则

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 根据事务 ID 与活跃事务列表判断“已提交且可见”还是“不可见需找旧版本”。面试里可按两点展开：事务 ID 越界判断是核心；不可见时沿 undo 链回溯。


**关键点：**
- 事务 ID 越界判断是核心。
- 不可见时沿 undo 链回溯。

</div>
</details>

### 回滚流程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 按 undo 记录反向恢复数据，并清理对应事务状态。面试里可按两点展开：回滚是逻辑层面的逆操作；与崩溃恢复（redo）是两条线。


**关键点：**
- 回滚是逻辑层面的逆操作。
- 与崩溃恢复（redo）是两条线。

</div>
</details>

### RC 和 RR 下 MVCC 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RC 每次查询生成新 Read View；RR 在事务首次快照读时生成并复用 Read View。面试里可按两点展开：RR 一致性更强；RC 更新可见更及时。


**关键点：**
- RR 一致性更强。
- RC 更新可见更及时。
</div>
</details>
