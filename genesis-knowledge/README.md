# 🤖 Genesis Robot Simulation Workshop — 知识总结

> 2026-06-19 实战记录 | AMD ROCm + RDNA GPU 环境

## 目录

- [环境搭建](./01_environment.md)
- [Sim-to-Real Pipeline](./02_pipeline.md)
- [Genesis 物理引擎](./03_genesis.md)
- [模型资源](./04_models.md)
- [Demo 制作](./05_demos.md)
- [踩坑记录](./06_pitfalls.md)
- [Watchdog 守护脚本](./07_watchdog.md)

## 文件结构

```
genesis-knowledge/
├── *.md                    ← 7 篇知识文档
├── samples/
│   ├── code/               ← Demo 源码 (7个)
│   ├── images/             ← 渲染截图 (6张)
│   └── videos/             ← 渲染视频 (6个)
└── models/                 ← MuJoCo Menagerie 模型配置
    ├── booster_t1/         ← 人形机器人
    ├── unitree_h1/         ← Unitree H1 人形
    ├── boston_dynamics_spot/← Spot 四足
    ├── unitree_go2/        ← Go2 机器狗
    ├── franka_emika_panda/ ← Franka 机械臂
    ├── characters/         ← GLB 3D 角色模型
    └── ...                 ← 共 11 个模型
```
