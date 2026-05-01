# Red Guide Detail Tour

Use this reference when a `red guide tour` needs to become a more detailed explanation without cutting away from the camera-led narrative.

## Core Pattern

The red guide marker has two roles:

- **Traveler**: it moves through a large diagram, giving the viewer a stable object to follow during camera pans and zooms.
- **Pinned pointer**: during a nested zoom, it moves near the upper-left of the camera frame and stops traveling. From there it points into a solid detail panel that opens in the remaining space.

The role change is the narrative turn. The viewer should feel that the tour has stopped on one precise sector and that the explanation now belongs to that sector.

## Composition Rules

- Keep one primary-red marker throughout the scene. Do not introduce a second competing guide unless the spike is explicitly comparing guides.
- During the nested zoom, reserve the upper-left area for the marker plus halo. Account for the halo radius and stroke when placing the marker; a dot that is technically inside the frame can still look clipped.
- Put the detail panel to the right and below the pinned marker. The marker should sit outside the panel body, with a short red pointer line into the panel.
- Use a solid primary background for the detail panel only when the panel is the explanatory surface. On a primary-blue or other primary-color panel, use white structure and text by default.
- Keep old station labels, headers, and panel borders from sitting behind the pinned marker. Fade or suppress the station shell during the nested zoom before it reaches the frame edge.
- Let faint source cells or scaffolds remain only if they explain where the detail came from. They should be weaker than the solid detail panel.

## Motion Rules

- Give the macro map a visible opening breath before the first zoom.
- At each local stop, let the marker activate or participate in a mechanism before it moves on.
- When traveling between distant zones, show a temporary red route copy, but remove that route before the camera zooms into the next station. A route that remains visible during the zoom can create cropped diagonal fragments at the frame edge.
- For the nested zoom, move the marker and camera together, then open the panel. The viewer should see the marker become a pinned pointer before the panel fills the explanation space.
- Transform a small selected cell or seed rectangle into the solid detail panel. This makes the panel feel like it opens from the selected sector instead of appearing as a separate slide overlay.
- Reveal detail-panel elements in functional order: input structure, rule or gate, active red segment, output structure, then final labels if needed.

## Validation

Sample these proof moments:

- macro opening with all distant zones visible,
- first local mechanism proof,
- route travel after the camera zooms back out,
- selected micro-cell before the nested zoom,
- marker pinned in the upper-left before the panel is populated,
- final panel hold.

Run the composition audit on camera-led versions:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<spike-name>.webm --cadence 1 --write-overlays
```

Treat `low_visual_margin` as blocking for camera-led scenes. Common fixes are:

- move the pinned marker slightly down and right to clear its halo,
- widen or recenter a travel camera frame,
- move the guide onto the visible route before zooming out,
- fade route guides before the next zoom-in,
- fade old station shells before they crop under the detail view.
