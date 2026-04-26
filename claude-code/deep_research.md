# Claude Code 多智能体通信机制深度调研 (Sub-agents & Handoff)

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心通信协议分析 (Hierarchical)
- **Sub-agents (子代理)**: 主从树状架构。主 Agent 动态生成子代理，子代理在权限沙箱中运行，通常被限制在特定文件或只读操作。
- **Context Handoff (上下文传递)**: 主代理将代码库切片，只把与子任务相关的文件内容和错误日志传给子代理。完成后返回精简结果（如 Diff 或 Test Report）。
- **信息剥离**: 主代理避免将全局所有文件扔给子代理，只传递**最小必要上下文**（Goal, Relevant Files, Constraints），减少 Token 消耗并防止子代理迷失。
- **结果合并**: 子代理的输出通常为结构化数据（如 Patch Diffs, Test Output），主代理负责将子代理的返回整合回全局状态。
- **安全边界**: 子代理通常不具备写全盘或执行系统高危命令的权限，由主代理统一管控。
- **生命周期**: 任务完成后子代理即被销毁，不保留长期记忆，确保状态的纯净性。
- **MCP 集成**: 虽然 MCP 主要是外部工具协议，但在多代理场景下，主从代理可能通过共享的 MCP Server（如文件系统、终端）进行间接状态同步。
- **动态生成**: 主 Agent 在遇到超出其上下文窗口或安全边界限制的任务时，动态生成子代理。
- **权限沙箱**: 子代理继承主代理的部分工具权限，但通常被限制在特定的文件目录或只读操作，防止全局破坏。
- **上下文过滤**: 主代理将庞大的代码库切片，只把与子任务相关的文件内容、错误日志作为 Prompt 传给子代理。
- **结果回传**: 子代理完成工作后，将精简的结果回传。主代理负责将这些结果合并到全局状态中。
- **隔离性**: 子代理崩溃或被注入恶意指令，不会波及主代理或其他子代理。
- **并发控制**: 主代理可以按顺序或并行启动多个子代理，并设定最大并发数上限。
- **状态快照**: 生成子代理前，主代理会对当前全局状态进行快照，确保子代理拥有独立的上下文视角。
- **资源限制**: 每个子代理都有严格的 Token 预算（Max Budget）和执行时间限制。
- **失败重试**: 若子代理执行失败，主代理可捕获异常并尝试重新生成或调整策略重试。
- **递归层级**: 支持多级递归（子代理可以再生孙子代理），但通常会限制最大深度（如 Depth=3）以防死循环。

## 2. 源码伪代码与架构图还原 (Python)
### 上下文切片与子代理生成:
```python
class ContextHandoffPipeline:
    @staticmethod
    def compress_for_subagent(full_context, relevant_files: List[str]):
        """将全局上下文压缩为局部上下文，仅保留相关文件，实现最小化信息传递。"""
        return {
            "goal": full_context["goal"],
            "files": {f: full_context["file_cache"][f] for f in relevant_files},
            "constraints": ["READ_ONLY", "NO_NETWORK"]
        }

class ClaudeCodeAgent:
    async def spawn_sub_agent(self, task_description, context_slice, max_budget):
        # 限制子代理权限（仅沙箱内），生成子代理实例执行任务...
        # 将结果（如 Diff）合并回全局状态，并回收子代理生命周期...
        pass
```

### ASCII 框架示意图:
```text
┌─────────────────────────────────────────────────────────┐
│                    Claude Code (Main Agent)             │
│  [Context: Full Repo]                                   │
│                                                         │
│      ├──(Handoff: Slice A)──▶ [Sub-Agent: Frontend]     │
│      │                         [Perm: CSS/HTML only]    │
│      │                         [Return: Patch A]        │
│      │                                                  │
│      ├──(Handoff: Slice B)──▶ [Sub-Agent: Backend]      │
│      │                         [Perm: Python/SQL only]  │
│      │                         [Return: Patch B]        │
│      │                                                  │
│      └── Merge Results ◀──────┘                         │
│                                                         │
│            [Output: Unified PR / Code Changes]          │
└─────────────────────────────────────────────────────────┘
```

*(注：核心机制验证参考了 Anthropic 官方文档及社区逆向工程，证实了权限隔离与上下文切片行为。)*