# RabbitMQ

这里主要整理消息队列相关的高频面试题，包括 RabbitMQ、自身机制以及和 Kafka、RocketMQ 的对比。

## 1. RabbitMQ、Kafka、RocketMQ 对比

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 三者都能做异步解耦与削峰，定位分别是：RabbitMQ 更通用灵活，Kafka 更偏高吞吐日志流，RocketMQ 更偏业务消息与事务消息。面试里可以按“核心优势 + 适合场景”展开。

| 消息队列 | 核心优势 | 适合场景 |
| --- | --- | --- |
| RabbitMQ | AMQP 支持成熟，Exchange 路由能力强，Direct、Topic、Fanout 等模型灵活，生态成熟、使用简单 | 业务系统解耦、任务队列、后台异步处理、复杂路由、失败重试 |
| Kafka | 吞吐量高，分区并行能力强，顺序追加写性能好，消费位点管理清晰 | 日志采集、埋点上报、实时计算、数据管道、事件流平台 |
| RocketMQ | 事务消息、顺序消息、延时消息、消息轨迹等业务能力完善 | 电商订单、金融支付、交易链路、分布式事务最终一致性 |

**关键点：**
- RabbitMQ：路由灵活，适合业务解耦和任务异步。
- Kafka：吞吐量高，适合日志流和大数据链路。
- RocketMQ：业务消息能力完善，适合订单、支付、交易等链路。

</div>
</details>

## 2. 消息队列的作用和使用场景

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 主要作用是异步解耦、削峰填谷、系统间可靠通信。面试里可按两点展开：下单后异步发短信、发券、积分；流量高峰时缓冲请求，保护下游。


**关键点：**
- 下单后异步发短信、发券、积分。
- 流量高峰时缓冲请求，保护下游。

</div>
</details>

## 3. 如何保证消息队列可靠性

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 要从“生产、存储、消费”三段都做可靠性设计。面试里可按三点展开：生产端：发送确认、重试、落库补偿；Broker：持久化、镜像/副本、ACK 机制；消费端：手动 ACK、失败重试、死信队列。


**关键点：**
- 生产端：发送确认、重试、落库补偿。
- Broker：持久化、镜像/副本、ACK 机制。
- 消费端：手动 ACK、失败重试、死信队列。

</div>
</details>

## 4. 如何防止消息重复消费（幂等）

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 重复消费无法完全避免，核心是消费端幂等。面试里可按三点展开：业务唯一键去重（订单号/消息 ID）；幂等表或状态机校验；保证“重复执行结果一致”。


**关键点：**
- 业务唯一键去重（订单号/消息 ID）。
- 幂等表或状态机校验。
- 保证“重复执行结果一致”。

</div>
</details>

## 5. 消息积压会发生什么，如何解决

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 积压会导致延迟升高、超时、甚至服务雪崩。面试里可按三点展开：临时扩容消费者和分区并发；提升消费逻辑性能，拆分慢处理链路；必要时限流、降级、转离线处理。


**关键点：**
- 临时扩容消费者和分区并发。
- 提升消费逻辑性能，拆分慢处理链路。
- 必要时限流、降级、转离线处理。

</div>
</details>

## 6. 消息队列算哪种设计模式

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 更接近架构模式中的“发布-订阅”和“生产者-消费者”模式。面试里可按两点展开：发布订阅：一条消息多订阅者；生产者消费者：削峰与并发处理。


**关键点：**
- 发布订阅：一条消息多订阅者。
- 生产者消费者：削峰与并发处理。

</div>
</details>

## 7. RabbitMQ 底层架构是什么样的

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 核心组件是 Producer、Exchange、Queue、Consumer，消息先到 Exchange，再按规则路由到 Queue。面试里可按三点展开：Exchange 不存消息，只做路由；Queue 负责存储与投递；连接基于 TCP，通道基于 Channel 复用。


**关键点：**
- Exchange 不存消息，只做路由。
- Queue 负责存储与投递。
- 连接基于 TCP，通道基于 Channel 复用。

</div>
</details>

## 8. RabbitMQ 的交换机类型

<details class="qa-answer">
<summary class="qa-answer-toggle">查看答案</summary>

<div class="qa-answer-body">

**可直接说：** 常见有 Direct、Topic、Fanout、Headers 四种。面试里可按三点展开：Direct：精确路由键匹配；Topic：通配符匹配（`*`、`#`）；Fanout：广播到所有绑定队列。


**关键点：**
- Direct：精确路由键匹配。
- Topic：通配符匹配（`*`、`#`）。
- Fanout：广播到所有绑定队列。
- Headers：按消息头匹配，使用较少。
</div>
</details>
