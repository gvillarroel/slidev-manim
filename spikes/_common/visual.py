from __future__ import annotations

from manim import Scene, WHITE, config

PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"

BLACK = "#000000"
WHITE_HEX = "#ffffff"
GRAY = "#333e48"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
GRAY_900 = "#1c1c1c"
PAGE_BACKGROUND = "#f7f7f7"

PRIMARY_PALETTE = [
    PRIMARY_RED,
    PRIMARY_ORANGE,
    PRIMARY_YELLOW,
    PRIMARY_GREEN,
    PRIMARY_BLUE,
    PRIMARY_PURPLE,
]


def configure_transparent_scene(scene: Scene) -> None:
    config.transparent = True
    config.background_opacity = 0.0
    scene.camera.background_color = WHITE
    scene.camera.background_opacity = 0.0


def configure_white_scene(scene: Scene) -> None:
    scene.camera.background_color = WHITE
    scene.camera.background_opacity = 1.0

