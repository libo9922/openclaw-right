# OpenClaw 实战经验库

> 基于真实生产环境的 OpenClaw 多 Agent 技能库，覆盖 GPU 加速、AI 出图/视频、元宝 Bot 管理、Gateway 守护、编程工具调试等场景。

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                   │
│              (端口 18789, WebSocket)                   │
├──────────┬──────────┬──────────┬──────────┬──────────┤
│  main    │ cc-agent │emma-agent│ monitor  │ good_job │
│  主Agent │ PPT制作  │ 视频制作  │ 健康监控  │ 编程调试  │
│  webchat │ 元宝cc   │ 元宝emma  │  cron    │  元宝/CLI │
└──────────┴────┬─────┴────┬─────┴──────────┴──────────┘
                │          │
           ┌────▼────┐ ┌───▼────┐
           │ComfyUI  │ │  SVD   │
           │ SDXL出图 │ │图生视频 │
           │ 端口8188 │ │        │
           └─────────┘ └────────┘
                │
           ┌────▼────────────┐
           │  AMD ROCm GPU   │
           │  gfx1100, 48GB  │
           └─────────────────┘
```

## 📁 技能列表

### 🎨 内容生成
| 技能 | Agent | 说明 |
|------|-------|------|
| [ppt-generation-guide.md](skills/ppt-generation-guide.md) | cc-agent | **PPT 制作完全指南** — 配色方案、布局模板、python-pptx 踩坑 |
| [video-generation-guide.md](skills/video-generation-guide.md) | emma-agent | **AI 视频制作完全指南** — 三种方案对比：帧切换/SVD/完整流水线 |
| [comfyui-sdxl-generation.md](skills/comfyui-sdxl-generation.md) | cc-agent | ComfyUI + SDXL 出图 API 调用 |

### 🔧 基础设施
| 技能 | Agent | 说明 |
|------|-------|------|
| [gateway-watchdog.md](skills/gateway-watchdog.md) | monitor | Gateway 健康监控与自动恢复脚本 |
| [rocm-gpu-setup.md](skills/rocm-gpu-setup.md) | main | AMD ROCm GPU 环境配置（pip加速、模型下载） |
| [yuanbao-bot-management.md](skills/yuanbao-bot-management.md) | main | 元宝 Bot 多账号配置与管理 |

### 💻 编程工具
| 技能 | Agent | 说明 |
|------|-------|------|
| [coding-tools-debug.md](skills/coding-tools-debug.md) | good_job | **Claude Code & Codex CLI 调试** — DNS、配置、代理问题排查 |

### 🏛️ 架构设计
| 技能 | Agent | 说明 |
|------|-------|------|
| [multi-agent-architecture.md](skills/multi-agent-architecture.md) | main | 多 Agent 架构设计与配置经验 |

---

## 🚀 快速开始

### 环境要求
- AMD GPU (RDNA3, 48GB+ VRAM)
- ROCm 7.2+
- Python 3.12 + PyTorch 2.9+rocm
- OpenClaw 2026.6.1+

### 安装 ComfyUI
```bash
# 克隆 ComfyUI
git clone https://gitee.com/mirrors/comfyui.git /opt/comfyui
cd /opt/comfyui
/opt/venv/bin/pip install -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载 SDXL 模型
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download \
  stabilityai/stable-diffusion-xl-base-1.0 \
  sd_xl_base_1.0.safetensors \
  --local-dir /opt/comfyui/models/checkpoints
```

### 启动 Gateway + Watchdog
```bash
# 启动 Gateway
openclaw gateway &

# 启动 Watchdog 守护
chmod +x /root/.openclaw/gateway-watchdog.sh
nohup /root/.openclaw/gateway-watchdog.sh &
```

---

## 🔧 踩坑总结

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Gateway 反复崩溃 | exec session 清理连带杀进程 | Watchdog 脚本自动重启 |
| Docker 无法运行 | 容器缺少 CAP_SYS_ADMIN | 直接裸装，不用 Docker |
| ComfyUI checkpoint 报错 | diffusers 格式不兼容 | 用原始 safetensors 格式 |
| 模型下载超时 | 国外源网络受限 | 清华源 + hf-mirror + ModelScope |
| SVD 模型 403 | HuggingFace 门控模型 | 用 ModelScope + token |
| 元宝 Bot 断连 | WebSocket 依赖 gateway | Watchdog 保活 + 自动重连 |
| pip install 报 PEP 668 | 系统 Python 保护 | 用 /opt/venv/bin/pip |
| Claude/Codex DNS 失败 | 容器 IPv6 优先但不通 | /etc/hosts 写死 IP |

---

## 📊 性能基准

| 模型 | 任务 | 耗时 | VRAM |
|------|------|------|------|
| SDXL 1.0 | 1024×1024 出图 | 14 秒 | ~8GB |
| SVD XT 1.1 | 25帧视频生成 | 120 秒 | ~12GB |
| Qwen3.6-35B | 文本推理 | ~40 tok/s | ~42GB |
| python-pptx | 18页 PPT | <1 秒 | 极低 |

---

## 📝 维护者

- **Amma** (main agent) — 架构设计、GPU 环境、元宝管理、README
- **cc** — PPT 制作、ComfyUI 出图
- **Emma** — 视频制作、SVD 生成、完整流水线
- **monitor** — Gateway 监控守护
- **good_job** — Claude/Codex 编程工具调试

---

## 📄 License

MIT
