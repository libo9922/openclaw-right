# CogVideoX-5B 文生视频

本目录包含 CogVideoX-5B 模型的下载、配置和推理脚本。

## 环境要求

- Python 3.10+
- PyTorch 2.x（CUDA 或 ROCm）
- AMD ROCm (gfx1100) 或 NVIDIA GPU (16GB+ VRAM)
- `diffusers >= 0.30.0`
- 磁盘空间: ~20GB（模型）+ 临时空间

## 快速开始

### 1. 下载模型

```bash
# 设置镜像（国内推荐）
export HF_ENDPOINT=https://hf-mirror.com

# 下载 CogVideoX-5B diffusers 格式
huggingface-cli download THUDM/CogVideoX-5B \
  --local-dir /workspace/models/CogVideoX-5B \
  --resume-download
```

模型大小约 21GB，包含:
- transformer: 11.1GB (2 个分片)
- text_encoder: 9.5GB (2 个分片)
- VAE: 862MB

### 2. 运行推理

```bash
# 设置 ROCm 环境（AMD GPU 必需）
export AITER_JIT_DISABLE=1
export HIP_FORCE_DEV_KERNARG=1
export USE_ROCM_AITER_ROPE_BACKEND=0

# 运行
python3 cogvideo_generate.py \
  --prompt "A cute golden retriever puppy playing in a field of flowers, sunny day, cinematic quality" \
  --steps 30 \
  --guidance 6.0 \
  --num_frames 25 \
  --output /workspace/openclaw/output/my_video.mp4
```

首次运行会编译 fused_layer_norm 算子（约 1-2 秒），之后自动缓存。

### 3. 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--prompt` | (必填) | 英文提示词，描述要生成的场景 |
| `--negative_prompt` | blurry, low quality | 负面提示词 |
| `--steps` | 30 | 推理步数，越多质量越好但越慢 (20-50) |
| `--guidance` | 6.0 | CFG 引导尺度 (3.0-7.0) |
| `--num_frames` | 25 | 生成帧数，最大 49 |
| `--height` | 480 | 视频高度 |
| `--width` | 720 | 视频宽度 |
| `--fps` | 8 | 视频帧率 |
| `--seed` | 随机 | 随机种子，固定可复现 |
| `--cpu_offload` | 否 | 启用 CPU offload（节省 VRAM） |
| `--output` | 自动 | 输出视频路径 |

## 示例

```bash
# 基础示例 — 30 步，25 帧，约 4 分钟
python3 cogvideo_generate.py \
  --prompt "A cute golden retriever puppy playing in a field of flowers, sunny day, cinematic quality" \
  --steps 30 \
  --num_frames 25 \
  --output example.mp4

# 高质量 — 50 步，49 帧，约 10 分钟（需要更多 VRAM）
python3 cogvideo_generate.py \
  --prompt "Cinematic shot of a dragon flying over a medieval castle, epic lighting, 4K" \
  --steps 50 \
  --num_frames 49 \
  --guidance 7.0 \
  --cpu_offload

# 快速测试 — 20 步，17 帧，约 2 分钟
python3 cogvideo_generate.py \
  --prompt "A cat walking on a beach" \
  --steps 20 \
  --num_frames 17
```

## 输出示例

`example_output.mp4` 使用以下参数生成:

```bash
prompt: "A cute golden retriever puppy playing in a field of flowers, sunny day, cinematic quality"
steps: 30, guidance: 6.0, num_frames: 25, fps: 8
size: 720x480, GPU: AMD ROCm gfx1100
耗时: ~6 分钟
```

## ROCm 注意事项

如遇 `aiter` JIT 编译锁问题:
```bash
# 清理锁文件
rm -f /opt/venv/lib/python3.12/site-packages/aiter/jit/build/lock_module_aiter_enum

# 禁用 NUMA balancing
sudo sh -c 'echo 0 > /proc/sys/kernel/numa_balancing'

# 环境变量
export AITER_JIT_DISABLE=1
export HIP_FORCE_DEV_KERNARG=1
export USE_ROCM_AITER_ROPE_BACKEND=0
```

## 模型说明

CogVideoX-5B 是智谱 AI / 清华大学开源文生视频模型，使用 diffusers 格式，支持:
- 文本到视频生成
- 最大 49 帧 / 约 6 秒 @ 8fps
- 最高 720p 分辨率
- BF16 推理

## 已知限制

- 中文 prompt 支持有限，建议用英文
- 复杂场景 / 精确镜头控制不精准
- 对 prompt 的叙事细节还原度有限
- 帧数越多推理越慢（线性增长）