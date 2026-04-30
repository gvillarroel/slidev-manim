---
id: SPEC-2026-04-29-polars-derived-column-video
title: Polars derived column video scenes
status: draft
date: 2026-04-29
---

# Polars Derived Column

## Overview

- **Topic**: Table-driven column derivation with Polars expressions.
- **Hook**: A new column is not typed manually; it falls out of a row-wise expression.
- **Target Audience**: Developers who understand tabular data and basic Python.
- **Estimated Length**: 30 seconds.
- **Key Insight**: `with_columns` keeps the original dataframe and attaches a new series computed from existing columns.

## Narrative Arc

The scene begins with a dataset that has `qty` and `unit_price` but an empty `revenue` column. A Polars expression appears underneath the table. Each row sends the two source values into a compact side formula, and the computed value lands in `revenue`.

## Scene 1: Source Table

**Duration**: ~1.3 seconds
**Purpose**: Establish the two input columns and the empty destination column.

### Visual Elements

- A compact four-column table.
- Green highlight for `qty`.
- Blue highlight for `unit_price`.
- Purple highlight for `revenue`.
- A two-line code panel using the actual Polars expression.

### Content

The table fades in first, followed by the expression:

```python
df.with_columns(
    (pl.col("qty") * pl.col("unit_price")).alias("revenue")
)
```

The source columns and matching code tokens pulse briefly.

### Technical Notes

- Build the dataframe with Polars in the script and derive `revenue` before animation.
- Keep text minimal except for table values and code tokens.

## Scene 2: Row Calculation

**Duration**: ~22 seconds
**Purpose**: Show the expression being applied row by row.

### Visual Elements

- One yellow row cursor with a left marker and bottom rule.
- Green and blue source values transformed into aligned formula terms.
- A compact white side formula badge with an orange border.
- A yellow computed formula term that lands in the destination cell and resolves into the purple table value.

### Content

For each row, the two source cell values duplicate into fixed positions inside a side formula badge. The computed `revenue` term appears in the same aligned formula, then lands in the destination column and resolves into the final purple table value.

### Technical Notes

- Animate one row at a time so the mechanism survives in still frames.
- Hold briefly after showing each formula and after landing each result so the viewer can read the calculation.
- Fade calculation scaffolding after each row so the final table remains clean.

## Scene 3: Resolved Dataset

**Duration**: ~1 second
**Purpose**: Close on the completed transformed dataframe.

### Visual Elements

- Filled `revenue` column.
- Purple outline around the derived column.
- Faded route guides removed before the final hold.

### Content

The final frame contains the original columns plus the derived column. The code token for `revenue` pulses once to connect the alias with the finished column.

The resolved table holds for several seconds so the video can breathe at the end.

## Transitions & Flow

The motion family is `side formula handoff`: two inputs transform into one aligned formula outside the table, then the computed output returns to the derived column. Support guides stay subordinate and disappear before the final resolved frame.

## Color Palette

- `primary-green`: `qty` header, moving source value, and code token.
- `primary-blue`: `unit_price` header, moving source value, and code token.
- `primary-purple`: `revenue` header, destination values, and code token.
- `primary-orange`: expression operator and row route.
- `primary-yellow`: row cursor and transient computed value.
- `white`: panel surfaces and calculation badge fill.
- `highlight-green`: `qty` body cells.
- `highlight-blue`: `unit_price` body cells.
- `highlight-purple`: `revenue` body cells.
- `gray`, `gray-200`, and `gray-400`: neutral text and table structure.
- `page-background`: poster review background.

## Implementation Order

1. Build the actual Polars dataframe and derived column.
2. Construct the table from computed data.
3. Animate row-level convergence and output reveal.
4. Render video and poster.
5. Extract proof frames and iterate on spacing or hierarchy.
