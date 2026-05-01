# Mermaid Layout Gallery

## Purpose

This spike creates a single Slidev presentation that showcases the main layout families already explored in this repository, but now driven by Mermaid diagrams plus transparent Manim explanation videos.

The gallery focuses on reusable layout families rather than derivative framing-only spikes.

Covered layout families:

- background loop layer
- corner callout
- side by side
- inset annotation
- compare two approaches
- timeline stack
- multi-video grid
- hero plus supporting loop
- device frame embed

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-layout-gallery/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-layout-gallery/
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/mermaid-layout-gallery/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/mermaid-layout-gallery/slides.md
```

## Notes

- All videos are rendered as transparent `.webm` assets.
- White `.png` posters are also generated for review and fallback.
- The deck uses the canonical project color system.
- Mermaid diagrams are themed to match the same palette used in the videos.
- The gallery videos are short autoplay loop embeds, not full 25-second narration scenes; the surrounding Slidev slide supplies the full reading time.
- For device-frame embeds, the Manim video should animate the content region only because the Slidev slide already provides the browser/device frame.
