#!/usr/bin/env node
import { chromium } from 'playwright'
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { mkdtemp, rm, mkdir, stat, rename } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve, dirname } from 'node:path'

const usage = `Usage: scripts/record-slidev-to-mp4.mjs <deck.md> [output.mp4]

Records the live Slidev presentation in Chromium, so CSS animations, transitions,
iframes, videos, and click reveals are captured as they run.

Environment variables:
  SIZE              Browser/video size. Default: 1920x1080
  FPS               Output MP4 frame rate. Default: 30
  PORT              Slidev dev-server port. Default: 3030
  STEP_WAIT_MS      Wait after each navigation/click step. Default: 1200
  INTRO_WAIT_MS     Wait before first navigation. Default: 1000
  MAX_STEPS         Safety limit for ArrowRight steps. Default: 200
  KEEP_WEBM         Keep Playwright's raw .webm next to MP4 when 1. Default: 0

Examples:
  node scripts/record-slidev-to-mp4.mjs slides.md videos/deck.mp4
  STEP_WAIT_MS=2000 MAX_STEPS=80 npm run record:mp4 -- slides.md videos/deck.mp4
`

if (process.argv.includes('-h') || process.argv.includes('--help')) {
  console.log(usage)
  process.exit(0)
}

const deck = process.argv[2]
const out = process.argv[3] || 'deck.mp4'
if (!deck || process.argv.length > 4) {
  console.error(usage)
  process.exit(2)
}

const deckPath = resolve(deck)
await stat(deckPath).catch(() => {
  console.error(`Deck not found: ${deck}`)
  process.exit(1)
})

const size = process.env.SIZE || '1920x1080'
const [width, height] = size.split('x').map(Number)
if (!width || !height) {
  console.error('SIZE must look like 1920x1080')
  process.exit(1)
}

const fps = Number(process.env.FPS || 30)
const port = Number(process.env.PORT || 3030)
const stepWaitMs = Number(process.env.STEP_WAIT_MS || 1200)
const introWaitMs = Number(process.env.INTRO_WAIT_MS || 1000)
const maxSteps = Number(process.env.MAX_STEPS || 200)
const keepWebm = process.env.KEEP_WEBM === '1' || process.env.KEEP_WEBM === 'true'
const url = `http://127.0.0.1:${port}`
const tmp = await mkdtemp(join(tmpdir(), 'slidev-record-'))
const videoDir = join(tmp, 'video')
await mkdir(videoDir, { recursive: true })

let slidev
let browser

function spawnCommand(command, args, options = {}) {
  return spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'], ...options })
}

function findSlidevCommand() {
  if (process.platform !== 'win32' && existsSync(resolve('node_modules/.bin/slidev'))) {
    return [resolve('node_modules/.bin/slidev'), []]
  }
  if (process.platform === 'win32' && existsSync(resolve('node_modules/.bin/slidev.cmd'))) {
    return [resolve('node_modules/.bin/slidev.cmd'), []]
  }
  if (process.env.npm_execpath?.includes('pnpm')) {
    return [process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm', ['exec', 'slidev']]
  }
  return [process.platform === 'win32' ? 'npx.cmd' : 'npx', ['slidev']]
}

async function waitForServer(page, deadlineMs = 60000) {
  const started = Date.now()
  let lastError
  while (Date.now() - started < deadlineMs) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 3000 })
      return
    } catch (err) {
      lastError = err
      await page.waitForTimeout(500)
    }
  }
  throw lastError || new Error(`Timed out waiting for ${url}`)
}

async function pageState(page) {
  return page.evaluate(() => {
    const path = location.pathname + location.search + location.hash
    const nav = document.querySelector('[aria-label="Slide navigation"]')?.textContent || ''
    const body = document.body?.innerText || ''
    const current = window.__slidev__?.nav?.currentPage
    const clicks = window.__slidev__?.nav?.clicks
    const total = window.__slidev__?.nav?.total
    return { path, nav, current, clicks, total, bodyLength: body.length }
  })
}

try {
  const [slidevBin, prefixArgs] = findSlidevCommand()
  const command = slidevBin
  const args = [...prefixArgs, deckPath, '--remote=false', '--port', String(port)]
  slidev = spawnCommand(command, args, { cwd: process.cwd() })

  slidev.stdout.on('data', (chunk) => process.stderr.write(chunk))
  slidev.stderr.on('data', (chunk) => process.stderr.write(chunk))

  browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width, height },
    recordVideo: { dir: videoDir, size: { width, height } },
  })
  const page = await context.newPage()
  await waitForServer(page)
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForTimeout(introWaitMs)

  let previous = await pageState(page)
  let stableAtEnd = 0
  let steps = 0

  while (steps < maxSteps) {
    await page.keyboard.press('ArrowRight')
    steps += 1
    await page.waitForTimeout(stepWaitMs)
    const current = await pageState(page)

    const changed = JSON.stringify(current) !== JSON.stringify(previous)
    const atKnownEnd = Number.isFinite(current.current) && Number.isFinite(current.total)
      && current.current >= current.total
      && (current.clicks == null || current.clicks >= 0)

    if (!changed) {
      stableAtEnd += 1
    } else {
      stableAtEnd = 0
    }

    previous = current

    // Two unchanged ArrowRight presses is the most reliable generic signal that
    // Slidev has no more click reveals, transitions, or slides to advance.
    if (stableAtEnd >= 2 && (atKnownEnd || steps > 2)) break
  }

  await page.waitForTimeout(500)
  const video = page.video()
  await context.close()
  const webmPath = await video.path()
  await browser.close()
  browser = undefined

  await mkdir(dirname(resolve(out)), { recursive: true })
  const ffmpeg = spawnCommand('ffmpeg', [
    '-y',
    '-i', webmPath,
    '-r', String(fps),
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    resolve(out),
  ])
  ffmpeg.stdout.on('data', (chunk) => process.stderr.write(chunk))
  ffmpeg.stderr.on('data', (chunk) => process.stderr.write(chunk))
  const code = await new Promise((resolveCode) => ffmpeg.on('close', resolveCode))
  if (code !== 0) throw new Error(`ffmpeg exited with ${code}`)

  if (keepWebm) {
    await rename(webmPath, resolve(`${out}.webm`))
  }

  console.log(`Wrote ${out} after ${steps} navigation step(s).`)
} finally {
  if (browser) await browser.close().catch(() => {})
  if (slidev) slidev.kill('SIGTERM')
  if (!keepWebm) await rm(tmp, { recursive: true, force: true }).catch(() => {})
}
