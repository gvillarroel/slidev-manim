# Arrow Growth And Connectors

Use this reference when a Manim scene depends on arrows, connector direction, arrowhead timing, route labels, or `GrowArrow` behavior.

## Core Lessons

- Treat `GrowArrow` as an introduction for `Arrow` and compatible `DoubleArrow` objects. It grows from the declared start point toward the end/tip direction.
- Use `point_color` when the collapsed start point needs to visibly identify the origin before the full arrow style appears.
- For `DoubleArrow`, the object has tips at both ends, but `GrowArrow` still uses the declared start point as the growth anchor. Mark the start point if the lesson depends on that detail.
- Prefer `Create(CurvedArrow(...))` for curved-route teaching scenes. `CurvedArrow` is useful for showing a curved connector, but `GrowArrow` is documented and reliable for `Arrow`; using it on non-`Arrow` tipable routes can stall or become brittle.
- If you want to test `GrowArrow` on a nonstandard arrow-like mobject, isolate that one case in a short low-quality render before building the full scene around it.

## Visual Pattern

Use this structure when teaching or comparing arrow APIs:

1. Show a faint gray ghost of the full arrow route during the opening breath.
2. Mark the start point with the active accent, usually primary red.
3. Mark the end point in gray unless the destination is the active concept.
4. Fade the ghost route as the live arrow is created, so the final hold does not contain duplicate arrow geometry.
5. Keep labels subordinate. The moving arrow is the mechanism; text only names API parameters or start/end roles.
6. Hold one proof frame while the arrow is partially grown, and one resolved frame after every arrow is complete.

## Code Pattern

```python
arrow = Arrow(
    start=start,
    end=end,
    buff=0.14,
    stroke_width=7,
    tip_length=0.24,
    color=GRAY_900,
)
ghost = arrow.copy().set_color(GRAY_300).set_stroke(width=4, opacity=0.44)
start_dot = Circle(radius=0.075, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1).move_to(start)
end_dot = Circle(radius=0.075, stroke_width=0, fill_color=GRAY_500, fill_opacity=1).move_to(end)

self.add(ghost, start_dot, end_dot)
self.wait(2.5)
self.play(GrowArrow(arrow), FadeOut(ghost), run_time=2.2, rate_func=smooth)
```

For `point_color`:

```python
self.play(
    GrowArrow(arrow, point_color=PRIMARY_RED),
    start_dot.animate.scale(1.8),
    FadeOut(ghost),
    run_time=2.35,
    rate_func=rate_functions.ease_in_out_cubic,
)
self.play(start_dot.animate.scale(1 / 1.8), run_time=0.4)
```

For a curved route:

```python
curved = CurvedArrow(
    start_point=start,
    end_point=end,
    angle=-TAU / 5,
    stroke_width=6,
    tip_length=0.22,
    color=PRIMARY_PURPLE,
)
self.play(Create(curved), FadeOut(ghost), run_time=2.55, rate_func=smooth)
```

## Labels And Typography

- Use a monospaced font for code-like labels when underscores, punctuation, or exact parameter names are part of the lesson. Proportional diagram fonts can make `point_color` or `PRIMARY_RED` hard to read.
- Use normal sans text for conceptual labels such as `start`, `end`, and short titles.
- Keep `start` and `end` labels gray when composition audits should focus on the active colored arrow. Use the red dot or ring, not red text, to mark the active start point.

## Composition Guidance

- Align arrow lanes high enough inside panels that the active saturated content remains visually centered. Start/end labels below the lane can otherwise make the colored content read bottom-heavy in audits.
- Remove or fade preview routes after they have served their purpose. A gray ghost that stays under the live arrow creates duplicate geometry and crowding notices.
- Make the arrow thick enough to survive a still frame, especially when the scene is a teaching gallery with multiple small panels.
- Use square-corner panels and a light page background when the scene includes code labels; transparent-only clips with labels are harder to inspect outside a slide.
- If several arrows end in a simultaneous hold, make one final action unify them, such as recoloring all live arrows to primary red after the start anchors have been established.

## Validation

- Render the real video, then extract proof frames before accepting the result.
- Sample at least:
  - opening breath with ghost routes visible,
  - mid-growth of the first `GrowArrow`,
  - the `point_color` proof frame,
  - the `DoubleArrow` proof frame if used,
  - any curved-route `Create` proof frame,
  - final unified hold.
- Run the frame composition audit at 0.5 second cadence. Treat `low_visual_margin` and `off_center_content` as patch prompts; review `possible_overlap_or_crowding` full-size when arrows, dots, rings, or ghost routes intentionally sit near each other.
- Run the resting mobject audit for multi-panel teaching scenes, because panel borders, titles, labels, and start/end markers all count as real layout objects.

## Common Failures

- Using `GrowArrow` on a curved tipable route without testing it first can make the render stall.
- Leaving a ghost arrow under the live arrow makes the final state look heavier and can trigger crowding notices.
- Red labels around every start marker can pull the active-content bounding box downward. Prefer a red dot or ring plus gray text.
- Small proportional code labels can hide underscores; switch to a monospaced label.
- A two-headed arrow without an explicit start marker can obscure the lesson that growth still begins from the declared start point.
