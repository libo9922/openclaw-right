# AI 视频制作流水线 — 能力迁移指南

> 本文档记录了 faker-agent 工作区中完成的完整 AI 视频制作流程，供其他会话快速学习和复用。

---

## 📋 概览

工作区完成了 **3 个迭代版本**的视频制作项目，从简单到复杂逐步演进：

| 项目 | 主题 | 图片来源 | 音频 | 最终产出 |
|------|------|---------|------|---------|
| `video-project/` | 星尘之梦（童话） | PIL 程序化绘制 | 无 | 无声视频 |
| `video-project2/` | 暗黑奇幻冒险 | PIL 程序化绘制 | 无 | 带淡入淡出的无声视频 |
| `video-project3/` | 破晓之剑（黑龙降世） | **Pollinations.ai AI 生图** | **TTS 语音** | **完整有声视频** ✅ |

最终产出：`video-project3/output/dawn_sword_ai.mp4`（约 20MB，含 11 个场景 + 标题卡 + 配音）

---

## 🔧 核心工具清单

### 1. Python + Pillow (PIL)
- **用途**：程序化生成标题卡、简单场景帧
- **关键函数**：`Image.new()`, `ImageDraw`, `ImageFont.truetype()`
- **中文字体**：`/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`（文泉驿正黑）

### 2. Pollinations.ai（免费 AI 图片生成）
- **用途**：根据英文 prompt 生成 1920×1080 高质量场景图
- **API 格式**：
  ```
  https://image.pollinations.ai/prompt/{URL编码的英文prompt}?width=1920&height=1080&nologo=true&seed={种子}
  ```
- **调用方式**：`curl -s -o output.jpg "URL"` 或 Python `subprocess.run(["curl", ...])`
- **注意**：免费服务，需加 `time.sleep(2)` 间隔避免限流；建议加重试逻辑（3 次）

### 3. FFmpeg（视频合成核心）
- **图片转视频**：`ffmpeg -loop 1 -i image.png -t 4 -vf "format=yuv420p" -c:v libx264 -r 30 out.mp4`
- **Ken Burns 效果**（慢速缩放平移）：
  ```
  zoompan=z='1+0.0008*in_time':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={帧数}:s=1920x1080:fps=30
  ```
- **淡入淡出**：`fade=t=in:st=0:d=1,fade=t=out:st={结束前1秒}:d=1`
- **拼接**：先生成 `concat_list.txt`，再 `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4`
- **音视频合并**：`ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest final.mp4`

### 4. FFprobe（获取时长）
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 file.mp3
```

### 5. TTS 语音生成
- 使用 TTS 工具为每个场景的旁白生成 `.mp3` 文件
- 文件命名：`audio/scene1.mp3`, `audio/scene2.mp3`, ...
- 最后用 ffmpeg 的 `amix` 或 concat 将所有语音合并为 `mixed_audio.mp3`

---

## 📐 完整流水线步骤（以 video-project3 为例）

### Step 1: 编写剧本
```python
# 定义场景列表，每个场景包含旁白文本和画面描述
scenes = [
    {"id": 1, "narration": "很久以前...", "prompt": "dark fantasy dragon..."},
    ...
]
```

### Step 2: 生成场景图片
```python
# download_v2.py — 逐张调用 Pollinations.ai
import urllib.parse, subprocess, time

for i, prompt in enumerate(prompts):
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed={i}42"
    subprocess.run(["curl", "-s", "--max-time", "90", "-o", f"frames/scene{i+1}.jpg", url])
    time.sleep(2)  # 防限流
```
- 输出：`frames/scene1.jpg` ~ `scene11.jpg`（每个 50-90KB）

### Step 3: 生成标题卡（PIL）
```python
from PIL import Image, ImageDraw, ImageFont
# 深色渐变背景 + 随机星星 + 居中标题文字
img = Image.new('RGB', (1920, 1080))
draw = ImageDraw.Draw(img)
# ... 渐变、星星、文字绘制
img.save('frames/title.png')
```

### Step 4: 生成 TTS 语音
- 为每个场景旁白调用 TTS，保存为 `audio/scene{N}.mp3`
- 用 ffmpeg concat 合并所有语音：`ffmpeg -f concat -safe 0 -i audio_list.txt -c:a libmp3lame mixed_audio.mp3`

### Step 5: 构建视频（build_video.sh）
```bash
#!/bin/bash
# 5a. 获取每个场景音频时长，计算视频片段时长（音频时长 + 2秒缓冲）
for i in $(seq 1 11); do
    dur=$(ffprobe -v error -show_entries format=duration ... audio/scene${i}.mp3)
    padded=$(python3 -c "print(f'{${dur} + 2.0:.3f}')")
done

# 5b. 标题卡 → 固定4秒视频
ffmpeg -y -loop 1 -i frames/title.png -t 4.0 -vf "format=yuv420p" -c:v libx264 -r 30 clip_title.mp4

# 5c. 每个场景图 → Ken Burns 效果视频片段
for i in $(seq 1 11); do
    ffmpeg -y -loop 1 -i "frames/scene${i}.jpg" -t "$dur" \
        -vf "scale=2112:1188,zoompan=z='1+0.0008*in_time':...:d=${frames}:s=1920x1080:fps=30,
             fade=t=in:st=0:d=1,fade=t=out:st=${fade_out}:d=1,format=yuv420p" \
        -c:v libx264 -r 30 -preset medium -crf 18 "clip_scene${i}.mp4"
done

# 5d. 拼接所有片段
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c:v libx264 video_silent.mp4

# 5e. 合并音视频
ffmpeg -y -i video_silent.mp4 -i audio/mixed_audio.mp3 \
    -c:v copy -c:a aac -b:a 192k -shortest output/dawn_sword_ai.mp4
```

---

## 🎯 关键经验 & 踩坑记录

### 图片生成
- **Pollinations.ai 免费但有速率限制**，必须加 `sleep(2)` 间隔
- **Seed 参数很重要**：固定 seed 可保证同一 prompt 生成一致的图片
- **英文 prompt 效果远好于中文**，用描述性短语组合（风格 + 内容 + 光照 + 氛围）
- **建议加 retry**：网络不稳定时需重试 3 次

### 视频合成
- **Ken Burns 效果**让静态图片"活起来"，比纯静态画面观感好很多
- **zoompan 参数**：`z='1+0.0008*in_time'` 表示缓慢放大，值越大放大越快
- **先放大再裁切**：`scale=2112:1188`（比 1920×1080 大 10%）给 zoompan 留余量
- **fade 必须在 zoompan 之后**，否则不生效
- **CRF 18** 是高质量，文件较大；CRF 23 是默认平衡值
- **-preset medium** 编码速度和质量的平衡点

### 音频
- **`-shortest` 参数**：以较短的流为准结束，避免视频比音频长时黑屏
- **TTS 生成的 mp3 时长不一致**，需要动态计算每个场景的视频时长

### 程序化绘图（PIL）
- **文泉驿字体**是 Linux 下最可靠的中文免费字体
- **渐变背景**：逐行绘制 `draw.line()`，计算插值颜色
- **光晕效果**：用 `Image.alpha_composite()` 叠加半透明圆形
- **星星**：随机位置和大小的 `draw.ellipse()`

---

## 🗂️ 文件结构参考

```
video-project3/
├── download_frames.py      # 图片下载脚本（无重试版）
├── download_v2.py          # 图片下载脚本（带重试+跳过已有）
├── build_video.sh          # 完整视频构建脚本
├── frames/                 # 场景图片（scene1-11.jpg + title.png）
├── audio/                  # TTS 音频（scene1-11.mp3 + mixed_audio.mp3）
├── clip_scene*.mp4         # 各场景视频片段
├── clip_title.mp4          # 标题卡视频片段
├── concat_list.txt         # ffmpeg concat 拼接清单
├── video_silent.mp4        # 无声完整视频
├── p1-p5.jpg               # 预览截图
└── output/
    └── dawn_sword_ai.mp4   # 最终成品
```

---

## 🚀 快速复用指南

想做一个新视频？按这个顺序来：

1. **写剧本**：定义场景列表（旁白 + 画面描述）
2. **生图**：用 `download_v2.py` 模板，改 prompts 列表，调用 Pollinations.ai
3. **生语音**：用 TTS 工具为每段旁白生成 mp3
4. **写 build 脚本**：参考 `build_video.sh`，改场景数量
5. **运行**：`bash build_video.sh`
6. **检查**：`ffprobe output/final.mp4` 确认时长和格式

**预计耗时**（11 场景）：
- 图片生成：~5 分钟（含等待）
- 语音生成：~2 分钟
- 视频合成：~3 分钟
- 总计：~10 分钟

---

## 📝 迭代历程

### v1（video-project/）
- 纯 PIL 绘制，画面较简单
- 无声，无转场
- 验证了基本流程可行性

### v2（video-project2/）
- PIL 绘制大幅升级（山脉、城堡、龙、人物等复杂图形）
- 加入了淡入淡出转场
- 画面精细但仍显"程序化"

### v3（video-project3/）✅ 最终版
- 切换到 Pollinations.ai AI 生图，画面质量飞跃
- 加入 TTS 语音旁白
- Ken Burns 效果让静态图有电影感
- 完整的标题卡 + 11 场景 + 音视频合并

**核心教训**：AI 生图 + Ken Burns + TTS = 低成本高质量叙事视频的最优方案。

---

*最后更新：2026-06-17 | 来源：faker-agent workspace*
