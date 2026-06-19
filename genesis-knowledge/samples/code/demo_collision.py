"""
Genesis Demo 2: 🎯 球体碰撞
"""
import genesis as gs
from PIL import Image
from pathlib import Path

OUTPUT_DIR = Path("/workspace/repo/demos/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

gs.init(backend=gs.gpu, logging_level="warning")
scene = gs.Scene(sim_options=gs.options.SimOptions(dt=1/60, gravity=(0,0,-9.81)), show_viewer=False)
scene.add_entity(gs.morphs.Plane())
positions = [[0,0,0.5],[0.1,0.1,0.8],[-0.1,0.05,0.6],[0.05,-0.1,0.7],[-0.05,-0.05,0.9]]
colors = [[0.95,0.26,0.21,1],[0.30,0.69,0.31,1],[0.25,0.47,0.85,1],[1,0.92,0.23,1],[1,0.60,0,1]]
for pos, color in zip(positions, colors):
    scene.add_entity(gs.morphs.Sphere(radius=0.03, pos=pos), surface=gs.surfaces.Default(color=color))
cam = scene.add_camera(pos=(0.4,0.4,0.4), lookat=(0,0,0.1), res=(640,480))
scene.build()
for step in range(200):
    scene.step()
Image.fromarray(cam.render()[0]).save(str(OUTPUT_DIR / "collision.png"))
print("✅ collision.png")
