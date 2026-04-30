---
title: Polars Derived Column
status: draft
date: 2026-04-29
---

# Purpose

Show how a Polars expression can calculate a new dataset column from two existing columns.

# Hypothesis

If the two source columns send row-level values through a small calculation gate before the result lands in the new column, the transformation should read as a table-driven computation rather than as a static before-and-after table.

# Dataset Transformation

The spike builds this dataset in Python with Polars:

```python
df.with_columns(
    (pl.col("qty") * pl.col("unit_price")).alias("revenue")
)
```

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-green` for `qty`
- `primary-blue` for `unit_price`
- `primary-purple` for `revenue`
- `primary-orange` for the operator
- `primary-yellow` and `highlight-yellow` for the active calculation beat
- `highlight-green`, `highlight-blue`, and `highlight-purple` for body cells
- `gray`, `gray-200`, `gray-400`, `white`, and `page-background` for neutral structure

# Run

```bash
uv run --script spikes/polars-derived-column/main.py
```

# Output

The render writes:

- `videos/polars-derived-column/polars-derived-column.webm`
- `videos/polars-derived-column/polars-derived-column.png`

The video render uses a transparent background for Slidev overlays. The poster render uses the canonical `page-background` color for review.
