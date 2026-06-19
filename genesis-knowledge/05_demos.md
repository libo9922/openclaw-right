# 05 — Demo 制作

## 已完成的 Demo

| Demo | 文件 | 内容 | 时长 |
|------|------|------|------|
| 🏗️ 多米诺骨牌 | `demo_domino.py` | 10 个彩色积木连锁倒塌 | 5 秒 |
| 🎯 球体碰撞 | `demo_collision.py` | 5 个球从不同高度落下 | 3 秒 |
| 🏢 积木金字塔 | `demo_tower.py` | 15 个积木堆成金字塔 | 2.5 秒 |
| 🤖 Franka 抓取 | `demo_franka_grasp.py` | 机械臂抓取彩色积木 | 20 秒 |
| 🕺 多角色 | `demo_multi_char.py` | 4 个角色绕圈旋转 | 15 秒 |
| 🔮 弹球雨 | `demo_ball_rain.py` | 35 个彩色球弹跳 | 15 秒 |

## 渲染视频模板

```python
import genesis as gs
import torch, numpy as np, subprocess
from pathlib import Path

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/30), show_viewer=False)
scene.add_entity(gs.morphs.Plane())

# 添加物体...

cam = scene.add_camera(pos=(2, 2, 1.5), lookat=(0, 0, 0.5), res=(1280, 720))
scene.build()

frames = []
for step in range(300):
    scene.step()
    frames.append(cam.render()[0])

# 写视频
out = str(Path("output.mp4"))
h, w = frames[0].shape[:2]
proc = subprocess.Popen(
    ["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24",
     "-s",f"{w}x{h}","-r","30","-i","pipe:0",
     "-c:v","libx264","-pix_fmt","yuv420p",
     "-preset","fast","-crf","23", out],
    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for f in frames:
    proc.stdin.write(f.tobytes())
proc.stdin.close()
proc.wait()
```

## 关键技巧

1. **摄像头必须在 build 前添加**
2. **`cam.render()` 返回 tuple**，用 `[0]` 取 RGB
3. **每帧渲染很慢**，用 `step % N == 0` 降采样
4. **分辨率影响速度**，1280x720 比 640x480 慢 4 倍
5. **场景实体越多越慢**，64 个地砖会让 build 超慢

## 多视角合并

```bash
ffmpeg -y \
    -i wide.mp4 -i front.mp4 -i top.mp4 \
    -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[2:v]scale=640:360[c];[a][b][c]hstack=inputs=3[v]" \
    -map "[v]" merged.mp4
```

## 已知限制

- ❌ 不能做动漫角色跳舞（没有骨骼动画系统）
- ❌ 不能做精细流体/布料仿真（效果差）
- ❌ 复杂机器人模型穿模（碰撞检测 bug）
- ✅ 机械臂场景效果好
- ✅ 刚体碰撞/堆叠效果好
