---
name: gjv1-slidev
description: Use when creating, refining, validating, or recording Slidev presentations in this repository, especially Slidev decks under spikes/*/slides.md that need code blocks, Mermaid diagrams, built-in or custom slide transitions, timed navigation, screenshot checks, or conversion into a shareable browser-recorded WebM video.
---

# Purpose

Use this skill to build Slidev decks that work as real presentations and can be recorded into timed videos for review or sharing.

# Core Rule

Treat the browser deck as the source of truth. Build the Markdown, run Slidev, record or screenshot the real rendered deck, and fix layout issues seen in the rendered output before shipping.

When the user gives visual feedback on a rendered Slidev video, update this skill with the reusable lesson before finishing the iteration.

# Repository Shape

- Put each experiment in `spikes/<spike-name>/`.
- Keep the Slidev entry at `spikes/<spike-name>/slides.md`.
- Add `spikes/<spike-name>/README.md` with exact run commands.
- Add `spikes/<spike-name>/main.py` when the deck needs generated assets or a repeatable video recording command.
- Write generated videos, screenshots, and review frames to `videos/<spike-name>/`.
- Add `dev:<spike-name>` and `build:<spike-name>` scripts to the root `package.json` when a deck is meant to be reused.

# Visual Defaults

Use the project palette and a quiet, inspectable layout:

- `#f7f7f7` page background
- `#333e48` text
- `#000000` strong text
- `#ffffff` panels
- primary accents: red `#9e1b32`, orange `#e77204`, yellow `#f1c319`, green `#45842a`, blue `#007298`, purple `#652f6c`
- highlight fills: red `#ffccd5`, orange `#ffe5cc`, yellow `#fff4cc`, green `#dbffcc`, blue `#cdf3ff`, purple `#f9ccff`

Prefer square or 8px-radius panels, clear grids, and compact headings. Do not let a Mermaid diagram, code block, or video overlap adjacent content at 1280x720.

# Slidev Transition Set

Use these built-in transitions when asked to cover the full current Slidev transition surface:

- `fade`
- `fade-out`
- `slide-left`
- `slide-right`
- `slide-up`
- `slide-down`
- `view-transition`

Also include a custom transition when the task asks for broad Slidev capability coverage. Custom transitions use Vue Transition class names in the deck stylesheet.

# Authoring Workflow

1. Create the spike folder with a self-contained `slides.md` and a neighboring `style.css` for deck-wide styles.
2. Put code and Mermaid examples on the rendered slide, not only in notes.
3. Use per-slide frontmatter for transition coverage:

```md
---
transition: slide-left
layout: two-cols
---
```

4. Keep recorded showcase decks to one keyboard advance per slide unless the recorder is configured for click steps. Avoid live `v-click` steps in transition-recording decks because one `ArrowRight` may reveal a click instead of changing slides.
5. Verify transition direction from the rendered video. In this repository's Slidev recording workflow, the visible transition to the next slide is controlled by the slide being left, so the source slide should carry the transition that should be seen during that navigation.
6. For `view-transition`, put a shared element on both neighboring slides and give it the same `view-transition-name`. Make the source and target positions far apart, give the animation at least 2 seconds, and review sampled frames around that transition; subtle same-position morphs are easy to miss in a recorded video.
7. When demonstrating in-slide animations, include explicit examples for the relevant Slidev primitives: `v-click`, `v-after`, `v-click-hide`, `<v-clicks>`, `<v-switch>`, `v-motion`, `magic-move`, and `v-mark`. Add every internal click stage to the recorder click plan.
8. Measure the real same-slide click count when a slide combines animations, code highlighting, and components. If `ArrowRight` does not leave the slide after the planned clicks, the video is incomplete; update `--click-plan` instead of falling back to direct navigation.
9. Contrast each intended click stage against the rendered frame or active-slide DOM before accepting the video. Record what should be visible, what code lines should be highlighted, and what the browser actually shows.
10. Avoid letting explanatory code highlights steal click stages from the animation they are explaining. Dynamic fenced code blocks register their own clicks; when the code is only an explanation for another animation, prefer `$clicks`-driven manual code highlights or absolute click positions so the code and action stay synchronized.
11. Do not use `<v-clicks fade>` when the intended behavior is hidden-until-click reveal. `fade` makes future list items visible at reduced opacity, which can look like the click animation is broken in recorded video.
12. Verify highlight ranges against actual rendered line numbers. Ranges that point past the end of a code block silently produce misleading empty or all-highlight stages.
13. Run a static build before recording:

```bash
npx slidev build spikes/<spike-name>/slides.md
```

14. Record the browser deck with the bundled script:

```bash
node .agents/skills/gjv1-slidev/scripts/record-slidev-video.mjs \
  --entry spikes/<spike-name>/slides.md \
  --output videos/<spike-name>/<spike-name>.webm \
  --seconds-per-slide 3 \
  --click-plan '{"2":4}' \
  --seconds-per-click 1.6 \
  --slide-count <count> \
  --screenshots-dir videos/<spike-name>/screenshots
```

15. Inspect the screenshots and sampled video frames. Patch slide spacing, code font size, Mermaid sizing, or transition timing if content is cropped or cramped. Keep global CSS in `style.css`; reserve inline `<style>` blocks for tiny slide-local experiments.
16. For polished videos, trim the initial Slidev loader from the WebM by matching the first recorded frame against `screenshots/slide-01.png`; the review start frame should show slide content, not `Loading slide...`.
17. When demonstrating dynamic code highlighting, use Slidev line highlight stages such as `{none|1-3|5|all}` and record same-slide clicks with `--click-plan`. Hold each click stage long enough to be legible and save click-stage screenshots.
18. When validating custom transitions, sample frames during the route change. A custom transition that only fades a white slide or uses a tiny transform may be technically applied but visually invisible in the final video. Use high-contrast content plus clip-path, rotation, blur, or large lateral motion when the purpose is demonstration.
19. Treat built-in `fade` and `fade-out` as easy-to-miss in recorded videos. Slidev's local default transition duration is short, and opacity-only changes between mostly white slides can look like no transition at all. For showcase decks, set an explicit `--slidev-transition-duration`, add high-contrast proof blocks on the source and target slides, and sample frames during the route change.

# Video Timing

- Default to at least 3 seconds of hold per slide for Slidev showcase videos.
- For dynamic code highlighting, hold each highlight stage for at least 1.4 seconds.
- For view transitions intended to be visibly reviewed in video, use around 2 seconds of transition duration and a matching navigation wait.
- Add 600 to 1000 ms of transition settle time between slides when recording.
- For opacity-only route transitions, use at least 1.4 to 1.6 seconds of Slidev transition duration and set `--transition-ms` long enough to include the delayed `fade-out` enter phase.
- Keep the browser recording size explicit. Use 1280x720 for fast drafts and 1920x1080 for polished review videos with code and diagrams.
- If trimming or transcoding a 1920x1080 WebM, use a high enough bitrate for legible code, typically around 12 to 16 Mbps.
- Prefer WebM as the native Playwright output. Transcode only when a downstream target strictly requires another container.

# Validation Checklist

Before finishing:

- `npx slidev build spikes/<spike-name>/slides.md` succeeds.
- `uv run --script spikes/<spike-name>/main.py` or the recorder script produces a video under `videos/<spike-name>/`.
- Every requested transition appears in a real browser navigation path.
- Each slide has readable code and Mermaid content.
- Every in-slide animation stage is represented in `--click-plan`; strict routing should fail if any slide still has unrecorded click stages.
- Screenshots show no cropped headings, clipped code, or overflowing Mermaid diagrams.
- Sampled review frames show real slide content at the start, middle, and end of the video.
- The final README documents the exact run commands and output path.

# Bundled Resources

- Use [scripts/record-slidev-video.mjs](scripts/record-slidev-video.mjs) to start a local Slidev server, navigate slides with Playwright, record WebM, and optionally save one screenshot per slide.
- Read [references/slidev-video-workflow.md](references/slidev-video-workflow.md) for transition and export notes.
- Copy or adapt [assets/canonical-slidev-theme.css](assets/canonical-slidev-theme.css) when a deck needs a quick local stylesheet that matches the repository visual system.
