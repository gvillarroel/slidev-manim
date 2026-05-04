# Multi Video Grid

## Purpose

This spike tests whether several independent Manim assets can live on the same Slidev slide without layout drift, playback conflicts, or awkward sizing.

The render set is intentionally varied and now uses the same restrained
red/gray motion grammar across all four clips:

- `orbit` tests circular motion in a compact card.
- `pulse` tests a centered signal-style animation.
- `sweep` tests horizontal motion across a track.
- `merge` tests two elements converging into a shared outcome.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/multi-video-grid/main.py
```

This renders the spike assets into:

```text
videos/multi-video-grid/
```

Expected outputs:

```text
videos/multi-video-grid/multi-video-grid-orbit.webm
videos/multi-video-grid/multi-video-grid-pulse.webm
videos/multi-video-grid/multi-video-grid-sweep.webm
videos/multi-video-grid/multi-video-grid-merge.webm
```

White poster PNGs are also written alongside the videos for review and fallback rendering.
Dense 0.3-second white-background review frames and contact sheets are written to:

```text
videos/multi-video-grid/review-frames-0.3s/
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/multi-video-grid/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/multi-video-grid/slides.md
```

## Notes

- The live slide uses transparent WebM assets.
- The PNG posters are for review and for browsers that do not visibly paint video frames in automated screenshots.
- Keeping every media import local to this spike avoids leaking experiment-specific references into the project root.

## Learnings

- Slidev can keep multiple Manim videos on the same slide when each asset has its own local import and readiness state.
- A 2x2 comparison grid is a practical way to check whether four independent videos stay aligned and readable at once.
- A two-up panel is useful for confirming that the same assets still look correct when the layout becomes more narrative.
- White PNG posters remain a useful fallback while the transparent WebM files are the delivery format.
- Multi-asset grid videos should not each redraw their own title card or rounded panel; let the Slidev grid supply labels and chrome, while each Manim asset stays content-first.
- Even when the deck loops the media, each promoted asset should still get slide-integration pacing unless it is explicitly documented as a micro-loop.
- Shared red/gray grammar across the clips keeps a dense grid from reading as four unrelated palettes.
