# Circle Left To Right

## Purpose

This spike validates the minimum Manim rendering workflow for this repository:

- execute a spike through `uv`,
- render into the repository-level `videos/` directory,
- produce an animation suitable for later Slidev integration,
- keep the example simple enough to serve as a baseline for future spikes.

The scene renders a single circle and moves it from left to right.

## Run

From the repository root, run:

```bash
uv run --script spikes/circle-left-to-right/main.py
```

This command renders the scene into:

```text
videos/circle-left-to-right/
```

The primary artifact is written as:

```text
videos/circle-left-to-right/circle-left-to-right.webm
```

## Notes

- The script defaults to a transparent WebM render so the output is aligned with Slidev overlay use cases.
- Pass `--preview` if you want Manim to open the rendered video after completion.

## Slidev Demo

This spike also includes a local Slidev deck at:

```text
spikes/circle-left-to-right/slides.md
```

To run it from the repository root:

```bash
npx @slidev/cli spikes/circle-left-to-right/slides.md
```

To build it from the repository root:

```bash
npx @slidev/cli build spikes/circle-left-to-right/slides.md
```

If you already installed project dependencies, you can also use:

```bash
npm run dev:circle-left-to-right
```

and:

```bash
npm run build:circle-left-to-right
```
