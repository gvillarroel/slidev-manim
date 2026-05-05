# Time Rail Branching

## Purpose

This spike explores `time rail` as a branching narrative device.

Instead of a red dot traveling across a route, a vertical time rail records the main progression and emits short horizontal branches at decision moments. The goal is to test whether time can behave like an organizing spine for multiple outcomes while still staying sparse enough for Slidev integration.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/time-rail-branching/main.py
```

The generated assets are written to:

```text
videos/time-rail-branching/
```

Expected outputs:

```text
videos/time-rail-branching/time-rail-branching.webm
videos/time-rail-branching/time-rail-branching.png
```

## Working Notes

- Motion family: `time rail`.
- Hypothesis: if the rail emits branches only after the active time segment reaches each tick, the branches read as consequences of time rather than generic side arrows.
- Branch guides should soften after the branch card lands so the final frame does not look mid-transition.
- Transparent branch reviews should use stroke-only pending slots and an alpha-on-white review surface; filled placeholders can become gray blocks and full red receiver outlines can make a single branch dominate sampled still frames.
