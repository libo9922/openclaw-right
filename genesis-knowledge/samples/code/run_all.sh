#!/bin/bash
# 运行所有 Genesis demos
set -e
cd /workspace/repo
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

echo "🎬 Genesis 有趣演示合集"
echo "=================================================="

echo ""
echo "🎬 Demo 1: 多米诺骨牌"
/opt/venv/bin/python3 demos/demo_domino.py

echo ""
echo "🎬 Demo 2: 球体碰撞"
/opt/venv/bin/python3 demos/demo_collision.py

echo ""
echo "🎬 Demo 3: 积木金字塔"
/opt/venv/bin/python3 demos/demo_tower.py

echo ""
echo "🎬 Demo 4: Franka 机器人手臂"
/opt/venv/bin/python3 demos/demo_franka.py

echo ""
echo "=================================================="
echo "✅ 所有演示完成！"
echo "📁 输出: /workspace/repo/demos/output/"
ls -la /workspace/repo/demos/output/*.png 2>/dev/null
