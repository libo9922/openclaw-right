const http = require('http')
const fs = require('fs')
const path = require('path')
const { execFileSync } = require('child_process')

const PORT = 3456

// 调用 hermes（用 execFileSync 避免 shell 注入）
function askHermes(prompt) {
  try {
    const result = execFileSync(
      '/opt/hermes-venv/bin/hermes',
      ['-z', prompt],
      { encoding: 'utf-8', timeout: 28000, stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim()
    if (!result || result.includes('no final response')) return null
    return result
  } catch (e) {
    // fallback: 直接调 API
    return callDirectAPI(prompt)
  }
}

// 直接调 agentrouter.org 作为 fallback
function callDirectAPI(prompt) {
  try {
    const https = require('https')
    const data = JSON.stringify({
      model: 'gpt-5.5',
      messages: [
        { role: 'system', content: '用中文简短回答(80字以内)，风格轻松有趣。' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 200,
    })
    const url = new URL('https://agentrouter.org/v1/chat/completions')
    // 同步请求用 child_process
    const result = execFileSync('curl', [
      '-s', '--connect-timeout', '8',
      '-X', 'POST', url.href,
      '-H', 'Authorization: Bearer sk-aFk…s8yB',
      '-H', 'Content-Type: application/json',
      '-d', data
    ], { encoding: 'utf-8', timeout: 15000 })
    const parsed = JSON.parse(result)
    return parsed.choices?.[0]?.message?.content || null
  } catch { return null }
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
}

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*')

  // API
  if (req.url.startsWith('/api/ask')) {
    const url = new URL(req.url, `http://localhost:${PORT}`)
    const q = url.searchParams.get('q') || ''
    const place = url.searchParams.get('place') || ''

    const prompt = place
      ? `用中文简短介绍${place}（80字以内），包含一个冷知识或趣闻，风格轻松有趣。`
      : `用中文简短回答（80字以内）：${q}`

    // 异步执行
    setImmediate(() => {
      const answer = askHermes(prompt)
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' })
      res.end(JSON.stringify({ answer: answer || '嗯...我的大脑短路了，换个地方试试？' }))
    })
    return
  }

  // 静态文件
  let filePath = req.url === '/' ? '/index.html' : req.url
  filePath = path.join(__dirname, 'public', filePath)
  const ext = path.extname(filePath)
  const mime = MIME[ext] || 'application/octet-stream'

  try {
    const data = fs.readFileSync(filePath)
    res.writeHead(200, { 'Content-Type': mime })
    res.end(data)
  } catch {
    res.writeHead(404)
    res.end('Not Found')
  }
})

server.listen(PORT, () => {
  console.log(`🌍 3D 地球已启动: http://localhost:${PORT}`)
})
