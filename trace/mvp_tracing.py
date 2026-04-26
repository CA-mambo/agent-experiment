# -*- coding: utf-8 -*-
"""
MVP Simulation: Agent Tracing & Observability
1. Decorator Injection (@trace_llm, @trace_tool)
2. Hierarchical Spans (Parent-Child relationships)
3. Metrics Collection (Tokens, Latency, Status)
"""

import time
import uuid
import random
from typing import Dict, Any

class Span:
    def __init__(self, name: str, parent: "Span" = None):
        self.trace_id = parent.trace_id if parent else str(uuid.uuid4())[:8]
        self.span_id = str(uuid.uuid4())[:6]
        self.parent_id = parent.span_id if parent else "root"
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.status = "OK"
        self.attributes: Dict[str, Any] = {}
        self.error = None

    def finish(self, error: Exception = None):
        self.end_time = time.time()
        if error:
            self.status = "ERROR"
            self.error = str(error)
            self.attributes["error.message"] = str(error)

    def __repr__(self):
        duration = (self.end_time - self.start_time) * 1000 if self.end_time else 0
        status_icon = "[OK]" if self.status == "OK" else "[ERR]"
        indent = "  " * (0 if self.parent_id == "root" else 1)
        return f"{indent}{status_icon} [{self.name}] {duration:.2f}ms | Attrs: {self.attributes}"

# --- Tracing Context ---

class TracingContext:
    def __init__(self):
        self.current_span: Span = None
        self.spans = []

    def start_span(self, name: str) -> Span:
        span = Span(name, parent=self.current_span)
        self.spans.append(span)
        self.current_span = span
        return span

    def end_span(self, span: Span, error: Exception = None):
        span.finish(error)
        self.current_span = span.parent_id == "root" and None or self._find_parent(span)
        self.export(span)

    def _find_parent(self, span: Span) -> Span:
        for s in reversed(self.spans):
            if s.span_id == span.parent_id: return s
        return None

    def export(self, span: Span):
        print(f"[Exporter] {span}")

context = TracingContext()

# --- Decorators ---

def trace_llm(func):
    def wrapper(*args, **kwargs):
        span = context.start_span("LLM Call")
        span.attributes["model"] = args[0] if args else "unknown"
        span.attributes["input_tokens"] = kwargs.get("tokens", 0)
        try:
            result = func(*args, **kwargs)
            span.attributes["output_tokens"] = result.get("tokens", 0)
            return result
        except Exception as e:
            context.end_span(span, e)
            raise
        finally:
            if span.end_time is None: context.end_span(span)
    return wrapper

def trace_tool(func):
    def wrapper(*args, **kwargs):
        span = context.start_span("Tool Execution")
        span.attributes["tool_name"] = func.__name__
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            context.end_span(span, e)
            raise
        finally:
            if span.end_time is None: context.end_span(span)
    return wrapper

# --- Agent Logic ---

@trace_llm
def call_model(model: str, tokens: int):
    time.sleep(random.uniform(0.5, 1.0))
    return {"content": "Weather is sunny", "tokens": tokens + 20}

@trace_tool
def search_weather_api(query: str):
    time.sleep(random.uniform(0.2, 0.5))
    if "error" in query.lower():
        raise ValueError("API Connection Timeout")
    return {"temp": 25}

def agent_loop(query: str):
    span = context.start_span("Agent Loop")
    try:
        print(f"\n[Agent] Processing: '{query}'")
        data = search_weather_api(query)
        print(f"  [Tool] Got data: {data}")
        response = call_model("GPT-4", tokens=50)
        print(f"  [LLM] Final response: {response['content']}")
    except Exception as e:
        context.end_span(span, e)
        print(f"  [Agent] Failed: {e}")
        return
    finally:
        if span.end_time is None: context.end_span(span)

# --- MVP Run ---

def main():
    print("--- Agent Tracing & Observability MVP ---")
    
    print("\n[Case 1] Successful Execution")
    agent_loop("What is the weather?")

    print("\n[Case 2] Tool Failure")
    agent_loop("Get weather error")

if __name__ == "__main__":
    main()
