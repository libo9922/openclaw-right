# LaTeX / PDF 生成

## 输出格式对比

| 格式 | 公式 | 图片 | 推荐场景 |
|------|------|------|---------|
| `.md` | 原始 LaTeX | 相对路径 | 通用 |
| `.html` | MathJax 渲染 | base64 内嵌 | 在线阅读 |
| `.pdf` | 需处理 | 内嵌 | 打印 |
| `.tex` | 原始 LaTeX | 引用 | 二次编辑 |

## Markdown 转 HTML

```bash
python3 md2html.py input.md
# 生成 input.html（自包含，图片 base64 内嵌）
```

## Markdown 转 PDF

```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --template=template.latex \
  --toc \
  --number-sections \
  -V title="标题" \
  -V author="作者" \
  --resource-path=./images/
```

## 公式处理策略

1. **HTML** — MathJax 渲染，容错最好，推荐
2. **PDF** — 替换为 `[公式]` 占位符
3. **Overleaf** — 拿 `.tex` 文件手动修复公式

## 字体配置

```latex
\setCJKmainfont{Noto Serif CJK SC}   % 中文
\setmainfont{DejaVu Serif}            % 英文
```
