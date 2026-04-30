---
id: KNOW-0001
title: Validate a spike Slidev deck with Playwright
status: active
date: 2026-04-14
---

# Summary

Use Playwright to verify that a spike-local Slidev deck loads and that its Manim video asset is reachable.

# Steps

1. Install dependencies with `npm install`.
2. Start the deck with `npx @slidev/cli spikes/<spike-name>/slides.md`.
3. Open `http://localhost:3030/1` and `http://localhost:3030/2` with Playwright.
4. Check that a `video` element exists on each slide.
5. Check that the video source returns `200`.
6. Save screenshots for visual review.

# Notes

- Use direct slide routes like `/1`, `/2` for stable validation.
- If Slidev serves stale optimized dependencies, restart with `--force`.
- Slidev can keep multiple slide DOM trees mounted, so visibility checks on `video` can be misleading if you do not target the active route explicitly.
- In this project, browser automation may load the `video` asset successfully and still fail to paint frames in screenshots.
- For slide-progress screenshots, force or preserve a white review background by default. Only capture against another background when the spike is specifically testing that surface.
- Check video duration and pacing against ADR-0003: normal slide-integration scenes should be at least 25 seconds, with an opening visible breath and a longer final hold.
- For visual iteration, generate and attach white-background poster PNGs even when the real delivery artifact is a transparent WebM.
- Use the transparent `.webm` asset for the real slide and keep the `.png` poster as the review fallback.
- When validating Slidev local media, prefer Vite-imported asset URLs over raw relative or `/videos/...` references.
- For functional verification, distinguish between:
  - standalone browser playback of the media file,
  - asset resolution inside Slidev,
  - and visible composition inside the final slide.
