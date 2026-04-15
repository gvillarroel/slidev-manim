# Timeline Stack

## Purpose

This spike tests a Slidev + Manim integration pattern built around stacked text sections and a clear progression feel.

The render set intentionally covers two aspect ratios:

- a wide hero asset for a full-slide or split-screen composition,
- a tall panel asset for a more vertical narrative block.

The goal is to learn how well Slidev can host a sequential timeline-style Manim asset without losing readability when the surrounding slide layout changes.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/timeline-stack/main.py
```

The generated assets are written to:

```text
videos/timeline-stack/
```

Expected outputs:

```text
videos/timeline-stack/timeline-stack-wide.webm
videos/timeline-stack/timeline-stack-wide.png
videos/timeline-stack/timeline-stack-portrait.webm
videos/timeline-stack/timeline-stack-portrait.png
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/timeline-stack/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/timeline-stack/slides.md
```

## Working Notes

- The WebM files are the live delivery assets for the slides.
- The PNG files are white-background posters for review and fallback rendering.
- Keep slide-local imports inside `spikes/timeline-stack/slides.md` so the experiment stays self-contained.

## Learnings So Far

- A timeline-style Manim asset works best when the slide gives it a dedicated visual lane instead of compressing it into a generic content slot.
- A wide render and a tall render solve different presentation needs better than a single crop.
- The combination of transparent WebM plus a white poster PNG remains the most practical setup for iteration.
- Reusing the same step labels in Slidev and Manim makes the progression easier to read and validate.
