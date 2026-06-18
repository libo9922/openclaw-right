# GAME 项目 — 暗黑地牢 · AI Dungeon Master

> 一个基于 AI 的文字 RPG 地牢冒险游戏，Hermes 作为剧情大脑，nanobot 作为游戏引擎。

## 文件结构
```
game/
├── game.js           # 主入口（Node.js，182 行）
├── src/game.ts       # TypeScript 源码（225 行）
├── package.json      # 依赖：nanobot-agent-sdk
├── save.json         # 存档文件
└── node_modules/
```

## 核心架构

```
┌──────────────────────────────────┐
│         nanobot-agent-sdk         │
│    (游戏引擎：状态、存档、循环)     │
├──────────────────────────────────┤
│           game.js / game.ts       │
│  ┌─────────┐  ┌────────────────┐ │
│  │ 游戏状态  │  │  Hermes AI     │ │
│  │ hero     │  │  (剧情生成)     │ │
│  │ location │  │  NPC对话       │ │
│  │ floor    │  │  战斗判定       │ │
│  │ inventory│  │  物品描述       │ │
│  └─────────┘  └────────────────┘ │
└──────────────────────────────────┘
         │
    ┌────▼────┐
    │ 存档系统 │
    │ save.json│
    └─────────┘
```

## 游戏状态
```typescript
interface GameState {
  hero: {
    name: string
    hp: number; maxHp: number
    attack: number; defense: number
    gold: number
    inventory: string[]
    level: number; xp: number
  }
  location: string
  floor: number
  history: string[]
  alive: boolean
}
```

## 玩法
1. 玩家输入自然语言指令（如"向前走"、"攻击怪物"、"打开宝箱"）
2. nanobot 处理游戏循环和状态管理
3. Hermes AI 生成剧情描述、NPC 对话、战斗结果
4. 游戏状态实时更新并可存档

## 运行
```bash
cd /workspace/repo/game
npm install
node game.js
```

## 技术栈
- **Runtime**: Node.js
- **AI 引擎**: Hermes (通过 nanobot-agent-sdk 调用)
- **语言**: JavaScript + TypeScript
- **存档**: JSON 文件

## 适用场景
- AI 驱动的文字冒险游戏
- nanobot-agent-sdk 使用示例
- Hermes AI 集成参考
