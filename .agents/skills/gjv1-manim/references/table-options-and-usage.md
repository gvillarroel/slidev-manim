# Table Options And Usage

Use this reference when a Manim scene needs a readable table, a table-driven calculation, or a visual survey of table options.

## Choose Table Or Custom Geometry

Use Manim `Table` when the scene needs a stable rectangular grid, readable labels, and table-native helpers for rows, columns, entries, highlights, and rules.

Use custom geometry when the table needs many independent animated cells, scrolling, responsive widths, nested badges, or layouts where label indexing would make the code harder to trust.

## Constructor Options

| Option | Use When | Notes |
| --- | --- | --- |
| `table` | You have raw 2D data. | Entries can be strings, numbers, or VMobjects. |
| `row_labels` | Rows have semantic identities. | Good for row-by-row transformations. |
| `col_labels` | Columns are the main roles. | Good for source, operator, and result columns. |
| `top_left_entry` | Row and column labels are both present. | Makes the visible corner explicit and easier to index. |
| `v_buff`, `h_buff` | You need denser or airier tables. | Compact galleries need smaller buffers; slide-readable tables need more space. |
| `include_outer_lines` | The table needs a strong boundary. | Useful for standalone tables and comparison panels. |
| `line_config` | Grid rules need hierarchy. | Keep default structure gray; reserve strong color for active rule roles. |
| `arrange_in_grid_config` | Alignment matters. | Use `cell_alignment` for numeric columns or compact API galleries. |
| `element_to_mobject` | Entries need controlled conversion. | Prefer a local wrapper around `Text` for font, size, and color. |
| `element_to_mobject_config` | Entry style is uniform. | Good for quick text styling. |
| `add_background_rectangles_to_entries` | Every entry needs a backplate. | Useful for overlays, but noisy in dense tables. |
| `entries_background_color` | Entry backplates need a tint. | Use highlight colors with restrained opacity. |
| `include_background_rectangle` | The whole table needs a backing. | Useful for transparent videos with text. |
| `background_rectangle_color` | The backing needs a stage color. | Usually white or page-background. |

## Helper Methods

| Method | Use When | Notes |
| --- | --- | --- |
| `create()` | The table should build on screen. | Good for the first reveal, then settle quickly. |
| `get_cell(pos)` | A specific cell needs an outline or custom fill. | Positions are 1-based. |
| `get_highlighted_cell(pos)` | You need a highlight object before adding it. | Add behind entries when readability matters. |
| `add_highlighted_cell(pos)` | A persistent quick highlight is enough. | Less flexible than managing the returned object. |
| `add_background_to_entries()` | All entries need text backplates. | Use sparingly. |
| `get_entries()` | You need rendered entries including labels. | Verify indexing when labels exist. |
| `get_entries_without_labels()` | You need data cells only. | Preferred for calculations and row work. |
| `get_labels()` | All labels should share style or motion. | Useful after establishing the table. |
| `get_row_labels()` | Row identity is active. | Pair with row cursors. |
| `get_col_labels()` | Column identity is active. | Pair with column colors or formula roles. |
| `get_rows()` | A row is the active unit. | Use for row outlines or row focus rules. |
| `get_columns()` | A column is the active unit. | Use for source/result columns. |
| `get_horizontal_lines()` | Row rules need emphasis. | Good for lanes and section breaks. |
| `get_vertical_lines()` | Column rules need emphasis. | Good for input/output separation. |
| `set_column_colors()` | Columns represent roles or categories. | This colors entries, not cell backgrounds. |
| `set_row_colors()` | Rows represent states or phases. | Best with few rows. |
| `scale()` | The table needs to fit the shot. | Use `scale_stroke=True` when line thickness should shrink too. |

## Scene Patterns

### Static Reference Table

Use `row_labels`, `col_labels`, `top_left_entry`, `include_outer_lines`, and neutral `line_config`. Keep motion outside the table unless the table is the lesson.

### Formula Handoff

Use `get_entries_without_labels()`, `get_columns()`, and `get_rows()`. Pulse source cells first, compose the formula in a side zone, then transform the result into the destination cell.

### Classification Table

Use a row cursor, `get_rows()`, and one aligned side badge column. Keep badges outside the table so they do not cover source text or destination values.

### Options Gallery

Group options into pages: constructor variants, backgrounds, cell helpers, accessors, line helpers, and color setters. If a page has one sparse table under a fixed title, move the table and side legend lower as one core composition instead of adding a disconnected footer.

### Transparent Slide Clip

If the table has labels or dark text, give it a local page-background stage or a whole-table background rectangle. Keep full transparency only for low-text decorative table layers.

## Indexing Rules

- Positions are 1-based.
- `get_entries()` includes labels.
- `get_entries_without_labels()` addresses data cells only and is usually safer for calculations.
- Use `top_left_entry` when both row and column labels exist so the visible grid is explicit.
- Always sample a proof frame after adding labels; label indexing can make code that looked obvious point at a different visible cell.

## Visual Rules

- Keep grid lines gray unless a line is the active concept.
- Use one accent family at a time for the active row, column, or cell.
- Prefer a left row marker plus a thin row rule over a filled row band.
- Keep formula badges, callouts, and temporary values out of table cells.
- Review both the active mechanism frame and the resolved hold.

## Validation

Render the real video, then audit sampled frames:

```bash
uv run --script spikes/<spike-name>/main.py
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<spike-name>.webm --cadence 0.5 --write-overlays
```

Open flagged frames full size. Table grid lines and text often trigger broad crowding notices; patch only when actual text, cell values, or stale support geometry collide.
