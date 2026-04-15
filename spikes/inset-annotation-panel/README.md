# Inset Annotation Panel

## Purpose

This spike tests a Slidev layout where the main slide content is accompanied by a small Manim inset used as an annotation or magnified detail view.

The goal is to learn how far we can push:

- a primary content slide with a small inset video anchored inside the layout,
- separate aspect ratios for the main and detail videos so each one matches its job.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/inset-annotation-panel/main.py
```

This writes the rendered assets to:

```text
videos/inset-annotation-panel/
```

Expected outputs:

```text
videos/inset-annotation-panel/inset-annotation-panel-main.webm
videos/inset-annotation-panel/inset-annotation-panel-main.png
videos/inset-annotation-panel/inset-annotation-panel-zoom.webm
videos/inset-annotation-panel/inset-annotation-panel-zoom.png
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/inset-annotation-panel/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/inset-annotation-panel/slides.md
```

## Working Notes

- The main render is a wide annotation panel that can sit beside explanatory text.
- The zoom render is a square detail asset meant to act as a small inset or magnified callout.
- White PNG posters are kept for review and screenshot fallback, while the WebM files are the live Slidev assets.

## Learnings

- A Slidev slide is easier to scan when the inset video is clearly smaller than the primary content area.
- Separate wide and square renders fit the composition better than stretching one asset into every role.
- Poster fallback remains useful because it gives a stable visual reference even when browser video playback is inconsistent.
