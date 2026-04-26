# -*- coding: utf-8 -*-
"""
MVP Simulation for OpenClaw (ACP + x402)
模拟多智能体去中心化通信与微支付拦截机制。
使用 asyncio 模拟并发请求和异步响应。
"""

import asyncio
import time
import random
import uuid
from typing import Dict, List, Callable, Any
from dataclasses import dataclass

# ================= 基础模拟组件 =================

@dataclass
class Message:
    msg_id: str
    sender: str
    receiver: str
    intent: str
    payload: Any
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class AgentRegistry:
    """模拟去中心化注册表 / 广播发现机制"""
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}

    def register(self, agent_id: str, capabilities: List[str], prices: Dict[str, float]):
        self.agents[agent_id] = {"capabilities": capabilities, "prices": prices}

    def discover(self, intent: str) -> List[str]:
        """发现能处理某意图的 Agent"""
        return [aid for aid, info in self.agents.items() if intent in info["capabilities"]]


class X402PaymentGateway:
    """模拟 x402 微支付协议"""
    def __init__(self):
        self.wallets: Dict[str, float] = {}

    def deposit(self, agent_id: str, amount: float):
        self.wallets[agent_id] = self.wallets.get(agent_id, 0.0) + amount

    def transfer(self, sender: str, receiver: str, amount: float) -> bool:
        if self.wallets.get(sender, 0.0) >= amount:
            self.wallets[sender] -= amount
            self.wallets[receiver] = self.wallets.get(receiver, 0.0) + amount
            return True
        return False

# ================= OpenClaw Agent 模拟 =================

class OpenClawAgent:
    def __init__(self, agent_id: str, registry: AgentRegistry, gateway: X402PaymentGateway):
        self.agent_id = agent_id
        self.registry = registry
        self.gateway = gateway
        self.skills: Dict[str, Callable] = {}
        self.prices: Dict[str, float] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()

    def add_skill(self, name: str, price: float, func: Callable):
        self.skills[name] = func
        self.prices[name] = price

    async def start(self):
        # 注册到全局发现
        self.registry.register(self.agent_id, list(self.skills.keys()), self.prices)
        print(f"[{self.agent_id}] Registered skills: {list(self.skills.keys())}")

    async def send_request(self, intent: str, payload: Any, timeout: float = 2.0):
        targets = self.registry.discover(intent)
        if not targets:
            print(f"[{self.agent_id}] No provider found for {intent}")
            return None
        
        target = targets[0] # 简单选第一个
        price = self.registry.agents[target]["prices"][intent]

        # x402 支付拦截
        if not self.gateway.transfer(self.agent_id, target, price):
            print(f"[{self.agent_id}] Payment failed for {intent} to {target}")
            return None
        
        msg = Message(uuid.uuid4().hex[:8], self.agent_id, target, intent, payload)
        print(f"[{self.agent_id}] Sent {intent} to {target} (Paid ${price})")
        
        # 异步等待响应 (模拟网络延迟)
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return f"Result for {intent} from {target}"

    async def handle_messages(self):
        while True:
            msg = await self.message_queue.get()
            # 模拟技能执行
            if msg.intent in self.skills:
                result = await self.skills[msg.intent](msg.payload)
                print(f"[{self.agent_id}] Executed {msg.intent}, returning result.")
            self.message_queue.task_done()

# ================= 模拟运行 =================

async def dummy_translator(payload):
    await asyncio.sleep(0.2)
    return f"Translated: {payload}"

async def dummy_coder(payload):
    await asyncio.sleep(0.3)
    return f"Code generated for: {payload}"

async def run_simulation():
    registry = AgentRegistry()
    gateway = X402PaymentGateway()

    # 充值
    gateway.deposit("Client_Agent", 100.0)

    # 创建专家 Agent
    translator = OpenClawAgent("Translator_Pro", registry, gateway)
    translator.add_skill("translate", 2.0, dummy_translator)

    coder = OpenClawAgent("Coder_Pro", registry, gateway)
    coder.add_skill("code_gen", 5.0, dummy_coder)

    await translator.start()
    await coder.start()

    # 客户端并发请求
    client = OpenClawAgent("Client_Agent", registry, gateway)
    
    print("\n--- Starting Concurrent Requests ---")
    tasks = [
        client.send_request("translate", "Hello World"),
        client.send_request("code_gen", "Python QuickSort"),
        client.send_request("translate", "OpenClaw is cool"),
        client.send_request("translate", "Async IO"),
    ]
    
    start = time.time()
    results = await asyncio.gather(*tasks)
    print(f"--- All finished in {time.time() - start:.2f}s ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())
