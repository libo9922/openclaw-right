# PDF OCR 项目 — MinerU + AMD ROCm GPU

基于 [MinerU](https://github.com/opendatalab/MinerU) 在 AMD ROCm GPU 平台上实现 PDF/图片 OCR 转 Markdown。

## 项目结构

```
pdf/
├── docs/                          # 项目文档
│   ├── README.md                  # 本文件
│   ├── 01-environment.md          # 环境配置
│   ├── 02-mineru-install.md       # MinerU 安装
│   ├── 03-ocr-usage.md            # OCR 使用方法
│   ├── 04-latex-pdf.md            # LaTeX/PDF 生成
│   ├── 05-faq.md                  # 常见问题
│   ├── md2html.py                 # Markdown 转 HTML 工具
│   └── template.latex             # XeLaTeX 模板
└── markdown/                      # OCR 输出结果
    ├── en_robotics/               # 英文版完整输出
    ├── cn_amplifier/              # 中文版完整输出
    ├── *.html                     # 自包含 HTML（公式完整）
    ├── *.pdf                      # PDF 文件
    └── *.tex                      # LaTeX 源文件
```

## 快速开始

```bash
# 1. 激活环境
source /opt/venv/bin/activate

# 2. OCR 转换
mineru -p input.pdf -o output_dir -b pipeline -l ch  # 中文
mineru -p input.pdf -o output_dir -b pipeline         # 英文

# 3. 转 HTML（公式完整）
python3 docs/md2html.py output.md

# 4. 转 PDF（需要 pandoc + xelatex）
pandoc input.md -o output.pdf --pdf-engine=xelatex --template=docs/template.latex
```

## 输出格式

| 格式 | 优点 | 缺点 |
|------|------|------|
| `.md` | 通用、可编辑 | 图片需相对路径 |
| `.html` | 公式完整、图片内嵌、随处可看 | 文件较大 |
| `.pdf` | 可打印、排版美观 | 公式需手动修复 |
| `.tex` | LaTeX 源文件、可二次编辑 | 需 LaTeX 环境编译 |

## 相关链接

- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [MinerU 文档](https://opendatalab.github.io/MinerU/)
- [PyTorch ROCm](https://pytorch.org/get-started/locally/)
- [Overleaf 在线 LaTeX](https://www.overleaf.com/)
