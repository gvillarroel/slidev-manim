# Background Loop Layer

## Purpose

This spike tests whether a Manim video can behave like an ambient Slidev background layer rather than a foreground animation.

The deck focuses on two related compositions:

- a full-slide hero slide with foreground copy over a looping background layer,
- a near-full-slide content slide that keeps the same background video behind denser text and cards.

The animation itself is intentionally subtle so the spike measures readability, layering, and loop quality instead of motion complexity.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/background-loop-layer/main.py
```

This renders the spike assets into:

```text
videos/background-loop-layer/
```

Expected outputs:

```text
videos/background-loop-layer/background-loop-layer.webm
videos/background-loop-layer/background-loop-layer.png
```

The WebM is the live transparent delivery asset. The PNG is a poster fallback for review and browser validation.

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/background-loop-layer/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/background-loop-layer/slides.md
```

## Working Notes

- Keep the background animation low-contrast so it supports the foreground content.
- Use poster fallback rendering so the slide remains reviewable even when the live video is still loading.
- Keep the deck local to this spike so the experiment stays isolated from the rest of the repository.

## Learnings So Far

- A transparent Manim WebM is a good fit for ambient slide layers because it lets Slidev own the visible slide background.
- A poster fallback should mirror the slide backdrop closely so review screenshots stay representative.
- Foreground copy works best when it sits on a solid or translucent card above the moving layer.
- A single looping asset can support both full-slide and near-full-slide compositions when the foreground layout changes around it.
