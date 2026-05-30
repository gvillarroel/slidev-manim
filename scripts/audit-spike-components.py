#!/usr/bin/env python
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SPIKES_DIR = REPO_ROOT / "spikes"
OUTPUT_PATH = REPO_ROOT / ".specs" / "knowledge" / "spike-component-review.md"

SKIP_DIRS = {"_common", "__pycache__", "component-library-demos"}

COMPONENT_KEYWORDS = {
    "aperture": "aperture_shutters",
    "arc": "arc_handoff",
    "bridge": "bridge_lane",
    "bumper": "bumper_stop",
    "clamp": "clamp_pair",
    "compression": "compression_channel",
    "corridor": "corridor_rails",
    "cradle": "cradle_catch",
    "counterlift": "balance_beam",
    "counterweight": "balance_beam",
    "deformation": "deformation_wave",
    "echo": "settle_echo",
    "edge": "edge_tension_marker",
    "fork": "fork_guides",
    "funnel": "merge_funnel",
    "fan": "fan_guides",
    "gate": "gate_column",
    "hinge": "hinge_pivot",
    "keystone": "keystone_lock",
    "latched": "latch_anchor",
    "layered": "layered_stack",
    "magnet": "magnet_capture",
    "mask": "mask_window",
    "negative": "negative_space_frame",
    "occlusion": "occlusion_peel",
    "orbit": "orbit_guides",
    "parallax": "parallax_planes",
    "pressure": "pressure_wall",
    "pulse": "pulse",
    "ramp": "ramp_plane",
    "receiver": "receiver_slot",
    "relay": "relay_nodes",
    "rhythm": "rhythm_gate_marks",
    "shear": "shear_rails",
    "sleeve": "sleeve_channel",
    "sling": "sling_arc",
    "snap": "snap_recoil_stop",
    "staged": "convergence_lane",
    "slot": "open_slot",
    "terminal": "terminal_brackets",
    "time-rail": "time_rail",
    "weave": "weave_crossing",
}

QUALITY_CANDIDATES = {
    "arc": "arc handoff guide",
    "bumper": "bumper deflection stop",
    "clamp": "clamp pair",
    "compression": "compression channel",
    "corridor": "corridor rails",
    "counterlift": "counterlift balance",
    "counterweight": "counterweight balance",
    "cradle": "cradle catch",
    "deformation": "deformation flow",
    "echo": "settle echo",
    "edge": "edge tension marker",
    "fan": "fan splay guides",
    "hinge": "hinge pivot",
    "keystone": "keystone lock",
    "latched": "latch anchor",
    "layered": "layered reveal stack",
    "magnet": "magnet capture",
    "negative": "negative-space focus frame",
    "occlusion": "occlusion peel",
    "parallax": "parallax planes",
    "ramp": "ramp lift",
    "relay": "relay handoff nodes",
    "scale": "scale hierarchy slots",
    "shear": "shear resolve rails",
    "sleeve": "sleeve reveal channel",
    "sling": "sling release",
    "snap": "snap recoil stop",
    "staged": "staged convergence lane",
    "throat": "throat gate",
    "weave": "weave crossing",
}

RED_DOT_CANDIDATES = {
    "alignment": "alignment guides",
    "anchor": "anchor marker",
    "arch": "arch guide",
    "balance": "balance beam",
    "beacon": "beacon pulse",
    "bloom": "bloom field",
    "bumper": "bumper stop",
    "caliper": "caliper gauge",
    "circuit": "circuit route",
    "coil": "coil guide",
    "compass": "compass sweep",
    "constellation": "constellation nodes",
    "cradle": "cradle catch",
    "crank": "crank pivot",
    "crown": "crown terminal",
    "domino": "domino row",
    "dovetail": "dovetail socket",
    "eclipse": "eclipse mask",
    "fold": "fold hinge",
    "glyph": "glyph marker",
    "harbor": "harbor slot",
    "hourglass": "hourglass choke",
    "iris": "iris aperture",
    "keyhole": "keyhole mask",
    "kite": "kite guide",
    "knot": "knot path",
    "labyrinth": "labyrinth route",
    "lantern": "lantern reveal",
    "latch": "latch hook",
    "lattice": "lattice grid",
    "lens": "lens focus",
    "loom": "loom weave",
    "membrane": "membrane flex",
    "mirror": "mirror plane",
    "moire": "moire overlay",
    "narrative": "narrative stage",
    "peel": "peel layer",
    "pendulum": "pendulum arc",
    "piston": "piston channel",
    "prism": "prism split",
    "pulley": "pulley route",
    "radial": "radial focus",
    "ramp": "ramp lift",
    "ratchet": "ratchet steps",
    "relay": "relay nodes",
    "resonance": "resonance rings",
    "rivet": "rivet pin",
    "rosette": "rosette guide",
    "semaphore": "semaphore arms",
    "shear": "shear rails",
    "sling": "sling release",
    "splice": "splice join",
    "spring": "spring recoil",
    "switchback": "switchback route",
    "thread": "thread path",
    "threshold": "threshold gate",
    "tuning": "tuning fork",
    "turbine": "turbine rotor",
    "vault": "vault door",
    "weave": "weave crossing",
    "zipper": "zipper track",
}


@dataclass(frozen=True)
class SpikeReview:
    name: str
    family: str
    decision: str
    reusable_surface: str
    evidence: str


def public_components() -> set[str]:
    source = (SPIKES_DIR / "_common" / "components.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    return {node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")}


def family_for(name: str) -> str:
    if name.startswith("quality-"):
        return "quality mechanism"
    if name.startswith("red-dot-") or name == "red-point-narrative-spa":
        return "browser-native red-dot"
    if name.startswith("mermaid-"):
        return "mermaid"
    if name.startswith("manim-"):
        return "manim lab"
    if name.startswith("mind-map-"):
        return "mind-map"
    if name.startswith("time-rail-") or name == "timeline-stack":
        return "time rail"
    return "presentation/spike"


def text_evidence(spike_dir: Path) -> str:
    evidence = []
    if (spike_dir / "README.md").exists():
        evidence.append("README")
    if (spike_dir / "main.py").exists():
        evidence.append("main.py")
    if (spike_dir / "index.html").exists():
        evidence.append("browser files")
    if (spike_dir / "slides.md").exists():
        evidence.append("slides")
    return ", ".join(evidence) or "directory name"


def component_from_keywords(name: str, components: set[str]) -> str | None:
    for keyword, component in COMPONENT_KEYWORDS.items():
        if keyword in name and component in components:
            return component
    return None


def review_spike(spike_dir: Path, components: set[str]) -> SpikeReview:
    name = spike_dir.name
    family = family_for(name)
    evidence = text_evidence(spike_dir)

    existing = component_from_keywords(name, components)
    if existing:
        return SpikeReview(name, family, "componentized", existing, evidence)

    if name.startswith("quality-"):
        mechanism = name.removeprefix("quality-")
        key = mechanism.split("-", 1)[0]
        surface = QUALITY_CANDIDATES.get(key, mechanism.replace("-", " "))
        return SpikeReview(name, family, "candidate", surface, evidence)

    if name.startswith("red-dot-"):
        motif = name.removeprefix("red-dot-").removesuffix("-spa")
        key = motif.split("-", 1)[0]
        surface = RED_DOT_CANDIDATES.get(key, motif.replace("-", " "))
        return SpikeReview(name, family, "candidate", surface, evidence)

    if name.startswith("mermaid-") and name.endswith("-svg-unfold"):
        return SpikeReview(name, family, "shared-runner", "mermaid_svg_unfold_engine", evidence)

    if name in {"mermaid-svg-component-remap", "mermaid-svg-direct-insert", "svg-subelement-transform", "diagram-svg-video-manipulation"}:
        return SpikeReview(name, family, "candidate", "svg role remap helpers", evidence)

    if name.startswith("time-rail-") or name == "timeline-stack":
        return SpikeReview(name, family, "componentized", "time_rail", evidence)

    if "callout" in name:
        return SpikeReview(name, family, "candidate", "callout panel", evidence)
    if "device-frame" in name:
        return SpikeReview(name, family, "candidate", "device content frame", evidence)
    if "grid" in name:
        return SpikeReview(name, family, "candidate", "multi-video grid", evidence)
    if "mind-map" in name:
        return SpikeReview(name, family, "candidate", "mind-map branch guides", evidence)

    return SpikeReview(name, family, "no-component", "workflow, API, layout, or reference experiment", evidence)


def write_review(reviews: list[SpikeReview]) -> None:
    decision_counts: dict[str, int] = {}
    for review in reviews:
        decision_counts[review.decision] = decision_counts.get(review.decision, 0) + 1

    rows = "\n".join(
        f"| `{review.name}` | {review.family} | {review.decision} | {review.reusable_surface} | {review.evidence} |"
        for review in reviews
    )
    summary = "\n".join(f"- {decision}: {decision_counts[decision]}" for decision in sorted(decision_counts))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        "\n".join(
            [
                "---",
                "title: Spike Component Review",
                f"updated: {date.today().isoformat()}",
                "---",
                "",
                "# Spike Component Review",
                "",
                "This matrix tracks the current review pass for every spike directory and whether it should feed the reusable component catalog.",
                "The review uses each spike directory name plus available README, `main.py`, browser, and slide artifacts as current-state evidence.",
                "",
                "Decision meanings:",
                "",
                "- `componentized`: the spike is already represented by an exported common component or composite catalog demo.",
                "- `candidate`: the spike contains a reusable visual or motion surface that should be extracted or refined.",
                "- `shared-runner`: the spike already uses shared infrastructure, and the reusable unit is not a GIF catalog component yet.",
                "- `no-component`: the spike is primarily a workflow, API, layout, or reference experiment with no clear visual component to extract.",
                "",
                "Summary:",
                "",
                summary,
                "",
                "## Review Matrix",
                "",
                "| Spike | Family | Decision | Reusable surface | Evidence checked |",
                "| --- | --- | --- | --- | --- |",
                rows,
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    components = public_components()
    reviews = [
        review_spike(path, components)
        for path in sorted(SPIKES_DIR.iterdir())
        if path.is_dir() and path.name not in SKIP_DIRS
    ]
    write_review(reviews)
    print(f"reviewed={len(reviews)}")
    print(f"output={OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
