# MinerU 安装

## 安装

```bash
/opt/venv/bin/pip install 'mineru[pipeline]' \
  -i https://mirrors.aliyun.com/pypi/simple/
```

## 下载模型

```bash
# 国内用 ModelScope
mineru-models-download -s modelscope -m pipeline
```

## 验证

```bash
mineru -p test.pdf -o output -b pipeline
```

## 依赖说明

| 包 | 版本要求 | 说明 |
|---|---------|------|
| torch | >=2.6.0 | PyTorch ROCm 版 |
| transformers | >=4.57.3 | HuggingFace |
| onnxruntime | >1.17.0 | ONNX 推理 |
