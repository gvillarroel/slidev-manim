# Mermaid Sequence Boundary

## Purpose

This spike explains a Mermaid sequence diagram with a boundary actor and a service actor.

It combines:

- a Mermaid diagram authored directly in Slidev Markdown,
- a transparent Manim video that visually reinforces the request and response exchange,
- the canonical project color system for both the slide and the animation.

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-sequence-boundary/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-sequence-boundary/
```

Expected outputs:

```text
videos/mermaid-sequence-boundary/mermaid-sequence-boundary.webm
videos/mermaid-sequence-boundary/mermaid-sequence-boundary.png
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/mermaid-sequence-boundary/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/mermaid-sequence-boundary/slides.md
```

## Learnings

- Sequence diagrams work well when Mermaid carries the exact protocol and Manim reinforces the timing and direction of the exchange.
- A transparent Manim video is useful here because the slide keeps ownership of the layout, labels, and diagram framing.
- The canonical project palette is strong enough to separate request and response without introducing a second ad hoc color system.
