---
title: Manim Table Options
status: draft
date: 2026-05-01
---

# Purpose

Create a visual lab for Manim Community `Table` options and helper methods.

# Hypothesis

If the API surface is grouped into constructor variants, cell helpers, accessors, line helpers, and color setters, then the useful `Table` options are easier to compare than isolated documentation examples.

# Coverage

This spike exercises the Manim Community v0.20.1 `Table` API documented at:

<https://docs.manim.community/en/stable/reference/manim.mobject.table.Table.html>

For option-level guidance and when to use each method, see:

- `.specs/knowledge/manim-table-options-reference.md`

Covered constructor options:

- `table`
- `row_labels`
- `col_labels`
- `top_left_entry`
- `v_buff`
- `h_buff`
- `include_outer_lines`
- `add_background_rectangles_to_entries`
- `entries_background_color`
- `include_background_rectangle`
- `background_rectangle_color`
- `element_to_mobject`
- `element_to_mobject_config`
- `arrange_in_grid_config`
- `line_config`

Covered helper methods:

- `add_background_to_entries`
- `add_highlighted_cell`
- `create`
- `get_cell`
- `get_col_labels`
- `get_columns`
- `get_entries`
- `get_entries_without_labels`
- `get_highlighted_cell`
- `get_horizontal_lines`
- `get_labels`
- `get_row_labels`
- `get_rows`
- `get_vertical_lines`
- `scale`
- `set_column_colors`
- `set_row_colors`

# Run

```bash
uv run --script spikes/manim-table-options/main.py
```

For a faster local pass:

```bash
uv run --script spikes/manim-table-options/main.py --quality low
```

# Output

The render writes:

- `videos/manim-table-options/manim-table-options.webm`
- `videos/manim-table-options/manim-table-options.png`

The video uses a neutral local stage so the table labels are readable when embedded in Slidev.
