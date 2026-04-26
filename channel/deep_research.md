# QwenPaw Channel & Heartbeat 通信机制深度调研

> **调研时间**: 2026-04-26 | **项目版本**: latest (QwenPaw v1.1.4, agentscope-ai/QwenPaw)

## 1. 核心通信协议分析 (Channel Architecture)

QwenPaw 的 Channel 模块是一个高度模块化、支持多平台（飞书、钉钉、Discord、微信等）接入的统一消息网关，并结合了强大的心跳（Heartbeat）机制来实现定时任务。

### 📡 核心架构组件
1. **Unified Queue Manager (统一队列管理)**: 系统的核心心脏。使用三维路由键 `QueueKey = (channel_id, session_id, priority)` 管理消息。
2. **Priority Registry (优先级注册)**: 支持 0 (critical, e.g., `/stop`) 到 20 (normal) 等多级优先级。确保紧急指令不被长对话阻塞。
3. **Debounce & Merge (防抖与合并)**: `BaseChannel` 内置 `_apply_no_text_debounce` 和 `merge_native_items`。对于即时通讯软件传来的碎片消息（如仅包含图片/音频的非文本块），系统会先将其**缓存 (Buffer)**，直到收到包含文本的消息或超时，才合并发送给 Agent。这极大地减少了无效推理。
4. **Dynamic Consumers (动态消费者)**: 消费者按需创建，空闲自动清理。

### 🔗 行为链/思维链/工具链 (Chain of X) 传递机制
QwenPaw 通过 `AgentRunner` 返回的 `AsyncIterator[Event]` 进行流式分发：
*   **行为链 (Action Chain)**: 最终由 `on_event_message_completed` 捕获 `RunStatus.Completed` 事件，并通过 `send_message_content` 将最终结果渲染给用户。
*   **思维链 (Reasoning Chain)**: 在 `on_event_content` 阶段处理。如果 Event 包含 reasoning/thinking 内容，且未配置 `filter_thinking`，则会以流式形式（通常是折叠卡片或进度条）推送给前端。
*   **工具链 (Tool Chain)**: 对应 `MessageType.FUNCTION_CALL` 和 `FUNCTION_CALL_OUTPUT`。`_format_stream_tool_output_body` 会提取工具调用参数和结果，并根据 `show_tool_details` 决定是否静默执行。

### 💓 Heartbeat 通信机制 (Cron & Event Injection)
心跳机制是 QwenPaw 实现“主动式智能”的关键。
1.  **定时触发**: `Heartbeat` 模块基于 Crontab 或时间间隔（如 `30m`）运行。
2.  **上下文注入**: 读取 `HEARTBEAT.md`，构建一个特殊的 `AgentRequest`。
3.  **流式回传**: 
    *   通过 `runner.stream_query(req)` 启动推理。
    *   **关键点**: 推理产生的 `Event` 流，不经过普通的入队逻辑，而是直接通过 **`channel_manager.send_event(user_id, session_id, event)`** 注入到 Channel 的输出流中！
    *   这意味着心跳产生的工具调用、思维过程会像用户刚刚发了一条消息一样，实时展示在聊天窗口中。

### 🛡️ 异常与抗抖动处理
*   **消息堆积 (Backpressure)**: 队列有 `maxsize`。
*   **任务追踪与取消 (TaskTracker)**: 普通消息通过 `TaskTracker` 包装。当用户发送 `/stop` 时，触发 `task.cancel()`，调用 `process_iterator.aclose()` 优雅终止底层 Agent 循环，防止资源浪费。
*   **网络抖动**: 各 Channel 实现层（如 DingTalk/Feishu）通常内置了 SDK 重试；在 `BaseChannel` 层面，通过 `_on_consume_error` 捕获所有未处理异常并发送错误提示。

---

## 2. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                         QwenPaw Ecosystem                        │
│                                                                  │
│   [ Client Apps ] ─────(Messages)────▶ [ Channel Instances ]     │
│         ▲                                   │                    │
│         │                                   ▼                    │
│         │                      ┌──────────────────────┐          │
│         │                      │  UnifiedQueueManager │          │
│         │                      │ (Priority + Debounce)│          │
│         │                      └──────────┬───────────┘          │
│         │                                 │                      │
│         │               (AgentRequest via Consumer)              │
│         │                                 ▼                      │
│         │                      ┌──────────────────────┐          │
│         │                      │    AgentRunner (LLM) │          │
│         │                      │  (Reasoning/Tools)   │          │
│         │                      └──────────┬───────────┘          │
│         │                                 │                      │
│         │                        (Stream of Events)              │
│         │                                 │                      │
│   [ Heartbeat/Cron ] ──(Inject Events)───┘                      │
│         │                                                        │
│         └──(Heartbeat Query & send_event)────────────────────────┘
│                                                                  │
│             [ BaseChannel Renderer ] ──▶ [ Client Apps ]         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. 本地极简 MVP 代码 (`mvp_qwenpaw_channel.py`)

本次 MVP 重点验证三个核心机制：
1. **Debounce (防抖)**: 模拟非文本消息的缓存与合并。
2. **Heartbeat Injection**: 模拟心跳事件绕过普通队列，直接推送到 Channel。
3. **Priority Interruption**: 模拟 `/stop` 中断正在进行的长任务。

*(注：源码分析基于 GitHub 仓库 `agentscope-ai/QwenPaw` 最新版 `base.py` 与 `heartbeat.py`。)*
