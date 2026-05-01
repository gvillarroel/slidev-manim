---
title: Red Point Narrative SPA
status: active
date: 2026-05-01
---

# Red Point Narrative SPA

## Purpose

This spike builds a one-screen experimental SPA where a single red point carries the whole narrative. The page avoids explanatory copy and relies on pacing, form search, conflict, transformation, and a calm resolved structure to guide attention.

## Narrative beats

1. Appearance: the point arrives with breathing room and a faint reserved destination zone.
2. Search: the point probes several candidate shapes without committing.
3. Tension: the stage narrows into a gate and the point visibly compresses under pressure.
4. Transformation: the point breaks through and starts drawing a structured route.
5. Resolution: the route settles into a balanced connected composition with the point as the anchor.

## Build the SPA output

From the repository root:

```bash
uv run --script spikes/red-point-narrative-spa/main.py
```

This copies the spike's static site into:

```text
videos/red-point-narrative-spa/site/
```

## Serve the built output locally

From the repository root:

```bash
python -m http.server 4173 --directory videos/red-point-narrative-spa/site
```

Then open:

```text
http://127.0.0.1:4173/
```

## Stable review phases

For visual review and screenshot capture, the SPA can freeze on a specific phase:

- `/?phase=appearance`
- `/?phase=search`
- `/?phase=tension`
- `/?phase=transform`
- `/?phase=resolution`

## Validation

From the repository root, after starting the local server:

```bash
node spikes/red-point-narrative-spa/validate.mjs --base-url http://127.0.0.1:4173
```

This writes screenshots and a validation summary to:

```text
videos/red-point-narrative-spa/review/desktop/
videos/red-point-narrative-spa/review/mobile/
videos/red-point-narrative-spa/review/validation-summary.json
```
