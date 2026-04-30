# Palette, Stage, And Transparency

Read this when deciding whether a Manim clip should stay transparent, gain a local background, or be color-normalized.

For exact token names and preferred values, use [preferred-color-styles.md](preferred-color-styles.md). This file focuses on when and why those colors should appear.

## Canonical Color Roles

Use the ADR-0002 palette as semantic roles, not decoration:

- `primary-green`, `primary-blue`, `primary-purple`: structural actors or state groups.
- `primary-orange`: routes, guides, bridges, funnels, sleeves, gates, and causal mechanisms.
- `primary-yellow`: transient pulses, pivots, cores, focus marks, and attractor points.
- `primary-red`: return paths, warnings, response paths, or deliberate tension.
- `gray-*`: scaffolding, frames, shadows, inactive paths, and low-emphasis text.
- `page-background`: local backing for text-heavy or diagram-heavy transparent clips.

Avoid default Manim color constants in spike scripts unless the spike is intentionally testing a non-canonical style.

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
stage = RoundedRectangle(
    width=12.8,
    height=7.15,
    corner_radius=0.34,
    stroke_width=0,
    fill_color=PAGE_BACKGROUND,
    fill_opacity=0.96,
)
self.add(stage)
```

For portrait clips, shrink width and expand height:

```python
stage = RoundedRectangle(
    width=6.95,
    height=12.75,
    corner_radius=0.34,
    stroke_width=0,
    fill_color=PAGE_BACKGROUND,
    fill_opacity=0.96,
)
```

## Drift Checks

Before finalizing a repo-wide pass:

```powershell
rg -n "PRIMARY_PRIMARY|HIGHLIGHT_PRIMARY|BRAND_GRAY|GRAY_[A-Z]\b|BLUE_[A-E]|GREY_[A-E]|GREEN_E|TEAL_|\bBLACK\b|#0b1120" spikes --glob main.py
```

Also check literal hex values against ADR-0002. Non-canonical hex values should be rare and intentional.
