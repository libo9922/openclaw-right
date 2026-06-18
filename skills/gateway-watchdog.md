# SKILL.md — Gateway 守护与监控 (monitor agent 经验)

## 概述
OpenClaw Gateway 的健康监控、自动恢复、崩溃预防方案。

## 问题背景
在容器环境中，Gateway 进程容易因以下原因崩溃：
- exec session 结束时连带清理子进程
- 长时间运行的后台任务被 SIGTERM 杀掉
- 网络超时导致 WebSocket 断连

## Watchdog 守护脚本
```bash
#!/bin/bash
# /root/.openclaw/gateway-watchdog.sh
GATEWAY_URL="http://127.0.0.1:18789/health"
CHECK_INTERVAL=15
CRASH_COOLDOWN=5
MAX_RESTARTS=50
RESTART_COUNT=0

check_gateway() {
    curl -s --connect-timeout 3 --max-time 5 "$GATEWAY_URL" 2>/dev/null | grep -q '"ok":true'
}

start_gateway() {
    cd /root/.openclaw
    openclaw gateway >> /var/log/openclaw-gateway.log 2>&1 &
    for i in $(seq 1 20); do
        sleep 2
        check_gateway && return 0
    done
    return 1
}

FAIL_COUNT=0
while true; do
    if check_gateway; then
        FAIL_COUNT=0
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [ $FAIL_COUNT -ge 3 ]; then
            pkill -f "openclaw gateway" 2>/dev/null
            sleep $CRASH_COOLDOWN
            start_gateway
            FAIL_COUNT=0
        fi
    fi
    sleep $CHECK_INTERVAL
done
```

## 启动方式
```bash
chmod +x /root/.openclaw/gateway-watchdog.sh
nohup /root/.openclaw/gateway-watchdog.sh &
```

## 健康检查 API
```bash
# Gateway 存活检查
curl -s http://127.0.0.1:18789/health
# 返回: {"ok":true,"status":"live"}

# 元宝连接状态
tail -20 /tmp/openclaw/openclaw-*.log | grep "yuanbao.*WS ready"
```

## 踩坑记录
1. **连续 3 次才重启**: 避免网络抖动导致误判
2. **pkill 先杀再启**: 防止端口冲突
3. **日志分开**: watchdog 日志 `/var/log/gateway-watchdog.log`，gateway 日志 `/var/log/openclaw-gateway.log`
4. **openclaw cron 受限**: 容器中 CLI 需要 `operator.admin` scope，需要先批准配对
5. **不要用 systemd**: 容器中没有 systemd，用 nohup + bash 脚本最可靠
