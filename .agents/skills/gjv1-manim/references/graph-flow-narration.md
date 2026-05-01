# Graph Flow Narration

Use this reference when a Manim scene explains a route, dependency path, graph traversal, workflow branch, or flow through a network.

## Narrative Roles

- The graph is structure, not the protagonist. Keep all non-selected edges gray, thin, and low-opacity until they are needed.
- The selected route should be the only saturated path. Default to `PRIMARY_RED` for the route, pulse, and final focus.
- Competing paths can be acknowledged with short `ShowPassingFlash` passes, but they should disappear immediately after proving that alternatives exist.
- A moving pulse should carry causality. One pulse traveling along one explicit path reads better than several simultaneous particles.
- Use `TracedPath` as temporary proof, not as permanent decoration. Give it a short `dissipating_time` or fade it during cleanup.
- The final graph should be simpler than the opening graph. Remove unused vertices, edges, rings, traces, and candidate flashes before the final hold.

## Layout Pattern

Start from a manual layout when route readability matters:

1. Put source and target on a clear left-to-right or top-to-bottom axis.
2. Place competing paths in separate lanes with enough vertical separation that flashes cannot merge into one wide band.
3. Keep the chosen route as a smooth chain with few crossings.
4. Leave room around the chosen route for a pulse halo and trace stroke.
5. After cleanup, recenter or straighten the remaining route so the final hold does not look stranded in the original network layout.

Automatic `Graph` and `DiGraph` layouts are useful for quick exploration, but narration-quality route scenes usually need a manual layout or explicit post-layout adjustments.

## Motion Pattern

Use this sequence for route-choice scenes:

1. Show the full graph in gray and hold a visible opening breath.
2. Flash one or two competing paths in gray. Do not recolor them permanently.
3. Select the intended route segment by segment with a red edge style and a brief red flash.
4. Move a single pulse along a `VMobject` path built from the selected vertex centers or route anchors.
5. Attach a halo with an updater when the pulse needs to stay readable over dense edges.
6. Add `TracedPath` behind the pulse with a short dissipating time.
7. Fade out non-selected edges, non-selected vertices, source/target rings, pulse, halo, and trace in the same cleanup beat.
8. Move or settle the selected vertices into a compact route for the final hold.

When the selected path sits in a lower or side lane during the full-network phase, do not hold that route alone for several seconds after cleanup. Replace it quickly with a newly laid out simplified route, or recenter it in the same cleanup beat. The interim selected route can pass as a graph path while alternatives are visible but become visibly off-center once the network context disappears.

## Manim API Notes

- `DiGraph` is a strong default for route narration because edge direction matters. Use `Graph` only when direction would add noise.
- Pass a manual `layout` dictionary when the story depends on spacing, crossings, or route lanes.
- Style individual `graph.edges[(u, v)]` mobjects directly after creating the graph. Keep route edges and competing edges in named lists so cleanup is explicit.
- Build pulse paths with `VMobject().set_points_as_corners([...])` when the pulse must follow graph legs rather than a smooth curve.
- Use `MoveAlongPath(pulse, route_path)` for one authored traversal.
- Use `ShowPassingFlash(route_path.copy(), time_width=...)` as an ephemeral emphasis layer. Do not leave the flash mobject in the final composition.
- Use an updater for follower geometry such as a halo: the halo should follow the pulse, then clear the updater before fading out.
- For the final hold, creating a fresh `Graph` or `DiGraph` with only the selected vertices is often cleaner than trying to animate the original graph into place. It avoids stale edge geometry, lingering hidden vertices, and off-center path holds.

## Proof Frames

Sample these frames before accepting the render:

- opening breath with all paths quiet and readable,
- gray competing-path flash while alternatives remain subordinate,
- segment-selection proof where the red route is becoming dominant,
- mid-route pulse with halo and trace visible,
- cleanup moment where non-selected structure is disappearing,
- final hold with only the simplified chosen route.

If any sampled frame reads as an undifferentiated network, patch in this order: spacing, edge opacity, pulse size, trace lifetime, cleanup timing.

## Common Failures

- Leaving all graph edges at equal opacity makes the selected route feel arbitrary.
- Letting candidate flashes use the same color or width as the chosen route makes alternatives compete with the story.
- A long-lived trace becomes residue after the pulse has already explained the route.
- Moving several particles through the graph creates ambient flow, not a chosen path.
- A vector field or `StreamLines` layer can be useful for environmental context, but it usually weakens route-choice narration unless it fades before the route is selected.
- Final holds often stay off-center after non-selected vertices disappear; recenter the surviving route during cleanup.
- Text headers can create edge-clearance and rest-centering audit failures without improving the route mechanism. Remove them unless the title carries information the graph cannot express.

## Validation

- Extract proof frames on a white review background and inspect the pulse/trace frame and final hold at full size.
- Run the frame composition audit after the cleanup timing is final. Treat `off_center_content` during cleanup as a patch prompt, not as harmless transition noise.
- Run the resting mobject audit for graph-flow scenes with waits. Titles, route labels, and final simplified graphs can all create rest-state issues that the contact sheet may hide.
