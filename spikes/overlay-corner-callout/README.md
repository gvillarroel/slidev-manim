# Overlay Corner Callout

## Purpose

This spike tests a common Slidev plus Manim pattern:

- a mostly normal slide with text content,
- a small transparent Manim video anchored in a corner or side area,
- a layout that keeps the slide readable while the animation acts as a callout.

The Manim asset is intentionally simple so the experiment focuses on integration and composition rather than on motion complexity.

## Run the render

From the repository root:

```bash
uv run --script spikes/overlay-corner-callout/main.py
```

This renders the spike output into:

```text
videos/overlay-corner-callout/
```

The main deliverables are:

```text
videos/overlay-corner-callout/overlay-corner-callout.webm
videos/overlay-corner-callout/overlay-corner-callout.png
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/overlay-corner-callout/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/overlay-corner-callout/slides.md
```

## Notes

- The video is rendered with a transparent background for real Slidev use.
- The PNG file is a white-background review artifact so the callout can still be inspected quickly.
- Keep the slide-local assets imported from `../../videos/overlay-corner-callout/` so the deck stays self-contained.
