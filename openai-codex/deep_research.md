# OpenAI Codex (Agent SDK) 多智能体通信机制深度调研 (Handoffs)

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心通信协议分析 (Pipeline)
- **Handoffs (交接机制)**: Agent 显式调用 Handoff Tool 移交控制权给另一个专家 Agent。底层通信高度依赖嵌套的 `tool_call` 序列。
- **Guardrails (上下文守卫)**: 严格过滤上下文，剥离工具调用历史（Tool Call/Output Items），防止提示词注入或上下文污染。
- **Function Calling 核心**: 通信高度依赖嵌套的 `tool_call` 序列，强制结构化输出（Pydantic/JSON Schema），确保下游能 100% 解析。
- **意图路由**: Agent A 根据用户输入或自身状态，显式调用一个特殊的 Function（Handoff Tool），将控制权连同当前上下文移交给 Agent B。
- **结构化输出**: 强制要求返回符合严格 JSON Schema 的数据，确保下游能 100% 解析。
- **确定性流水线**: 通信流程是串行的、高度可控的。每个 Agent 都是流程中的一个环节（Node）。
- **无缝接管**: Handoff 发生时，目标 Agent 会继承发起者的所有相关状态，就像人类交接工作一样自然。
- **权限分级**: 不同级别的 Agent 拥有不同的 Handoff 权限，低级 Agent 无法直接调用高级 Agent 的敏感接口。
- **回退机制**: 若目标 Agent 无法处理或报错，控制权可交还给上一级或主调度器。
- **状态同步**: 交接前后，上下文变量（如用户 ID、当前任务状态）必须严格对齐。
- **监控与追踪**: 每次 Handoff 都会生成唯一的 Trace ID，便于调试和分析整个决策链路。
- **循环检测**: 系统内置循环检测逻辑，防止 Agent A 把任务交给 Agent B，Agent B 又交回给 Agent A 的死循环。

## 2. 源码伪代码与架构图还原 (Python)
### Guardrails 上下文过滤 (参考 openai-agents-python):
```python
class ContextGuard:
    def filter_context(self, full_context, allowed_keys: List[str]):
        # 严格白名单过滤，剔除敏感信息和无关历史工具调用，确保交接安全...
        return {k: v for k, v in full_context.items() if k in allowed_keys}

def handoff_to_db_agent():
    """Handoff to the Database Specialist Agent."""
    return HandoffResult(reason="Need SQL expertise", transferred_context={"db_schema": "users"})
```

### ASCII 框架示意图:
```text
┌──────────────────────────────────────────────────────┐
│                    OpenAI Agent SDK                  │
│                                                      │
│  User Input ──▶ [ Orchestrator Agent ]                │
│                 [ Tools: handoff_A, handoff_B ]       │
│                                                      │
│           ┌────────────┴────────────┐                │
│           ▼                         ▼                │
│  [ Guardrail Filter A ]     [ Guardrail Filter B ]   │
│  (Strip Secrets)            (Limit History)          │
│           ▼                         ▼                │
│  [ Specialist Agent A ]     [ Specialist Agent B ]   │
│  (SQL Expert)               (UI Expert)              │
│           │                         │                │
│           └────────────┬────────────┘                │
│                        ▼                             │
│               [ Final Response ]                     │
└──────────────────────────────────────────────────────┘
```

*(注：源码验证参考了 `openai/openai-agents-python` 仓库中的 `handoff_filters.py`，其实现了明确的工具剥离逻辑。)*