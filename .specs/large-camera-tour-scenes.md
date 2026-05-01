---
id: SPEC-0010
title: Large camera tour diagram scene
status: draft
date: 2026-04-30
---

# Overview

- **Topic**: A large diagram explored through staged Manim camera zooms.
- **Hook**: The viewer starts with the whole map, then discovers that each distant segment has its own motion logic.
- **Target Audience**: Slide authoring and animation workflow viewers.
- **Estimated Length**: 35 to 40 seconds.
- **Narrative Pattern**: `red guide tour`.
- **Key Insight**: A wide static diagram can feel authored if the camera treats each region as a local mechanism instead of a passive detail.

# Narrative Arc

The scene begins with the complete map visible. The camera then follows one primary-red companion marker through four distant segments: compression, orbit, fork, and merge. Each local beat changes only a few actors, then hands the eye to the next remote region through the guide's travel path.

# Scene

## Scene 1: Camera Tour Map

**Duration**: ~37 seconds

**Purpose**: Validate a large Manim diagram that remains coherent during repeated zoom and pan moves.

## Visual Elements

- A large page-background stage with a faint grid.
- Four remote square-corner diagram panels.
- Quiet gray route lines connecting the panels through the map.
- One primary-red active pulse that travels between focused segments.
- Local grayscale actors in each panel.

## Camera Movements

- Start wide enough to reveal the whole map.
- Zoom into the top-left segment for a compression beat.
- Pan and zoom to a far top-right segment for an orbit beat.
- Pan to a bottom-left segment for a fork beat.
- Pan to a bottom-right segment for a merge beat.
- Zoom back out to the whole map for a resolved hold.

## Technical Notes

- Use `MovingCameraScene`.
- Keep the scene at least 25 seconds long.
- Render the delivery video as transparent WebM and a non-transparent poster PNG.
- Validate camera framing with sampled frames and the composition audit.
