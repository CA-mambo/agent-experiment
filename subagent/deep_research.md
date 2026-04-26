# 主流 Agent Sub-Agent 机制深度调研

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心维度对比分析
主流 Agent 框架在子代理（Sub-Agent）的管理上呈现出明显的差异化设计，主要围绕**生成机制、生命周期、记忆上下文、权限隔离**四个核心维度展开。

| Agent 项目 | 生成机制 | 生命周期模型 | 记忆管理 (Memory) | 权限控制 (Permission) |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | **动态按需生成** (Dynamic Spawning) | **任务级短生命周期** (Ephemeral)。任务完成即销毁。 | **最小化切片** (Context Slicing)。仅传递相关文件与任务约束。 | **严格沙箱** (Sandbox)。限制文件目录与读写权限。 |
| **OpenAI Codex** | **显式声明/交接** (Explicit Handoff) | **流水线式** (Pipeline)。控制权单向或双向流转。 | **上下文守卫** (Guardrails)。交接前剥离敏感/无关历史。 | **角色绑定** (Role-based)。预定义工具集与指令。 |
| **OpenClaw** | **P2P 网络发现** (Discovery) | **请求-响应** (RPC)。验证通过即服务，服务完断开。 | **无状态** (Stateless)。每次调用视为独立交易。 | **支付验证** (Payment Gate)。x402 协议拦截。 |
| **OpenCode** | **并发子进程** (Subprocess Spawn) | **进程级短生命周期**。执行完特定工具后退出。 | **文件系统共享**。通过临时文件或 Stdio 交换数据。 | **受限环境**。子进程通常锁定在工作目录。 |
| **Hermes** | **订阅路由** (Pub/Sub Routing) | **持续监听/按需实例**。依赖消息总线驱动。 | **共享黑板** (Shared Blackboard)。全局状态同步。 | **Topic 级隔离**。基于主题的发布/订阅权限。 |

---

## 2. 详细机制还原

### 🧬 生成机制 (Generation)
- **Claude Code (Tree-based Spawning)**: 主代理在遇到超出上下文窗口（Context Window）或安全边界的任务时，**自主决定**生成子代理。这是一种“树状分裂”模型。
- **OpenAI (Delegation)**: 主代理通过识别用户意图，调用预定义的 `Handoff Tool`，将控制权**移交**给另一个专家 Agent。
- **OpenClaw (Marketplace)**: 通过广播或注册中心（`/.well-known/`）发现外部 Agent，发起协作请求。

### ⏳ 生命周期管理 (Lifecycle)
- **Ephemeral (瞬态)**: 如 Claude Code 和 OpenCode 的子代理。它们的寿命仅限于完成单个任务或处理一次文件块。一旦返回结果（Diff/Report），立即被**回收（Reap）**，不留痕迹。
- **Stateful (有状态)**: Hermes 中的 Agent 实例通常保持活跃，持续监听事件总线。

### 🧠 记忆传递 (Memory Context)
- **隔离原则**: 几乎所有现代框架都不允许子代理直接访问主代理的完整内存（Full Memory）。
- **Context Filtering**: OpenAI SDK 实现了 `handoff_filters`，在交接前自动过滤掉工具调用历史（Tool Call History）和敏感变量。
- **Context Compression**: Claude Code 会将庞大的代码库压缩为“任务相关片段（Relevant Files）”，减少 Token 消耗。

### 🛡️ 权限控制 (Permission & Sandbox)
- **沙箱隔离**: 子代理运行在受限环境中。例如，Claude Code 的子代理通常只有**只读权限**或特定目录的**写入权限**。
- **能力降级**: 防止子代理调用主代理拥有的高危工具（如执行系统级命令）。

---

## 3. 源码级架构示意图 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                         Main Agent Context                       │
│                                                                  │
│  [ Global Memory: Full Repo / History / Secrets ]                │
│           │                                                      │
│           │ (1. Decision to Delegate)                            │
│           ▼                                                      │
│  ┌───────────────────────────────────────────────────────┐       │
│  │            Sub-Agent Manager / Runtime                │       │
│  │                                                       │       │
│  │   [ Context Filter/Slicer ] -> [ Sandbox/Permissions ]│       │
│  │         │                                    │        │       │
│  │         ▼                                    ▼        │       │
│  │   [ Spawn Agent A ]                 [ Spawn Agent B ] │       │
│  │   (Task: Frontend)                  (Task: Database)  │       │
│  │         │                                    │        │       │
│  │         └────────────(2. Result)─────────────┘        │       │
│  └────────────────────────┬──────────────────────────────┘       │
│                           │                                      │
│                           ▼                                      │
│                  [ Merge Results / Reap ]                        │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 本地极简 MVP 代码 (`mvp_subagent_lifecycle.py`)
模拟了一个通用的子代理生命周期管理器，实现了以下功能：
1.  **动态生成 (Spawn)**: 模拟 Claude Code 的任务分解。
2.  **上下文切片 (Context Slicing)**: 过滤全局记忆，只传递必要信息。
3.  **权限沙箱 (Sandbox)**: 拦截越权操作。
4.  **回收机制 (Reap)**: 任务完成后销毁实例。

*(注：基于 Claude Code, OpenAI Agent SDK, OpenClaw 源码逻辑综合提炼。)*
