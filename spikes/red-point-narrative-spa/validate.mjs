#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const spikeDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(spikeDir, "..", "..");
const spikeName = "red-point-narrative-spa";
const reviewDir = path.join(repoRoot, "videos", spikeName, "review");
const phases = ["appearance", "search", "tension", "transform", "resolution"];
const viewports = [
  {
    label: "desktop",
    viewport: { width: 1440, height: 1100 },
    deviceScaleFactor: 1,
  },
  {
    label: "mobile",
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
  },
];

function parseArgs(argv) {
  const args = { baseUrl: "http://127.0.0.1:4173" };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--base-url" && argv[index + 1]) {
      args.baseUrl = argv[index + 1];
      index += 1;
    }
  }
  return args;
}

async function ensureDir(target) {
  await fs.mkdir(target, { recursive: true });
}

async function capturePhase(page, baseUrl, phase, viewportLabel) {
  const url = `${baseUrl}/?phase=${phase}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForSelector(`.app[data-phase="${phase}"]`);
  await page.waitForTimeout(220);

  const outputDir = path.join(reviewDir, viewportLabel);
  await ensureDir(outputDir);
  const screenshot = path.join(outputDir, `${phase}.png`);
  await page.screenshot({ path: screenshot });

  const metrics = await page.evaluate(() => {
    const shell = document.querySelector(".stage-shell");
    const app = document.querySelector(".app");
    const controls = document.querySelectorAll(".phase-dot.is-active").length;
    const bounds = shell?.getBoundingClientRect();
    return {
      phase: app?.dataset.phase ?? null,
      activeMarkers: controls,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      stageWidth: bounds ? Math.round(bounds.width) : null,
      stageHeight: bounds ? Math.round(bounds.height) : null,
    };
  });

  return {
    phase,
    viewportLabel,
    url,
    screenshot,
    ...metrics,
  };
}

async function main() {
  const { baseUrl } = parseArgs(process.argv.slice(2));
  await ensureDir(reviewDir);

  const browser = await chromium.launch();
  const results = [];
  try {
    for (const viewportSpec of viewports) {
      const page = await browser.newPage({
        viewport: viewportSpec.viewport,
        deviceScaleFactor: viewportSpec.deviceScaleFactor,
      });
      for (const phase of phases) {
        results.push(await capturePhase(page, baseUrl, phase, viewportSpec.label));
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }

  const summary = {
    spike: spikeName,
    baseUrl,
    capturedAt: new Date().toISOString(),
    viewports,
    phases: results,
  };

  await fs.writeFile(
    path.join(reviewDir, "validation-summary.json"),
    `${JSON.stringify(summary, null, 2)}\n`,
    "utf8",
  );

  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
