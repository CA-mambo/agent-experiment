# -*- coding: utf-8 -*-
"""
MVP Simulation: Agent Evaluation
1. Multi-metric Evaluation (Accuracy, Cost, Steps)
2. LLM-as-a-Judge Simulation
3. Report Generation
"""

import time
import random
from typing import List, Dict, Any

class Metric:
    def __init__(self, name: str):
        self.name = name
    
    def evaluate(self, expected: Any, actual: Any, context: Dict) -> float:
        raise NotImplementedError

class ExactMatchMetric(Metric):
    def evaluate(self, expected: Any, actual: Any, context: Dict) -> float:
        if isinstance(expected, str) and isinstance(actual, str):
            return 1.0 if expected.lower().strip() == actual.lower().strip() else 0.0
        return 0.0

class LLMJudgeMetric(Metric):
    def evaluate(self, expected: Any, actual: Any, context: Dict) -> float:
        # Simulate LLM judge giving a score between 0 and 1
        # In real life, this calls an LLM with a prompt like "Rate this response..."
        return random.uniform(0.7, 1.0)

class CostMetric(Metric):
    def evaluate(self, expected: Any, actual: Any, context: Dict) -> float:
        # Lower is better, normalize to 0-1
        tokens = context.get("tokens_used", 1000)
        score = max(0, 1.0 - (tokens / 2000.0))
        return score

class Evaluator:
    def __init__(self):
        self.metrics = [ExactMatchMetric("Accuracy"), LLMJudgeMetric("Quality"), CostMetric("CostEfficiency")]
    
    def run_evaluation(self, task: str, expected: Any, actual: Any, context: Dict) -> Dict[str, float]:
        results = {}
        print(f"\n[Evaluator] Evaluating task: '{task}'")
        for metric in self.metrics:
            score = metric.evaluate(expected, actual, context)
            results[metric.name] = score
            print(f"  - {metric.name}: {score:.2f}")
        return results

# --- Simulated Agent Task ---

def run_agent_task(task: str) -> Dict:
    print(f"[Agent] Running task: '{task}'")
    time.sleep(0.5)
    tokens = random.randint(100, 1500)
    result = {
        "answer": "The weather is sunny with 25C.", # Simulated correct answer
        "tokens": tokens
    }
    return result

# --- MVP Run ---

def main():
    print("--- Agent Evaluation MVP ---")
    
    evaluator = Evaluator()
    
    test_cases = [
        ("What is the weather?", "The weather is sunny with 25C."),
        ("Find files in /tmp", "No files found."), # Agent fails this one intentionally
    ]
    
    all_reports = []
    
    for task, expected_answer in test_cases:
        # Run Agent
        agent_result = run_agent_task(task)
        
        # Evaluate
        report = evaluator.run_evaluation(
            task=task,
            expected=expected_answer,
            actual=agent_result["answer"],
            context={"tokens_used": agent_result["tokens"]}
        )
        all_reports.append(report)

    # Summary
    print("\n--- Final Evaluation Summary ---")
    avg_acc = sum(r["Accuracy"] for r in all_reports) / len(all_reports)
    avg_cost = sum(r["CostEfficiency"] for r in all_reports) / len(all_reports)
    print(f"Overall Accuracy: {avg_acc:.2%}")
    print(f"Overall Cost Efficiency: {avg_cost:.2%}")

if __name__ == "__main__":
    main()
