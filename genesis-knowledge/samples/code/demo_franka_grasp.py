"""
Genesis: 🤖 Franka 抓取彩色积木
机械臂在桌面上抓取和移动彩色积木
"""
import genesis as gs
import torch, numpy as np, subprocess
from pathlib import Path

OUTPUT_DIR = Path("/workspace/repo/samples/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/30), show_viewer=False)
scene.add_entity(gs.morphs.Plane())

# 桌子
scene.add_entity(gs.morphs.Box(size=(0.6, 0.6, 0.02), pos=(0.4, 0, 0.35)),
    surface=gs.surfaces.Default(color=[0.6, 0.4, 0.2, 1]))
scene.add_entity(gs.morphs.Box(size=(0.05, 0.05, 0.35), pos=(0.4, 0, 0.175)),
    surface=gs.surfaces.Default(color=[0.5, 0.35, 0.15, 1]))

# 彩色积木
colors = [[0.95,0.26,0.21,1],[0.25,0.47,0.85,1],[0.30,0.69,0.31,1],[1,0.92,0.23,1],[0.91,0.12,0.39,1]]
blocks = []
for i in range(5):
    b = scene.add_entity(gs.morphs.Box(size=(0.03,0.03,0.03), pos=(0.3+i*0.05, 0, 0.37)),
        surface=gs.surfaces.Default(color=colors[i]))
    blocks.append(b)

# Franka
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))

cam = scene.add_camera(pos=(1.2, 0.8, 0.8), lookat=(0.3, 0, 0.3), res=(1280, 720))
scene.build()

duration = 600  # 20秒
frames = []

print("🤖 Franka 抓取彩色积木...")

for step in range(duration):
    t = step / 30.0
    
    # 手臂在桌面上方移动
    phase = (t * 0.3) % 1.0
    x = 0.3 + 0.2 * np.sin(2 * np.pi * 0.5 * t)
    y = 0.15 * np.sin(2 * np.pi * 0.7 * t)
    z_hover = 0.45
    z_grasp = 0.38
    
    # 周期性抓取：下降→抓→上升→移动→释放
    cycle = (t * 0.4) % 1.0
    if cycle < 0.3:
        z = z_hover
        finger = 0.04
    elif cycle < 0.5:
        z = z_hover - (z_hover - z_grasp) * ((cycle - 0.3) / 0.2)
        finger = 0.04
    elif cycle < 0.7:
        z = z_grasp
        finger = 0.01
    else:
        z = z_grasp + (z_hover - z_grasp) * ((cycle - 0.7) / 0.3)
        finger = 0.01
    
    # IK 近似：直接设置关节角度模拟运动
    joints = torch.tensor([
        0.0,
        -0.5 + 0.3 * np.sin(2 * np.pi * 0.3 * t),
        0.0,
        -1.5 + 0.3 * np.sin(2 * np.pi * 0.3 * t + 0.5),
        0.0,
        1.0 + 0.2 * np.sin(2 * np.pi * 0.3 * t + 1.0),
        0.5 * np.sin(2 * np.pi * 0.5 * t),
        finger, finger
    ], dtype=torch.float32)
    franka.set_dofs_position(joints)
    
    scene.step()
    frames.append(cam.render()[0])
    
    if step % 100 == 0:
        print(f"  {step}/{duration}")

out = str(OUTPUT_DIR / "franka_grasp.mp4")
h, w = frames[0].shape[:2]
proc = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r","30","-i","pipe:0","-c:v","libx264","-pix_fmt","yuv420p","-preset","fast","-crf","23",out], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for f in frames:
    proc.stdin.write(f.tobytes())
proc.stdin.close()
proc.wait()
print(f"✅ franka_grasp.mp4 ({len(frames)} frames)")
