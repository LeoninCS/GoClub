---
title: "计算机网络"
---

# 计算机网络

这里整理计算机网络面试里的常见问题，覆盖 DNS、TCP、HTTP、HTTPS 和排障思路等主题。

## 基础

### 输入一个 URL 会发生什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这个过程我一般按五步说：第一步先做 DNS 解析，把域名变成 IP；第二步和服务端建立连接，HTTP 是 TCP 三次握手，HTTPS 还要多一次 TLS 握手；第三步浏览器发请求，服务端返回 HTML、CSS、JS 等资源；第四步浏览器做解析和渲染，构建 DOM、CSSOM，再布局和绘制；最后连接会复用或者关闭。整体上就是“解析 -> 建连 -> 请求响应 -> 渲染 -> 连接管理”。面试里可按三点展开：DNS 解析（本地缓存 -> 递归/权威解析）；TCP 三次握手；HTTPS 还包含 TLS 握手；浏览器构建 DOM/CSSOM，布局绘制。

**关键点：**
- DNS 解析（本地缓存 -> 递归/权威解析）。
- TCP 三次握手；HTTPS 还包含 TLS 握手。
- 浏览器构建 DOM/CSSOM，布局绘制。

</div>
</details>

### 域名和 IP 的关系是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** IP 是网络里的真实地址，域名是给人看的可读名字。我们访问网站时其实最终都要落到 IP 上，DNS 就是做这层映射。并且映射关系不是一对一的，一个域名可以对应多个 IP 做负载均衡，多个域名也可以指向同一个 IP 做虚拟主机。面试里可按两点展开：一个域名可对应多个 IP（负载均衡）；多个域名也可指向同一 IP（虚拟主机）。

**关键点：**
- 一个域名可对应多个 IP（负载均衡）。
- 多个域名也可指向同一 IP（虚拟主机）。

</div>
</details>

### DNS 是什么协议？解析流程是怎样的？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** DNS 是应用层协议，平时查询多数走 UDP 53 端口，少数大报文或区域传送会用 TCP。解析时它是分层查找：先问根域名服务器，再问顶级域服务器，最后到权威 DNS 拿到结果，然后客户端会按 TTL 做缓存，所以同一个域名短时间重复访问通常更快。面试里可按三点展开：典型路径：根域名 -> 顶级域 -> 权威域名服务器；大报文或区域传送会用 TCP；结果会按 TTL 缓存。

**关键点：**
- 典型路径：根域名 -> 顶级域 -> 权威域名服务器。
- 大报文或区域传送会用 TCP。
- 结果会按 TTL 缓存。

</div>
</details>

### 网站访问异常时如何定位问题？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 我会按分层思路排查，先看应用层再看网络层。先确认状态码和服务日志，判断是 4xx 还是 5xx；再用 `ping` 看连通性、`traceroute` 看链路在哪一跳出问题；然后用 `nc/telnet` 验证端口是否可达；最后用 `nslookup/dig` 看 DNS 解析是不是指到了错误地址。这样基本能快速缩小问题范围。面试里可按三点展开：看状态码（4xx/5xx）；`ping`、`traceroute/tracert` 查连通性与链路；`nc/telnet` 测端口，`nslookup/dig` 查 DNS。

**关键点：**
- 看状态码（4xx/5xx）。
- `ping`、`traceroute/tracert` 查连通性与链路。
- `nc/telnet` 测端口，`nslookup/dig` 查 DNS。

</div>
</details>

## HTTP

### HTTP/1.1、HTTP/2、HTTP/3 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这三个版本核心就是不断优化性能和时延。HTTP/1.1 还是文本协议，请求复用能力有限；HTTP/2 变成二进制分帧，支持多路复用和头部压缩，性能提升明显；HTTP/3 直接基于 QUIC，也就是 UDP 之上做可靠传输，在弱网和连接迁移场景下体验更好，握手时延也更低。面试里可按三点展开：HTTP/1.1：文本协议，复用能力弱；HTTP/2：二进制分帧、多路复用、HPACK；HTTP/3：基于 QUIC（UDP），握手和弱网表现更好。

**关键点：**
- HTTP/1.1：文本协议，复用能力弱。
- HTTP/2：二进制分帧、多路复用、HPACK。
- HTTP/3：基于 QUIC（UDP），握手和弱网表现更好。

</div>
</details>

### HTTPS 的 S 是什么？核心原理是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** HTTPS 里的 S 就是 Secure，本质是 HTTP + TLS。TLS 握手阶段用非对称机制协商出会话密钥，后续业务数据用对称加密传输保证效率。同时通过 CA 证书链校验服务端身份，防止中间人攻击。可以理解成“握手阶段保安全，传输阶段保性能”。面试里可按三点展开：非对称用于协商密钥；对称用于业务数据加密；证书链用于身份校验，防中间人。

**关键点：**
- 非对称用于协商密钥。
- 对称用于业务数据加密。
- 证书链用于身份校验，防中间人。

</div>
</details>

### 为什么有了 HTTP，还要 RPC 和 WebSocket？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 因为它们解决的问题不一样。HTTP 更通用，适合对外接口；RPC 更适合服务内部调用，强调性能和治理能力；WebSocket 适合实时双向通信，比如聊天和推送。所以不是替代关系，而是按场景选型：对外用 HTTP、内调用 RPC、实时连接用 WebSocket。面试里可按三点展开：HTTP：跨平台通用；RPC：内部服务性能与治理更好；WebSocket：长连接、服务端主动推送。

**关键点：**
- HTTP：跨平台通用。
- RPC：内部服务性能与治理更好。
- WebSocket：长连接、服务端主动推送。

</div>
</details>

## TCP

### TCP 为什么是三次握手？为什么不是两次？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三次握手的目的，是让客户端和服务端都确认“发送和接收能力正常”，同时同步初始序列号。两次握手只能保证一部分状态，不能完整确认客户端对服务端报文的接收情况，容易留下半连接或历史报文干扰的问题，所以 TCP 选择三次握手作为可靠建立连接的最小成本方案。面试里可按两点展开：客户端和服务端都要确认“我发你能收、你发我能收”；两次握手无法充分确认客户端接收能力。

**关键点：**
- 客户端和服务端都要确认“我发你能收、你发我能收”。
- 两次握手无法充分确认客户端接收能力。

</div>
</details>

### 三次握手和四次挥手分别是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 建连是三次：`SYN -> SYN+ACK -> ACK`。断连通常四次：`FIN -> ACK -> FIN -> ACK`。之所以挥手多一次，是因为 TCP 是全双工，两个方向要分别关闭：我不发了不代表我不收了，所以双方都要各自发 FIN 并确认。面试里可按三点展开：握手建立连接；挥手释放连接；挥手常是四次因为全双工双方独立关闭。

**关键点：**
- 握手建立连接。
- 挥手释放连接。
- 挥手常是四次因为全双工双方独立关闭。

</div>
</details>

### TCP 和 UDP 的核心区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** TCP 是面向连接且可靠的协议，有重传、有序、流控和拥塞控制，适合对可靠性要求高的场景；UDP 是无连接、尽力而为，开销小、时延低，更适合实时性优先的场景。简单说就是 TCP 要“稳”，UDP 要“快”。面试里可按三点展开：TCP：连接、重传、流控、拥塞控制；UDP：无连接、尽力而为；场景：TCP 偏事务传输，UDP 偏实时音视频/游戏。

**关键点：**
- TCP：连接、重传、流控、拥塞控制。
- UDP：无连接、尽力而为。
- 场景：TCP 偏事务传输，UDP 偏实时音视频/游戏。

</div>
</details>

### TCP 的滑动窗口、流量控制、拥塞控制是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 这三块分别解决不同问题。滑动窗口是提升发送效率，让发送端可以连续发多个包；流量控制是避免接收端处理不过来，通过接收窗口限制发送速率；拥塞控制是避免把网络打崩，根据网络状态动态调节发送速率，典型过程包括慢启动、拥塞避免、快重传和快恢复。面试里可按三点展开：滑动窗口：提高链路利用率；流量控制：防止接收端被打爆；拥塞控制：慢启动、拥塞避免、快重传、快恢复。

**关键点：**
- 滑动窗口：提高链路利用率。
- 流量控制：防止接收端被打爆。
- 拥塞控制：慢启动、拥塞避免、快重传、快恢复。
</div>
</details>
