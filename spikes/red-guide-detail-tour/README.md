---
title: Red Guide Detail Tour
status: draft
date: 2026-05-01
---

# Purpose

This spike tests a red guide narrative where one primary-red marker leads a camera tour across a large diagram, zooms into one region, then performs a second zoom inside that region.

# Narrative Pattern

The red guide starts as a travel companion on the macro map. It moves with the camera through distant elements, then pins itself near the upper-left corner during the nested zoom. That pinned position turns the marker into a pointer, leaving open space for a solid detail panel that explains the selected sector.

# Hypothesis

If the red marker changes role from traveler to pinned pointer during the nested zoom, the scene can shift from orientation to explanation without adding heavy text.

# Run

```bash
uv run --script spikes/red-guide-detail-tour/main.py
```

# Output

The render writes:

- `videos/red-guide-detail-tour/red-guide-detail-tour.webm`
- `videos/red-guide-detail-tour/red-guide-detail-tour.png`

# Timing

The scene is designed for Slidev integration. It opens on a meaningful full-map composition, gives the first zoom room to breathe, and holds the final detailed explanation panel long enough for narration.
