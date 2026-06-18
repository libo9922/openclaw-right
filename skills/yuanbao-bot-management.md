# SKILL.md — 元宝 Bot 管理 (main agent 经验)

## 概述
腾讯元宝 (YuanBao) Bot 的配置、连接、多账号管理全流程。

## 插件信息
- 插件: `openclaw-plugin-yuanbao` v2.13.1
- 协议: WebSocket (wss://bot-wss.yuanbao.tencent.com)
- 认证: appKey + appSecret → sign-token → WS auth-bind

## 配置结构 (openclaw.json)
```json
{
  "channels": {
    "yuanbao": {
      "enabled": true,
      "accounts": {
        "cc": {
          "appId": "wx_your_appid",
          "appKey": "your_appkey",
          "appSecret": "your_appsecret",
          "botId": "bot_xxx"
        },
        "emma": {
          "appId": "wx_your_appid",
          "appKey": "your_appkey",
          "appSecret": "your_appsecret",
          "botId": "bot_xxx"
        }
      }
    }
  }
}
```

## Agent 绑定
```json
{
  "bindings": [
    {"agentId": "cc-agent", "match": {"channel": "yuanbao", "accountId": "cc"}},
    {"agentId": "emma-agent", "match": {"channel": "yuanbao", "accountId": "emma"}}
  ]
}
```

## 连接状态检查
```bash
# 查看日志
tail -50 /tmp/openclaw/openclaw-*.log | grep -i "yuanbao.*connected\|yuanbao.*error"

# 正常状态标志
# [cc] WS ready: connectId=xxx ✅
# [emma] WS ready: connectId=xxx ✅
```

## 踩坑记录
1. **单账号 vs accounts 结构**: 如果同时配了 base-level 和 accounts，base-level 默认账号不会连接。必须统一用 accounts 结构
2. **token 刷新**: sign-token 有效期 30 天，自动刷新间隔约 24 天
3. **Gateway 断连**: 元宝 WebSocket 依赖 gateway 进程，gateway 崩溃则全部断开
4. **网络超时**: 云容器中 `bot.yuanbao.tencent.com` 可能超时，需等待自动重连（最多 10 次）
5. **Agent workspace**: 绑定独立 workspace 后，agent 需要有完整的 AGENTS.md 才能正常回复
