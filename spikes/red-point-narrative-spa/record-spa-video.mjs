import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const options = {
    width: 1920,
    height: 1080,
    screenshotsDir: "",
    videoDir: "",
    output: "",
    summary: "",
    url: "",
  };

  for (let index = 2; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!value) {
      throw new Error(`Missing value for ${key}`);
    }
    switch (key) {
      case "--url":
        options.url = value;
        break;
      case "--output":
        options.output = value;
        break;
      case "--video-dir":
        options.videoDir = value;
        break;
      case "--screenshots-dir":
        options.screenshotsDir = value;
        break;
      case "--summary":
        options.summary = value;
        break;
      case "--width":
        options.width = Number(value);
        break;
      case "--height":
        options.height = Number(value);
        break;
      default:
        throw new Error(`Unknown option: ${key}`);
    }
  }

  if (!options.url || !options.output || !options.videoDir || !options.screenshotsDir || !options.summary) {
    throw new Error("Missing required arguments.");
  }

  return options;
}

async function importPlaywright() {
  return import("playwright");
}

async function captureScreenshots(browser, options) {
  const context = await browser.newContext({
    viewport: { width: options.width, height: options.height },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const phases = ["appearance", "search", "tension", "transform", "resolution"];
  const screenshotPlan = [];
  for (const [index, phase] of phases.entries()) {
    await page.goto(`${options.url}?phase=${phase}`, { waitUntil: "networkidle" });
    await page.waitForSelector(`.app[data-phase="${phase}"]`);
    await page.waitForTimeout(200);
    await page.screenshot({
      path: path.join(
        options.screenshotsDir,
        `act-${String(index + 1).padStart(2, "0")}-${phase}.png`,
      ),
      fullPage: false,
    });
    screenshotPlan.push({
      label: phase,
    });
  }

  await page.goto(`${options.url}?phase=resolution`, { waitUntil: "networkidle" });
  await page.waitForSelector(`.app[data-phase="resolution"]`);
  await page.waitForTimeout(200);
  await page.screenshot({
    path: path.join(options.screenshotsDir, "poster-final.png"),
    fullPage: false,
  });

  await context.close();
  return screenshotPlan;
}

async function recordVideo(browser, options) {
  const context = await browser.newContext({
    viewport: { width: options.width, height: options.height },
    deviceScaleFactor: 1,
    recordVideo: {
      dir: options.videoDir,
      size: {
        width: options.width,
        height: options.height,
      },
    },
  });

  const page = await context.newPage();
  await page.goto(options.url, { waitUntil: "networkidle" });
  await page.waitForFunction(() => Boolean(window.redPointNarrative));
  await page.waitForFunction(() => window.redPointNarrative.getState().finished === true, null, {
    timeout: 45000,
  });

  await page.waitForTimeout(300);
  const video = await page.video();
  await page.close();
  const savedPath = await video.path();
  await context.close();
  await fs.copyFile(savedPath, options.output);
}

async function main() {
  const options = parseArgs(process.argv);
  await fs.mkdir(options.screenshotsDir, { recursive: true });
  await fs.mkdir(options.videoDir, { recursive: true });

  const { chromium } = await importPlaywright();
  const browser = await chromium.launch({
    headless: true,
    args: ["--autoplay-policy=no-user-gesture-required"],
  });

  try {
    const screenshots = await captureScreenshots(browser, options);
    await recordVideo(browser, options);
    const summary = {
      capturedAt: new Date().toISOString(),
      durationSeconds: 26.2,
      screenshots,
      output: options.output,
      viewport: {
        width: options.width,
        height: options.height,
      },
    };
    await fs.writeFile(options.summary, `${JSON.stringify(summary, null, 2)}\n`, "utf8");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
