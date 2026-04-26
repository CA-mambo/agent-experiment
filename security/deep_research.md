# Agent 安全与工具审批机制深度调研 (Approval & Guardrails)

> **调研时间**: 2026-04-26 | **项目版本**: latest (QwenPaw `ApprovalService`, OpenAI Guardrails)

## 1. 核心机制：从 静态过滤 到 动态审批
Agent 在执行敏感操作（如删除文件、发送消息）时，必须有安全保障机制。

| 机制类型 | 典型代表 | 核心逻辑 | 优缺点 |
| :--- | :--- | :--- | :--- |
| **静态过滤 (Static Filtering)** | OpenAI SDK | **基于规则/LLM 预判**。在调用工具前，先让 LLM 或正则检查请求是否合规。 | ✅ 速度快；❌ 容易误杀或漏杀。 |
| **动态审批 (Human-in-the-loop)** | QwenPaw, Claude | **异步阻塞**。遇到敏感工具调用时，Agent 暂停执行，等待人类确认（批准/拒绝）。 | ✅ 安全性极高；❌ 需要人类实时在线。 |
| **沙箱执行 (Sandbox)** | E2B, CodeInterpreter | **隔离环境**。即使恶意代码执行了，也只影响虚拟机，不影响宿主机。 | ✅ 防御力强；❌ 资源消耗大。 |

## 2. QwenPaw (`ApprovalService`) 源码深度解析
通过分析 `agentscope-ai/QwenPaw` 源码 (`approvals/service.py`)，其审批机制设计得非常优雅：

### ⏸️ 异步阻塞与异步恢复 (Async Blocking & Resume)
- **Future 机制**: 当需要审批时，系统创建一个 `asyncio.Future` 对象并挂在 `ApprovalService` 上。
- **工具循环暂停**: 底层的 Tool Loop 会 `await future`。此时协程挂起，不消耗 CPU，直到用户输入 `/approve`。
- **恢复执行**: 用户批准后，系统调用 `future.set_result(ApprovalDecision.APPROVED)`，Tool Loop 瞬间恢复并执行工具。

### 🗑️ 垃圾回收与防堆积 (GC & Anti-Accumulation)
- **超时机制**: 如果用户长时间不响应，审批请求会自动超时（默认 300 秒），防止 Agent 永久卡死。
- **队列清理**: `ApprovalService` 会定期清理过期的或数量过多的 Pending 请求，防止内存泄漏。

---

## 3. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Tool Execution Loop                        │
│                                                                  │
│  [ Agent ] ──(Call Tool: "delete_file")──▶ [ Tool Guard ]        │
│                                              │                   │
│                                              ▼                   │
│                                   [ ApprovalService ]            │
│                                   (Create async Future)          │
│                                              │                   │
│                                              ▼                   │
│                                   [ Pause Execution ]            │
│                                   (Waiting for User...)          │
│                                              │                   │
│                                      (User types /approve)       │
│                                              │                   │
│                                              ▼                   │
│                                   [ Resume Execution ]           │
│                                   (Future.set_result)            │
│                                              │                   │
│                                              ▼                   │
│                                    [ Execute Tool ]              │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 本地极简 MVP 代码 (`mvp_approval_system.py`)

模拟 QwenPaw 的审批流程：
1. **动态拦截**: 识别敏感工具（如 `delete`），暂停执行。
2. **异步等待**: 使用 `asyncio.Future` 模拟挂起，直到“用户”批准。
3. **超时熔断**: 模拟用户长时间不响应，自动拒绝并恢复 Agent 循环。

*(注：源码分析基于 GitHub 仓库 `agentscope-ai/QwenPaw` 的 `approvals/service.py`。)*
