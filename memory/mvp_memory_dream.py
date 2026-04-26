# -*- coding: utf-8 -*-
"""
MVP Simulation: Agent Memory Management & Dream Optimization
1. Short-term to Long-term Transfer (Summarization)
2. Auto-Retrieval (Simple Keyword/Vector Simulation)
3. Dream Optimization (Consolidation & Pruning)
"""

import asyncio
import time

class MemoryManager:
    def __init__(self, short_capacity=3):
        self.short_term = []  # Recent messages
        self.long_term = []   # Summaries / Facts
        self.short_capacity = short_capacity

    def add_message(self, msg: str):
        print(f"[Input] User: '{msg}'")
        self.short_term.append({"role": "user", "content": msg})
        
        # Check if Short-term is full
        if len(self.short_term) >= self.short_capacity:
            self.summarize_and_store()

    def summarize_and_store(self):
        # Mock Summarization: Just combine contents
        contents = [m["content"] for m in self.short_term]
        summary = f"Summary({', '.join(contents[:2])}...)"
        print(f"[Manager] Short-term Full! Summarizing -> '{summary}'")
        
        self.long_term.append({
            "type": "summary",
            "content": summary,
            "timestamp": time.time(),
            "keywords": self._extract_keywords(contents)
        })
        
        # Keep only the last message in short-term to maintain context continuity
        self.short_term = [self.short_term[-1]] 

    def _extract_keywords(self, texts):
        # Simple keyword extraction
        return " ".join(texts).lower().split()

    def retrieve(self, query: str) -> list:
        # Mock Retrieval: Simple keyword match
        print(f"[Retrieval] Searching memory for '{query}'...")
        results = []
        query_words = query.lower().split()
        for mem in self.long_term:
            if any(word in mem["keywords"] for word in query_words):
                results.append(mem["content"])
        return results

    async def dream_optimize(self):
        print("\n[Dream Optimizer] Sleeping... Analyzing long-term memory...")
        await asyncio.sleep(1) # Simulate processing time
        
        # 1. Deduplicate / Merge
        new_memories = []
        seen_topics = set()
        for mem in self.long_term:
            topic = mem["content"].split("(")[0] # Extract topic
            if topic not in seen_topics:
                seen_topics.add(topic)
                new_memories.append(mem)
            else:
                print(f"[Dream] Merged duplicate: '{mem['content']}'")

        # 2. Prune old/irrelevant (Keep top 5)
        self.long_term = new_memories[-5:]
        print(f"[Dream] Optimization Complete. Retained {len(self.long_term)} memories.\n")

# ================= MVP Run =================

async def main():
    print("--- Agent Memory & Dream MVP ---")
    manager = MemoryManager(short_capacity=3)

    # Phase 1: Populate Memory
    print("\n[Phase 1] Short-term Memory Overflow")
    manager.add_message("Fix the login bug")
    manager.add_message("The error is 404 Not Found")
    manager.add_message("Check the router config") # Triggers Summarization
    manager.add_message("Also, update the README")
    manager.add_message("Add a new feature for dark mode") # Triggers Summarization again

    # Phase 2: Retrieval
    print("\n[Phase 2] Auto-Retrieval Test")
    found = manager.retrieve("What was the login bug?")
    print(f"[Result] Found: {found}")

    # Phase 3: Dream Optimization
    print("\n[Phase 3] Dream Optimization (Background Task)")
    
    # Add some "duplicate" memories to trigger cleaning
    manager.long_term.append({"type": "fact", "content": "Summary(Fix login...)", "timestamp": 0, "keywords": ["login"]})
    
    await manager.dream_optimize()

if __name__ == "__main__":
    asyncio.run(main())
