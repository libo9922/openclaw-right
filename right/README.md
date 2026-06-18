# Qwen3-8B on AMD GPU (ROCm) — 完整指南

## 一、chat.py 解析

文件位置: `~/workspace/right/chat.py`

### 核心思路

用 vLLM 启动 OpenAI 兼容 API server，chat.py 作为客户端通过 HTTP 调用。

```
┌──────────┐   HTTP/SSE    ┌──────────────┐   ROCm/HIP   ┌──────────────┐
│ chat.py  │ ───────────> │  vLLM Server │ ──────────> │  AMD GPU     │
│ (终端)   │ <─────────── │  :8000       │ <────────── │  (gfx1100)   │
└──────────┘   流式token   └──────────────┘              └──────────────┘
```

### 关键代码说明

1. **OpenAI 客户端** — `base_url` 指向本地 vLLM server，`api_key` 随意填（vLLM 不校验）
2. **流式输出** — `stream=True`，逐 token 返回，实现打字机效果
3. **thinking 模式** — Qwen3 默认开启 `<think>` 思考链，通过 `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` 关闭
4. **上下文管理** — `messages` 列表累积完整对话历史，每轮发送全部历史

### Qwen3 特有参数

```python
# 关闭思考（默认开启，会消耗大量 token）
extra_body = {"chat_template_kwargs": {"enable_thinking": False}}

# 开启思考（默认行为，不需要额外参数）
extra_body = {}
```

---

## 二、运行 Qwen3-8B 的完整流程

### 环境概况

| 项目 | 版本 |
|------|------|
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.8.0-79-generic |
| Python | 3.12.3 |
| ROCm | 7.2.1 (HIP 7.2.53211) |
| PyTorch | 2.9.1+rocm700 |
| vLLM | 0.14.0+rocm700 |
| GPU | AMD Radeon Graphics (gfx1100, 51.5GB VRAM) |

### 步骤 1: 确认 GPU 可见

```bash
# 检查 ROCm 是否识别 GPU
rocm-smi

# 检查 PyTorch 能否看到 GPU
/opt/venv/bin/python3 -c "
import torch
print('HIP available:', torch.cuda.is_available())
print('Device count:', torch.cuda.device_count())
print('Device name:', torch.cuda.get_device_name(0))
print('VRAM:', torch.cuda.get_device_properties(0).total_memory / 1e9, 'GB')
"
```

### 步骤 2: 修复 triton（关键！）

**问题**: 预装的 `pytorch-triton-rocm-0.0.1` 是空壳 stub，`import triton` 会抛 `RuntimeError: Should never be installed`。

**解决**:

```bash
# 卸载空壳
/opt/venv/bin/pip uninstall triton pytorch-triton-rocm -y

# 安装真正的 triton（用清华镜像，201MB 下载仅需 2 秒）
/opt/venv/bin/pip install triton -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤 3: 下载模型

```bash
# 模型已预下载到: /root/.cache/huggingface/Qwen3-8B/
# 如果需要重新下载，用 HuggingFace 镜像：
export HF_ENDPOINT=https://hf-mirror.com
/opt/venv/bin/huggingface-cli download Qwen/Qwen3-8B --local-dir /root/.cache/huggingface/Qwen3-8B
```

### 步骤 4: 启动 vLLM Server

```bash
export HIP_VISIBLE_DEVICES=0
nohup /opt/venv/bin/python3 -m vllm.entrypoints.openai.api_server \
  --model /root/.cache/huggingface/Qwen3-8B \
  --served-model-name Qwen3-8B \
  --dtype auto \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  > /tmp/vllm-qwen3.log 2>&1 &

# 等待启动完成（约 90 秒）
curl http://localhost:8000/health
```

### 步骤 5: 使用交互式对话

```bash
/opt/venv/bin/python3 ~/workspace/right/chat.py
```

---

## 三、踩坑与技巧

### 🔧 triton 问题（最常见的坑）

| 现象 | 原因 | 解决 |
|------|------|------|
| `RuntimeError: Should never be installed` | pytorch-triton-rocm 是空壳 | 卸载后装真正的 triton |
| `ImportError: triton not available on ROCm` | 手动改 stub 为 ImportError | 同上，直接装真 triton |
| vLLM 要求 `triton==3.4.0` 但装了 3.7.0 | 版本不匹配 | 忽略警告，实际可用 |

### 🔧 flash_attn 问题

vLLM 的 rotary embedding 会通过 `flash_attn.ops.triton.rotary` 导入 triton。如果 triton 不工作，整个 vLLM 就起不来。

错误链路:
```
vLLM → Qwen3Attention → get_rope → ApplyRotaryEmb
  → flash_attn.ops.triton.rotary → import triton → 💥
```

### 🔧 transformers 版本问题

预装的 transformers 4.57.6 有 `GenerationMixin` 导入错误。如果用 transformers 直接推理（非 vLLM），需要降级:

```bash
/opt/venv/bin/pip install 'transformers>=4.51,<4.55' -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 🚀 源和镜像速度对比

| 源 | 速度 | 用途 |
|----|------|------|
| `pypi.tuna.tsinghua.edu.cn` | **95 MB/s** | pip 安装（国内最快） |
| `hf-mirror.com` | ~1 MB/s（偶尔超时） | HuggingFace 模型下载 |
| `pypi.org` | 超时/极慢 | 不推荐 |
| `huggingface.co` | 超时/极慢 | 不推荐 |

**最佳实践**: pip 走清华源，HF 模型优先检查本地缓存。

```bash
# 全局配置 pip 清华源（可选）
/opt/venv/bin/pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 🚀 vLLM 启动参数调优

```bash
--max-model-len 8192          # 上下文长度，越大 KV cache 占用越多
--gpu-memory-utilization 0.9  # GPU 显存使用率，留 10% 余量
--dtype auto                  # 自动选择精度（bfloat16）
--enforce-eager               # 禁用 CUDA graph（调试用，生产去掉）
```

### 🚀 性能参考

| 指标 | 数值 |
|------|------|
| 模型加载 | ~90s（含 torch.compile + CUDA graph capture） |
| 显存占用 | ~19.3 GiB（模型 15.3 GiB + KV cache 4 GiB） |
| 推理速度 | 23.2 tok/s（单请求） |
| KV cache 容量 | 189,008 tokens |

### 🔍 调试技巧

```bash
# 查看 vLLM 实时日志
tail -f /tmp/vllm-qwen3.log

# 检查 GPU 状态
rocm-smi

# 检查 server 是否存活
curl http://localhost:8000/health

# 列出已加载模型
curl http://localhost:8000/v1/models

# 测试 API 调用
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3-8B",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 64
  }'

# 杀掉 server 重启
pkill -f "vllm.entrypoints"
```

---

## 四、文件清单

```
~/workspace/right/
├── chat.py      # 交互式对话客户端
└── README.md    # 本文档
```
