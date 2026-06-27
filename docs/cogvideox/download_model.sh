#!/usr/bin/env bash
# CogVideoX-5B 一键下载脚本
# 用法: bash download_model.sh

set -e

MODEL_DIR="${1:-/workspace/models/CogVideoX-5B}"
MIRROR="${HF_ENDPOINT:-https://hf-mirror.com}"

echo "================================================"
echo "CogVideoX-5B 模型下载"
echo "================================================"
echo "模型目录: $MODEL_DIR"
echo "镜像源:   $MIRROR"
echo ""

# 检查 huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli 未安装"
    echo "   安装: pip install huggingface_hub"
    exit 1
fi

# 检查磁盘空间
AVAILABLE=$(df -BG "$MODEL_DIR" 2>/dev/null | awk 'NR==2 {print $4}' | tr -d 'G' || echo "?")
echo "📀 可用磁盘: ${AVAILABLE}GB"
echo ""

# 下载
echo "⬇️  开始下载模型 (约 21GB)..."
echo "    包含: transformer(11GB), text_encoder(9.5GB), VAE(862MB)"
echo ""

start_time=$(date +%s)

HF_ENDPOINT=$MIRROR huggingface-cli download THUDM/CogVideoX-5B \
    --local-dir "$MODEL_DIR" \
    --resume-download

end_time=$(date +%s)
elapsed=$((end_time - start_time))

echo ""
echo "✅ 下载完成! (${elapsed}秒)"
echo ""
echo "📂 文件列表:"
du -sh "$MODEL_DIR"/*
echo ""
echo "💡 运行推理:"
echo "   python3 cogvideo_generate.py --model_dir $MODEL_DIR --prompt \"your prompt\""