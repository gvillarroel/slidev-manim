---
title: Manim Narration Timing Lab
status: active
date: 2026-04-30
---

# Manim Narration Timing Lab

## Hypothesis

If Manim timing primitives are treated as narration cues instead of decorative motion controls, a slide-integrated video can feel paced for a speaker without requiring recorded audio during the spike.

## Purpose

This spike tests the narrative use of:

- a visible opening breath before any major motion,
- `Succession` for ordered sentence beats,
- `LaggedStart` and `AnimationGroup` for progressive grouped reveals,
- `ChangeSpeed` for a deliberate slow-down and hold around the critical point,
- `Scene.next_section()` plus `--save_sections` for cue metadata,
- scripted voiceover-style durations through a local tracker object without microphone input or a TTS service.

The visual design is intentionally sparse: a single primary-red timing marker moves across a grayscale section rail on an opaque page-background stage.

## Run the render

From the repository root:

```bash
uv run --script spikes/manim-narration-timing-lab/main.py
```

For a slower but smoother proof render:

```bash
uv run --script spikes/manim-narration-timing-lab/main.py --quality medium
```

The script renders the video, promotes section metadata, extracts proof frames, and writes validation artifacts to:

```text
videos/manim-narration-timing-lab/
```

Primary output:

```text
videos/manim-narration-timing-lab/manim-narration-timing-lab.webm
```

Review outputs:

```text
videos/manim-narration-timing-lab/proof-contact-sheet.png
videos/manim-narration-timing-lab/proof-frames/
videos/manim-narration-timing-lab/sections/
videos/manim-narration-timing-lab/scripted-cues.json
videos/manim-narration-timing-lab/validation.json
```

## Narrative Timing Budget

The scene is intended for slide integration and therefore follows the repository pacing floor:

- opening breath: 2.5 seconds after the first meaningful composition is visible,
- progressive beat groups: 6.5 seconds,
- deliberate slow-down and hold: 7.5 seconds,
- section cue metadata reveal: 5.0 seconds,
- resolved final hold: 1.0 second cleanup plus a 6.0 second stable hold.

The scripted cue helper mirrors the useful part of a voiceover tracker: every beat has a planned duration and caption, but the render does not require audio recording or external TTS.
