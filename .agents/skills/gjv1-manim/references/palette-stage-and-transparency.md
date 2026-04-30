# Palette, Stage, And Transparency

Read this when deciding whether a Manim clip should stay transparent, gain a local background, or be color-normalized.

For exact token names and preferred values, use [preferred-color-styles.md](preferred-color-styles.md). This file focuses on when and why those colors should appear.

## Canonical Color Roles

Use the skill-local palette as semantic roles, not decoration. The default style is red, black, and grayscale on white:

- `white` or `page-background`: stage surface and local backing for text-heavy or diagram-heavy transparent clips.
- `black`: primary text, axes, stable outlines, and the strongest neutral actor.
- `gray-*`: scaffolding, frames, shadows, inactive paths, low-emphasis text, panels, cards, cells, and guide rails.
- `primary-red`: active accent, selected path, warning, response path, return path, pulse, or final focus mark.
- `primary-orange`, `primary-yellow`, `primary-green`, `primary-blue`, `primary-purple`: extended palette for explicitly colorful scenes or categorical views that need more separation than red plus grayscale.

Avoid default Manim color constants in spike scripts unless the spike is intentionally testing a non-canonical style.

## Typography

Use `Open Sans` for Manim `Text` where available. The intended fallback stack is `"Open Sans", Arial, sans-serif`.

## Geometry

Use straight edges and square corners by default. Use `Rectangle` for panels, cards, badges, bars, table cells, local stages, and support blocks. If a `RoundedRectangle` is unavoidable, set `corner_radius=0` unless the spike explicitly tests rounded geometry.

## Stage Decision

Use a local `page-background` stage when the video contains:

- labels or captions,
- timeline cards,
- diagram nodes,
- dark text,
- arrows with explanatory text,
- poster-compatible output that must be inspectable outside Slidev.

Keep transparency when the clip is a decorative layer:

- ambient orbital loops,
- tiny support loops,
- no text,
- no diagram labels,
- intended to sit over a Slidev background or card that supplies contrast.

Do not treat every black PyAV review frame as a defect. PyAV composites transparent frames over black unless the review script explicitly composites alpha over a background.

## Minimum Local Stage Pattern

Use a neutral stage behind explanatory content:

```python
stage = Rectangle(
    width=12.8,
    height=7.15,
    stroke_width=0,
    fill_color=PAGE_BACKGROUND,
    fill_opacity=0.96,
)
self.add(stage)
```

For portrait clips, shrink width and expand height:

```python
stage = Rectangle(
    width=6.95,
    height=12.75,
    stroke_width=0,
    fill_color=PAGE_BACKGROUND,
    fill_opacity=0.96,
)
```

## Drift Checks

Before finalizing a repo-wide pass:

```powershell
rg -n "PRIMARY_PRIMARY|HIGHLIGHT_PRIMARY|BRAND_GRAY|GRAY_[A-Z]\b|BLUE_[A-E]|GREY_[A-E]|GREEN_E|TEAL_|#0b1120" spikes --glob main.py
```

Also check literal hex values against [preferred-color-styles.md](preferred-color-styles.md). Non-canonical hex values should be rare and intentional.
