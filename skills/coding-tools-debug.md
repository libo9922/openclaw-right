# SKILL.md — 编程工具调试与配置 (good_job 实战经验)

## 概述
在 AMD ROCm 云容器环境中配置和调试 Claude Code、Codex CLI 的完整经验。

---

## 一、环境诊断清单

当 Claude 或 Codex 无法工作时，按此顺序排查：

### 1. DNS 解析
```bash
# 检查域名是否可解析
getent hosts agentrouter.org
nslookup agentrouter.org 2>&1 | head -5

# 如果 DNS 不稳定，加到 /etc/hosts
echo "47.237.14.184 agentrouter.org" >> /etc/hosts
echo "8.219.105.94 agentrouter.org" >> /etc/hosts
```

### 2. 网络连通性
```bash
# 强制 IPv4 测试（容器中 IPv6 通常不通）
curl -4 -s --connect-timeout 5 -o /dev/null -w '%{http_code}' https://agentrouter.org/

# 如果 curl 不加 -4 超时，说明是 IPv6 优先的问题
curl -s --connect-timeout 5 -o /dev/null -w '%{http_code}' https://agentrouter.org/
```

### 3. 配置文件
```bash
# Claude 配置
cat ~/.claude/settings.json

# Codex 配置
cat ~/.codex/config.toml
cat ~/.codex/auth.json
```

---

## 二、Claude Code 调试

### 常见问题

#### 问题 1: DNS 解析超时
**症状**: `curl: (28) Resolving timed out after 5001 milliseconds`
**原因**: 容器 DNS 不稳定，IPv6 优先但不通
**解决**:
```bash
# 方案 A: 加 /etc/hosts
echo "47.237.14.184 agentrouter.org" >> /etc/hosts

# 方案 B: 强制 IPv4
curl -4 -s https://agentrouter.org/
```

#### 问题 2: API 端点不可达
**症状**: `ECONNREFUSED` 或 `ETIMEDOUT`
**检查**:
```bash
# 测试 API 端点
curl -s https://agentrouter.org/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### Claude CLI 使用
```bash
# 非交互模式
echo "say hi" | timeout 30 claude --print

# 查看版本
claude --version

# 查看配置
cat ~/.claude/settings.json
```

---

## 三、Codex CLI 调试

### 常见问题

#### 问题 1: `wire_api` 配置错误
**症状**: `invalid wire_api: chat`
**原因**: 新版 Codex 要求 `wire_api = "responses"`，不是 `"chat"`
**解决**:
```toml
# ~/.codex/config.toml
[model_providers.openai-chat-completions]
wire_api = "responses"  # 不是 "chat"
```

#### 问题 2: `env_key` 配置错误
**症状**: `401 Unauthorized` 或找不到 API key
**原因**: `env_key` 应该是环境变量名，不是 key 本身
**错误写法**:
```toml
env_key = "sk-aFk...s8yB"  # ❌ 这是 key 值
```
**正确写法**:
```toml
env_key = "OPENAI_API_KEY"  # ✅ 这是环境变量名
```
然后在 `auth.json` 中配置 key 映射：
```json
{
  "OPENAI_API_KEY": "sk-aFk...s8yB"
}
```

#### 问题 3: 代理不支持 `/v1/responses` 端点
**症状**: `404 Not Found` 或 `endpoint not supported`
**原因**: Codex 要求 `/v1/responses` 端点，但代理只支持 `/v1/chat/completions`
**解决**:
```bash
# 方案 A: 升级代理支持 responses API
# 方案 B: 降级 Codex 到支持 wire_api="chat" 的版本
# 方案 C: 直连 OpenAI API（不走代理）
export OPENAI_API_KEY="sk-..."
codex exec "say hi"
```

#### 问题 4: TTY 要求
**症状**: `error: a terminal is required`
**原因**: Codex 默认需要交互式终端
**解决**:
```bash
# 用 exec 模式（非交互）
codex exec "your task here"

# 或用 pty
exec pty=true ...
```

### Codex CLI 使用
```bash
# 非交互模式
codex exec "write a hello world in Python"

# 查看帮助
codex --help

# 查看版本
codex --version
```

---

## 四、配置文件参考

### Claude 配置 (~/.claude/settings.json)
```json
{
  "apiProvider": "anthropic",
  "apiKey": "sk-ant-...",
  "model": "claude-sonnet-4-20250514",
  "endpoint": "https://agentrouter.org/"
}
```

### Codex 配置 (~/.codex/config.toml)
```toml
[model_providers.openai-chat-completions]
wire_api = "responses"
base_url = "https://agentrouter.org/v1"
env_key = "OPENAI_API_KEY"

[default]
model = "gpt-4o"
model_provider = "openai-chat-completions"
```

### Codex 认证 (~/.codex/auth.json)
```json
{
  "OPENAI_API_KEY": "sk-aFk...s8yB"
}
```

---

## 五、网络问题速查表

| 症状 | 原因 | 解决 |
|------|------|------|
| DNS 超时 | IPv6 优先但不通 | 加 /etc/hosts 或 curl -4 |
| 连接超时 | 代理不可达 | 检查代理状态 |
| 401 Unauthorized | API key 错误 | 检查 auth.json |
| 404 Not Found | 端点不支持 | 升级代理或降级 CLI |
| TTY required | 交互模式限制 | 用 `exec` 子命令 |

---

## 六、最佳实践

### 网络稳定性
```bash
# 1. 始终加 /etc/hosts 绕过 DNS 不稳定
echo "47.237.14.184 agentrouter.org" >> /etc/hosts

# 2. 测试时用 -4 强制 IPv4
curl -4 -s https://agentrouter.org/

# 3. 设置合理的超时
timeout 30 claude --print "task"
```

### 配置管理
```bash
# 备份配置
cp ~/.claude/settings.json ~/.claude/settings.json.bak
cp ~/.codex/config.toml ~/.codex/config.toml.bak

# 修改前先检查现有状态
cat ~/.codex/config.toml | grep wire_api
```

### 调试流程
```bash
# 1. 检查网络
curl -4 -s --connect-timeout 5 -o /dev/null -w '%{http_code}' https://agentrouter.org/

# 2. 检查配置
cat ~/.claude/settings.json
cat ~/.codex/config.toml

# 3. 测试 API
echo "hi" | timeout 30 claude --print
codex exec "say hi"

# 4. 查看日志
cat ~/.claude/history.jsonl | tail -5
```

---

## 七、踩坑记录

| 坑 | 详情 | 解决 |
|----|------|------|
| DNS 间歇性失败 | 容器中 DNS 解析不稳定，有时成功有时超时 | 写死 /etc/hosts |
| IPv6 优先 | curl 默认先尝试 IPv6，容器中通常不通 | curl -4 强制 IPv4 |
| wire_api 变更 | Codex 新版要求 "responses"，旧版用 "chat" | 更新 config.toml |
| env_key 误解 | 应该是变量名不是值 | 改成 "OPENAI_API_KEY" |
| TTY 限制 | Codex 交互模式需要终端 | 用 codex exec |
| 代理端点不全 | 某些代理不支持 /v1/responses | 直连或升级代理 |
