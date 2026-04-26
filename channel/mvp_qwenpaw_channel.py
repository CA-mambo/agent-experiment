# -*- coding: utf-8 -*-
"""
MVP Simulation for QwenPaw Channel & Heartbeat Mechanism
1. Debounce/Buffer (Non-text message merging)
2. Heartbeat Injection (Direct Event sending)
3. Priority Interruption (/stop task cancellation)
"""

import asyncio

class Event:
    def __init__(self, type, content="", status="completed"):
        self.type = type
        self.content = content
        self.status = status

class AgentRunner:
    async def stream_query(self, query):
        yield Event("message", "Starting process...")
        yield Event("reasoning", "Thinking about the query...")
        await asyncio.sleep(2.0) 
        yield Event("reasoning", "Calling tools...")
        yield Event("tool_output", "Got 3 search results.")
        await asyncio.sleep(1.0)
        yield Event("message", "Final Answer: Process Complete!", status="completed")

class ChannelRenderer:
    def __init__(self, name):
        self.name = name
    
    async def render_event(self, event):
        icon = {"message": "[MSG]", "reasoning": "[THOUGHT]", "tool_output": "[TOOL]"}.get(event.type, "[?]")
        print(f"[{self.name}] {icon} {event.content}")

class UnifiedQueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.renderer = ChannelRenderer("Feishu Client")
        self.runner = AgentRunner()
        self._current_task = None 

    async def enqueue(self, req, priority=20):
        if req.get("type") == "image":
            print("[Manager] Buffering non-text message... waiting for text.")
            await asyncio.sleep(0.1) 
        print(f"[Manager] Enqueued '{req.get('text', 'non-text')}' (P{priority})")
        await self.queue.put({"req": req, "priority": priority})

    async def enqueue_critical(self, req):
        print(f"[Manager] CRITICAL: '{req.get('text')}' (Priority 0!) -> Interrupting!")
        if self._current_task:
            self._current_task.cancel()

    async def send_event(self, event):
        print("[Heartbeat] Injecting event directly to renderer!")
        await self.renderer.render_event(event)

    async def process_queue(self):
        print("[Consumer] Loop started.")
        try:
            while True:
                payload = await self.queue.get()
                req = payload["req"]
                
                if req.get("text") == "/stop":
                    print(f"[Manager] /stop received!")
                    continue

                print(f"[Consumer] Processing '{req.get('text')}'...")
                try:
                    self._current_task = asyncio.current_task()
                    async for event in self.runner.stream_query(req.get("text")):
                        await self.renderer.render_event(event)
                except asyncio.CancelledError:
                    print(f"[Consumer] Cancelled by /stop!")
                    await self.renderer.render_event(Event("message", "WARNING: Task Cancelled."))
                except Exception as e:
                    print(f"[Consumer] Error: {e}")
                finally:
                    self._current_task = None
                self.queue.task_done()
        except asyncio.CancelledError:
            print("[Consumer] Consumer loop terminated.")

    async def heartbeat(self):
        while True:
            await asyncio.sleep(4) 
            print("\n[Heartbeat] Waking up...")
            await self.send_event(Event("message", "[STATUS] All Systems Normal."))

async def main():
    print("--- QwenPaw Channel & Heartbeat MVP ---")
    manager = UnifiedQueueManager()
    task = asyncio.create_task(manager.process_queue())
    hb_task = asyncio.create_task(manager.heartbeat())

    await manager.enqueue({"id": "1", "text": "Tell me a joke"})
    await asyncio.sleep(0.2)
    await manager.enqueue({"id": "2", "type": "image"})

    await asyncio.sleep(0.8) 
    print("\n--- User sends /stop ---")
    await manager.enqueue_critical({"id": "3", "text": "/stop"}) 

    await asyncio.sleep(6) 
    task.cancel()
    hb_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
