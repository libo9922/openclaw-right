# SKILL.md — 容器环境 ROCm GPU 配置 (main agent 经验)

## 概述
在 AMD ROCm 云容器中配置 GPU 加速环境的完整指南。

## 环境信息
| 项目 | 值 |
|------|------|
| OS | Ubuntu 24.04 (Noble) |
| GPU | AMD Radeon gfx1100 (Navi 31), 48GB VRAM |
| ROCm | 7.2.1 (ROCk module 6.14.14) |
| PyTorch | 2.9.1+rocm |
| Python | 3.12.3 |
| VRAM 总量 | 51.5GB |

## GPU 状态检查
```bash
# ROCm 状态
rocm-smi

# 详细信息
rocm-smi --showmeminfo vram
rocm-smi --showtemp
rocm-smi --showpower

# Python 检查
/opt/venv/bin/python -c "
import torch
print(f'CUDA: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB')
"
```

## 关键路径
| 路径 | 说明 |
|------|------|
| `/opt/venv/` | Python 虚拟环境 |
| `/opt/comfyui/` | ComfyUI 安装目录 |
| `/opt/comfyui/models/checkpoints/` | 模型文件 |
| `/opt/comfyui/output/` | 输出文件 |
| `/opt/comfyui/input/` | 输入文件 |
| `/dev/kfd` | GPU 设备 (必须) |
| `/dev/dri/` | DRI 设备 (card3, renderD130) |

## pip 加速
```bash
# 使用清华源
/opt/venv/bin/pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 模型下载加速
```bash
# HuggingFace 镜像
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download ...

# ModelScope (需要令牌)
export MODELSCOPE_API_TOKEN=ms-xxxx
/opt/venv/bin/python -c "
from modelscope import snapshot_download
snapshot_download('model_id', local_dir='/tmp/model', token='ms-xxxx')
"
```

## 踩坑记录
1. **Docker 不可用**: 容器缺少 `CAP_SYS_ADMIN` 和 `CAP_NET_ADMIN`，无法运行 Docker
2. **apt 源问题**: ROCm 源 `repo.radeon.com` 无法访问，需禁用后用 Ubuntu 默认源
3. **Python 包路径**: 系统 pip 受 PEP 668 限制，必须用 `/opt/venv/bin/pip`
4. **exec session 生命周期**: 后台进程会在 session 结束时被清理，需用 nohup 或 watchdog
5. **PyTorch 版本**: ROCm 版 PyTorch 通过 `/app/pytorch/` 安装，版本号带 `+git` 后缀
6. **VRAM 释放**: `pkill -f vllm` 后 VRAM 会释放，`rocm-smi --showmeminfo vram` 确认
