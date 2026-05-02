# Code Options And Highlighting

Use this reference when a Manim scene needs programming-language code snippets, syntax-highlighting comparisons, or narrated emphasis over source code.

## Choose Native Code Or Rasterized Previews

Use native Manim `Code` when the scene has one or two listings and the code itself needs vector-level transforms or direct `code_lines` access.

Use rasterized Pygments previews when the scene is a dense gallery of languages, styles, or snippets. `Code` is vector-heavy because each rendered glyph becomes geometry; a grid of listings can make even low-quality WebM renders slow.

The rasterized pattern is:

1. Render each snippet to PNG with Pygments using the same lexer and style names that `Code` uses.
2. Load the PNGs as `ImageMobject`s.
3. Keep all explanation overlays as native Manim geometry: rectangles, line markers, token boxes, cursors, and pulses.
4. Document that the snippets are rasterized for performance.

## Code Constructor Options

| Option | Use When | Notes |
| --- | --- | --- |
| `code_file` | Showing source from a real file. | Good for examples tied to checked-in code. |
| `code_string` | Showing compact teaching snippets. | Best for small slide cards and generated snippets. |
| `language` | The lexer must be stable. | Prefer explicit language names; auto-detection can be unreliable. |
| `formatter_style` | Comparing syntax themes. | Use `Code.get_styles_list()` in the local environment. |
| `tab_width` | Indentation density matters. | Use `2` for compact slide cards, `4` for conventional source display. |
| `add_line_numbers` | Referencing lines in narration. | Disable for tiny swatches. |
| `line_numbers_from` | Showing an excerpt from a larger source file. | Keeps references aligned to the original file. |
| `background` | The listing needs a native frame. | Use `rectangle` for clean slide cards or `window` when the shell metaphor matters. |
| `background_config` | The frame must match the project palette. | Set fill, opacity, stroke, and buffer. |
| `paragraph_config` | Text needs readable typography. | Set monospace font and font size before scaling. |

## Highlighting Patterns

- Use syntax highlighting only for lexical categories.
- Use a semi-opaque line wash for the current line.
- Use a narrow primary-red marker at the line start when the active line must be visible in thumbnails.
- Use `SurroundingRectangle` around a `code_lines` slice for native `Code` token or region emphasis.
- Use an animated thin rectangle as an execution cursor or scan pass.
- Use a short diff flash or outline for changed regions.

## Layout Rules

- Keep gallery snippets to two to four lines.
- Shorten real source code before scaling it below readability.
- Compare languages using one formatter style; compare formatter styles using one tiny snippet.
- Give code cards a local white or page-background stage unless the formatter style is intentionally dark.
- Keep the project primary palette in headers and accents, not token colors.
- For dense code galleries, reserve a measured title/subtitle band before placing cards or option panels. Header collisions can be easy to miss in contact-sheet thumbnails and obvious at full size.
- Do not spend frame zero fading in a dense scaffold. Add the initial code grid, option panel, or receiver structure before the opening wait, then use the breath for reading.
- Keep terminal holds calmer than the teaching beat. Fade broad washes or transient row highlights, and leave at most one durable code-region cue plus any short summary badge.
- Keep summary badges inside the local stage with visible bottom clearance. If the badge sits on the stage edge, it reads as a footer artifact rather than a resolved state.
