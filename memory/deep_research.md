# 主流 Agent 记忆管理机制深度调研 (Memory & Dream Optimization)

> **调研时间**: 2026-04-26 | **项目版本**: latest (QwenPaw ReMeLight, LangChain, AutoGen)

## 1. 记忆分层架构 (Memory Hierarchy)
主流 Agent 框架的记忆系统通常被划分为三个层级，模拟人类认知：

| 层级 | 对应技术 | 作用与特点 | 典型实现 |
| :--- | :--- | :--- | :--- |
| **短期记忆** (Short-term) | Context Window (Sliding Window) | **工作记忆**。当前对话的上下文，响应最快但容量有限。 | LangChain `BufferMemory` |
| **中期记忆** (Mid-term) | Summarization (摘要) | **会话总结**。将冗长的历史对话压缩为精炼摘要，节省 Token。 | QwenPaw `summarize` |
| **长期记忆** (Long-term) | VectorDB + FTS (向量/全文检索) | **知识库**。跨会话持久化存储，按需检索 (RAG)。 | QwenPaw `ReMeLight` |

## 2. QwenPaw (ReMeLight) 核心机制解析
基于 GitHub `agentscope-ai/QwenPaw` 源码 (`reme_light_memory_manager.py`) 的深度拆解：

### 🧠 Dream Optimization (做梦优化)
这是 QwenPaw 最独特的记忆管理机制。
- **独立智能体**: 系统会启动一个专用的 `ReActAgent` (DreamOptimizer)。
- **触发时机**: 在空闲时段或特定配置下触发（类似 Cron 任务）。
- **优化动作**:
  1.  **压缩**: 读取 `MEMORY.md`，合并琐碎的日志，提取关键决策。
  2.  **清理**: 移除过期的、已废弃的方案或无效信息。
  3.  **备份**: 优化前自动创建 `memory_backup_TIMESTAMP.md`。
- **意义**: 让 Agent 拥有了类似人类的“睡眠整理记忆”能力，防止记忆无限膨胀导致检索噪音增加。

### 🔎 Auto-Retrieval (自动检索)
- **混合检索**: 结合了 **Vector (语义)** 和 **FTS (关键词)**。
- **透明注入**: 在 Agent 生成回复前，`retrieve` 方法会自动根据最新对话内容去记忆库搜索，并将结果作为 `ToolResult` 隐式注入到上下文中，无需用户显式调用。

---

## 3. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                        Agent Memory System                       │
│                                                                  │
│  [ Agent Runtime ] ───(Context Full?)──▶ [ Summarization Layer ] │
│        │                                       │                 │
│        │ (1. Summarize old chat)               ▼                 │
│        │                            [ Persistent Storage ]       │
│        │                            (MEMORY.md / VectorDB)       │
│        │                                       │                 │
│        │ (2. Background Task)                  │                 │
│        ▼                                       │                 │
│  [ Dream Optimizer Agent ] ◀───────────────────┘                 │
│                                                                  │
│   [Actions]:                                                     │
│   - Merge redundant entries (Consolidation)                      │
│   - Remove obsolete plans (Pruning)                              │
│   - Update project status (Refining)                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. 本地极简 MVP 代码 (`mvp_memory_dream.py`)

本次 MVP 重点验证三个机制：
1.  **Short-to-Long Term Transfer**: 短期记忆溢出时，压缩为摘要存入长期记忆。
2.  **Retrieval (RAG)**: 根据用户输入，从长期记忆中检索相关摘要。
3.  **Dream Optimization**: 模拟后台任务，对长期记忆进行“去重”和“精炼”。

*(注：核心灵感来源于 QwenPaw `ReMeLight` 的 `summarize` 和 `dream` 方法。)*
