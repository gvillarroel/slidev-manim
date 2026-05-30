#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "imageio-ffmpeg>=0.6.0",
#   "manim>=0.20.0",
#   "Pillow>=10.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, AnimationGroup, Create, FadeIn, FadeOut, Line, Rectangle, Scene, Transform, VGroup, smooth, there_and_back

SPIKE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SPIKE_DIR.parent.parent
SPIKES_DIR = SPIKE_DIR.parent
if str(SPIKES_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKES_DIR))

from _common.components import bridge_lane, gate_column, mask_window, neutral_cluster, open_slot, pulse, slab, terminal_brackets_around, time_rail
from _common.runner import convert_video_to_gif, render_scene
from _common.visual import GRAY_100, GRAY_200, GRAY_300, GRAY_400, GRAY_500, GRAY_600, PRIMARY_RED, WHITE_HEX, configure_transparent_scene

SPIKE_NAME = SPIKE_DIR.name
OUTPUT_DIR = REPO_ROOT / "videos" / SPIKE_NAME
DOC_GIF_DIR = REPO_ROOT / ".specs" / "assets" / "component-demos"


class ReceiverSlotDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        slot = open_slot(4.1, 2.15, opacity=0.42).move_to(ORIGIN)
        card = slab(GRAY_600, 1.45, 0.62).move_to(LEFT * 3.35)
        actor = pulse(0.14).move_to(LEFT * 2.0 + UP * 0.72)
        terminal = terminal_brackets_around(card.copy().move_to(ORIGIN), padding=0.34)
        self.add(slot, card, actor)
        self.wait(0.7)
        self.play(slot.animate.set_stroke(color=PRIMARY_RED, opacity=0.74), actor.animate.move_to(LEFT * 1.35 + UP * 0.72), run_time=0.55, rate_func=smooth)
        self.play(card.animate.move_to(ORIGIN), actor.animate.move_to(RIGHT * 1.15 + UP * 0.72), run_time=1.2, rate_func=smooth)
        self.play(FadeOut(slot), FadeOut(actor), FadeIn(terminal), run_time=0.45)
        self.play(card.animate.scale(1.05), run_time=0.35, rate_func=there_and_back)
        self.wait(1.2)


class TerminalBracketsDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        cluster = neutral_cluster().scale(1.15).move_to(ORIGIN)
        brackets = terminal_brackets_around(cluster, padding=0.44)
        guide = open_slot(cluster.width + 1.0, cluster.height + 0.92, color=GRAY_200, opacity=0.32)
        self.add(guide, cluster)
        self.wait(0.7)
        self.play(Create(brackets), guide.animate.set_opacity(0.0), run_time=0.8, rate_func=smooth)
        self.play(cluster.animate.scale(1.04), run_time=0.35, rate_func=there_and_back)
        self.wait(1.55)


class BridgeLaneDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        lane = bridge_lane(width=4.4, gap=1.1, opacity=0.46)
        source = neutral_cluster().scale(0.9).move_to(LEFT * 4.0)
        target_slot = open_slot(2.1, 1.45, opacity=0.46).move_to(RIGHT * 3.6)
        actor = pulse(0.15).move_to(LEFT * 2.25 + UP * 0.8)
        final = neutral_cluster().scale(0.9).move_to(RIGHT * 3.6)
        self.add(lane, source, target_slot, actor)
        self.wait(0.7)
        self.play(lane.animate.set_opacity(0.86), actor.animate.move_to(LEFT * 1.7 + UP * 0.8), run_time=0.5, rate_func=smooth)
        self.play(Transform(source, final), actor.animate.move_to(RIGHT * 2.05 + UP * 0.8), run_time=1.55, rate_func=smooth)
        self.play(FadeOut(lane), FadeOut(target_slot), FadeOut(actor), run_time=0.45)
        self.wait(1.15)


class RhythmGateDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        rail = Line(LEFT * 4.75, RIGHT * 4.75, color=GRAY_200, stroke_width=4).set_opacity(0.42)
        gates = VGroup(gate_column().move_to(LEFT * 2.2), gate_column().move_to(ORIGIN), gate_column().move_to(RIGHT * 2.2))
        actor = pulse(0.2).move_to(LEFT * 4.45)
        marks = VGroup(*[Rectangle(width=0.46, height=0.12, stroke_width=0, fill_color=GRAY_300, fill_opacity=0.75).move_to(RIGHT * x + DOWN * 2.25) for x in (-2.2, 0, 2.2)])
        self.add(rail, gates, marks, actor)
        self.wait(0.55)
        for index, x in enumerate([-2.2, 0, 2.2]):
            gate = gates[index]
            self.play(actor.animate.move_to(RIGHT * (x - 0.68)), run_time=0.45, rate_func=smooth)
            self.play(gate[0].animate.shift(UP * 0.28), gate[1].animate.shift(DOWN * 0.28), gate[2].animate.set_color(PRIMARY_RED), gate[3].animate.set_color(PRIMARY_RED), run_time=0.35)
            self.play(actor.animate.move_to(RIGHT * (x + 0.68)), marks[index].animate.set_fill(PRIMARY_RED, opacity=1), run_time=0.42)
            self.play(gate[0].animate.shift(DOWN * 0.28), gate[1].animate.shift(UP * 0.28), gate[2].animate.set_color(GRAY_200), gate[3].animate.set_color(GRAY_200), marks[index].animate.set_fill(GRAY_500, opacity=0.75), run_time=0.25)
        self.play(actor.animate.move_to(RIGHT * 4.45), run_time=0.45, rate_func=smooth)
        self.play(FadeOut(gates), rail.animate.set_opacity(0.16), run_time=0.45)
        self.wait(1.0)


class TimeRailDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        rail = time_rail(ticks=4).move_to(LEFT * 3.7)
        active = Line(LEFT * 3.7 + DOWN * 2.3, LEFT * 3.7 + DOWN * 2.3, color=PRIMARY_RED, stroke_width=5)
        cards = VGroup(*[open_slot(2.2, 0.62, opacity=0.38).move_to(LEFT * 0.35 + UP * y) for y in (-1.55, -0.5, 0.55, 1.6)])
        fills = VGroup(*[slab(GRAY_600 if i % 2 else GRAY_400, 1.72, 0.38).move_to(cards[i]) for i in range(4)])
        self.add(rail, active, cards)
        self.wait(0.7)
        for index, y in enumerate([-1.55, -0.5, 0.55, 1.6]):
            end_y = -2.3 + (index + 1) * (4.6 / 4)
            branch = Line(LEFT * 3.48 + UP * end_y, fills[index].get_left(), color=GRAY_200, stroke_width=2.2).set_opacity(0.56)
            self.play(active.animate.put_start_and_end_on(LEFT * 3.7 + DOWN * 2.3, LEFT * 3.7 + UP * end_y), Create(branch), run_time=0.45, rate_func=smooth)
            self.play(FadeIn(fills[index]), cards[index].animate.set_opacity(0.12), run_time=0.35)
        self.play(FadeOut(cards), FadeIn(terminal_brackets_around(fills, padding=0.26)), run_time=0.55)
        self.wait(1.05)


class MaskWindowDemo(Scene):
    def construct(self) -> None:
        configure_transparent_scene(self)
        row = VGroup(*[slab(GRAY_600 if i % 2 else GRAY_400, 1.1, 0.42).move_to(LEFT * 3.15 + RIGHT * i * 2.1 + UP * 0.9) for i in range(4)])
        slots = VGroup(*[open_slot(1.1, 0.88, opacity=0.34).move_to(row[i].get_center() + DOWN * 1.85) for i in range(4)])
        mask = mask_window(height=3.7).move_to(LEFT * 4.25)
        outputs = VGroup(*[pulse(0.24 if i == 3 else 0.18, PRIMARY_RED if i == 3 else GRAY_500).move_to(slots[i]) for i in range(4)])
        self.add(row, slots, mask)
        self.wait(0.7)
        for index, x in enumerate([-3.15, -1.05, 1.05, 3.15]):
            line = Line(row[index].get_bottom(), slots[index].get_top(), color=PRIMARY_RED, stroke_width=3.4)
            self.play(mask.animate.move_to(RIGHT * x), run_time=0.45, rate_func=smooth)
            self.play(Create(line), FadeIn(outputs[index]), slots[index].animate.set_opacity(0.12), run_time=0.35)
            self.play(line.animate.set_color(GRAY_300).set_opacity(0.3), run_time=0.18)
        self.play(FadeOut(mask), FadeOut(row), FadeOut(slots), outputs.animate.arrange(RIGHT, buff=0.28).move_to(ORIGIN), run_time=0.65, rate_func=smooth)
        self.play(FadeIn(terminal_brackets_around(outputs, padding=0.34)), run_time=0.45)
        self.wait(1.0)


SCENES = {
    "receiver-slot": ReceiverSlotDemo,
    "terminal-brackets": TerminalBracketsDemo,
    "bridge-lane": BridgeLaneDemo,
    "rhythm-gate": RhythmGateDemo,
    "time-rail": TimeRailDemo,
    "mask-window": MaskWindowDemo,
}


class _Args(argparse.Namespace):
    quality: str
    component: str
    skip_gifs: bool


def parse_args() -> _Args:
    parser = argparse.ArgumentParser(description="Render common component GIF demos.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "production", "4k"), default="low")
    parser.add_argument("--component", choices=("all", *SCENES.keys()), default="all")
    parser.add_argument("--skip-gifs", action="store_true")
    return parser.parse_args(namespace=_Args())


def selected_components(args: _Args) -> list[str]:
    return list(SCENES.keys()) if args.component == "all" else [args.component]


def main() -> int:
    args = parse_args()
    DOC_GIF_DIR.mkdir(parents=True, exist_ok=True)
    for slug in selected_components(args):
        scene = SCENES[slug]
        component_dir = OUTPUT_DIR / "components" / slug
        rendered = render_scene(Path(__file__).resolve(), scene.__name__, component_dir, quality=args.quality, output_stem=slug)
        if not args.skip_gifs:
            gif_path = component_dir / f"{slug}.gif"
            convert_video_to_gif(rendered.video, gif_path)
            shutil.copy2(gif_path, DOC_GIF_DIR / gif_path.name)
            print(f"gif={gif_path}")
            print(f"doc_gif={DOC_GIF_DIR / gif_path.name}")
        print(f"video={rendered.video}")
        print(f"poster={rendered.poster}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

