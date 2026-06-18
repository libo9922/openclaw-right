# GLOBE 项目 — AI 地球

> 一个 3D 地球可视化应用，集成了 Hermes AI 对话能力，点击地球上的国家可获取 AI 生成的信息。

## 文件结构
```
globe/
├── server.js           # Node.js HTTP 服务器（98 行）
├── package.json
└── public/
    └── index.html      # 前端页面（228 行）
```

## 核心功能
- **3D 地球渲染**: Canvas 绘制旋转地球
- **国家交互**: 点击国家弹出信息面板
- **AI 对话**: 通过 Hermes 获取国家信息
- **玻璃拟态 UI**: 半透明面板 + 模糊效果

## 架构

```
┌─────────────────────────────────┐
│          浏览器 (index.html)      │
│  ┌──────────┐  ┌──────────────┐ │
│  │ 3D 地球   │  │ 信息面板      │ │
│  │ Canvas    │  │ 玻璃拟态      │ │
│  └──────────┘  └──────────────┘ │
└───────────────┬─────────────────┘
                │ HTTP API
┌───────────────▼─────────────────┐
│        server.js (Node.js)       │
│  ┌──────────────────────────┐  │
│  │  askHermes(prompt)       │  │
│  │  ├── execFileSync        │  │
│  │  │   (hermes CLI)        │  │
│  │  └── callDirectAPI       │  │
│  │      (agentrouter.org)   │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

## 技术特点
- **单文件前端**: index.html 包含所有 CSS + JS
- **双层 AI 调用**: 优先 hermes CLI，失败则直连 API
- **execFileSync**: 避免 shell 注入
- **超时控制**: 28 秒超时防止卡死

## 运行
```bash
cd /workspace/repo/globe
npm install
node server.js
# 访问 http://localhost:3456
```

## 配色方案
```css
背景: #000 (纯黑)
面板: rgba(6,10,24,.95) + backdrop-filter:blur(24px)
标题渐变: #4a9eff → #a855f7 → #ec4899
边框: rgba(100,180,255,.2)
```

## 适用场景
- 3D 数据可视化
- AI 集成 Web 应用
- Node.js 全栈示例
- 玻璃拟态 UI 参考
