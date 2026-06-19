# 03 — Genesis 物理引擎

## 简介

Genesis 是一个用于物理 AI 开发的仿真平台，由 Genesis Embodied AI 开发。

- **GitHub**: https://github.com/Genesis-Embodied-AI/genesis-world
- **速度**: 比 Isaac Sim 快 10-80 倍
- **后端**: CUDA, ROCm (AMD), Metal (Apple), Vulkan, CPU

## 架构

```
┌─────────────────────────────────┐
│      Simulation Interface       │  ← 用户 API
├─────────────────────────────────┤
│   Physics (多物理求解器耦合)      │  ← Rigid/FEM/MPM/SPH/PBD/IPC
├─────────────────────────────────┤
│   Render (Nyx/Luisa/Pyrender)   │  ← 渲染器
├─────────────────────────────────┤
│   Compiler (Quadrants)          │  ← CUDA/ROCm/Metal/Vulkan
└─────────────────────────────────┘
```

## 求解器

| 求解器 | 用途 | 例子 |
|--------|------|------|
| Rigid | 刚体碰撞、关节 | 机器人抓取、积木塔 |
| FEM | 有限元（软体变形） | 橡胶球挤压 |
| MPM | 物质点法 | 沙子流动、雪地脚印 |
| SPH | 光滑粒子流体 | 水流、倒水入杯 |
| PBD | 位置约束 | 布料飘动、液体飞溅 |
| IPC | 隐式接触 | 机器人叠衣服 |

## API 要点

```python
import genesis as gs

# 初始化（只能调用一次！）
gs.init(backend=gs.gpu, logging_level="warning")

# 创建场景
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/30, gravity=(0, 0, -9.81)),
    show_viewer=False,  # 无头模式
)

# 添加实体
scene.add_entity(gs.morphs.Plane())  # 地面
scene.add_entity(gs.morphs.Box(size=(0.1, 0.1, 0.1), pos=[0, 0, 0.5]),
    surface=gs.surfaces.Default(color=[1, 0, 0, 1]))

# 机器人
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))

# 摄像头（必须在 build 前添加！）
cam = scene.add_camera(pos=(1, 1, 1), lookat=(0, 0, 0.5), res=(640, 480))

# 构建场景
scene.build()

# 模拟
for step in range(100):
    scene.step()

# 渲染（返回 tuple，第一个元素是 RGB numpy 数组）
rgb = cam.render()[0]  # shape: (H, W, 3)
```

## 注意事项

1. `gs.init()` 只能调用一次，多次调用会报错
2. 摄像头必须在 `scene.build()` 之前添加
3. `cam.render()` 返回 tuple，用 `[0]` 获取 RGB
4. `set_pos()` 接受 torch.Tensor (1D)，不接受 numpy 2D
5. MJCF 模型的碰撞检测有 bug，复杂模型会穿模

## 擅长 vs 不擅长

| ✅ 擅长 | ❌ 不擅长 |
|---------|----------|
| 机械臂抓取 | 复杂人形机器人平衡 |
| 刚体碰撞 | 精细流体仿真 |
| 大规模并行仿真 | 动漫角色动画 |
| Sim-to-Real 迁移 | 布料/软体效果 |
| RL 策略训练 | 3D 艺术渲染 |
