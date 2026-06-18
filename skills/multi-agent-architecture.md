# SKILL.md — 多 Agent 架构设计 (main agent 经验)

## 概述
OpenClaw 多 Agent 架构的设计与配置经验。

## Agent 列表
| Agent ID | 职责 | Workspace | 绑定渠道 |
|----------|------|-----------|----------|
| main | 主 agent，协调一切 | /root/.openclaw/workspace | webchat |
| cc-agent | PPT 制作 | /root/.openclaw/cc-agent | 元宝 cc |
| emma-agent | 视频制作 | /root/.openclaw/emma-agent | 元宝 emma |
| monitor | 健康监控 | /root/.openclaw/workspace/monitor | cron |
| good_job | 辅助任务 | /root/.openclaw/workspace/good_job | - |

## 配置结构 (openclaw.json)
```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "model": {"primary": "xiaomi-token-plan/mimo-v2.5-pro"}
    },
    "list": [
      {"id": "main"},
      {"id": "cc-agent", "workspace": "/root/.openclaw/cc-agent"},
      {"id": "emma-agent", "workspace": "/root/.openclaw/emma-agent"},
      {"id": "qwen-agent", "workspace": "/root/.openclaw/qwen-agent"},
      {"id": "comfyui-agent", "workspace": "/root/.openclaw/comfyui-agent"}
    ]
  },
  "bindings": [
    {"agentId": "cc-agent", "match": {"channel": "yuanbao", "accountId": "cc"}},
    {"agentId": "emma-agent", "match": {"channel": "yuanbao", "accountId": "emma"}}
  ]
}
```

## Agent Workspace 结构
```
/root/.openclaw/<agent-name>/
├── SOUL.md          # 人格定义
├── AGENTS.md        # 行为规范
├── IDENTITY.md      # 身份信息
├── USER.md          # 用户信息
├── TOOLS.md         # 工具配置
├── HEARTBEAT.md     # 心跳任务
└── workspace/       # 工作目录
```

## 子 Agent 调度
```python
# 通过 sessions_spawn 创建子 agent
# 在 exec 中调用其他 agent 的能力
```

## 踩坑记录
1. **Binding 路由**: 配了 binding 后，元宝消息会路由到指定 agent，如果 agent workspace 不完整会卡住
2. **独立 workspace**: 每个 agent 需要独立的 AGENTS.md 和 SOUL.md，否则用默认模板
3. **共享模型**: 所有 agent 共用同一个 LLM 模型，通过 agent 隔离 prompt
4. **Gateway 依赖**: 所有 agent 的消息收发都依赖 gateway 进程
5. **ComfyUI 共享**: 多个 agent 可以共用同一个 ComfyUI 实例（端口 8188）
