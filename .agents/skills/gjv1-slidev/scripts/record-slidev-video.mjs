#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import {
  basename,
  dirname,
  isAbsolute,
  join,
  relative,
  resolve,
} from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const DEFAULT_PORT = 3030;
const DEFAULT_WIDTH = 1280;
const DEFAULT_HEIGHT = 720;
const DEFAULT_SECONDS_PER_SLIDE = 3;
const DEFAULT_SECONDS_PER_CLICK = 1.4;
const DEFAULT_TRANSITION_MS = 850;
const DEFAULT_CLICK_SETTLE_MS = 350;
const DEFAULT_TIMEOUT_MS = 90_000;

function usage() {
  return `
Usage:
  node record-slidev-video.mjs --entry spikes/demo/slides.md --output videos/demo/demo.webm [options]

Options:
  --entry <path>              Slidev markdown entry.
  --output <path>             Output WebM path.
  --seconds-per-slide <n>     Hold time per slide. Default: 3.
  --seconds-per-click <n>     Hold time after same-slide click stages. Default: 1.4.
  --transition-ms <n>         Wait after each ArrowRight. Default: 850.
  --click-settle-ms <n>       Wait after each same-slide click. Default: 350.
  --click-plan <json>         JSON object mapping slide numbers to same-slide clicks.
  --slide-count <n>           Override parsed slide count.
  --screenshots-dir <path>    Save one PNG screenshot per slide.
  --port <n>                  Slidev server port. Default: 3030.
  --width <n>                 Browser width. Default: 1280.
  --height <n>                Browser height. Default: 720.
  --timeout-ms <n>            Server/browser timeout. Default: 90000.
`;
}

function parseArgs(argv) {
  const args = {
    port: DEFAULT_PORT,
    width: DEFAULT_WIDTH,
    height: DEFAULT_HEIGHT,
    secondsPerSlide: DEFAULT_SECONDS_PER_SLIDE,
    secondsPerClick: DEFAULT_SECONDS_PER_CLICK,
    transitionMs: DEFAULT_TRANSITION_MS,
    clickSettleMs: DEFAULT_CLICK_SETTLE_MS,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    clickPlan: new Map(),
    slideCount: undefined,
    screenshotsDir: undefined,
    entry: undefined,
    output: undefined,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--help" || key === "-h") {
      console.log(usage());
      process.exit(0);
    }
    if (!key.startsWith("--")) {
      throw new Error(`Unexpected argument: ${key}`);
    }
    if (value === undefined || value.startsWith("--")) {
      throw new Error(`Missing value for ${key}`);
    }

    i += 1;
    switch (key) {
      case "--entry":
        args.entry = value;
        break;
      case "--output":
        args.output = value;
        break;
      case "--seconds-per-slide":
        args.secondsPerSlide = Number(value);
        break;
      case "--seconds-per-click":
        args.secondsPerClick = Number(value);
        break;
      case "--transition-ms":
        args.transitionMs = Number(value);
        break;
      case "--click-settle-ms":
        args.clickSettleMs = Number.parseInt(value, 10);
        break;
      case "--click-plan":
        args.clickPlan = parseClickPlan(value);
        break;
      case "--slide-count":
        args.slideCount = Number.parseInt(value, 10);
        break;
      case "--screenshots-dir":
        args.screenshotsDir = value;
        break;
      case "--port":
        args.port = Number.parseInt(value, 10);
        break;
      case "--width":
        args.width = Number.parseInt(value, 10);
        break;
      case "--height":
        args.height = Number.parseInt(value, 10);
        break;
      case "--timeout-ms":
        args.timeoutMs = Number.parseInt(value, 10);
        break;
      default:
        throw new Error(`Unknown option: ${key}`);
    }
  }

  if (!args.entry) throw new Error("--entry is required");
  if (!args.output) throw new Error("--output is required");
  if (!Number.isFinite(args.secondsPerSlide) || args.secondsPerSlide <= 0) {
    throw new Error("--seconds-per-slide must be a positive number");
  }
  if (!Number.isFinite(args.secondsPerClick) || args.secondsPerClick < 0) {
    throw new Error("--seconds-per-click must be a non-negative number");
  }
  if (!Number.isFinite(args.transitionMs) || args.transitionMs < 0) {
    throw new Error("--transition-ms must be a non-negative number");
  }
  if (!Number.isInteger(args.clickSettleMs) || args.clickSettleMs < 0) {
    throw new Error("--click-settle-ms must be a non-negative integer");
  }
  return args;
}

function parseClickPlan(value) {
  let parsed;
  try {
    parsed = JSON.parse(value);
  } catch (error) {
    throw new Error(`--click-plan must be valid JSON. ${error.message}`);
  }

  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("--click-plan must be a JSON object like {\"2\":4}");
  }

  const plan = new Map();
  for (const [slide, clicks] of Object.entries(parsed)) {
    const slideNumber = Number.parseInt(slide, 10);
    if (!Number.isInteger(slideNumber) || slideNumber < 1) {
      throw new Error(`Invalid slide number in --click-plan: ${slide}`);
    }
    if (!Number.isInteger(clicks) || clicks < 0) {
      throw new Error(`Invalid click count for slide ${slide}: ${clicks}`);
    }
    plan.set(slideNumber, clicks);
  }
  return plan;
}

function slideNumberFromUrl(url) {
  const pathname = new URL(url).pathname;
  const match = pathname.match(/\/(\d+)\/?$/);
  return match ? Number.parseInt(match[1], 10) : 1;
}

function findRepoRoot(startDir) {
  let current = resolve(startDir);
  while (true) {
    if (existsSync(join(current, "package.json"))) return current;
    const parent = dirname(current);
    if (parent === current) return resolve(startDir);
    current = parent;
  }
}

async function parseSlideCount(entry, override) {
  if (override !== undefined) {
    if (!Number.isInteger(override) || override < 1) {
      throw new Error("--slide-count must be a positive integer");
    }
    return override;
  }

  const markdown = readFileSync(entry, "utf8");
  try {
    const parser = await import("@slidev/parser/core");
    const parsed = parser.parseSync(markdown, entry);
    if (parsed?.slides?.length) return parsed.slides.length;
  } catch (error) {
    console.warn(`Could not parse with @slidev/parser: ${error.message}`);
  }

  const normalized = markdown.replace(/\r\n/g, "\n");
  return normalized.split(/\n---\s*\n/g).length;
}

function npxCommand() {
  return process.platform === "win32" ? "npx.cmd" : "npx";
}

function slidevCommand(cwd) {
  const localCli = join(cwd, "node_modules", "@slidev", "cli", "bin", "slidev.mjs");
  if (existsSync(localCli)) {
    return {
      command: process.execPath,
      prefixArgs: [localCli],
      shell: false,
    };
  }
  return {
    command: npxCommand(),
    prefixArgs: ["slidev"],
    shell: process.platform === "win32",
  };
}

function spawnSlidev(entry, port, cwd) {
  const entryForCli = isAbsolute(entry) ? relative(cwd, entry) : entry;
  const cli = slidevCommand(cwd);
  const child = spawn(
    cli.command,
    [
      ...cli.prefixArgs,
      entryForCli,
      "--port",
      String(port),
      "--open",
      "false",
      "--log",
      "warn",
    ],
    {
      cwd,
      env: { ...process.env, BROWSER: "none", NO_COLOR: "1" },
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
      shell: cli.shell,
    },
  );

  child.stdout.on("data", (chunk) => process.stdout.write(chunk));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  return child;
}

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function waitForServer(url, child, timeoutMs) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (child.exitCode !== null) {
      throw new Error(`Slidev exited before serving ${url}`);
    }
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {
      // Keep polling until timeout.
    }
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(
      `Playwright is required for recording. Install project dependencies first. ${error.message}`,
    );
  }
}

async function saveSlideScreenshot(page, screenshotsDir, slideIndex, clickIndex) {
  if (!screenshotsDir) return;

  const slide = String(slideIndex).padStart(2, "0");
  const suffix = clickIndex
    ? `-click-${String(clickIndex).padStart(2, "0")}`
    : "";
  await page.screenshot({
    path: join(screenshotsDir, `slide-${slide}${suffix}.png`),
    fullPage: false,
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const entry = resolve(args.entry);
  const output = resolve(args.output);
  if (!existsSync(entry)) throw new Error(`Slidev entry not found: ${entry}`);

  const repoRoot = findRepoRoot(dirname(entry));
  const slideCount = await parseSlideCount(entry, args.slideCount);
  const outputDir = dirname(output);
  mkdirSync(outputDir, { recursive: true });

  const screenshotsDir = args.screenshotsDir
    ? resolve(args.screenshotsDir)
    : undefined;
  if (screenshotsDir) {
    rmSync(screenshotsDir, { recursive: true, force: true });
    mkdirSync(screenshotsDir, { recursive: true });
  }

  const videoTempDir = join(
    tmpdir(),
    `slidev-video-${Date.now()}-${Math.round(Math.random() * 1e9)}`,
  );
  mkdirSync(videoTempDir, { recursive: true });

  const baseUrl = `http://localhost:${args.port}`;
  const slidev = spawnSlidev(entry, args.port, repoRoot);
  let browser;

  const shutdown = () => {
    if (slidev.exitCode === null && slidev.pid) {
      if (process.platform === "win32") {
        spawnSync("taskkill", ["/pid", String(slidev.pid), "/t", "/f"], {
          stdio: "ignore",
          windowsHide: true,
        });
        return;
      }
      slidev.kill("SIGTERM");
    }
  };
  process.once("SIGINT", () => {
    shutdown();
    process.exit(130);
  });
  process.once("SIGTERM", () => {
    shutdown();
    process.exit(143);
  });

  try {
    await waitForServer(`${baseUrl}/`, slidev, args.timeoutMs);
    const { chromium } = await loadPlaywright();
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: args.width, height: args.height },
      recordVideo: {
        dir: videoTempDir,
        size: { width: args.width, height: args.height },
      },
      deviceScaleFactor: 1,
      colorScheme: "light",
    });
    const page = await context.newPage();
    page.setDefaultTimeout(args.timeoutMs);

    await page.goto(`${baseUrl}/1`, { waitUntil: "networkidle" });
    await page.mouse.move(args.width - 10, Math.floor(args.height / 2));
    await page.mouse.click(Math.floor(args.width / 2), Math.floor(args.height / 2));
    await page.waitForTimeout(800);

    const pageVideo = page.video();
    for (let index = 1; index <= slideCount; index += 1) {
      console.log(`Recording slide ${index}/${slideCount}`);
      await page.waitForTimeout(350);
      await saveSlideScreenshot(page, screenshotsDir, index, 0);
      await page.waitForTimeout(args.secondsPerSlide * 1000);

      const sameSlideClicks = args.clickPlan.get(index) ?? 0;
      for (let click = 1; click <= sameSlideClicks; click += 1) {
        const beforeSlide = slideNumberFromUrl(page.url());
        console.log(`Recording slide ${index}/${slideCount}, click ${click}/${sameSlideClicks}`);
        await page.keyboard.press("ArrowRight");
        await page.waitForTimeout(args.clickSettleMs);
        const afterSlide = slideNumberFromUrl(page.url());
        if (afterSlide !== beforeSlide) {
          throw new Error(
            `Click plan for slide ${index} advanced to slide ${afterSlide}. Reduce the click count.`,
          );
        }
        await saveSlideScreenshot(page, screenshotsDir, index, click);
        await page.waitForTimeout(args.secondsPerClick * 1000);
      }

      if (index < slideCount) {
        const beforeSlide = slideNumberFromUrl(page.url());
        await page.keyboard.press("ArrowRight");
        await page.waitForTimeout(args.transitionMs);
        const afterSlide = slideNumberFromUrl(page.url());
        if (afterSlide === beforeSlide) {
          throw new Error(
            `ArrowRight did not change the URL on slide ${index}. The slide still has unrecorded click stages; increase --click-plan for slide ${index}.`,
          );
        }
      }
    }

    await page.close();
    await context.close();
    await browser.close();
    browser = undefined;

    const recordedPath = await pageVideo.path();
    copyFileSync(recordedPath, output);
    console.log(`Recorded ${basename(output)} (${slideCount} slides) -> ${output}`);
  } finally {
    if (browser) await browser.close();
    shutdown();
    rmSync(videoTempDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
