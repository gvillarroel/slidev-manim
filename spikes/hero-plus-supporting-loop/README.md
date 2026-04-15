# Hero Plus Supporting Loop

## Purpose

This spike tests a Slidev composition where one Manim asset owns the slide and a second, smaller looping asset reinforces the same idea without competing with the hero.

The goal is to validate:

- a dominant transparent hero video,
- a secondary looping support video,
- a slide layout that keeps the hero visually primary while the support asset stays subordinate.

## Run the render

From the repository root:

```bash
uv run --script spikes/hero-plus-supporting-loop/main.py
```

This renders the spike output into:

```text
videos/hero-plus-supporting-loop/
```

Expected outputs:

```text
videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.webm
videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.png
videos/hero-plus-supporting-loop/hero-plus-supporting-loop-support.webm
videos/hero-plus-supporting-loop/hero-plus-supporting-loop-support.png
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/hero-plus-supporting-loop/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/hero-plus-supporting-loop/slides.md
```

## Notes

- The hero asset is the dominant visual and uses a wide framing.
- The support asset is smaller and loops cleanly so it can behave like an accent or reinforcement element.
- White PNG posters are included for review and fallback rendering.
- Keep the Slidev imports local to this spike so the experiment remains self-contained.

## Learnings

- A hero plus support pattern works best when the support asset is simpler and smaller than the main animation.
- The support loop should be designed as a repeating accent, not a second headline.
- Separate render outputs are useful when the hero and the support asset need different framing or aspect ratios.
- Poster PNGs remain useful for review because they make the composition readable even when the video frame is not visible immediately.
- Keeping the poster visible behind the transparent video is a practical review fallback when headless Chromium does not paint the video frame.
- Putting the support loop in an absolute overlay keeps the hierarchy intact and prevents the secondary animation from being pushed out of view.
