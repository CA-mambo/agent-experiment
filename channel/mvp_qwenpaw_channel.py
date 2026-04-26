# -*- coding: utf-8 -*-
"""
MVP Simulation for QwenPaw Channel Mechanism
模拟 QwenPaw 的核心机制：三维优先级队列、动态消费者、超时保护、流式思维链分发。
"""

import asyncio
import time
import random
from typing import Dict, Tuple

# ================= 核心数据结构 =================

QueueKey = Tuple[str, str, int]  # (channel_id, session_id, priority)

class Event:
    """模拟 Agent 产出的流式事件"""
    def __init__(self, type: str, content: str = "", delta: bool = False):
        self.type = type  # MESSAGE, REASONING, FUNCTION_CALL, TOOL_OUTPUT
        self.content = content
        self.delta = delta

class AgentRequest:
    def __init__(self, query: str, session_id: str, channel: str):
        self.query = query
        self.session_id = session_id
        self.channel = channel

# ================= 优先级注册表 =================

class PriorityRegistry:
    """模拟 QwenPaw 的优先级计算逻辑"""
    def __init__(self):
        self.rules = {
            "/stop": 0,
            "/kill": 0,
            "/status": 10,
            "/restart": 10
        }
        self.default = 20

    def get_level(self, query: str) -> int:
        q_lower = query.strip().lower()
        for prefix, level in self.rules.items():
            if q_lower.startswith(prefix):
                return level
        return self.default

# ================= 统一队列管理器 =================

class UnifiedQueueManager:
    def __init__(self, consumer_fn, queue_maxsize=5, idle_timeout=2.0):
        self.queues: Dict[QueueKey, asyncio.Queue] = {}
        self.consumers: Dict[QueueKey, asyncio.Task] = {}
        self.consumer_fn = consumer_fn
        self.registry = PriorityRegistry()
        self.maxsize = queue_maxsize
        self.idle_timeout = idle_timeout

    async def enqueue(self, req: AgentRequest):
        priority = self.registry.get_level(req.query)
        key = (req.channel, req.session_id, priority)
        
        if key not in self.queues:
            print(f"[Manager] Creating new queue & consumer for {key}")
            self.queues[key] = asyncio.Queue(maxsize=self.maxsize)
            # 启动动态消费者
            self.consumers[key] = asyncio.create_task(
                self.consumer_fn(self.queues[key], key)
            )
        
        try:
            # 模拟超时保护，防止无限阻塞
            await asyncio.wait_for(self.queues[key].put(req), timeout=5.0)
            print(f"[Manager] Enqueued {req.query} -> Priority {priority}")
        except asyncio.TimeoutError:
            print(f"[Manager] WARNING: Queue FULL for {key}! Message dropped.")
        except asyncio.CancelledError:
            print(f"[Manager] CANCELLED: Enqueue cancelled for {key}.")

    async def stop_all(self):
        for task in self.consumers.values():
            task.cancel()
        await asyncio.gather(*self.consumers.values(), return_exceptions=True)
        print("[Manager] All consumers stopped.")

# ================= 消费者逻辑 (Agent Runtime 模拟) =================

async def agent_runtime_consumer(queue: asyncio.Queue, key: QueueKey):
    """模拟从队列取消息并执行 Agent 行为链/思维链"""
    print(f"[Consumer] Started for {key}")
    try:
        while True:
            req = await queue.get()
            print(f"\n[Agent] Processing '{req.query}' (Channel: {key[0]})")
            
            # 模拟网络抖动或处理延迟
            processing_time = random.uniform(0.5, 2.0)
            
            # 思维链流式输出
            if "how" in req.query.lower() or "why" in req.query.lower():
                print(f"   [Stream] [Reasoning] Analyzing request...")
                await asyncio.sleep(0.3)
                print(f"   [Stream] [Reasoning] Retrieving knowledge...")
                await asyncio.sleep(0.3)

            # 工具链调用
            if "search" in req.query.lower() or "calculate" in req.query.lower():
                print(f"   [Tool] Calling Tool: search_api('{req.query}')")
                await asyncio.sleep(0.5)
                print(f"   [Tool] Tool Output: Found 3 results.")
            
            # 最终响应
            print(f"   [Response] Done! Answering user...")
            await asyncio.sleep(processing_time)
            
            queue.task_done()
            
            # 模拟 idle 清理：如果队列空了且一段时间没新消息，可以自我销毁
            # 这里为了演示简单，不做复杂的定时器销毁
    except asyncio.CancelledError:
        print(f"[Consumer] Terminated for {key}")

# ================= 主运行模拟 =================

async def run_simulation():
    print("--- QwenPaw Channel MVP Simulation ---")
    
    manager = UnifiedQueueManager(agent_runtime_consumer, queue_maxsize=3)
    
    # 1. 模拟普通消息 (Priority 20)
    await manager.enqueue(AgentRequest("Hello, what's the weather?", "user1", "feishu"))
    
    # 2. 模拟快速连续发消息 (触发队列堆积测试)
    await manager.enqueue(AgentRequest("Tell me a joke", "user1", "feishu"))
    await manager.enqueue(AgentRequest("What is AI?", "user1", "feishu"))
    await manager.enqueue(AgentRequest("Write code for me", "user1", "feishu"))
    await manager.enqueue(AgentRequest("This might be dropped if queue is full", "user1", "feishu"))
    
    await asyncio.sleep(0.5)
    
    # 3. 模拟紧急命令插队 (Priority 0)
    # 注意：它属于同一个 session，但是优先级不同，所以会进入一个新的队列！
    await manager.enqueue(AgentRequest("/stop", "user1", "feishu"))
    
    await asyncio.sleep(3)
    await manager.stop_all()
    print("--- Finished ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())
