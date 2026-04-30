---
title: SVG Subelement Transform
status: draft
date: 2026-04-29
---

# SVG Subelement Transform

## Purpose

Test a repeatable way to treat an SVG as a semantic set of components instead of as one opaque imported shape.

The spike uses three SVG stages:

- `assets/source.svg` has `body`, `slot`, `accent`, and `delete_badge` groups.
- `assets/middle.svg` keeps the shared groups after the delete-only group is removed.
- `assets/target.svg` remaps the remaining shared groups into a new symbol.

The render first removes the `delete_badge` subelement, then transforms the surviving SVG groups through the middle SVG and into the target SVG.

After frame-by-frame review, the `body` role intentionally does not use a direct geometric morph for the final stage. The source and middle bodies are filled rounded rectangles, while the target body is an open stroked path. Direct `ReplacementTransform` and `FadeTransform` attempts produced ambiguous intermediate geometry, so the final version uses a short sequential `FadeOut` of the middle body and `Create` of the target body. The compatible `slot` and `accent` roles move only after the target body exists.

## Hypothesis

If SVG groups are extracted and animated by stable semantic ids, a deletion plus a chained SVG-to-SVG transform should read more clearly than morphing the whole SVG at once.

## Run

From the repository root:

```bash
uv run --script spikes/svg-subelement-transform/main.py
```

## Output

The render writes:

- `videos/svg-subelement-transform/svg-subelement-transform.webm`
- `videos/svg-subelement-transform/svg-subelement-transform.png`

Generated fragment SVGs are written under `videos/svg-subelement-transform/.generated/` and are not intended for version control.

Frame review sheets are generated during validation at:

- `videos/svg-subelement-transform/review-every-second/contact-sheet-1.png`
- `videos/svg-subelement-transform/review-every-second/contact-sheet-2.png`
- `videos/svg-subelement-transform/review-half-second/contact-sheet-1.png`
- `videos/svg-subelement-transform/review-half-second/contact-sheet-2.png`
- `videos/svg-subelement-transform/review-half-second/contact-sheet-3.png`
- `videos/svg-subelement-transform/review-half-second/contact-sheet-4.png`
