---
title: "CC-货拉拉大数据一面"
slug: "cc-huolala-bigdata-1"
weight: 90
aliases:
  - "/s/orqs/"
shortlink: "orqs"
---

# 货拉拉一面

> 方向：大数据 / 后端 / 系统设计。
>
> 本文记录面试真题，参考答案仅用于复习，实际回答应结合自己的技术栈和项目经历调整。

## 一、系统设计题：统一文件存储（网盘）系统

设计一个类似网盘的服务，统一管理云盘、本地盘、HDFS 等底层存储中的大量小文件，支持目录归类、跨存储搜索和打包下载。

### 1. 数据库表结构怎么设计？

可以按“存储系统、目录、文件元数据”拆分：

| 表 | 核心字段 | 作用 |
| --- | --- | --- |
| `storage_systems` | `id`、`name`、`type`、`endpoint`、`status` | 记录云盘、本地盘、HDFS 等存储系统 |
| `directories` | `id`、`storage_id`、`parent_id`、`name`、`path` | 记录目录树，`parent_id` 指向父目录 |
| `files` | `id`、`directory_id`、`storage_id`、`name`、`object_key`、`size`、`hash`、`mime_type`、`updated_at` | 记录文件位置和展示、搜索所需的元数据 |

文件表里保存 `directory_id`，因为一个目录下可以有很多文件；如果把文件 ID 列表放在目录表中，会造成字段膨胀、更新困难，也不利于索引。目录树可以先用邻接表（`parent_id`）实现，层级查询复杂时再增加物化路径或闭包表。

如果同一个逻辑文件可能同时存在多个物理存储，可以再增加 `file_sources` 表，把 `file_id` 和多个 `storage_id/object_key` 关联起来。

### 2. 整体架构如何拆分？

可以拆成以下模块：

```text
客户端 → API 网关 → 文件元数据服务 → MySQL
                         ↓
                   存储适配器层 → 云盘 / 本地盘 / HDFS
                         ↓
              变更事件 → 消息队列 → 搜索索引服务 → Elasticsearch

客户端 → 下载服务 → 打包任务调度 → 文件读取 Worker → ZIP 临时文件 / 对象存储
```

- **元数据服务**：负责目录、文件信息、权限和状态管理。
- **存储适配器层**：屏蔽不同存储系统的 API 差异。
- **搜索服务**：消费文件新增、修改、删除事件，维护统一索引。
- **下载服务**：负责权限校验、任务拆分、并发读取和 ZIP 输出。
- **任务与消息模块**：承载索引同步、批量扫描和大文件打包等异步任务。

### 3. 关键接口和抽象类有哪些？

Go 中通常使用 interface 表达抽象：

```go
type StorageAdapter interface {
    List(ctx context.Context, path string) ([]Object, error)
    Stat(ctx context.Context, objectKey string) (Object, error)
    Open(ctx context.Context, objectKey string) (io.ReadCloser, error)
}

type FileRepository interface {
    Find(ctx context.Context, query FileQuery) ([]File, error)
    Save(ctx context.Context, file File) error
    Delete(ctx context.Context, fileID int64) error
}
```

此外还可以抽象 `DirectoryService`、`SearchService`、`DownloadJobService` 和 `ZipWriter`。`StorageAdapter` 的不同实现分别对应对象存储、本地文件系统和 HDFS。

### 4. 会用到哪些设计模式？

- **适配器模式**：把不同存储系统的 SDK 适配成统一的 `StorageAdapter`。
- **工厂模式**：根据 `storage_systems.type` 创建对应适配器。
- **策略模式**：切换不同的搜索、目录遍历或 ZIP 读取策略。
- **仓储模式**：封装 MySQL 查询，隔离业务层和持久化细节。
- **观察者 / 事件驱动**：文件发生变化时发布事件，由索引服务异步消费。

### 5. 如何实现跨存储系统搜索？为什么使用搜索引擎？

把文件名、路径、扩展名、大小、更新时间、存储系统 ID 等元数据写入 Elasticsearch，查询时由搜索服务统一检索，再根据文件 ID 回查 MySQL 获取最新权限和状态。

不直接查 MySQL 的主要原因是：文件名和路径通常需要分词、前缀或模糊匹配，跨多个字段筛选时搜索引擎的倒排索引更合适；MySQL 适合保存强一致的元数据，不适合承载复杂全文搜索和高并发搜索流量。

同步流程可以这样做：

1. 文件新增、修改、删除时，在事务中记录 Outbox 事件，后台可靠投递到消息队列。
2. 索引消费者按 `file_id` 幂等 upsert 或删除 Elasticsearch 文档，并保存事件版本号。
3. 对已有存量文件执行全量扫描，之后通过增量事件保持更新。
4. 搜索结果标记索引时间或版本；对刚写入但尚未索引的数据，必要时回查 MySQL，降低短暂延迟带来的不可见问题。

### 6. 不同文件系统的文件如何打包成 ZIP？

1. 客户端提交文件 ID 或目录 ID，下载服务校验权限、文件是否存在以及总大小和数量限制。
2. 服务根据元数据把文件分组，并为每个文件选择对应的 `StorageAdapter`。
3. 小任务可以直接流式写 HTTP 响应；大任务创建异步任务，后台生成 ZIP 并保存到临时对象存储。
4. Worker 读取文件流后交给 ZIP Writer，写入时使用用户看到的相对路径，避免把底层存储的真实路径暴露出去。
5. 生成完成后更新任务状态，返回临时下载地址；失败时记录失败文件并支持重试，任务过期后清理临时文件。

ZIP Writer 只能由一个顺序写入方操作，因此读取可以并发，但最终写 ZIP 需要通过有界队列串行写入。全流程使用流式读写，不能把所有文件一次性加载到内存；文件很多时要使用 ZIP64 格式。

### 7. 异步下载场景还有哪些优化？

- 按存储类型、存储实例或 endpoint 分组，复用连接并调用批量读取接口，减少网络往返。
- 每组使用有界 Worker Pool，并设置超时、限流和队列长度，避免并发打满某个底层存储。
- 读取和 ZIP 写入之间增加有界缓冲，利用背压控制内存；对大文件采用流式传输，不落本地或只使用分片临时文件。
- 已经压缩过的文件可以降低 ZIP 压缩级别，减少 CPU 消耗；可提前读取下一个文件，尽量隐藏网络延迟。
- 对重复下载的文件或常用目录缓存已生成的 ZIP；任务使用幂等键，失败只重试失败分片，并记录进度。
