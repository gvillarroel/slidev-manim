from __future__ import annotations

from manim import RoundedRectangle, Text

BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#333e48"
PAGE_BACKGROUND = "#f7f7f7"
PRIMARY_RED = "#9e1b32"
PRIMARY_ORANGE = "#e77204"
PRIMARY_YELLOW = "#f1c319"
PRIMARY_GREEN = "#45842a"
PRIMARY_BLUE = "#007298"
PRIMARY_PURPLE = "#652f6c"
GRAY_100 = "#e7e7e7"
GRAY_200 = "#cfcfcf"
GRAY_300 = "#b5b5b5"
GRAY_400 = "#9c9c9c"
GRAY_500 = "#828282"
GRAY_600 = "#696969"
GRAY_700 = "#4f4f4f"
GRAY_800 = "#363636"
GRAY_900 = "#1c1c1c"
HIGHLIGHT_RED = "#ffccd5"
HIGHLIGHT_ORANGE = "#ffe5cc"
HIGHLIGHT_YELLOW = "#fff4cc"
HIGHLIGHT_GREEN = "#dbffcc"
HIGHLIGHT_BLUE = "#cdf3ff"
HIGHLIGHT_PURPLE = "#f9ccff"
SHADOW_RED = "#6d1222"
SHADOW_ORANGE = "#994a00"
SHADOW_YELLOW = "#98700c"
SHADOW_GREEN = "#294d19"
SHADOW_BLUE = "#004d66"
SHADOW_PURPLE = "#431f47"
STATUS_RED = "#e8002a"
STATUS_ORANGE = "#ff9633"
STATUS_YELLOW = "#ffd332"
STATUS_GREEN = "#36b300"
STATUS_BLUE = "#00ace6"
STATUS_PURPLE = "#9e00b3"


def stage_panel(
    width: float = 12.8,
    height: float = 7.15,
    corner_radius: float = 0.34,
    opacity: float = 0.96,
) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=corner_radius,
        stroke_width=0,
        fill_color=PAGE_BACKGROUND,
        fill_opacity=opacity,
    )


def soft_zone(width: float, height: float, opacity: float = 0.24) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.35,
        stroke_width=0,
        fill_color=GRAY_100,
        fill_opacity=opacity,
    )


def slab(color: str, width: float, height: float, opacity: float = 1.0) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=min(height * 0.28, 0.24),
        stroke_width=0,
        fill_color=color,
        fill_opacity=opacity,
    )


def fit_text_to_width(label: Text, max_width: float) -> Text:
    if label.width > max_width:
        label.scale_to_fit_width(max_width)
    return label
