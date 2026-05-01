# Split Screen Sync

## Purpose

This spike tests a Slidev + Manim split-screen composition:

- explanatory text and bullets on the left,
- a larger Manim video panel on the right,
- a second slide that reuses the same video in a broader review layout.

The scene stays text-light, but the Manim asset now uses a staged three-row synchronization mechanism so the video itself can be reviewed for pacing, spacing, and split-screen handoff clarity.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/split-screen-sync/main.py
```

This renders the spike assets into:

```text
videos/split-screen-sync/
```

Expected outputs:

```text
videos/split-screen-sync/split-screen-sync.webm
videos/split-screen-sync/split-screen-sync.png
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/split-screen-sync/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/split-screen-sync/slides.md
```

## Working Notes

- The live slide uses the rendered WebM asset.
- The PNG poster is a white-background fallback for quick review and screenshot validation.
- Keep new experiment assets under `videos/split-screen-sync/` so the spike stays isolated.
- The Manim scene should keep the source cards, faint routes, and receiver slots visible before the opening breath, then hand off one row at a time with enough clearance to pass strict frame-crowding review.

## Learnings So Far

- Slidev handles local asset imports from inside the spike directory cleanly when the paths point back to `videos/split-screen-sync/`.
- A transparent Manim WebM is a good live asset, while a white poster fallback remains useful for visual review.
- Reusing the same Manim asset across multiple slide layouts is a practical way to test composition without adding animation complexity.
- Receiver slots should disappear when target cards land. Leaving a same-size hollow slot behind the actor creates actor-to-outline crowding in still-frame audits.
