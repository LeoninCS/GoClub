---
title: "Agent 相关网站推荐"
weight: 2
type: docs
slug: "agent-websites"
aliases:
  - "/docs/resources/Agent相关网站推荐/"
  - "/s/yrxb/"
shortlink: "yrxb"
---

# Agent 相关网站推荐

如果你最近在找 Agent、Claude Code、AI Native Agent 相关学习资料，可以先从下面这几个站点开始。

这页内容根据站点首页与公开说明整理，重点不是简单贴链接，而是帮你快速判断每个网站更适合解决什么问题。

## 入门概念

### AI Agent 教程 | 菜鸟教程

这是一个偏入门的 Agent 教程，先从什么是 Agent 讲起，再把 Agent 拆成 `LLM + Planning + Tool use + Memory` 四个核心部分。页面里还放了一个“天气穿衣助手”的简单伪代码示例，适合先建立直觉，再继续往下看它后续的工具与框架内容。

- 适合人群：刚接触 Agent，想先把基本概念讲明白的人
- 你能学到：Agent 的基本定义、组成方式、工作流程、简单示例
- 访问地址：https://www.runoob.com/ai-agent/ai-agent-tutorial.html

## Claude Code 与 Coding Agent

### 解码 Agent Harness

这个站点更偏“架构拆解”，不是普通的上手教程。它围绕 Claude Code 展开，重点解释对话循环、工具系统、权限管线、上下文压缩、MCP、子智能体调度，以及怎样自己构建一个可落地的 Agent Harness。更适合把 Claude Code 当成工程系统来理解，而不是只学几个命令。

- 适合人群：想深入理解 Coding Agent 底层设计的开发者
- 你能学到：Agent Harness 设计思路、权限与上下文管理、子智能体与扩展机制
- 访问地址：https://lintsinghua.github.io/

### Claude Code 教程 | 菜鸟教程

如果你的目标是尽快上手 Claude Code，这个教程会更直接。它把 Claude Code 定位成一个可以在本地代码仓库中执行任务的 Agent 工具，内容覆盖安装、API 配置、项目初始化、交互模式、MCP、子代理、插件、记忆系统和 Skills，比较适合作为实用入口。

- 适合人群：已经有编程基础，想快速开始使用 Claude Code 的同学
- 你能学到：Claude Code 的定位、基础操作、常见能力模块和工程化使用方式
- 访问地址：https://www.runoob.com/claude-code/claude-code-tutorial.html

### Learn Claude Code

这个站点的风格很适合“边学边造”。它把一个 Claude Code 风格的 Coding Agent 拆成多个渐进式学习单元，从最小化的 agent loop 开始，逐步加入 tools、TodoWrite、subagents、skills、compact、tasks、background tasks、agent teams、worktree isolation 等机制。优点是结构清晰，能帮助你通过“自己实现一遍”来吃透原理。

- 适合人群：喜欢通过动手实现来理解 Agent 机制的人
- 你能学到：agent loop、规划与协作、上下文压缩、任务隔离、多 agent 组织方式
- 访问地址：https://learn.shareai.run/

## 系统化学习

### Hello-Agents | Datawhale

这是 Datawhale 的系统性智能体教程，覆盖面很广，既讲原理，也讲实践。内容从智能体定义、发展史、大语言模型基础讲起，进一步延伸到经典范式、低代码平台、主流框架、自研框架、记忆与检索、上下文工程、通信协议、Agentic-RL、性能评估，以及多智能体综合案例，适合按章节完整学习。

- 适合人群：想系统补齐 Agent 知识体系，并且愿意跟着章节深入的人
- 你能学到：从单智能体到多智能体的完整学习路径，以及较完整的实战主题覆盖
- 访问地址：https://hello-agents.datawhale.cc/

## 阅读建议

- 如果你是第一次接触 Agent，先看“AI Agent 教程”建立整体概念。
- 如果你已经会写代码，想尽快把 Claude Code 用起来，先看“Claude Code 教程”。
- 如果你更关心 Claude Code 背后的设计逻辑，再去看“解码 Agent Harness”。
- 如果你想通过自己实现来理解 Coding Agent，优先看“Learn Claude Code”。
- 如果你想系统学一轮，从基础一路走到多智能体实践，可以把“Hello-Agents”当主线。
