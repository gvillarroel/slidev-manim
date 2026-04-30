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

## Latest Validation

Rendered with:

```bash
uv run --script spikes/svg-repo-video-lab/main.py --quality medium
```

Observed output:

- Duration: 44.151 seconds.
- Frames: 1325 decoded frames at 30 fps.
- Resolution: 1600x900.
- Transparency: WebM VP9 stream reports `alpha_mode=1`; `ffmpeg -c:v libvpx-vp9 -vf alphaextract` confirmed alpha extrema `(0, 255)`.
- Half-second review: regenerated `videos/svg-repo-video-lab/review-half-second/contact-sheet-*.png` for the full medium render; inspected the scan pass, the exact 14-second clamp beat, and the 29.5-30.5 second continuation transition.
- Composition audit: `frame-composition-audit.py --cadence 0.5 --write-overlays` reported `sampled_frames=89` and `blocking_frames=0` on the promoted medium WebM.
- Exact callout audit: `frame-composition-audit.py --times 14 --out-dir videos/svg-repo-video-lab/composition-audit-14s --write-overlays` reported `blocking_frames=0`.
