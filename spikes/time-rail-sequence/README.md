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
videos/time-rail-sequence/review-frames-0.3s/frames/
videos/time-rail-sequence/review-frames-0.3s/sheets/contact-sheet-01.png
```

## Working Notes

- Motion family: `time rail`.
- Hypothesis: if the rail itself records progress, the viewer reads time as the narrator rather than following a traveling dot.
- The first frame must show the whole pending timeline structure, then the opening breath lets the viewer read it.
- The final hold keeps only the resolved cards, active rail, and terminal cap.

## Polished Pass

- The WebM render is a transparent content asset; only the poster uses the local `page-background` stage.
- Pending cards are outline scaffolds, so the first frame remains readable without turning into heavy gray placeholder bars.
- Each tick emits a short branch cue only after the red rail reaches it, then the card resolves.
- The final hold is owned by the filled rail and bottom cap instead of a detached red rule away from the timeline.
- Latest validation: 25.498 seconds, 85 alpha-on-white review frames at 0.3-second cadence, decoded alpha range `0..255`, composition audit 0 blocking frames across 86 samples, crowding audit 0 blocking frames across 86 samples, and resting-mobject audit 0 blocking snapshots across 5 rest states.
