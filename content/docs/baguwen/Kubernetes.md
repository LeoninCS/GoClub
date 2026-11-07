---
title: "Kubernetes"
slug: "kubernetes"
description: "Kubernetes（K8s）面试题，覆盖集群组件、Pod、调度、网络、存储、etcd、安全和运维排障。"
aliases:
  - "/s/4sw3/"
shortlink: "4sw3"
---

# Kubernetes

根据《K8S面试题》整理。可以先沿着“一个 Pod 从创建到接收流量”的过程复习，再看调度、存储和故障排查。每道题的答案都可以单独展开。

## 集群架构与 API

### Kubernetes 解决什么问题，什么时候值得用

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 容器编排要解决的是一组容器跨机器部署以后，谁来放置、补副本、更新版本和接入流量。Kubernetes 让使用者提交期望状态，控制器持续观察实际状态并缩小差距。

**要答的点：**

- 以三个 Web 副本为例，Deployment 描述版本和副本数，调度器选择节点，Service 提供稳定访问入口。
- 滚动发布、弹性伸缩和声明式配置适合多个服务共享资源的场景。单机小应用要衡量控制面、网络、存储和升级的维护成本。

**重点讲解摘录：**

- 自愈有边界。副本控制器可以补建进程，但应用数据的备份、幂等和恢复仍需应用与存储系统配合。

**原文链接：**

- [Kubernetes 概览](https://kubernetes.io/docs/concepts/overview/)
- [控制器与控制循环](https://kubernetes.io/docs/concepts/architecture/controller/)

</div>
</details>

### 控制面和工作节点有哪些组件，靠什么协作

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** kube-apiserver 是 Kubernetes API 的入口，etcd 持久化集群对象，kube-controller-manager 运行各类控制循环，kube-scheduler 为待调度的 Pod 选节点。节点上的 kubelet 通过容器运行时落实 Pod 配置。

**要答的点：**

- 客户端通过 API Server 提交对象。控制器通常先 List 再 Watch，利用资源版本衔接变化，必要时重新列举。
- 调度器通过 API 写入绑定结果。kubelet 汇报 Pod 和节点状态。kube-proxy 或替代的数据面实现负责 Service 转发。

**重点讲解摘录：**

- 以 Deployment 为例，Deployment 控制器管理 ReplicaSet，ReplicaSet 控制器补足 Pod。它们通过 API 对象交接工作，调度器无需直接给 kubelet 下命令。

**原文链接：**

- [集群组件](https://kubernetes.io/docs/concepts/overview/components/)
- [API 的 List 与 Watch](https://kubernetes.io/docs/reference/using-api/api-concepts/)

</div>
</details>

### Kubernetes 和 Docker、Docker Swarm 分别是什么关系

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Docker 可以构建镜像并运行容器，Kubernetes 编排集群里的工作负载。Docker Swarm 则是 Docker Engine 自带的集群编排模式，与 Kubernetes 比较时应看两者如何部署和管理服务。

**要答的点：**

- kubelet 通过 CRI 对接 containerd、CRI-O 等运行时。自 v1.24 起，Kubernetes 移除了内置 dockershim，Docker 构建的兼容镜像仍可使用。
- Swarm 的 manager 维护 service 的期望状态并分配 task。Kubernetes 用 Deployment、Pod、Service 等独立对象描述副本、执行和访问。

**重点讲解摘录：**

- 面试追问“能不能用 Docker”时，先区分构建镜像、运行镜像和编排多个节点这三件事。

**原文链接：**

- [容器运行时与 CRI](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)
- [Docker Swarm 的服务模型](https://docs.docker.com/engine/swarm/key-concepts/)

</div>
</details>

### Minikube、kubectl、kubelet 和 GKE 各用在什么地方

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Minikube 用于搭建本地学习或测试集群，kubectl 是调用 Kubernetes API 的客户端，kubelet 是每个节点上的代理。GKE 是 Google Cloud 提供的托管 Kubernetes 服务。

**要答的点：**

- 在笔记本上运行 `kubectl get pods`，访问的是当前 kubeconfig context 指向的集群，本机可以不运行 kubelet。
- 在 GKE 中由平台维护控制面，工作节点的运维分工取决于集群模式。应用仍通过 Kubernetes API 部署。

**重点讲解摘录：**

- 排查命令连错集群先看 `kubectl config current-context`。排查一个已绑定节点的 Pod 为什么没启动，再看该节点的 kubelet 和运行时。

**原文链接：**

- [Minikube 本地集群](https://minikube.sigs.k8s.io/docs/start/)
- [集群组件](https://kubernetes.io/docs/concepts/overview/components/)
- [Google Kubernetes Engine 概览](https://cloud.google.com/kubernetes-engine/docs/concepts/kubernetes-engine-overview)

</div>
</details>

### Pod 怎样访问 API Server，Proxy API 有什么用途

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** API Server 的默认安全监听端口是 6443。集群内的客户端通常通过 `kubernetes.default.svc` 对应的 Service 的 443 端口访问，并使用集群 CA 验证服务端。

**要答的点：**

- Pod 可以使用挂载的 ServiceAccount 凭据进行身份认证。授权范围取决于 RBAC 等配置，端口可达只说明网络连通。
- 已授权用户可以通过 API Server 的 proxy 子资源访问后端。例如 `kubectl get --raw /api/v1/namespaces/demo/services/web:http/proxy/` 访问 demo 命名空间的 web 服务，端口名为 http。

**重点讲解摘录：**

- `kubectl proxy` 在本地建立通往 API Server 的代理。处理 Service 业务流量的 kube-proxy 是节点网络组件，两者职责不同。

**原文链接：**

- [控制面端口](https://kubernetes.io/docs/reference/networking/ports-and-protocols/)
- [在 Pod 内访问 API](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/)
- [访问集群内的服务](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster-services/)

</div>
</details>

### kubelet 在节点上负责哪些事，容器挂了它怎么知道

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** kubelet 根据分配到本节点的 Pod 规格协调运行时和卷，运行配置好的健康探针，再上报容器、Pod 和 Node 的状态。判断进程退出与判断业务是否就绪是两个独立信号。

**要答的点：**

- 运行时经 CRI 提供容器状态。容器退出时，kubelet 按重启策略处理，并在 Pod 状态中记录原因、退出码与重启次数。
- 探针可以识别仍在运行的进程是否卡死或暂时不能接流量。节点级 Lease 和 Node 状态更新则帮助控制面判断 kubelet 是否还能通信。

**重点讲解摘录：**

- 遇到“节点 Ready 但应用不可用”，应沿 Pod 条件、探针、端点和应用日志检查。节点心跳正常只能说明节点级信号，不能证明每个服务健康。

**原文链接：**

- [节点、注册与心跳](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [容器运行时接口](https://kubernetes.io/docs/concepts/containers/cri/)
- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [配置启动、存活与就绪探针](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

</div>
</details>

### 工作节点怎样加入集群，kubelet 怎样维持节点状态

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 以 kubeadm 为例，新节点通过发现过程确认控制面身份，再用引导凭据申请 kubelet 客户端证书。完成授权和注册后，kubelet 就能持续同步分配给本节点的 Pod。

**要答的点：**

- `kubeadm join` 通常通过 CA 公钥哈希验证发现信息。引导 token 和长期使用的客户端证书各有用途。
- 节点心跳包括 Node 状态更新和 `kube-node-lease` 命名空间中的 Lease 续约。kubelet 还上报容量、可分配资源和就绪条件。

**重点讲解摘录：**

- 排查加入失败可沿发现、证书签发、Node 注册三个阶段检查。已出现 Node 但长期 NotReady 时，再检查运行时和 CNI 的就绪情况。

**原文链接：**

- [kubeadm join 与 TLS 引导](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/)
- [节点、注册与心跳](https://kubernetes.io/docs/concepts/architecture/nodes/)

</div>
</details>

### Namespace、Label 和 Selector 分别解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Namespace 给有命名空间的资源划分名称和管理范围。Label 是对象上的键值标记，Selector 用这些标记选出对象集合。

**要答的点：**

- 同一个命名空间可同时用 `app=checkout`、`environment=prod`、`tier=backend` 组织对象，`kubectl get pods -l app=checkout,tier=backend` 要求两个条件同时满足。
- Pod 和 Service 属于命名空间，Node 和 PV 属于集群。多租户通常还需要 RBAC、ResourceQuota 和 NetworkPolicy。

**重点讲解摘录：**

- 给 Pod 加上新标签就可能改变匹配它的 Service 后端。设计选择器时要区分持久的应用标识和随发布变化的版本号。

**原文链接：**

- [命名空间](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [标签与选择器](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)

</div>
</details>

## Pod、容器与健康检查

### Pod 内部共享什么，pause 容器有什么作用

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Pod 是 Kubernetes 调度的基本单位，同一个 Pod 的容器落在同一节点。常见 Linux CRI 实现使用基础设施容器维持 Pod 沙箱的命名空间，业务容器加入同一网络环境。

**要答的点：**

- 容器共享 Pod IP 和端口空间，可经 localhost 通信。两个进程若同时绑定同一地址和端口会发生冲突。
- 容器各有自己的根文件系统。要共享文件，需把同一个卷挂到需要访问的容器中。共享进程命名空间则需单独配置。

**重点讲解摘录：**

- 同一 Pod 内重启一个业务容器时，沙箱和卷通常仍在。删除并重建 Pod 会得到新的 UID，IP 也可能改变。

**原文链接：**

- [Pod 的资源共享](https://kubernetes.io/docs/concepts/workloads/pods/)
- [容器运行时接口](https://kubernetes.io/docs/concepts/containers/cri/)

</div>
</details>

### 从提交 Deployment 到 Pod 开始接流量，依次发生什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** API Server 完成访问控制和对象校验后持久化 Deployment。控制器创建 ReplicaSet 和 Pod，调度器写入节点绑定，目标 kubelet 再驱动运行时启动容器。

**要答的点：**

- 在节点上，kubelet 协调卷准备、Pod 沙箱和镜像准备。运行时配合网络插件配置网络，普通 init 容器完成后才启动应用容器。
- 有匹配的 Service 时，EndpointSlice 控制器维护端点及其条件。Pod 就绪、端点更新并且数据面规则生效后，新的连接才能正常到达它。

**重点讲解摘录：**

- 定位卡点可以顺序查看 Deployment、ReplicaSet、Pod Events 和 EndpointSlice。直接创建一个裸 Pod 时，流程从创建 Pod 对象开始。

**原文链接：**

- [Deployment 更新与回滚](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [EndpointSlice 及端点条件](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

</div>
</details>

### Pod phase、容器状态和 kubectl 的 STATUS 有什么区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Pod 的 phase 有 Pending、Running、Succeeded、Failed 和 Unknown。容器状态有 Waiting、Running、Terminated，kubectl 的 STATUS 列还会展示更具体的原因。

**要答的点：**

- Running 表示 Pod 已绑定节点，至少一个容器正在运行、启动或重启。能否接流量还要看 Ready 条件。
- `CrashLoopBackOff` 表示反复失败后的重启退避，`ImagePullBackOff` 表示镜像拉取重试退避。排查时查看 Events 和容器的 `lastState`。

**重点讲解摘录：**

- 原题把 Pending、Running 称作“镜像状态”。镜像本身是构建产物，`kubectl get pod -o yaml` 中的 `status.phase` 描述的是 Pod。

**原文链接：**

- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [排查 Pod 异常](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [容器镜像与拉取策略](https://kubernetes.io/docs/concepts/containers/images/)

</div>
</details>

### 容器退出后谁负责重启，删除 Pod 后谁负责补副本

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 同一个 Pod 内，kubelet 按重启策略处理已退出的容器。Pod 被删除后，是否出现新 Pod 取决于 Deployment、Job 等上层控制器的期望状态。

**要答的点：**

- 常用 Pod 级 `restartPolicy` 有 Always、OnFailure、Never。OnFailure 针对失败退出，Never 会保留终止结果供查询。
- Deployment 的 Pod 使用 Always。Job 可用 OnFailure 或 Never，Job 控制器还会根据完成条件和重试上限决定是否创建后续 Pod。

**重点讲解摘录：**

- 看 UID 可以区分两种情况。UID 相同且 `restartCount` 增长是容器重启，替换出来的 Pod 有新的 UID。

**原文链接：**

- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Job 的执行与重试](https://kubernetes.io/docs/concepts/workloads/controllers/job/)

</div>
</details>

### 删除 Pod 时怎样优雅终止，流量何时摘除

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 删除请求会设置删除时间戳和宽限期。kubelet 在节点上执行本地终止流程，同时控制面更新服务端点状态。应用要能停止接新请求并在宽限期内完成在途工作。

**要答的点：**

- 如配置了 `preStop`，钩子会占用终止宽限期。随后运行时通常发送 SIGTERM，超时仍未退出的进程会被强制终止。
- 终止端点通常变为 `terminating=true`、`ready=false`。端点更新与本地关闭并行，已有连接还可能持续一段时间。

**重点讲解摘录：**

- 例如应用最多需要 20 秒完成请求，preStop 还会消耗 5 秒，就应按两段耗时和传播余量设置 `terminationGracePeriodSeconds`。

**原文链接：**

- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [EndpointSlice 及端点条件](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

</div>
</details>

### init 容器、Sidecar 和静态 Pod 各适合什么任务

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 普通 init 容器依次运行并成功结束，再启动业务容器。Sidecar 伴随应用长期运行。静态 Pod 则由指定节点的 kubelet 直接管理。

**要答的点：**

- 准备配置或运行前置检查适合 init 容器。持续收集日志、代理流量适合 Sidecar。原生 Sidecar 可在 `initContainers` 中设置容器级 `restartPolicy: Always`。
- 静态 Pod 常用本地清单描述。kubelet 可在 API Server 创建镜像 Pod 以便观察，实际配置由节点上的清单控制。

**重点讲解摘录：**

- 修改或删除静态 Pod 的镜像对象不能持久改变本地工作负载。排查 kubeadm 控制面组件时，应同时检查本机静态清单和运行时状态。

**原文链接：**

- [初始化容器](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [原生 Sidecar 容器](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [静态 Pod 与镜像 Pod](https://kubernetes.io/docs/tasks/configure-pod-container/static-pod/)

</div>
</details>

### 镜像怎样拉取，command 和 args 怎样覆盖镜像默认值

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** `imagePullPolicy` 决定何时解析或拉取镜像。Pod 中的 `command` 对应镜像 ENTRYPOINT，`args` 对应 CMD，可以只替换参数并沿用原入口。

**要答的点：**

- Always 每次启动都向仓库解析镜像，节点已有相同摘要时可复用缓存。IfNotPresent 优先用本地镜像，Never 要求本地已有镜像。
- 默认策略在对象创建时确定。固定 digest 能把部署与具体镜像内容绑定，排查拉取失败还应检查镜像名、凭据和节点连通性。

**重点讲解摘录：**

- `command: ["sh", "-c"]` 搭配 `args: ["echo hello && exec ./server"]` 显式使用 shell。普通参数数组不会自动解释管道、重定向等 shell 语法。

**原文链接：**

- [容器镜像与拉取策略](https://kubernetes.io/docs/concepts/containers/images/)
- [容器命令与参数](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/)

</div>
</details>

### 启动、存活和就绪探针分别处理哪种故障

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 启动探针回答应用是否完成初始化，存活探针判断容器是否需要重启，就绪探针判断是否适合接收流量。慢启动应用可用启动探针保护预热过程。

**要答的点：**

- 配置 startupProbe 后，成功前不会执行存活和就绪探针。启动或存活探针连续失败到阈值会触发 kubelet 终止相应容器，后续按重启策略处理。
- 就绪探针失败会使容器变为未就绪，影响 Pod Ready 和通常的 Service 后端选择，进程仍可继续运行并恢复。

**重点讲解摘录：**

- 例如数据库短暂不可用时，重启所有前端常会放大故障。是否应停止接流量取决于服务能否降级，存活探针应能区分本地进程卡死与下游抖动。

**原文链接：**

- [配置启动、存活与就绪探针](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod 生命周期与终止](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

</div>
</details>

### 探针支持哪些检查方式，阈值应该怎样解释

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 探针可执行命令、发送 HTTP GET、建立 TCP 连接或调用 gRPC 健康检查。检查内容要反映服务真正具备的能力。

**要答的点：**

- exec 依据退出码，HTTP 以 200～399 为成功，TCP 检查端口能否建立连接，gRPC 要求实现健康检查协议。
- `initialDelaySeconds` 设置初始等待，`periodSeconds` 设置检查周期，`timeoutSeconds` 限制单次等待。`failureThreshold` 和 `successThreshold` 都按连续结果计数。

**重点讲解摘录：**

- 启动和存活探针的成功阈值必须为 1。给通常需要两分钟启动的程序配置每 5 秒检查、失败阈值 30，约可留出 150 秒的启动预算。

**原文链接：**

- [配置启动、存活与就绪探针](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

</div>
</details>

## 调度、资源与工作负载

### 调度器如何给一个 Pod 选节点，污点和亲和性怎样参与

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 调度器先过滤不满足硬约束的节点，再对可行节点评分，最后选定节点并通过 API 完成绑定。硬约束决定能不能放，软偏好影响放在哪里。

**要答的点：**

- 过滤条件包括节点可分配资源、节点选择条件、卷拓扑，以及 Pod 是否容忍节点的污点。`requiredDuringSchedulingIgnoredDuringExecution` 属于硬约束。
- `preferredDuringSchedulingIgnoredDuringExecution` 表达偏好。容忍 NoSchedule 只让节点成为可能的候选，要把 Pod 限定到某类节点还需选择器或必需亲和性。

**重点讲解摘录：**

- 即使某节点 CPU 空闲，也可能因已分配的 requests、未容忍的污点或卷所在可用区而无法调度。可以从 Pod 的 FailedScheduling 事件查看哪个条件失败。

**原文链接：**

- [调度器的过滤与评分](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [节点选择与亲和性](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [污点与容忍](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)

</div>
</details>

### requests、limits 和 QoS 怎样影响调度与运行

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 调度器用资源请求量判断节点是否装得下，kubelet 和运行时在节点上落实资源约束。CPU 超限通常会被限流，内存达到限制且无法回收时可能触发 OOM。

**要答的点：**

- 按常见的容器级配置，所有容器的 CPU 和内存都设了相等的非零 request 和 limit 才是 Guaranteed。都未设置是 BestEffort，其余一般为 Burstable。
- 资源有单位。`250m` CPU 是四分之一个核，`256Mi` 表示 256 MiB 内存。检查实际生效对象时还要考虑默认值和准入时注入的配置。

**重点讲解摘录：**

- 节点出现内存压力时，kubelet 会综合使用量是否超过请求、Pod 优先级和相对使用量决定驱逐次序。容器自身触发 OOM 与节点压力驱逐的排查路径不同。

**原文链接：**

- [容器资源管理](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Pod QoS 类别](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)

</div>
</details>

### Pod 长期 Pending，怎样快速把原因范围缩小

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先查 `kubectl get pod <pod> -o wide` 是否已有节点，再看 `kubectl describe pod <pod>` 的 Conditions 和 Events。这一步把调度失败与节点启动失败区分开。

**要答的点：**

- 如果没有绑定节点，检查 `FailedScheduling` 中的资源不足、污点、亲和性或未绑定 PVC 等原因，再对照候选节点的 allocatable 和已请求资源。
- 如果已有节点，检查 FailedMount、FailedCreatePodSandBox、ErrImagePull 等事件，再分别核对卷、CNI、镜像凭据或 init 容器状态。

**重点讲解摘录：**

- 例如事件明确写着多个节点都缺少 GPU，新增普通 CPU 节点无法解除这个约束。排查结论应当能解释调度器给出的具体淘汰原因。

**原文链接：**

- [排查 Pod 异常](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [调度器的过滤与评分](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)

</div>
</details>

### ReplicationController、ReplicaSet 和 Deployment 如何分工

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RC 和 RS 都用标签选择器维持指定副本数。RS 支持集合型选择条件，Deployment 在 RS 之上管理 Pod 模板版本、滚动更新和回滚。

**要答的点：**

- 副本控制器根据匹配且受其管理的 Pod 数量补建或删除副本。RC 的选择器使用等值匹配，RS 还支持 `matchExpressions`。
- 修改 Deployment 的 Pod 模板通常会创建或复用与该模板匹配的 RS。只改副本数会伸缩已有版本，通常不会产生新的发布修订。

**重点讲解摘录：**

- 可以沿 Pod 的 `ownerReferences` 找到 RS，再找到 Deployment。手工删除一个受控 Pod 后，创建替代副本的是 RS 控制器。

**原文链接：**

- [ReplicationController](https://kubernetes.io/docs/concepts/workloads/controllers/replicationcontroller/)
- [ReplicaSet 的选择与认领](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Deployment 更新与回滚](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

</div>
</details>

### Deployment 如何滚动发布，三个副本时能同时下线几台

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** RollingUpdate 逐步扩大新 RS、缩小旧 RS。`maxSurge` 限制滚动期间额外创建的副本数，`maxUnavailable` 限制允许不可用的副本数。Recreate 会先终止旧版本，再创建新版本。

**要答的点：**

- 期望 3 个副本，两项都设为 25% 时，surge 向上取整为 1，unavailable 向下取整为 0。正常发布时至少要保持 3 个可用副本，可先创建第 4 个。
- 新 Pod 必须达到可用条件才会释放下一步的替换空间。若设置了 `minReadySeconds`，还要连续就绪指定时长。

**重点讲解摘录：**

- 若没有第 4 个 Pod 所需容量，又要求零不可用，发布可能停住。滚动上限约束的是控制器的副本计算，仍处于终止宽限期的 Pod 可能额外占用节点资源。

**原文链接：**

- [Deployment 更新与回滚](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

</div>
</details>

### 怎样更新、扩缩容和回滚 Deployment

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 更新镜像可改清单后执行 `kubectl apply -f app.yaml`，或用 `kubectl set image deployment/web web=registry.example/web:v2`。更新后用 `kubectl rollout status deployment/web` 观察进度。

**要答的点：**

- 手动伸缩可用 `kubectl scale deployment/web --replicas=5`。由 HPA 管理副本数时，应协调伸缩入口，否则多个写入者会反复调整 replicas。
- `kubectl rollout history deployment/web` 查看保留的修订，`kubectl rollout undo deployment/web --to-revision=2` 恢复指定版本的 Pod 模板。

**重点讲解摘录：**

- 回滚能否成功取决于历史修订是否保留。恢复模板并不会撤销数据库迁移，未改变名称的外部 ConfigMap 或 Secret 也不会随它回到旧值。

**原文链接：**

- [Deployment 更新与回滚](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [水平自动伸缩算法](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)

</div>
</details>

### DaemonSet 和 StatefulSet 分别保证什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** DaemonSet 让每个符合条件的节点运行一份节点级工作负载。StatefulSet 为每个副本提供稳定的序号、网络标识，并可为其绑定独立的持久卷。

**要答的点：**

- 日志代理和节点网络组件适合 DaemonSet。控制器为目标节点创建带节点亲和性的 Pod，默认调度器负责完成绑定。
- 有状态应用需要重建后找回自身身份和数据时可用 StatefulSet。配合无头 Service 提供稳定名称，用 `volumeClaimTemplates` 为各副本申请卷。

**重点讲解摘录：**

- DaemonSet 的数量随合格节点变化。StatefulSet 即使给了数据库稳定身份，也不会自动实现数据库复制、选主或备份。

**原文链接：**

- [DaemonSet 的调度过程](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [StatefulSet 的稳定标识](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

</div>
</details>

### Job 和 CronJob 如何判断完成，执行为什么要幂等

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Job 运行需要正常结束的任务，控制成功完成次数、并行度和失败重试。CronJob 按计划创建 Job，每次实际执行仍由 Job 管理。

**要答的点：**

- `completions` 决定需要多少次成功完成，`parallelism` 限制同时运行的数量，`backoffLimit` 控制失败重试。
- CronJob 的 `concurrencyPolicy` 可以允许、禁止或替换同一 CronJob 的并发任务。控制器或节点故障时仍需考虑重复执行或错过调度。

**重点讲解摘录：**

- 例如按日结算应以业务日期和账户作为去重键。重试同一次任务时，已经写入的结果要能被识别。

**原文链接：**

- [Job 的执行与重试](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJob 的调度语义](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)

</div>
</details>

### HPA 根据什么计算副本数，为什么 CPU 很忙却没有扩容

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** HPA 定期读取指标，比较观测值和目标值，再通过目标资源的 scale 子资源调整副本数。它既可使用 CPU、内存等资源指标，也可接入自定义或外部指标。

**要答的点：**

- 简化关系为期望副本数等于当前副本数乘以指标与目标的比值，再向上取整。实际还受 min/max、容差、就绪状态和稳定窗口影响。
- CPU 利用率按使用量相对于 request 计算。先看 `kubectl describe hpa` 的 Conditions 和 Targets，再检查相关容器的 CPU request 和指标 API。

**重点讲解摘录：**

- 若 3 个副本平均利用率为 80%，目标是 50%，初步计算为 5 个副本。即使 HPA 扩到了 5，节点容量仍决定新增 Pod 能否落地。

**原文链接：**

- [水平自动伸缩算法](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [资源指标链路](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)

</div>
</details>

## 服务发现与网络

### Service 如何找到 Pod，EndpointSlice 和 kube-proxy 各管哪一步

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 带选择器的 Service 匹配同命名空间中的 Pod。EndpointSlice 控制器维护后端地址、端口和就绪条件，kube-proxy 观察 Service 与 EndpointSlice，把映射编程到节点数据面。

**要答的点：**

- 客户端连接 ClusterIP 和 Service port，数据面选择可用后端，转发到 Pod IP 和 targetPort。应用进程必须在相应端口监听。
- 排查可先用 `kubectl get endpointslice -l kubernetes.io/service-name=web`，再核对 selector、Pod label、Ready 条件与端口。

**重点讲解摘录：**

- 有 ClusterIP 而没有就绪端点时，DNS 仍可能正确解析。把“取得服务地址”和“服务有可用后端”分开验证，可以少查一层。

**原文链接：**

- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlice 及端点条件](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Service 虚拟 IP 与代理模式](https://kubernetes.io/docs/reference/networking/virtual-ips/)

</div>
</details>

### Pod 如何通过 DNS 或环境变量发现服务，Headless Service 有何不同

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 普通 Service 的 DNS 名通常解析为 ClusterIP。无头 Service 配置 `clusterIP: None`，对带选择器的服务，DNS 可直接返回后端地址，由客户端选择连接目标。

**要答的点：**

- 同命名空间常用短名 `web`，跨命名空间常用 `web.demo`。完整名称形式是 `web.demo.svc.<cluster-domain>`，集群域可配置。
- 若启用 Service 环境变量注入，Pod 创建时已有的 Service 才会反映在该组变量中。DNS 可查询后来新增的服务。

**重点讲解摘录：**

- StatefulSet 常通过无头 Service 为副本提供 `web-0.web.demo.svc.<cluster-domain>` 这样的稳定名字。普通 Pod 的地址型 DNS 记录依赖 DNS 实现，应用不宜依赖这类记录。

**原文链接：**

- [Service 与 Pod 的 DNS 记录](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)
- [StatefulSet 的稳定标识](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

</div>
</details>

### ClusterIP、NodePort、LoadBalancer 和 ExternalName 怎么选

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** ClusterIP 给集群内客户端一个稳定入口。NodePort 在节点地址上开放端口。LoadBalancer 请求基础设施提供负载均衡入口。ExternalName 用 DNS CNAME 指向另一个域名。

**要答的点：**

- NodePort 的默认分配范围是 30000～32767。LoadBalancer 需要云控制器或其他实现支持，实际转发是否经过 NodePort 取决于该实现。
- ExternalName 在 DNS 层返回别名。HTTP Host 或 TLS 证书名仍按客户端使用的名字处理，接已有 HTTPS 服务时要核对域名匹配。

**重点讲解摘录：**

- 若只是将几个集群内后端暴露给另一个 Pod，用 ClusterIP 就能完成。需要外部四层入口时，再检查 LoadBalancer 的地址分配和后端健康检查。

**原文链接：**

- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Service 与 Pod 的 DNS 记录](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)

</div>
</details>

### 怎样让集群内应用通过 Service 名访问外部数据库

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 后端有稳定 DNS 名时可以用 ExternalName。有一组外部 IP 需要以固定 Service 地址访问时，可建无 selector 的 Service，再由自己或控制器维护关联的 EndpointSlice。

**要答的点：**

- EndpointSlice 要设置 `kubernetes.io/service-name` 指向 Service，填入可路由的后端地址与匹配的端口。集群不会通过 Pod selector 自动发现这些外部端点。
- 两种方案都需要验证 Pod 到外部服务的网络路径、DNS、防火墙、证书和数据库授权。

**重点讲解摘录：**

- 例如数据库迁移到新 IP 后，使用自管 EndpointSlice 的方案要同步更新地址。只改 Service 名称不会改变数据面连接目标。

**原文链接：**

- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlice 及端点条件](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

</div>
</details>

### iptables、IPVS 和 nftables 模式怎样实现 Service 转发

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 它们都是 Linux 上实现 Service 虚拟 IP 转发的方式。kube-proxy 监听 API 对象后维护内核状态，正常业务报文直接由内核数据面处理。

**要答的点：**

- iptables 使用规则链匹配 Service 并选择后端，结合 DNAT 和连接跟踪维持连接。IPVS 使用内核虚拟服务和后端表，某些场景还要配合其他包过滤规则。
- nftables 模式利用集合、映射等机制更新转发表。IPVS 在 Kubernetes v1.35 标记为弃用，解释具体行为时应说明集群所用版本和代理模式。

**重点讲解摘录：**

- Service 的分发通常按连接选择后端。长连接可能让多个请求落在同一 Pod。`sessionAffinity: ClientIP` 还可在一定时间内保持客户端亲和性。

**原文链接：**

- [Service 虚拟 IP 与代理模式](https://kubernetes.io/docs/reference/networking/virtual-ips/)
- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)

</div>
</details>

### Service 怎样选择后端，为什么三个副本流量不均

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Service 声明可用后端集合，实际选端点由代理实现、流量策略和连接状态共同决定。客户端复用少量长连接时，三个就绪副本的请求量仍可能相差很大。

**要答的点：**

- `sessionAffinity: None` 是默认设置。iptables 模式通常在新连接建立时随机选择端点。使用 `ClientIP` 可以让同一客户端一段时间内倾向同一后端。
- `internalTrafficPolicy: Local` 限制集群内流量只选本节点端点。外部入口也有 `externalTrafficPolicy`，设为 Local 时要确认接入节点确实有本地就绪端点。

**重点讲解摘录：**

- 排查不均衡时，先比较各 Pod 的新建连接数、连接持续时间和请求数，再检查就绪端点及会话亲和配置。只看一次请求分布很难判断转发规则是否异常。

**原文链接：**

- [Service 虚拟 IP 与代理模式](https://kubernetes.io/docs/reference/networking/virtual-ips/)
- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)

</div>
</details>

### 外部请求如何经过 Ingress 到达 Pod，四层与七层有什么区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** LoadBalancer Service 通常按 IP、协议和端口接入。Ingress 描述 HTTP(S) 的主机名和路径规则，需要实际运行的 Ingress Controller 实现转发。

**要答的点：**

- 以 `api.example.com/orders` 为例，请求先到入口控制器，控制器匹配主机名和路径，再按规则把请求交给目标 Service 对应的后端。
- 一个入口可复用外部地址和证书服务多个域名。控制器是否直接连接 Pod 端点、在哪一层终止 TLS，取决于配置和实现。

**重点讲解摘录：**

- 若访问返回 404，先分辨响应来自入口控制器还是应用，再核对 IngressClass、Host、路径类型和后端。若报无可用后端，应接着查 EndpointSlice。

**原文链接：**

- [Ingress 路由规则](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Service 的类型与外部后端](https://kubernetes.io/docs/concepts/services-networking/service/)

</div>
</details>

### CNI、Flannel、Open vSwitch 和 Calico 各负责哪一层

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Kubernetes 的 Pod 网络模型要求集群为 Pod 提供地址和跨节点可达性。CNI 定义运行时与网络插件之间的调用约定，具体路由、封装和策略由实现负责。

**要答的点：**

- Flannel 可用 VXLAN 跨节点封装，也支持 host-gw 等后端。Open vSwitch 是可编程虚拟交换机，可作为 OVN 等网络方案的数据面组件。
- Calico 的节点代理 Felix 编程本机路由和策略，可通过 BGP 分发路由，也可使用 IP-in-IP 或 VXLAN 封装。具体组合取决于底层网络。

**重点讲解摘录：**

- 同节点可达、跨节点不通时，应按使用的后端查路由或隧道、MTU 和底层安全组。仅确认 CNI 配置文件存在，不能证明数据包能跨节点往返。

**原文链接：**

- [Kubernetes 网络模型](https://kubernetes.io/docs/concepts/services-networking/)
- [CNI 插件规范](https://www.cni.dev/docs/spec/)
- [Flannel 网络后端](https://github.com/flannel-io/flannel/blob/master/Documentation/backends.md)
- [Open vSwitch 架构](https://docs.openvswitch.org/en/latest/intro/what-is-ovs/)
- [Calico 路由与封装](https://docs.tigera.io/calico/latest/networking/configuring/vxlan-ipip)
- [Calico 组件与 Felix](https://docs.tigera.io/calico/latest/reference/architecture/overview)

</div>
</details>

### NetworkPolicy 如何生效，两端都被隔离时怎样放行

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** NetworkPolicy 用 Pod 选择器圈定策略作用对象，分别声明入口和出口允许的对端与端口。需要网络实现支持并执行策略。

**要答的点：**

- 某方向未被任何相应策略隔离时，该方向默认允许。对已隔离的 Pod，同一方向上多份策略的允许规则取并集。
- 若源 Pod 的出口和目的 Pod 的入口均被隔离，一条新连接要同时满足两端的允许条件。`namespaceSelector` 和 `podSelector` 放在同一个 peer 中表示同时匹配。

**重点讲解摘录：**

- 排查“允许出站后仍访问失败”时，同时检查目的端入口和 DNS 放行规则。用域名访问会比直接连接 IP 多出一次 DNS 请求。

**原文链接：**

- [NetworkPolicy 规则与示例](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

</div>
</details>

## 存储与数据持久化

### 容器重启或 Pod 换节点后，哪些数据还能保留

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 容器可写层跟随容器实例，卷有独立的生命周期。选择卷之前，先确定要承受的是单个容器重启、Pod 重建，还是整个节点丢失。

**要答的点：**

- `emptyDir` 供同一 Pod 内的容器共享，容器重启后数据仍在，Pod 被移除后数据随之清理。`hostPath` 指向节点本地文件，换节点后可能看到不同内容。
- ConfigMap、Secret 和 projected 卷适合注入配置或身份材料。数据库数据通常使用 PVC 对接能满足可用性和性能要求的后端存储。

**重点讲解摘录：**

- 跨节点多副本要共享文件时，还要确认后端支持并发挂载和应用所需的一致性语义。单纯给两个 Pod 写相同的挂载路径不会同步文件。

**原文链接：**

- [卷的类型与生命周期](https://kubernetes.io/docs/concepts/storage/volumes/)
- [持久卷、访问模式与回收](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

</div>
</details>

### PV、PVC、StorageClass 和 CSI 怎样串起来

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** PVC 是工作负载在命名空间内提出的容量、访问模式等要求，PV 是集群级的存储资源。StorageClass 指定制备器和参数，CSI 为 Kubernetes 与存储驱动提供通用接口。

**要答的点：**

- 静态供应先准备 PV，控制面选择符合条件的卷与 PVC 绑定。动态供应可根据 StorageClass 创建后端卷和相应 PV。
- CSI 控制器侧可负责创建卷、删除卷和按需挂接，节点侧负责把卷发布给本机工作负载。具体操作取决于驱动能力。

**重点讲解摘录：**

- PVC 一直 Pending 要先看事件。有些存储类设置 `WaitForFirstConsumer`，需要等使用它的 Pod 参与调度，才能在合适的可用区建卷。

**原文链接：**

- [持久卷、访问模式与回收](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [StorageClass 与动态供应](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [CSI 驱动接口](https://github.com/container-storage-interface/spec/blob/master/spec.md)

</div>
</details>

### RWO、ROX、RWX 和 RWOP 的区别是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 卷的访问模式描述挂载约束，尤其要说清限制的是节点还是 Pod。后端与驱动需要支持所选模式。

**要答的点：**

- ReadWriteOnce 允许单节点读写，同一节点的多个 Pod 仍可能使用它。ReadOnlyMany 允许多节点只读，ReadWriteMany 允许多节点读写。
- ReadWriteOncePod 将读写使用限制为集群中的单个 Pod，适用于支持它的 CSI 卷。

**重点讲解摘录：**

- 有状态应用只允许一个活动写者时，先确认访问模式是否满足约束，再考虑应用层锁和故障恢复。RWO 单独不能保证整个集群只有一个写进程。

**原文链接：**

- [持久卷、访问模式与回收](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

</div>
</details>

### PV 有哪些阶段，删除 PVC 后数据会怎样

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** PV 常见阶段是 Available、Bound、Released、Failed。PVC 删除后是否保留后端数据由 PV 的回收策略决定。

**要答的点：**

- Retain 会保留底层存储，待管理员核对数据并手工处理。Delete 会要求支持删除的插件同时清理后端卷及 PV。
- 动态创建的 PV 通常继承 StorageClass 的回收策略，StorageClass 未指定时默认为 Delete。历史 Recycle 策略已弃用。

**重点讲解摘录：**

- Released 表示原声明已释放，旧数据可能仍在。需要在释放 PVC 前确认 PV 自身的策略、备份和数据归属。

**原文链接：**

- [持久卷、访问模式与回收](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [StorageClass 与动态供应](https://kubernetes.io/docs/concepts/storage/storage-classes/)

</div>
</details>

### PVC 空间不够怎样扩容，为什么不直接修改 PV 容量

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先确认 StorageClass 允许 `allowVolumeExpansion`，驱动和后端支持扩容，再调大 PVC 的 `spec.resources.requests.storage`。控制面和驱动负责扩展原卷。

**要答的点：**

- 用 `kubectl describe pvc <claim>` 查看事件和条件，核对 PVC status、后端实际容量，以及容器内文件系统看到的容量。
- 文件系统扩展取决于类型、驱动和挂载状态，有的情况需重新挂载。卷扩展只支持增大。

**重点讲解摘录：**

- 手工把 PV 的容量字段改成目标值，可能让控制面以为扩容已经完成，实际磁盘仍旧不足。

**原文链接：**

- [持久卷、访问模式与回收](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [StorageClass 与动态供应](https://kubernetes.io/docs/concepts/storage/storage-classes/)

</div>
</details>

## etcd 与 Raft

### etcd 保存什么，为什么常用于配置、服务发现和选主

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** etcd 是有版本号的分布式键值存储。Kubernetes 用它保存 API 对象的持久状态。应用进程、容器镜像和持久卷里的业务数据另有各自的存储。

**要答的点：**

- Watch 可以从指定 revision 观察键的变更。若所需历史已被压缩，客户端需要重新读取状态，再从新的 revision 继续。
- 事务支持比较条件后原子更新，租约提供有生命周期的键。两者可以用于配置通知、服务注册以及协调锁和选主。

**重点讲解摘录：**

- 例如把实例注册信息绑定到租约，实例停止续租后键会过期。发现服务的一方消费键变化，真正转发业务流量的仍是客户端或代理。

**原文链接：**

- [etcd 的键值、Watch 与租约](https://etcd.io/docs/v3.6/learning/api/)
- [集群组件](https://kubernetes.io/docs/concepts/overview/components/)

</div>
</details>

### etcd 能用偶数节点吗，三节点和四节点各能坏几台

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 可以。Raft 对投票成员要求严格多数，法定人数是 `⌊N/2⌋ + 1`。3 个成员需要 2 票，4 个需要 3 票，两种配置都只能容忍 1 个成员失效。

**要答的点：**

- 5 个成员需要 3 票，可容忍 2 个失效。增加到 6 个时需要 4 票，容错数仍是 2，这就是常见部署用奇数个投票成员的原因。
- 网络分区时，拥有多数派的一侧可以继续提交写入，少数派无法独立提交。一个两节点集群失去任意一台就无法继续写入。

**重点讲解摘录：**

- 三节点已经掉了一台时，贸然新增第四个投票成员会抬高多数门槛。成员替换要结合当前 quorum 和成员变更流程判断。

**原文链接：**

- [etcd 的多数派与容错](https://etcd.io/docs/v3.6/faq/)

</div>
</details>

### Raft 如何选出 Leader，平票和网络分区后会怎样

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Follower 在选举超时前没有收到有效 Leader 心跳时，可以发起新任期并请求投票。一个候选人要得到多数票，且每个成员在同一任期至多投一票。

**要答的点：**

- 任期号 term 单调递增。比较候选日志的新旧时先看最后一条日志的 term，相同再看 index，以保护已提交日志。
- 平票时本轮无人当选，随机化选举超时让下一轮有机会错开发起投票。旧 Leader 看到更高 term 后转为 Follower。

**重点讲解摘录：**

- 两个网络分区可暂时各自看到不同任期的 Leader 身份，但互不相交的两边无法同时获得同一成员配置的多数派来提交冲突写入。

**原文链接：**

- [Raft 原始论文（图 2）](https://raft.github.io/raft.pdf)
- [etcd 的多数派与容错](https://etcd.io/docs/v3.6/faq/)

</div>
</details>

### 一次 etcd 写入如何复制，落后的 Follower 怎样追上

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Leader 将写操作编码为日志条目，使用 AppendEntries 复制给 Follower。满足多数复制及 Raft 当前任期提交规则后，推进提交位置，各成员按序应用到状态机。

**要答的点：**

- 请求含前一条日志的 index 和 term。Follower 校验前缀后追加条目，如前缀不一致，Leader 回退探测位置，找到共同前缀再补齐。
- Leader 为各 Follower 记录 `nextIndex` 和 `matchIndex`。落后太久且所需日志已压缩时，可以先安装快照再补后续日志。

**重点讲解摘录：**

- 区分“本机写入日志”“集群提交”“状态机已应用”。节点可以暂时落后，Raft 保护的是已经提交的日志顺序。

**原文链接：**

- [Raft 原始论文（图 2）](https://raft.github.io/raft.pdf)
- [检查 etcd 成员与端点状态](https://etcd.io/docs/v3.6/tasks/operator/how-to-check-cluster-status/)

</div>
</details>

### 两个 etcd 端点都报告自己是 Leader，先查什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 题源中的测试集群出现查询结果时有时无、日志报告成员 ID 冲突、端点看似各有 Leader。要先确认比较的是同一集群、同一时间段和同一任期的观测。

**要答的点：**

- 逐端点检查 `etcdctl endpoint status -w json`，对照 cluster ID、member ID、Leader ID、Raft term 和应用进度。结合 `etcdctl member list` 检查成员及 peer URL。
- 对照每个 API Server 的 etcd 端点配置和负载均衡后端。若 cluster ID 不同，应优先调查是否发生了独立引导或误连另一套数据目录。

**重点讲解摘录：**

- 原案例在空的测试环境重建后恢复，根因未证实。生产排查要保留日志、数据目录和可验证快照，再按成员状态与恢复流程决定动作。

**原文链接：**

- [检查 etcd 成员与端点状态](https://etcd.io/docs/v3.6/tasks/operator/how-to-check-cluster-status/)
- [etcd 的多数派与容错](https://etcd.io/docs/v3.6/faq/)
- [etcd 快照与灾难恢复](https://etcd.io/docs/v3.6/op-guide/recovery/)

</div>
</details>

## 访问控制与安全

### 一个 API 请求依次经过哪些访问控制

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** API Server 先认证请求者，再授权其对目标资源执行某个动作。通过后，适用的写请求还会经过准入和对象校验，最后才可能持久化。

**要答的点：**

- 认证可使用客户端证书或 ServiceAccount token。鉴权考虑身份、verb、资源、子资源、命名空间等信息。
- 准入可以先变更对象，再验证最终对象。常见用途包括补默认值、执行 Pod 安全约束和检查组织规则。普通读取请求通常不经过准入控制。

**重点讲解摘录：**

- 凭据无法通过认证时常见 401。身份已确认但授权不足通常是 403。准入也可能拒绝请求，应结合响应中的理由定位。

**原文链接：**

- [API 请求的访问控制](https://kubernetes.io/docs/concepts/security/controlling-access/)
- [准入控制器](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)

</div>
</details>

### RBAC 的四种对象如何组合，怎样验证最小权限

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Role 和 ClusterRole 定义允许的动作，RoleBinding 和 ClusterRoleBinding 把权限绑定给用户、组或 ServiceAccount。RBAC 的授权规则是累加的。

**要答的点：**

- RoleBinding 在自己的命名空间内生效，可引用本地 Role 或可复用的 ClusterRole。ClusterRoleBinding 可授予跨命名空间或集群级权限。
- 资源与子资源分开授权，例如读取 Pod 日志需要 `pods/log`。`kubectl auth can-i get pods --namespace demo` 可检查调用者的实际权限。

**重点讲解摘录：**

- 若应用只需观察本命名空间的 Deployment，可为其专用 ServiceAccount 绑定 get、list、watch 权限，再逐项验证。授予通配权限会连带暴露将来新增的资源或动作。

**原文链接：**

- [RBAC 授权](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [API 请求的访问控制](https://kubernetes.io/docs/concepts/security/controlling-access/)

</div>
</details>

### Secret 如何注入应用，为什么 Base64 保护不了凭据

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Secret 可作为只读卷文件、环境变量或 imagePullSecrets 使用。`data` 字段的 Base64 是可逆编码。持久化加密、访问权限和凭据轮换需要另外配置。

**要答的点：**

- 普通 Secret 卷会最终反映数据更新，但应用需要重新读取文件。通过 subPath 挂载的内容不自动更新。环境变量在容器启动时注入。
- 对 Secret 的 list、watch 权限同样可能泄露内容。还要考虑谁能创建挂载这些 Secret 的 Pod，以及日志和备份的访问范围。

**重点讲解摘录：**

- 轮换数据库密码时，先确认应用能重载文件或安排滚动重启，再撤销旧凭据。只改 Secret 对象可能留下仍使用旧密码的进程。

**原文链接：**

- [Secret 的用法与安全性](https://kubernetes.io/docs/concepts/configuration/secret/)
- [应用安全检查清单](https://kubernetes.io/docs/concepts/security/application-security-checklist/)

</div>
</details>

### PodSecurityPolicy 退役后怎样限制特权容器，集群还需要哪些防线

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 历史上的 PSP 能约束 privileged、宿主机命名空间、卷和提权等行为，已在 v1.25 移除。内置 Pod Security Admission 使用 Pod Security Standards，并可按命名空间配置。

**要答的点：**

- 标准分 privileged、baseline、restricted。模式分 enforce、audit、warn，分别用于拒绝违规 Pod、记录审计信息和向用户提醒。
- Restricted 涉及非 root、禁止提权、能力集和 seccomp 等约束。更细的组织规则可通过额外准入策略实现。

**重点讲解摘录：**

- 上线策略前可先用 warn 和 audit 找出现有违规工作负载。运行时防护还应配合最小 RBAC、网络隔离、凭据保护和可信镜像。

**原文链接：**

- [从 PodSecurityPolicy 迁移](https://kubernetes.io/docs/tasks/configure-pod-container/migrate-from-psp/)
- [Pod 安全准入](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Pod 安全标准](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [应用安全检查清单](https://kubernetes.io/docs/concepts/security/application-security-checklist/)

</div>
</details>

## 指标、日志与集群运维

### kubelet、cAdvisor、Metrics Server 和 kubectl top 怎样串起来

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** kubelet 提供本节点和容器的指标，常见来源是内置的 cAdvisor，某些配置下也可从 CRI 获取容器统计。Metrics Server 从各 kubelet 收集 CPU、内存指标，通过聚合 API 提供给 HPA 和 kubectl top。

**要答的点：**

- `kubectl top pod` 查询的是 `metrics.k8s.io`。若普通 `kubectl get pods` 正常但 top 失败，可以检查该 APIService 是否可用，以及 Metrics Server 到 kubelet 的连通性和证书。
- Heapster 是历史上使用过的指标聚合组件，已经退役。资源指标 API 用于近期 CPU 和内存观测，长期趋势和告警通常还需独立的时序监控系统。

**重点讲解摘录：**

- 单个节点缺指标时优先沿该节点的采集链路调查。所有节点都缺时先检查聚合 API 和 Metrics Server。业务延迟等自定义指标需要对应的适配器。

**原文链接：**

- [节点指标与 kubelet 统计接口](https://kubernetes.io/docs/reference/instrumentation/node-metrics/)
- [资源指标链路](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- [Heapster 项目退役说明](https://github.com/kubernetes-retired/heapster)

</div>
</details>

### 怎样用 EFK 汇总日志，Pod 删除后还能怎样查

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** EFK 常指 Elasticsearch、Fluentd 和 Kibana。节点采集代理读取容器标准输出和标准错误对应的日志文件，附加 Pod、容器和命名空间信息，再发送到集中存储。

**要答的点：**

- 采集代理常以 DaemonSet 部署，读取节点日志路径。要处理日志轮转、断点续传、缓冲和重复投递，并区分应用事件时间与采集时间。
- `kubectl logs <pod> -c <container> --previous` 可读取同一 Pod 中该容器上一实例仍保留的日志。Pod 或节点已消失时，集中日志的价值才真正体现。

**重点讲解摘录：**

- 追一次跨副本请求，用时间窗口、命名空间、Pod UID 和请求 ID 组合过滤。只按 Pod 名过滤容易漏掉重建后的实例。

**原文链接：**

- [Kubernetes 日志架构](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [DaemonSet 的调度过程](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)

</div>
</details>

### 怎样维护一个节点，cordon、drain 和 PDB 各管什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 先确认副本分布、集群余量和干扰预算，再 cordon 阻止常规新调度，drain 请求驱逐已有工作负载，验证替代 Pod 就绪后再停机。维护完成后 uncordon 恢复调度。

**要答的点：**

- `kubectl cordon <node>` 不会迁走已有 Pod。`kubectl drain <node> --ignore-daemonsets` 使用驱逐流程时会遵守 PDB，DaemonSet Pod 和镜像 Pod 需要区别处理。
- PDB 约束自愿干扰可同时造成的不可用数。如果单副本应用要求至少一个可用，驱逐可能一直被阻止。此时要协调容量或维护安排。

**重点讲解摘录：**

- emptyDir 数据随 Pod 被删除而丢失，本地卷和有状态服务还需核对数据与拓扑约束。节点维护能否无感，应通过端点就绪和业务请求验证。

**原文链接：**

- [安全排空节点](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)
- [Pod 干扰预算](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)

</div>
</details>

### 两个负载均衡节点同时持有 VIP，怎样验证原因

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 题源中的 Keepalived 案例里，备节点报告 VRRP 通告超时并接管 VIP，主节点仍持有该地址。客户端请求一时正常，也不能据此判断主备切换健康。

**要答的点：**

- 先在两端核对 VIP、VRRP 实例的 VRID、优先级、接口和时间线。同时抓取协议号 112 的报文，确认主端是否发出、备端是否收到，以及哪一端在回应 ARP。
- 若发送端有通告、接收端没有，要查中间网络的组播转发、防火墙和丢包。若双方都收得到，则检查配置匹配、源地址校验及健康检查引发的角色变化。

**重点讲解摘录：**

- 原案例调整心跳间隔后曾复发，改为显式单播对端后未再观察到。应把恢复现象和已经验证的根因分开，并用双端抓包及实际 VIP 故障切换复核。

**原文链接：**

- [Keepalived 的 VRRP 配置](https://www.keepalived.org/documentation/keepalived-conf/)

</div>
</details>

### Helm 的 Chart、Release 和 values 分别是什么

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** Chart 是一组模板、默认配置和元数据。安装时 Helm 用 values 渲染 Kubernetes 清单，一次带名称的安装形成独立 release，可跟踪修订、升级和回滚。

**要答的点：**

- `helm template` 可先检查渲染结果，`helm upgrade --install` 创建或更新 release，`helm history` 和 `helm rollback` 用于查看修订及回退。
- 同一 Chart 可在不同命名空间安装多个 release。排查差异时，要同时核对 Chart 版本、覆盖的 values 和集群里的实际资源。

**重点讲解摘录：**

- 如果新版本同时迁移了数据库，Helm 回滚模板只影响其管理的发布资源。数据兼容和回退方案需要单独设计。

**原文链接：**

- [Helm 的 Chart、Release 和仓库](https://helm.sh/docs/intro/using_helm/)

</div>
</details>

### 集群联邦或多集群管理解决什么问题

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 多集群管理把工作负载的分发、放置策略和状态汇总集中起来，各成员集群仍有自己的控制面。常见诉求有跨地域容灾、隔离故障域和按可用容量分配副本。

**要答的点：**

- 以 Karmada 为例，传播策略选择哪些资源下发，调度策略决定目标成员和副本放置，覆盖策略处理不同集群的配置差异。
- 跨集群服务发现、入口流量切换、镜像可达和数据复制需要明确实现。把同一份 Deployment 下发到两地只解决了应用分发。

**重点讲解摘录：**

- 面试中可以用区域故障解释边界。备用集群即使拥有足够副本，也要等入口切流、依赖可用且数据满足恢复要求，才能真正接管请求。

**原文链接：**

- [Karmada 多集群架构](https://karmada.io/docs/core-concepts/architecture/)

</div>
</details>
