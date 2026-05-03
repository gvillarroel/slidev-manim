# Motion Line Styles

Use this reference when a scene needs visible connection behavior that feels authored by Manim rather than drawn like a static diagram.

## `cellular sprout line`

Use a `cellular sprout line` when a concept should feel generated, grown, or emitted from a source. This style replaces a literal stroke with a staggered chain of small cells along an implicit curved route.

### Visual Grammar

- The route is implied by many dots or cells, not by `Line`, `ArcBetweenPoints`, `Arrow`, or a stroked path.
- Active growth uses the scene accent color, usually `PRIMARY_RED`.
- Settled route residue fades into gray and becomes subordinate to the nodes.
- A terminal bud appears at the destination before the destination body appears.
- The bud fades out while the box body fades in; do not morph a circle directly into a rectangle.
- Labels fade in after the body is stable, so proof frames never show warped text.
- Initial focus cues should also use cells or pulses, not rectangular outline flashes.

### Implementation Recipe

1. Define an implicit route with a quadratic Bezier point function.
2. Place cells at deterministic `t` values along the route.
3. Add a small normal-direction jitter so the route feels biological but remains readable.
4. Reveal cells with `LaggedStart(*[FadeIn(cell, scale=0.35) ...])`.
5. Show a terminal bud at the route endpoint.
6. Fade the bud out and fade the destination body in.
7. Fade in the destination label after the body.
8. Settle active cells back to gray at low opacity.

### Copyable Shape

```python
def normal_for(start, end):
    delta = np.array(end) - np.array(start)
    length = math.hypot(float(delta[0]), float(delta[1]))
    if length < 0.001:
        return UP * 0
    return np.array([-delta[1] / length, delta[0] / length, 0])


def growth_point(start, end, bend, t):
    start_point = np.array(start)
    end_point = np.array(end)
    control = (start_point + end_point) / 2 + normal_for(start_point, end_point) * bend
    return ((1 - t) ** 2) * start_point + 2 * (1 - t) * t * control + (t**2) * end_point


def cellular_sprout_line(start, end, bend, count, color, opacity, base_radius, z_index):
    cells = VGroup()
    route_normal = normal_for(start, end)
    for index in range(count):
        t = (index + 1) / (count + 1)
        radius = base_radius * (0.74 + 0.28 * math.sin((index + 1) * 1.7) ** 2)
        jitter = route_normal * (0.035 * math.sin(index * 2.23 + count))
        cell = Circle(radius=radius, stroke_width=0, fill_color=color, fill_opacity=opacity)
        cell.move_to(growth_point(start, end, bend, t) + jitter)
        cell.set_z_index(z_index)
        cells.add(cell)
    return cells
```

### Timing

- Opening breath: show source, pending destination fields, and faint pending cells for 2 to 3 seconds.
- Trunk growth: use longer cell chains and a visible terminal bud.
- Child growth: use shorter chains, faster cadence, and smaller buds.
- Final hold: keep only low-opacity gray residue, stable boxes, and the source hub.

### Review Frames

Sample at least:

- the opening breath with faint pending cells,
- the first active red trunk growth,
- the moment a destination bud becomes a box body,
- the first child growth,
- the final hold.

Run the composition audit at 0.5 second cadence when the scene has many branches.

### Failure Modes

- A rectangular outline focus flash reads like a stray connector; use a cell corona or circular pulse instead.
- Morphing a circle into a rectangle creates skewed intermediate plates; fade the bud out and the body in.
- Revealing children before all category trunks exist makes the map feel top-heavy.
- Leaving cells too red after landing makes every old route look active.
- Too much random jitter turns the route into noise; keep jitter normal to the path and deterministic.

## `organic fractal line`

Use an `organic fractal line` when a connection should read as plant-like growth rather than a diagram connector. This style uses a readable main stem plus delayed recursive side tendrils.

### Visual Grammar

- Keep the main route readable as one parent path.
- Use `Create` on native `VMobject` stems so the path visibly grows.
- Use a thicker active main stem and thinner, lower-opacity side tendrils.
- Grow side tendrils after the main route has established direction by ordering the `VGroup` main stem first.
- Use no more than two recursion levels for slide clarity.
- Fade side tendrils harder than the main route so they do not overpower labels.
- Fade settled organic routes to gray residue rather than leaving old red routes active.
- Use a terminal bud at the destination before revealing the node body.

### Implementation Recipe

1. Generate a smooth main route from an implicit Bezier curve.
2. Add low-amplitude sinusoidal wiggle in the route normal direction.
3. Sample deterministic branch points along the main route.
4. Build each side tendril from the local tangent plus the local normal.
5. Add optional second-level twigs only on long trunks.
6. Put stems in this order: main stem, first-level tendrils, second-level twigs.
7. Reveal with `LaggedStart(*[Create(stem) for stem in organic_line], lag_ratio=0.12)`.
8. Fade the destination bud out and fade the destination body in.

### Timing

- Opening breath: show faint pending organic routes and destination fields.
- Category trunks: use a thick red main stem with multiple side tendrils.
- Child branches: use shorter lines with fewer tendrils and no second recursion level unless space is generous.
- Final hold: keep the main structure visible in gray, but make twigs subtle.

### Review Frames

Sample at least:

- the opening breath with faint pending stems,
- an active red trunk where the main stem and side tendrils are both visible,
- a child branch growth frame,
- the final hold.

Run the composition audit at 0.5 second cadence because organic stems can introduce stray-looking fragments near boxes.

### Failure Modes

- If side tendrils are as strong as the trunk, the route becomes visual noise.
- If the active stem is too thin, it reads like a faint connector instead of growth.
- If every trunk has many second-level twigs, the final hold becomes scratchy and competes with labels.
- If pending routes are too dark during the opening breath, the scene looks already completed.
- If old red routes stay saturated after landing, every branch reads as still active.

## `scale spine line`

Use a `scale spine line` when the user wants a connection made from many visible elements growing like scales, thorns, or spines. This style avoids both continuous strokes and dot chains: the route is perceived from repeated directional polygon units.

### Visual Grammar

- The visible route is a sequence of small polygonal scales or spines.
- Each unit points along the tangent of an implicit curved route.
- Units alternate around the route so the chain reads as a crest rather than a dashed line.
- Active growth uses the accent color, usually `PRIMARY_RED`.
- Settled units fade to low-opacity gray.
- A terminal bud can mark the final push before the node body appears.
- Labels fade in after the destination body, not while the spine chain is still forming.

### Implementation Recipe

1. Define an implicit Bezier route for placement only.
2. For each sample position, compute the local tangent from nearby route samples.
3. Compute the route normal and offset alternating units slightly to either side.
4. Build each unit as a pointed `Polygon` with one forward tip, two shoulders, and a tail.
5. Reveal units with `LaggedStart(*[FadeIn(spine, scale=0.2) ...])`.
6. Place a terminal bud at the destination before the node body appears.
7. Fade the bud out, fade the body in, then fade the label in.
8. Settle the active spines back to gray with reduced opacity and slight scale reduction.

### Timing

- Opening breath: show faint pending scale-spine routes and target fields.
- Category trunks: use larger, more numerous spines so the texture is unmistakable.
- Child branches: use fewer, smaller spines so children remain secondary.
- Final hold: keep enough gray residue that the scale pattern remains visible, but not so much that it competes with labels.

### Density Control

- Increase unit count before increasing unit size when the user asks for denser scales.
- Slightly reduce each unit's length, width, and settled opacity as count rises.
- Keep active trunks dense enough that units overlap visually, but keep child branches lighter.
- Recheck full-size active growth frames; thumbnails can hide whether density reads as scales or as a dotted route.

### Aloe-Like Variant

- Use wide lance-shaped polygons with a sharp forward tip, broad shoulders, and a narrower tail.
- Use several side offsets, such as center, far left, far right, near left, and near right, instead of simple left/right alternation.
- Let active trunk units overlap heavily so the route reads like layered succulent leaves.
- Add a darker, narrow stroke to each active leaf when dense overlap starts reading as one irregular ribbon.
- Fade the stroke down with the fill after landing so the final hold keeps leaf separation without becoming a hard connector.
- Reduce settled opacity after the node appears; aloe-like density becomes a soft structural residue quickly if it stays too strong.
- Keep the project accent color unless the spike explicitly tests botanical color. The aloe reference is about growth density and leaf shape, not necessarily green.

### Non-Diamond Token Comparison Variant

- Compare alternate token shapes on the same implicit route before choosing a new connector grammar.
- Include at least one directional token, such as rectangles or triangles, and at least one non-directional token, such as squares or circles.
- Keep all variants on screen in the final hold with low but visible gray opacity so the comparison does not depend on memory.
- Rectangles and triangles tend to preserve path direction; squares and circles read more like generic beads or pixels; stars are distinctive but can become decorative noise.
- Use the same active color, settle color, count range, and target-card structure for every candidate so shape is the tested variable.
- Do not show every full candidate route in the opening breath. Use short starter chains near the source plus small receiver hints near the target cards; otherwise the growth test reads as a completed diagram that is merely recolored.
- Give the source node and target cards enough clearance from the local stage border and route endpoints. Pull terminal buds back from card outlines so strict crowding review does not confuse a prepared receiver cue with an actor-to-outline collision.
- Fan route starts slightly away from a single source point when several pending token families overlap. A small vertical offset keeps the opening proof from becoming one pale knot while preserving the shared source.

### Review Frames

Sample at least:

- the opening breath with faint pending spines,
- one active trunk where the scale shape is visible at full size,
- one active child branch,
- the final hold.

Open the active trunk frame full size. In thumbnails, spines can collapse into dots or dashes even when the full-size frame reads correctly.

### Failure Modes

- If units are too small, the style collapses into a dotted line.
- If units are too large or too opaque after landing, the residue competes with labels.
- If every unit is centered, the route reads like a dashed stroke; alternate side offsets for a crest.
- If the polygon has a blunt front edge, it reads as a tile rather than a spine.
- If pending routes are too visible, the generated structure looks prebuilt.
- If a terminal bud touches the target card, the receiver reads like a collision rather than a prepared landing.
