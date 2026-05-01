---
title: Manim Data Counter Lab
status: draft
date: 2026-05-01
---

# Purpose

Test the clearest narrative use of Manim data features for a table-driven aggregation that lands in a live counter and then returns to the table.

# Hypothesis

If a source row is cued before data moves, the aggregation lives in a separate side zone, and the counter changes only while a visible handoff is in flight, then a table calculation can read as a narrated event instead of a static spreadsheet.

# Assessment

This video is a good direction for expressing transformations. The table-to-side-formula-to-live-counter handoff makes the change visible as a narrated state transition instead of a static result. The polished pass keeps handoffs token-led, removes temporary row scaffolding before the final hold, and treats the clean table with the resolved value as the landing state.

# Feature Coverage

This spike exercises the Manim Community v0.20.1 data and number APIs documented in the official reference:

- `MobjectTable`, inheriting `Table` helpers for a row-labeled source table.
- `DecimalNumber` and `ChangeDecimalToValue` for the live counter.
- `ValueTracker` for the progress rail synchronized with the counter.
- `BarChart` for a compact comparison context while the active value rises.

The scene intentionally uses `MobjectTable` instead of `MathTable` so entries can use native `Text` mobjects and render reliably without requiring a local LaTeX installation. The side aggregation is still formula-like, but it stays in a sparse, high-contrast panel rather than animating text on top of table cells.

# Run

```bash
uv run --script spikes/manim-data-counter-lab/main.py
```

For a faster local pass:

```bash
uv run --script spikes/manim-data-counter-lab/main.py --quality low
```

# Output

The render writes:

- `videos/manim-data-counter-lab/manim-data-counter-lab.webm`
- `videos/manim-data-counter-lab/manim-data-counter-lab.png`

The video uses a neutral local stage so the table, formula panel, counter, and chart remain readable when embedded in Slidev.

# Review Focus

Accept the spike only if proof frames show:

- the active source row before any aggregation terms appear,
- source values handed to the formula side zone without covering the table text,
- the counter changing while a visible result handoff is in flight,
- the final value landing in the destination cell after the placeholder has been removed,
- no source or destination text overlap during the landing.
