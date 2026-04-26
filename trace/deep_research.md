# Agent 链路追踪与可观测性深度调研 (Tracing & Observability)

> **调研时间**: 2026-04-26 | **项目版本**: latest (AgentScope Tracing, OpenTelemetry)

## 1. 核心机制：黑盒变白盒
在生产环境中，Agent 的行为必须是**可观测**的。主流框架（如 AgentScope）深度集成了 **OpenTelemetry** 标准，实现了全链路的透明化。

### 🔗 核心追踪对象 (Trace Targets)
AgentScope 提供了专门的装饰器来追踪以下核心组件：
*   **Agent**: `@trace_agent` - 追踪整个 Agent 的执行生命周期。
*   **LLM**: `@trace_llm` - 记录模型输入输出、Token 消耗、延迟。
*   **Tool**: `@trace_tool` - 记录工具调用的参数、执行结果、异常信息。
*   **Formatter**: `@trace_formatter` - 记录 Prompt 组装前后的格式变化。
*   **Embedding**: `@trace_embedding` - 记录向量检索的细节。

### 📊 关键指标采集 (Span Attributes)
每个 Span 会携带丰富的 Attributes：
*   **Input/Output**: 具体的 Prompt 和 Response（可配置脱敏）。
*   **Token Usage**: `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`。
*   **Status**: 成功 (`OK`) 或失败 (`ERROR`)，失败时会记录异常堆栈。
*   **Operation Name**: 明确当前是 `agent.run`, `llm.chat`, `tool.execute`。

### 🌳 嵌套追踪 (Nested Spans)
*   Agent 的执行通常包含多个 LLM 调用和 Tool 调用。
*   Tracing 系统会自动维护 `Context`，形成父子层级关系：
    `Agent Span` -> `LLM Span 1` -> `Tool Span` -> `LLM Span 2`.

---

## 2. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                   OpenTelemetry Tracing System                   │
│                                                                  │
│  [ User Input ] ─▶ [ @trace_agent ]                              │
│                         │                                        │
│                         ▼                                        │
│                    [ Agent Span ]                                │
│                    (status: in_progress)                         │
│                         │                                        │
│          ┌──────────────┴──────────────┐                         │
│          ▼                             ▼                         │
│   [ @trace_llm ]                [ @trace_tool ]                  │
│   (LLM Span)                    (Tool Span)                      │
│   [input_tokens: 120]           [tool: search]                   │
│   [output_tokens: 50]           [latency: 200ms]                 │
│          │                             │                         │
│          └──────────────┬──────────────┘                         │
│                         ▼                                        │
│                    [ @trace_llm ]                                │
│                    (Final Response)                              │
│                         │                                        │
│                         ▼                                        │
│                 [ SpanExporter ]                                 │
│                 (Send to Jaeger/Zipkin)                          │
└──────────────────────────────────────────────────────────────────┘
```

## 3. 本地极简 MVP 代码 (`mvp_tracing.py`)

模拟 AgentScope 的 Tracing 机制：
1. **装饰器注入**: 使用 `@trace_llm` 和 `@trace_tool` 包装函数。
2. **上下文管理**: 维护 Span 的层级关系（父子）。
3. **指标上报**: 收集 Token 消耗和执行耗时。

*(注：源码分析基于本地 AgentScope 库 `tracing/_trace.py` 及 `opentelemetry` 标准。)*
