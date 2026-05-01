---
id: KNOW-0007
title: Manim Table options reference
status: active
date: 2026-05-01
---

# Summary

Use Manim `Table` when the scene needs a real grid with readable cells, row or column roles, and table-native accessors. Use custom Manim geometry when every cell needs independent layout, non-rectangular structure, or heavy per-cell animation that fights the built-in table model.

The companion spike is `spikes/manim-table-options/`. It renders a visual survey of constructor options and helper methods.

# First Decision

Use `Table` for:

- compact tabular data with 2 to 6 rows or columns,
- row-by-row calculations or classifications,
- visual explanation of accessors, highlights, column roles, or line styling,
- Slidev clips where the table remains readable as a stable object while accents move around it.

Use custom cell geometry for:

- large data tables that need responsive column widths,
- cells with complex nested content, badges, sparklines, or multiple moving parts,
- row virtualization, scrolling, or camera tours,
- designs where labels, gutters, and cell highlights must ignore Manim `Table` indexing behavior.

# Constructor Options

| Option | Use When | Notes |
| --- | --- | --- |
| `table` | You have the raw 2D data. | Entries can be strings, numbers, or VMobjects. |
| `row_labels` | Rows have stable semantic roles. | Good for datasets, transactions, categories, and matrix rows. |
| `col_labels` | Columns are the main reading path. | Use for derived-column, comparison, and formula scenes. |
| `top_left_entry` | Both row and column labels are present. | Makes the visible grid explicit and avoids an ambiguous blank corner. |
| `v_buff`, `h_buff` | You need denser or airier tables. | Reduce for compact galleries; increase for presentation-readable data. |
| `include_outer_lines` | The table needs a strong boundary. | Useful for standalone tables and comparison panels. |
| `line_config` | Grid rules need hierarchy. | Use gray for structure; reserve strong color for active line roles. |
| `arrange_in_grid_config` | Cell alignment matters. | Use `cell_alignment` for right-aligned numeric columns or centered labels. |
| `element_to_mobject` | Entries need consistent text or custom conversion. | Prefer a local wrapper around `Text` for font, size, and color control. |
| `element_to_mobject_config` | Text style is simple and uniform. | Faster than manual styling every entry after creation. |
| `add_background_rectangles_to_entries` | Each entry needs a local backplate. | Good for low-contrast overlays; can add visual noise in dense tables. |
| `entries_background_color` | Entry backplates need a semantic tint. | Use highlight tokens and keep opacity quiet. |
| `include_background_rectangle` | The whole table needs one readable backing. | Useful for transparent WebM clips over Slidev backgrounds. |
| `background_rectangle_color` | The table backing needs a review or slide surface. | Usually `white` or `page-background`. |

# Helper Methods

| Method | Use When | Notes |
| --- | --- | --- |
| `create()` | You want the table to appear as a built object. | Good for an API gallery or first reveal; keep the final table stable afterward. |
| `get_cell(pos)` | You need a polygon outline for one cell. | Use for crisp focus boxes or custom fills; positions are 1-based. |
| `get_highlighted_cell(pos)` | You need a highlight object before adding it. | Add it behind the table with `add_to_back()` when the table should own the layer stack. |
| `add_highlighted_cell(pos)` | You want a quick persistent highlight. | Fast for static emphasis; less flexible than managing the returned highlight yourself. |
| `add_background_to_entries()` | Every entry needs a text backplate. | Use sparingly; it can make small tables look busy. |
| `get_entries()` | You need all rendered entries or one rendered entry. | Includes labels. Verify indexing when labels are present. |
| `get_entries_without_labels()` | You only want data cells. | Best for data transformations, calculations, and row-by-row pulses. |
| `get_labels()` | Labels should share a style or animation. | Useful for de-emphasizing headers after the table is established. |
| `get_row_labels()` | Row labels carry identity. | Color or pulse row labels during row-level work. |
| `get_col_labels()` | Column labels carry identity. | Color source, operator, and destination columns. |
| `get_rows()` | A row is the active unit. | Use with `SurroundingRectangle`, row cursors, or subtle bottom rules. |
| `get_columns()` | A column is the active unit. | Use for source columns, destination columns, or column-level role colors. |
| `get_horizontal_lines()` | Horizontal rules need emphasis or removal. | Use for row lanes, section breaks, or table-rule hierarchy. |
| `get_vertical_lines()` | Vertical rules need emphasis or removal. | Use for column lanes or separating input/output regions. |
| `set_column_colors()` | Columns represent categories or formula roles. | This colors entries, not backgrounds; pair with neutral grid lines. |
| `set_row_colors()` | Rows represent states, groups, or phases. | Works best when rows are few and labels remain readable. |
| `scale()` | The whole table needs to fit the shot. | Use `scale_stroke=True` when thick grid lines should shrink with the table. |

# Patterns

## Static Reference Table

Use `Table` with `col_labels`, `row_labels`, `top_left_entry`, `include_outer_lines`, and quiet `line_config`.

Prefer this when the table is reference material and not the main moving mechanism.

## Derived Column Or Formula Handoff

Use `get_entries_without_labels()`, `get_columns()`, `get_rows()`, and a side formula zone.

Pulse source cells first, compose the formula away from dense table cells, then transform the result into the destination cell. Do not leave transient result text on top of final cell text.

## Classification Or Rule Table

Use row labels, a row cursor, `get_rows()`, and a side badge.

The row should be visibly active before the side badge appears. Keep badges aligned to one side column rather than positioning each badge from its cell.

## API Gallery Or Options Survey

Use small tables and group related options into pages:

- constructor variants,
- background and entry conversion,
- cell helpers,
- read accessors,
- line and color setters.

If the page has a fixed top title and one sparse table, move the table and side legend lower as one core composition. A disconnected footer does not fix top-heavy framing.

## Slidev Transparent Clip

If the table contains labels or dark text, add a local `page-background` stage or a table-level background rectangle. Transparent clips are only safe without local backing when the slide surface supplies contrast and the table has minimal text.

# Indexing Rules

- Table positions are 1-based.
- Label-heavy tables need explicit proof frames because `get_entries()` includes labels while `get_entries_without_labels()` does not.
- Prefer `top_left_entry` when using both row and column labels; it makes the rendered grid easier to reason about.
- For data-cell animation, prefer `get_entries_without_labels((row, col))` so the code addresses the data region rather than the rendered label grid.

# Visual Rules

- Keep grid lines gray unless the line itself is the lesson.
- Use one active accent at a time for the current row, column, or cell.
- Use fills for meaning only when the table is sparse; filled bands can overpower numbers.
- Use a left row marker plus a thin row rule before using a full filled row highlight.
- Keep formula badges and side labels out of table cells.
- Sample both the mechanism frame and the resolved frame before accepting the scene.

# Validation

For table-heavy scenes:

```bash
uv run --script spikes/<spike-name>/main.py
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<spike-name>.webm --cadence 0.5 --write-overlays
```

Open flagged frames full size. Table grid lines and text can trigger `possible_overlap_or_crowding`; treat it as blocking only when the overlay shows actual text collision, cell occlusion, or support geometry left after it stops explaining the motion.
