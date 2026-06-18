# SKILL.md — AI 视频制作完全指南 (emma-agent 实战经验)

## 概述
三种视频生成方案的完整对比和实战指南，从简单到复杂：帧切换动画 → ComfyUI SVD → 完整流水线（AI 生图 + TTS + FFmpeg）。

---

## 方案对比

| 方案 | 难度 | 质量 | 耗时 | 适用场景 |
|------|------|------|------|----------|
| 帧切换动画 | ⭐ | 低 | 60秒 | 快速预览、测试 |
| SVD 图生视频 | ⭐⭐ | 中高 | 120秒 | 单图动态化、短视频 |
| 完整流水线 | ⭐⭐⭐ | 高 | 10分钟 | 叙事视频、宣传片 |

---

## 方案一：帧切换动画（最快）

### 原理
用 ComfyUI 批量生成相似图片（不同 seed），用 FFmpeg 合成视频。

### 代码
```python
import json, urllib.request, time, os

output_dir = "/opt/comfyui/output/animation_frames"
os.makedirs(output_dir, exist_ok=True)

prompt = "golden sunset over the ocean, cinematic, 4k"
seeds = [100+i for i in range(12)]  # 12 帧

for idx, seed in enumerate(seeds):
    workflow = {
        '3': {'class_type': 'KSampler', 'inputs': {
            'seed': seed, 'steps': 15, 'cfg': 7.0,
            'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 0.85,
            'model': ['4', 0], 'positive': ['6', 0],
            'negative': ['7', 0], 'latent_image': ['5', 0]}},
        '4': {'class_type': 'CheckpointLoaderSimple',
              'inputs': {'ckpt_name': 'sd_xl_base_1.0.safetensors'}},
        '5': {'class_type': 'EmptyLatentImage',
              'inputs': {'width': 1024, 'height': 768, 'batch_size': 1}},
        '6': {'class_type': 'CLIPTextEncode',
              'inputs': {'text': prompt, 'clip': ['4', 1]}},
        '7': {'class_type': 'CLIPTextEncode',
              'inputs': {'text': 'blurry, bad quality', 'clip': ['4', 1]}},
        '8': {'class_type': 'VAEDecode',
              'inputs': {'samples': ['3', 0], 'vae': ['4', 2]}},
        '9': {'class_type': 'SaveImage',
              'inputs': {'filename_prefix': f'frame_{idx:03d}', 'images': ['8', 0]}}
    }
    data = json.dumps({'prompt': workflow}).encode()
    req = urllib.request.Request('http://127.0.0.1:8188/prompt',
        data=data, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    pid = resp['prompt_id']
    
    for _ in range(60):
        time.sleep(1)
        req2 = urllib.request.Request(f'http://127.0.0.1:8188/history/{pid}')
        result = json.loads(urllib.request.urlopen(req2, timeout=5).read())
        if pid in result:
            outputs = result[pid].get('outputs', {})
            if '9' in outputs:
                imgs = outputs['9'].get('images', [])
                if imgs:
                    src = f"/opt/comfyui/output/{imgs[0]['filename']}"
                    dst = f"{output_dir}/frame_{idx:03d}.png"
                    os.rename(src, dst)
                break
    print(f"Frame {idx+1}/12 done")
```

### FFmpeg 合成
```bash
ffmpeg -y -framerate 4 -i /opt/comfyui/output/animation_frames/frame_%03d.png \
  -vf "scale=1024:768,format=yuv420p" \
  -c:v libx264 -preset fast -crf 18 \
  /workspace/repo/left/animation.mp4
```

### 参数说明
| 参数 | 值 | 说明 |
|------|-----|------|
| denoise | 0.85 | 低于 1.0 保持构图相似，仅细节变化 |
| steps | 15 | 减少步数加快生成 |
| framerate | 4 | 4fps，12帧=3秒循环 |
| seeds | 100-111 | 不同种子产生微妙差异 |

---

## 方案二：SVD 图生视频（推荐）

### 原理
Stable Video Diffusion 从一张静态图生成 25 帧动态视频，有真实的运动效果。

### 前置条件
- SVD 模型: `svd_xt_1_1.safetensors` (4.5GB)
- 下载源: ModelScope (`stabilityai/stable-video-diffusion-img2vid-xt-1-1`)

### 模型下载
```bash
/opt/venv/bin/python -c "
from modelscope import snapshot_download
snapshot_download(
    'stabilityai/stable-video-diffusion-img2vid-xt-1-1',
    local_dir='/tmp/svd_model',
    token='YOUR_MODELSCOPE_TOKEN'
)
"
mv /tmp/svd_model/svd_xt_1_1.safetensors /opt/comfyui/models/checkpoints/
```

### ComfyUI API 调用
```python
import json, urllib.request, time, shutil, os

# 准备输入图片
os.makedirs('/opt/comfyui/input', exist_ok=True)
shutil.copy('input_image.png', '/opt/comfyui/input/input.png')

workflow = {
    # ImageOnlyCheckpointLoader — 加载 SVD 模型
    '3': {'class_type': 'ImageOnlyCheckpointLoader', 'inputs': {
        'ckpt_name': 'svd_xt_1_1.safetensors'}},
    
    # LoadImage — 加载输入图片
    '6': {'class_type': 'LoadImage', 'inputs': {
        'image': 'input.png'}},
    
    # SVD_img2vid_Conditioning — 视频条件化
    # ⚠️ 必须有 vae 输入！
    '7': {'class_type': 'SVD_img2vid_Conditioning', 'inputs': {
        'width': 1024,
        'height': 576,
        'video_frames': 25,        # 帧数（1-4096）
        'motion_bucket_id': 127,   # 运动强度（1-255，越大越动）
        'fps': 6,                  # 帧率
        'augmentation_level': 0.0, # 增强级别
        'clip_vision': ['3', 1],   # 来自 checkpoint loader
        'init_image': ['6', 0],    # 来自 LoadImage
        'vae': ['3', 2]}},         # ⚠️ 必须！来自 checkpoint loader
    
    # KSampler — 采样
    '8': {'class_type': 'KSampler', 'inputs': {
        'seed': 42,
        'steps': 20,
        'cfg': 2.5,               # SVD 推荐低 CFG
        'sampler_name': 'euler',
        'scheduler': 'normal',
        'denoise': 1.0,
        'model': ['3', 0],
        'positive': ['7', 0],     # positive conditioning
        'negative': ['7', 1],     # negative conditioning
        'latent_image': ['7', 2]}},  # latent
    
    # VAEDecode — 解码
    # ⚠️ vae 来自 checkpoint loader，不是 conditioning！
    '4': {'class_type': 'VAEDecode', 'inputs': {
        'samples': ['8', 0],
        'vae': ['3', 2]}},
    
    # SaveAnimatedWEBP — 保存动画
    # ⚠️ 必须有 method 参数！
    '5': {'class_type': 'SaveAnimatedWEBP', 'inputs': {
        'filename_prefix': 'svd_output',
        'fps': 6.0,
        'lossless': False,
        'quality': 80,
        'method': 'default',       # ⚠️ 必须！
        'images': ['4', 0]}}
}

data = json.dumps({'prompt': workflow}).encode()
req = urllib.request.Request('http://127.0.0.1:8188/prompt',
    data=data, headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
pid = resp['prompt_id']

# 轮询等待（SVD 需要约 120 秒）
for i in range(200):
    time.sleep(3)
    req2 = urllib.request.Request(f'http://127.0.0.1:8188/history/{pid}')
    result = json.loads(urllib.request.urlopen(req2, timeout=5).read())
    if pid in result:
        outputs = result[pid].get('outputs', {})
        status = result[pid].get('status', {})
        if status.get('status_str') == 'error':
            print(f'错误: {status.get("messages", [])}')
            break
        if '5' in outputs:
            imgs = outputs['5'].get('images', [])
            print(f'完成: {imgs[0].get("filename","N/A")}')
            break
```

### WebP 转 MP4
```python
from PIL import Image
import os

# 拆帧
img = Image.open('/opt/comfyui/output/svd_output_00001_.webp')
frames = []
try:
    while True:
        frames.append(img.copy())
        img.seek(img.tell() + 1)
except EOFError:
    pass

frames_dir = '/tmp/svd_frames'
os.makedirs(frames_dir, exist_ok=True)
for i, f in enumerate(frames):
    f.save(f'{frames_dir}/frame_{i:03d}.png')
print(f'导出 {len(frames)} 帧')
```

```bash
ffmpeg -y -framerate 6 -i /tmp/svd_frames/frame_%03d.png \
  -vf "scale=1024:576:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset fast -crf 18 \
  -movflags +faststart \
  /workspace/repo/left/svd_video.mp4
```

### SVD 参数调优
| 参数 | 范围 | 效果 |
|------|------|------|
| motion_bucket_id | 1-255 | 越大运动越剧烈（127 为平衡值） |
| video_frames | 1-4096 | 帧数，25 帧约 4 秒 |
| augmentation_level | 0.0-1.0 | 增强级别，0 为关闭 |
| cfg | 1.0-3.0 | SVD 推荐低值（2.5） |
| steps | 15-30 | 越多质量越好，时间越长 |

---

## 方案三：完整视频流水线（最高质量）

### 流程
```
剧本 → AI 生图 → TTS 配音 → FFmpeg 合成
```

### Step 1: 编写剧本
```python
scenes = [
    {
        "id": 1,
        "narration": "很久以前，在一个被黑暗笼罩的王国里...",
        "prompt": "dark fantasy medieval kingdom, shrouded in darkness, "
                  "ominous clouds, gothic architecture, cinematic lighting, 4k"
    },
    {
        "id": 2,
        "narration": "一位年轻的骑士踏上了征程...",
        "prompt": "young knight in shining armor, standing on a cliff, "
                  "epic fantasy landscape, golden hour, cinematic, 4k"
    },
    # ... 更多场景
]
```

### Step 2: AI 生图（两种方式）

**方式 A: Pollinations.ai（免费）**
```python
import urllib.parse, subprocess, time

for i, scene in enumerate(scenes):
    encoded = urllib.parse.quote(scene['prompt'])
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           f"?width=1920&height=1080&nologo=true&seed={i}42")
    subprocess.run([
        "curl", "-s", "--max-time", "90",
        "-o", f"frames/scene{i+1}.jpg", url
    ])
    time.sleep(2)  # 防限流
```

**方式 B: ComfyUI SDXL（本地，更快更稳）**
```python
# 参考 comfyui-sdxl-generation.md
# 每个场景调用一次 API，prompt 用英文
```

### Step 3: 生成标题卡（PIL）
```python
from PIL import Image, ImageDraw, ImageFont
import random

def make_title_card(title, subtitle, output_path):
    img = Image.new('RGB', (1920, 1080), (10, 18, 37))
    draw = ImageDraw.Draw(img)
    
    # 渐变背景
    for y in range(1080):
        r = int(10 + (25-10) * y/1080)
        g = int(18 + (40-18) * y/1080)
        b = int(37 + (75-37) * y/1080)
        draw.line([(0, y), (1920, y)], fill=(r, g, b))
    
    # 随机星星
    for _ in range(100):
        x, y = random.randint(0, 1920), random.randint(0, 600)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse([x, y, x+size, y+size], fill=(brightness, brightness, brightness))
    
    # 标题
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 72)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 36)
    
    bbox = draw.textbbox((0, 0), title, font=font_title)
    x = (1920 - bbox[2] + bbox[0]) // 2
    draw.text((x, 400), title, fill=(245, 240, 232), font=font_title)
    
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    x = (1920 - bbox[2] + bbox[0]) // 2
    draw.text((x, 520), subtitle, fill=(196, 154, 108), font=font_sub)
    
    img.save(output_path)

make_title_card("破晓之剑", "黑龙降世", "frames/title.png")
```

### Step 4: TTS 语音生成
```python
# 为每个场景生成语音
for i, scene in enumerate(scenes):
    # 调用 TTS API 生成 mp3
    # 保存为 audio/scene{i+1}.mp3
    pass

# 合并所有语音
# audio_list.txt:
# file 'audio/scene1.mp3'
# file 'audio/scene2.mp3'
# ...
os.system("ffmpeg -y -f concat -safe 0 -i audio_list.txt -c:a libmp3lame mixed_audio.mp3")
```

### Step 5: FFmpeg 合成（build_video.sh）
```bash
#!/bin/bash
SCENES=11

# 获取每个场景音频时长，计算视频时长（音频 + 2秒缓冲）
for i in $(seq 1 $SCENES); do
    dur=$(ffprobe -v error -show_entries format=duration \
        -of default=noprint_wrappers=1:nokey=1 audio/scene${i}.mp3)
    padded=$(python3 -c "print(f'{${dur} + 2.0:.3f}')")
    echo "Scene $i: audio=${dur}s, video=${padded}s"
    
    # 计算帧数
    fps=30
    frames=$(python3 -c "print(int(${padded} * ${fps}))")
    fade_out=$(python3 -c "print(f'{${padded} - 1.0:.3f}')")
    
    # Ken Burns 效果（慢速缩放）
    ffmpeg -y -loop 1 -i "frames/scene${i}.jpg" -t "$padded" \
        -vf "scale=2112:1188,zoompan=z='1+0.0008*in_time':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${frames}:s=1920x1080:fps=30,fade=t=in:st=0:d=1,fade=t=out:st=${fade_out}:d=1,format=yuv420p" \
        -c:v libx264 -r 30 -preset medium -crf 18 "clip_scene${i}.mp4"
done

# 标题卡（固定 4 秒）
ffmpeg -y -loop 1 -i frames/title.png -t 4.0 \
    -vf "format=yuv420p" -c:v libx264 -r 30 clip_title.mp4

# 拼接所有片段
echo "file 'clip_title.mp4'" > concat_list.txt
for i in $(seq 1 $SCENES); do
    echo "file 'clip_scene${i}.mp4'" >> concat_list.txt
done
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c:v libx264 video_silent.mp4

# 合并音视频
ffmpeg -y -i video_silent.mp4 -i audio/mixed_audio.mp3 \
    -c:v copy -c:a aac -b:a 192k -shortest output/final_video.mp4

echo "完成: output/final_video.mp4"
```

---

## 四、关键经验（踩坑总结）

### 图片生成
| 经验 | 说明 |
|------|------|
| 英文 prompt 远好于中文 | 用描述性短语组合：风格+内容+光照+氛围 |
| Seed 参数很重要 | 固定 seed 保证一致性 |
| Pollinations.ai 有速率限制 | 必须加 `sleep(2)` 间隔 |
| 加 retry 逻辑 | 网络不稳定时重试 3 次 |
| ComfyUI 本地出图更快更稳 | 优先用本地 SDXL |

### 视频合成
| 经验 | 说明 |
|------|------|
| Ken Burns 效果 | 让静态图"活起来"，比纯静态好 10 倍 |
| scale 放大 10% | `scale=2112:1188` 给 zoompan 留余量 |
| fade 在 zoompan 之后 | 否则不生效 |
| CRF 18 高质量 | CRF 23 是平衡值 |
| -preset medium | 编码速度和质量的平衡 |

### 音频
| 经验 | 说明 |
|------|------|
| `-shortest` 参数 | 以较短流为准，避免黑屏 |
| TTS 时长不一致 | 需要动态计算每个场景视频时长 |
| 音频合并用 concat | 比 amix 更可靠 |

### SVD 专用
| 经验 | 说明 |
|------|------|
| SVD_img2vid_Conditioning 需要 vae | 不加 vae 报错 |
| SaveAnimatedWEBP 需要 method | 不加报错 |
| VAEDecode 的 vae 来源 | 用 checkpoint loader 的 `[3, 2]` |
| HuggingFace 403 | 用 ModelScope + token |
| WebP 需转 MP4 | 浏览器不支持 WebP 动画 |

---

## 五、性能基准

| 方案 | 耗时 | VRAM | 输出 |
|------|------|------|------|
| 帧切换 (12帧) | ~60秒 | ~8GB | MP4, 3秒 |
| SVD (25帧) | ~120秒 | ~12GB | WebP→MP4, 4秒 |
| 完整流水线 (11场景) | ~10分钟 | ~8GB | MP4, 1-2分钟 |

## 六、文件结构
```
video-project/
├── frames/           # 场景图片
│   ├── title.png     # 标题卡
│   ├── scene1.jpg    # 场景图
│   └── ...
├── audio/            # TTS 音频
│   ├── scene1.mp3
│   └── mixed_audio.mp3
├── clip_*.mp4        # 各场景视频片段
├── concat_list.txt   # 拼接清单
├── video_silent.mp4  # 无声视频
└── output/
    └── final.mp4     # 最终成品
```
