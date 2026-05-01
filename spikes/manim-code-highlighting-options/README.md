---
title: Manim Code Highlighting Options
status: draft
date: 2026-05-01
---

# Purpose

Create a visual spike for showing programming code in Manim, with one compact example per language and a focused comparison of code-highlighting options.

# Hypothesis

If `Code` examples are grouped by language and paired with normal Manim overlay tactics, then the practical options for code presentation become clearer than a static API list.

# Coverage

This spike visualizes the Manim Community v0.20.1 `Code` mobject options documented at:

<https://docs.manim.community/en/stable/reference/manim.mobject.text.code_mobject.Code.html>

Covered built-in `Code` options:

- `code_string`
- `language`
- `formatter_style`
- `tab_width`
- `add_line_numbers`
- `line_numbers_from`
- `background`
- `background_config`
- `paragraph_config`
- `Code.get_styles_list()`

Covered overlay tactics:

- line wash highlight,
- line start cursor,
- token or region outline from `code_lines`,
- style swatches for `formatter_style`,
- persistent final summary suitable for slide review.

# Implementation Note

The scene uses rasterized Pygments previews for the six compact code cards, because animating many native `Code` mobjects keeps hundreds of glyph paths live on every frame. This preserves the same syntax-highlighting source that `Code` uses, while the explanatory emphasis remains normal Manim geometry.

Use native `Code` directly when the scene has one or two code blocks that need vector-level transforms. Use the rasterized preview pattern when the slide needs a dense gallery of languages or styles.

# Languages

The scene includes one code listing for each language:

- Python
- TypeScript
- Rust
- Go
- SQL
- Bash

# Run

```bash
uv run --script spikes/manim-code-highlighting-options/main.py
```

For a faster local pass:

```bash
uv run --script spikes/manim-code-highlighting-options/main.py --quality low
```

# Output

The render writes:

- `videos/manim-code-highlighting-options/manim-code-highlighting-options.webm`
- `videos/manim-code-highlighting-options/manim-code-highlighting-options.png`

The WebM uses transparency with a local page-background stage so it remains readable when embedded in Slidev.
