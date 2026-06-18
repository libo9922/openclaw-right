# faker-agent 能力总览 — 会话间知识迁移

> 本文件记录 faker-agent 工作区已验证的能力、工具链和最佳实践。新会话读此文件即可快速上手。

---

## 🧠 Agent 基本信息

- **Agent ID**: `faker-agent`
- **身份**: Amma（faker 版），温暖友好的中文 AI 助手
- **Emoji**: 🐾
- **模型**: xiaomi-token-plan/mimo-v2.5-pro
- **工作区**: `/root/.openclaw/faker-agent/`
- **独立记忆**: 有自己的 MEMORY.md，不依赖主 agent

---

## 🛠️ 已验证的核心能力

### 1. AI 视频制作流水线 ⭐ 最强能力
- **完整流程**: 剧本 → AI 生图 → TTS 配音 → FFmpeg 合成 → 成品视频
- **关键技术**: Pollinations.ai 免费生图、Ken Burns 效果、动态时长计算
- **产出示例**: `video-project3/output/dawn_sword_ai.mp4`（20MB，11 场景有声视频）
- **详细文档**: → `right/VIDEO_PIPELINE_GUIDE.md`

### 2. Python 脚本编写 & 执行
- PIL/Pillow 图像处理和程序化绘图
- 网络请求（urllib, subprocess + curl）
- 文件 I/O 和批量处理
- 环境中已有: Python3, Pillow, 常用标准库

### 3. Shell 脚本 & FFmpeg
- Bash 脚本编写和执行
- FFmpeg 视频/音频处理（拼接、转码、滤镜、混合）
- FFprobe 媒体信息提取
- 环境中已有: ffmpeg, ffprobe, curl, python3

### 4. 文件操作
- 读写任意文件（read/write/edit 工具）
- 目录创建和管理
- 大文件处理（20MB+ 视频文件）

### 5. 网络搜索 & 抓取
- `web_search`: 搜索引擎查询
- `web_fetch`: 抓取网页内容

### 6. 图像分析
- `image` 工具: 分析图片内容、OCR、描述

### 7. 定时任务 & 提醒
- `cron` 工具: 创建定时任务、一次性提醒
- 支持 cron 表达式、时区设置

### 8. 会话管理
- 跨会话消息发送
- 子 agent 生成和管理
- 会话历史查询

### 9. TTS 语音合成
- **MiMo TTS API**: `mimo-v2.5-tts` 模型，支持多种声音（茉莉、冰糖、苏打等）
- **声音克隆**: `mimo-v2.5-tts-voiceclone`，voice 参数用 DataURL 格式
- 详见 → `right/session-capabilities.md`

### 10. 人声分离
- **轻量方案**: FFmpeg 带通滤波 + 降噪
- **专业方案**: Demucs（htdemucs），AMD GPU 跑 117 秒音频仅需 5 秒
- 详见 → `right/session-capabilities.md`

### 11. Bilibili 音频下载
- API 获取视频信息 → DASH 音频流 → 下载
- 必须带 Referer 头，否则 403
- 详见 → `right/session-capabilities.md`

### 12. 本地 LLM 推理
- **Qwen3-8B on AMD GPU**: vLLM + ROCm 部署
- 性能: 23.2 tok/s，显存 19.3 GiB
- 详见 → `right/README.md`

---

## 📁 工作区结构

```
/root/.openclaw/faker-agent/
├── AGENTS.md          # Agent 行为规则
├── SOUL.md            # 身份和人格定义
├── IDENTITY.md        # 名字、角色、Emoji
├── USER.md            # 用户信息
├── TOOLS.md           # 工具配置笔记
├── MEMORY.md          # 长期记忆
├── HEARTBEAT.md       # 心跳任务配置
├── BOOTSTRAP.md       # 首次启动引导（应删除）
├── workspace/         # 子工作区（含独立 AGENTS/SOUL/MEMORY）
├── video-project/     # v1 视频项目（星尘之梦）
├── video-project2/    # v2 视频项目（暗黑奇幻）
├── video-project3/    # v3 视频项目（破晓之剑）✅
└── right/             # 📖 知识文档目录（主目录: ~/workspace/right/）
    ├── CAPABILITIES_OVERVIEW.md  ← 你正在读的文件
    ├── VIDEO_PIPELINE_GUIDE.md   # 视频制作详细指南
    ├── session-capabilities.md   # TTS/人声分离/B站下载/多账号路由
    ├── README.md                 # Qwen3-8B AMD GPU 部署指南
    └── chat.py                   # Qwen3-8B 对话客户端
```

---

## 🔑 关键经验速查

### 环境信息
- **OS**: Linux 6.8.0-79-generic (x64)
- **Node**: v24.16.0
- **中文字体**: `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`
- **Python**: python3（含 Pillow）
- **FFmpeg**: 已安装，支持 libx264, aac

### 工具调用模式
```
exec → 执行 shell 命令（长时间任务用 yieldMs 或 background）
read → 读取文件内容
write → 创建/覆盖文件
edit → 精确编辑文件（oldText → newText 替换）
web_search → 搜索
web_fetch → 抓取网页
image → 分析图片
cron → 定时任务
sessions_spawn → 生成子 agent 处理长任务
```

### 长任务处理
- 耗时 > 10s 的命令: `exec` 加 `yieldMs` 或 `background:true`
- 复杂多步任务: 用 `sessions_spawn` 生成子 agent
- 避免轮询: 用 `sessions_yield` 等待子 agent 完成

### 文件路径注意
- 工作区根目录: `/root/.openclaw/faker-agent/`
- 写文件时自动创建父目录
- 相对路径基于工作区根目录

---

## ⚠️ 已知限制

1. **Memory search 不可用**: 索引元数据缺失，需运行 `openclaw memory index --force` 重建
2. **Pollinations.ai 速率限制**: 免费服务，需 sleep(2) 间隔 + 重试
3. **无浏览器工具**: 当前 capabilities=none，无法使用 browser-automation
4. **无 TTS 内置工具**: 需通过其他方式生成语音（如外部 API 或预生成）

---

## 📖 文档索引

| 文件 | 内容 |
|------|------|
| `right/CAPABILITIES_OVERVIEW.md` | 本文件 — 能力总览 |
| `right/VIDEO_PIPELINE_GUIDE.md` | AI 视频制作完整指南 |
| `right/session-capabilities.md` | TTS 语音合成、Bilibili 下载、人声分离、多账号路由等 |
| `right/README.md` | Qwen3-8B on AMD GPU (ROCm) 部署指南 |
| `right/chat.py` | Qwen3-8B 交互式对话客户端 |

---

*新会话启动后，读取 `right/` 目录下的文档即可快速继承已有能力。*

*最后更新: 2026-06-17*
