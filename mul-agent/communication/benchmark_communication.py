# -*- coding: utf-8 -*-
"""
Multi-Agent Communication Benchmark
通用性能对比框架，模拟并发客户端请求，对比不同通信机制（ACP, Handoff, Pub/Sub）的延迟与吞吐量。
"""

import asyncio
import time
import random
from typing import List, Callable, Dict, Any

class CommunicationBenchmark:
    def __init__(self, name: str, handler: Callable, concurrency_levels: List[int] = [1, 5, 10, 20]):
        self.name = name
        self.handler = handler
        self.concurrency_levels = concurrency_levels

    async def run_single(self, n: int) -> float:
        """运行 N 个并发请求，返回总耗时"""
        start = time.time()
        tasks = [self.handler(f"req_{i}") for i in range(n)]
        await asyncio.gather(*tasks)
        return time.time() - start

    async def benchmark(self, iterations: int = 3):
        print(f"\n[BENCHMARK] {self.name}")
        print(f"{'Concurrency':<15} | {'Avg Time (s)':<12} | {'Throughput (req/s)':<18}")
        print("-" * 50)

        for level in self.concurrency_levels:
            times = []
            for _ in range(iterations):
                t = await self.run_single(level)
                times.append(t)
            
            avg_time = sum(times) / len(times)
            throughput = level / avg_time
            print(f"{level:<15} | {avg_time:<12.4f} | {throughput:<18.2f}")

# ================= 模拟处理函数 =================

async def mock_acp_handler(req_id: str):
    """模拟 OpenClaw ACP + x402 验证延迟"""
    await asyncio.sleep(random.uniform(0.05, 0.15)) # 网络 + 支付验证

async def mock_handoff_handler(req_id: str):
    """模拟 Codex Handoff 上下文守卫过滤延迟"""
    await asyncio.sleep(random.uniform(0.1, 0.2)) # 深度上下文拷贝

async def mock_pubsub_handler(req_id: str):
    """模拟 Hermes 消息总线路由延迟"""
    await asyncio.sleep(random.uniform(0.02, 0.08)) # 极低延迟的路由

async def mock_stdio_handler(req_id: str):
    """模拟 OpenCode 子进程 Stdio 延迟"""
    await asyncio.sleep(random.uniform(0.05, 0.12)) # 进程启动 + IO

# ================= 主运行器 =================

async def run_all_benchmarks():
    benchmarks = [
        CommunicationBenchmark("OpenClaw (ACP + x402)", mock_acp_handler),
        CommunicationBenchmark("Codex (Handoff + Guardrails)", mock_handoff_handler),
        CommunicationBenchmark("Hermes (Pub/Sub Bus)", mock_pubsub_handler),
        CommunicationBenchmark("OpenCode (Stdio Spawn)", mock_stdio_handler),
    ]

    print("=" * 50)
    print("  Multi-Agent Communication Mechanisms Benchmark")
    print("=" * 50)

    for b in benchmarks:
        await b.benchmark(iterations=3)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
