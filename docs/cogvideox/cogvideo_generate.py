#!/usr/bin/env python3
"""
CogVideoX-5B 文生视频推理脚本
支持 AMD ROCm / NVIDIA CUDA

用法:
  python3 cogvideo_generate.py --prompt "A puppy in a field" --steps 30 --num_frames 25
"""

import os, sys, time, argparse

# ROCm 环境变量
os.environ.setdefault("AITER_JIT_DISABLE", "1")
os.environ.setdefault("HIP_FORCE_DEV_KERNARG", "1")
os.environ.setdefault("USE_ROCM_AITER_ROPE_BACKEND", "0")

import torch
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video


def parse_args():
    parser = argparse.ArgumentParser(
        description="CogVideoX-5B Text-to-Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --prompt "A golden retriever puppy in a flower field"
  %(prog)s --prompt "Cinematic dragon city" --steps 50 --num_frames 49
  %(prog)s --prompt "A cat on beach" --steps 20 --num_frames 17 --quick
        """,
    )
    parser.add_argument("--model_dir", type=str,
                        default="/workspace/models/CogVideoX-5B",
                        help="CogVideoX-5B 模型目录路径")
    parser.add_argument("--prompt", type=str, required=True,
                        help="英文提示词，描述要生成的视频场景")
    parser.add_argument("--negative_prompt", type=str,
                        default="blurry, low quality, distorted, ugly, deformed",
                        help="负面提示词")
    parser.add_argument("--steps", type=int, default=30,
                        help="推理步数 (默认30, 推荐20-50)")
    parser.add_argument("--guidance", type=float, default=6.0,
                        help="CFG 引导尺度 (默认6.0, 范围3.0-7.0)")
    parser.add_argument("--num_frames", type=int, default=25,
                        help="生成帧数 (默认25, 最大49)")
    parser.add_argument("--fps", type=int, default=8,
                        help="视频帧率 (默认8)")
    parser.add_argument("--height", type=int, default=480,
                        help="视频高度 (默认480)")
    parser.add_argument("--width", type=int, default=720,
                        help="视频宽度 (默认720)")
    parser.add_argument("--output", type=str, default=None,
                        help="输出视频路径 (默认自动生成)")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子 (固定种子可复现)")
    parser.add_argument("--cpu_offload", action="store_true",
                        help="启用 CPU offload 以减少 VRAM 占用")
    parser.add_argument("--quick", action="store_true",
                        help="快速模式: 20步, 17帧, 480p")
    return parser.parse_args()


def main():
    args = parse_args()

    # 快速模式覆盖参数
    if args.quick:
        args.steps = 20
        args.num_frames = 17
        args.height = 480
        args.width = 720

    # 检查 GPU
    if not torch.cuda.is_available():
        print("❌ 错误: 未检测到 GPU (CUDA/ROCm)")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"🖥️  GPU: {device_name}")
    print(f"📊 VRAM: {vram_total:.1f}GB")
    print(f"📦 模型: {args.model_dir}")

    # 检查模型目录
    if not os.path.isdir(args.model_dir):
        print(f"❌ 错误: 模型目录不存在: {args.model_dir}")
        print("请先下载模型: huggingface-cli download THUDM/CogVideoX-5B "
              "--local-dir /workspace/models/CogVideoX-5B")
        sys.exit(1)

    # 加载模型
    print("⏳ 加载模型... ", end="", flush=True)
    t0 = time.time()
    pipe = CogVideoXPipeline.from_pretrained(
        args.model_dir,
        torch_dtype=torch.bfloat16,
    )

    # offload 策略
    if args.cpu_offload:
        pipe.enable_model_cpu_offload()
        print("[CPU offload] ", end="")
    else:
        pipe.to("cuda")

    pipe.enable_attention_slicing()
    t1 = time.time()
    print(f"✅ ({t1-t0:.1f}s)")

    # 推理参数
    generator = None
    if args.seed is not None:
        generator = torch.Generator(device="cuda").manual_seed(args.seed)

    print(f"\n🎬 生成中...")
    print(f"   Prompt: {args.prompt}")
    print(f"   Steps: {args.steps} | CFG: {args.guidance} | Frames: {args.num_frames}")
    print(f"   Size: {args.width}x{args.height} @ {args.fps}fps")
    print()

    t2 = time.time()
    with torch.no_grad():
        result = pipe(
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance,
            num_frames=args.num_frames,
            height=args.height,
            width=args.width,
            generator=generator,
        )
    t3 = time.time()

    # 提取帧
    frames = result.frames
    if isinstance(frames, (list, tuple)) and len(frames) == 1 and isinstance(frames[0], (list, tuple)):
        frames = frames[0]

    vram_peak = torch.cuda.max_memory_allocated() / 1e9
    print(f"\n✅ 生成完成 ({t3-t2:.1f}s)")
    print(f"   VRAM 峰值: {vram_peak:.1f}GB")
    print(f"   帧数: {len(frames)}")

    # 保存视频
    output_path = args.output
    if output_path is None:
        os.makedirs("output", exist_ok=True)
        ts = int(time.time())
        output_path = f"output/cogvideo_{ts}.mp4"

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    export_to_video(frames, output_path, fps=args.fps)
    file_size = os.path.getsize(output_path)

    print(f"💾 保存至: {output_path}")
    print(f"   文件大小: {file_size / 1e6:.1f}MB")


if __name__ == "__main__":
    main()