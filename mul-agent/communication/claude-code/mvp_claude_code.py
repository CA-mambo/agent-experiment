# -*- coding: utf-8 -*-
"""
MVP Simulation for Claude Code (Sub-agents & Context Handoff)
模拟主从架构下的子代理动态生成、上下文压缩与结果合并。
使用 asyncio 模拟并发子任务执行。
"""

import asyncio
import time
import random
import uuid
from typing import Dict, List, Any
from dataclasses import dataclass, field

# ================= 基础数据结构 =================

@dataclass
class RepoContext:
    files: Dict[str, str]
    goal: str
    patches: List[str] = field(default_factory=list)

@dataclass
class TaskSlice:
    description: str
    relevant_files: List[str]
    permissions: List[str] # 例如: ["READ", "WRITE_CSS"]

# ================= Claude Code Agent 模拟 =================

class ClaudeAgent:
    def __init__(self, agent_id: str, parent_id: str = None, context: RepoContext = None, permissions: List[str] = None):
        self.agent_id = agent_id
        self.parent_id = parent_id
        self.context = context or RepoContext(files={}, goal="")
        self.permissions = permissions or ["ALL"]
        self.sub_agents: List['ClaudeAgent'] = []

    def _compress_context(self, task: TaskSlice) -> RepoContext:
        """模拟上下文手递手：只提取相关文件"""
        sliced_files = {f: self.context.files.get(f, "") for f in task.relevant_files}
        return RepoContext(files=sliced_files, goal=task.description, patches=[])

    def _check_permission(self, action: str) -> bool:
        if "ALL" in self.permissions:
            return True
        return action in self.permissions

    async def execute_task(self, task: TaskSlice) -> Dict[str, Any]:
        """执行分配的任务，必要时生成子代理"""
        print(f"[{self.agent_id}] Starting task: {task.description}")
        
        # 模拟复杂任务拆分为子任务
        if len(task.relevant_files) > 2 and "DELEGATE" in self.permissions:
            sub_tasks = self._split_task(task)
            sub_results = await asyncio.gather(*[
                self._spawn_sub_agent(st).execute_task(st) for st in sub_tasks
            ])
            
            # 合并子代理结果
            combined_patches = []
            for res in sub_results:
                combined_patches.extend(res.get("patches", []))
            return {"patches": combined_patches, "status": "DONE"}
        
        # 模拟本地执行
        await asyncio.sleep(random.uniform(0.2, 0.6))
        patch_name = f"Patch_{self.agent_id}_{uuid.uuid4().hex[:4]}"
        print(f"[{self.agent_id}] Generated {patch_name}")
        return {"patches": [patch_name], "status": "DONE"}

    def _split_task(self, task: TaskSlice) -> List[TaskSlice]:
        """简单将文件列表拆分"""
        mid = len(task.relevant_files) // 2
        return [
            TaskSlice(description=f"Part 1 of {task.description}", relevant_files=task.relevant_files[:mid], permissions=["WRITE"]),
            TaskSlice(description=f"Part 2 of {task.description}", relevant_files=task.relevant_files[mid:], permissions=["WRITE"])
        ]

    def _spawn_sub_agent(self, task: TaskSlice) -> 'ClaudeAgent':
        sub_id = f"Sub_{self.agent_id}_{uuid.uuid4().hex[:4]}"
        sub_ctx = self._compress_context(task)
        # 子代理权限受限
        sub_perms = ["WRITE"] if "WRITE" in self.permissions else ["READ"]
        sub = ClaudeAgent(sub_id, self.agent_id, sub_ctx, sub_perms)
        self.sub_agents.append(sub)
        return sub

# ================= 模拟运行 =================

async def run_simulation():
    # 初始化主代理，拥有完整上下文和委派权限
    main_ctx = RepoContext(
        files={f"file_{i}.py": f"Content of file {i}" for i in range(6)},
        goal="Refactor the entire codebase"
    )
    main_agent = ClaudeAgent("Main", context=main_ctx, permissions=["ALL", "DELEGATE"])

    # 提交一个涉及多个文件的复杂任务
    big_task = TaskSlice(
        description="Refactor Utils Module",
        relevant_files=[f"file_{i}.py" for i in range(6)],
        permissions=["DELEGATE"]
    )

    print("--- Claude Code Sub-agent Simulation ---")
    start = time.time()
    result = await main_agent.execute_task(big_task)
    print(f"--- Finished in {time.time() - start:.2f}s ---")
    print(f"Total Patches Generated: {len(result['patches'])}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
