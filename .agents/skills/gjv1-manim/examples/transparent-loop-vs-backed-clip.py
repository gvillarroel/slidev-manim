from __future__ import annotations

from manim import Circle, Dot, MoveAlongPath, Rectangle, Scene, Text, VGroup, linear

# Preferred color styles: references/preferred-color-styles.md in this skill.
BLACK = "#000000"
PRIMARY_RED = "#9e1b32"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_400 = "#9c9c9c"
PAGE_BACKGROUND = "#f7f7f7"
DEFAULT_FONT = "Open Sans"


class TransparentDecorativeLoop(Scene):
    """Keep transparent when the slide supplies the surface and the clip has no text."""

    def construct(self) -> None:
        orbit = Circle(radius=1.7, color=GRAY_400, stroke_width=8).set_stroke(opacity=0.72)
        dot = Dot(color=PRIMARY_RED, radius=0.12).move_to(orbit.point_from_proportion(0))
        self.add(orbit, dot)
        self.play(MoveAlongPath(dot, orbit), run_time=3.2, rate_func=linear)
        self.wait(0.2)


class BackedExplanatoryClip(Scene):
    """Add a local page-background stage when the clip contains labels or diagram text."""

    def construct(self) -> None:
        stage = Rectangle(
            width=12.8,
            height=4.35,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )
        source = Rectangle(width=2.4, height=1.0)
        source.set_stroke(BLACK, width=5, opacity=0.82)
        source.set_fill(GRAY_100, opacity=0.92)
        target = Rectangle(width=2.4, height=1.0)
        target.set_stroke(PRIMARY_RED, width=5, opacity=0.82)
        target.set_fill(GRAY_200, opacity=0.72)
        source.shift((-3.4, 0, 0))
        target.shift((3.4, 0, 0))
        labels = VGroup(
            Text("Source", font=DEFAULT_FONT, font_size=30, color=GRAY).move_to(source),
            Text("Target", font=DEFAULT_FONT, font_size=30, color=GRAY).move_to(target),
        )
        pulse = Dot(color=PRIMARY_RED, radius=0.14).move_to(source.get_right())
        guide = Rectangle(width=4.0, height=0.06)
        guide.set_stroke(PRIMARY_RED, width=0)
        guide.set_fill(PRIMARY_RED, opacity=0.55)
        guide.move_to((0, 0, 0))
        self.add(stage, source, target, labels, guide, pulse)
        self.play(pulse.animate.move_to(target.get_left()), run_time=2.2, rate_func=linear)
        self.wait(0.4)
