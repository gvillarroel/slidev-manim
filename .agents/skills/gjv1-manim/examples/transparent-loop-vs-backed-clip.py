from __future__ import annotations

from manim import Circle, Dot, MoveAlongPath, RoundedRectangle, Scene, Text, VGroup, linear

# Preferred color styles: ../references/preferred-color-styles.md
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
GRAY = "#333e48"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
PAGE_BACKGROUND = "#f7f7f7"


class TransparentDecorativeLoop(Scene):
    """Keep transparent when the slide supplies the surface and the clip has no text."""

    def construct(self) -> None:
        orbit = Circle(radius=1.7, color=PRIMARY_BLUE, stroke_width=8).set_stroke(opacity=0.72)
        dot = Dot(color=PRIMARY_YELLOW, radius=0.12).move_to(orbit.point_from_proportion(0))
        self.add(orbit, dot)
        self.play(MoveAlongPath(dot, orbit), run_time=3.2, rate_func=linear)
        self.wait(0.2)


class BackedExplanatoryClip(Scene):
    """Add a local page-background stage when the clip contains labels or diagram text."""

    def construct(self) -> None:
        stage = RoundedRectangle(
            width=12.8,
            height=4.35,
            corner_radius=0.3,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        source = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        source.set_stroke(PRIMARY_GREEN, width=6, opacity=0.82)
        source.set_fill(HIGHLIGHT_GREEN, opacity=0.92)
        target = RoundedRectangle(width=2.4, height=1.0, corner_radius=0.18)
        target.set_stroke(PRIMARY_BLUE, width=6, opacity=0.82)
        target.set_fill(HIGHLIGHT_BLUE, opacity=0.92)
        source.shift((-3.4, 0, 0))
        target.shift((3.4, 0, 0))
        labels = VGroup(
            Text("Source", font_size=30, color=GRAY).move_to(source),
            Text("Target", font_size=30, color=GRAY).move_to(target),
        )
        pulse = Dot(color=PRIMARY_YELLOW, radius=0.14).move_to(source.get_right())
        guide = RoundedRectangle(width=4.0, height=0.06, corner_radius=0.03)
        guide.set_stroke(PRIMARY_ORANGE, width=0)
        guide.set_fill(PRIMARY_ORANGE, opacity=0.55)
        guide.move_to((0, 0, 0))
        self.add(stage, source, target, labels, guide, pulse)
        self.play(pulse.animate.move_to(target.get_left()), run_time=2.2, rate_func=linear)
        self.wait(0.4)
