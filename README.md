# Slidev Manim Lab

This repository is a lab for combining [Slidev](https://sli.dev/) decks with
[Manim](https://www.manim.community/) animations. The main goal is to build
presentations where slides can include Manim-rendered transparent videos that
support the slide narrative progressively instead of behaving like separate
standalone videos.

The repo is intentionally organized around small spikes. Each spike owns its
source files, documents what it is testing, and renders into a matching ignored
output folder under `videos/`.

## What This Project Tests

- Transparent Manim WebM assets embedded inside Slidev slides.
- Slide layouts that coordinate text, diagrams, and video motion.
- Mermaid-to-SVG-to-Manim pipelines for diagram animation.
- Manim composition patterns for slide-paced narration.
- Validation workflows for rendered videos, review frames, and Slidev decks.
- Reusable authoring skills for higher-quality Slidev plus Manim experiments.

## Requirements

Install the project-level Node dependencies:

```bash
npm install
```

Install these system tools for the full workflow:

- `uv` for running spike-local Python scripts with inline dependencies.
- Node.js and npm for Slidev, Playwright, and Mermaid CLI execution.
- A working Manim environment, including the platform dependencies Manim needs
  for video rendering.
- `ffmpeg`, which is required by many render and review workflows.

Each spike `main.py` should be runnable with `uv` from the repository root and
should declare its Python dependencies inline in script metadata.

## Repository Layout

```text
.
|-- .agents/                 # Local agent skills and validation helpers
|-- .specs/                  # Project specs, ADRs, issues, and knowledge notes
|-- evaluations/             # Skill and workflow evaluation configs
|-- results/                 # Evaluation outputs and comparison workspaces
|-- skills/                  # Reusable skill assets
|-- spikes/                  # Source code for experiments
`-- videos/                  # Rendered outputs; ignored by git
```

Every spike should follow this shape:

```text
spikes/<spike-name>/
|-- README.md                # Purpose, render command, and notes
|-- main.py                  # Primary executable entrypoint
|-- slides.md                # Optional Slidev deck
`-- ...                      # Optional assets, Mermaid sources, helpers
```

Rendered outputs belong in:

```text
videos/<spike-name>/
```

The folder name under `videos/` must match the folder name under `spikes/`.

## Quick Start

Render a Manim spike:

```bash
uv run --script spikes/overlay-corner-callout/main.py
```

Run a Slidev spike deck:

```bash
npx @slidev/cli spikes/overlay-corner-callout/slides.md
```

Build a Slidev spike deck:

```bash
npx @slidev/cli build spikes/overlay-corner-callout/slides.md
```

Run one of the scripted deck workflows:

```bash
npm run dev:overlay-corner-callout
npm run build:overlay-corner-callout
```

## Common Workflows

### Create a New Spike

1. Create a folder under `spikes/<spike-name>/`.
2. Add a `README.md` that explains the experiment and exact render command.
3. Add a primary `main.py` entrypoint runnable with `uv run --script`.
4. Render assets into `videos/<spike-name>/`.
5. Keep any Slidev deck for the spike inside the same spike folder.

### Render for Slidev

For Manim clips intended to sit on a slide, prefer this asset set:

- transparent `.webm` for the real Slidev asset,
- white-background `.png` poster or review frame for fast inspection,
- alternate aspect-ratio variants when the slide composition needs different
  framing.

Normal slide-integration videos should be at least 25 seconds long, with an
initial visible breathing hold and a 5 to 7 second final hold. Shorter micro
loops or bumpers are fine when the spike documents that intent.

### Validate a Deck

For Slidev deck checks, verify three layers separately:

- the standalone rendered media file,
- the asset resolution inside Slidev,
- the visible slide composition in a browser screenshot.

Playwright screenshots can confirm layout, palette, and asset resolution, but
transparent WebM decoding can still appear blank in headless screenshots even
when the browser successfully loads the file. Keep poster images or review
frames for visual inspection.

## Visual System

Use the canonical palette and typography from
`.specs/adr/0002-slide-and-video-color-system.md` unless a spike explicitly
tests another direction.

The default primary colors are:

- `primary-red` `#9e1b32`
- `primary-orange` `#e77204`
- `primary-yellow` `#f1c319`
- `primary-green` `#45842a`
- `primary-blue` `#007298`
- `primary-purple` `#652f6c`

When one of those primary colors is used as a background, use white text by
default. For review screenshots, use a white background unless the spike is
testing a specific non-white surface.

## Important Project Docs

- `.specs/adr/0001-spikes-and-rendered-video-layout.md` defines the spike and
  render-output structure.
- `.specs/adr/0002-slide-and-video-color-system.md` defines the visual system.
- `.specs/adr/0003-scene-duration-and-pacing.md` defines pacing expectations for
  slide-oriented Manim videos.
- `.specs/knowledge/slidev-manim-spike-learnings.md` captures integration
  patterns and validation lessons.
- `.specs/knowledge/playwright-slidev-validation.md` captures the browser
  validation workflow.
- `.specs/knowledge/gjv1-manim-video-quality.md` captures reusable Manim quality
  lessons from previous iterations.

## Useful Spike Families

- `overlay-corner-callout`, `inset-annotation-panel`, `multi-video-grid`, and
  `hero-plus-supporting-loop` test transparent video placement patterns.
- `mermaid-*-svg-unfold` spikes test Mermaid diagram types converted into
  animated Manim scenes.
- `quality-*` spikes test focused motion-language ideas such as aperture,
  compression, handoff, masking, orbit, and pacing.
- `slidev-transition-showcase` records a Slidev deck as a timed WebM video.
- `zoomedscene-image-tour` and `large-camera-tour` test camera movement,
  framing, and visual review constraints.

## Git Hygiene

Generated render outputs should stay out of version control. `videos/`, `media/`,
`node_modules/`, `dist/`, logs, Playwright screenshots, and Python caches are
ignored by default.

Project-management artifacts belong in `.specs/` and should include Markdown
frontmatter. Reusable implementation and validation learnings should be recorded
under `.specs/knowledge/`.
