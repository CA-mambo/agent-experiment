# OpenCode 多智能体通信机制深度调研 (Parallel Tools)

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心通信协议分析 (Tool-based)
- **Plugin-based Multi-Agent**: 编辑器维护主循环，每个插件（Linter, Formatter 等）作为微型 Agent。
- **Parallel Execution**: 允许并发启动多个子进程执行不同任务。对大文件或多目录操作，并发启动多个子进程（每个子进程是一个 Agent 实例）。
- **通信管道**:
  - **Stdio**: 快速传递任务指令和结果（JSON Lines）。
  - **File Share**: 对大文件通过读写临时目录共享数据，避免 Stdio 瓶颈。
- **并发调度**: 对于大文件或多目录操作，允许同时启动多个子进程（每个子进程是一个 Agent 实例）。
- **能力解耦**: Agent 之间不直接通信，而是通过主调度器按顺序或并行触发。
- **Stdio 瓶颈优化**: 大量数据通过读写共享工作区目录/临时文件交换，避免 Stdio 缓冲区溢出。
- **跨平台兼容**: 基于标准输入输出 (Stdio) 实现，天然兼容任何支持 CLI 的语言和环境。
- **状态保持**: 插件间无直接状态共享，完全依赖调度器分发的上下文（如文件路径、代码片段）。
- **快速失败**: 某个插件/Agent 执行失败不会阻塞其他并发任务的执行，调度器统一收集结果。
- **异步通信**: 调度器向 Stdout 写入指令后，不需要阻塞等待，可继续分发下一个任务，收到响应后异步回调处理。
- **资源隔离**: 每个子进程拥有独立的内存空间和运行环境，即使崩溃也不会影响编辑器主进程。
- **动态加载**: 可以在运行时动态注册或卸载新的工具插件，无需重启编辑器。
- **超时控制**: 调度器对每个子进程任务设置了严格的超时时间，防止恶意或卡死的插件挂起整个系统。
- **增量更新**: 对于长耗时任务（如全量编译），插件支持流式输出（Streaming），调度器可实时展示进度。

## 2. 源码伪代码与架构图还原 (Python/Go)
### OpenCode 并发调度器:
```python
class OpenCodeScheduler:
    async def execute_parallel(self, tasks):
        # 并发执行所有任务 (如 Go 中的 goroutine, Python 中的 asyncio.gather)
        # 根据任务类型分配通信通道：小数据走 Stdio，大数据走文件系统...
        coroutines = [agent.run_async(task) for task in tasks]
        return await asyncio.gather(*coroutines)
```

### ASCII 框架示意图:
```text
┌──────────────────────────────────────────────────────────┐
│                    OpenCode Editor                       │
│                                                          │
│   [ Main Loop / Scheduler ]                              │
│          │                                               │
│          ├──(Stdio)──▶ [ Linter Agent ] ──▶ (Output)     │
│          │                                               │
│          ├──(Stdio)──▶ [ Formatter Agent ] ──▶ (Output)  │
│          │                                               │
│          ├──(File Share)──▶ [ Refactor Agent ] ──▶ (Diff)│
│          │                                               │
│          └──(File Share)──▶ [ Test Runner Agent ] ─▶ (OK)│
│                                                          │
│   [ Unified Output Panel ] ◀──── Merge Results           │
└──────────────────────────────────────────────────────────┘
```

*(注：验证参考了 `sst/opencode` 的 Go 源码，其内部大量使用 goroutine 并发执行外部子进程，并通过 Stdio 读取 JSON Lines。)*