# Agent MCP (Model Context Protocol) 协议深度调研

> **调研时间**: 2026-04-26 | **项目版本**: latest (AgentScope `mcp`, MCP Python SDK)

## 1. 核心机制：标准化的工具扩展
MCP 旨在解决 Agent 与外部工具/数据源之间的连接标准化问题。AgentScope 通过内置的 MCP 客户端，实现了与外部 MCP Server 的无缝对接。

### 🔌 客户端架构 (Client Architecture)
AgentScope 提供了两种主要类型的 MCP 客户端：
*   **Stateful Client (有状态)**: 适用于需要保持会话连接的场景（如控制浏览器、长期运行的终端）。
    *   实现类: `HttpStatefulClient`, `StdioStatefulClient`.
    *   核心逻辑: 维护一个持久的 `ClientSession`，直到显式关闭。
*   **Stateless Client (无状态)**: 适用于简单的单次请求响应场景。

### 🛠️ 工具封装 (Tool Wrapping)
*   **MCPToolFunction**: 将 MCP Server 暴露的工具转换为 AgentScope 可调用的函数对象。
*   **Schema 提取**: 自动从 MCP Tool 定义中提取 JSON Schema，供 LLM 进行参数生成。
*   **结果包装**: 可选地将 MCP 的原始结果包装为 `ToolResponse` 格式，统一 Agent 的上下文。

---

## 2. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Agent MCP Layer                            │
│                                                                  │
│  [ AgentScope Agent ] ◀── [ MCPToolFunction ]                    │
│         ▲                      │                                 │
│         │                      ▼                                 │
│         │              [ MCP Client Base ]                       │
│         │           (Stateful / Stateless)                       │
│         │                      │                                 │
│         │                      ▼                                 │
│         │           [ Transport Layer (HTTP/SSE/Stdio) ]         │
│         │                      │                                 │
│         └──────────────────────┼─────────────────────────────────┘
│                                ▼                                 │
│                  [ External MCP Server ]                         │
│                  (e.g. GitHub, Browser, DB)                      │
└──────────────────────────────────────────────────────────────────┘
```

## 3. 本地极简 MVP 代码 (`mvp_mcp.py`)

模拟 AgentScope 的 MCP 接入流程：
1. **连接建立**: 模拟 HTTP/SSE 客户端握手。
2. **工具发现**: 获取 Server 提供的工具列表并提取 Schema。
3. **工具调用**: 发送参数并获取结果。

*(注：源码分析基于本地 AgentScope 库 `mcp/_http_stateful_client.py` 等。)*
