# 01 — 环境搭建

## 硬件环境

- **GPU**: AMD RDNA (51GB VRAM)
- **ROCm**: 7.2.1
- **PyTorch**: 2.9.1+rocm7.2.1

## 软件栈

| 包 | 版本 | 用途 |
|---|------|------|
| genesis-world | 1.1.2 | 物理仿真引擎 |
| lerobot | 0.4.4 | HuggingFace 机器人学习框架 |
| torchcodec | 0.10.0 | 视频编解码（CPU 编译） |
| transformers | 4.57.6 | SmolVLA 模型加载 |
| scikit-image | 0.22 | 图像处理 |

## 安装步骤

```bash
# 1. 用清华镜像加速 pip（网络慢时必须）
/opt/venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    "lerobot==0.4.4" genesis-world

# 2. torchcodec 需要从源码编译（ROCm 没有预编译包）
cd /workspace/repo && bash setup_torchcodec.sh

# 3. 系统依赖
apt-get install -y xvfb ffmpeg pkg-config \
    libavdevice-dev libavfilter-dev libavformat-dev \
    libavcodec-dev libavutil-dev libswresample-dev libswscale-dev
```

## 模型下载

HuggingFace 在国内网络不通，用 ModelScope 镜像：

```bash
pip install modelscope

# SmolVLA base 模型 (~864MB)
python -c "
from modelscope import snapshot_download
snapshot_download('lerobot/smolvla_base', cache_dir='/opt/workshop/models')
"

# SmolVLM2 背景模型 (~1.9GB)
python -c "
from modelscope import snapshot_download
snapshot_download('HuggingFaceTB/SmolVLM2-500M-Video-Instruct', cache_dir='/opt/workshop/models')
"
```

## 路径配置

```bash
# Notebook 期望模型在 /opt/workshop/models/smolvla_base
ln -sf /opt/workshop/models/lerobot/smolvla_base /opt/workshop/models/smolvla_base

# SmolVLM2 需要 patch lerobot 源码指向本地路径
python -c "
import site, re
from pathlib import Path
VLM_LOCAL = '/opt/workshop/models/HuggingFaceTB/SmolVLM2-500M-Video-Instruct'
site_pkg = site.getsitepackages()[0]
for pyfile in ['policies/smolvla/configuration_smolvla.py',
               'policies/smolvla/smolvlm_with_expert.py']:
    fpath = Path(site_pkg) / 'lerobot' / pyfile
    src = fpath.read_text()
    fixed = re.sub(r'[\"][^\"]*SmolVLM2-500M-Video-Instruct[\"]', f'\"{VLM_LOCAL}\"', src)
    fpath.write_text(fixed)
"
```
