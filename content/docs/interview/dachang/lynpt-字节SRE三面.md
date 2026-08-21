---
title: "lynpt字节SRE三面"
weight: 25
slug: "lynpt-bytedance-sre-3"
aliases:
  - "/docs/interview/dachang/lynpt-字节SRE三面/"
  - "/s/sdgr/"
shortlink: "sdgr"
---

# lynpt 字节 SRE 三面

> 根据口述整理，岗位方向为 SRE。整体考察重点是项目动机、容器与云原生、Python 并发模型、网络基础、排障方法和现场算法。

## 面试画像

这场三面从项目真实性和工程选择切入，持续追问 OJ 系统为什么自研、DinD 难点、部署方式和云上经验。基础题集中在 Docker / K8s、Python GIL、goroutine、网络与 Linux 排障，最后用验证二叉搜索树检查数据结构和递归边界处理。

## 完整题目

1. 自我介绍。
2. 你的 OJ 系统是大作业，还是有实际应用需求？
3. 自研 OJ 相比开源平台或 LeetCode 类现成平台的价值是什么？
4. 在这个项目中你遇到的最大难点是什么？（回答 DinD）
5. 部署是上云了，还是物理主机？（回答第二个项目的上云）
6. Docker 和 K8s 的区别？
7. 你对 Python 了解到什么程度？
8. Python 多线程能力受什么限制？
9. Goroutine 和线程的区别？
10. 你对大数据方面的了解是什么？
11. 你的常用编程语言？
12. Socket、TCP、UDP 分别能解决什么问题？
13. Java 你平时用得多吗？
14. 写代码 debug 时，你常用的 troubleshooting 工具或方案？（分别讲 Docker、Go、Python）
15. Linux 端口被打满了应该如何排查？
16. 算法：检验是否二叉搜索树。

## 参考答案（AI 生成）

> 以下答案由 AI 生成，仅供面试复盘参考。

## 项目与云原生

### 自我介绍怎么讲

**可直接说：** 我主要做后端和云原生方向，常用 Go 和 Python。项目上做过 OJ 系统和一个云上部署项目，OJ 重点在判题隔离、容器执行和资源控制，云上项目重点在服务部署、域名反代、日志和基础运维。我的准备方向和岗位匹配点是后端工程能力、容器化实践、Linux 排障和持续学习能力。

### OJ 项目是大作业还是实际需求

**可直接说：** 这个 OJ 的起点是课程项目，后续按真实应用需求继续完善。它解决的是代码提交、隔离执行、结果判定和资源限制这条完整链路，工程上有用户提交、任务调度、判题容器、结果回传和异常处理。

回答时可以强调：

1. 课程项目提供了明确场景和交付目标。
2. 后续实现按真实 OJ 的核心链路推进。
3. 项目价值在于把容器隔离、并发任务、资源限制和安全边界做成可运行系统。

### 自研 OJ 的价值怎么讲

**可直接说：** 开源平台适合快速搭建，自研 OJ 的价值是掌握判题系统的核心链路和工程取舍。比如代码如何进入沙箱、容器如何限制 CPU 和内存、判题进程如何回收、异常提交如何处理，这些细节都能变成项目深挖点。

可以补充这几个点：

1. 自研能体现个人对系统架构的理解。
2. 判题隔离和资源控制适合展示容器能力。
3. 任务队列、超时控制、结果状态机适合展示后端工程能力。
4. 开源平台可以作为设计参考和对照基准。

### DinD 难点怎么讲

**可直接说：** DinD 最大难点是容器里再管理容器时，安全隔离、权限、cgroup、文件系统和网络都会变复杂。判题场景需要把用户代码放进隔离环境运行，所以我重点关注容器权限、资源限制、超时回收和异常清理。

可以展开为：

1. 权限：Docker daemon 通常需要较高权限，配置要控制风险。
2. 资源：CPU、内存、进程数和运行时间都要被限制。
3. 文件系统：每次判题要准备代码、输入输出文件和临时目录，并在结束后清理。
4. 网络：判题容器通常需要限制网络访问，减少恶意代码影响范围。
5. 回收：编译失败、运行超时、进程残留都要有兜底清理逻辑。

### 部署方式怎么回答

**可直接说：** 我会把两个项目分开讲。OJ 项目更关注判题容器和宿主机资源隔离；第二个项目有上云部署经历，涉及云服务器、域名、Nginx 反向代理、容器部署、日志查看和基础监控。

这类问题要主动补齐：

1. 服务部署在哪里。
2. 请求链路怎么进入后端。
3. 日志和错误怎么查看。
4. 配置、镜像和数据怎么管理。
5. 出问题时怎么回滚或重启。

### Docker 和 K8s 的区别

**可直接说：** Docker 主要解决单机容器构建、运行和镜像管理；K8s 主要解决多节点容器编排、调度、服务发现、扩缩容、滚动发布和自愈。

可以按层次回答：

1. Docker：镜像、容器、网络、卷、单机生命周期。
2. K8s：Pod、Deployment、Service、Ingress、ConfigMap、Secret。
3. Docker 更像运行时和打包工具。
4. K8s 更像集群操作系统，负责把声明式配置维持成目标状态。

## 编程语言与并发

### Python 了解到什么程度

**可直接说：** 我熟悉 Python 基础语法、常用标准库、虚拟环境和包管理，能用它写脚本、爬取处理数据、做简单 Web 服务和自动化工具。工程上我会关注异常处理、日志、依赖管理、单元测试和性能分析。

可以补充：

1. 常用 `list`、`dict`、生成器、装饰器和上下文管理器。
2. 常用 `requests`、`json`、`pathlib`、`logging`、`pytest`。
3. 排查会用 `pdb`、日志、`cProfile`、`tracemalloc`。

### Python 多线程能力受什么限制

**可直接说：** CPython 的 `threading` 提供并发能力，GIL 会让同一进程同一时刻通常只有一个线程执行 Python 字节码。因此 Python 线程适合 I/O 密集任务，CPU 密集任务更适合多进程、C 扩展释放 GIL、或者交给 Go / C++ 这类语言处理。

面试里可以讲清楚：

1. GIL 保护解释器内部对象和引用计数。
2. I/O 阻塞时线程可以切换，网络请求和文件读写能受益。
3. CPU 密集计算会受到 GIL 影响。
4. 常见方案是 `multiprocessing`、`asyncio`、C 扩展、任务队列。

### Goroutine 和线程的区别

**可直接说：** goroutine 是 Go 运行时管理的轻量执行单元，线程是操作系统内核调度的执行单元。Go 使用 G-M-P 调度模型把大量 goroutine 映射到少量 OS 线程上，创建成本和切换成本更低，栈也会按需增长。

重点对比：

1. 调度者：goroutine 由 Go runtime 调度，线程由 OS 调度。
2. 栈空间：goroutine 初始栈很小并可增长，线程栈通常更大。
3. 并发规模：goroutine 更适合大量并发任务。
4. 通信方式：Go 推荐 channel 和共享内存加锁结合使用。

### 常用编程语言和 Java 使用情况

**可直接说：** 我的常用语言是 Go 和 Python，Go 主要用于后端服务和并发场景，Python 主要用于脚本、自动化和数据处理。Java 使用频率中等，能写基础业务代码，也了解集合、线程池、JVM 基础和 Spring 生态的基本概念。

## 大数据与网络基础

### 大数据了解什么

**可直接说：** 我对大数据的理解主要包括数据采集、消息队列、批处理、流处理、存储和分析查询。典型组件有 Kafka、HDFS、Spark、Flink、Hive、ClickHouse，核心问题是高吞吐、分区、容错、状态管理和数据一致性。

回答时可以按链路讲：

1. 采集：日志、埋点、业务库 CDC。
2. 传输：Kafka 做缓冲和削峰。
3. 计算：Spark 偏批处理，Flink 偏流处理。
4. 存储：HDFS、对象存储、数据仓库、OLAP 引擎。
5. 保障：checkpoint、重试、幂等、监控和告警。

### Socket、TCP、UDP 分别解决什么问题

**可直接说：** Socket 是应用程序进行网络通信的编程接口；TCP 提供可靠、有序、面向连接的字节流；UDP 提供低开销、低延迟、面向报文的数据传输。

可以补充场景：

1. Socket：服务端监听端口、客户端建立连接、读写网络数据。
2. TCP：HTTP、数据库连接、文件传输、RPC。
3. UDP：DNS、音视频、游戏同步、监控上报。
4. 可靠性要求高的业务优先用 TCP，延迟敏感且可自定义重传的业务可以用 UDP。

## 排障准备

### Debug 常用工具和方案

**可直接说：** 我会先定位问题层级，再选工具。Docker 问题看容器状态、日志、镜像、网络和挂载；Go 问题看日志、pprof、race、trace 和 panic 栈；Python 问题看日志、断点、测试、性能分析和依赖环境。

Docker 常用命令：

```bash
docker ps -a
docker logs <container>
docker inspect <container>
docker stats
docker exec -it <container> sh
docker network ls
```

Go 常用方案：

1. `log` / 结构化日志定位请求链路。
2. `pprof` 看 CPU、内存、goroutine。
3. `go test -race` 查数据竞争。
4. `go tool trace` 看调度和阻塞。
5. `dlv` 做断点调试。

Python 常用方案：

1. `logging` 输出上下文和异常栈。
2. `pdb` / IDE 断点调试。
3. `pytest` 缩小复现范围。
4. `cProfile` 看耗时热点。
5. `pip freeze` / 虚拟环境确认依赖版本。

### Linux 端口被打满怎么排查

**可直接说：** 我会先判断是监听端口冲突、连接数过高，还是临时端口耗尽。然后用 `ss`、`lsof`、`netstat`、`top` 和进程日志定位具体进程、连接状态和远端地址分布。

排查路径：

1. 看整体连接状态。

```bash
ss -s
ss -tan | awk '{print $1}' | sort | uniq -c | sort -nr
```

2. 看端口和进程占用。

```bash
ss -lntp
lsof -i :<port>
```

3. 看大量连接集中在哪些远端。

```bash
ss -tanp | awk '{print $5}' | sort | uniq -c | sort -nr | head
```

4. 看临时端口范围和文件描述符限制。

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
ulimit -n
cat /proc/<pid>/limits
```

5. 结合业务处理方案：复用连接池、缩短无效连接超时、检查泄漏连接、扩容服务实例、调整临时端口范围、优化反向代理和负载均衡配置。

## 算法：检验是否二叉搜索树

推荐面试写递归上下界法，核心是每个节点都要满足祖先节点传下来的取值范围。

```go
/**
 * Definition for a binary tree node.
 * type TreeNode struct {
 *     Val int
 *     Left *TreeNode
 *     Right *TreeNode
 * }
 */
func isValidBST(root *TreeNode) bool {
	return valid(root, nil, nil)
}

func valid(node, low, high *TreeNode) bool {
	if node == nil {
		return true
	}
	if low != nil && node.Val <= low.Val {
		return false
	}
	if high != nil && node.Val >= high.Val {
		return false
	}
	return valid(node.Left, low, node) && valid(node.Right, node, high)
}
```

复杂度：

1. 时间复杂度：`O(n)`，每个节点访问一次。
2. 空间复杂度：`O(h)`，`h` 是树高，来自递归调用栈。

## 复盘重点

这场面试的核心准备方向：

1. 项目要讲清楚来源、真实需求、技术取舍和个人贡献。
2. OJ 自研价值要落到判题隔离、资源控制、任务调度和异常处理。
3. DinD 要重点准备权限、cgroup、文件系统、网络和容器回收。
4. Docker / K8s、GIL / goroutine、Socket / TCP / UDP 要能用短答案说明核心区别。
5. Linux 端口排障要记住 `ss`、`lsof`、连接状态、临时端口范围和文件描述符限制。
6. 验证二叉搜索树优先用上下界递归，注意祖先约束和重复值边界。
