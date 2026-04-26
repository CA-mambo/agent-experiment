# Agent 规划与记忆压缩机制深度调研 (Planning & Compression)

> **调研时间**: 2026-04-26 | **项目版本**: latest (AgentScope `ReActAgent`, LangGraph)

## 1. 核心机制：从 线性执行 到 结构化规划
面对复杂任务，Agent 不再仅仅是“想一步做一步”，而是引入了**显式规划**和**记忆压缩**。

| 机制类型 | 典型代表 | 核心逻辑 | 优缺点 |
| :--- | :--- | :--- | :--- |
| **ReAct (Reasoning + Acting)** | AgentScope, LangChain | **思考-行动循环**。通过“观察-思考-行动”逐步推进。 | ✅ 灵活性高；❌ 容易陷入死循环。 |
| **显式规划 (Explicit Planning)** | AgentScope `PlanNotebook` | **任务拆解**。Agent 先制定计划表，然后逐项执行并打钩。 | ✅ 适合长链路任务；❌ 规划可能不准确。 |
| **记忆压缩 (Memory Compression)** | AgentScope `CompressionConfig` | **结构化摘要**。当上下文过长时，将旧对话压缩为结构化摘要（任务、状态、发现）。 | ✅ 节省 Token 且保留关键信息；❌ 压缩过程可能丢失细节。 |

## 2. AgentScope (`ReActAgent`) 源码深度解析
通过分析本地 `agentscope` 源码 (`agent/_react_agent.py`)，其实现非常精细：

### 📝 结构化记忆压缩 (Structured Memory Compression)
AgentScope 引入了 `SummarySchema` 模型来指导记忆压缩，确保压缩后的记忆依然是结构化的、有用的：
*   **task_overview**: 用户的核心请求和成功标准。
*   **current_state**: 目前完成了什么（创建/修改了哪些文件）。
*   **important_discoveries**: 发现的技术约束、遇到的错误及解决方案。
*   **next_steps**: 接下来需要执行的具体步骤和阻碍。
*   **context_to_preserve**: 用户的偏好或领域特定的细节。

### 🗓️ 计划本 (PlanNotebook)
*   Agent 可以将复杂任务拆解为多个子任务（Plan）。
*   在执行过程中，Agent 会更新计划的状态（Done/In Progress）。
*   这使得 Agent 在执行长任务（如“写一个完整的 Web 应用”）时不会迷失方向。

---

## 3. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                        ReAct Agent Loop                          │
│                                                                  │
│  [ User Input ] ─▶ [ Context Manager ] ─▶ [ Memory Compression?] │
│                         │                       │                │
│                         │ (If Context > Limit)  ▼                │
│                         │              [ Summarize Old Context ] │
│                         │              (SummarySchema)           │
│                         │                       │                │
│                         ▼                       ▼                │
│                    [ LLM Reasoning ] ◀── [ Compressed Summary ]  │
│                         │                                        │
│                         ▼                                        │
│              [ Plan Update (Optional) ]                          │
│              (Check PlanNotebook Status)                         │
│                         │                                        │
│                         ▼                                        │
│                   [ Tool Execution ]                             │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 本地极简 MVP 代码 (`mvp_planning.py`)

模拟 AgentScope 的规划与压缩机制：
1. **任务拆解 (Plan Decomposition)**: 将长任务拆解为子步骤。
2. **执行与状态更新**: 逐步执行并更新计划状态。
3. **记忆压缩**: 当对话历史过长时，利用 `SummarySchema` 生成结构化摘要。

*(注：源码分析基于本地 AgentScope 库 `ReActAgent` 实现。)*
