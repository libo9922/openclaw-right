# OCR 使用方法

## 基本用法

```bash
mineru -p <输入文件> -o <输出目录> -b pipeline
```

## 常用参数

| 参数 | 说明 |
|------|------|
| `-p` | 输入文件路径 |
| `-o` | 输出目录 |
| `-b` | 后端，推荐 `pipeline` |
| `-l` | 语言，`ch` 中文，`en` 英文 |
| `-s` | 起始页码（从 0 开始） |
| `-e` | 结束页码 |

## 示例

```bash
# 中文 PDF
mineru -p input.pdf -o output -b pipeline -l ch

# 英文 PDF，前 100 页
mineru -p input.pdf -o output -b pipeline -s 0 -e 99

# 并行处理
mineru -p file1.pdf -o out1 -b pipeline &
mineru -p file2.pdf -o out2 -b pipeline &
wait
```

## 输出文件

| 文件 | 用途 |
|------|------|
| `.md` | Markdown 正文 |
| `_middle.json` | 结构数据 |
| `_content_list.json` | 内容列表 |
| `_layout.pdf` | 版面标注 |
| `images/` | 提取的图片 |

## 性能参考（AMD gfx1100 48GB）

| 内容类型 | 页数 | 耗时 |
|---------|------|------|
| 英文教材（含公式） | 100 | ~14 分钟 |
| 中文教材（含表格） | 100 | ~10 分钟 |
