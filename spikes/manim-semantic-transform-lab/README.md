---
title: Manim Semantic Transform Lab
status: draft
date: 2026-04-30
---

# Purpose

This spike tests narrative use of Manim semantic transforms from the official v0.20.1 transform docs:

- `Transform`
- `ReplacementTransform`
- `TransformFromCopy`
- `FadeTransform`
- `TransformMatchingShapes`
- `TransformMatchingTex`
- `MoveToTarget`

# Hypothesis

Semantic transforms narrate best when identity is preserved only where the viewer benefits from continuity. A visible handoff proof frame should carry ownership across the scene, while incompatible topology should fade and land instead of morphing into unreadable soup.

# Design

The scene uses one red identity marker and a sparse grayscale stage:

- `Transform` changes the marker shape while preserving the same narrative actor.
- `MoveToTarget` compacts the claim card into the next slot.
- `TransformFromCopy` creates a visible handoff proof frame while the original marker remains in place.
- `ReplacementTransform` promotes a transient proof into a new resolved object.
- `TransformMatchingShapes` reorders identical geometric parts.
- `TransformMatchingTex` preserves tex-like tokens through an additive formula change without requiring a local LaTeX installation.
- `FadeTransform` handles incompatible topology where a direct morph would become ambiguous.

# Run

```bash
uv run --script spikes/manim-semantic-transform-lab/main.py
```

# Output

The render writes:

- `videos/manim-semantic-transform-lab/manim-semantic-transform-lab.webm`
- `videos/manim-semantic-transform-lab/manim-semantic-transform-lab.png`

Review artifacts are expected under:

- `videos/manim-semantic-transform-lab/review-frames/`
