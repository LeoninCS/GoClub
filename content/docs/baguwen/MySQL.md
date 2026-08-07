---
title: "MySQL"
aliases:
  - "/s/4qwj/"
shortlink: "4qwj"
---

# MySQL

这里按基础、索引、事务、锁和日志几个方向整理 MySQL 常见面试题，适合系统梳理数据库知识。

## 基础

### 增删改查的语法

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 核心是 `SELECT/INSERT/UPDATE/DELETE` 四类语句，面试更看你是否会结合条件、排序、分页和事务使用。查询用 `SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT`；插入用 `INSERT INTO ... VALUES ...` 或 `INSERT ... SELECT`；更新用 `UPDATE ... SET ... WHERE ...`；删除用 `DELETE FROM ... WHERE ...`。修改类语句上线前要确认条件、影响行数和事务边界。

**要答的点：**
- `SELECT`：查询数据，常配合过滤、分组、排序、分页。
- `INSERT`：插入单行、多行，或从查询结果写入。
- `UPDATE`：按条件定位行，再用 `SET` 修改列。
- `DELETE`：按条件删除行，核心是控制影响范围。
- 事务：多个修改语句用事务包起来，失败时回滚。
- 安全：线上修改先 `SELECT` 验证条件，再执行修改。

**重点讲解摘录：**
- MySQL 官方把 `SELECT`、`INSERT`、`UPDATE`、`DELETE` 放在 DML 章节。
- `SELECT` 语法覆盖投影、表引用、条件、分组、过滤、排序和分页。
- `UPDATE` 和 `DELETE` 都强依赖 `WHERE` 控制影响行范围。
- `COMMIT` 让事务修改永久生效，`ROLLBACK` 取消当前事务修改。

**原文链接：**
- [MySQL 8.4: Data Manipulation Statements](https://dev.mysql.com/doc/refman/8.4/en/sql-data-manipulation-statements.html)
- [MySQL 8.4: SELECT Statement](https://dev.mysql.com/doc/refman/8.4/en/select.html)
- [MySQL 8.4: INSERT Statement](https://dev.mysql.com/doc/refman/8.4/en/insert.html)
- [MySQL 8.4: UPDATE Statement](https://dev.mysql.com/doc/refman/8.4/en/update.html)
- [MySQL 8.4: DELETE Statement](https://dev.mysql.com/doc/refman/8.4/en/delete.html)

</div>
</details>

### select 语句执行流程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 一条 `SELECT` 进入 MySQL 后，先建立连接并做认证和权限校验；随后 SQL 层完成词法语法解析、语义检查；优化器根据表、索引、统计信息和条件选择执行计划；执行器按计划调用存储引擎接口读取数据；存储引擎负责访问索引页、数据页、Buffer Pool 和锁等底层结构；最后结果返回客户端。面试里按 Server 层和存储引擎层拆开讲最清晰。

**要答的点：**
- 连接层：认证、权限、会话变量、连接管理。
- 解析层：SQL 文本解析成内部结构，检查表和列。
- 优化器：选择索引、连接顺序、访问方式、过滤方式。
- 执行器：按执行计划逐步取数、过滤、聚合、排序。
- 引擎层：InnoDB 负责 B+Tree、Buffer Pool、锁和 MVCC。
- 观察：用 `EXPLAIN` 查看优化器选出的执行计划。

**重点讲解摘录：**
- MySQL 存储引擎架构文档说明 Server 通过统一 API 访问不同引擎。
- `EXPLAIN` 文档说明优化器会结合表、列、索引和条件选择执行计划。
- MySQL 源码文档把 SQL 处理拆成 resolver、optimizer、planner、executor 等模块。
- 面试中可以用 `EXPLAIN` 字段 `type/key/rows/Extra` 说明可观测性。

**原文链接：**
- [MySQL 8.4: Storage Engine Architecture](https://dev.mysql.com/doc/refman/8.4/en/pluggable-storage-overview.html)
- [MySQL 8.4: EXPLAIN Output Format](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [MySQL Source: SQL Optimizer](https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_SQL_Optimizer.html)

</div>
</details>

### SQL 中一行记录如何存储

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 表数据按聚簇索引 B+Tree 组织，叶子页保存完整行记录，默认页大小通常是 16KB。一行记录包含用户列、变长列元信息、NULL 标记，以及 InnoDB 隐藏系统列，例如事务 ID 和回滚指针；如果表没有显式主键，InnoDB 会生成隐藏 row ID。较长的 `VARCHAR/TEXT/BLOB` 在 DYNAMIC 行格式下可放到溢出页，行内保存指针。

**要答的点：**
- 页：InnoDB 数据和索引按页管理，默认页大小 16KB。
- 聚簇索引：主键 B+Tree 叶子节点保存整行。
- 二级索引：叶子保存索引列和主键值。
- 隐藏列：事务 ID、roll pointer 支持 MVCC 和回滚。
- 行格式：COMPACT、DYNAMIC 等影响变长字段布局。
- 溢出页：大字段可能页外存储，行内保存指针。

**重点讲解摘录：**
- InnoDB 行格式文档说明表数据和二级索引都使用 B-tree 结构。
- 聚簇索引记录包含行的全部列值，二级索引记录包含索引列和主键列。
- InnoDB 多版本文档说明聚簇索引记录包含隐藏系统列。
- InnoDB 物理结构文档说明默认 index page 大小由 `innodb_page_size` 决定。

**原文链接：**
- [MySQL 8.4: InnoDB Row Formats](https://dev.mysql.com/doc/refman/8.4/en/innodb-row-format.html)
- [MySQL 8.4: Physical Structure of an InnoDB Index](https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)

</div>
</details>

### 执行 update 会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `UPDATE` 会先经过解析和优化，执行器按执行计划通过索引或扫描定位目标行；InnoDB 对命中记录加锁，生成 undo 记录旧版本，用于回滚和 MVCC；随后在 Buffer Pool 中修改数据页并写 redo log，事务提交时 Server 层写 binlog，InnoDB 通过两阶段提交协调 redo 和 binlog；提交后锁释放，脏页通常由后台线程异步刷盘。

**要答的点：**
- 定位：根据优化器计划走索引或扫描。
- 加锁：更新是当前读，对目标记录或范围加锁。
- undo：保存旧版本，支持回滚和一致性读。
- redo：记录页修改，支持崩溃恢复。
- binlog：记录逻辑变更，用于复制和恢复。
- 提交：两阶段提交保证 redo 与 binlog 一致。

**重点讲解摘录：**
- InnoDB 多版本文档说明记录通过 roll pointer 指向 undo log。
- Binary Log 文档说明事务表修改会在提交时整体写入 binlog。
- MySQL 事务文档说明 `COMMIT` 让当前事务修改永久生效。
- 两阶段提交用于协调存储引擎日志和 Server 层 binlog。

**原文链接：**
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: The Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)
- [MySQL 8.4: COMMIT and ROLLBACK](https://dev.mysql.com/doc/refman/8.4/en/commit.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)

</div>
</details>

## 索引

### 什么是索引？作用和类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 索引是数据库为了加速查询维护的数据结构，本质是用额外存储和写入维护成本换更少的扫描行数。InnoDB 最常见索引结构是 B+Tree，主键索引是聚簇索引，叶子节点保存整行；普通二级索引叶子节点保存索引列和主键值。类型上常见主键索引、唯一索引、普通索引、联合索引、全文索引、空间索引。

**要答的点：**
- 作用：减少扫描行数，加速过滤、排序、分组和连接。
- 代价：占空间，增加插入、更新、删除的维护成本。
- 结构：InnoDB 主流是 B+Tree。
- 类型：主键、唯一、普通、联合、全文、空间。
- 聚簇索引：表数据按主键组织。
- 二级索引：通过主键回到聚簇索引取完整行。

**重点讲解摘录：**
- MySQL 索引文档说明索引用于快速查找特定列值的行。
- InnoDB 索引类型文档说明每个 InnoDB 表都有一个聚簇索引。
- InnoDB 物理结构文档说明索引记录存储在 B-tree 页面中。
- 多列索引文档说明联合索引可用于最左前缀匹配。

**原文链接：**
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)
- [MySQL 8.4: Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)
- [MySQL 8.4: Multiple-Column Indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html)

</div>
</details>

### 如何优化索引

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 索引优化的目标是让高频 SQL 少扫描、少回表、少排序。先用慢查询日志和 `EXPLAIN` 找到问题 SQL，看 `type`、`key`、`rows`、`Extra`；再根据 `WHERE`、`JOIN`、`ORDER BY`、`GROUP BY` 设计联合索引，遵循最左前缀，优先覆盖高频过滤和排序；能覆盖索引就减少回表；同时清理重复索引和低价值索引，控制写入成本。

**要答的点：**
- 定位：慢查询日志 + `EXPLAIN`。
- 过滤：高选择性、高频条件优先。
- 联合索引：按最左前缀和查询模式设计。
- 覆盖索引：查询列都在索引中，减少回表。
- 排序分组：让索引顺序服务 `ORDER BY/GROUP BY`。
- 控制数量：避免重复索引和低区分度单列索引。

**重点讲解摘录：**
- MySQL 官方建议用 `EXPLAIN` 分析查询执行计划。
- 多列索引可按最左前缀加速查询。
- 索引会提高查询速度，同时增加写入和存储成本。
- 优化器是否用索引取决于统计信息、选择性和成本估算。

**原文链接：**
- [MySQL 8.4: EXPLAIN Output](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [MySQL 8.4: Multiple-Column Indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html)
- [MySQL 8.4: Optimization and Indexes](https://dev.mysql.com/doc/refman/8.4/en/optimization-indexes.html)

</div>
</details>

### 什么时候用索引、怎么设计

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 高频查询条件、连接条件、排序分组字段、唯一约束字段适合建索引。设计时先从业务 SQL 出发，把等值过滤列放前面，把范围列和排序列结合起来考虑；联合索引满足最左前缀，尽量覆盖查询列；主键要短、稳定、递增或近似递增，减少二级索引膨胀和页分裂。写多读少、低区分度、频繁更新的大字段要谨慎建索引。

**要答的点：**
- 高频过滤：`WHERE` 常用列优先。
- 连接字段：`JOIN ON` 两边关联列优先。
- 排序分组：服务 `ORDER BY/GROUP BY`。
- 唯一约束：业务唯一字段用 unique index。
- 联合索引：按查询模式设计，覆盖最左前缀。
- 成本：索引越多，写入维护越重。

**重点讲解摘录：**
- MySQL 索引文档说明索引能帮助快速定位行。
- 多列索引文档说明联合索引可用于其左侧前缀列。
- InnoDB 二级索引会保存主键值，主键长度影响二级索引大小。
- 优化器会在可选索引之间按成本选择执行计划。

**原文链接：**
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)
- [MySQL 8.4: Multiple-Column Indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html)
- [MySQL 8.4: Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)

</div>
</details>

### B+ 树结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** B+ 树是多路平衡搜索树，非叶子节点主要保存键和子节点指针，叶子节点保存完整索引记录，叶子节点之间按键顺序连接，适合范围扫描。数据库页通常一次读 16KB，B+ 树一个节点能放很多 key，所以树高很低，查一行通常只需要少量页访问；范围查询时定位到起点叶子页后，可以沿叶子链表顺序扫描。

**要答的点：**
- 多路：一个节点有多个孩子，树高低。
- 平衡：从根到叶子的路径长度一致。
- 非叶：保存键和子指针，用于导航。
- 叶子：保存索引记录，按 key 有序。
- 范围：叶子有序链接，范围扫描友好。
- 页结构：节点对应磁盘页，降低随机 I/O 次数。

**重点讲解摘录：**
- InnoDB 物理结构文档说明索引记录存储在 B-tree 页面中。
- InnoDB 表数据按聚簇索引组织，主键搜索会沿 B-tree 查找。
- B+ 树叶子层有序，适合 `BETWEEN`、`ORDER BY`、范围分页。
- 树高低是数据库索引适合磁盘页模型的重要原因。

**原文链接：**
- [MySQL 8.4: Physical Structure of an InnoDB Index](https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html)
- [MySQL 8.4: Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)

</div>
</details>

### B+ 树 vs B 树、B+ 树 vs 哈希

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** B+ 树相较 B 树，非叶子节点主要做导航，单页能放更多 key，树高更低；数据集中在叶子层，范围扫描更顺。相较哈希索引，B+ 树支持等值、范围、排序、前缀匹配等访问方式；哈希索引适合等值查找，范围查询、排序、最左前缀这类能力较弱。数据库通用 OLTP 场景更依赖 B+ 树。

**要答的点：**
- B+ 树非叶节点更轻，扇出更大。
- B+ 树叶子层有序，范围查询方便。
- B 树数据可能分布在内部节点和叶子节点。
- 哈希等值查找快，范围和排序能力弱。
- B+ 树适配磁盘页和顺序扫描。
- InnoDB 主流索引用 B+Tree，Memory 引擎支持 hash index。

**重点讲解摘录：**
- MySQL 索引文档说明多数 MySQL 索引以 B-tree 存储。
- Memory 引擎默认使用 hash index，也支持 B-tree index。
- B-tree 索引可用于比较、范围和排序优化。
- Hash index 主要用于等值比较。

**原文链接：**
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)
- [MySQL 8.4: Comparison of B-Tree and Hash Indexes](https://dev.mysql.com/doc/refman/8.4/en/index-btree-hash.html)
- [MySQL 8.4: MEMORY Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/memory-storage-engine.html)

</div>
</details>

### 聚簇索引和二级索引

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 聚簇索引决定表数据的物理组织方式，InnoDB 中主键索引的叶子节点保存整行数据；二级索引是主键之外的索引，叶子节点保存二级索引列和对应主键值。通过二级索引查询完整行时，通常先在二级索引中找到主键，再拿主键回聚簇索引取整行，这个过程叫回表。主键越短，所有二级索引占用空间越小。

**要答的点：**
- 聚簇索引：叶子保存整行，表按主键组织。
- 主键选择：优先短、稳定、递增或近似递增。
- 二级索引：叶子保存索引列和主键值。
- 回表：二级索引查主键，再查聚簇索引。
- 覆盖索引：查询列都在二级索引中，可直接返回。
- 影响：主键大小会放大到每个二级索引里。

**重点讲解摘录：**
- InnoDB 索引类型文档说明每个 InnoDB 表都有聚簇索引。
- 二级索引记录包含该行的主键列。
- 聚簇索引让主键查询非常快，因为叶子节点就是数据行。
- 没有合适主键时，InnoDB 会选择或生成隐藏聚簇索引键。

**原文链接：**
- [MySQL 8.4: Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)
- [MySQL 8.4: Physical Structure of an InnoDB Index](https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html)

</div>
</details>

### 什么是回表，优劣势

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 回表是通过二级索引找到主键后，再用主键到聚簇索引中读取完整行的过程。优势是二级索引更小，可以快速过滤候选行；劣势是每个候选行可能多一次聚簇索引查找，随机 I/O 或 Buffer Pool 访问次数增加。优化方式是减少回表次数，例如选择性更好的索引、覆盖索引、延迟关联和控制返回列。

**要答的点：**
- 触发：二级索引命中，但查询列超出索引覆盖范围。
- 流程：二级索引 -> 主键 -> 聚簇索引。
- 优势：用小索引先筛选，提高定位效率。
- 劣势：候选行多时回表成本高。
- 优化：覆盖索引、少查列、先取主键再关联。
- 判断：`EXPLAIN Extra` 出现 `Using index` 通常表示覆盖索引。

**重点讲解摘录：**
- InnoDB 二级索引记录包含主键列，完整行需要通过聚簇索引获取。
- MySQL 覆盖索引可以直接从索引返回所需列。
- `EXPLAIN` 可观察使用索引、扫描行数和额外操作。
- 深分页和低选择性条件常会放大回表成本。

**原文链接：**
- [MySQL 8.4: Clustered and Secondary Indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)
- [MySQL 8.4: EXPLAIN Output](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)

</div>
</details>

### 索引失效场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见索引失效或利用不充分的场景包括联合索引跳过最左列、范围条件后的列利用受限、对索引列做函数或计算、隐式类型转换、`LIKE` 前导通配符、`OR` 条件两边索引条件不对称、低选择性条件被优化器放弃、排序方向或列顺序与索引不匹配。面试里要强调用 `EXPLAIN` 验证，优化器按成本选择计划。

**要答的点：**
- 最左前缀：联合索引从左连续命中。
- 函数计算：`where date(create_time)=...` 影响索引利用。
- 隐式转换：列类型和参数类型保持一致。
- 前导通配符：`LIKE '%abc'` 难以利用普通 B-tree。
- 范围条件：范围列后的索引列利用能力下降。
- 优化器选择：低选择性和统计信息会影响是否使用索引。

**重点讲解摘录：**
- 多列索引文档说明联合索引可用于左侧前缀。
- MySQL 索引文档说明 B-tree 可用于 `=、>、<、BETWEEN、LIKE 'prefix%'` 等条件。
- `EXPLAIN` 可显示实际选择的 key 和扫描行数。
- 函数索引或生成列索引可解决部分表达式查询问题。

**原文链接：**
- [MySQL 8.4: Multiple-Column Indexes](https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html)
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)
- [MySQL 8.4: EXPLAIN Output](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [MySQL 8.4: CREATE INDEX](https://dev.mysql.com/doc/refman/8.4/en/create-index.html)

</div>
</details>

### 如何高效分页

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 深分页要减少大 offset 扫描。`LIMIT 100000, 20` 会让 MySQL 先找到并丢弃前面大量行，再返回目标行；更高效的做法是基于游标分页，例如 `where id > last_id order by id limit 20`，或者先用覆盖索引取主键，再和原表延迟关联取详情。业务允许时用搜索游标、时间游标或上一页最后一条记录作为下一页起点。

**要答的点：**
- 浅分页：`limit offset, size` 简单直接。
- 深分页问题：扫描和丢弃大量行，回表成本高。
- 游标分页：基于 `id`、时间、复合排序键继续查询。
- 延迟关联：子查询先取主键，再回表取详情。
- 覆盖索引：排序和过滤尽量走同一索引。
- 稳定排序：排序字段要唯一或加主键兜底，避免翻页重复/漏数据。

**重点讲解摘录：**
- MySQL `LIMIT` 文档说明可限制返回行数和偏移。
- 优化器对大 offset 仍需处理被跳过的行。
- 覆盖索引可以减少回表数据量。
- 游标分页本质是把“跳过 N 行”变成“从上次位置继续”。

**原文链接：**
- [MySQL 8.4: SELECT Statement](https://dev.mysql.com/doc/refman/8.4/en/select.html)
- [MySQL 8.4: LIMIT Query Optimization](https://dev.mysql.com/doc/refman/8.4/en/limit-optimization.html)
- [MySQL 8.4: How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html)

</div>
</details>

## 事务

### 事务四大特性（ACID）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** ACID 是原子性、一致性、隔离性、持久性。原子性保证事务内操作整体成功或整体回滚，InnoDB 主要靠 undo log；一致性保证数据从一个合法状态转到另一个合法状态，依赖约束、事务机制和业务规则；隔离性控制并发事务之间的可见性，靠锁和 MVCC；持久性保证提交后即使崩溃也能恢复，靠 redo log、刷盘策略和崩溃恢复。

**要答的点：**
- Atomicity：事务操作整体提交或回滚。
- Consistency：约束、业务规则和事务机制保证状态合法。
- Isolation：并发事务互相隔离，靠锁和 MVCC。
- Durability：提交结果持久保存，崩溃后可恢复。
- InnoDB：undo 支持回滚，redo 支持崩溃恢复。
- 面试扩展：四种隔离级别和三类读问题。

**重点讲解摘录：**
- MySQL ACID 文档说明 InnoDB 遵循 ACID 模型。
- `COMMIT` 让当前事务修改永久生效，`ROLLBACK` 取消修改。
- InnoDB 事务模型结合多版本和锁机制处理并发。
- redo log 是 InnoDB 崩溃恢复的重要基础。

**原文链接：**
- [MySQL 8.4: InnoDB and the ACID Model](https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html)
- [MySQL 8.4: COMMIT and ROLLBACK](https://dev.mysql.com/doc/refman/8.4/en/commit.html)
- [MySQL 8.4: InnoDB Transaction Model](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html)

</div>
</details>

### 脏读、不可重复读、幻读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 脏读是一个事务读到了另一个事务尚未提交的数据；不可重复读是同一事务两次读取同一行，结果因为其他事务提交修改而变化；幻读是同一事务按相同条件两次查询，结果集合因为其他事务插入或删除而变化。面试里抓住三个关键词：未提交数据、同一行变化、结果集合变化。

**要答的点：**
- 脏读：读取到其他事务未提交修改。
- 不可重复读：同一行两次读取值发生变化。
- 幻读：同一查询条件下行集合发生变化。
- 隔离级别：隔离越强，这些问题越少。
- InnoDB：MVCC 和锁共同处理读一致性。
- 追问：快照读和当前读在 RR 下表现不同。

**重点讲解摘录：**
- SQL 标准用这些现象定义隔离级别的差异。
- MySQL 隔离级别文档覆盖 READ UNCOMMITTED、READ COMMITTED、REPEATABLE READ、SERIALIZABLE。
- InnoDB 一致性读通过快照读取历史版本。
- 锁定读和更新属于当前读，会看到并锁定最新记录。

**原文链接：**
- [MySQL 8.4: Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)

</div>
</details>

### 事务隔离级别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL/InnoDB 支持四种隔离级别：读未提交、读已提交、可重复读、串行化。读未提交允许读到未提交数据；读已提交每次一致性读使用新的快照；可重复读是 InnoDB 默认级别，同一事务内一致性读使用首次读取建立的快照；串行化会让普通 `SELECT` 也变成加锁读，隔离最强，并发成本最高。

**要答的点：**
- READ UNCOMMITTED：隔离最弱，可能脏读。
- READ COMMITTED：只能读已提交，每条语句一个 Read View。
- REPEATABLE READ：InnoDB 默认，同一事务复用快照。
- SERIALIZABLE：读也加锁，事务近似串行执行。
- 取舍：隔离越强，并发冲突越多。
- 实践：默认 RR 常见，报表或读写冲突场景按业务调整。

**重点讲解摘录：**
- MySQL 文档列出四种 SQL 标准隔离级别。
- InnoDB 默认隔离级别是 REPEATABLE READ。
- READ COMMITTED 下每次一致性读会设置并读取自己的新快照。
- SERIALIZABLE 会把普通 SELECT 转换为锁定读。

**原文链接：**
- [MySQL 8.4: Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [MySQL 8.4: SET TRANSACTION](https://dev.mysql.com/doc/refman/8.4/en/set-transaction.html)

</div>
</details>

### 什么是 Read View

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Read View 是 InnoDB MVCC 做一致性读时生成的可见性快照，用来判断某个行版本对当前事务是否可见。它记录生成快照时活跃事务集合和事务 ID 边界；读取一行时，InnoDB 根据行版本的事务 ID、Read View 边界和活跃事务集合判断版本可见性。不可见时沿 undo 版本链继续找更老版本。

**要答的点：**
- 用途：一致性读的可见性判断。
- 内容：活跃事务 ID 集合、低水位和高水位边界。
- 行版本：聚簇索引记录有事务 ID 和回滚指针。
- 判断：已提交且在快照范围内的版本可见。
- 回溯：当前版本不可见时沿 undo 链找旧版本。
- 隔离：RC 每条语句新建，RR 事务内复用。

**重点讲解摘录：**
- InnoDB 一致性读文档说明查询会看到某个时间点的数据库快照。
- InnoDB 多版本文档说明记录包含事务 ID 和 roll pointer。
- MySQL 源码文档中 `ReadView` 类用于 MVCC 读视图。
- Undo log 保存旧版本，是 Read View 回溯版本链的基础。

**原文链接：**
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL Source: ReadView](https://dev.mysql.com/doc/dev/mysql-server/latest/classReadView.html)

</div>
</details>

### Read View 如何解决读问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Read View 通过“快照 + 版本链”让普通查询读到一个稳定的历史视图。查询开始时创建 Read View，之后读取行时判断最新版本是否对当前视图可见；可见就返回，不可见就沿 undo 链找到更老版本。这样普通 `SELECT` 可以在并发更新时保持一致读，降低读写互相阻塞，也避免读到未提交数据。

**要答的点：**
- 快照：Read View 表示查询或事务开始时的可见范围。
- 版本链：undo log 串起旧版本。
- 可见性：按事务 ID 和活跃事务集合判断。
- 一致读：普通 SELECT 读快照版本。
- 并发：读不阻塞写，写不阻塞一致性读。
- 边界：当前读和锁定读走最新版本和锁机制。

**重点讲解摘录：**
- InnoDB 一致性读是通过多版本提供的快照查询。
- 一致性读不会对读取的表设置锁。
- InnoDB 多版本文档说明旧版本可通过 undo 记录重建。
- 锁定读、UPDATE、DELETE 会读取最新可用版本并加锁。

**原文链接：**
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)

</div>
</details>

### RR 是否完全解决幻读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 的 RR 对普通快照读通过 Read View 保持同一事务内查询结果稳定；对当前读和更新语句，通过 next-key lock 锁住记录和间隙，抑制范围内新插入带来的幻读。面试里要区分快照读和当前读：普通 `SELECT` 主要靠 MVCC；`SELECT ... FOR UPDATE`、`UPDATE`、`DELETE` 这类当前读主要靠记录锁、间隙锁和 next-key lock。

**要答的点：**
- 快照读：同一事务复用 Read View，结果稳定。
- 当前读：读取最新版本，并对范围加锁。
- Next-key lock：记录锁 + 间隙锁。
- 防插入：锁住索引范围内的 gap，限制新记录进入范围。
- 前提：SQL 走合适索引，锁范围与查询条件相关。
- 实践：缺少索引会扩大锁范围，影响并发。

**重点讲解摘录：**
- InnoDB 隔离级别文档说明 RR 使用一致性读。
- InnoDB 锁文档说明 next-key lock 是索引记录锁和其前间隙锁的组合。
- Gap lock 用于防止其他事务向间隙插入记录。
- 锁范围取决于搜索条件和使用的索引。

**原文链接：**
- [MySQL 8.4: Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)

</div>
</details>

### RR 下执行 Update 会发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RR 下 `UPDATE` 是当前读，会读取并修改最新可用版本，按索引条件对目标记录或范围加锁。等值命中唯一索引时通常锁单条记录；范围条件或普通索引可能使用 next-key lock，锁住记录和间隙。更新时会写 undo 旧版本、修改 Buffer Pool 中的数据页、写 redo，并在提交时写 binlog，最后释放事务持有的锁。

**要答的点：**
- 当前读：UPDATE 读取最新版本。
- 加锁：按访问路径加 record lock、gap lock 或 next-key lock。
- 唯一索引：精确命中时锁范围更小。
- 范围条件：可能锁住多个记录和间隙。
- 日志：生成 undo、redo、binlog。
- 并发：其他事务更新同一行会等待或死锁回滚。

**重点讲解摘录：**
- InnoDB 锁文档解释 record lock、gap lock、next-key lock。
- UPDATE 会对扫描到的索引记录设置锁。
- InnoDB 多版本文档说明更新会产生新版本并保留旧版本信息。
- Binary log 在事务提交时记录修改事件。

**原文链接：**
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: UPDATE Statement](https://dev.mysql.com/doc/refman/8.4/en/update.html)

</div>
</details>

## 锁

### MySQL 中有哪些锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL 锁可以按粒度分为全局锁、表级锁、行级锁；按模式分为共享锁 S 和排他锁 X；InnoDB 里还常见意向锁、记录锁、间隙锁、next-key lock、插入意向锁、自增锁、元数据锁 MDL。面试回答先按粒度建立框架，再重点展开 InnoDB 行锁依赖索引、next-key lock 用于范围并发控制。

**要答的点：**
- 全局锁：全库只读，常见于一致性备份语义。
- 表级锁：表读写锁、MDL、意向锁、自增锁。
- 行级锁：record lock、gap lock、next-key lock。
- S/X：共享读锁和排他写锁。
- 意向锁：表级标记，协调表锁和行锁。
- MDL：保护表结构元数据，DDL/DML 会互相影响。

**重点讲解摘录：**
- InnoDB 锁文档列出 shared/exclusive locks、intention locks、record locks、gap locks、next-key locks。
- Metadata locking 文档说明 MySQL 使用 MDL 管理对象元数据并发访问。
- InnoDB 行锁基于索引记录实现，访问路径会影响锁范围。
- 表锁和行锁的取舍是并发能力与管理成本的取舍。

**原文链接：**
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: Metadata Locking](https://dev.mysql.com/doc/refman/8.4/en/metadata-locking.html)
- [MySQL 8.4: LOCK TABLES](https://dev.mysql.com/doc/refman/8.4/en/lock-tables.html)

</div>
</details>

### 全局锁、表级锁、行级锁

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 全局锁影响整个实例，典型命令是 `FLUSH TABLES WITH READ LOCK`，常用于全局一致性备份场景；表级锁锁住整张表，实现简单但并发粒度粗，MyISAM 使用表级锁较多，InnoDB 也有 MDL 和意向锁；行级锁锁住索引记录或范围，InnoDB 通过行锁提供高并发写入能力，但会带来死锁检测和锁范围分析成本。

**要答的点：**
- 全局锁：影响全库写入，适合少数运维场景。
- 表级锁：锁粒度大，管理简单，并发能力较弱。
- 行级锁：粒度小，并发能力强。
- InnoDB：行锁依赖索引，条件和执行计划影响锁范围。
- MDL：DML 和 DDL 之间的元数据保护。
- 选型：线上业务主要依赖 InnoDB 行锁和短事务。

**重点讲解摘录：**
- `FLUSH TABLES WITH READ LOCK` 可关闭打开表并加全局读锁。
- `LOCK TABLES` 提供显式表锁能力。
- InnoDB 支持行级锁，并通过意向锁与表锁协调。
- Metadata lock 在表结构变更和普通查询修改之间自动生效。

**原文链接：**
- [MySQL 8.4: FLUSH TABLES WITH READ LOCK](https://dev.mysql.com/doc/refman/8.4/en/flush.html)
- [MySQL 8.4: LOCK TABLES](https://dev.mysql.com/doc/refman/8.4/en/lock-tables.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: Metadata Locking](https://dev.mysql.com/doc/refman/8.4/en/metadata-locking.html)

</div>
</details>

### 表级锁类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL 常见表级锁包括表读锁、表写锁、元数据锁 MDL、意向锁和自增锁。表读写锁可以通过 `LOCK TABLES` 显式加；MDL 在访问表时自动加，用于保护表结构，DDL 常因为等待 MDL 被阻塞；意向锁是 InnoDB 表级标记，用于说明事务准备在某些行上加 S/X 锁；自增锁用于协调 `AUTO_INCREMENT` 值分配。

**要答的点：**
- 表读锁：允许多个会话读，限制写。
- 表写锁：独占表级写入。
- MDL：保护表元数据，DML/DDL 自动参与。
- 意向锁：IS/IX 标记事务将加行锁。
- 自增锁：协调自增值生成。
- 排查：`performance_schema` 可查看锁等待。

**重点讲解摘录：**
- `LOCK TABLES` 文档说明显式表锁的读写模式。
- Metadata locking 文档说明 DDL 和 DML 都会获取元数据锁。
- InnoDB 意向锁用于表级别表示后续行级锁意图。
- 自增锁模式受 `innodb_autoinc_lock_mode` 控制。

**原文链接：**
- [MySQL 8.4: LOCK TABLES](https://dev.mysql.com/doc/refman/8.4/en/lock-tables.html)
- [MySQL 8.4: Metadata Locking](https://dev.mysql.com/doc/refman/8.4/en/metadata-locking.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: InnoDB AUTO_INCREMENT Handling](https://dev.mysql.com/doc/refman/8.4/en/innodb-auto-increment-handling.html)

</div>
</details>

### 行级锁类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 常见行级锁有记录锁、间隙锁、next-key lock 和插入意向锁。记录锁锁住索引记录本身；间隙锁锁住两个索引记录之间的间隙，控制范围内插入；next-key lock 是记录锁加前一个间隙锁，用于 RR 下范围查询和当前读防幻读；插入意向锁表示事务准备向某个间隙插入记录，多个插入不同位置的事务可以并发。

**要答的点：**
- Record lock：锁索引记录。
- Gap lock：锁索引记录之间的间隙。
- Next-key lock：记录锁 + 间隙锁。
- Insert intention lock：插入前的间隙意向锁。
- 触发：锁定读、UPDATE、DELETE、范围条件。
- 影响：锁范围由索引和执行计划决定。

**重点讲解摘录：**
- InnoDB 锁文档定义 record lock 为索引记录上的锁。
- Gap lock 作用于索引记录之间的间隙。
- Next-key lock 是索引记录锁和其前间隙锁的组合。
- Insert intention lock 用于插入前表示插入意图。

**原文链接：**
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)

</div>
</details>

### 记录锁 + 间隙锁能防删除导致的幻读吗

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 在当前读和范围查询场景下，next-key lock 通过记录锁和间隙锁锁住匹配记录及其相邻间隙，能控制同一索引范围内插入新记录带来的集合变化。删除已经存在的记录本身要拿记录锁，和其他事务的锁会互相约束。面试里要说清前提：SQL 走了合适索引，锁住了目标范围；不同索引和不同条件会导致锁区间变化。

**要答的点：**
- 记录锁：锁住已有索引记录。
- 间隙锁：锁住记录之间的可插入区间。
- Next-key：组合两者控制范围变化。
- 删除：删除现有记录需要对记录加锁。
- 前提：命中正确索引，锁范围覆盖查询条件。
- 实践：用 `EXPLAIN` 和锁等待信息分析实际锁范围。

**重点讲解摘录：**
- InnoDB next-key lock 用于防止 phantom rows。
- Gap lock 可阻止其他事务向间隙插入记录。
- 锁范围基于索引扫描路径，而非单纯 SQL 文本。
- 缺索引会让 InnoDB 扫描更多记录，锁影响范围扩大。

**原文链接：**
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)

</div>
</details>

### MySQL 死锁怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL/InnoDB 发生死锁时，会检测等待环并回滚其中一个事务，让另一个事务继续。业务层要捕获死锁错误并做幂等重试；治理上要缩短事务、统一访问顺序、用合适索引缩小锁范围、减少交互式长事务、避免持锁调用外部服务。排查时看 `SHOW ENGINE INNODB STATUS`、错误日志、`performance_schema` 锁等待信息和慢 SQL。

**要答的点：**
- 处理：InnoDB 自动检测死锁并回滚一个事务。
- 业务：捕获错误，按幂等逻辑重试。
- 预防：短事务、固定顺序、合适索引、减少范围锁。
- 排查：`SHOW ENGINE INNODB STATUS` 查看最近死锁。
- 监控：锁等待、事务时长、慢 SQL、行扫描。
- 工程：把外部 RPC、用户交互放到事务外。

**重点讲解摘录：**
- InnoDB deadlock 文档说明 InnoDB 自动检测事务死锁并回滚一个或多个事务。
- 官方建议应用程序始终准备在死锁时重新发起事务。
- `SHOW ENGINE INNODB STATUS` 可查看最近一次死锁信息。
- 统一访问顺序和短事务是降低死锁概率的常见手段。

**原文链接：**
- [MySQL 8.4: Deadlocks in InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html)
- [MySQL 8.4: How to Minimize and Handle Deadlocks](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)
- [MySQL 8.4: SHOW ENGINE Statement](https://dev.mysql.com/doc/refman/8.4/en/show-engine.html)

</div>
</details>

## 日志

### 三种日志及作用

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB/MySQL 高频三种日志是 undo log、redo log、binlog。undo log 记录旧版本，支持事务回滚和 MVCC；redo log 是 InnoDB 物理重做日志，记录数据页修改，支持崩溃恢复；binlog 是 MySQL Server 层逻辑日志，记录已提交事务的逻辑变更，用于复制、归档和基于时间点恢复。面试里顺着“回滚、一致性读、崩溃恢复、主从复制”讲。

**要答的点：**
- undo：旧版本、回滚、MVCC。
- redo：物理页修改、WAL、崩溃恢复。
- binlog：逻辑变更、复制、审计、恢复。
- 层级：undo/redo 属于 InnoDB，binlog 属于 Server 层。
- 提交：redo 和 binlog 通过两阶段提交协调。
- 刷盘：redo 看 `innodb_flush_log_at_trx_commit`，binlog 看 `sync_binlog`。

**重点讲解摘录：**
- InnoDB undo logs 文档说明 undo 记录用于回滚和一致性读。
- InnoDB redo log 文档说明 redo 用于崩溃恢复。
- Binary Log 文档说明 binlog 记录数据库修改事件。
- 事务提交时，binlog 用于复制和时间点恢复。

**原文链接：**
- [MySQL 8.4: InnoDB Undo Logs](https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html)
- [MySQL 8.4: The InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: The Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)

</div>
</details>

### undo log 结构与回滚

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** undo log 保存数据被修改前的旧版本信息，聚簇索引记录里的 roll pointer 指向 undo 记录，多个旧版本串成版本链。事务回滚时，InnoDB 根据 undo 记录执行反向操作，把数据恢复到事务开始前状态；一致性读时，如果当前版本对 Read View 不可见，也会沿 undo 链重建旧版本。提交后的 undo 会在没有 Read View 需要时由 purge 清理。

**要答的点：**
- 内容：旧值、事务信息、回滚所需信息。
- 指针：行记录 roll pointer 指向 undo。
- 回滚：按 undo 反向恢复修改。
- MVCC：一致性读通过 undo 找历史版本。
- 清理：purge 线程清理无用 undo。
- 成本：长事务会阻碍 undo 清理，拉长版本链。

**重点讲解摘录：**
- InnoDB undo logs 文档说明 undo 用于回滚事务修改。
- InnoDB 多版本文档说明聚簇索引记录包含 roll pointer。
- 旧版本可通过 undo log 重建。
- 长时间一致性读会让旧版本保留更久。

**原文链接：**
- [MySQL 8.4: InnoDB Undo Logs](https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: Purge Configuration](https://dev.mysql.com/doc/refman/8.4/en/innodb-purge-configuration.html)

</div>
</details>

### redo log 什么时候刷盘

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** redo 刷盘主要由 `innodb_flush_log_at_trx_commit` 控制。值为 1 时，每次事务提交都会把 redo log buffer 写入日志文件并刷盘，持久性最好；值为 2 时，每次提交写入日志文件，刷盘通常由后台每秒完成；值为 0 时，写入和刷盘都主要按后台周期进行。生产强一致和主从可靠性场景常配合 `sync_binlog=1` 使用。

**要答的点：**
- redo buffer：事务执行时先写内存日志缓冲。
- 参数 1：提交写入并 fsync，持久性最强。
- 参数 2：提交写文件，后台刷盘。
- 参数 0：后台写入和刷盘。
- 权衡：安全性和吞吐延迟之间取舍。
- 配合：`sync_binlog` 控制 binlog 刷盘。

**重点讲解摘录：**
- MySQL 参数文档解释 `innodb_flush_log_at_trx_commit` 三种取值。
- 默认值 1 可在崩溃时提供最高事务持久性。
- `sync_binlog` 控制 binary log 同步到磁盘的频率。
- 持久性要求高时常用 redo 和 binlog 都每次提交刷盘。

**原文链接：**
- [MySQL 8.4: InnoDB System Variables](https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html)
- [MySQL 8.4: Binary Logging System Variables](https://dev.mysql.com/doc/refman/8.4/en/replication-options-binary-log.html)
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)

</div>
</details>

### redo log 写满怎么办

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** redo log 是循环使用的日志空间，写入推进到可复用空间不足时，InnoDB 需要推进 checkpoint，把相关脏页刷到磁盘，让更早的 redo 空间变成可覆盖状态。写入压力大、脏页多或磁盘慢时，checkpoint 推进跟不上 redo 产生速度，前台事务可能等待刷脏页，表现为写入延迟升高。

**要答的点：**
- 循环写：redo log 空间按逻辑序列推进复用。
- Checkpoint：表示某个点之前的修改已落到数据页。
- 刷脏页：把 Buffer Pool 中脏页写回磁盘。
- 写满影响：前台写入等待可用 redo 空间。
- 优化：增加 redo 容量、优化 I/O、控制脏页比例、提升磁盘能力。
- 监控：checkpoint age、脏页比例、fsync 延迟、写入吞吐。

**重点讲解摘录：**
- InnoDB redo log 文档说明 redo 用于崩溃恢复。
- InnoDB checkpoint 机制会把已持久化的数据页与 redo 可回收空间关联起来。
- Buffer Pool 脏页刷新速度影响 checkpoint 推进。
- redo 容量越小，写入高峰越容易触发频繁 checkpoint。

**原文链接：**
- [MySQL 8.4: The InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: InnoDB Checkpoints](https://dev.mysql.com/doc/refman/8.4/en/innodb-checkpoints.html)
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)

</div>
</details>

### redo log 和 binlog 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** redo log 是 InnoDB 引擎层日志，记录数据页物理修改，用于崩溃恢复，通常循环写；binlog 是 MySQL Server 层日志，记录逻辑变更事件，用于主从复制、审计和时间点恢复，通常追加写。事务提交时二者通过两阶段提交协调，保证崩溃恢复后数据状态和复制日志保持一致。

**要答的点：**
- 层级：redo 属于 InnoDB，binlog 属于 Server。
- 内容：redo 偏物理页修改，binlog 偏逻辑事件。
- 用途：redo 崩溃恢复，binlog 复制和恢复。
- 写法：redo 循环写，binlog 追加写。
- 提交：两阶段提交协调一致性。
- 参数：redo 看 `innodb_flush_log_at_trx_commit`，binlog 看 `sync_binlog`。

**重点讲解摘录：**
- InnoDB redo log 文档说明 redo 记录用于 crash recovery。
- Binary Log 文档说明 binlog 记录数据库修改事件并用于复制。
- InnoDB 支持 XA/两阶段提交来协调 binlog 与存储引擎。
- binlog 有 statement、row、mixed 等格式。

**原文链接：**
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)
- [MySQL 8.4: Binary Log Formats](https://dev.mysql.com/doc/refman/8.4/en/binary-log-formats.html)

</div>
</details>

### 主从复制实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL 复制基于主库 binary log。主库提交事务并写 binlog；从库 I/O 线程连接主库读取 binlog，写入本地 relay log；从库 SQL 线程或多线程 worker 读取 relay log 并重放事件，让从库追上主库。复制默认异步，会存在延迟；半同步复制可以让主库等待至少一个从库确认收到事务，降低主库宕机时的数据丢失窗口。

**要答的点：**
- 主库：写 binlog。
- 从库 I/O：拉取 binlog 写 relay log。
- 从库 SQL：重放 relay log。
- 位点：传统 file/position 或 GTID。
- 延迟：网络、SQL 重放、锁等待、长事务都会造成延迟。
- 增强：半同步、多线程复制、GTID、只读保护。

**重点讲解摘录：**
- MySQL 复制文档说明复制基于源服务器 binary log。
- Relay log 是从库保存来自主库事件的本地日志。
- GTID 为事务提供全局唯一标识，方便故障切换和复制定位。
- 半同步复制要求源库等待副本确认接收事务事件。

**原文链接：**
- [MySQL 8.4: Replication Implementation](https://dev.mysql.com/doc/refman/8.4/en/replication-implementation.html)
- [MySQL 8.4: Replication Threads](https://dev.mysql.com/doc/refman/8.4/en/replication-threads.html)
- [MySQL 8.4: GTID Concepts](https://dev.mysql.com/doc/refman/8.4/en/replication-gtids-concepts.html)
- [MySQL 8.4: Semisynchronous Replication](https://dev.mysql.com/doc/refman/8.4/en/replication-semisync.html)

</div>
</details>

### binlog 什么时候刷盘

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** binlog 刷盘由 `sync_binlog` 控制。`sync_binlog=1` 表示每次事务提交后同步 binary log 到磁盘，崩溃丢失风险最低，性能成本更高；大于 1 表示累计多个提交后同步一次；为 0 时由操作系统决定刷盘时机。强持久性场景常用 `sync_binlog=1` 配合 `innodb_flush_log_at_trx_commit=1`。

**要答的点：**
- binlog cache：事务执行过程中先缓存事件。
- 提交：事务提交时写入 binlog 文件。
- `sync_binlog=1`：每次提交 fsync。
- `sync_binlog=N`：每 N 次提交同步一次。
- `sync_binlog=0`：交给 OS 刷盘策略。
- 取舍：持久性、复制一致性和写入性能。

**重点讲解摘录：**
- MySQL 复制选项文档说明 `sync_binlog` 控制 binary log 同步频率。
- Binary Log 文档说明 binlog 对复制和恢复很关键。
- 强一致配置常同时关注 redo 和 binlog 两个刷盘参数。
- 事务表的事件在提交时写入 binary log。

**原文链接：**
- [MySQL 8.4: Binary Logging Options and Variables](https://dev.mysql.com/doc/refman/8.4/en/replication-options-binary-log.html)
- [MySQL 8.4: The Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)

</div>
</details>

### update 语句执行过程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `UPDATE` 流程可以概括为：连接和权限校验；解析优化生成执行计划；按索引定位记录；InnoDB 对目标记录或范围加锁；生成 undo 旧版本；在 Buffer Pool 修改数据页；写 redo log；提交时写 binlog 并协调两阶段提交；提交成功释放锁；脏页后续由后台刷盘。面试里要突出 WAL 思想：先保证日志持久，再让数据页异步落盘。

**要答的点：**
- SQL 层：解析、优化、执行。
- 引擎层：索引定位、加锁、修改页。
- undo：回滚和 MVCC。
- redo：崩溃恢复和 WAL。
- binlog：复制和恢复。
- 提交：redo prepare -> binlog -> redo commit。

**重点讲解摘录：**
- `UPDATE` 文档定义更新语句语法和行为。
- InnoDB 多版本文档说明更新会维护旧版本。
- Redo log 用于崩溃恢复，binlog 用于复制。
- 两阶段提交让存储引擎日志和 binary log 保持一致。

**原文链接：**
- [MySQL 8.4: UPDATE Statement](https://dev.mysql.com/doc/refman/8.4/en/update.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)

</div>
</details>

### 为什么两阶段提交

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 两阶段提交用于保证 InnoDB redo log 和 Server 层 binlog 在事务提交时保持原子一致。流程是 InnoDB 先把 redo 写到 prepare 状态，Server 写 binlog 并刷盘，然后 InnoDB 写 redo commit。崩溃恢复时，MySQL 可以根据 redo prepare 状态和 binlog 是否存在来决定提交或回滚，避免主库数据和复制日志出现不一致。

**要答的点：**
- 问题：redo 和 binlog 分属不同层。
- 目标：保证本地数据恢复和主从复制一致。
- prepare：redo 记录进入准备提交状态。
- binlog：Server 写入事务事件。
- commit：InnoDB 提交 redo。
- 恢复：崩溃后结合 redo 状态和 binlog 判断事务结局。

**重点讲解摘录：**
- Binary Log 文档说明事务提交时写入 binlog。
- InnoDB 和 binlog 的 XA 协调保证二者同步。
- 两阶段提交解决“一个日志成功、另一个日志缺失”的一致性问题。
- 复制依赖 binlog，本地崩溃恢复依赖 redo。

**原文链接：**
- [MySQL 8.4: The Binary Log](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)
- [MySQL 8.4: XA Transactions](https://dev.mysql.com/doc/refman/8.4/en/xa.html)
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)

</div>
</details>

### 提交时异常重启会怎样

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 提交过程中崩溃后，MySQL 会在重启恢复时检查 redo 状态和 binlog 记录。redo 已 commit 的事务会重做；redo 处于 prepare 状态时，会检查对应 binlog 是否完整存在：binlog 存在则提交，binlog 缺失则回滚。这样恢复后本地数据和复制日志能对齐，减少主从不一致和时间点恢复异常。

**要答的点：**
- redo commit：重启后按 redo 重做。
- redo prepare + binlog 存在：补提交。
- redo prepare + binlog 缺失：回滚。
- undo：用于回滚未提交事务。
- redo：用于恢复已提交或应提交事务。
- 目标：数据文件、redo、binlog 达到一致状态。

**重点讲解摘录：**
- InnoDB 崩溃恢复依赖 redo log 和 undo log。
- Binary log 参与事务提交和复制恢复。
- XA/两阶段提交提供崩溃点判断依据。
- 未提交事务在恢复过程中会通过 undo 回滚。

**原文链接：**
- [MySQL 8.4: InnoDB Recovery](https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html)
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: InnoDB Undo Logs](https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html)
- [MySQL 8.4: XA Transactions](https://dev.mysql.com/doc/refman/8.4/en/xa.html)

</div>
</details>

### MySQL I/O 高如何优化

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL I/O 高要先定位来源，再分层优化。读 I/O 高时看慢 SQL、索引命中、扫描行数、Buffer Pool 命中率和热点数据；写 I/O 高时看 redo/binlog 刷盘、脏页刷新、临时表、批量写入和磁盘能力。优化手段包括优化 SQL 和索引、增加 Buffer Pool、控制大事务、调整刷盘策略、拆分冷热数据、使用 SSD、读写分离和归档历史数据。

**要答的点：**
- 定位：慢查询、`EXPLAIN`、I/O wait、磁盘队列、InnoDB 指标。
- 读优化：索引、覆盖索引、减少全表扫描、扩大 Buffer Pool。
- 写优化：批量提交、控制事务大小、优化 redo/binlog 刷盘。
- 脏页：关注 dirty page ratio 和 checkpoint 压力。
- 临时表：减少 filesort、磁盘临时表和大排序。
- 架构：分库分表、归档、读写分离、硬件升级。

**重点讲解摘录：**
- InnoDB Buffer Pool 缓存表和索引数据，命中率影响读 I/O。
- `EXPLAIN` 可以帮助发现扫描行数和索引选择问题。
- redo 和 binlog 刷盘参数会影响写 I/O 延迟。
- InnoDB 后台刷新脏页会带来持续写 I/O。

**原文链接：**
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [MySQL 8.4: Optimizing InnoDB Disk I/O](https://dev.mysql.com/doc/refman/8.4/en/optimizing-innodb-diskio.html)
- [MySQL 8.4: EXPLAIN Output](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [MySQL 8.4: InnoDB System Variables](https://dev.mysql.com/doc/refman/8.4/en/innodb-parameters.html)

</div>
</details>

## 内存

### 什么是 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Buffer Pool 是 InnoDB 在内存中维护的数据页和索引页缓存区，用来减少磁盘 I/O。查询数据时，InnoDB 会把需要的页读入 Buffer Pool；更新数据时，先修改 Buffer Pool 中的页并标记为脏页，再由后台线程按策略刷回磁盘。Buffer Pool 命中率直接影响 MySQL 性能，是 InnoDB 最重要的内存组件之一。

**要答的点：**
- 缓存对象：数据页、索引页、undo 页、自适应哈希等。
- 读路径：先查 Buffer Pool，缺失时从磁盘读页。
- 写路径：先改内存页，标记脏页，后台刷盘。
- 管理结构：LRU list、free list、flush list。
- 参数：`innodb_buffer_pool_size` 控制大小。
- 影响：命中率、脏页比例、刷盘压力。

**重点讲解摘录：**
- MySQL 文档说明 Buffer Pool 是 InnoDB 缓存表和索引数据的内存区域。
- 频繁访问的数据直接从内存处理，提升查询性能。
- InnoDB 使用 LRU 变体管理 Buffer Pool 页。
- 写入先修改内存页，后续刷盘由后台完成。

**原文链接：**
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [MySQL 8.4: Configuring InnoDB Buffer Pool Size](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool-resize.html)

</div>
</details>

### 为什么要有 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Buffer Pool 的核心价值是把频繁访问的数据页留在内存里，减少磁盘随机 I/O，同时让写入先落到内存页和 redo log，再由后台合并刷脏页。这样读请求可以直接命中缓存，写请求可以通过 WAL 和后台刷盘提高吞吐。它承担了数据库性能中的“缓存层”和“写缓冲层”角色。

**要答的点：**
- 降低读 I/O：热点页命中内存。
- 提升写吞吐：先改内存页，配合 redo 保证持久性。
- 合并写：后台批量刷脏页，减少随机写。
- 支持事务：undo、锁、MVCC 等都围绕页和版本工作。
- 性能关键：Buffer Pool 过小会导致频繁淘汰和磁盘读取。
- 与 redo：Buffer Pool 提性能，redo 保崩溃恢复。

**重点讲解摘录：**
- InnoDB Buffer Pool 文档说明它缓存表和索引数据。
- InnoDB redo log 用于恢复尚未刷到数据文件的已提交修改。
- 脏页异步刷盘让前台事务降低随机写等待。
- Buffer Pool 命中率越高，磁盘读压力越低。

**原文链接：**
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [MySQL 8.4: The InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)
- [MySQL 8.4: Optimizing InnoDB Disk I/O](https://dev.mysql.com/doc/refman/8.4/en/optimizing-innodb-diskio.html)

</div>
</details>

### Buffer Pool 结构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Buffer Pool 由多个缓存页 frame 和对应控制块组成，常见管理链表有 free list、LRU list、flush list。free list 管空闲页；LRU list 管页的冷热和淘汰，InnoDB 使用改进 LRU，把新读入页放到 old 子列表附近，降低全表扫描污染热点缓存；flush list 管脏页，按修改时间和 checkpoint 需求刷盘。

**要答的点：**
- Frame：真正存放页内容的缓存页。
- 控制块：记录页号、表空间、状态、脏标记等元信息。
- Free list：可分配空页。
- LRU list：冷热淘汰和访问管理。
- Flush list：脏页刷盘管理。
- 分区：Buffer Pool 可分为多个 instance 降低竞争。

**重点讲解摘录：**
- InnoDB Buffer Pool 文档说明使用 LRU 算法变体管理页。
- Buffer Pool 被划分为 young 和 old 区域，以降低顺序扫描污染。
- Flush list 关联脏页刷新和 checkpoint 推进。
- 多个 Buffer Pool instances 可以降低并发争用。

**原文链接：**
- [MySQL 8.4: InnoDB Buffer Pool](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool.html)
- [MySQL 8.4: Multiple Buffer Pool Instances](https://dev.mysql.com/doc/refman/8.4/en/innodb-multiple-buffer-pools.html)
- [MySQL 8.4: InnoDB Checkpoints](https://dev.mysql.com/doc/refman/8.4/en/innodb-checkpoints.html)

</div>
</details>

### 如何管理 Buffer Pool

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Buffer Pool 管理重点是大小、命中率、脏页比例、淘汰和刷盘。配置上按机器内存和 MySQL 专用程度设置 `innodb_buffer_pool_size`，大实例可使用多个 instances；运行中关注 `Innodb_buffer_pool_read_requests`、`Innodb_buffer_pool_reads`、脏页比例、页刷新、checkpoint age；问题治理包括优化 SQL 和索引、避免全表扫描污染缓存、控制大事务、调整刷脏参数和提升磁盘能力。

**要答的点：**
- 容量：`innodb_buffer_pool_size` 是核心参数。
- 命中率：逻辑读和物理读对比。
- 脏页：关注 dirty pages 和 flush 压力。
- 淘汰：全表扫描和大查询会挤出热点页。
- 预热：dump/load Buffer Pool 降低重启冷启动影响。
- 调优：结合 SQL、索引、磁盘和业务峰值。

**重点讲解摘录：**
- MySQL 支持在线调整 Buffer Pool 大小。
- Buffer Pool dump/load 可保存和恢复热页信息。
- InnoDB status 和 performance schema 可观察 Buffer Pool 指标。
- Buffer Pool 调优要和查询模式一起看。

**原文链接：**
- [MySQL 8.4: Configuring InnoDB Buffer Pool Size](https://dev.mysql.com/doc/refman/8.4/en/innodb-buffer-pool-resize.html)
- [MySQL 8.4: Saving and Restoring Buffer Pool State](https://dev.mysql.com/doc/refman/8.4/en/innodb-preload-buffer-pool.html)
- [MySQL 8.4: InnoDB Standard Monitor](https://dev.mysql.com/doc/refman/8.4/en/innodb-standard-monitor.html)

</div>
</details>

## 引擎

### 常见 MySQL 引擎

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MySQL 常见存储引擎有 InnoDB、MyISAM、Memory、CSV、Archive、NDB 等。生产 OLTP 业务最常用 InnoDB，它支持事务、行级锁、崩溃恢复、外键和 MVCC；MyISAM 是早期常见引擎，结构简单，表级锁，适合历史遗留和部分只读场景；Memory 把数据放内存，适合临时数据；CSV 便于文件交换；Archive 适合归档追加。

**要答的点：**
- InnoDB：默认主流，事务和并发能力强。
- MyISAM：表级锁，历史读多场景。
- Memory：内存表，重启数据清空。
- CSV：以 CSV 文件存储。
- Archive：压缩归档，追加写。
- 选择：核心业务优先 InnoDB。

**重点讲解摘录：**
- MySQL 存储引擎章节列出可插拔存储引擎架构。
- InnoDB 是通用事务型存储引擎。
- MyISAM 章节描述其存储特性和限制。
- `SHOW ENGINES` 可查看当前实例支持的存储引擎。

**原文链接：**
- [MySQL 8.4: Storage Engines](https://dev.mysql.com/doc/refman/8.4/en/storage-engines.html)
- [MySQL 8.4: InnoDB Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html)
- [MySQL 8.4: MyISAM Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/myisam-storage-engine.html)
- [MySQL 8.4: SHOW ENGINES](https://dev.mysql.com/doc/refman/8.4/en/show-engines.html)

</div>
</details>

### InnoDB 和 MyISAM 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 面向事务和高并发 OLTP，支持事务、行级锁、外键、MVCC 和崩溃恢复；MyISAM 结构更简单，使用表级锁，读多写少历史场景曾经常见。InnoDB 数据按聚簇索引组织，二级索引叶子保存主键；MyISAM 数据和索引分开存储。线上核心业务表通常选 InnoDB，因为它在一致性、恢复和并发控制上更完整。

**要答的点：**
- 事务：InnoDB 支持 ACID。
- 锁：InnoDB 行锁，MyISAM 表锁。
- 外键：InnoDB 支持外键约束。
- 崩溃恢复：InnoDB 通过 redo/undo 恢复。
- 索引组织：InnoDB 聚簇索引，MyISAM 数据索引分离。
- 场景：核心 OLTP 用 InnoDB，历史只读场景可见 MyISAM。

**重点讲解摘录：**
- InnoDB 文档强调事务、提交、回滚和崩溃恢复能力。
- MyISAM 文档描述其表文件和索引文件结构。
- InnoDB 锁文档说明其支持行级锁。
- MySQL 默认存储引擎长期以 InnoDB 为主。

**原文链接：**
- [MySQL 8.4: InnoDB Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html)
- [MySQL 8.4: MyISAM Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/myisam-storage-engine.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)
- [MySQL 8.4: InnoDB and ACID](https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html)

</div>
</details>

### InnoDB 底层架构

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB 底层可以按内存、磁盘、日志、线程四块讲。内存核心是 Buffer Pool、Change Buffer、自适应哈希索引、log buffer；磁盘上有表空间、段、区、页、行，数据按聚簇索引 B+Tree 组织；日志有 undo log、redo log，并和 binlog 协调提交；后台线程负责刷脏页、purge undo、checkpoint 和 I/O。核心思想是缓存加 WAL 加后台刷盘，在性能和可靠性之间平衡。

**要答的点：**
- 内存：Buffer Pool、log buffer、change buffer、AHI。
- 存储：tablespace、segment、extent、page、row。
- 索引：聚簇索引和二级索引 B+Tree。
- 日志：undo 回滚/MVCC，redo 崩溃恢复。
- 线程：page cleaner、purge、I/O threads。
- 事务：锁、MVCC、隔离级别、两阶段提交。

**重点讲解摘录：**
- InnoDB 架构文档描述内存结构和磁盘结构。
- Buffer Pool 缓存表和索引数据。
- Redo log 支持崩溃恢复，undo log 支持回滚和历史版本。
- InnoDB 以页为基本 I/O 和缓存单位。

**原文链接：**
- [MySQL 8.4: InnoDB Architecture](https://dev.mysql.com/doc/refman/8.4/en/innodb-architecture.html)
- [MySQL 8.4: InnoDB In-Memory Structures](https://dev.mysql.com/doc/refman/8.4/en/innodb-in-memory-structures.html)
- [MySQL 8.4: InnoDB On-Disk Structures](https://dev.mysql.com/doc/refman/8.4/en/innodb-on-disk-structures.html)
- [MySQL 8.4: InnoDB Redo Log](https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html)

</div>
</details>

### 两个引擎使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 大多数线上业务选 InnoDB，尤其订单、支付、账户、库存、用户资料这类需要事务、一致性、并发和崩溃恢复的表。MyISAM 更适合历史遗留、低并发、读多写少、事务要求很弱的场景。面试里建议把 InnoDB 作为默认答案，再说明选择引擎要看事务、并发、恢复、索引、写入模式和运维成本。

**要答的点：**
- InnoDB：核心 OLTP、高并发读写、事务一致性。
- MyISAM：历史只读/低并发/简单查询场景。
- Memory：临时表、会话级中间结果。
- Archive：日志归档和追加写。
- 选择维度：事务、锁粒度、恢复能力、读写比例、数据安全。
- 生产建议：核心业务表优先 InnoDB。

**重点讲解摘录：**
- InnoDB 是 MySQL 的通用事务型存储引擎。
- MyISAM 在事务和崩溃恢复能力上较弱，表级锁限制写并发。
- Memory 引擎数据存储在内存中，服务重启后数据消失。
- Archive 引擎面向高压缩的归档存储。

**原文链接：**
- [MySQL 8.4: InnoDB Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html)
- [MySQL 8.4: MyISAM Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/myisam-storage-engine.html)
- [MySQL 8.4: MEMORY Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/memory-storage-engine.html)
- [MySQL 8.4: ARCHIVE Storage Engine](https://dev.mysql.com/doc/refman/8.4/en/archive-storage-engine.html)

</div>
</details>

## MVCC

### 什么是 MVCC，解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** MVCC 是多版本并发控制，InnoDB 为同一行保留多个历史版本，让普通查询可以读取符合 Read View 的历史版本，而写事务继续修改最新版本。它解决的核心问题是提高并发下的一致性读能力，让读写冲突减少，同时避免普通查询读到未提交数据。InnoDB 的 MVCC 依赖隐藏事务 ID、roll pointer、undo 版本链和 Read View。

**要答的点：**
- 多版本：同一行存在当前版本和历史版本。
- 一致性读：普通 SELECT 读快照版本。
- 降低冲突：读写可并发进行。
- 组成：隐藏列、undo log、Read View。
- 隔离：RC 和 RR 下 Read View 创建时机不同。
- 边界：当前读仍需要锁控制最新数据。

**重点讲解摘录：**
- InnoDB 多版本文档说明每行记录包含事务 ID 和 roll pointer。
- 一致性读文档说明查询看到某个时间点的快照。
- Undo log 可用于重建旧版本。
- MVCC 与锁共同实现 InnoDB 事务隔离。

**原文链接：**
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Transaction Model](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html)

</div>
</details>

### MVCC 如何实现

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** InnoDB MVCC 由隐藏列、undo 版本链和 Read View 实现。每行聚簇索引记录带有最近修改它的事务 ID 和回滚指针；更新行时，新版本写到数据页，旧版本信息写入 undo log，并通过 roll pointer 串起来；普通查询创建 Read View 后，按版本事务 ID 判断当前版本可见性，可见就返回，不可见就沿 undo 链找旧版本。

**要答的点：**
- 隐藏列：事务 ID 和 roll pointer。
- 更新：生成新版本，旧版本进 undo。
- 版本链：roll pointer 串起历史版本。
- Read View：记录可见性边界和活跃事务。
- 查询：按规则选择可见版本。
- 清理：purge 清理无用历史版本。

**重点讲解摘录：**
- InnoDB 多版本文档说明聚簇索引记录有隐藏系统列。
- Roll pointer 指向 undo log record，旧版本可由 undo 重建。
- 一致性读通过快照查看历史版本。
- Purge 负责清理不再需要的 undo 版本。

**原文链接：**
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL 8.4: InnoDB Undo Logs](https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html)
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)

</div>
</details>

### 当前读和快照读

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 快照读是普通一致性读，读取 Read View 下可见的历史版本，常见于普通 `SELECT`；当前读读取最新可用版本，并可能加锁，常见于 `SELECT ... FOR UPDATE`、`SELECT ... FOR SHARE`、`UPDATE`、`DELETE`、`INSERT`。快照读靠 MVCC 降低读写冲突，当前读靠锁保证读到并保护即将修改的数据。

**要答的点：**
- 快照读：普通 SELECT，一致性视图。
- 当前读：锁定读和写操作，读取最新版本。
- 快照读机制：Read View + undo 版本链。
- 当前读机制：record/gap/next-key lock。
- RC：每条快照读一个 Read View。
- RR：事务首次快照读创建并复用 Read View。

**重点讲解摘录：**
- Consistent read 文档说明 InnoDB 使用快照为查询提供一致性读。
- Locking reads 文档说明 `FOR SHARE` 和 `FOR UPDATE` 会设置锁。
- UPDATE 和 DELETE 需要读取并锁定待修改记录。
- 当前读常用于先查再改、防止并发修改。

**原文链接：**
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)
- [MySQL 8.4: InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)

</div>
</details>

### Read View 可见性规则

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Read View 可见性规则围绕版本的事务 ID 判断。当前事务自己修改的版本可见；版本事务 ID 小于 Read View 低水位，表示创建快照前已提交，通常可见；版本事务 ID 大于等于高水位，表示快照创建后才出现，通常不可见；版本事务 ID 落在中间时，要看它是否在活跃事务集合里，活跃则不可见，已提交则可见。不可见时沿 undo 链找更老版本。

**要答的点：**
- 自己事务：自己改的版本可见。
- 小于低水位：快照前已提交，可见。
- 大于等于高水位：快照后出现，隐藏。
- 中间范围：查活跃事务 ID 集合。
- 活跃事务：创建快照时尚未提交，隐藏。
- 回溯：不可见版本沿 undo 链继续找。

**重点讲解摘录：**
- InnoDB 一致性读文档说明查询读取某个时间点的数据库快照。
- InnoDB 多版本文档说明行版本带事务 ID，旧版本由 undo 重建。
- MySQL 源码 `ReadView` 类实现事务可见性判断。
- RC 与 RR 的关键差异在 Read View 创建和复用时机。

**原文链接：**
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html)
- [MySQL Source: ReadView](https://dev.mysql.com/doc/dev/mysql-server/latest/classReadView.html)

</div>
</details>

### 回滚流程

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 事务回滚时，InnoDB 根据 undo log 中保存的旧版本和反向操作信息，把事务已经修改的数据恢复回去。例如 insert 的回滚是删除插入记录，delete 的回滚是恢复记录，update 的回滚是恢复旧值。回滚本身也会产生 redo，保证回滚过程崩溃后仍可继续恢复。完成后释放事务锁，后续 purge 在安全时机清理无用 undo。

**要答的点：**
- 依据：undo log 保存回滚所需信息。
- insert undo：回滚时删除新插入记录。
- update undo：回滚时恢复旧值或删除标记。
- redo：回滚动作也需要崩溃恢复保障。
- 锁释放：事务结束后释放持有锁。
- 清理：purge 清理无用历史版本。

**重点讲解摘录：**
- Undo logs 文档说明 undo 记录用于回滚事务修改。
- InnoDB 崩溃恢复会处理未提交事务的回滚。
- Purge 线程会删除不再需要的 undo log。
- 长事务会延迟 purge，导致 undo 保留时间变长。

**原文链接：**
- [MySQL 8.4: InnoDB Undo Logs](https://dev.mysql.com/doc/refman/8.4/en/innodb-undo-logs.html)
- [MySQL 8.4: InnoDB Recovery](https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html)
- [MySQL 8.4: Purge Configuration](https://dev.mysql.com/doc/refman/8.4/en/innodb-purge-configuration.html)

</div>
</details>

### RC 和 RR 下 MVCC 区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RC 和 RR 的 MVCC 核心差异是 Read View 创建时机。READ COMMITTED 下，每条一致性读语句都会创建新的 Read View，所以同一事务中后续查询可以看到其他事务已提交的新结果；REPEATABLE READ 下，事务第一次一致性读创建 Read View，后续一致性读复用它，所以同一事务内普通查询结果稳定。当前读仍读取最新版本并加锁。

**要答的点：**
- RC：每条语句一个 Read View。
- RR：事务首次快照读创建并复用 Read View。
- 可见性：RC 更及时看到新提交，RR 一致性更稳定。
- 默认：InnoDB 默认 RR。
- 当前读：两者都读取最新版本并加锁。
- 影响：报表一致性、并发更新和幻读处理方式不同。

**重点讲解摘录：**
- InnoDB 隔离级别文档说明 RC 下每次一致性读都设置自己的新快照。
- RR 是 InnoDB 默认隔离级别。
- 一致性读文档说明同一事务内快照如何提供稳定视图。
- 当前读和锁定读遵循锁机制，不按普通快照读方式返回。

**原文链接：**
- [MySQL 8.4: Transaction Isolation Levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [MySQL 8.4: Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [MySQL 8.4: InnoDB Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)

</div>
</details>
