---
title: Manim Callout Reveal Lab
status: draft
date: 2026-05-01
---

# Purpose

Test which Manim indication and text-reveal features are useful for narration when a slide needs to direct attention to one changing object.

# Hypothesis

If the receiver is cued before the attention animation lands, `Circumscribe`, `Indicate`, `Flash`, `FocusOn`, `Broadcast`, and `Write` read as narrative handoffs instead of decorative effects.

# Run

```bash
uv run --script spikes/manim-callout-reveal-lab/main.py
```

# Output

The render writes:

- `videos/manim-callout-reveal-lab/manim-callout-reveal-lab.webm`
- `videos/manim-callout-reveal-lab/manim-callout-reveal-lab.png`
