# 02 — Sim-to-Real Pipeline

## 概念

```
Genesis 物理仿真 → 生成专家数据 → 训练 VLA 模型 → 部署到真实机器人
```

## 三步流水线

| 步骤 | 脚本 | 时间 | 产出 |
|------|------|------|------|
| Data Generation | `02_gen_data_custom_scene.py` | ~15 min | 100 episodes × 135 frames |
| Training | `02_train_vla.py` | ~11 min | SmolVLA 4000 steps |
| Evaluation | `04_eval_custom_scene.py` | ~4 min | 20 episodes closed-loop |

## Data Generation

```bash
python scripts/02_gen_data_custom_scene.py \
    --scene rustic_kitchen --anchor floor_origin \
    --camera-layout up_wrist \
    --n-episodes 100 --repo-id local/kitchen-pick --seed 42
```

- 使用 IK (逆运动学) 规划抓取轨迹
- 双摄像头: up (俯视) + wrist (手腕)
- 渲染: GPU 硬件光栅化 (radeonsi)
- 输出: LeRobot 数据集格式 (parquet + AV1 视频)

## Training

```bash
python scripts/02_train_vla.py \
    --dataset-id local/kitchen-pick \
    --pretrained /opt/workshop/models/smolvla_base \
    --n-steps 4000 --batch-size 4
```

### 关键发现: 冻结 vs 解冻 Vision Encoder

| 配置 | Steps | Final Loss | Eval Success Rate |
|------|-------|------------|-------------------|
| 冻结 vision encoder, 只训 expert | 4000 | 0.037 | **0%** |
| **解冻 vision encoder, 训所有层** | 6000 | 0.037 | **35%** |

**教训: 解冻 vision encoder 是关键改进！**

改进训练配置:
```python
cfg = SmolVLAConfig(
    freeze_vision_encoder=False,  # 解冻!
    train_expert_only=False,       # 训所有层!
    train_state_proj=True,
)
# + Cosine LR schedule with warmup
# + Lower LR (5e-5)
```

## Evaluation

```bash
python scripts/04_eval_custom_scene.py \
    --checkpoint output/train/smolvla_kitchen_v2/final \
    --dataset-id local/kitchen-pick \
    --n-episodes 20 --max-steps 150 --record-video
```

## Sim-to-Real 的核心挑战

1. **视觉差距** — 仿真渲染 vs 真实摄像头
2. **物理差距** — 仿真摩擦/碰撞 vs 真实物理
3. **动作差距** — 完美 PD 控制 vs 真实电机延迟

## 解决方案

- **Domain Randomization**: 随机化仿真参数
- **多摄像头**: 减少单视角过拟合
- **GPU 渲染**: 更接近真实画面
- **预训练 VLA**: SigLIP 视觉编码器有泛化能力
