# Slidev deck to MP4

There are two useful export paths in this repo.

## Full-fidelity recording: captures animations and transitions

Use this for real presentation video. It starts the Slidev dev server, opens the deck in Chromium with Playwright, walks forward through the presentation, records the browser, and re-encodes the Playwright `.webm` capture to MP4 with `ffmpeg`.

```bash
npm run record:mp4 -- slides.md videos/deck.mp4
```

Useful options are environment variables:

```bash
STEP_WAIT_MS=2000 MAX_STEPS=80 FPS=30 SIZE=1920x1080 \
  npm run record:mp4 -- slides.md videos/deck.mp4
```

Options:

- `STEP_WAIT_MS`: milliseconds to wait after each `ArrowRight` step. Increase this for long animations/transitions.
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
