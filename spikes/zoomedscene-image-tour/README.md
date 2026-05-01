---
title: ZoomedScene Image Tour
status: draft
date: 2026-04-30
---

# Purpose

Test ManimCE `ZoomedScene` as an inset magnifier over a single large high-detail raster background.

# Hypothesis

If the background image has enough native detail and the zoom frame moves through a few distinct regions, the inset should read as a deliberate guided inspection rather than a generic camera pan.

# Run

```bash
uv run --script spikes/zoomedscene-image-tour/main.py
```

To force regeneration of the deterministic 5K source image:

```bash
uv run --script spikes/zoomedscene-image-tour/main.py --regenerate-image
```

# Output

The render writes:

- `videos/zoomedscene-image-tour/zoomedscene-image-tour.webm`
- `videos/zoomedscene-image-tour/zoomedscene-image-tour.png`
- `videos/zoomedscene-image-tour/generated-5k-detail-map.png`

# Timing

The scene is designed as a Slidev integration video: it opens on the full image, activates the `ZoomedScene` display, visits several detail regions, and leaves a resolved overview long enough to read.
