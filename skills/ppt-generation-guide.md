# SKILL.md — PPT 制作完全指南 (cc-agent 实战经验)

## 概述
使用 python-pptx 在 AMD ROCm 服务器上生成高质量 PPT 的完整流程，包含配色方案、布局模板、常见坑和最佳实践。

## 技术栈
- **库**: python-pptx (纯 Python，无需 Office)
- **字体**: Microsoft YaHei / SimHei / wqy-zenhei
- **环境**: Python 3.12 + /opt/venv/

## 安装
```bash
/opt/venv/bin/pip install python-pptx -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 一、配色方案（已验证最优）

### 方案 A：深蓝灰 + 暖米色 + 古铜金（学术/历史/商务）⭐推荐
```python
NAVY       = RGBColor(0x1B, 0x2A, 0x4A)  # 主背景、标题栏
DEEP_NAVY  = RGBColor(0x0A, 0x12, 0x25)  # 封面背景
CREAM      = RGBColor(0xF5, 0xF0, 0xE8)  # 浅色文字、卡片底
PARCHMENT  = RGBColor(0xE8, 0xDE, 0xD0)  # 浅色页面背景
GOLD       = RGBColor(0xC4, 0x9A, 0x6C)  # 装饰条、强调
CRIMSON    = RGBColor(0xA0, 0x30, 0x40)  # 警示、重点
GRAY       = RGBColor(0x6B, 0x7B, 0x8D)  # 次要文字
```

### 方案 B：科技蓝
```python
DARK_BLUE  = RGBColor(0x0D, 0x1B, 0x2A)
BRIGHT_BLUE= RGBColor(0x1B, 0x98, 0xE0)
LIGHT_GRAY = RGBColor(0xE0, 0xE1, 0xDD)
```

### 方案 C：中国红
```python
DARK_RED   = RGBColor(0x8B, 0x00, 0x00)
CREAM      = RGBColor(0xF5, 0xF0, 0xE8)
GOLD       = RGBColor(0xD4, 0xA5, 0x74)
```

---

## 二、核心布局模板

### 1. 封面页
```python
def make_cover(prs, title, subtitle, author):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局
    
    # 深色满背景
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DEEP_NAVY
    bg.line.fill.background()
    
    # 金色装饰边框
    border = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(0.3),
        prs.slide_width - Inches(0.6), prs.slide_height - Inches(0.6))
    border.fill.background()
    border.line.color.rgb = GOLD
    border.line.width = Pt(2)
    
    # 大标题
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.color.rgb = CREAM
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(18)
    p2.font.color.rgb = GOLD
    p2.alignment = PP_ALIGN.CENTER
    
    # 底部金色装饰条
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2), Inches(5.5), Inches(6), Pt(3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()
```

### 2. 内容页（标题栏 + 双栏卡片）
```python
def make_content_slide(prs, title, left_items, right_items):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 标题栏（深蓝色）
    title_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.3))
    title_bar.fill.solid()
    title_bar.fill.fore_color.rgb = NAVY
    title_bar.line.fill.background()
    
    # 标题文字
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
    p = txBox.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.color.rgb = CREAM
    p.font.bold = True
    
    # 左栏卡片
    left_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(0.5), Inches(1.8), Inches(4.2), Inches(4.5))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = PARCHMENT
    left_card.line.fill.background()
    
    # 右栏卡片
    right_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(5.3), Inches(1.8), Inches(4.2), Inches(4.5))
    right_card.fill.solid()
    right_card.fill.fore_color.rgb = PARCHMENT
    right_card.line.fill.background()
    
    # 填充内容（左右各 3-4 个要点）
    for card, items in [(left_card, left_items), (right_card, right_items)]:
        txBox = slide.shapes.add_textbox(card.left + Inches(0.3), card.top + Inches(0.3),
            card.width - Inches(0.6), card.height - Inches(0.6))
        tf = txBox.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(14)
            p.font.color.rgb = NAVY
            p.space_before = Pt(6)
```

### 3. 时间线页
```python
def make_timeline(prs, title, events):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # ... 标题栏同上 ...
    
    for i, event in enumerate(events):
        y = Inches(1.8) + Inches(i * 0.8)
        
        # 左侧金色竖条
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
            Inches(0.8), y, Pt(4), Inches(0.6))
        bar.fill.solid()
        bar.fill.fore_color.rgb = GOLD
        bar.line.fill.background()
        
        # 日期
        date_box = slide.shapes.add_textbox(Inches(1.1), y, Inches(1.2), Inches(0.3))
        p = date_box.text_frame.paragraphs[0]
        p.text = event['date']
        p.font.size = Pt(12)
        p.font.color.rgb = GOLD
        p.font.bold = True
        
        # 标题 + 描述
        desc_box = slide.shapes.add_textbox(Inches(2.5), y, Inches(6.5), Inches(0.6))
        tf = desc_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = event['title']
        p.font.size = Pt(16)
        p.font.color.rgb = NAVY
        p.font.bold = True
        p2 = tf.add_paragraph()
        p2.text = event['desc']
        p2.font.size = Pt(12)
        p2.font.color.rgb = GRAY
```

### 4. 结语页
```python
def make_ending(prs, quote, author):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # 同封面风格，居中引文
    # ...
    txBox = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(7), Inches(2))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f'"{quote}"'
    p.font.size = Pt(24)
    p.font.color.rgb = CREAM
    p.font.italic = True
    p.alignment = PP_ALIGN.CENTER
```

---

## 三、完整工作流程

```
1. 确定主题和页数
2. 写大纲（每页的类型和内容）
3. 选择配色方案
4. 用模板生成 Python 脚本
5. 执行脚本生成 .pptx
6. 检查输出文件
```

### 生成脚本模板
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# 1. 封面
make_cover(prs, "主标题", "副标题", "作者")

# 2-N. 内容页
make_content_slide(prs, "标题", ["要点1", "要点2"], ["要点3", "要点4"])

# N+1. 时间线
make_timeline(prs, "发展历程", [
    {"date": "2024", "title": "事件1", "desc": "描述"},
])

# 结语
make_ending(prs, "结束语", "出处")

prs.save("output.pptx")
```

---

## 四、关键经验（踩坑总结）

### ✅ 必须做
| 项目 | 说明 |
|------|------|
| 用 `slide_layouts[6]`（空白） | 最灵活，不受默认占位符限制 |
| `shape.line.fill.background()` | 去掉默认蓝色边框 |
| `text_frame.word_wrap = True` | 文字自动换行 |
| 在 paragraph 上设 alignment | 不是 text_frame |
| 每页 6-8 行要点 | 信息密度适中 |
| 先写大纲再写代码 | 避免返工 |

### ❌ 不要做
| 项目 | 原因 |
|------|------|
| 用默认 layout | 占位符位置固定，难调 |
| 堆太多字 | 视觉疲劳，重点不突出 |
| 用太多种字体 | 不专业 |
| 忘记 `line.fill.background()` | 默认蓝边框很丑 |

### 常见坑
| 问题 | 解决方案 |
|------|----------|
| 形状默认有蓝色边框 | `shape.line.fill.background()` |
| 文字不换行 | `text_frame.word_wrap = True` |
| 居中不生效 | 在 `paragraph` 上设 `alignment` |
| 中文字体方块 | 用 `Microsoft YaHei` 或 `SimHei` |
| 段落间距太大 | `paragraph.space_before = Pt(6)` |
| 矩形重叠遮挡 | 注意 z-order，后添加的在上层 |

---

## 五、性能指标
| 指标 | 数值 |
|------|------|
| 生成速度 | < 1 秒/页 |
| 文件大小 | 50-100KB（纯形状，无图片） |
| 支持的最大页数 | 无限制 |
| 中文字体兼容性 | Microsoft YaHei 最佳 |

## 六、输出路径
```python
prs.save("/workspace/repo/left/output.pptx")  # 用户指定目录
```
