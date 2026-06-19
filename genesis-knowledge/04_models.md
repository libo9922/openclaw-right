# 04 — 模型资源

## Genesis 内置模型

路径: `/opt/venv/lib/python3.12/site-packages/genesis/assets/`

| 模型 | 格式 | 自由度 | 状态 |
|------|------|--------|------|
| Franka Panda | MJCF | 9 (7+2手指) | ✅ 可用 |
| KUKA iiwa | URDF | 7 | ✅ 可用 |
| UR5e | MJCF | 6 | ✅ 可用 |
| Shadow Hand | URDF | 多 | ✅ 可用 |
| Go2 机器狗 | URDF | 18 | ❌ 穿模 |
| ANYmal C | URDF | 18 | ❌ 穿模 |
| Crazyflie 无人机 | URDF | 4 | ✅ 可用 |
| Walker | MJCF | 9 | ⚠️ 看起来像大炮 |
| Humanoid | MJCF | 27 | ❌ 穿模 |

## MuJoCo Menagerie 模型

已下载到 `/workspace/repo/models/` (332MB)

来源: https://github.com/google-deepmind/mujoco_menagerie

| 模型 | 类型 | 自由度 | 状态 |
|------|------|--------|------|
| booster_t1 | 人形 | 29 | ⚠️ 可见但倒地 |
| unitree_h1 | 人形 | 25 | ⚠️ 可见但倒地 |
| boston_dynamics_spot | 四足 | 18 | ❌ 穿模 |
| unitree_go2 | 四足 | 18 | ❌ 穿模 |
| anybotics_anymal_c | 四足 | 18 | ❌ 穿模 |
| franka_fr3 | 机械臂 | 7 | ✅ 可用 |
| apptronik_apollo | 人形 | 多 | 未测试 |
| berkeley_humanoid | 人形 | 多 | 未测试 |
| leap_hand | 灵巧手 | 多 | 未测试 |

## GLB 3D 模型

路径: `/workspace/repo/models/characters/`

| 模型 | 来源 | 状态 |
|------|------|------|
| cesium_man.glb | KhronosGroup glTF-Sample | ✅ 可用 |

## 穿模问题分析

Genesis 的 MJCF/URDF 碰撞检测对复杂模型不生效:
- 四足机器人 (Go2, ANYmal, Spot): 加载后直接掉穿地面
- 人形机器人 (H1, T1, Berkeley): 加载后倒地或穿模
- 机械臂 (Franka): 正常工作

**原因**: Genesis 的碰撞系统对 mesh-based 碰撞体支持不完善

**解决方案**:
1. 只用 Franka 等验证过的模型
2. 用 GLB 格式做静态装饰（无碰撞）
3. 等 Genesis 更新修复碰撞 bug

## 模型格式对比

| 格式 | 用途 | 碰撞 | 动画 | 视觉质量 |
|------|------|------|------|----------|
| MJCF | MuJoCo 仿真 | ✅ | ✅ 关节 | ⚠️ 工业风 |
| URDF | ROS 仿真 | ✅ | ✅ 关节 | ⚠️ 工业风 |
| GLB | 3D 渲染 | ❌ | ✅ 骨骼 | ✅ 好看 |
| OBJ | 静态网格 | ❌ | ❌ | ✅ 好看 |
| USD | Pixar 格式 | ✅ | ✅ | ✅ 好看 |
