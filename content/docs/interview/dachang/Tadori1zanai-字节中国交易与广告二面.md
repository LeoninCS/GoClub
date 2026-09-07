---
title: "Tadori1zanai 字节中国交易与广告二面"
slug: "tadori-bytedance-ecom-ads-2"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-字节中国交易与广告二面/"
  - "/s/08bm/"
shortlink: "08bm"
---

# Tadori1zanai 字节中国交易与广告二面

作者：Tadori1zanai  
时间：2026.4.29

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。

## Kafka 为什么可以处理高吞吐？

- Kafka 把消息当成日志做顺序追加写，顺序写磁盘效率高于随机写。
- Kafka 通过 partition 把一个 topic 拆成多条并行日志，生产和消费都可以并行扩展。
- Kafka 支持批量发送、批量写入、批量拉取，减少网络和系统调用开销。
- Kafka 充分利用操作系统 page cache，很多文件读写先走内存。
- Kafka 使用零拷贝发送消息，减少用户态和内核态之间的数据搬运。
