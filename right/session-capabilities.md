# Amma Session Capabilities Guide

> 2026-06-17 会话实录，涵盖所有工具链、操作步骤、踩坑点。
> 目标：其它会话读完后可直接迁移复用。

---

## 1. MiMo TTS 语音合成

### 1.1 基础 TTS

**API 端点：** `https://token-plan-cn.xiaomimimo.com/v1/chat/completions`

**模型：** `mimo-v2.5-tts`

**可用声音：** `mimo_default`, `冰糖`, `茉莉`, `苏打`, `白桦`, `Mia`, `Chloe`, `Milo`, `Dean`

```python
import json, urllib.request, base64

# 读取 API key
with open('/root/.openclaw/agents/main/agent/auth-profiles.json') as f:
    data = json.load(f)
key = data["profiles"]["xiaomi-token-plan:default"]["key"]

payload = json.dumps({
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    "modalities": ["text", "audio"],
    "audio": {"voice": "茉莉", "format": "mp3"}
}).encode()

req = urllib.request.Request(
    "https://token-plan-cn.xiaomimimo.com/v1/chat/completions",
    data=payload,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read())
audio_bytes = base64.b64decode(result["choices"][0]["message"]["audio"]["data"])

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

**踩坑：**
- 声音参数不能随便填，会报错并返回可用声音列表
- `messages` 格式必须是 `user`（空）+ `assistant`（要合成的文本）

### 1.2 声音克隆 (VoiceClone)

**模型：** `mimo-v2.5-tts-voiceclone`

**关键：** `audio.voice` 必须是 **DataURL** 格式，不是字符串！

```python
# 读取参考音频并转为 DataURL
with open('reference.mp3', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

voice_data_url = f"data:audio/mp3;base64,{audio_b64}"

payload = json.dumps({
    "model": "mimo-v2.5-tts-voiceclone",
    "messages": [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    "modalities": ["text", "audio"],
    "audio": {
        "voice": voice_data_url,   # ← DataURL，不是 "clone"
        "format": "mp3"
    }
}).encode()
```

**踩坑：**
- 错误 `audio.voice must be a DataURL for voice clone model` → 说明 voice 传了字符串，要用 DataURL
- 参考音频越大越慢，建议 1-2MB 以内
- 参考音频质量直接影响克隆效果

---

## 2. Bilibili 音频下载

### 2.1 获取视频信息

```python
import requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com',
}

bvid = 'BV1xxxxxxx'
r = requests.get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}', headers=headers, timeout=15)
info = r.json()['data']
cid = info['pages'][0]['cid']
aid = info['aid']
```

### 2.2 获取音频流

```python
r2 = requests.get(
    f'https://api.bilibili.com/x/player/playurl?avid={aid}&cid={cid}&qn=64&fnval=16',
    headers=headers, timeout=15
)
audio_url = r2.json()['data']['dash']['audio'][0]['baseUrl']

# 下载
r3 = requests.get(audio_url, headers={**headers, 'Range': 'bytes=0-'}, timeout=120, stream=True)
with open('audio.m4a', 'wb') as f:
    for chunk in r3.iter_content(chunk_size=65536):
        f.write(chunk)
```

**踩坑：**
- Bilibili 搜索 API 需要 wbi 签名，直接调用容易 412
- `fnval=16` 返回 DASH 格式（含独立音频流）
- 必须带 `Referer: https://www.bilibili.com` 否则 403
- yt-dlp 也可以用，但 Bilibili 经常 412

---

## 3. 人声分离

### 3.1 FFmpeg 频段分离（轻量，无需额外依赖）

```bash
# 提取指定时间段
ffmpeg -y -i input.m4a -ss 00:05:34 -t 00:00:33 clip.wav

# 女声频率分离（带通滤波 + 降噪）
ffmpeg -y -i clip.wav \
  -af "pan=stereo|c0=c0-c1|c1=c1-c0,highpass=f=200,lowpass=f=8000,afftdn=nf=-20,volume=2.0" \
  female_isolated.wav
```

**效果：** 一般，频段分离不精确

### 3.2 Demucs（专业级，推荐）

**安装：**
```bash
/opt/venv/bin/pip install demucs soundfile
```

**GPU 运行（AMD ROCm）：**
```python
import torch, soundfile as sf, numpy as np
from demucs.pretrained import get_model
from demucs.apply import apply_model

model = get_model('htdemucs')
model.eval()
model.cuda()

data, sr = sf.read('input.wav')  # 用 soundfile 代替 torchaudio（避免 torchcodec 问题）
wav = torch.from_numpy(data.T).float()

if sr != model.samplerate:
    import torchaudio.functional as F
    wav = F.resample(wav, sr, model.samplerate)

wav = wav.unsqueeze(0).cuda()

with torch.no_grad():
    sources = apply_model(model, wav, device='cuda', progress=True)

vocals = sources[0, model.sources.index('vocals')].cpu().numpy()
sf.write('vocals.wav', vocals.T, model.samplerate)
```

**踩坑：**
- `torchaudio.load()` 会报 torchcodec 错误 → 改用 `soundfile.read()`
- `torch._C._CudaDeviceProperties.total_mem` → 应为 `total_memory`
- AMD GPU 需要 ROCm，PyTorch 通过 HIP 兼容 CUDA API
- 48GB VRAM 的 AMD GPU 跑 117 秒音频只要 **5 秒**
- CPU 要 **13 分钟**

---

## 4. OpenClaw 多账号 & 多 Agent 路由

### 4.1 元宝多账号配置

```json
{
  "channels": {
    "yuanbao": {
      "defaultAccount": "faker",
      "accounts": {
        "faker": { "appKey": "xxx", "appSecret": "xxx", "name": "faker" },
        "JDI":   { "appKey": "yyy", "appSecret": "yyy", "name": "JDI" }
      },
      "enabled": true,
      "requireMention": false
    }
  }
}
```

### 4.2 多 Agent 路由

```json
{
  "agents": {
    "list": [
      { "id": "main" },
      { "id": "faker-agent", "workspace": "/root/.openclaw/faker-agent" },
      { "id": "JDI-agent", "workspace": "/root/.openclaw/JDI-agent" }
    ]
  },
  "bindings": [
    { "agentId": "faker-agent", "match": { "channel": "yuanbao", "accountId": "faker" } },
    { "agentId": "JDI-agent", "match": { "channel": "yuanbao", "accountId": "JDI" } }
  ]
}
```

**要点：**
- `bindings` 中 `accountId` 匹配元宝账号
- `match.peer.id` 匹配特定用户
- 先匹配先生效，顺序重要
- config 修改后自动热重载

### 4.3 Session 隔离

- 每个 agent 有独立的 workspace、memory、SOUL
- 主 agent 看不到其它 agent 的 session（visibility=tree）
- `sessions_send` 跨 agent 发消息会被 forbidden

---

## 5. 文件服务

### 5.1 Canvas 嵌入（webchat 内嵌）

```json
{
  "plugins": {
    "entries": {
      "canvas": {
        "config": {
          "host": {
            "enabled": true,
            "root": "/path/to/files",
            "liveReload": true
          }
        }
      }
    }
  }
}
```

嵌入语法：`[embed url="/__openclaw__/canvas/file.html" title="xxx" height="300" /]`

### 5.2 简易 HTTP 服务器

```python
# serve.py
import http.server, socketserver, os, sys
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 18800
os.chdir(os.path.dirname(os.path.abspath(__file__)))
handler = http.server.SimpleHTTPRequestHandler
handler.extensions_map.update({'.mp3': 'audio/mpeg', '.mp4': 'video/mp4'})
with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
    httpd.serve_forever()
```

---

## 6. 环境信息

| 项目 | 值 |
|------|-----|
| GPU | AMD Radeon (Navi 31, 48GB VRAM) |
| ROCm | 7.2.1 |
| PyTorch | 2.9.1 (ROCm) |
| Python | 3.12 |
| FFmpeg | 已安装 |
| API | Xiaomi MiMo (token-plan-cn.xiaomimimo.com) |
| TTS 模型 | mimo-v2.5-tts, mimo-v2.5-tts-voiceclone |

---

## 7. 工作目录结构

```
/workspace/seedmotion/
├── 1/                          # 八奈见杏菜声音克隆
│   ├── amma_voice_cloned_v2.mp3
│   ├── amma_story.mp3
│   └── ...
├── 2/                          # 超市后门抽烟的她
│   ├── separated_vocals.mp3    # Demucs GPU 分离
│   ├── amma_voice_cloned_demucs.mp3
│   └── ...
```

---

## 8. 踩坑速查

| 问题 | 解决 |
|------|------|
| `nvidia-smi: not found` | 这是 AMD GPU，用 `rocm-smi` |
| `torchcodec` 报错 | 用 `soundfile` 代替 `torchaudio.load()` |
| `total_mem` 不存在 | 改为 `total_memory` |
| B站 API 412 | 带 Referer + User-Agent，用 `/x/web-interface/view` |
| `audio.voice must be a DataURL` | voice 参数传 `data:audio/mp3;base64,...` |
| demucs CPU 太慢 | 确认 `model.cuda()`，用 GPU 跑 |
| session send forbidden | visibility=tree 限制，无法跨 agent 发消息 |
| 元宝 bot 状态 SETUP | 需要启动 gateway（`openclaw gateway` 或 `nohup`） |
