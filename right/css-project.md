# CSS 项目 — Vibe Keyboard

> 一个纯 CSS + HTML 实现的赛博朋克风格虚拟键盘界面。

## 文件
- `vibe-keyboard.html` — 单文件完整应用（514 行）

## 技术特点
- **纯前端**: 无依赖，单 HTML 文件即可运行
- **赛博朋克美学**: 深色背景 + 紫色/青色渐变 + 玻璃拟态
- **CSS 变量系统**: 通过 `--bg`, `--panel`, `--accent` 等变量统一配色
- **响应式布局**: 适配不同屏幕尺寸
- **键盘交互**: 支持按键高亮、音效反馈

## 配色方案
```css
--bg: #0a0a14;        /* 深空背景 */
--panel: #14142400;    /* 半透明面板 */
--accent: #7c5cff;     /* 主紫色 */
--accent2: #00e0c6;    /* 青色强调 */
--text: #e8e8f0;       /* 浅色文字 */
--muted: #8a8aa0;      /* 次要文字 */
```

## 运行
```bash
# 直接浏览器打开
open vibe-keyboard.html

# 或用任意 HTTP 服务
python3 -m http.server 8080 -d /workspace/repo/css
```

## 适用场景
- 前端 CSS 技术演示
- 虚拟键盘 UI 组件
- 赛博朋克风格参考
