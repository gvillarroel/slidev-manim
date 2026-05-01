---
title: Slidev Transition Showcase
status: active
date: 2026-04-30
---

# Slidev Transition Showcase

## Purpose

This spike creates a Slidev deck that demonstrates the current built-in Slidev transition set and additional custom transitions in one recorded video.

The deck also includes code blocks, Mermaid diagrams, KaTeX, tables, view-transition naming, click animations, motion directives, rough markers, Shiki Magic Move, and custom Vue transitions so the video can be used as a broad Slidev feature check.

## Transition Coverage

The visible transition into each target slide is controlled by the previous slide's frontmatter:

- slide 2: source slide 1 uses `fade` with high-contrast route proof blocks and a 1.5 second built-in transition duration
- slide 3: source slide 2 uses `fade-out` with high-contrast route proof blocks and a 1.5 second built-in transition duration
- slide 4: source slide 3 uses `slide-left`
- slide 5: source slide 4 uses `slide-right`
- slide 6: source slide 5 uses `slide-up`
- slide 7: source slide 6 uses `slide-down`
- slide 8: source slide 7 uses `view-transition`
- slide 9: source slide 8 uses `pulse-route` custom transition with an obvious clip-path, rotation, blur, and lateral move
- slide 10: source slide 9 uses `fade`
- slide 11: source slide 10 uses `zoom-route` custom transition
- slide 12: source slide 11 uses `rotate-route` custom transition
- slide 13: source slide 12 uses `curtain-route` custom transition
- slide 14: source slide 13 uses `blur-route` custom transition
- slide 15: source slide 14 uses `diagonal-route` custom transition
- slide 16: source slide 15 uses `stack-route` custom transition

## Code Highlighting Coverage

The recorder advances same-slide click stages so dynamic code highlighting can be seen in the video:

- slide 2: 4 highlight stages
- slide 3: 3 highlight stages
- slide 5: 4 highlight stages
- slide 9: 2 highlight stages
- slide 10: code/action highlight is driven by `$clicks` and does not register extra click stages
- slide 11: code/action highlight is driven by `$clicks` and does not register extra click stages
- slide 12: 2 total click stages for `v-switch`; the initial `Parse` state is visible at click 0
- slide 13: 3 total click stages shared by code highlighting and `v-motion`

Each highlight or animation stage is held for 1.8 seconds after a 450 ms settle delay.

## Slide Animation Coverage

The appended slides add the main interactive animation primitives from the local Slidev 52.14.2 install:

- slide 10: `v-click`, `v-after`, click ranges, and `v-click-hide`
- slide 11: `<v-clicks>` with nested list depth and hidden-until-click items
- slide 12: `<v-switch>` with an internal transition
- slide 13: `v-motion` enter and click variants
- slide 14: Shiki Magic Move code morphing
- slide 15: `v-mark` rough annotations

The recorder uses a strict click plan. If `ArrowRight` does not leave a slide after the planned click stages, the recording fails instead of navigating directly, because direct navigation would hide missing in-slide animation stages.

## Run the Video Render

From the repository root:

```bash
uv run --script spikes/slidev-transition-showcase/main.py
```

The default render is 1920x1080. The loader-trim pass re-encodes the WebM at 14 Mbps so the final review video keeps code and Mermaid details legible.

This writes the rendered video and review images to:

```text
videos/slidev-transition-showcase/
```

Expected outputs:

```text
videos/slidev-transition-showcase/slidev-transition-showcase.webm
videos/slidev-transition-showcase/screenshots/slide-01.png
videos/slidev-transition-showcase/screenshots/slide-02-click-01.png
videos/slidev-transition-showcase/screenshots/slide-14-click-03.png
videos/slidev-transition-showcase/review-frames/frame-start.png
videos/slidev-transition-showcase/review-frames/frame-middle.png
videos/slidev-transition-showcase/review-frames/frame-final.png
videos/slidev-transition-showcase/review-frames/intent-vs-actual.json
videos/slidev-transition-showcase/review-frames/video-quality-review.json
videos/slidev-transition-showcase/review-frames/custom-transition-final.png
videos/slidev-transition-showcase/review-frames/all-slides-final.png
videos/slidev-transition-showcase/review-frames/route-transition-sweep-final.png
videos/slidev-transition-showcase/review-frames/fade-final.png
videos/slidev-transition-showcase/review-frames/fade-out-final.png
videos/slidev-transition-showcase/review-frames/slide-11-list-clicks.png
videos/slidev-transition-showcase/review-frames/view-transition-final/t62.4.png
```

## Run the Slidev Deck

From the repository root:

```bash
npx slidev spikes/slidev-transition-showcase/slides.md
```

To build the deck:

```bash
npx slidev build spikes/slidev-transition-showcase/slides.md
```

## Notes

- The video recording uses real browser navigation so the slide transitions are visible.
- Each slide is held for at least 3 seconds by default.
- Fade and fade-out route transitions use high-contrast proof blocks because the default opacity animation can disappear against mostly white slides.
- Custom route transitions should be validated from frames sampled during navigation; a subtle fade on a white slide can be technically correct but visually useless.
- Dynamic code highlight stages are recorded as same-slide clicks instead of being skipped by route navigation.
- In-slide animations are recorded with explicit click stages so they are contained in the final WebM.
- Undercounted click plans are treated as recording failures.
- Feedback-driven iterations compare intended visible elements and highlighted lines against the active rendered slide before accepting the video.
- The view transition is validated from sampled video frames, not only from the target slide screenshot.
- The recorder saves one screenshot per slide before advancing, which makes layout review faster than inspecting the full video manually.
