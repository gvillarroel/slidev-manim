# Compare Two Approaches

## Purpose

This spike tests a Slidev comparison slide where two related Manim assets sit side by side.

The goal is to learn whether the deck stays readable when:

- each approach has its own rendered video,
- both assets are imported locally through Vite,
- the slide uses simple, robust markup instead of a custom component stack.

## Run the Manim render

From the repository root, run:

```bash
uv run --script spikes/compare-two-approaches/main.py
```

This renders the spike assets into:

```text
videos/compare-two-approaches/
```

Expected outputs:

```text
videos/compare-two-approaches/compare-two-approaches-approach-a.webm
videos/compare-two-approaches/compare-two-approaches-approach-a.png
videos/compare-two-approaches/compare-two-approaches-approach-b.webm
videos/compare-two-approaches/compare-two-approaches-approach-b.png
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/compare-two-approaches/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/compare-two-approaches/slides.md
```

## Working Notes

- The live deck uses Vite imports for both videos and posters.
- Transparent WebM is the delivery format for the slide, while white PNG posters help with review and screenshot validation.
- A comparison slide works best when each panel owns its own readiness state and keeps the markup minimal.

## Learnings

- Two related Manim assets are enough to test a comparison layout without making the slide code fragile.
- Side-by-side panels should be sized independently so the comparison stays balanced even if the videos have slightly different visual density.
- Keeping the deck local to the spike avoids mixing this experiment with other Slidev tests.
