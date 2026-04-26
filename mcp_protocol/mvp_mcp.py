# -*- coding: utf-8 -*-
"""
MVP Simulation: MCP (Model Context Protocol) Client
1. Simulated Stateful Connection
2. Tool Discovery & Schema Extraction
3. Tool Call Execution
"""

import time
import random
from typing import Dict, Any

# --- Simulated MCP Server ---

class MockMCPServer:
    def __init__(self):
        self.tools = {
            "get_repo": {"desc": "Get repository details", "params": {"repo": "str"}},
            "list_issues": {"desc": "List issues in a repo", "params": {"repo": "str", "state": "str"}},
            "create_issue": {"desc": "Create a new issue", "params": {"repo": "str", "title": "str", "body": "str"}}
        }
        print("[MCP Server] Initialized with 3 tools.")

    def call_tool(self, name: str, args: Dict[str, str]):
        print(f"  [MCP Server] Executing tool '{name}' with args: {args}")
        time.sleep(0.3)
        return {"result": f"Successfully executed {name}"}

# --- MCP Client Simulation ---

class MCPClient:
    def __init__(self, server: MockMCPServer):
        self.server = server
        self.connected = False
        self.tools_schema = {}

    async def connect(self):
        print("[MCP Client] Connecting to server...")
        time.sleep(0.5)
        self.connected = True
        # Discover tools
        self.tools_schema = {
            name: {"description": info["desc"], "parameters": info["params"]}
            for name, info in self.server.tools.items()
        }
        print(f"[MCP Client] Connected! Discovered {len(self.tools_schema)} tools.")

    def get_tool(self, name: str):
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        if name not in self.tools_schema:
            raise ValueError(f"Tool '{name}' not found")
        
        schema = self.tools_schema[name]
        
        # Return a wrapper function
        def wrapper(**kwargs):
            return self.server.call_tool(name, kwargs)
        return wrapper

# --- Agent Interaction ---

async def main():
    print("--- MCP Protocol MVP ---")
    
    server = MockMCPServer()
    client = MCPClient(server)
    
    # 1. Connect
    await client.connect()
    
    # 2. Get Tool & Call
    print("\n[Agent] Getting tool 'get_repo'...")
    get_repo = client.get_tool("get_repo")
    
    result1 = get_repo(repo="CA-mambo/agent-experiment")
    print(f"[Agent] Result: {result1}")

    # 3. Another Tool
    print("\n[Agent] Getting tool 'list_issues'...")
    list_issues = client.get_tool("list_issues")
    
    result2 = list_issues(repo="CA-mambo/agent-experiment", state="open")
    print(f"[Agent] Result: {result2}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
