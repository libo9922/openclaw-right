/**
 * Hermes MCP Server - 地牢冒险的"灵魂"
 * 负责：剧情生成、NPC对话、战斗判定、物品描述
 */

import { createAgent } from 'nanobot-agent-sdk'
import * as readline from 'readline'

// 游戏状态
interface GameState {
  hero: {
    name: string
    hp: number
    maxHp: number
    attack: number
    defense: number
    gold: number
    inventory: string[]
    level: number
    xp: number
  }
  location: string
  floor: number
  storySoFar: string[]
  alive: boolean
}

const INITIAL_STATE: GameState = {
  hero: {
    name: '冒险者',
    hp: 100,
    maxHp: 100,
    attack: 15,
    defense: 5,
    gold: 20,
    inventory: ['铁剑', '面包x3'],
    level: 1,
    xp: 0,
  },
  location: '地牢入口',
  floor: 1,
  storySoFar: [],
  alive: true,
}

// Hermes MCP - 故事引擎
const HERMES_MCP = {
  storyEngine: {
    type: 'stdio' as const,
    command: '/opt/hermes-venv/bin/hermes',
    args: [
      '-z',
      `你是地下城主(Dungeon Master)。你运行一个文字冒险游戏。
规则：
1. 玩家会告诉你他们的行动，你推进剧情
2. 每次回复包含：剧情描述、战斗结果（如有）、获得物品（如有）
3. 用🎲表示骰子判定，⚔️表示战斗，💰表示获得金币，❤️表示生命
4. 风格：暗黑幽默，像《黑暗之魂》遇上《猴岛小英雄》
5. 每次回复控制在150字以内，保持节奏
6. 死亡要写得很有仪式感
7. 给玩家2-4个选项，但允许自由行动`,
    ],
  },
}

async function main() {
  console.log(`
╔══════════════════════════════════════════════╗
║        ⚔️  暗黑地牢 · AI Dungeon Master  🐉    ║
║                                              ║
║   powered by nanobot + hermes                ║
║   输入你的行动，或输入 "quit" 退出            ║
╚══════════════════════════════════════════════╝
  `)

  // 创建 nanobot agent，接 hermes MCP
  const agent = await createAgent({
    model: 'claude-sonnet-4-20250514',
    assistant: {
      enabled: true,
      id: 'dungeon-master',
      name: '暗黑地牢',
      proactive: false,
    },
    tools: { type: 'preset', preset: 'operations' },
    mcpServers: HERMES_MCP,
    onEvent(event) {
      if (event.type === 'tool_result') {
        // 打印游戏事件
        console.log('\n🎲 事件:', event.result?.text || event.result)
      }
    },
  })

  let state: GameState = { ...INITIAL_STATE }

  // 读取存档（如有）
  try {
    const fs = await import('fs')
    const saveData = fs.readFileSync('./save.json', 'utf-8')
    state = JSON.parse(saveData)
    console.log('📂 读取存档成功！')
    console.log(`   ${state.hero.name} | ❤️ ${state.hero.hp}/${state.hero.maxHp} | ⚔️ ${state.hero.attack} | 🛡️ ${state.hero.defense} | 💰 ${state.hero.gold}`)
    console.log(`   📍 ${state.location} | 第${state.floor}层\n`)
  } catch {
    console.log('✨ 开始新的冒险...\n')
  }

  // 开场白
  if (state.storySoFar.length === 0) {
    const intro = await agent.run(`
      游戏开始。玩家刚进入地牢入口。描述环境，给玩家3-4个选择。
      玩家状态：${JSON.stringify(state.hero)}
    `)
    console.log(intro.text)
    state.storySoFar.push(intro.text)
  }

  // 主循环
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })

  const ask = () => {
    rl.question('\n> 你的行动: ', async (input) => {
      const trimmed = input.trim()

      if (trimmed === 'quit' || trimmed === 'exit') {
        // 存档
        const fs = await import('fs')
        fs.writeFileSync('./save.json', JSON.stringify(state, null, 2))
        console.log('\n💾 游戏已存档。下次再见，冒险者...\n')
        rl.close()
        return
      }

      if (trimmed === 'status' || trimmed === 's') {
        const h = state.hero
        console.log(`
┌─────────────────────────┐
│  ${h.name}  Lv.${h.level}
│  ❤️  ${h.hp}/${h.maxHp}  ⚔️ ${h.attack}  🛡️ ${h.defense}
│  💰 ${h.gold}g  ✨ ${h.xp}xp
│  🎒 ${h.inventory.join(', ') || '空'}
│  📍 ${state.location} · 第${state.floor}层
└─────────────────────────┘`)
        ask()
        return
      }

      // 发送给 agent
      const prompt = `
        当前游戏状态：${JSON.stringify(state)}
        玩家行动：${trimmed}
        
        请作为地下城主回应：
        1. 描述发生了什么
        2. 如果有战斗，判定结果（基于玩家属性）
        3. 更新状态（hp变化、获得物品、金币等）
        4. 给出下一步选择
        
        回复格式：
        [故事]
        [状态变化: JSON]
      `

      try {
        const response = await agent.run(prompt)
        console.log('\n' + response.text)

        // 尝试从回复中提取状态变化
        const stateMatch = response.text.match(/\[状态变化:\s*(\{.*?\})\]/s)
        if (stateMatch) {
          try {
            const changes = JSON.parse(stateMatch[1])
            if (changes.hp !== undefined) state.hero.hp = Math.max(0, Math.min(state.hero.maxHp, state.hero.hp + changes.hp))
            if (changes.gold !== undefined) state.hero.gold += changes.gold
            if (changes.xp !== undefined) {
              state.hero.xp += changes.xp
              // 升级判定
              const xpNeeded = state.hero.level * 100
              if (state.hero.xp >= xpNeeded) {
                state.hero.level++
                state.hero.maxHp += 20
                state.hero.hp = state.hero.maxHp
                state.hero.attack += 5
                state.hero.defense += 3
                state.hero.xp -= xpNeeded
                console.log(`\n🎉 升级！现在是 Lv.${state.hero.level}！`)
              }
            }
            if (changes.item) state.hero.inventory.push(changes.item)
            if (changes.removeItem) {
              const idx = state.hero.inventory.indexOf(changes.removeItem)
              if (idx !== -1) state.hero.inventory.splice(idx, 1)
            }
            if (changes.location) state.location = changes.location
            if (changes.floor) state.floor = changes.floor
          } catch { /* 状态解析失败，忽略 */ }
        }

        // 死亡判定
        if (state.hero.hp <= 0) {
          state.alive = false
          console.log('\n💀 你死了。输入 "quit" 退出，或重新开始。')
          state = { ...INITIAL_STATE }
          state.storySoFar = []
          console.log('\n✨ 新的冒险开始了...\n')
          const newIntro = await agent.run('玩家重生在地牢入口。简短描述环境，给3个选择。')
          console.log(newIntro.text)
        }

        state.storySoFar.push(response.text)
        // 只保留最近20条
        if (state.storySoFar.length > 20) state.storySoFar = state.storySoFar.slice(-20)
      } catch (err) {
        console.log('⚠️ 发生了意外... 地牢似乎在震动。再试一次？')
      }

      ask()
    })
  }

  ask()
}

main().catch(console.error)
