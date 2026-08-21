---
title: "krypton-深信服Golang"
slug: "krypton-sangfor-golang"
aliases:
  - "/docs/interview/zhongchang/krypton-深信服Golang/"
  - "/s/9vh4/"
shortlink: "9vh4"
---

# 深信服Golang

1. 第一个 PR 修复了什么问题？
2. SQLite 数据库有了解吗？
3. 用的什么数据库比较多？
4. MySQL 性能调优
5. MySQL 事务包含哪几个方面？
6. Redis 有哪几种数据类型？
7. ZSet 底层结构
8. 单线程 IO 模型是怎么样的？
9. Redis 怎么保证原子性？通过什么操作保证原子性？
10. GMP 模型是怎么样的？
11. Channel 的底层数据结构
12. Skill 二级渐进式暴露
13. MCP
14. 在项目当中你怎么体现你的 Prompt 工程能力
15. B 分支 merge A 分支的代码出现了问题怎么做？回滚命令
16. Git 查看提交记录
17. Git 暂存
18. 项目怎么部署的？
19. 项目挂了怎么办？会有重启吗？
20. Go 写项目的时候有用到什么框架？
21. Gin 框架是做什么？在项目中起到什么作用？Gin 一般用在什么场景下？

## 参考答案（AI 生成）

> 以下答案由 AI 生成，仅供面试复盘参考。

### 1. 第一个 PR 修复了什么问题？

答：结合实际情况说明，如修复了某个 bug（空指针、并发问题、数据不一致等），或优化了某段逻辑、补充了单元测试等。重点是讲清楚问题根因、修复方案和影响范围。

### 2. SQLite 数据库有了解吗？

答：SQLite 是嵌入式关系型数据库，无需独立服务进程，数据存为单个文件。适合移动端、桌面应用、小型服务等场景。不支持高并发写入，不适合分布式或大规模 Web 服务。

### 3. 用的什么数据库比较多？

答：结合实际回答。一般后端开发以 MySQL/PostgreSQL 为主，缓存用 Redis，搜索用 Elasticsearch，有时序场景用 TDengine/InfluxDB 等。

### 4. MySQL 性能调优

答：从几个维度入手：SQL 优化（explain 分析执行计划、索引覆盖、避免回表）、索引优化（联合索引最左前缀、避免索引失效）、表结构优化（合理字段类型、垂直/水平拆分）、配置调优（buffer pool、连接数）、读写分离和分库分表。

### 5. MySQL 事务包含哪几个方面？

答：ACID 四大特性：原子性（undo log 回滚）、一致性（约束 + 业务逻辑）、隔离性（MVCC + 锁机制、四个隔离级别）、持久性（redo log + binlog 保证落盘）。

### 6. Redis 有哪几种数据类型？

答：String、Hash、List、Set、ZSet。扩展类型：Bitmap、HyperLogLog、GEO、Stream、Bitfield。

### 7. ZSet 底层结构

答：ZSet 采用 dict + skiplist（跳表）实现。dict 按 member 快速定位 score，skiplist 按 score 有序排列，支持范围查询和排名。数据量小时使用 listpack 紧凑存储以节省内存。

### 8. 单线程 IO 模型是怎么样的？

答：Redis 使用 I/O 多路复用（epoll/kqueue）单线程处理命令。主线程循环监听多个 socket，将就绪事件加入事件队列，按序执行命令。单线程避免了锁竞争和上下文切换开销，命令天然原子性。

### 9. Redis 怎么保证原子性？通过什么操作保证原子性？

答：单线程执行命令保证单条命令原子性。多条命令用 Lua 脚本（EVAL）或事务（MULTI/EXEC）保证原子性，管道化（Pipeline）不保证原子性，只减少 RTT。

### 10. GMP 模型是怎么样的？

答：G（Goroutine）：用户态轻量协程。M（Machine）：OS 线程，实际执行载体。P（Processor）：逻辑处理器，持有本地任务队列，数量由 GOMAXPROCS 决定。M 绑定 P 后才能执行 G，work stealing 实现负载均衡，handoff 避免 M 阻塞时 P 闲置。

### 11. Channel 的底层数据结构

答：Channel 底层是 hchan 结构体，包含环形队列 buf、发送/接收等待队列（sudog）、锁 mutex、元素计数和大小等字段。无缓冲 channel 直接传递，有缓冲 channel 通过环形队列暂存。

### 12. Skill 二级渐进式暴露

答：一级是 Skill 的简要描述和触发条件，让模型只看到摘要；二级是 Skill 的完整指令内容，仅在匹配触发后展开。这样既节省上下文，又保证 Skill 只在需要时完整加载，避免无关指令干扰。

### 13. MCP

答：MCP（Model Context Protocol）是 Anthropic 发布的模型上下文协议，定义了 AI 模型与外部工具/数据源的标准化交互方式。包含 Server（能力提供方）和 Client（消费方），通过 JSON-RPC 通信，支持 Resources、Tools、Prompts 等原语。

### 14. 在项目当中你怎么体现你的 Prompt 工程能力

答：结合实际项目说明，如设计 System Prompt 约束模型输出格式、编写 Few-shot 示例引导回答风格、使用 Chain-of-Thought 提升推理准确性、控制 token 消耗和缓存命中率等。

### 15. B 分支 merge A 分支的代码出现了问题怎么做？回滚命令

答：如果 merge 未 push，用 `git reset --hard HEAD~1` 回退；如果已 push，用 `git revert -m 1 <merge_commit_hash>` 生成反向提交。冲突时 `git merge --abort` 取消本次合并。

### 16. Git 查看提交记录

答：`git log` 查看提交历史，常用参数：`--oneline` 简洁模式、`--graph` 图形化分支、`--author` 按作者过滤、`--since/--until` 时间范围过滤。

### 17. Git 暂存

答：`git stash` 暂存当前工作区修改，`git stash pop` 恢复最近一次暂存，`git stash list` 查看暂存列表，`git stash drop` 删除暂存。

### 18. 项目怎么部署的？

答：结合实际回答。常见方式：Jenkins/GitLab CI 触发构建 → 编译打包 → Docker 镜像构建 → 推送镜像仓库 → K8s 滚动更新或蓝绿部署。简单项目可能用 Docker Compose 或直接 Supervisor + 二进制部署。

### 19. 项目挂了怎么办？会有重启吗？

答：K8s 通过 liveness probe 检测容器健康状态，挂了自动重启 Pod；Supervisor/systemd 守护进程，进程崩溃自动拉起；Docker 使用 `--restart=always` 策略。同时配合告警通知，持久化日志方便排查。

### 20. Go 写项目的时候有用到什么框架？

答：结合实际回答。Web 框架常用 Gin/Echo/Fiber，ORM 用 GORM/Ent，RPC 用 gRPC/go-zero 等。

### 21. Gin 框架是做什么？在项目中起到什么作用？Gin 一般用在什么场景下？

答：Gin 是 Go 的高性能 HTTP Web 框架，提供路由分组、中间件链、参数绑定、请求校验、渲染输出等功能。在项目中作为 HTTP 入口层，处理路由分发、鉴权、日志、限流等横切关注点。适用于 RESTful API、微服务网关、反向代理、静态资源服务等场景。
