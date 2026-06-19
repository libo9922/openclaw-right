# 常见问题

## Q: MinerU 支持 AMD ROCm 吗？

支持。PyTorch ROCm 版使用 `torch.cuda.*` API，MinerU 无需修改即可运行。

## Q: PyTorch 下载太慢？

平台已预装在 `/opt/venv/`。手动安装用阿里云镜像：

```bash
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/rocm6.2.4
```

## Q: 模型下载失败？

```bash
mineru-models-download -s modelscope -m pipeline
```

## Q: PDF 中文显示为空格？

安装字体：

```bash
apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
```

## Q: Pandoc 报错 `\tightlist`？

模板中添加：

```latex
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
```

## Q: Pandoc 报错 `Shaded` 环境？

模板中添加：

```latex
\usepackage{framed}
\definecolor{shadecolor}{RGB}{245,245,245}
\newenvironment{Shaded}{\begin{snugshade}}{\end{snugshade}}
\newenvironment{Highlighting}{}{}
```

## 在线工具

| 工具 | 链接 |
|------|------|
| Overleaf | overleaf.com |
| StackEdit | stackedit.io |
| HackMD | hackmd.io |
