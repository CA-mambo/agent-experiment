# Agent 技能/工具管理机制深度调研 (Skills & Tools)

> **调研时间**: 2026-04-26 | **项目版本**: latest (QwenPaw `skills_manager.py`, MCP)

## 1. 核心机制：从 MCP 到 本地技能池
在 Agent 架构中，“工具” (Tools) 和 “技能” (Skills) 是让 Agent 具备行动能力的关键。主流方案主要分为两类：

| 机制类型 | 典型代表 | 核心逻辑 | 优缺点 |
| :--- | :--- | :--- | :--- |
| **MCP (Model Context Protocol)** | QwenPaw, Cursor | **API 驱动**。Agent 通过 Stdio 或 HTTP 与外部 Server 通信，动态获取工具列表。 | ✅ 跨语言、安全隔离；❌ 延迟稍高，依赖外部进程。 |
| **本地技能池 (Local Skill Pool)** | QwenPaw (`skill_pool`), Claude | **文件驱动**。每个技能是一个目录，包含 `SKILL.md` (描述) 和脚本。Agent 直接加载。 | ✅ 极致快速，易于人类编辑；❌ 依赖本地环境配置。 |

## 2. QwenPaw (`skills_manager.py`) 源码深度解析
通过分析 `agentscope-ai/QwenPaw` 源码，其技能管理机制非常精细：

### 🧩 技能生命周期
1.  **发现 (Discovery)**: 系统定期扫描 `skill_pool` 和内置目录 (`skills/`)，寻找包含 `SKILL.md` 的文件夹。
2.  **解析 (Parsing)**: 使用 `frontmatter` 解析 Markdown 头部的 YAML 元数据（如 `name`, `version`, `requires`）。
3.  **注册 (Registration)**: 更新 `skill.json` 清单。如果发生名称冲突，系统会自动添加时间戳后缀（如 `skill_name-20260426`）。
4.  **执行 (Execution)**: 
    *   **环境注入**: 在执行特定技能前，将相关配置注入环境变量 (`QWENPAW_SKILL_CONFIG_...`)。
    *   **清理**: 执行完毕后，通过 `finally` 块恢复原始环境变量。

### 🔒 安全与隔离
- **Zip 炸弹防护**: 导入技能包时限制解压大小 (200MB)，并禁止软链接。
- **沙箱扫描**: `skill_scanner` 会检查脚本内容，防止恶意代码注入。

---

## 3. 源码级架构还原 (ASCII)

```text
┌──────────────────────────────────────────────────────────────────┐
│                        Agent Skill System                        │
│                                                                  │
│  [ User / System ] ──(Drop Zip/Dir)──▶ [ Skill Pool Directory ]  │
│                                          │                       │
│                                          ▼                       │
│                                    [ Skill Scanner ]             │
│                                    (Parse SKILL.md)              │
│                                          │                       │
│                                          ▼                       │
│                                  [ Manifest Reconcile ]          │
│                                  (Update skill.json)             │
│                                          │                       │
│                                          ▼                       │
│                                  [ Agent Execution ]             │
│                           (Inject Config Env Vars)               │
└──────────────────────────────────────────────────────────────────┘
```

## 4. 本地极简 MVP 代码 (`mvp_skill_loader.py`)

模拟 QwenPaw 的技能管理机制：
1. **动态加载**: 扫描目录并注册技能。
2. **环境隔离**: 执行技能时注入临时环境变量，执行完自动清理。
3. **冲突处理**: 当技能名重复时，模拟重命名策略。

*(注：源码分析基于 GitHub 仓库 `agentscope-ai/QwenPaw` 的 `skills_manager.py`。)*
