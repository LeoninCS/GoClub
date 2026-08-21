---
title: "m佬PDD服务端开发实习"
slug: "m-pdd-backend-intern"
aliases:
  - "/docs/interview/dachang/m佬PDD服务端开发实习/"
  - "/s/4e2v/"
shortlink: "4e2v"
---

# m佬 PDD 服务端开发实习

岗位：服务端开发实习

## 面试流程

### 一面

1. 项目细节追问。
2. 手撕 UDP 黏包问题相关题。
3. 简单模拟题。

### 二面

1. 手写 HashMap，实现方式是开放寻址。
2. 围绕 HashMap 底层聊了较多。
3. 项目细节追问较多。

### 三面

1. 面试官对开源经历比较感兴趣，围绕开源项目聊了很多。
2. 手撕经典前缀表达式求值。

### HR 面

1. 聊研究生阶段做项目的一些经历。
2. 结果：HR 面后流程结束。

## 参考答案（AI 生成）

> 以下答案由 AI 生成，仅供面试复盘参考。

### 1. UDP 黏包问题怎么回答？

答：UDP 按报文交付，应用层一次 `recvfrom` 读取的是一个 datagram。面试里如果提到 UDP 黏包，可以先说明 UDP 保留报文边界，重点风险在于报文过大导致 IP 分片、接收缓冲区过小导致截断、网络丢包乱序，以及应用层把多个逻辑消息塞进一个 UDP 包后需要自行拆分。

工程处理思路是设计应用层协议。比如每个逻辑消息使用 `length + payload`，或者使用固定长度头部，头部里放 magic、version、seq、len、checksum。接收后先校验头部和长度，再按协议拆出多个逻辑消息。

```go
func splitFrames(buf []byte) ([][]byte, error) {
    frames := make([][]byte, 0)
    for len(buf) > 0 {
        if len(buf) < 4 {
            return nil, fmt.Errorf("short header")
        }
        n := int(binary.BigEndian.Uint32(buf[:4]))
        if n < 0 || len(buf[4:]) < n {
            return nil, fmt.Errorf("invalid frame length")
        }
        frames = append(frames, buf[4:4+n])
        buf = buf[4+n:]
    }
    return frames, nil
}
```

### 2. 开放寻址 HashMap 怎么实现？

答：开放寻址把所有元素都放在数组里，冲突时按探测序列寻找下一个可用槽位，常见探测方式有线性探测、二次探测和双重哈希。每个槽位通常有三种状态：empty、used、deleted。查找时从 hash 位置开始探测，遇到目标 key 返回，遇到 empty 说明 key 缺席，遇到 deleted 继续探测。

扩容条件通常基于负载因子，比如元素数量超过容量的 0.7 时扩容到两倍，再把旧元素重新插入新数组。删除时使用 deleted 标记，保留探测链路，后续可以在扩容时清理 tombstone。

```go
type entry struct {
    key   string
    val   int
    state uint8 // 0 empty, 1 used, 2 deleted
}

type HashMap struct {
    data []entry
    size int
}

func NewHashMap(capacity int) *HashMap {
    if capacity < 8 {
        capacity = 8
    }
    return &HashMap{data: make([]entry, capacity)}
}

func (m *HashMap) Put(key string, val int) {
    if float64(m.size+1)/float64(len(m.data)) > 0.7 {
        m.resize(len(m.data) * 2)
    }
    m.putNoResize(key, val)
}

func (m *HashMap) Get(key string) (int, bool) {
    idx := int(hashString(key) % uint64(len(m.data)))
    for i := 0; i < len(m.data); i++ {
        p := (idx + i) % len(m.data)
        e := m.data[p]
        if e.state == 0 {
            return 0, false
        }
        if e.state == 1 && e.key == key {
            return e.val, true
        }
    }
    return 0, false
}

func (m *HashMap) Delete(key string) bool {
    idx := int(hashString(key) % uint64(len(m.data)))
    for i := 0; i < len(m.data); i++ {
        p := (idx + i) % len(m.data)
        e := m.data[p]
        if e.state == 0 {
            return false
        }
        if e.state == 1 && e.key == key {
            m.data[p].state = 2
            m.size--
            return true
        }
    }
    return false
}

func (m *HashMap) putNoResize(key string, val int) {
    idx := int(hashString(key) % uint64(len(m.data)))
    firstDeleted := -1

    for i := 0; i < len(m.data); i++ {
        p := (idx + i) % len(m.data)
        e := m.data[p]
        if e.state == 1 && e.key == key {
            m.data[p].val = val
            return
        }
        if e.state == 2 && firstDeleted == -1 {
            firstDeleted = p
            continue
        }
        if e.state == 0 {
            if firstDeleted != -1 {
                p = firstDeleted
            }
            m.data[p] = entry{key: key, val: val, state: 1}
            m.size++
            return
        }
    }
}

func (m *HashMap) resize(capacity int) {
    old := m.data
    m.data = make([]entry, capacity)
    m.size = 0
    for _, e := range old {
        if e.state == 1 {
            m.putNoResize(e.key, e.val)
        }
    }
}

func hashString(s string) uint64 {
    var h uint64 = 1469598103934665603
    for i := 0; i < len(s); i++ {
        h ^= uint64(s[i])
        h *= 1099511628211
    }
    return h
}
```

### 3. HashMap 底层常见追问

答：开放寻址的核心问题是冲突处理、删除标记、负载因子和扩容。负载因子过高会导致探测长度变长，查询和插入退化；删除留下 tombstone 会影响探测效率，需要在扩容或重建时清理。和链地址法相比，开放寻址局部性更好，数组连续存储更利于缓存，但对负载因子更敏感。

### 4. 前缀表达式求值

答：前缀表达式可以从右向左扫描。遇到数字就入栈，遇到运算符就弹出两个操作数计算，再把结果压回栈。扫描结束后栈顶就是结果。

```go
func evalPrefix(tokens []string) (int, error) {
    stack := make([]int, 0)
    for i := len(tokens) - 1; i >= 0; i-- {
        t := tokens[i]
        switch t {
        case "+", "-", "*", "/":
            if len(stack) < 2 {
                return 0, fmt.Errorf("invalid expression")
            }
            a := stack[len(stack)-1]
            b := stack[len(stack)-2]
            stack = stack[:len(stack)-2]

            var v int
            switch t {
            case "+":
                v = a + b
            case "-":
                v = a - b
            case "*":
                v = a * b
            case "/":
                if b == 0 {
                    return 0, fmt.Errorf("division by zero")
                }
                v = a / b
            }
            stack = append(stack, v)
        default:
            v, err := strconv.Atoi(t)
            if err != nil {
                return 0, err
            }
            stack = append(stack, v)
        }
    }
    if len(stack) != 1 {
        return 0, fmt.Errorf("invalid expression")
    }
    return stack[0], nil
}
```

### 5. 开源经历怎么讲？

答：开源经历可以按“项目背景、参与动机、贡献内容、协作方式、工程收获”来讲。重点讲清楚你解决了什么问题、读了哪些模块、怎么和 maintainer 沟通、PR 怎么设计和验证、最终合入后带来什么效果。技术之外，也可以补充 issue 拆解、review 反馈处理、文档补充和社区协作经验。
