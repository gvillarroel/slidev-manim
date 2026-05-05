import { copyFileSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = {
    url: "http://127.0.0.1:4173/",
    outputVideo: resolve("videos/red-dot-bloom-spa/red-dot-bloom-spa.webm"),
    screenshotDir: resolve("videos/red-dot-bloom-spa/screenshots"),
    summary: resolve("videos/red-dot-bloom-spa/browser-validation.json"),
    width: 1600,
    height: 900,
    durationMs: 35000,
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
  { file: "01-appearance.png", at: 4000 },
  { file: "02-search.png", at: 11400 },
  { file: "03-tension.png", at: 17800 },
  { file: "04-transformation.png", at: 23800 },
  { file: "05-resolution.png", at: 33400 },
];
const mobileCapture = {
  file: "mobile-resolution.png",
  at: 33400,
  width: 430,
  height: 932,
};

rmSync(args.screenshotDir, { recursive: true, force: true });
mkdirSync(args.screenshotDir, { recursive: true });
mkdirSync(dirname(args.outputVideo), { recursive: true });

const videoTempDir = join(tmpdir(), `red-dot-bloom-${Date.now()}-${Math.round(Math.random() * 1e9)}`);
mkdirSync(videoTempDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const recordingContext = await browser.newContext({
  viewport: { width: args.width, height: args.height },
  deviceScaleFactor: 1,
  recordVideo: {
    dir: videoTempDir,
    size: { width: args.width, height: args.height },
  },
});

const consoleMessages = [];
const pageErrors = [];
const page = await recordingContext.newPage();
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
await page.evaluate(() => {
  window.__RED_DOT_APP?.setLooping?.(false);
  window.__RED_DOT_APP?.reset?.();
});
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
await recordingContext.close();

const stillContext = await browser.newContext({
  viewport: { width: args.width, height: args.height },
  deviceScaleFactor: 1,
});
const stillPage = await stillContext.newPage();
await stillPage.goto(args.url, { waitUntil: "domcontentloaded" });
await stillPage.waitForFunction(() => Boolean(window.__RED_DOT_READY));
await stillPage.evaluate(() => {
  window.__RED_DOT_APP?.setLooping?.(false);
  window.__RED_DOT_APP?.pause?.();
});

for (const capture of captures) {
  await stillPage.evaluate((at) => {
    window.__RED_DOT_APP?.seek?.(at);
  }, capture.at);
  await stillPage.waitForTimeout(80);
  await stillPage.screenshot({
    path: join(args.screenshotDir, capture.file),
  });
}
await stillContext.close();

const mobileContext = await browser.newContext({
  viewport: { width: mobileCapture.width, height: mobileCapture.height },
  deviceScaleFactor: 2,
});
const mobilePage = await mobileContext.newPage();
await mobilePage.goto(args.url, { waitUntil: "domcontentloaded" });
await mobilePage.waitForFunction(() => Boolean(window.__RED_DOT_READY));
await mobilePage.evaluate((at) => {
  window.__RED_DOT_APP?.setLooping?.(false);
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
