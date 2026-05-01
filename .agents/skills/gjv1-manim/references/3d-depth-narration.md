# 3D Depth Narration

Use this reference when a Manim scene needs `ThreeDScene`, 3D axes, surfaces, solids, or camera movement to reveal a hidden relationship. The default test is simple: if the same idea is clear from a 2D diagram, keep it 2D. Use 3D only when depth, occlusion, height, or camera position exposes information that would otherwise be invisible.

## Narrative Pattern

Start from a readable flat projection, then move the camera to reveal the missing dimension. The first view should be a meaningful composition, not a blank or a decorative orbit. Keep a fixed-in-frame 2D reference when the audience must compare "what the screen showed" against "what depth explains."

Good 3D narration usually follows this order:

1. Show the flat projection or front view for 2 to 3 seconds.
2. Tilt or move the camera once to expose the hidden z-depth.
3. Reveal physical depth evidence during the camera move, such as columns, shadows, occlusion gaps, or a surface ridge.
4. Use a very short ambient rotation only if it helps inspect the revealed structure.
5. Stop the camera and hold a clean final 3D view for 5 to 7 seconds.

## Composition Rules

- Treat `move_camera` as the causal reveal, not as a flourish. The proof frame should show what became visible because the camera moved.
- Keep one stable reference: a fixed overlay, a ground-plane shadow, or a front-view outline. Do not use all three unless the relation is otherwise ambiguous.
- Pair elevated objects with their projection on the floor or source plane. A sphere floating over a surface is weaker than a sphere plus a visible vertical column or shadow.
- Use `Surface` for the hidden relationship and keep its color neutral. Reserve the primary red accent for the probe, path, selected point, or current slice.
- Use 3D solids semantically: `Sphere` for sampled positions, `Prism` for measured depth or volume, `Cube` only when a block-like quantity matters. Do not add solids as generic decoration.
- Keep axis ticks, labels, and checkerboards subordinate. In narration scenes the camera and the active accent should do the explaining.

## Camera Discipline

- Start with `set_camera_orientation` at the view that hides the intended dimension, commonly top-down or front-on.
- Use one staged `move_camera` to reveal depth. Avoid multiple exploratory moves before the audience has a stable model.
- If using `begin_ambient_camera_rotation`, keep the rate low and the duration short. Stop it before the final hold.
- Return to a readable final orientation after any ambient rotation. A final spinning scene is not a resolved slide-integration hold.
- For fixed overlays, use `add_fixed_in_frame_mobjects` so the reference does not drift during camera motion.

## Proof Frames

Sample these moments before accepting the scene:

- opening flat view with the fixed or floor projection visible,
- camera-tilt mid-state where the hidden depth first becomes legible,
- inspection frame where the active accent sits on the revealed 3D relation,
- final stopped hold after transient camera motion is over.

Patch in this order when proof frames fail:

1. Increase separation between elevated object and projection.
2. Strengthen the column, shadow, or occlusion evidence.
3. Reduce surface opacity or checkerboard contrast if it competes with the accent.
4. Slow or shorten ambient rotation.
5. Recenter the final camera and remove any guide that no longer explains depth.

## Failure Patterns

- Rotation for rotation's sake: the camera moves but no new relationship appears.
- Floating actors: objects sit in 3D space without projection, shadow, support, or axes.
- Unreadable final hold: the camera is still rotating or the final angle hides the relationship again.
- Over-modeled surface: the checkerboard or mesh becomes the subject instead of the hidden relationship.
- Text compensation: labels explain the z-depth because the geometry did not.
