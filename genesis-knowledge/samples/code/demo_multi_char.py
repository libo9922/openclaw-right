"""
Genesis: 🎬 多角色场景 — 角色在彩色地板上走动旋转
"""
import genesis as gs
import torch, numpy as np, subprocess
from pathlib import Path

OUTPUT_DIR = Path("/workspace/repo/samples/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/30), show_viewer=False)
scene.add_entity(gs.morphs.Plane())

# 彩色地板
for i in range(6):
    for j in range(6):
        c = [[0.95,0.26,0.21,1],[0.25,0.47,0.85,1],[0.30,0.69,0.31,1],[1,0.92,0.23,1],[0.91,0.12,0.39,1]][(i+j)%5]
        scene.add_entity(gs.morphs.Box(size=(0.3,0.3,0.002), pos=[(i-2.5)*0.35, (j-2.5)*0.35, 0.001]),
            surface=gs.surfaces.Default(color=c))

# 多个角色
chars = []
for i in range(4):
    angle = i * np.pi / 2
    x = 0.8 * np.cos(angle)
    y = 0.8 * np.sin(angle)
    c = scene.add_entity(gs.morphs.Mesh(file='/workspace/repo/models/characters/cesium_man.glb', scale=0.4, pos=(x, y, 0.4)))
    chars.append(c)

# 中间的装饰球
scene.add_entity(gs.morphs.Sphere(radius=0.1, pos=(0, 0, 0.5)),
    surface=gs.surfaces.Default(color=[1, 0.8, 0.2, 1]))

cam = scene.add_camera(pos=(3, 3, 2), lookat=(0, 0, 0.3), res=(1280, 720))
scene.build()

duration = 450  # 15秒
frames = []

print("🎬 多角色场景...")

for step in range(duration):
    t = step / 30.0
    
    for i, c in enumerate(chars):
        angle = i * np.pi / 2 + t * 0.5  # 绕圈
        r = 0.8 + 0.2 * np.sin(t * 1.5 + i)  # 半径变化
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        z = 0.4 + 0.1 * abs(np.sin(t * 2.0 + i * 0.7))  # 弹跳
        c.set_pos(torch.tensor([x, y, z], dtype=torch.float32))
    
    scene.step()
    frames.append(cam.render()[0])
    
    if step % 100 == 0:
        print(f"  {step}/{duration}")

out = str(OUTPUT_DIR / "multi_char.mp4")
h, w = frames[0].shape[:2]
proc = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r","30","-i","pipe:0","-c:v","libx264","-pix_fmt","yuv420p","-preset","fast","-crf","23",out], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for f in frames:
    proc.stdin.write(f.tobytes())
proc.stdin.close()
proc.wait()
print(f"✅ multi_char.mp4 ({len(frames)} frames)")
