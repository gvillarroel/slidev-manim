# Slide Step Handshake

## Purpose

This spike tests whether one Manim animation can carry a concept across consecutive Slidev slides without changing the visual language.

The same asset is reused on multiple slides so the deck can answer a simple question: can a single motion language support step-based narration while staying visually consistent?

## Run the render

From the repository root:

```bash
uv run --script spikes/slide-step-handshake/main.py
```

This renders the spike output into:

```text
videos/slide-step-handshake/
```

Expected outputs:

```text
videos/slide-step-handshake/slide-step-handshake.webm
videos/slide-step-handshake/slide-step-handshake.png
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/slide-step-handshake/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/slide-step-handshake/slides.md
```

## Notes

- The deck stays local to the spike so the experiment remains isolated.
- Slidev imports use Vite so the video asset resolves correctly.
- The render uses a transparent `.webm` for the real deck and a white `.png` poster for review and fallback.
- The same asset is reused across consecutive slides, but the framing and annotation change between slides.

## Learnings

- One animation can support step-based narration when each slide changes the framing or emphasis instead of changing the underlying motion language.
- A shared transparent video works better than duplicating similar assets when the point of the spike is continuity.
- A white poster is still useful for review because it makes the composition readable before the video finishes loading.
- Local Slidev asset imports should stay simple and slide-scoped so the spike remains robust.
