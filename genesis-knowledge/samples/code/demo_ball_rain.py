"""
Genesis: 🔮 彩色弹球雨
大量彩色球从空中落下，弹跳碰撞
"""
import genesis as gs
import torch, numpy as np, subprocess
from pathlib import Path

OUTPUT_DIR = Path("/workspace/repo/samples/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/60, gravity=(0,0,-9.81)), show_viewer=False)
scene.add_entity(gs.morphs.Plane())

# 容器壁
scene.add_entity(gs.morphs.Box(size=(0.01, 1.0, 0.5), pos=(-0.5, 0, 0.25)),
    surface=gs.surfaces.Default(color=[0.5,0.5,0.5,1]))
scene.add_entity(gs.morphs.Box(size=(0.01, 1.0, 0.5), pos=(0.5, 0, 0.25)),
    surface=gs.surfaces.Default(color=[0.5,0.5,0.5,1]))
scene.add_entity(gs.morphs.Box(size=(1.0, 0.01, 0.5), pos=(0, -0.5, 0.25)),
    surface=gs.surfaces.Default(color=[0.5,0.5,0.5,1]))
scene.add_entity(gs.morphs.Box(size=(1.0, 0.01, 0.5), pos=(0, 0.5, 0.25)),
    surface=gs.surfaces.Default(color=[0.5,0.5,0.5,1]))

# 彩色球（分批落下）
balls = []
colors = [
    [0.95,0.26,0.21,1], [0.25,0.47,0.85,1], [0.30,0.69,0.31,1],
    [1,0.92,0.23,1], [0.91,0.12,0.39,1], [0.61,0.15,0.69,1],
    [1,0.60,0,1], [0.2,0.8,0.8,1],
]

# 第一批
for i in range(20):
    x = np.random.uniform(-0.3, 0.3)
    y = np.random.uniform(-0.3, 0.3)
    c = colors[i % len(colors)]
    b = scene.add_entity(gs.morphs.Sphere(radius=0.02, pos=(x, y, 0.8 + i*0.05)),
        surface=gs.surfaces.Default(color=c))
    balls.append(b)

# 第二批（延迟落下）
for i in range(15):
    x = np.random.uniform(-0.2, 0.2)
    y = np.random.uniform(-0.2, 0.2)
    c = colors[(i+4) % len(colors)]
    b = scene.add_entity(gs.morphs.Sphere(radius=0.025, pos=(x, y, 1.5 + i*0.05)),
        surface=gs.surfaces.Default(color=c))
    balls.append(b)

cam = scene.add_camera(pos=(1.5, 1.5, 1.0), lookat=(0, 0, 0.2), res=(1280, 720))
scene.build()

duration = 450  # 15秒
frames = []

print("🔮 彩色弹球雨...")

for step in range(duration):
    scene.step()
    frames.append(cam.render()[0])
    if step % 100 == 0:
        print(f"  {step}/{duration}")

out = str(OUTPUT_DIR / "ball_rain.mp4")
h, w = frames[0].shape[:2]
proc = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r","30","-i","pipe:0","-c:v","libx264","-pix_fmt","yuv420p","-preset","fast","-crf","23",out], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for f in frames:
    proc.stdin.write(f.tobytes())
proc.stdin.close()
proc.wait()
print(f"✅ ball_rain.mp4 ({len(frames)} frames)")
