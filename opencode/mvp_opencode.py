# -*- coding: utf-8 -*-
"""
MVP Simulation for OpenCode (Parallel Tool Agents & Stdio/File Share)
模拟终端编辑器中多工具插件的并发执行，对比 Stdio 与文件共享通信的性能。
"""

import asyncio
import time
import random
import uuid
import os
import json
import tempfile
from typing import List, Dict, Any

# ================= 基础模拟组件 =================

class ToolAgent:
    def __init__(self, name: str, exec_time: float = 0.2):
        self.name = name
        self.exec_time = exec_time

    async def run_stdio(self, input_data: Any) -> str:
        """模拟通过 Stdio 传递小数据"""
        await asyncio.sleep(self.exec_time + random.uniform(0.01, 0.05))
        return f"[{self.name}] Stdio Result: {str(input_data)[:20]}..."

    async def run_file_share(self, input_data: Any, work_dir: str) -> str:
        """模拟通过文件共享传递大数据"""
        task_id = uuid.uuid4().hex[:8]
        input_path = os.path.join(work_dir, f"{task_id}_in.json")
        output_path = os.path.join(work_dir, f"{task_id}_out.json")
        
        # 写入输入文件 (模拟大数据写入)
        await asyncio.sleep(0.1) 
        with open(input_path, 'w') as f:
            json.dump({"size": len(str(input_data)), "data": "big_payload"}, f)
            
        # 处理
        await asyncio.sleep(self.exec_time)
        
        # 写入输出文件
        with open(output_path, 'w') as f:
            json.dump({"result": "processed_large_data"}, f)
            
        return f"[{self.name}] FileShare Result (Task {task_id})"


class OpenCodeScheduler:
    def __init__(self):
        self.tools: Dict[str, ToolAgent] = {}
        self.work_dir = tempfile.mkdtemp()

    def register(self, name: str, tool: ToolAgent):
        self.tools[name] = tool

    async def run_parallel_stdio(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """并发执行：使用 Stdio"""
        coroutines = []
        for t in tasks:
            agent = self.tools[t["tool"]]
            coroutines.append(agent.run_stdio(t["input"]))
        return await asyncio.gather(*coroutines)

    async def run_parallel_file_share(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """并发执行：使用文件共享 (适合大数据)"""
        coroutines = []
        for t in tasks:
            agent = self.tools[t["tool"]]
            coroutines.append(agent.run_file_share(t["input"], self.work_dir))
        return await asyncio.gather(*coroutines)

# ================= 模拟运行 =================

async def run_simulation():
    scheduler = OpenCodeScheduler()
    scheduler.register("linter", ToolAgent("Linter", 0.3))
    scheduler.register("formatter", ToolAgent("Formatter", 0.2))
    scheduler.register("refactor", ToolAgent("Refactor", 0.4))

    # 模拟轻量任务 (适合 Stdio)
    small_tasks = [
        {"tool": "linter", "input": "check_syntax(main.py)"},
        {"tool": "formatter", "input": "format_code(main.py)"},
        {"tool": "linter", "input": "check_syntax(utils.py)"},
    ]

    # 模拟重量任务 (适合 File Share)
    big_payload = "X" * 500000 # 500KB 数据
    big_tasks = [
        {"tool": "refactor", "input": big_payload},
        {"tool": "refactor", "input": big_payload},
    ]

    print("--- OpenCode Stdio Simulation (Small Data) ---")
    start = time.time()
    res1 = await scheduler.run_parallel_stdio(small_tasks)
    print(f"Finished in {time.time() - start:.2f}s")

    print("\n--- OpenCode FileShare Simulation (Big Data) ---")
    start = time.time()
    res2 = await scheduler.run_parallel_file_share(big_tasks)
    print(f"Finished in {time.time() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(run_simulation())
