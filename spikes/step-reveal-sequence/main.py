#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "manim>=0.19.0",
# ]
# ///

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import manimpango

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
STAGING_DIR = OUTPUT_DIR / ".manim"

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
WHITE = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
SHADOW_BLUE = "#004d66"
PAGE_BACKGROUND = "#f7f7f7"


def pick_text_font() -> str:
    fonts = set(manimpango.list_fonts())
    for candidate in ("Open Sans", "Arial", "Sans"):
        if candidate in fonts:
            return candidate
    return "Sans"


TEXT_FONT = pick_text_font()

VARIANTS = {
    "intro": {
        "scene": "StepRevealIntroScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-intro.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-intro.png",
    },
    "context": {
        "scene": "StepRevealContextScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-context.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-context.png",
    },
    "wrap": {
        "scene": "StepRevealWrapScene",
        "resolution": "1920,1080",
        "output": OUTPUT_DIR / "step-reveal-sequence-wrap.webm",
        "poster": OUTPUT_DIR / "step-reveal-sequence-wrap.png",
    },
}


class _Args(argparse.Namespace):
    quality: str
    preview: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(
        description="Render the step-reveal-sequence Manim spike."
    )
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "production", "4k"),
        default="medium",
        help="Manim quality preset. Defaults to medium for presentation review.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the rendered output after rendering.",
    )
    return parser.parse_args(namespace=_Args())


def quality_flag(quality: str) -> str:
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
        "4k": "-qk",
    }[quality]


def render_command(args: _Args, variant_name: str, poster: bool) -> list[str]:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    variant = VARIANTS[variant_name]

    command = [
        sys.executable,
        "-m",
        "manim",
        "render",
        quality_flag(args.quality),
        "-r",
        variant["resolution"],
        "-o",
        Path(variant["poster"] if poster else variant["output"]).stem,
        "--media_dir",
        str(STAGING_DIR),
    ]

    if not poster:
        command.extend(["--format", "webm", "-t"])
    else:
        command.append("-s")

    if args.preview:
        command.append("-p")

    command.extend([str(Path(__file__).resolve()), variant["scene"]])
    return command


def promote_rendered_file(target_name: str, destination: Path) -> None:
    matches = sorted(
        STAGING_DIR.glob(f"**/{target_name}"),
        key=lambda path: path.stat().st_mtime,
    )
    if not matches:
        raise FileNotFoundError(f"Could not find {target_name} under {STAGING_DIR}")

    source = matches[-1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def run_variant(args: _Args, variant_name: str) -> int:
    variant = VARIANTS[variant_name]
    print(f"Rendering {variant['scene']} into {variant['output']}")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    video_result = subprocess.run(
        render_command(args, variant_name, poster=False),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "video"},
    )
    if video_result.returncode != 0:
        return video_result.returncode
    promote_rendered_file(Path(variant["output"]).name, variant["output"])

    poster_result = subprocess.run(
        render_command(args, variant_name, poster=True),
        check=False,
        env={**os.environ, "SPIKE_RENDER_TARGET": "poster"},
    )
    if poster_result.returncode != 0:
        return poster_result.returncode
    promote_rendered_file(Path(variant["poster"]).name, variant["poster"])

    return 0


from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    Line,
    Rectangle,
    Scene,
    Square,
    Text,
    Transform,
    VGroup,
    linear,
)


class BaseStepRevealScene(Scene):
    headline = ""
    subtitle = ""
    card_title = ""
    card_body = ""
    final_label = ""
    stage_label = ""
    show_context = False
    show_wrap = False

    def construct(self) -> None:
        if os.environ.get("SPIKE_RENDER_TARGET") == "poster":
            self.camera.background_color = PAGE_BACKGROUND

        stage = Rectangle(
            width=12.5,
            height=6.72,
            stroke_width=0,
            fill_color=PAGE_BACKGROUND,
            fill_opacity=0.96,
        )

        title = self._text(self.headline, 33, GRAY)
        title.to_edge(UP, buff=0.72)
        subtitle = self._text(self.subtitle, 18, GRAY_600)
        if subtitle.width > 10.6:
            subtitle.scale_to_fit_width(10.6)
        subtitle.next_to(title, DOWN, buff=0.12)

        label = self._text(self.stage_label, 16, GRAY_700)
        label.move_to(LEFT * 3.72 + UP * 1.95)
        source_cards = self._build_source_cards()
        target_slots, target_fills = self._build_target_slots()
        routes = self._build_routes(source_cards, target_slots)

        source_label = self._text("source", 14, GRAY_600)
        source_label.next_to(source_cards, UP, buff=0.16)
        target_label = self._text("revealed", 14, GRAY_600)
        target_label.next_to(target_slots, UP, buff=0.16)

        pulse = Circle(radius=0.13, stroke_width=0, fill_color=PRIMARY_RED, fill_opacity=1)
        pulse.move_to(source_cards[0].get_right() + RIGHT * 0.25)

        self.add(
            stage,
            title,
            subtitle,
            label,
            source_label,
            target_label,
            source_cards,
            target_slots,
            routes,
            pulse,
        )
        self.wait(2.4)

        for index in range(3):
            self._reveal_step(index, source_cards, target_slots, target_fills, routes, pulse)

        support_group = None
        if self.show_context:
            support_group = self._build_context_support(target_slots)
            self.play(FadeIn(support_group, shift=UP * 0.12), run_time=1.0)
            self.play(
                Indicate(support_group[1], color=PRIMARY_RED, scale_factor=1.03),
                run_time=1.0,
            )
            self.wait(1.0)

        resolved_members = [target_fills, target_slots]
        if support_group is not None and not self.show_wrap:
            resolved_members.append(support_group)
        resolved = VGroup(*resolved_members)
        cleanup = [routes, source_cards, source_label, target_label, label]
        if support_group is not None and self.show_wrap:
            cleanup.append(support_group)

        self.play(
            AnimationGroup(
                *[FadeOut(mob) for mob in cleanup],
                resolved.animate.move_to(UP * 0.1).scale(1.08),
                FadeOut(pulse),
                lag_ratio=0.05,
            ),
            run_time=1.8,
        )

        if self.show_wrap:
            badge = self._build_terminal_badge()
            arrow = Arrow(
                resolved.get_bottom() + DOWN * 0.12,
                badge.get_top() + UP * 0.08,
                color=PRIMARY_RED,
                stroke_width=5,
                buff=0.08,
                max_tip_length_to_length_ratio=0.12,
            )
            self.play(GrowArrow(arrow), run_time=0.85)
            self.play(FadeIn(badge, shift=DOWN * 0.12), run_time=0.9)
            self.play(FadeOut(arrow), run_time=0.8)
        else:
            halo = Rectangle(
                width=resolved.width + 0.5,
                height=resolved.height + 0.42,
                stroke_color=PRIMARY_RED,
                stroke_width=3,
                fill_opacity=0,
            )
            halo.move_to(resolved)
            self.play(Create(halo), run_time=1.0)

        self.wait(6.2)

    def _text(self, value: str, font_size: int, color: str) -> Text:
        return Text(value, font=TEXT_FONT, font_size=font_size, color=color)

    def _build_source_cards(self) -> VGroup:
        cards = VGroup()
        labels = ("motion", "context", "outcome")
        colors = (PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE)
        for index, (label, color) in enumerate(zip(labels, colors, strict=True)):
            box = Rectangle(
                width=2.1,
                height=0.62,
                stroke_color=GRAY_300,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=0.92,
            )
            swatch = Rectangle(
                width=0.16,
                height=0.62,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.92,
            )
            swatch.align_to(box, LEFT)
            swatch.align_to(box, UP)
            number = self._text(f"{index + 1}", 18, GRAY)
            number.move_to(box.get_left() + RIGHT * 0.42)
            text = self._text(label, 15, GRAY_700)
            text.move_to(box.get_center() + RIGHT * 0.36)
            card = VGroup(box, swatch, number, text)
            card.move_to(LEFT * 3.72 + UP * (0.9 - index * 0.92))
            cards.add(card)
        return cards

    def _build_target_slots(self) -> tuple[VGroup, VGroup]:
        slots = VGroup()
        fills = VGroup()
        colors = (PRIMARY_GREEN, PRIMARY_BLUE, PRIMARY_PURPLE)
        for index, color in enumerate(colors):
            slot = Rectangle(
                width=1.25,
                height=0.74,
                stroke_color=GRAY_300,
                stroke_width=2.2,
                fill_opacity=0,
            )
            slot.move_to(RIGHT * 2.92 + UP * (0.9 - index * 0.92))
            core = Rectangle(
                width=0.84,
                height=0.38,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.9,
            )
            core.move_to(slot)
            slots.add(slot)
            fills.add(core)
        return slots, fills

    def _build_routes(self, source_cards: VGroup, target_slots: VGroup) -> VGroup:
        routes = VGroup()
        for source, target in zip(source_cards, target_slots, strict=True):
            route = Line(
                source.get_right() + RIGHT * 0.18,
                target.get_left() + LEFT * 0.18,
                color=GRAY_200,
                stroke_width=4,
                stroke_opacity=0.55,
            )
            routes.add(route)
        return routes

    def _reveal_step(
        self,
        index: int,
        source_cards: VGroup,
        target_slots: VGroup,
        target_fills: VGroup,
        routes: VGroup,
        pulse: Circle,
    ) -> None:
        source = source_cards[index]
        slot = target_slots[index]
        fill = target_fills[index]
        route = routes[index]
        active_route = Line(
            route.get_start(),
            route.get_end(),
            color=PRIMARY_ORANGE,
            stroke_width=5,
        )
        pulse.move_to(route.get_start())

        self.play(
            source[0].animate.set_stroke(PRIMARY_RED, width=3),
            Create(active_route),
            run_time=0.75,
        )
        self.play(
            pulse.animate.move_to(slot.get_center()),
            run_time=2.0,
            rate_func=linear,
        )
        self.play(
            FadeIn(fill, scale=0.78),
            Transform(active_route, route.copy().set_color(GRAY_300).set_stroke(width=3, opacity=0.5)),
            slot.animate.set_stroke(PRIMARY_RED, width=3),
            run_time=0.85,
        )
        self.play(
            source[0].animate.set_stroke(GRAY_300, width=2),
            slot.animate.set_stroke(GRAY_300, width=2.2),
            FadeOut(active_route),
            pulse.animate.move_to(route.get_end() + RIGHT * 0.22),
            run_time=0.65,
        )
        self.add(fill)
        self.wait(1.35)

    def _build_context_support(self, target_slots: VGroup) -> VGroup:
        rail = Rectangle(
            width=5.2,
            height=0.74,
            stroke_color=GRAY_300,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.88,
        )
        rail.next_to(target_slots, DOWN, buff=0.44)
        words = VGroup(
            self._text("why", 14, GRAY_700),
            self._text("tradeoff", 14, GRAY_700),
            self._text("next", 14, GRAY_700),
        )
        for word, x_offset in zip(words, (-1.55, 0, 1.55), strict=True):
            word.move_to(rail.get_center() + RIGHT * x_offset)
        ticks = VGroup()
        for word in words:
            tick = Square(
                side_length=0.13,
                stroke_width=0,
                fill_color=PRIMARY_RED,
                fill_opacity=0.9,
            )
            tick.next_to(word, LEFT, buff=0.14)
            ticks.add(tick)
        return VGroup(rail, words, ticks)

    def _build_terminal_badge(self) -> VGroup:
        badge = Rectangle(
            width=3.85,
            height=0.82,
            stroke_color=PRIMARY_RED,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=0.92,
        )
        label = self._text(self.final_label, 18, GRAY)
        if label.width > badge.width - 0.4:
            label.scale_to_fit_width(badge.width - 0.4)
        label.move_to(badge.get_center())
        group = VGroup(badge, label)
        group.move_to(DOWN * 2.35)
        return group


class StepRevealIntroScene(BaseStepRevealScene):
    headline = "Step Reveal Sequence"
    subtitle = "One route creates three visible receivers before the slide adds words."
    stage_label = "same motion, clearer states"
    card_title = ""
    card_body = ""
    final_label = ""


class StepRevealContextScene(BaseStepRevealScene):
    headline = "Step 1: Add context"
    subtitle = "The same handoff now leaves a small support structure behind."
    stage_label = "motion plus context"
    card_title = "Why this matters"
    card_body = "Stable reuse keeps the story legible."
    final_label = ""
    show_context = True


class StepRevealWrapScene(BaseStepRevealScene):
    headline = "Step 2: Close the loop"
    subtitle = "Cleanup moves the revealed states into one resolved landing."
    stage_label = "context becomes outcome"
    card_title = "What changed"
    card_body = "The result now owns the emphasis."
    final_label = "Ready for the slide narrative"
    show_context = True
    show_wrap = True


def main() -> int:
    args = parse_args()
    for variant_name in VARIANTS:
        result = run_variant(args, variant_name)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
