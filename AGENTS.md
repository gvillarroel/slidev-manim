# AGENTS.md

## Language

- Always write in English for code, documentation, issues, architecture notes, commit messages, and agent-generated project artifacts.

## Project Management Files

- Use `.specs/` as the canonical location for project management and project-definition files.
- Store requirement and planning documents under `.specs/`.
- Store issues as Markdown files under `.specs/issues/*.md`.
- Store architecture decision records under `.specs/adr/*.md`.
- Store concise reusable implementation and validation notes under `.specs/knowledge/*.md`.
- All documents in `.specs/` must be written in Markdown and include frontmatter.
- Reuse validated workflows recorded in `.specs/knowledge/` before inventing a new local process for the same task.

## Repository Layout

- Keep rendered experiment outputs in `videos/`.
- The `videos/` directory must be ignored by git.
- Store source code for experiments under `spikes/`.
- Each spike must live in its own subdirectory under `spikes/`.
- Each spike directory must have a matching output subdirectory under `videos/` that uses the same spike folder name.
- Each spike directory must include a `README.md` that explains the purpose of the experiment.
- Any Slidev presentation documents for a spike must live inside that spike directory and must not be stored at the repository root.
- Each spike directory may contain one or more Python scripts, but it must expose a primary executable script named `main.py`.
- The primary `main.py` entrypoint must be executable with `uv` and must declare its dependencies inline in the script metadata.
- Each spike `README.md` must document exactly how to execute `main.py` so the rendered video is generated in the corresponding `videos/<spike-name>/` directory.

## Project Goal

- This project exists to experiment with combining Slidev and Manim.
- The main goal is to generate presentations where slides can include Manim-rendered videos with transparent backgrounds.
- Those animations should help express ideas progressively inside each slide, instead of being treated as isolated standalone videos.

## Skills Strategy

- Reuse and adapt relevant skills from the external `manim_skill` repository when they are useful for this workflow.
- Evolve those skills so they work well for the specific needs of Slidev + Manim authoring.
- Prioritize skills and workflows that improve authoring, rendering, composition, transparent-video integration, and slide-oriented animation patterns.

## External References

- Manim skill repository: <https://github.com/adithya-s-k/manim_skill/tree/main/skills>
- Manim Community: <https://github.com/manimCommunity/manim>
- Slidev: <https://github.com/slidevjs/slidev>
