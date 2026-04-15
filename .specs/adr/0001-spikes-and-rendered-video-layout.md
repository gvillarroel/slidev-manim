---
id: ADR-0001
title: Spikes and rendered video layout
status: accepted
date: 2026-04-14
---

# Context

This repository is focused on experimenting with Slidev and Manim together. The project needs a repeatable way to:

- keep exploratory source code organized,
- render animation assets for slide integration,
- avoid committing generated video artifacts,
- make each experiment independently understandable and executable.

# Decision

We will organize experiments and rendered outputs with the following structure:

- `spikes/` stores the source code for experiments.
- Each experiment lives in its own subdirectory under `spikes/`.
- Every spike directory must include a `README.md`.
- Any Slidev deck associated with a spike must be stored inside that spike directory.
- Every spike directory may include multiple Python files, but it must provide a primary executable entrypoint named `main.py`.
- `main.py` must be runnable with `uv` and define its dependencies inline in script metadata.
- `videos/` stores rendered outputs and is ignored by git.
- Each spike renders into `videos/<spike-name>/`, where `<spike-name>` matches the name of the corresponding folder under `spikes/`.
- Each spike `README.md` must document the command used to render its video output into the matching `videos/` subfolder.

# Consequences

- Generated artifacts stay out of version control.
- Each experiment can be executed in isolation without requiring a project-wide Python environment definition.
- The repository gains a predictable convention for moving from exploratory code to rendered assets that can later be embedded in Slidev slides.
- Spike-level documentation becomes mandatory, which should reduce ambiguity as new experiments are added.
