---
title: SVG Repo Video Lab
status: draft
date: 2026-04-30
---

# SVG Repo Video Lab

## Purpose

Download several SVG Repo assets and test a practical SVG-to-video workflow:

- cache external SVGs under `assets/raw/`,
- generate edited SVG variants under `videos/svg-repo-video-lab/.generated/svg/`,
- recolor SVG fills into the project palette,
- deform imported SVGs as Manim vector mobjects,
- attach animated text to a downloaded text-document SVG,
- transform the edited SVGs into a final slide-ready composition.
- continue from the resolved SVG composition into two generated subproject blocks with progressive keypoint lists.

## Source SVGs

The spike uses SVG Repo `show` URLs because the direct `download` URLs can be blocked by a browser-security challenge from command-line requests.

- Robot: <https://www.svgrepo.com/svg/35383/robot>
- Chart: <https://www.svgrepo.com/svg/528126/chart>
- Light bulb: <https://www.svgrepo.com/svg/27795/light-bulb>
- Text document: <https://www.svgrepo.com/svg/17578/text>
- Code window: <https://www.svgrepo.com/svg/245847/code>

## Hypothesis

If SVG Repo icons are normalized into local palette variants before animation, they can behave like video-native components instead of static imported clip art.

## Run

From the repository root:

```bash
uv run --script spikes/svg-repo-video-lab/main.py
```

Refresh the cached source SVGs:

```bash
uv run --script spikes/svg-repo-video-lab/main.py --refresh-assets
```

## Output

The render writes:

- `videos/svg-repo-video-lab/svg-repo-video-lab.webm`
- `videos/svg-repo-video-lab/svg-repo-video-lab.png`

Generated SVG edit variants are written under:

- `videos/svg-repo-video-lab/.generated/svg/`

Validation review frames are written under:

- `videos/svg-repo-video-lab/review-frames/`
- `videos/svg-repo-video-lab/review-half-second/`
- `videos/svg-repo-video-lab/review-frames-0.3s/`

## Latest Validation

Rendered with:

```bash
uv run --script spikes/svg-repo-video-lab/main.py
```

Observed output:

- Duration: 42.967 seconds from 1289 decoded frames at 30 fps.
- Frames: 1289 decoded frames at 30 fps.
- Resolution: 1600x900.
- Transparency: `imageio-ffmpeg` with `-c:v libvpx-vp9 -vf format=yuva420p,alphaextract` confirmed sampled alpha extrema including `(0, 255)`; PyAV RGB/RGBA reads can report opaque samples for this VP9 alpha stream and should not be the only alpha check.
- 0.3-second review: regenerated 144 individual frames under `videos/svg-repo-video-lab/review-frames-0.3s/frames/` plus 8 `contact-sheet-*.png` files; inspected the opening, RAW/VIDEO label, clamp proof frames, fan-out proof frames, core pulse frames, and the 27-43 second project-block continuation. The terminal `SVG` core now uses a stroke-only halo pulse so the accent does not cover the glyph during the fan-out proof frames.
- Composition audit: `frame-composition-audit.py --cadence 0.3 --write-overlays` reported `sampled_frames=144` and `blocking_frames=0` on the promoted medium WebM.
- Resting mobject audit: `resting-mobject-audit.py --scene-file spikes/svg-repo-video-lab/main.py --scene-class SvgRepoVideoLabScene` reported `rest_snapshots=14` and `blocking_snapshots=0`.
- Core pulse crowding audit: `frame-crowding-audit.py --start 23 --end 25 --cadence 0.3 --write-overlays` still reports low component clearance from expected imported SVG internals and label-in-card geometry; full-size overlay review found the halo no longer obscures the `SVG` glyph.
- Continuation crowding audit: `frame-crowding-audit.py --start 27 --end 36 --cadence 0.3 --write-overlays` reports low component clearance in all sampled frames from expected imported SVG internals, labels inside the compact source panel, and text/header elements inside project cards; full-size overlay review found no visible actor-to-guide or actor-to-actor collision that weakens the mechanism.
- Final hold crowding audit: `frame-crowding-audit.py --start 36 --end 43 --cadence 0.3 --write-overlays` reports low component clearance from expected compact source SVG internals and project-card text/header internals; full-size overlay review accepted the softened fork guides as non-blocking support context.
- Exact callout audit: `frame-composition-audit.py --times 14 --out-dir videos/svg-repo-video-lab/composition-audit-14s --write-overlays` reported `blocking_frames=0`.
- Clamp crowding audit: `frame-crowding-audit.py --times 14 --write-overlays` reported `blocking_frames=0`; `frame-crowding-audit.py --start 12 --end 16 --cadence 0.5 --write-overlays` reports one low-clearance compression frame at 15.5s where the bulb intentionally crosses the chart bars inside the clamp. Full-size review accepted it as the visible squeeze rather than an accidental actor-to-guide collision.
- Fan crowding audit: `frame-crowding-audit.py --start 18 --end 24 --cadence 0.3 --write-overlays` still reports low component clearance from expected imported SVG internals, the document label inside its card, and the `SVG` glyph inside the core ring; full-size overlay review found no visible actor-to-guide collision after the clamp clears.
- Block activation crowding audit: `frame-crowding-audit.py --start 33 --end 36 --cadence 0.3 --write-overlays` still reports low component clearance from expected header-inside-card, source-icon, label, and list-row internals; full-size overlay review found no visible actor-to-guide or actor-to-actor collision that weakens the mechanism.
