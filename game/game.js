#!/usr/bin/env node
/**
 * ⚔️ 暗黑地牢 · AI Dungeon Master
 * 
 * nanobot = 游戏引擎（状态、存档、循环）
 * hermes  = 剧情大脑（故事生成、NPC、战斗）
 */

const { execSync } = require('child_process')
const readline = require('readline')
const fs = require('fs')

const SAVE_FILE = __dirname + '/save.json'

// ── 游戏状态 ──
const INITIAL_STATE = {
  hero: {
    name: '冒险者',
    hp: 100, maxHp: 100,
    attack: 15, defense: 5,
    gold: 20,
    inventory: ['铁剑', '面包x3'],
    level: 1, xp: 0,
  },
  location: '地牢入口',
  floor: 1,
  history: [],
  alive: true,
}

// ── 调用 hermes 生成剧情 ──
function askHermes(gameState, playerAction) {
  const prompt = `暗黑幽默地下城主。玩家${playerAction}。状态:${JSON.stringify(gameState.hero)}。简短描述(80字)，给2-3选项。有变化末行写STATE:{"hp":数字,"gold":数字}`

  try {
    const result = execSync(
      `timeout 25 /opt/hermes-venv/bin/hermes -z "${prompt.replace(/["\\]/g, '\\$&')}" 2>/dev/null`,
      { encoding: 'utf-8', timeout: 30000 }
    ).trim()
    if (!result || result.includes('no final response')) return fallbackStory(playerAction, gameState)
    return result
  } catch (e) {
    // hermes 挂了，用内置 fallback
    return fallbackStory(playerAction, gameState)
  }
}

// ── 内置 fallback（hermes 不可用时） ──
function fallbackStory(action, state) {
  const stories = [
    `你小心翼翼地${action}。黑暗中传来低沉的笑声...\n前方出现一条岔路。\n  A) 左边 - 传来水滴声\n  B) 右边 - 隐约有火光`,
    `你鼓起勇气${action}。突然！一只哥布林跳了出来！\n⚔️ 哥布林朝你扑来！\n  A) 拔剑迎战\n  B) 丢面包引开它\n  C) 转身就跑`,
    `你${action}。地上发现一个宝箱！\n💰 打开后获得 15金币！\n  A) 继续前进\n  B) 搜索周围`,
    `你${action}。一阵寒风吹过...\n❤️ -10 HP（陷阱！）\n  A) 包扎伤口继续\n  B) 原路返回`,
    `你${action}。遇到一个神秘商人。\n"要买点什么吗？"\n  A) 治疗药水 30g\n  B) 钢剑 (+5攻击) 50g\n  C) 不买，继续走`,
  ]
  const pick = stories[Math.floor(Math.random() * stories.length)]

  // 随机状态变化
  const hpChange = Math.random() > 0.7 ? -Math.floor(Math.random() * 20) : 0
  const goldChange = Math.random() > 0.5 ? Math.floor(Math.random() * 20) : 0

  return pick + (hpChange || goldChange ? `\nSTATE:{"hp":${hpChange},"gold":${goldChange}}` : '')
}

// ── 解析状态变化 ──
function parseStateChange(text) {
  const match = text.match(/STATE:\s*(\{.*?\})/)
  if (!match) return null
  try { return JSON.parse(match[1]) } catch { return null }
}

// ── 显示状态 ──
function showStatus(hero) {
  console.log(`
┌──────────────────────────────┐
│  ${hero.name.padEnd(10)} Lv.${hero.level}
│  ❤️  ${String(hero.hp).padStart(3)}/${hero.maxHp}  ⚔️ ${hero.attack}  🛡️ ${hero.defense}
│  💰 ${hero.gold}g  ✨ ${hero.xp}xp
│  🎒 ${hero.inventory.join(', ') || '空'}
└──────────────────────────────┘`)
}

// ── 主程序 ──
async function main() {
  console.log(`
╔════════════════════════════════════════════╗
║      ⚔️  暗黑地牢 · AI Dungeon Master  🐉   ║
║                                            ║
║   nanobot 🤝 hermes                        ║
║   输入行动，或 quit 退出 | status 看状态    ║
╚════════════════════════════════════════════╝`)

  // 读存档
  let state
  try {
    state = JSON.parse(fs.readFileSync(SAVE_FILE, 'utf-8'))
    console.log('\n📂 读取存档成功！')
    showStatus(state.hero)
  } catch {
    state = JSON.parse(JSON.stringify(INITIAL_STATE))
    console.log('\n✨ 开始新的冒险...\n')
    // 开场
    const intro = askHermes(state, '进入地牢入口')
    console.log('\n' + intro)
    state.history.push(intro)
  }

  // 主循环
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })

  const prompt = () => {
    rl.question('\n> ', async (input) => {
      const action = input.trim()

      if (action === 'quit' || action === 'q') {
        fs.writeFileSync(SAVE_FILE, JSON.stringify(state, null, 2))
        console.log('\n💾 已存档。下次再见，冒险者...\n')
        rl.close()
        return
      }

      if (action === 'status' || action === 's') {
        showStatus(state.hero)
        prompt()
        return
      }

      // hermes 生成剧情
      const story = askHermes(state, action)
      console.log('\n' + story.split('STATE:')[0].trim())

      // 解析状态变化
      const changes = parseStateChange(story)
      if (changes) {
        if (changes.hp) {
          state.hero.hp = Math.max(0, Math.min(state.hero.maxHp, state.hero.hp + changes.hp))
        }
        if (changes.gold) state.hero.gold += changes.gold
        if (changes.item) state.hero.inventory.push(changes.item)
        if (changes.removeItem) {
          const i = state.hero.inventory.indexOf(changes.removeItem)
          if (i !== -1) state.hero.inventory.splice(i, 1)
        }
        if (changes.location) state.location = changes.location
        if (changes.floor) state.floor = changes.floor
        if (changes.xp) {
          state.hero.xp += changes.xp
          if (state.hero.xp >= state.hero.level * 100) {
            state.hero.level++
            state.hero.maxHp += 20
            state.hero.hp = state.hero.maxHp
            state.hero.attack += 5
            state.hero.defense += 3
            state.hero.xp -= (state.hero.level - 1) * 100
            console.log(`\n🎉 升级！Lv.${state.hero.level}！`)
          }
        }
      }

      // 死亡
      if (state.hero.hp <= 0) {
        console.log('\n💀 你死了。但死神觉得你太有趣了，又把你踢了回来。')
        state.hero.hp = Math.floor(state.hero.maxHp * 0.3)
        state.hero.gold = Math.floor(state.hero.gold * 0.5)
        console.log(`❤️ 复活！HP: ${state.hero.hp}，但丢了一半金币。`)
      }

      // 自动存档
      fs.writeFileSync(SAVE_FILE, JSON.stringify(state, null, 2))

      state.history.push(story)
      if (state.history.length > 30) state.history = state.history.slice(-30)

      prompt()
    })
  }

  prompt()
}

main()
