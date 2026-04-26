# -*- coding: utf-8 -*-
"""
MVP Simulation for Hermes (Message Bus, Pub/Sub & Shared Blackboard)
模拟基于消息总线的发布/订阅机制、语义路由与共享黑板。
"""

import asyncio
import time
import random
import uuid
from typing import Dict, List, Any, Callable

# ================= 基础组件 =================

class SharedBlackboard:
    """共享黑板，支持状态读写与变更监听"""
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.listeners: List[Callable] = []

    def write(self, key: str, value: Any):
        self.state[key] = value
        for cb in self.listeners:
            cb(key, value)

    def read(self, key: str) -> Any:
        return self.state.get(key)

    def subscribe(self, callback: Callable):
        self.listeners.append(callback)

class HermesBus:
    """Hermes 消息总线：支持 Topic Pub/Sub 和语义路由"""
    def __init__(self, blackboard: SharedBlackboard):
        self.blackboard = blackboard
        self.subscribers: Dict[str, List[Callable]] = {}
        self.semantic_registry: Dict[str, List[str]] = {} # topic -> tags

    def subscribe(self, topic: str, tags: List[str], handler: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)
        self.semantic_registry[topic] = tags

    async def publish(self, topic: str, payload: dict):
        handlers = self.subscribers.get(topic, [])
        tasks = [h(payload) for h in handlers]
        await asyncio.gather(*tasks)

    async def semantic_publish(self, query_tags: List[str], payload: dict):
        """根据语义标签匹配最相关的 Topic"""
        best_topic = None
        max_score = 0
        
        for topic, tags in self.semantic_registry.items():
            # 简单交集计算匹配度
            score = len(set(query_tags) & set(tags))
            if score > max_score:
                max_score = score
                best_topic = topic
        
        if best_topic:
            print(f"[Bus] Routed to '{best_topic}' (Score: {max_score})")
            await self.publish(best_topic, payload)
        else:
            print(f"[Bus] No matching topic for tags: {query_tags}")

# ================= Agent 模拟 =================

class HermesAgent:
    def __init__(self, name: str, bus: HermesBus):
        self.name = name
        self.bus = bus

    async def handle_data(self, payload: dict):
        print(f"[{self.name}] Received: {payload.get('task')}")
        await asyncio.sleep(random.uniform(0.1, 0.3))
        self.bus.blackboard.write(f"result_{self.name}", f"Done by {self.name}")

# ================= 模拟运行 =================

async def run_simulation():
    blackboard = SharedBlackboard()
    bus = HermesBus(blackboard)

    # 注册黑板监听
    blackboard.subscribe(lambda k, v: print(f"[Blackboard] Updated {k} = {v}"))

    # 创建 Agent 并订阅
    search_agent = HermesAgent("WebSearch_Agent", bus)
    local_agent = HermesAgent("LocalFile_Agent", bus)

    # WebSearch 订阅 "search" 话题，带有 ["network", "web"] 标签
    bus.subscribe("search", ["network", "web"], search_agent.handle_data)
    # LocalFile 订阅 "search" 话题，带有 ["local", "disk"] 标签
    bus.subscribe("search", ["local", "disk"], local_agent.handle_data)
    
    # 另一个 Agent 订阅 "analysis"
    analysis_agent = HermesAgent("DataAnalysis_Agent", bus)
    bus.subscribe("analysis", ["compute", "stats"], analysis_agent.handle_data)

    print("--- Hermes Bus & Blackboard Simulation ---")
    start = time.time()

    # 1. 语义路由测试：发布一个带有 network 标签的请求
    await bus.semantic_publish(["network", "fast"], {"task": "Find latest AI news"})

    # 2. 直接发布到 Topic
    await bus.publish("analysis", {"task": "Calculate stats"})

    # 3. 读取黑板结果
    print(f"\n[Final] Blackboard State: {blackboard.state}")
    print(f"--- Finished in {time.time() - start:.2f}s ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())
