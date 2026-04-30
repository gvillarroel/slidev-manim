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

- Use `PRIMARY_GREEN`, `PRIMARY_BLUE`, `PRIMARY_PURPLE`, and `PRIMARY_RED` for structural actors, states, destinations, warnings, or deliberate tension.
- Use `PRIMARY_ORANGE` for routes, guides, bridges, funnels, sleeves, gates, formula borders, and causal mechanisms.
- Use `PRIMARY_YELLOW` for transient pulses, pivots, attractor cores, focus marks, and momentary attention.
- Use `HIGHLIGHT_*` tokens for low-pressure fills behind the matching primary role.
- Use `GRAY_*` tokens for scaffolding, frames, inactive text, and support geometry.
- Use `PAGE_BACKGROUND` for local stages behind text-heavy or diagram-heavy clips.
- Use `WHITE` as the default review background and as text on primary-color backgrounds.

## Example Requirements

- Example scripts should define colors as named constants from this reference or copy from `assets/manim_scene_helpers.py`.
- Avoid default Manim color constants such as `BLUE`, `GREEN`, `BLACK`, or `WHITE` in examples; use project tokens instead.
- Literal hex values in examples should match this reference. Non-canonical colors need a short comment explaining the intentional exception.
