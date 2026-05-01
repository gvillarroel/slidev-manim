import { mkdirSync, rmSync, copyFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = {
    url: "http://127.0.0.1:4173/",
    outputVideo: resolve("videos/red-dot-radial-focus-spa/red-dot-radial-focus-spa.webm"),
    screenshotDir: resolve("videos/red-dot-radial-focus-spa/screenshots"),
    summary: resolve("videos/red-dot-radial-focus-spa/browser-validation.json"),
    width: 1600,
    height: 900,
    durationMs: 32500,
  };

  for (let index = 2; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!value) break;
    if (key === "--url") args.url = value;
    if (key === "--output-video") args.outputVideo = resolve(value);
    if (key === "--screenshot-dir") args.screenshotDir = resolve(value);
    if (key === "--summary") args.summary = resolve(value);
    if (key === "--width") args.width = Number(value);
    if (key === "--height") args.height = Number(value);
    if (key === "--duration-ms") args.durationMs = Number(value);
  }

  return args;
}

const args = parseArgs(process.argv);
const captures = [
  { file: "01-appearance.png", at: 4200 },
  { file: "02-fanout.png", at: 10500 },
  { file: "03-focus.png", at: 18000 },
  { file: "04-rotation.png", at: 24500 },
  { file: "05-resolution.png", at: 32000 },
];
const mobileCapture = {
  file: "mobile-resolution.png",
  at: 32000,
  width: 430,
  height: 932,
};

rmSync(args.screenshotDir, { recursive: true, force: true });
mkdirSync(args.screenshotDir, { recursive: true });
mkdirSync(dirname(args.outputVideo), { recursive: true });

const videoTempDir = join(tmpdir(), `red-dot-radial-focus-${Date.now()}-${Math.round(Math.random() * 1e9)}`);
mkdirSync(videoTempDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: args.width, height: args.height },
  deviceScaleFactor: 1,
  recordVideo: {
    dir: videoTempDir,
    size: { width: args.width, height: args.height },
  },
});

const consoleMessages = [];
const pageErrors = [];
const page = await context.newPage();
const pageVideo = page.video();

page.on("console", (message) => {
  if (message.type() === "error" || message.type() === "warning") {
    consoleMessages.push({
      type: message.type(),
      text: message.text(),
    });
  }
});

page.on("pageerror", (error) => {
  pageErrors.push(error.message);
});

await page.goto(args.url, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => Boolean(window.__RED_DOT_READY));
await page.evaluate(() => window.__RED_DOT_APP?.reset?.());
await page.waitForTimeout(80);

let lastCapture = 0;
for (const capture of captures) {
  const delay = Math.max(0, capture.at - lastCapture);
  if (delay > 0) {
    await page.waitForTimeout(delay);
  }
  lastCapture = capture.at;
  await page.screenshot({
    path: join(args.screenshotDir, capture.file),
  });
}

if (args.durationMs > lastCapture) {
  await page.waitForTimeout(args.durationMs - lastCapture);
}

const finalState = await page.evaluate(() => window.__RED_DOT_APP?.getState?.() ?? null);
await context.close();

const mobileContext = await browser.newContext({
  viewport: { width: mobileCapture.width, height: mobileCapture.height },
  deviceScaleFactor: 2,
});
const mobilePage = await mobileContext.newPage();
await mobilePage.goto(args.url, { waitUntil: "domcontentloaded" });
await mobilePage.waitForFunction(() => Boolean(window.__RED_DOT_READY));
await mobilePage.evaluate((at) => {
  window.__RED_DOT_APP?.pause?.();
  window.__RED_DOT_APP?.seek?.(at);
}, mobileCapture.at);
await mobilePage.waitForTimeout(80);
await mobilePage.screenshot({
  path: join(args.screenshotDir, mobileCapture.file),
});
await mobileContext.close();

const recordedVideo = await pageVideo.path();
copyFileSync(recordedVideo, args.outputVideo);
await browser.close();
rmSync(videoTempDir, { recursive: true, force: true });

const summary = {
  url: args.url,
  width: args.width,
  height: args.height,
  durationMs: args.durationMs,
  captures,
  mobileCapture,
  consoleMessages,
  pageErrors,
  finalState,
};

writeFileSync(args.summary, `${JSON.stringify(summary, null, 2)}\n`, "utf-8");

if (consoleMessages.some((entry) => entry.type === "error") || pageErrors.length > 0) {
  process.exitCode = 1;
}
