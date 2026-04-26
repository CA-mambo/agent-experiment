# 🤖 头部 Agent 项目多智能体协作机制分析

本文档整理了当前头部 AI Agent 项目（Claude Code, Codex, OpenCode, OpenClaw, Hermes）在多智能体协作和通信机制方面的架构与协议。

---

## 1. OpenClaw (Moltbook 生态)

OpenClaw 是 Moltbook 平台背后的核心 Agent 运行时环境，其多智能体协作机制建立在**去中心化协议**之上，强调 Agent 间的直接交互与价值交换。

### 📡 核心通信协议
- **ACP (Agent Communication Protocol)**:
  - 一种通用的 Agent 间通信标准，定义了 Agent 如何发现彼此、建立连接以及交换消息。
  - 支持**结构化消息**（不仅仅是纯文本，还包括任务指令、状态报告等）。
- **x402 (Payment Protocol)**:
  - 专为 Agent 设计的微支付协议。允许 Agent 在请求其他 Agent 服务时自动进行加密货币结算（如 USDC）。
  - 确保了协作的**经济可持续性**（Agent 需要支付计算资源费用）。

### 🏗️ 架构特点
- **去中心化 (Decentralized)**: 没有中心服务器调度，Agent 通过广播或目录服务发现彼此。
- **能力发布 (Capability Advertisement)**: Agent 通过特定端点（如 `/.well-known/agent.json`）公开其技能和价格。
- **应用场景**: 跨 Agent 的任务外包（如一个 Agent 雇佣另一个 Agent 进行特定计算或数据检索）。

---

## 2. Claude Code (Anthropic)

Claude Code 是 Anthropic 推出的命令行 Agent，其多智能体协作主要体现在**主从架构**和**上下文隔离**上。

### 📡 协作机制
- **Sub-agents (子代理)**:
  - Claude Code 允许主 Agent 在遇到复杂任务时生成**子代理**（Sub-agents）。
  - 这些子代理通常运行在独立的上下文中，拥有受限的工具权限。
- **Context Handoff (上下文传递)**:
  - 主 Agent 将部分任务和必要的文件上下文“剥离”给子代理。
  - 子代理执行完毕后，将结果（代码变更、分析报告）返回给主 Agent，主 Agent 再整合到全局上下文中。

### 🛠️ 通信方式
- **MCP (Model Context Protocol)**:
  - 虽然主要用于工具集成，但 MCP 的标准化接口使得不同 Agent 可以通过共享的 MCP 服务器交换数据。
  - **内部通信**: 子代理与主代理之间通过进程间通信（IPC）或内部消息队列进行交互。

---

## 3. OpenAI Codex (Agent SDK / CLI)

OpenAI 的 Codex（及其相关的 Agent SDK）代表了 OpenAI 在多智能体编排上的思路，侧重于**确定性**和**工具链集成**。

### 📡 协作机制
- **Handoffs (交接机制)**:
  - 在 OpenAI 的 Agent 架构中，多智能体协作通常通过**显式的手动交接**（Handoffs）实现。
  - Agent A 判断任务超出能力范围或权限，主动将控制权移交给 Agent B（例如：从“通用助手”移交给“代码专家”或“数据库管理员”）。
- **Guardrails (护栏)**:
  - 在交接过程中，严格的 Guardrails 确保只有必要的信息被传递，防止上下文污染。

### 🏗️ 通信协议
- **JSON-RPC / Function Calling**:
  - 底层依赖强大的 Function Calling 能力。Agent 之间的交互本质上是对特定工具（或另一个 Agent 的入口函数）的调用。
  - **结构化输出**: 强制要求 Agent 返回符合特定 JSON Schema 的结果，确保下游 Agent 能准确解析。

---

## 4. OpenCode (`opencode-ai`)

OpenCode 是一个开源的终端 AI 编辑器/Agent，其多智能体功能主要体现在**模块化扩展**和**并行处理**上。

### 📡 协作机制
- **Tool-based Multi-Agent**:
  - 通过定义不同的“工具”或“插件”，每个插件可以视为一个专门的微型 Agent。
  - 主循环负责调度这些工具，形成事实上的多智能体协作。
- **Parallel Execution**:
  - 支持同时运行多个 Agent 实例处理不同的代码块或文件，最后由主 Agent 合并结果。

### 🛠️ 通信方式
- **Standard Input/Output (Stdio)**:
  - 许多子任务通过子进程（Subprocess）执行，通过 Stdio 进行简单的文本或 JSON 数据交换。
  - **文件系统共享**: Agent 之间经常通过读写临时文件或共享工作区目录来传递复杂状态。

---

## 5. Hermes

*注：此处指多智能体框架/协议中的 Hermes，而非单纯的 LLM 模型。*

Hermes 通常在多智能体研究中指的是用于**高效消息传递**或**异构 Agent 协调**的中间件/协议。

### 📡 核心机制
- **Message Bus (消息总线)**:
  - 采用发布/订阅（Pub/Sub）模式。Agent 订阅感兴趣的主题（Topics），当其他 Agent 发布相关消息时，自动触发响应。
- **Semantic Routing (语义路由)**:
  - 消息不仅仅是广播，而是根据内容的语义（意图）自动路由到最匹配的 Agent。

### 🏗️ 架构特点
- **异构支持**: 能够连接不同类型的 Agent（如基于 LLM 的 Agent、基于规则的 Agent、传统的微服务）。
- **状态同步**: 提供共享黑板（Shared Blackboard）机制，让多个 Agent 可以读写全局状态。

---

## 📊 总结对比

| 项目 | 协作模式 | 核心协议/机制 | 典型应用场景 |
| :--- | :--- | :--- | :--- |
| **OpenClaw** | 去中心化 P2P | **x402**, **ACP** | Agent 经济、跨平台任务外包 |
| **Claude Code** | 主从 (树状) | **MCP**, Sub-agents | 复杂代码库重构、并行测试 |
| **OpenAI Codex** | 显式交接 (流水线) | **Handoffs**, Function Calling | 专家分工、权限隔离 |
| **OpenCode** | 插件/并行 | **Stdio**, 文件共享 | 本地编辑器增强、多文件处理 |
| **Hermes** | 消息总线 | **Pub/Sub**, 语义路由 | 大规模 Agent 集群协调 |
