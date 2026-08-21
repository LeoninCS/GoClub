---
title: "Tadori1zanai Bilibili增值一面（项目：分布式缓存系统 / IM 聊天系统）"
slug: "tadori-bilibili-vas-1"
aliases:
  - "/docs/interview/dachang/Tadori1zanai-Bilibili增值一面/"
  - "/s/2zht/"
shortlink: "2zht"
---

# Tadori1zanai Bilibili 增值一面（项目：分布式缓存系统 / IM 聊天系统）

作者：Tadori1zanai  
时间：2026.5.7

> 注：
>
> - 回答多数为 AI 生成，仅供参考。
> - 只记录部分面试和部分问题，部分问题暂无回答。
> - 个人项目相关的面试题用 `*` 标识。

## 群聊是怎么实现的*

- Gateway 校验发送者群成员身份后，先把群消息写入 `group_messages`。
- 再查出群成员列表，然后复用单聊下发链路。
- 群聊没有做逐条 ACK，这是一个有意取舍。
- 如果群聊每条消息都等待每个成员回 ACK，状态会膨胀成“消息数 × 群成员数”。
- 所以群聊采用“实时推送 + 落库 + 离线同步补偿”。

当前复用单聊链路：

- Goim 本身有 room broadcast 机制，后续可以作为群聊性能优化方向。
- 当前没有把 room broadcast 作为主实现，是因为面向几百人的规模时，复用单聊链路更直接。
