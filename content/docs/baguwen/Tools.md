---
title: "常用工具"
---

# 常用工具

## Git

- Git 的工作区、暂存区和本地仓库分别是什么
- `git pull` 和 `git fetch` 的区别
- `git merge` 和 `git rebase` 的区别
- 发生代码冲突后如何处理
- `git reset`、`git revert` 和 `git checkout` 的区别
- `git cherry-pick` 的使用场景
- `git stash` 的作用和常见用法
- 如何查看某次提交改了什么内容

## CI/CD

- 什么是 CI，什么是 CD
- 一个典型的 CI/CD 流程包含哪些阶段
- 为什么要在流水线中加入自动化测试
- 持续集成和持续部署分别解决了什么问题
- GitHub Actions、GitLab CI、Jenkins 有什么区别
- 如何设计开发、测试、预发、生产多环境发布流程
- 什么是灰度发布、蓝绿发布和滚动发布
- 发布失败后如何快速回滚

## Docker 与部署

- Docker 镜像和容器的区别
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 镜像是静态、只读的文件系统快照，而容器是动态、运行中的进程及其环境的实例。面试里可按三点展开：生命周期：镜像一次构建可以多次复用，而容器是临时的，生命周期短，只能运行一次；可修改性：镜像只读，改了必须重新构建，而容器有独立的读写层；数量关系：一个镜像可以对应多个容器实例，而一个容器实例只能对应一个镜像。


**关键点：**
- 生命周期：镜像一次构建可以多次复用，而容器是临时的，生命周期短，只能运行一次。
- 可修改性：镜像只读，改了必须重新构建，而容器有独立的读写层。
- 数量关系：一个镜像可以对应多个容器实例，而一个容器实例只能对应一个镜像。

</div>
</details>

- Dockerfile 常见指令有哪些
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Dockerfile 是构建 Docker 镜像的声明式文本文件，所有指令按功能可分为以下几类：
- 基础指令：如`FROM`指定基础镜像、`ENV`/`ARG`指定环境变量、`LABEL`添加标签、`EXPOSE`声明监听端口等；
- 文件操作类：如`COPY`/`ADD`复制文件、`WORKDIR`设置工作目录、`USER`指定运行容器的用户等；
- 执行指令类：如`RUN`构建时执行命令、`CMD`/`ENTRYPOINT`指定容器启动时执行的命令等；
- 其他：如`VOLUME`声明挂载的卷、`HEALTHCHECK`声明健康检查命令、`FROM ... AS builder`指定构建阶段的镜像等。

</div>
</details>

- 什么是多阶段构建，为什么要使用多阶段构建
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 多阶段构建是指在一个 dockerfile 中用多个`FROM`指令，每一个`FROM`代表一个独立的构建阶段，本质是多个镜像的接力构建。每个`FROM`指令都会启动一个全新的镜像，前面阶段生成的文件可以通过`COPY --from=阶段名`复制到后面的阶段，所有前面的阶段不会出现在最终镜像里。

**关键点：**
- 极致减小镜像体积：避免复制不必要的文件，大幅加快镜像的拉取速度，使得部署时间大幅缩短；磁盘占用小、传输带宽成本降低；
- 提升安全性：运行镜像里没有编译器、调试器等工具，减小了攻击面；没有多余的二进制文件，黑客无法利用这些文件进行攻击。
- 分离构建和运行环境：构建阶段只负责编译和打包应用，不负责运行；运行阶段负责负责运行应用，不负责编译和打包。

**注意**
先复制`go.mod go.sum`文件到构建阶段，再复制应用代码到运行阶段。这样做的目的是最大化利用 Docker 构建缓存，只要`go.mod go.sum`文件没有改变，`go mod download`就会直接用缓存，不用每次都重新下载依赖，大幅加快构建速度。

</div>
</details>

- `CMD` 和 `ENTRYPOINT` 的区别
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `CMD`指定容器启动时默认执行的命令，会被`docker run`后面的参数完全覆盖，`ENTRYPOINT`指定容器启动时的入口命令，不会被`docker run`覆盖，参数会被追加到入口命令后面。
| 场景 | CMD | ENTRYPOINT |
| --- | --- | --- |
| 被 `docker run` 参数覆盖 | 完全覆盖 | 参数被追加 |
| 最佳用途 | 提供默认命令和参数 | 固定容器的主程序 |
| 推荐组合 | 配合 ENTRYPOINT 提供默认参数 | 作为主程序入口 |

</div>
</details>

- 容器启动失败时如何排查问题
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先看容器状态，再看日志、容器配置、最后看容器资源、依赖、网络。
- 看容器状态：`docker ps -a`
- 看容器日志：`docker logs 容器 ID/容器名`
- 看容器配置：`docker inspect 容器ID`
- 看容器资源、依赖、网络：`netstat -ltnp`检查网络端口占用情况，`docker stats`检查内存/CPU占用情况，`docker network inspect 容器名`检查网络配置。

</div>
</details>

- `docker compose` 的作用是什么
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `docker compose` 是一个单机的多容器编排工具，用于定义和运行多容器应用。它通过一个声明式文件`docker-compose.yml`配置所有服务，然后一条命令启动/停止整个应用栈，而不需要手动启动和管理每个容器。

**和`docker run`的区别：**
- `docker run` 是一个单容器命令，只能启动一个容器，不能启动多个容器，适用于单个容器测试。
- `docker compose` 是一个多容器命令，可以在一个声明式文件中定义多个服务并一起启动，适用于多容器应用的开发、测试、部署和管理。

</div>
</details>

- 应用部署时如何管理配置和环境变量
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 应避免将配置和环境变量硬编码到容器中，优先考虑外部化、隔离环境、安全存储，目的是让应用一套镜像跑所有的环境。

- 环境变量：把配置通过`ENV`指令或运行时传给容器
- 环境变量文件：把环境变量写入一个`.env`文件，容器启动时通过`--env-file`参数指定。
- 配置文件：把配置文件挂载进容器，不打包进镜像

</div>
</details>

- 服务发布时如何尽量做到不停机
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 服务发布时，为了做到不停机，通常采用滚动更新策略。具体来说就是流量不中断，旧的容器实例跑完请求之后再下线，新的容器实例就绪了再接流量，全程业务不中断。

- 健康检查前置：发布前先检查旧容器实例是否健康（`/health`正常），确保旧容器实例可以正常服务。
- 健康检查后置：发布后检查新容器实例是否健康（`/health`正常），确保新容器实例可以正常服务。
- 负载均衡层配合：配合负载均衡层（如`nginx`），实现流量平滑迁移，确保业务不中断。
- 优雅停机：先摘除流量，不再接受新请求，等旧容器实例处理完当前请求后再下线。
</div>
</details>

- 滚动发布、灰度发布、蓝绿发布等策略的目的是什么，核心区别是什么？
<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 滚动发布、灰度发布、蓝绿发布都是为了做到不停机而采用的发布策略，它们的核心区别在于**流量切换方式、回滚速度和资源成本**。

- **滚动发布**：分批逐步替换旧实例为新实例，新旧实例同时在线，流量通过负载均衡器自动分发，不需要显式切换。
- **灰度发布**：先发布到部分用户并引流小部分流量验证，确认正常后再逐步扩大范围到所有用户。
- **蓝绿发布**：准备一套完整的新环境（绿环境），切换前保留旧环境（蓝环境），确认新环境稳定后将流量一次性切换到新环境。

| 对比维度 | 滚动发布 | 灰度发布 | 蓝绿发布 |
| --- | --- | --- | --- |
| 流量切换 | 自动分发，无显式切换 | 逐步调整流量比例 | 一次性切换 |
| 回滚速度 | 慢，需逐个回滚实例 | 较快，停止灰度即可 | 极快，切回旧环境即可 |
| 资源成本 | 低（只需一套环境） | 低（只需一套环境） | 高（需两套完整环境） |
| 影响范围 | 按实例比例逐步影响 | 按流量比例精准控制 | 全量切换，影响范围大 |
| 适用场景 | 资源有限、需要快速迭代 | 需要小范围验证新功能 | 对稳定性要求极高、预算充足 |

</div>
</details>
