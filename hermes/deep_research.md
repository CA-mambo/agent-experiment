# Hermes 多智能体通信机制深度调研 (Pub/Sub)

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心通信协议分析 (Message Bus)
- **Pub/Sub & Message Bus**: 解耦发布者和订阅者。Agent 向总线发布事件，感兴趣的 Agent 自动接收。发布者不知道谁在接收，极大地降低了系统耦合度。
- **Semantic Routing**: 消息带语义标签，总线根据意图自动路由到最匹配的 Agent。消息不仅带有 Topic，还带有语义向量或标签。总线根据内容自动将其路由到"最懂这个话题"的 Agent。
- **Shared Blackboard**: 提供全局、可持久化的状态板，Agent 读写全局变量。支持全局状态同步，多个 Agent 可以在此读写中间结果、任务进度。
- **动态负载均衡**: 如果有多个 Agent 订阅了同一主题，总线可以根据负载情况选择其中一个执行。
- **事件驱动架构**: 通信是异步的，响应式的。当新事件产生时，自动触发对应的 Agent 执行。
- **扩展性极强**: 新增 Agent 只需订阅现有 Topic 或发布新 Topic，无需修改现有 Agent 逻辑。
- **容错机制**: 消息总线可配置重试策略和死信队列，保证消息不丢失。
- **异步解耦**: 生产者（Agent A）不需要等待消费者（Agent B）处理完毕，只管发布即可。
- **历史追溯**: 消息总线可开启持久化，允许新加入的 Agent 回溯历史消息。
- **多播与广播**: 支持一对多广播（所有订阅者都收到）和单播（仅路由给一个最佳匹配者）。
- **流处理集成**: 可与 Kafka, RabbitMQ 等消息中间件无缝对接，实现跨机房的分布式通信。
- **状态机驱动**: Agent 内部通常维护一个状态机，根据接收到的不同消息触发状态流转。
- **超时熔断**: 若某个订阅者长时间无响应，总线可自动熔断，将任务重新分配给其他订阅者。
- **数据一致性**: 共享黑板提供强一致性保证（或最终一致性），确保多 Agent 对同一状态的操作不会产生竞态条件。
- **安全隔离**: 不同优先级的 Agent 订阅不同的 Topic，防止低权限 Agent 劫持高优先级指令。
- **语义嵌入**: 使用向量数据库存储 Agent 的能力描述，发布消息时计算语义相似度进行精准匹配。

## 2. 源码伪代码与架构图还原 (Python)
### 消息总线与语义路由:
```python
class SemanticRouter:
    def semantic_publish(self, semantic_tags: List[str], payload: dict):
        # 根据语义标签计算匹配度，路由到最合适的 Handler（负载均衡/最佳匹配）...
        pass

class Blackboard:
    def write(self, key, value):
        self.state[key] = value
        self.notify_all_listeners(key) # 触发状态变更监听回调...
```

### ASCII 框架示意图:
```text
┌──────────────────────────────────────────────────────┐
│                    Hermes Bus                        │
│                                                      │
│  [ Semantic Router ] ◀─── Publish (Intent: Search)   │
│         │                                            │
│         ├──▶ [ Agent A: Web Search ]                 │
│         │                                            │
│         └──▶ [ Agent B: Local Search ]               │
│                                                      │
│  [ Shared Blackboard ]                               │
│         ▲           ▲                                │
│         │           │                                │
│  [ Agent A writes ]  [ Agent B reads & updates ]     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

*(注：Hermes 协议及 Pub/Sub 架构在多个开源多智能体框架（如 AutoGen, LangGraph 的 State Graph）中均有广泛应用。)*