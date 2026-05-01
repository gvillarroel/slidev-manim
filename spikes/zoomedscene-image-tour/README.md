---
title: ZoomedScene Image Tour
status: draft
date: 2026-04-30
---

# Purpose

Test ManimCE `ZoomedScene` as an inset magnifier over a real Artemis photo from NASA.

# Hypothesis

If a real mission photo has enough native detail and the zoom frame moves through a few distinct regions, the inset should read as a deliberate guided inspection rather than a generic camera pan.

# Run

```bash
uv run --script spikes/zoomedscene-image-tour/main.py
```

To force a fresh download of the NASA source image:

```bash
uv run --script spikes/zoomedscene-image-tour/main.py --refresh-source
```

# Source Photo

The background is a real NASA Artemis I image from [View the Best Images from NASA's Artemis I Mission](https://www.nasa.gov/humans-in-space/view-the-best-images-from-nasas-artemis-i-mission/).

The local source asset is:

- `spikes/zoomedscene-image-tour/assets/artemis-i-earth-after-opf.jpg`

# Output

The render writes:

- `videos/zoomedscene-image-tour/zoomedscene-image-tour.webm`
- `videos/zoomedscene-image-tour/zoomedscene-image-tour.png`
- `videos/zoomedscene-image-tour/artemis-i-earth-after-opf-16x9.jpg`

# Timing

The scene is designed as a Slidev integration video: it opens on the full image, activates the `ZoomedScene` display, visits several detail regions, and leaves a resolved overview long enough to read.
