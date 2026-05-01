# Time Rail Sequence

## Purpose

This spike explores `time rail` as a narrative alternative to a red guide dot.

The left-side rail behaves like elapsed time: it is visible from the first frame, then the active red segment grows downward and causes each content card to resolve. The goal is to test whether a timeline-shaped mechanism can carry narration without needing a separate moving marker.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/time-rail-sequence/main.py
```

The generated assets are written to:

```text
videos/time-rail-sequence/
```

Expected outputs:

```text
videos/time-rail-sequence/time-rail-sequence.webm
videos/time-rail-sequence/time-rail-sequence.png
```

## Working Notes

- Motion family: `time rail`.
- Hypothesis: if the rail itself records progress, the viewer reads time as the narrator rather than following a traveling dot.
- The first frame must show the whole pending timeline structure, then the opening breath lets the viewer read it.
- The final hold keeps only the resolved cards, active rail, and terminal rule.
