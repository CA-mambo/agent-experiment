# OpenClaw 多智能体通信机制深度调研 (ACP + x402)

> **调研时间**: 2026-04-26 | **项目版本**: latest

## 1. 核心通信协议分析 (P2P)
- **ACP (Agent Communication Protocol)**: 发现与路由机制。Agent 启动时广播或注册到 `/.well-known/agent.json`，声明能力、端点、价格。
- **x402 (Payment Protocol)**: 微支付拦截器。在 ACP 层之上，拦截跨 Agent 服务请求，验证 Header 中的支付凭证（如 USDC 签名）。
- **去中心化架构**: 强调 Agent 间的直接交互与价值交换，而非中心化的主从控制。
- **身份签名**: ACP 消息包含 `signature`，确保消息来源不可抵赖。
- **动态组网**: 支持通过本地网络广播或远程注册中心发现新加入的 Agent。

## 2. 源码伪代码与架构图还原 (Python)
### ACP 发现与路由伪代码:
```python
class AgentCapability:
    def __init__(self, name: str, price: float, endpoint: str):
        self.name = name
        self.price = price
        self.endpoint = endpoint
    def to_dict(self) -> dict:
        return {"skill": self.name, "price": self.price, "url": self.endpoint}

class OpenClawAgent:
    async def advertise(self):
        # 广播或更新能力清单到注册中心/本地网络，声明自身能力与定价策略...
        manifest = [skill.to_dict() for skill in self.skills]
        await self.directory_service.register(self.agent_id, manifest)

class X402Interceptor:
    def validate(self, msg, required_price: float) -> bool:
        if not msg.payment_proof:
            raise PermissionError("Payment proof required")
        # 验证链上签名或预付款凭证，确保服务请求有效...
        return verify_crypto_signature(msg.sender, msg.payment_proof, required_price)
```

### ASCII 框架示意图:
```text
┌─────────────────────────────────────────────────────────────┐
│                        OpenClaw Ecosystem                   │
├──────────────────────┐            ┌─────────────────────────┤
│  Agent A (Client)    │            │  Agent B (Provider)     │
│                      │  ACP Msg   │                         │
│  [Intent: Translate] │───────────>│  [x402 Interceptor]     │
│  [USDC Payment Sig]  │            │      ↓ Validate         │
│                      │  Result    │  [Skill Executor]       │
│  [Translated Text]   │<───────────│      ↓ Execute          │
└──────────────────────┘            └─────────────────────────┘
        ▲                                    ▲
        │                                    │
        └─────────── ACP Discovery ──────────┘
          (/.well-known/agent.json Broadcast)
```

*(注：参考社区开源项目 `wgopar/a2a-x402-agent-template` 验证了微支付拦截机制的可行性。)*