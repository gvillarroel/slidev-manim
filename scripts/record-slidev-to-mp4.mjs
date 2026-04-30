#!/usr/bin/env node
import { chromium } from 'playwright'
import { spawn } from 'node:child_process'
import { mkdtemp, rm, mkdir, stat, rename, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve, dirname } from 'node:path'

const usage = `Usage: scripts/record-slidev-to-mp4.mjs <deck.md> [output.mp4]

Records the live Slidev presentation in Chromium, so CSS animations, transitions,
iframes, videos, and click reveals are captured as they run.

Per-slide timing can be set with Slidev frontmatter:
  ---
  recordWait: 5000
  ---

Environment variables:
  SLIDEV_URL        Already-running Slidev URL. Default: http://127.0.0.1:3030
  SIZE              Browser/video size. Default: 1920x1080
  FPS               Output MP4 frame rate. Default: 30
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
const slidevUrl = process.env.SLIDEV_URL || 'http://127.0.0.1:3030'
const stepWaitMs = Number(process.env.STEP_WAIT_MS || 1200)
const introWaitMs = Number(process.env.INTRO_WAIT_MS || 1000)
const maxSteps = Number(process.env.MAX_STEPS || 200)
const keepWebm = process.env.KEEP_WEBM === '1' || process.env.KEEP_WEBM === 'true'
const slideWaits = parseSlideRecordWaits(await readFile(deckPath, 'utf8'))
const url = slidevUrl
const tmp = await mkdtemp(join(tmpdir(), 'slidev-record-'))
const videoDir = join(tmp, 'video')
await mkdir(videoDir, { recursive: true })

let browser

function spawnCommand(command, args, options = {}) {
  return spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'], ...options })
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

function readRecordWait(frontmatter) {
  const match = frontmatter.match(/^recordWait\s*:\s*['"]?([0-9]+(?:\.[0-9]+)?)['"]?\s*$/m)
  return match ? Number(match[1]) : undefined
}

function looksLikeFrontmatter(chunk) {
  const text = chunk.trim()
  return text.length > 0 && !text.includes('\n#') && /^[A-Za-z0-9_-]+\s*:/m.test(text)
}

function parseSlideRecordWaits(markdown) {
  let body = markdown.replace(/\r\n/g, '\n')
  const waits = new Map()
  const topFrontmatter = body.match(/^---\n([\s\S]*?)\n---\n?/)
  if (topFrontmatter) {
    const wait = readRecordWait(topFrontmatter[1])
    if (Number.isFinite(wait)) waits.set(1, wait)
    body = body.slice(topFrontmatter[0].length)
  }

  const chunks = body.split(/^---\s*$/m)
  let slide = 1
  if (chunks[0]?.trim()) slide += 1

  for (let i = 1; i < chunks.length; i += 1) {
    if (looksLikeFrontmatter(chunks[i]) && i + 1 < chunks.length) {
      const wait = readRecordWait(chunks[i])
      if (Number.isFinite(wait)) waits.set(slide, wait)
      slide += 1
      i += 1
    } else if (chunks[i]?.trim()) {
      slide += 1
    }
  }

  return waits
}

function waitForSlide(state) {
  const slide = Number(state.current ?? state.slideNo)
  return (Number.isFinite(slide) && slideWaits.get(slide)) || stepWaitMs
}

async function pageState(page) {
  return page.evaluate(() => {
    const path = location.pathname + location.search + location.hash
    const current = window.__slidev__?.nav?.currentPage
    const slideNo = window.__slidev__?.nav?.currentSlideNo
    const clicks = window.__slidev__?.nav?.clicks
    const total = window.__slidev__?.nav?.total
    const hasNext = window.__slidev__?.nav?.hasNext
    return { path, current, slideNo, clicks, total, hasNext }
  })
}

try {
  browser = await chromium.launch({ headless: true })

  // Wait for Slidev before creating the recorded context, otherwise the output
  // video includes several seconds of blank startup time.
  const probeContext = await browser.newContext({ viewport: { width, height } })
  const probePage = await probeContext.newPage()
  await waitForServer(probePage)
  await probeContext.close()

  const context = await browser.newContext({
    viewport: { width, height },
    recordVideo: { dir: videoDir, size: { width, height } },
  })
  const page = await context.newPage()
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForTimeout(introWaitMs)

  let previous = await pageState(page)
  let stableAtEnd = 0
  let steps = 0

  await page.waitForTimeout(waitForSlide(previous))

  while (steps < maxSteps) {
    await page.keyboard.press('ArrowRight')
    steps += 1
    const current = await pageState(page)

    const changed = JSON.stringify(current) !== JSON.stringify(previous)
    const currentSlide = Number(current.current ?? current.slideNo)
    const atKnownEnd = current.hasNext === false || (Number.isFinite(currentSlide) && Number.isFinite(current.total)
      && currentSlide >= current.total
      && (current.clicks == null || current.clicks >= 0))

    if (!changed) {
      stableAtEnd += 1
    } else {
      stableAtEnd = 0
    }

    previous = current

    // One unchanged ArrowRight at the known last slide is enough; otherwise use
    // two unchanged presses as a generic safety net.
    if ((atKnownEnd && stableAtEnd >= 1) || stableAtEnd >= 2) break

    await page.waitForTimeout(waitForSlide(current))
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
  if (!keepWebm) await rm(tmp, { recursive: true, force: true }).catch(() => {})
}
