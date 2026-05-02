---
title: Quality Staged Convergence
status: draft
date: 2026-04-15
---

# Purpose

Test whether convergence through a visible staging lane feels more intentional than having all elements collapse directly into one cluster.

# Hypothesis

If the forms first align into a narrow shared lane and only then converge into the final cluster, the motion should feel more choreographed than a direct collapse.

# Current Result

The promoted render is a 25.6-second transparent WebM with a visible opening scaffold, a held compressed-lane proof, cleanup of transient slots and rails, and an 8.1-second centered final hold.

# Run

```bash
uv run --script spikes/quality-staged-convergence/main.py
```

# Output

The render writes:

- `videos/quality-staged-convergence/quality-staged-convergence.webm`
- `videos/quality-staged-convergence/quality-staged-convergence.png`
