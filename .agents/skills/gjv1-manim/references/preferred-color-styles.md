# Preferred Color Styles

This is the skill-local canonical color reference. Use these tokens in GJV1 Manim examples and copied spikes unless a spike explicitly documents a different style direction.

Any future color-system change must update this file directly. Do not make this reference depend on a project ADR, web page, external repository, or any other source outside this skill directory.

## Primary Palette

- `PRIMARY_RED = "#9e1b32"`
- `PRIMARY_ORANGE = "#e77204"`
- `PRIMARY_YELLOW = "#f1c319"`
- `PRIMARY_GREEN = "#45842a"`
- `PRIMARY_BLUE = "#007298"`
- `PRIMARY_PURPLE = "#652f6c"`

## Neutral And Stage Tokens

- `BLACK = "#000000"`
- `WHITE = "#ffffff"`
- `GRAY = "#333e48"`
- `PAGE_BACKGROUND = "#f7f7f7"`
- `GRAY_100 = "#e7e7e7"`
- `GRAY_200 = "#cfcfcf"`
- `GRAY_300 = "#b5b5b5"`
- `GRAY_400 = "#9c9c9c"`
- `GRAY_500 = "#828282"`
- `GRAY_600 = "#696969"`
- `GRAY_700 = "#4f4f4f"`
- `GRAY_800 = "#363636"`
- `GRAY_900 = "#1c1c1c"`

## Highlight Tokens

- `HIGHLIGHT_RED = "#ffccd5"`
- `HIGHLIGHT_ORANGE = "#ffe5cc"`
- `HIGHLIGHT_YELLOW = "#fff4cc"`
- `HIGHLIGHT_GREEN = "#dbffcc"`
- `HIGHLIGHT_BLUE = "#cdf3ff"`
- `HIGHLIGHT_PURPLE = "#f9ccff"`

## Shadow Tokens

- `SHADOW_RED = "#6d1222"`
- `SHADOW_ORANGE = "#994a00"`
- `SHADOW_YELLOW = "#98700c"`
- `SHADOW_GREEN = "#294d19"`
- `SHADOW_BLUE = "#004d66"`
- `SHADOW_PURPLE = "#431f47"`

## Status Tokens

- `STATUS_RED = "#e8002a"`
- `STATUS_ORANGE = "#ff9633"`
- `STATUS_YELLOW = "#ffd332"`
- `STATUS_GREEN = "#36b300"`
- `STATUS_BLUE = "#00ace6"`
- `STATUS_PURPLE = "#9e00b3"`

## Role Rules

- Default to `WHITE` or `PAGE_BACKGROUND` as the stage, `BLACK` and `GRAY_*` for text and structure, and `PRIMARY_RED` for the single active accent, warning, selected path, or return route.
- Use `GRAY_*` tokens for scaffolding, frames, inactive text, support geometry, panels, table rules, guide rails, and quiet shadows.
- Use `PRIMARY_RED`, `HIGHLIGHT_RED`, `SHADOW_RED`, and `STATUS_RED` for the default accent family.
- Use `PRIMARY_ORANGE`, `PRIMARY_YELLOW`, `PRIMARY_GREEN`, `PRIMARY_BLUE`, `PRIMARY_PURPLE`, and their highlight, shadow, or status variants only when the user asks for a colored result, when a spike explicitly tests color, or when several simultaneous categories cannot be understood with red plus grayscale.
- Use `PAGE_BACKGROUND` for local stages behind text-heavy or diagram-heavy clips.
- Use `WHITE` as the default review background.

## Typography

- Prefer the CSS-like family order `"Open Sans", Arial, sans-serif`.
- In Manim, set `font="Open Sans"` for normal `Text` labels and allow the renderer or system to fall back to Arial or a sans-serif face if Open Sans is unavailable.
- Keep labels sparse, smaller than the moving geometry, and aligned to a square grid.

## Geometry Defaults

- Prefer straight rectangular edges and square corners.
- Set `corner_radius=0` when a `RoundedRectangle` is unavoidable, or use `Rectangle` for panels, badges, cards, tracks, table cells, and stage blocks.
- Use rounded geometry only when the spike explicitly tests rounded forms or a physical mechanism needs curvature.

## Example Requirements

- Example scripts should define colors as named constants from this reference or copy from `assets/manim_scene_helpers.py`.
- Avoid default Manim color constants such as `BLUE`, `GREEN`, `BLACK`, or `WHITE` in examples; use project tokens instead.
- Literal hex values in examples should match this reference. Non-canonical colors need a short comment explaining the intentional exception.
