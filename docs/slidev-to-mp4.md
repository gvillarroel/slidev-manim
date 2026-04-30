# Slidev deck to MP4

There are two useful export paths in this repo.

## Full-fidelity recording: captures animations and transitions

Use this for real presentation video. It assumes a Slidev dev server is already running, opens the deck in Chromium with Playwright, walks forward through the presentation, records the browser, and re-encodes the Playwright `.webm` capture to MP4 with `ffmpeg`.

Start Slidev separately:

```bash
npm run dev:your-deck
# or: npx slidev slides.md
```

Then record the active browser presentation:

```bash
npm run record:mp4 -- slides.md videos/deck.mp4
```

Set the default timing with environment variables:

```bash
SLIDEV_URL=http://127.0.0.1:3030 STEP_WAIT_MS=2000 MAX_STEPS=80 FPS=30 SIZE=1920x1080 \
  npm run record:mp4 -- slides.md videos/deck.mp4
```

Override timing per slide with Slidev frontmatter:

```md
---
recordWait: 5000
---

# This slide records for 5 seconds before advancing
```

`recordWait` is in milliseconds and overrides `STEP_WAIT_MS` for that slide.

Options:

- `SLIDEV_URL`: already-running Slidev URL, default `http://127.0.0.1:3030`.
- `STEP_WAIT_MS`: default milliseconds to wait on each slide/click step. Increase this for long animations/transitions.
- `INTRO_WAIT_MS`: milliseconds to wait before navigation starts.
- `MAX_STEPS`: safety cap for slide/click advances.
- `SIZE`: browser/video size, default `1920x1080`.
- `FPS`: output MP4 frame rate, default `30`.
- `KEEP_WEBM=1`: keep Playwright's raw `.webm` beside the MP4.

## Static fallback: PNG frames to MP4

This is useful for quick static decks, but it does **not** capture runtime animations or transitions.

```bash
scripts/slidev-to-mp4.sh slides.md videos/deck-static.mp4
```

Requirements:

- Node dependencies installed (`npm install` or `pnpm install`)
- Playwright browser installed (`npx playwright install chromium` if needed)
- `ffmpeg` in `PATH`
