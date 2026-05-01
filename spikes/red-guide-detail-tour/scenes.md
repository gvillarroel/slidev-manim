---
title: Red Guide Detail Tour Narrative
status: draft
date: 2026-05-01
---

# Red Guide Detail Tour

## Overview

- **Topic**: Camera-led visual explanation with a red guide marker.
- **Hook**: A single point can first orient the viewer, then become the pointer that opens a deeper explanation.
- **Target Audience**: Slide authors experimenting with Manim clips embedded inside Slidev.
- **Estimated Length**: 30 to 35 seconds.
- **Key Insight**: The red marker should change narrative role at the exact moment the camera performs the nested zoom.

## Narrative Arc

The viewer starts with a large map that feels intentionally navigable rather than dense. The red point tours one station, zooms back out, then enters a second station. Inside that station, the camera and marker zoom again; the marker lands at the upper-left of the new frame, and a solid detail panel opens to its right so the scene can explain the selected sector.

---

## Scene 1: Macro Map

**Duration**: ~3 seconds
**Purpose**: Establish the world and make the red marker feel like the viewer's guide.

### Visual Elements

- Wide page-background stage.
- Four quiet rectangular stations connected by gray routes.
- One primary-red dot with a faint halo.

### Content

The map is already visible at frame one. The red marker waits near the first station long enough for the viewer to understand that it is the only active accent.

### Narration Notes

Describe the marker as the thing we follow, not as a decorative highlight.

### Technical Notes

- Use `MovingCameraScene`.
- Start with a wide camera frame.
- Keep station labels sparse and subordinate.

---

## Scene 2: First Zoom Stop

**Duration**: ~7 seconds
**Purpose**: Prove the red marker can guide attention into a local mechanism.

### Visual Elements

- A local scan panel with stacked neutral blocks.
- A receiver slot.
- A short red trace showing the selected signal.

### Content

The camera zooms into the first station. The red marker activates a small slot and moves a selected signal into place. The station is simple enough to read as a mechanism, not a static diagram.

### Narration Notes

This is the orientation pass: "we can enter a region, inspect it, and leave with a selected thread."

### Technical Notes

- Hold the proof moment where the selected signal is visibly inside the receiver.
- Remove unnecessary route emphasis before moving to the next station.

---

## Scene 3: Zoom Out And Travel

**Duration**: ~5 seconds
**Purpose**: Keep spatial continuity between local explanation and the next target.

### Visual Elements

- The camera widens to show the route between stations.
- The red marker travels along a red copy of the route.

### Content

After the first inspection, the camera zooms out enough to restore context. The marker travels to the nested station rather than cutting there.

### Narration Notes

Use this beat to say that the next explanation is still part of the same map.

### Technical Notes

- The red route is temporary and should fade before the nested zoom.

---

## Scene 4: Nested Zoom

**Duration**: ~7 seconds
**Purpose**: Shift the marker from traveler to pointer.

### Visual Elements

- A grid of micro-cells inside the second station.
- A red selection frame around one micro-cell.
- A camera zoom from station scale to detail scale.

### Content

The marker selects one small cell. Then the camera performs a second zoom, and the marker moves to the upper-left of the camera frame. The selected cell remains close enough to transform into the explanatory panel.

### Narration Notes

This is the turn: "now we stop touring and explain this exact piece."

### Technical Notes

- The marker must land near the upper-left before the panel fills the available space.
- The final camera view should leave a clean rectangle of negative space to the right and below the marker.

---

## Scene 5: Solid Detail Panel

**Duration**: ~10 seconds
**Purpose**: Convert the selected sector into a readable explanation surface.

### Visual Elements

- Solid primary-blue rectangular panel.
- White input, rule, and output elements.
- A primary-red pointer line from the pinned marker.
- A small red active segment inside the mechanism.

### Content

The selected micro-cell opens into a solid background rectangle. Elements appear in a staged order: inputs, rule slot, active red segment, and output stack. The final frame is clean enough to become a slide hold.

### Narration Notes

Use the detail panel to explain the sector in a few beats. The marker no longer travels; it points.

### Technical Notes

- Use white text and white structure over the primary-blue background.
- Keep the red marker outside the body of the panel so it does not crowd the detail elements.
- End with a 6-second resolved hold.
