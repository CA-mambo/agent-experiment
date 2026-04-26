# Agent Architecture Deep Research & MVP Benchmarks

> **Release**: `v0.0.1` | **Updated**: 2026-04-26 13:00 (UTC+8) | **Maintainer**: mambo & ca

---

## 🚀 Overview
This module contains deep-dive research into the core mechanisms of top-tier open-source Agent frameworks (AgentScope, LangChain, etc.), combined with **pseudo-code implementations** and **MVP (Minimum Viable Product)** benchmarks to validate architectural decisions.

**Target**: To dissect, understand, and reproduce the internal logic of modern Agent systems, from communication protocols to memory management.

## 📦 Module Manifest
Current directory structure and core research subjects:

| Module | Focus Area | Validation Artifact |
| :--- | :--- | :--- |
| `channel/` | Gateway, Heartbeat & Debounce | `mvp_qwenpaw_channel.py` |
| `communication/` | Multi-Agent Protocols (Go/Python) | `benchmark_communication.go` |
| `evaluate/` | LLM-as-Judge & Cost Metrics | `mvp_evaluation.py` |
| `mcp_protocol/` | MCP Client & Tool Discovery | `mvp_mcp.py` |
| `memory/` | Dream Optimization & Vector Retrieval | `mvp_memory_dream.py` |
| `pipeline/` | Workflow Orchestration (Fan-out/Seq) | `mvp_pipeline.py` |
| `planning/` | Explicit Plans & Memory Compression | `mvp_planning.py` |
| `security/` | Async Approval & Circuit Breakers | `mvp_approval_system.py` |
| `skills/` | Skill Pool & Env Isolation | `mvp_skill_loader.py` |
| `subagent/` | Sub-Agent Lifecycle & Sandbox | `mvp_subagent_lifecycle.py` |
| `trace/` | OpenTelemetry & Observability | `mvp_tracing.py` |

*(Note: `mul-agent/` contains historical communication baselines and sub-repo research.)*

## 💡 Key Findings
1.  **Priority Routing (Channel)**: Implemented a 3D priority routing system (Source/Context/Urgency) to prevent queue blocking.
2.  **Async Approval (Security)**: Modeled on `asyncio.Future` to allow non-blocking user interaction with strict timeout circuit breakers.
3.  **Dream Optimization (Memory)**: Automated background summarization turns chaotic logs into structured, persistent knowledge.
4.  **Protocol Unification (MCP)**: Standardized tool exposure via JSON Schema extraction, decoupling Agent logic from Tool implementation.

## 🛠️ Local Dev Guide
- **Python**: `uv run <module>/mvp_*.py`
- **Go**: `go run <module>/benchmark_*.go`

---

## 📖 项目概述 (中文)
本项目针对主流开源 Agent 框架的核心机制进行**源码级调研**，并通过**伪代码复现**与**MVP 基准测试**验证架构设计的可行性。

### 🔧 模块清单
- `channel/`: 网关心跳与消息防抖
- `communication/`: 多智能体通信协议与并发基准
- `evaluate/`: LLM 裁判评估体系与成本监控
- `mcp_protocol/`: MCP 协议接入与工具动态发现
- `memory/`: 记忆管理与做梦优化机制
- `pipeline/`: 串行/并行工作流编排
- `planning/`: 任务规划与结构化压缩
- `security/`: 异步审批与超时熔断
- `skills/`: 技能池加载与环境隔离
- `subagent/`: 子代理生命周期管理与沙箱
- `trace/`: 全链路追踪与可观测性

### 🌟 核心发现
- 采用了基于优先级的三维路由防止消息堆积。
- 使用 `asyncio.Future` 实现无阻塞的安全审批机制。
- 通过后台“做梦”整理碎片化日志为结构化知识。
- 借助 MCP 协议统一工具暴露标准，实现逻辑解耦。
