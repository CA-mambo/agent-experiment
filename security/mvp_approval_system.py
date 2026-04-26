# -*- coding: utf-8 -*-
"""
MVP Simulation: Agent Security & Approval System (Human-in-the-loop)
1. Async Blocking (Future mechanism)
2. Approval Resolution (Approve/Deny)
3. Timeout Fallback
"""

import asyncio
import uuid
import time

# 模拟审批结果枚举
class ApprovalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"

class ApprovalService:
    """Global Approval Service (Like QwenPaw's ApprovalService)"""
    def __init__(self):
        self.pending_requests = {}

    async def request_approval(self, tool_name: str, timeout: float = 3.0):
        """Agent requests permission to use a sensitive tool"""
        req_id = str(uuid.uuid4())[:6]
        print(f"[Security] [WARN] Sensitive tool '{tool_name}' requires approval! (ReqID: {req_id})")
        
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        self.pending_requests[req_id] = {
            "tool": tool_name,
            "future": future,
            "status": ApprovalStatus.PENDING,
            "created_at": time.time()
        }

        try:
            # Wait for user input with timeout
            print(f"[System] Waiting for user to type '/approve {req_id}' ...")
            decision = await asyncio.wait_for(future, timeout=timeout)
            print(f"[Security] [OK] Request {req_id} {decision}. Executing...")
            return True
        except asyncio.TimeoutError:
            print(f"[Security] [FAIL] Request {req_id} timed out. Cancelled execution.")
            self.pending_requests[req_id]["status"] = ApprovalStatus.TIMEOUT
            # Notify any other waiters if needed
            return False

    async def approve_request(self, req_id: str, approved: bool = True):
        """User approves or denies the request"""
        if req_id not in self.pending_requests:
            print(f"[System] Invalid Request ID: {req_id}")
            return

        req = self.pending_requests[req_id]
        future = req["future"]
        
        if not future.done():
            status = ApprovalStatus.APPROVED if approved else ApprovalStatus.DENIED
            req["status"] = status
            future.set_result(status) # Resume the agent!
        else:
            print(f"[System] Request {req_id} is already resolved.")

# ================= MVP Run =================

async def agent_task(name, approval_svc, tool_name, delay_before_use):
    print(f"\n--- Agent '{name}' starting... ---")
    await asyncio.sleep(delay_before_use) # Agent doing some prep work
    
    # Call sensitive tool
    success = await approval_svc.request_approval(tool_name)
    if success:
        print(f"  [Action] Executing {tool_name} successfully!")
    else:
        print(f"  [Action] Aborted {tool_name} due to security denial.")

async def user_interaction(approval_svc):
    """Simulate a user watching and typing commands"""
    await asyncio.sleep(1.5)
    print("\n[User] I see a request. Typing '/approve...")
    
    # Find pending request (Simulate user looking at screen)
    pending_ids = [k for k, v in approval_svc.pending_requests.items() if v["status"] == ApprovalStatus.PENDING]
    if pending_ids:
        req_id = pending_ids[0]
        await approval_svc.approve_request(req_id)
        print(f"[User] Request {req_id} approved.")

async def main():
    print("--- Agent Security & Approval MVP ---")
    svc = ApprovalService()

    # Scenario 1: User Approves quickly
    task = asyncio.create_task(agent_task("Coder", svc, "write_file", delay_before_use=1))
    await user_interaction(svc)
    await task

    # Scenario 2: Timeout (User is busy)
    print("\n--- Scenario: User Timeout ---")
    await agent_task("Admin", svc, "delete_db", delay_before_use=0)

if __name__ == "__main__":
    asyncio.run(main())
