---
id: KNOW-0008
title: Manim Code options reference
status: active
date: 2026-05-01
---

# Summary

Use Manim `Code` for syntax-highlighted source listings when a scene has one or two code blocks. For dense galleries of languages or formatter styles, rasterize the listings with Pygments and animate normal Manim geometry on top. This keeps the scene fast while preserving the same highlighting source.

The companion spike is `spikes/manim-code-highlighting-options/`.

# Built-In Code Options

| Option | Use When | Notes |
| --- | --- | --- |
| `code_file` | The code lives in a real source file. | Good when the spike should display checked-in code. |
| `code_string` | The snippet is small or generated. | Best for option galleries and short teaching examples. |
| `language` | The lexer must be explicit. | Prefer explicit language names; automatic detection can be flaky. |
| `formatter_style` | You need a Pygments theme. | Use `Code.get_styles_list()` to inspect available styles in the installed version. |
| `tab_width` | Indentation needs control. | Use `2` for compact slide snippets; use `4` when matching source code conventions. |
| `add_line_numbers` | Line references matter. | Turn off for tiny swatches. |
| `line_numbers_from` | The snippet is extracted from a larger file. | Useful when narration refers to original file line numbers. |
| `background` | The listing needs a frame style. | Manim supports `rectangle` and `window`. |
| `background_config` | The frame needs project styling. | Set fill, opacity, stroke, and buffer to match the slide surface. |
| `paragraph_config` | Text needs font and size control. | Use a monospace font and tune `font_size` before scaling the whole block. |

# Highlighting Patterns

Use built-in syntax highlighting for lexical categories only. Use normal Manim mobjects for narrative emphasis:

- line wash: place a semi-opaque `Rectangle` behind the active line,
- line marker: add a narrow accent bar at the line start,
- token or region box: draw a `SurroundingRectangle` around a `code_lines` slice when using native `Code`,
- execution cursor: animate a thin rectangle across the line,
- diff pulse: draw or fade a colored outline around changed lines.

# Performance Rule

Native `Code` is vector-heavy because every rendered glyph becomes geometry. A single large listing is usually fine. A grid of many `Code` listings can make even low-quality WebM renders slow.

For gallery-style scenes:

1. Render snippets to PNG with Pygments.
2. Load them with `ImageMobject`.
3. Keep all highlights as Manim rectangles, outlines, cursors, and pulses.
4. Document that the preview is rasterized for performance.

# Visual Rules

- Keep snippets shorter than normal source code; line wrapping and scaling make code unreadable quickly.
- Prefer two to four visible lines per card in a multi-language gallery.
- Use one formatter style across language cards when comparing languages.
- Compare formatter styles with the same tiny snippet.
- Keep code cards on a local white or page-background stage unless the style is intentionally dark.
- Use the project primary palette for language headers, but avoid making token colors compete with the header.

# Validation

Render the spike and sample opening, language-pulse, option-panel, overlay, and final-hold frames:

```bash
uv run --script spikes/manim-code-highlighting-options/main.py --quality low
```

Check full-size frames, not only thumbnails. Code text that looks acceptable in a contact sheet can still be too small or too washed out in the actual frame.
