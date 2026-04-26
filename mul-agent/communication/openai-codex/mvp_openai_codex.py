# -*- coding: utf-8 -*-
"""
MVP Simulation for OpenAI Codex / Agent SDK (Handoffs & Guardrails)
模拟显式交接机制与上下文守卫（Guardrails）过滤。
"""

import asyncio
import time
import random
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# ================= 基础数据结构 =================

@dataclass
class ContextState:
    user_query: str
    history: List[str] = field(default_factory=list)
    sensitive_data: Dict[str, str] = field(default_factory=dict)
    task_specific: Dict[str, Any] = field(default_factory=dict)

class Guardrail:
    """模拟上下文守卫，严格白名单过滤"""
    def __init__(self, allowed_keys: List[str]):
        self.allowed_keys = allowed_keys

    def apply(self, context: ContextState) -> ContextState:
        # 过滤敏感数据
        safe_data = {k: v for k, v in context.task_specific.items() if k in self.allowed_keys}
        return ContextState(
            user_query=context.user_query,
            history=context.history[-2:], # 只保留最近两条历史
            sensitive_data={}, # 彻底清空敏感数据
            task_specific=safe_data
        )

# ================= OpenAI Agent 模拟 =================

class CodexAgent:
    def __init__(self, name: str, capabilities: List[str], guardrail: Optional[Guardrail] = None):
        self.name = name
        self.capabilities = capabilities
        self.guardrail = guardrail
        self.handoff_targets: Dict[str, 'CodexAgent'] = {}

    def register_handoff(self, intent: str, target: 'CodexAgent'):
        self.handoff_targets[intent] = target

    async def process(self, context: ContextState) -> Dict[str, Any]:
        print(f"[{self.name}] Processing: '{context.user_query}'")
        
        # 1. 检查是否需要 Handoff
        target_intent = self._decide_handoff(context)
        if target_intent:
            target_agent = self.handoff_targets[target_intent]
            return await self._perform_handoff(target_agent, context)

        # 2. 本地执行
        await asyncio.sleep(random.uniform(0.2, 0.5))
        return {"agent": self.name, "result": f"Processed locally by {self.name}"}

    def _decide_handoff(self, context: ContextState) -> Optional[str]:
        # 简单路由逻辑：只在已注册的目标中寻找匹配，防止叶子节点死循环
        for intent in self.handoff_targets:
            if "db" in context.user_query.lower() or "sql" in context.user_query.lower():
                if intent == "db_expert": return intent
            elif "ui" in context.user_query.lower() or "css" in context.user_query.lower():
                if intent == "ui_expert": return intent
        return None

    async def _perform_handoff(self, target: 'CodexAgent', context: ContextState) -> Dict[str, Any]:
        print(f"[{self.name}] Decided to handoff to [{target.name}]")
        
        # 应用 Guardrail
        safe_context = context
        if target.guardrail:
            safe_context = target.guardrail.apply(context)
            print(f"[{self.name}] Guardrail applied. Safe keys: {list(safe_context.task_specific.keys())}")

        # 移交控制权
        return await target.process(safe_context)

# ================= 模拟运行 =================

async def run_simulation():
    # 定义专家 Agent 和它们的 Guardrails
    db_guard = Guardrail(allowed_keys=["table_schema", "query_history"])
    ui_guard = Guardrail(allowed_keys=["component_tree", "theme"])

    db_agent = CodexAgent("DB_Specialist", ["sql"], db_guard)
    ui_agent = CodexAgent("UI_Specialist", ["css"], ui_guard)

    # 定义 Orchestrator
    orchestrator = CodexAgent("Orchestrator", ["general"])
    orchestrator.register_handoff("db_expert", db_agent)
    orchestrator.register_handoff("ui_expert", ui_agent)

    # 模拟几个并发请求
    tasks = [
        orchestrator.process(ContextState(user_query="Fix the SQL login bug", task_specific={"table_schema": "users", "api_token": "SECRET"})),
        orchestrator.process(ContextState(user_query="Make the button blue", task_specific={"component_tree": "Header", "user_pass": "SECRET"})),
        orchestrator.process(ContextState(user_query="General greeting", task_specific={"lang": "en"})),
    ]

    print("--- OpenAI Codex Handoff Simulation ---")
    start = time.time()
    results = await asyncio.gather(*tasks)
    print(f"--- Finished in {time.time() - start:.2f}s ---")
    for r in results:
        print(f"Result: {r}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
