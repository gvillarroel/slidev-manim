# Step Reveal Sequence

## Purpose

This spike tests a narrative Slidev plus Manim pattern where several slides reuse related video assets to explain the same idea in stages.

The render set is intentionally small and coherent:

- `intro` establishes the motion and composition.
- `context` adds supporting explanation while keeping the same visual motif.
- `wrap` closes the sequence with the same movement and a stronger conclusion.

## Run the Manim spike

From the repository root:

```bash
uv run --script spikes/step-reveal-sequence/main.py
```

The generated assets are written to:

```text
videos/step-reveal-sequence/
```

Primary outputs:

```text
videos/step-reveal-sequence/step-reveal-sequence-intro.webm
videos/step-reveal-sequence/step-reveal-sequence-context.webm
videos/step-reveal-sequence/step-reveal-sequence-wrap.webm
```

White poster PNGs are also written alongside the videos for review.

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/step-reveal-sequence/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/step-reveal-sequence/slides.md
```

## Notes

- The real delivery asset is the transparent WebM output.
- The PNG posters are only for quick visual review and fallback rendering.
- Each slide imports its media locally so the spike stays self-contained.

## Learnings

- A narrative deck can stay coherent when each slide reuses the same visual motif with a different render stage.
- Transparent WebM is the delivery format for the slide, while white PNG posters are useful for review and fallback.
- Keeping the slide-local imports in `slides.md` avoids leaking spike-specific media references into the project root.
