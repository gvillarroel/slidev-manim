# Time Rail Point One

## Purpose

This spike explores how `time rail` can move from an agenda into the first detailed section.

The first beat shows a complete agenda. Then the active rail reaches point 1, the remaining agenda items soften, and the first point expands into a detail panel. The goal is to test a narrative continuation: the rail starts as agenda structure, then becomes a section opener.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/time-rail-point-one/main.py
```

The generated assets are written to:

```text
videos/time-rail-point-one/
```

Expected outputs:

```text
videos/time-rail-point-one/time-rail-point-one.webm
videos/time-rail-point-one/time-rail-point-one.png
```

## Working Notes

- Motion family: `time rail`.
- Hypothesis: a time rail can begin as an agenda, then open point 1 by keeping the rail fixed, softening future items, and letting the first card become the detail stage.
- The first point should not feel like another agenda row; it should become the main content while the rail preserves orientation.
