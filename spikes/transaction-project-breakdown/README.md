---
title: Transaction Project Breakdown
status: draft
date: 2026-04-30
---

# Purpose

Continue the transaction-category table spike from its resolved final state and transform that resolved table into two project backlog blocks.

# Hypothesis

If the resolved table stays visible as a compact input while two project blocks appear progressively, the viewer should read the task lists as generated from the classified transactions rather than as unrelated planning cards.

# Continuation

The opening frame recreates the final state from `transaction-category-table`:

- a two-column transaction/category table,
- highlighted source keywords inside the original descriptions,
- filled category cells,
- a purple outline around the resolved category column.

The scene then compacts that table into a left input panel and branches it into two right-side project blocks:

| Project | Tasks |
| --- | --- |
| Classifier Project | clean bank text, expand keyword rules, score uncertain rows, export category dataset |
| Needs Plan Project | group needs by category, rank weekly priorities, convert gaps to tasks, track completed actions |

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-blue` for the classifier project header,
- `primary-purple` for the needs-plan project header and resolved category column,
- `primary-orange` for branching guide geometry,
- `primary-yellow` and `primary-green` for task row dots and pulses,
- `gray-*`, `white`, and `page-background` for structure and readable local staging.

# Run

```bash
uv run --script spikes/transaction-project-breakdown/main.py
```

# Output

The render writes:

- `videos/transaction-project-breakdown/transaction-project-breakdown.webm`
- `videos/transaction-project-breakdown/transaction-project-breakdown.png`

The scene is at least 25 seconds long and includes a long final hold for slide integration.
