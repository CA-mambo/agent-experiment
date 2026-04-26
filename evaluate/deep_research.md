# Agent 评估与评测机制深度调研 (Evaluation)

> **调研时间**: 2026-04-26 | **项目版本**: latest (AgentScope `evaluate`, OpenEval)

## 1. 核心机制：从结果到过程
Agent 的评估不再局限于最终答案的对错（如传统的 Exact Match），而是深入到**执行过程**和**多维指标**。

| 评估维度 | 典型指标 | 核心逻辑 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **结果准确性** | Exact Match, F1, LLM-as-Judge | 对比最终输出与 Ground Truth。 | QA, 摘要, 代码生成。 |
| **过程合规性** | Trajectory Score, Step Check | 检查 Agent 是否遵循了特定步骤或约束。 | 复杂推理, 安全合规。 |
| **效率与成本** | Token Usage, Tool Calls, Latency | 统计消耗的资源和时间。 | 成本控制, 性能优化。 |
| **工具调用** | Tool Success Rate, Argument Match | 检查工具是否被正确调用且参数合法。 | 搜索, 数据库, API 调用。 |

## 2. AgentScope (`evaluate`) 源码解析
AgentScope 提供了一套灵活的评测框架：
*   **Evaluator**: 抽象基类，支持自定义评估逻辑。
*   **Metric**: 封装了具体的评估算法（如 `Accuracy`, `LLMEval`).
*   **Workflow Integration**: 可以直接嵌入到 Agent 的运行循环中，实现实时的自我评估或事后批量评估。

### 📊 典型架构 (LLM-as-a-Judge)
当没有标准答案时，使用强大的 LLM (如 GPT-4) 作为裁判，根据评分标准（Rubric）对 Agent 的输出进行打分。

---

## 3. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                      Evaluation Pipeline                         │
│                                                                  │
│  [ Task Dataset ] ─▶ [ Agent Execution ] ─▶ [ Agent Output ]     │
│                         │                       │                │
│                         ▼                       ▼                │
│              [ Ground Truth ]           [ Evaluation Engine ]    │
│                                         │                        │
│                               ┌───────────┴───────────┐          │
│                               ▼                       ▼          │
│                       [ Rule-Based ]           [ LLM-as-Judge ]  │
│                      (Regex, Matching)         (Scoring, Rubric) │
│                               │                       │          │
│                               └───────────┬───────────┘          │
│                                           ▼                      │
│                                    [ Evaluation Report ]         │
│                                    (Accuracy, Cost, Score)       │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 本地极简 MVP 代码 (`mvp_evaluation.py`)

模拟 Agent 评估机制：
1. **任务集**: 包含多个输入和预期结果。
2. **执行器**: 模拟 Agent 运行。
3. **评估器**: 混合使用“规则匹配”和“LLM 模拟打分”来输出评估报告。
