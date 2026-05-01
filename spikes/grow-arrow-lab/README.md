# Grow Arrow Lab

This spike explores how ManimCE arrows can be introduced with `GrowArrow`.

The scene compares four arrow patterns:

- `Arrow(start, end, buff=...)` as the basic directed connector.
- `GrowArrow(arrow, point_color=...)` to show the collapsed start color before the arrow reaches its full style.
- `DoubleArrow(start, end)` to show that a two-headed arrow can still grow from the declared start point.
- `CurvedArrow(start, end, angle=...)` with `Create`, because `GrowArrow` is documented for `Arrow` and can be too brittle for curved-route experiments.

The design keeps each example in a separate square-corner panel, marks each start point in primary red, and holds the final state long enough to inspect how the growth anchor behaves across arrow types.

## Source References

- Manim Community `GrowArrow`: <https://docs.manim.community/en/stable/reference/manim.animation.growing.GrowArrow.html>
- Manim Community `Arrow`: <https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Arrow.html>
- Manim Community `CurvedArrow`: <https://docs.manim.community/en/stable/reference/manim.mobject.geometry.arc.CurvedArrow.html>
- Manim Community `DoubleArrow`: <https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.DoubleArrow.html>

## Render

From the repository root:

```bash
uv run --script spikes/grow-arrow-lab/main.py
```

Optional quality selection:

```bash
uv run --script spikes/grow-arrow-lab/main.py --quality low
uv run --script spikes/grow-arrow-lab/main.py --quality high
```

The promoted outputs are written to:

- `videos/grow-arrow-lab/grow-arrow-lab.webm`
- `videos/grow-arrow-lab/grow-arrow-lab.png`
