# Camera Focus Narration

Use this reference for Manim scenes where camera movement is the narration device, especially large diagrams that would be unreadable if shown all at once.

## Narrative Rule

Move the camera only after the viewer can see where it is going. A destination scaffold, slot, panel, target pocket, or route continuation should be visible before the frame starts traveling.

## Recommended Pattern

1. Open on the largest meaningful map, not a blank frame.
2. Use one primary-red guide marker as the companion focus point.
3. Show subdued route scaffolds and prepared destination panels before the guide moves.
4. Zoom into one local mechanism at a time with `MovingCameraScene`.
5. Keep the red guide involved in the local mechanism so the camera stop has a reason.
6. Widen the frame before long travel moves so the next destination scaffold is visible.
7. Retire or soften transient guide scaffolds before the resolved hold.
8. Recenter cleanly for the final hold so the last frame is a complete composition, not a cropped travel view.
9. For transparent slide assets, let panels, routes, and grid structure carry the scene; avoid a full-frame opaque stage plate unless the slide needs that local surface.

## Moving Camera Choices

Use `self.camera.frame.animate.move_to(...).set(width=...)` when the story needs deliberate framing. Save the opening map frame after sizing it, then restore or manually return to that centered frame for the final hold.

Use `self.camera.auto_zoom(...)` when fitting a group is more important than authored composition, but audit the resulting margins. Automatic fitting can put important route context too close to the edge.

Use `ZoomedScene` only when an inset view adds information that the main camera cannot show without losing the global context. Do not add a zoomed display just to prove the API is available; an inset competes with narration unless it solves a real simultaneous-context problem.

Use fixed-in-frame labels or HUD elements sparingly. For slide narration, a route marker plus visible destination scaffolds usually reads cleaner than a persistent overlay. If a fixed element is needed, keep it small, neutral, and outside the mechanism path.

## Receiver and Guide Detail

Use open receiver brackets for local focus slots when a red guide dot enters the target. Closed boxes can enclose the guide and create zero-clearance proof frames even when the motion reads in playback.

Keep the guide marker as one primary-red dot unless the halo carries a specific meaning. A decorative halo can collide with focus dots, receiver brackets, or transformed stack bars in sampled still frames and make the camera stop read crowded.

When a local mechanism transforms bars, tokens, or dots into a prepared slot, leave visible vertical or horizontal gutters between the transformed pieces. A stack that looks acceptable while moving can collapse into true overlap in a 0.3-second proof frame.

## Proof Frames

Sample these moments before accepting a camera-led scene:

- the opening map with all destination scaffolds visible,
- the first focused local mechanism,
- the wide frame just before each long camera travel move,
- the mid-travel frame where the red guide and destination are both readable,
- the final full-map hold after recentering.

Run the frame composition audit for camera-led scenes. Treat low visual margin and off-center content as blocking, because camera crops are often invisible in code review but obvious in rendered frames. Open any reported side fragment at full size before deciding whether it is intentional context or accidental crop residue.

Run the resting-mobject audit after camera widths are tuned. It catches held travel frames where origin and destination panels are technically visible but too close to the active camera edge.

## Common Fixes

- If the pan feels arbitrary, make the destination scaffold visible earlier or widen the pre-travel frame.
- If the camera stop feels like a static zoom, make the red guide trigger or participate in a local mechanism.
- If a neighboring panel is cropped at the edge, either widen enough to include it as context or tighten enough to remove it entirely.
- If the final hold feels stranded, remove transient supports and return to a centered map or centered resolved cluster.
- If labels are needed, make them local to panels. Avoid fixed labels that explain what the camera should be proving through motion.
- If strict crowding reports many guide contacts, inspect whether the guide halo or closed receiver slot is the cause before changing the whole camera path.
