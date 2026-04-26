# -*- coding: utf-8 -*-
"""
MVP Simulation for Sub-Agent Lifecycle
模拟主流 Agent 的子代理管理机制：
1. Dynamic Spawning (动态生成)
2. Context Slicing (上下文切片/过滤)
3. Permission Sandbox (权限沙箱)
4. Reaping (生命周期回收)
"""

import asyncio
import random
import uuid

# ================= 基础组件 =================

class ContextFilter:
    """模拟 OpenAI/Claude 的上下文守卫机制"""
    @staticmethod
    def slice(full_context: dict, relevant_keys: list[str]) -> dict:
        """从全局上下文中切片，仅保留必要信息"""
        return {k: full_context.get(k) for k in relevant_keys}

class Sandbox:
    """模拟 Claude Code 的权限沙箱"""
    def __init__(self, allowed_permissions: list[str]):
        self.allowed = set(allowed_permissions)

    def check(self, action: str) -> bool:
        return action in self.allowed

# ================= 子代理定义 =================

class SubAgent:
    def __init__(self, role: str, permissions: list[str], context: dict):
        self.id = str(uuid.uuid4())[:4]
        self.role = role
        self.sandbox = Sandbox(permissions)
        self.context = context  # 仅包含切片后的局部记忆
        self.is_alive = True

    async def execute_task(self, task: str) -> dict:
        if not self.is_alive:
            return {"status": "error", "msg": "Agent is dead."}
        
        print(f"  [Sub-{self.role} ({self.id})] Executing: {task}")
        print(f"  [Sub-{self.role} ({self.id})] Context Loaded: {list(self.context.keys())}")

        # 模拟工作过程
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # 模拟权限检查 (模拟越权操作)
        needs_write = "fix" in task.lower() or "write" in task.lower() or "style" in task.lower()
        action = "write_code" if needs_write else "read_file"
        
        print(f"  [Sub-{self.role} ({self.id})] Attempting Action: {action}")
        if not self.sandbox.check(action):
            print(f"  [Sandbox] [DENIED] Permission Denied: Action '{action}' requires higher privileges!")
            return {"status": "denied", "reason": f"Sandbox blocked {action}"}
        
        print(f"  [Sub-{self.role} ({self.id})] Task Done!")
        return {"status": "success", "result": f"Output from {self.role}", "agent_id": self.id}

    def destroy(self):
        """模拟生命周期结束后的资源回收"""
        self.is_alive = False
        self.context.clear()  # 清除局部记忆
        print(f"  [Manager] Reaping Sub-Agent {self.id} ({self.role})...")

# ================= 管理器 (Manager) =================

class SubAgentManager:
    def __init__(self):
        self.active_agents: list[SubAgent] = []
        self.global_memory = {
            "repo_structure": "Full Codebase...",
            "user_secrets": "API_KEY=12345",
            "relevant_files": ["main.py", "utils.py"],
            "goal": "Fix the bug in login"
        }

    async def spawn_and_run(self, role: str, permissions: list[str], task: str):
        # 1. Context Slicing (上下文过滤，防止泄露 Secrets)
        # 模拟：只允许看到 goal 和 relevant_files，隐藏 user_secrets
        safe_keys = ["goal", "relevant_files"]
        local_context = ContextFilter.slice(self.global_memory, safe_keys)
        print(f"[Manager] Spawning {role} agent... Context filtered.")

        # 2. Instantiate SubAgent
        agent = SubAgent(role, permissions, local_context)
        self.active_agents.append(agent)

        # 3. Execute
        try:
            res = await agent.execute_task(task)
            return res
        finally:
            # 4. Reap (销毁回收)
            agent.destroy()
            self.active_agents.remove(agent)

# ================= 模拟运行 =================

async def main():
    print("--- Sub-Agent Lifecycle MVP ---")
    manager = SubAgentManager()

    # 场景 1: 正常任务 (代码生成)
    print("\n[Scenario 1] Spawn Frontend Specialist")
    res = await manager.spawn_and_run(
        role="Frontend",
        permissions=["read_file", "write_code"],
        task="Fix UI button style"
    )
    print(f"Result: {res}\n")

    # 场景 2: 权限受限任务 (试图越权)
    print("\n[Scenario 2] Spawn Junior Reader (Limited Permission)")
    res = await manager.spawn_and_run(
        role="Reader",
        permissions=["read_file"], # 没有 write_code 权限
        task="Fix UI button style"
    )
    print(f"Result: {res}\n")

    # 场景 3: 验证记忆隔离 (Context Slicing)
    # 虽然我们在日志中看不到 SubAgent 内部的 Secrets，但可以通过检查 local_context 确认
    print("\n[Scenario 3] Context Isolation Check")
    print(f"Global Memory has secrets? {'user_secrets' in manager.global_memory}")
    # Agent 内部已经 clear，验证 Reap 逻辑

if __name__ == "__main__":
    asyncio.run(main())
