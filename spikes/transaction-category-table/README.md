---
title: Transaction Category Table
status: draft
date: 2026-04-29
---

# Purpose

Show a two-column transaction table where each row category is derived from a keyword inside the original transaction description.

# Hypothesis

If the matched text inside each transaction pulses before the category lands in the second column, the viewer should read the category as extracted from the source description rather than as a manually filled label.

# Dataset Transformation

The spike simulates transaction descriptions and applies ordered keyword rules:

| Matched text | Category |
| --- | --- |
| `SUPERMARKET` | Groceries |
| `PAYROLL` | Income |
| `UBER` | Transport |
| `NETFLIX.COM` | Entertainment |
| `PHARMACY` | Health |

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-blue` for the transaction-description column
- `primary-purple` for the category column
- `primary-orange` for matched source text and the extraction badge
- `primary-yellow` for the active row cue and transient category handoff
- `highlight-purple`, `gray-*`, `white`, and `page-background` for table structure

# Run

```bash
uv run --script spikes/transaction-category-table/main.py
```

# Output

The render writes:

- `videos/transaction-category-table/transaction-category-table.webm`
- `videos/transaction-category-table/transaction-category-table.png`

The video render uses the canonical `page-background` stage so the table remains inspectable in Slidev and in standalone review.
