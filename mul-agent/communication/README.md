# 🤖 Multi-Agent Communication Mechanisms Deep Research

> **Version**: v0.0.1  
> **Updated By**: mambo  
> **Last Updated**: 2026-04-26

本目录包含对当前头部 Agent 项目（OpenClaw, Claude Code, OpenAI Codex/Agents, OpenCode, Hermes）多智能体通信机制的深度调研。

### 📂 项目结构
每个子目录包含：
- `deep_research.md`: 核心协议分析、GitHub 官方/社区源码伪代码还原、框架示意图。
- `mvp_*.py`: 本地极简模拟脚本 (Python `asyncio` 原型验证)。

验证参考了 `openai/openai-agents-python` (Handoffs), `sst/opencode` (Tool Parallelism) 等官方仓库。

根目录包含通用性能对比基准测试脚本：
- `benchmark_communication.go`: 使用 Go 原生并发（Goroutines）模拟客户端请求，对比不同机制的延迟与吞吐量。

### 📊 Go 并发基准测试结果 (Goroutines)
| 通信机制 | 20并发 (req/s) | 100并发 (req/s) | 评价 |
| :--- | :--- | :--- | :--- |
| **Hermes (Pub/Sub)** | ~258 | **~1255** | ⭐ 扩展性极佳 |
| **OpenCode (Stdio)** | ~175 | **~835** | ⭐ 协程调度优势明显 |
| **OpenClaw (ACP)** | ~136 | **~672** | ✅ 支付验证开销可控 |
| **Codex (Handoff)** | ~102 | **~501** | ✅ 上下文过滤成本随并发增加 |
| **Claude Code (Sub-Agents)** | ~95 | **~480** | ✅ 上下文切片与合并开销稳定 |

### 🚀 如何使用
1.  **阅读调研**: 进入对应子目录查看 `deep_research.md`。
2.  **运行基准测试**: 确保安装了 Go 1.20+，运行 `go run benchmark_communication.go` 查看高并发下的性能表现。
3.  **运行 MVP 模拟**: 确保安装了 Python 环境 (uv)，进入子目录运行对应的 `mvp_*.py` 查看流程演示。
