"""
Genesis Demo 1: 🏗️ 多米诺骨牌
"""
import genesis as gs
import torch
from PIL import Image
from pathlib import Path

OUTPUT_DIR = Path("/workspace/repo/demos/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/60, gravity=(0,0,-9.81)), show_viewer=False)
scene.add_entity(gs.morphs.Plane())

colors = [[0.95,0.26,0.21,1],[0.30,0.69,0.31,1],[0.25,0.47,0.85,1],[1,0.92,0.23,1],[1,0.60,0,1],[0.91,0.12,0.39,1],[0.61,0.15,0.69,1]]
blocks = []
for i in range(10):
    block = scene.add_entity(gs.morphs.Box(size=(0.015,0.04,0.06)), surface=gs.surfaces.Default(color=colors[i%len(colors)]))
    blocks.append(block)
scene.add_entity(gs.morphs.Sphere(radius=0.025, pos=[-0.05,0,0.1]), surface=gs.surfaces.Default(color=[0.8,0.2,0.8,1]))
cam = scene.add_camera(pos=(0.3,0.3,0.3), lookat=(0,0,0.03), res=(640,480))
scene.build()
for i, block in enumerate(blocks):
    block.set_pos(torch.tensor([i*0.04-0.15, 0, 0.03], dtype=torch.float32))
for step in range(300):
    scene.step()
Image.fromarray(cam.render()[0]).save(str(OUTPUT_DIR / "domino.png"))
print("✅ domino.png")
