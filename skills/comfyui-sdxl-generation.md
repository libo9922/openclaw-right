# SKILL.md — ComfyUI SDXL 出图 (cc-agent 经验)

## 概述
在 AMD ROCm GPU 上使用 ComfyUI + SDXL 模型生成图片的完整流程。

## 环境要求
- AMD GPU (RDNA3 架构, gfx1100)
- ROCm 7.2+ 
- PyTorch 2.9+ (rocm 版)
- ComfyUI 最新版
- SDXL checkpoint (约 6.5GB)

## 快速启动 ComfyUI
```bash
cd /opt/comfyui && /opt/venv/bin/python main.py --listen 0.0.0.0 --port 8188 &
sleep 10
```

## API 调用出图
```python
import json, urllib.request, time

workflow = {
    '3': {'class_type': 'KSampler', 'inputs': {
        'seed': 42, 'steps': 20, 'cfg': 7.0,
        'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0,
        'model': ['4', 0], 'positive': ['6', 0],
        'negative': ['7', 0], 'latent_image': ['5', 0]}},
    '4': {'class_type': 'CheckpointLoaderSimple',
          'inputs': {'ckpt_name': 'sd_xl_base_1.0.safetensors'}},
    '5': {'class_type': 'EmptyLatentImage',
          'inputs': {'width': 1024, 'height': 1024, 'batch_size': 1}},
    '6': {'class_type': 'CLIPTextEncode',
          'inputs': {'text': 'your prompt here', 'clip': ['4', 1]}},
    '7': {'class_type': 'CLIPTextEncode',
          'inputs': {'text': 'blurry, bad quality', 'clip': ['4', 1]}},
    '8': {'class_type': 'VAEDecode',
          'inputs': {'samples': ['3', 0], 'vae': ['4', 2]}},
    '9': {'class_type': 'SaveImage',
          'inputs': {'filename_prefix': 'output', 'images': ['8', 0]}}
}

data = json.dumps({'prompt': workflow}).encode()
req = urllib.request.Request('http://127.0.0.1:8188/prompt',
    data=data, headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
pid = resp['prompt_id']

# 轮询等待完成
for i in range(150):
    time.sleep(2)
    req2 = urllib.request.Request(f'http://127.0.0.1:8188/history/{pid}')
    result = json.loads(urllib.request.urlopen(req2, timeout=5).read())
    if pid in result:
        outputs = result[pid].get('outputs', {})
        if '9' in outputs:
            imgs = outputs['9'].get('images', [])
            print(f'完成: /opt/comfyui/output/{imgs[0]["filename"]}')
            break
```

## 性能指标
| 指标 | 数值 |
|------|------|
| 出图速度 | ~14 秒/张 (1024×1024, 20步) |
| 推理速度 | 3.7 it/s |
| VRAM 占用 | ~8GB |
| GPU | AMD Radeon gfx1100, 48GB |

## 踩坑记录
1. **Checkpoint 格式问题**: 合并 diffusers 格式的 safetensors 后 ComfyUI 无法识别，需要原始的 `conditioner.embedders.*` 格式
2. **网络下载慢**: 用清华源 `pypi.tuna.tsinghua.edu.cn` 加速 pip，用 `hf-mirror.com` 下载 HuggingFace 模型
3. **ComfyUI 被杀**: 容器环境中 background 进程会被清理，需用 watchdog 脚本守护
4. **Docker 不可用**: 容器缺少 `CAP_SYS_ADMIN`，无法运行 Docker-in-Docker

## 模型下载
```bash
# 从 HuggingFace 镜像下载 SDXL
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download \
  stabilityai/stable-diffusion-xl-base-1.0 \
  sd_xl_base_1.0.safetensors \
  --local-dir /opt/comfyui/models/checkpoints
```
