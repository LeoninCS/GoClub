---
title: "计算机网络"
aliases:
  - "/s/xidg/"
shortlink: "xidg"
---

# 计算机网络

这里整理计算机网络面试里的常见问题，覆盖 DNS、TCP、HTTP、HTTPS 和排障思路等主题。

## 基础

### 输入一个 URL 会发生什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 浏览器输入 URL 后，先解析 URL 并确定协议、域名、端口和路径；然后通过缓存和 DNS 系统把域名解析成 IP；再建立传输连接，HTTP/1.1 和 HTTP/2 常走 TCP，HTTPS 还要完成 TLS 握手，HTTP/3 走 QUIC；连接建立后浏览器发送 HTTP 请求，服务端返回响应；浏览器解析 HTML，下载 CSS、JS、图片等资源，构建 DOM/CSSOM，完成布局、绘制和合成。连接后续可能复用，也可能按协议和服务端策略关闭。

**要答的点：**
- URL 解析：确定 scheme、host、port、path、query。
- DNS：先查浏览器/系统/本地 DNS 缓存，再走递归解析和权威解析。
- 建连：TCP 三次握手；HTTPS 增加 TLS 握手；HTTP/3 基于 QUIC。
- 请求响应：发送 HTTP 请求，服务端处理后返回状态码、响应头和响应体。
- 渲染：解析 HTML/CSS/JS，构建 DOM、CSSOM、渲染树，布局、绘制、合成。
- 连接管理：Keep-Alive、多路复用、缓存、重定向、Cookie 等都会影响真实链路。

**重点讲解摘录：**
- MDN 的 Web 工作原理文章把过程拆成 DNS 找到服务器地址、浏览器向服务器发送请求、服务器返回页面副本。
- MDN 浏览器渲染文档提到，浏览器得到资源后会解析 HTML、CSS、JavaScript，再进行布局和绘制。
- RFC 9293 把 TCP 建连称为 “three-way handshake”，这是 HTTP over TCP 的基础。
- RFC 8446 说明 TLS 的目标是为通信应用提供安全通道，HTTPS 的安全性来自这一层。
- RFC 9114 说明 HTTP/3 使用 QUIC 传输，适合回答 HTTP/3 和前两代的建连差异。

**原文链接：**
- [MDN: How the web works](https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works)
- [MDN: Populating the page: how browsers work](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/How_browsers_work)
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 8446: The Transport Layer Security Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [RFC 9114: HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)

</div>
</details>

### 域名和 IP 的关系是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** IP 是网络通信使用的地址，域名是面向人的可读名字，DNS 负责把域名映射到 IP。一个域名可以解析到多个 IP，用于负载均衡、容灾和就近访问；多个域名也可以指向同一个 IP，服务器再通过 Host 头或 SNI 区分站点。面试时可以把域名理解成“服务名”，把 IP 理解成“服务当前可达的网络位置”。

**要答的点：**
- IP：网络层寻址标识，IPv4 常见 32 位，IPv6 常见 128 位。
- 域名：层级化、可读、可缓存的名字。
- DNS 记录：A 记录对应 IPv4，AAAA 记录对应 IPv6，CNAME 做别名。
- 多 IP：同一域名可返回多个地址做负载均衡和容灾。
- 多域名同 IP：虚拟主机和反向代理按 Host/SNI 路由。
- TTL：解析结果会按 TTL 缓存，域名变更需要考虑缓存窗口。

**重点讲解摘录：**
- RFC 1034 说明 DNS 的目标是提供一种一致的名字空间，用于引用资源。
- RFC 1035 定义 A 记录把域名映射到 IPv4 地址。
- RFC 3596 定义 AAAA 记录用于 IPv6 地址。
- MDN 的 Web 工作原理文章把 DNS 类比为查找网站真实地址的过程。
- HTTP 规范里的 Host 字段让同一 IP 上承载多个源站成为常见实践。

**原文链接：**
- [RFC 1034: Domain Names - Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034)
- [RFC 1035: Domain Names - Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 3596: DNS Extensions to Support IP Version 6](https://www.rfc-editor.org/rfc/rfc3596)
- [MDN: How the web works](https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)

</div>
</details>

### DNS 是什么协议？解析流程是怎样的？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** DNS 是应用层的分布式命名系统，常见查询使用 UDP 53，响应较大、区域传送、部分扩展场景会使用 TCP 53。解析流程一般是客户端先查本地缓存，再把请求交给递归解析器；递归解析器按根域名服务器、顶级域服务器、权威域名服务器的层级逐步查询，拿到记录后按 TTL 缓存并返回客户端。

**要答的点：**
- 协议定位：DNS 是应用层协议，服务于域名到资源记录的查询。
- 传输方式：普通查询常走 UDP 53，TCP 用于大响应、区域传送等场景。
- 查询角色：客户端 stub resolver、递归解析器、根服务器、TLD、权威服务器。
- 解析路径：本地缓存 -> 递归解析器 -> 根 -> TLD -> 权威 -> 返回记录。
- 缓存机制：结果按 TTL 缓存，降低延迟和权威服务器压力。
- 记录类型：A、AAAA、CNAME、MX、TXT、NS 都是常见面试追问。

**重点讲解摘录：**
- RFC 1034 描述 DNS 是层级化、分布式的数据库。
- RFC 1035 定义 DNS 使用 53 端口，并描述 UDP 和 TCP 两种传输。
- Cloudflare DNS 文档把递归解析器描述为代表客户端完成后续查询的角色。
- RFC 7766 说明 DNS over TCP 是完整协议要求的一部分，大响应和现代扩展场景会依赖它。
- DNS TTL 控制缓存有效期，面试排障时常和“改了域名仍访问旧地址”一起出现。

**原文链接：**
- [RFC 1034: Domain Names - Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034)
- [RFC 1035: Domain Names - Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [RFC 7766: DNS Transport over TCP](https://www.rfc-editor.org/rfc/rfc7766)
- [Cloudflare Learning Center: What is DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/)

</div>
</details>

### 网站访问异常时如何定位问题？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 我会按“客户端、DNS、网络、端口、TLS、HTTP、服务端”分层定位。先看浏览器报错、状态码和服务日志；再用 `dig/nslookup` 看域名解析，用 `ping/traceroute` 看连通性和路径，用 `nc/curl` 看端口、TLS 和 HTTP 响应；如果服务端返回 5xx，就看网关、应用日志、依赖服务、数据库和资源指标。这样能快速把问题缩小到解析、链路、证书、应用或下游依赖。

**要答的点：**
- 客户端现象：状态码、错误码、请求耗时、是否仅某地区或某用户异常。
- DNS：`dig`/`nslookup` 查解析结果、TTL、CNAME 链路和权威结果。
- 网络：`ping` 看基本连通，`traceroute`/`mtr` 看路径和丢包。
- 端口/TLS：`nc -vz host port`、`curl -v`、`openssl s_client` 看握手和证书。
- HTTP：看 3xx/4xx/5xx、响应头、网关日志、应用日志。
- 服务端：CPU、内存、连接数、线程池、数据库、缓存、队列和限流状态。

**重点讲解摘录：**
- curl 文档说明 `-v` 会输出请求和响应细节，适合排查连接、TLS 和 HTTP 头。
- Linux `traceroute` 文档说明它会打印到目标主机的路由路径。
- `dig` 文档把它定位为 DNS 查询工具，适合查看权威解析和递归结果。
- OpenSSL `s_client` 可建立 TLS/SSL 客户端连接并输出证书链与握手信息。
- HTTP 状态码语义来自 RFC 9110，4xx 指向客户端请求问题，5xx 指向服务端处理问题。

**原文链接：**
- [curl: command line tool and library for transferring data with URLs](https://curl.se/docs/manpage.html)
- [Linux man-pages: traceroute(8)](https://man7.org/linux/man-pages/man8/traceroute.8.html)
- [BIND 9: dig](https://bind9.readthedocs.io/en/latest/manpages.html#dig)
- [OpenSSL: s_client](https://docs.openssl.org/master/man1/openssl-s_client/)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)

</div>
</details>

## HTTP

### HTTP/1.1、HTTP/2、HTTP/3 的区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** HTTP/1.1 是文本协议，连接复用主要靠 Keep-Alive，同一连接上的请求响应仍容易受队头阻塞影响；HTTP/2 引入二进制分帧、流、多路复用和 HPACK 头部压缩，一个 TCP 连接可以并发承载多个请求；HTTP/3 保留 HTTP 语义，底层改用 QUIC，获得更快握手、连接迁移和流级别的阻塞控制。面试里按“文本到二进制、单路到多路、TCP 到 QUIC”回答最清晰。

**要答的点：**
- HTTP/1.1：文本报文、持久连接、管线化实践有限，常用多连接提高并发。
- HTTP/2：二进制分帧、Stream 多路复用、HPACK 头部压缩、服务端推送曾经存在。
- HTTP/2 的瓶颈：底层仍是 TCP，丢包会影响同连接所有流的交付。
- HTTP/3：基于 QUIC，运行在 UDP 之上，内置 TLS 1.3 安全能力。
- QUIC 优势：连接迁移、较低握手时延、流之间独立恢复。
- 面试收口：HTTP 语义基本延续，性能优化主要发生在连接和传输层。

**重点讲解摘录：**
- MDN HTTP 演进文档说明 HTTP/2 是二进制协议，并支持多路复用。
- RFC 9113 说明 HTTP/2 使用 frame 和 stream 承载 HTTP 语义。
- RFC 9114 说明 HTTP/3 “uses QUIC as a transport”。
- RFC 9000 说明 QUIC 在 UDP 上提供可靠传输、安全和多路复用。
- MDN 提到 HTTP/3 保留早期 HTTP 语义，传输层改为 QUIC。

**原文链接：**
- [MDN: Evolution of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Evolution_of_HTTP)
- [RFC 9112: HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112)
- [RFC 9113: HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)
- [RFC 9114: HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)

</div>
</details>

### HTTPS 的 S 是什么？核心原理是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** HTTPS 的 S 是 Secure，本质是 HTTP over TLS。TLS 提供三类能力：通过证书链验证服务端身份；通过密钥协商生成会话密钥；通过对称加密和完整性校验保护后续 HTTP 数据。握手阶段使用非对称密码学和 ECDHE 这类密钥交换建立共享密钥，传输阶段使用 AES-GCM 或 ChaCha20-Poly1305 这类 AEAD 算法高效加密。

**要答的点：**
- HTTPS：HTTP 语义加 TLS 安全层，默认端口 443。
- 身份认证：浏览器验证服务端证书链、域名、有效期和信任根。
- 密钥协商：TLS 握手协商协议版本、加密套件和共享密钥。
- 数据保护：业务数据用对称加密传输，并带完整性校验。
- TLS 1.3：握手更简化，默认使用前向安全的密钥交换。
- 风险点：证书过期、域名和证书不匹配、弱协议和弱加密套件都会导致安全问题。

**重点讲解摘录：**
- RFC 8446 说明 TLS 的目标是为两个通信应用提供安全通道。
- TLS 1.3 握手通过 ClientHello、ServerHello、EncryptedExtensions、Certificate 等消息建立安全参数。
- MDN HTTPS 文档把 HTTPS 描述为使用 TLS 加密的 HTTP。
- CA/Browser Forum 规则是浏览器证书信任生态的重要基础。
- 面试时可以把 TLS 拆成“认证、协商、加密、完整性”四个关键词。

**原文链接：**
- [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [MDN: HTTPS](https://developer.mozilla.org/en-US/docs/Glossary/HTTPS)
- [MDN: Transport Layer Security](https://developer.mozilla.org/en-US/docs/Glossary/TLS)
- [CA/Browser Forum: Baseline Requirements](https://cabforum.org/baseline-requirements-documents/)

</div>
</details>

### 为什么有了 HTTP，还要 RPC 和 WebSocket？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** HTTP、RPC、WebSocket 关注的场景不同。HTTP 适合开放接口和资源访问，生态通用、调试方便、跨语言跨平台；RPC 适合服务内部调用，强调接口契约、序列化效率、连接复用、负载均衡和治理能力；WebSocket 适合客户端和服务端保持一条双向长连接，用于聊天、协作、行情推送和在线状态。对外 API 常用 HTTP，内部服务常用 RPC，实时双向通信常用 WebSocket。

**要答的点：**
- HTTP：资源语义清晰，浏览器和网关生态成熟，适合 REST/开放 API。
- RPC：像调用本地函数一样调用远程服务，IDL 约束接口，适合微服务内部通信。
- gRPC：基于 HTTP/2，使用 Protocol Buffers，支持流式调用。
- WebSocket：HTTP Upgrade 后建立全双工连接，服务端可主动推送。
- 选型：公网开放、调试和缓存重 HTTP；低延迟内部调用重 RPC；强实时双向重 WebSocket。

**重点讲解摘录：**
- RFC 9110 定义 HTTP 语义和请求响应模型，适合资源访问。
- gRPC 文档说明它可以像调用本地对象一样调用另一台机器上的服务。
- Protocol Buffers 文档强调结构化数据序列化，适合 RPC 接口契约。
- RFC 6455 说明 WebSocket 目标是在单个 TCP 连接上提供双向通信。
- MDN WebSocket 文档把 WebSocket 描述为浏览器和服务器之间的双向交互通信会话。

**原文链接：**
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [gRPC: Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [Protocol Buffers: Overview](https://protobuf.dev/overview/)
- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)
- [MDN: WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

</div>
</details>

## TCP

### TCP 为什么是三次握手？为什么不是两次？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三次握手用于建立连接状态、同步双方初始序列号，并确认双方的发送和接收能力都可用。第一次客户端发 SYN，服务端确认客户端的发送能力和自己的接收能力；第二次服务端回 SYN+ACK，客户端确认服务端的发送能力和自己的接收能力；第三次客户端回 ACK，服务端确认客户端收到了自己的 SYN。三次也能处理历史 SYN 报文延迟到达的场景，减少服务端误建连接和资源浪费。

**要答的点：**
- SYN：客户端发起连接并携带初始序列号。
- SYN+ACK：服务端确认客户端序列号，并发送自己的初始序列号。
- ACK：客户端确认服务端序列号，双方进入 ESTABLISHED。
- 核心目的：双向能力确认、初始序列号同步、连接状态建立。
- 历史报文：延迟的旧 SYN 会在握手确认过程中暴露，降低误建连接风险。
- 工程追问：SYN flood、半连接队列、`TIME_WAIT` 常和这题一起考。

**重点讲解摘录：**
- RFC 9293 把建立连接的过程称为 “three-way handshake”。
- RFC 9293 说明连接建立需要同步双方初始序列号。
- TCP 头部里的 SYN、ACK 标志位就是三次握手的核心控制信号。
- 初始序列号用于后续可靠传输、重传、去重和有序交付。
- 面试回答要把“三次”落到双方都确认对方序列号和收发能力上。

**原文链接：**
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 793: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc793)

</div>
</details>

### 三次握手和四次挥手分别是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三次握手是 `SYN -> SYN+ACK -> ACK`，用于建立连接和同步初始序列号。四次挥手通常是 `FIN -> ACK -> FIN -> ACK`，用于释放连接的两个方向。TCP 是全双工协议，一个方向发送完 FIN 只代表该方向发送结束，另一个方向仍可能继续发送数据，所以关闭连接通常需要双方分别发送 FIN 并收到 ACK。主动关闭方最后进入 `TIME_WAIT`，用于处理迟到报文和保证对端收到最后的 ACK。

**要答的点：**
- 三次握手：客户端 SYN，服务端 SYN+ACK，客户端 ACK。
- 四次挥手：主动方 FIN，被动方 ACK；被动方 FIN，主动方 ACK。
- 全双工：读方向和写方向可以独立关闭。
- 半关闭：收到 FIN 后仍可继续发送剩余数据。
- TIME_WAIT：主动关闭方等待 2MSL，消化旧报文并补发最后 ACK。
- 状态名：`SYN_SENT`、`SYN_RECEIVED`、`ESTABLISHED`、`FIN_WAIT`、`CLOSE_WAIT`、`TIME_WAIT`。

**重点讲解摘录：**
- RFC 9293 定义 SYN、FIN、ACK 标志位以及连接状态机。
- RFC 9293 说明 FIN 用于表示发送方已经结束发送数据。
- TCP 状态机把主动关闭和被动关闭拆成多个状态，体现全双工关闭过程。
- TIME_WAIT 是主动关闭方常见追问，和端口复用、迟到报文处理相关。
- 面试时可以画出两条方向：客户端发送方向关闭、服务端发送方向关闭。

**原文链接：**
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 793: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc793)

</div>
</details>

### TCP 和 UDP 的核心区别

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** TCP 是面向连接的可靠字节流协议，提供重传、有序交付、流量控制和拥塞控制，适合文件传输、网页、数据库连接、RPC 等可靠性优先场景。UDP 是无连接的数据报协议，头部小、交付路径短，适合实时音视频、游戏、DNS、QUIC 这类更关注时延或应用层自定义可靠性的场景。面试里按“连接、可靠性、顺序、控制、场景”五个维度对比即可。

**要答的点：**
- 连接：TCP 先建连，UDP 直接发数据报。
- 数据形态：TCP 是字节流，UDP 保留报文边界。
- 可靠性：TCP 负责确认、重传、去重、有序；UDP 把可靠性留给应用层。
- 控制能力：TCP 有流量控制和拥塞控制；UDP 头部简单，控制能力由应用补充。
- 头部开销：TCP 基础头部 20 字节，UDP 基础头部 8 字节。
- 场景：TCP 用于可靠传输，UDP 用于实时和自定义传输，例如 QUIC。

**重点讲解摘录：**
- RFC 9293 定义 TCP 是可靠的、面向连接的端到端协议。
- RFC 768 定义 UDP 是面向事务的数据报协议，协议机制很轻。
- TCP 的序列号、ACK、窗口和重传共同完成可靠有序交付。
- UDP 的报文边界适合 DNS、RTP、QUIC 这类协议在上层设计自己的语义。
- RFC 9000 说明 QUIC 在 UDP 上实现可靠传输、安全和多路复用。

**原文链接：**
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 768: User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)

</div>
</details>

### TCP 的滑动窗口、流量控制、拥塞控制是什么？

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 滑动窗口是 TCP 提高吞吐的机制，允许发送端在收到前面数据 ACK 之前继续发送窗口内的数据；流量控制保护接收端，通过接收窗口 `rwnd` 告诉发送端自己还能接收多少；拥塞控制保护网络，通过拥塞窗口 `cwnd` 根据丢包、延迟和 ACK 情况调节发送速率。真正可发送的数据量通常受 `min(rwnd, cwnd)` 约束。

**要答的点：**
- 滑动窗口：窗口随 ACK 前移，支持连续发送和乱序确认后的有序交付。
- 流量控制：接收端通告窗口，避免发送端把接收缓冲区打满。
- 拥塞控制：发送端估计网络承载能力，动态调整 `cwnd`。
- 常见算法：慢启动、拥塞避免、快重传、快恢复。
- 窗口关系：发送窗口受接收窗口和拥塞窗口共同限制。
- 追问方向：零窗口、Nagle、延迟 ACK、BBR/CUBIC。

**重点讲解摘录：**
- RFC 9293 定义 TCP 窗口字段用于流量控制。
- RFC 5681 说明 TCP 拥塞控制包含 slow start、congestion avoidance、fast retransmit、fast recovery。
- 滑动窗口让 TCP 在长 RTT 链路上保持管道里有数据，提高链路利用率。
- 接收窗口是接收端能力反馈，拥塞窗口是网络能力估计。
- 面试里把“保护接收端”和“保护网络”分开讲，答案会清楚很多。

**原文链接：**
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)

</div>
</details>
