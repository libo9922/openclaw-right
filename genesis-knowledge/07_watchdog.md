# 07 — Watchdog 守护脚本

## 用途

监控 OpenClaw Gateway 进程，崩溃时自动重启。

## 脚本位置

`/root/.openclaw/gateway-watchdog.sh`

## 核心逻辑

```bash
check_gateway() {
    curl -s --connect-timeout 3 --max-time 5 \
        "http://127.0.0.1:18789/health" 2>/dev/null | grep -q '"ok":true'
}

# 主循环：每 15 秒检查一次
while true; do
    if check_gateway; then
        FAIL_COUNT=0
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [ "$FAIL_COUNT" -ge 3 ]; then
            pkill -f "openclaw gateway"
            sleep 5
            openclaw gateway &
        fi
    fi
    sleep 15
done
```

## 配置项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| CHECK_INTERVAL | 15s | 检查间隔 |
| MAX_RESTARTS | 50 | 最大重启次数 |
| CRASH_COOLDOWN | 5s | 重启后等待时间 |

## 关键设计

1. **连续 3 次失败才重启** — 避免网络抖动误判
2. **先 pkill 再启动** — 防止端口冲突
3. **日志分离** — watchdog 日志和 gateway 日志分开
4. **不用 systemd** — 容器中没有 systemd，用 nohup + bash

## 启动方式

```bash
chmod +x /root/.openclaw/gateway-watchdog.sh
nohup /root/.openclaw/gateway-watchdog.sh >> /var/log/gateway-watchdog.log 2>&1 &
```

## 健康检查

```bash
# Gateway 存活检查
curl -s http://127.0.0.1:18789/health
# 返回: {"ok":true,"status":"live"}

# Watchdog 状态
ps aux | grep gateway-watchdog
tail -f /var/log/gateway-watchdog.log
```

## 自动启动

添加到 `~/.bashrc`:

```bash
if ! pgrep -f "gateway-watchdog.sh" >/dev/null 2>&1; then
    nohup /root/.openclaw/gateway-watchdog.sh >> /var/log/gateway-watchdog.log 2>&1 &
fi
```
