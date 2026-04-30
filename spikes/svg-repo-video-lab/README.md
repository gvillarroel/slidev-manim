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

- Duration: 43.251 seconds.
- Frames: 1298 decoded frames at 30 fps.
- Resolution: 1600x900.
- Transparency: WebM VP9 stream reports `alpha_mode=1`; `imageio-ffmpeg` with `-c:v libvpx-vp9 -vf alphaextract` confirmed alpha extrema `(0, 255)`.
- 0.3-second review: regenerated 145 individual frames under `videos/svg-repo-video-lab/review-frames-0.3s/frames/` plus 6 `contact-sheet-*.png` files; inspected the opening, fan-out proof frames, and the 33-36 second project-block activation.
- Composition audit: `frame-composition-audit.py --cadence 0.3 --write-overlays` reported `sampled_frames=145` and `blocking_frames=0` on the promoted medium WebM.
- Resting mobject audit: `resting-mobject-audit.py --scene-file spikes/svg-repo-video-lab/main.py --scene-class SvgRepoVideoLabScene` reported `rest_snapshots=14` and `blocking_snapshots=0`.
- Exact callout audit: `frame-composition-audit.py --times 14 --out-dir videos/svg-repo-video-lab/composition-audit-14s --write-overlays` reported `blocking_frames=0`.
- Crowding audit: `frame-crowding-audit.py --times 14 --write-overlays` and `frame-crowding-audit.py --start 12 --end 16 --cadence 0.5 --write-overlays` both reported `blocking_frames=0` after widening the clamp and separating the intermediate SVG roles.
- Block activation crowding audit: `frame-crowding-audit.py --start 33 --end 36 --cadence 0.3 --write-overlays` still reports low component clearance from normal text glyphs, list rows, and panel internals; full-size review found no actor-to-guide, actor-to-outline, or actor-to-actor collision.
