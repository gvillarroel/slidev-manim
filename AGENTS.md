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
- Reuse the canonical slide and video visual system defined in `.specs/adr/0002-slide-and-video-color-system.md`.

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
- Use the scene pacing decision in `.specs/adr/0003-scene-duration-and-pacing.md` for Manim videos intended for slide integration.

## Visual System

- Use the canonical project palette and typography system for Slidev slides and Manim videos unless a spike is intentionally testing a different style direction.
- Do not use source-system prefixes in project artifacts when referring to colors, typography, or iconography.
- Treat `primary-red`, `primary-orange`, `primary-yellow`, `primary-green`, `primary-blue`, and `primary-purple` as the default solid background palette for slides, panels, and video composition blocks.
- When those primary colors are used as backgrounds, use white text by default.
- When taking screenshots to review slide progress, use a white review background by default unless the spike is explicitly validating a different slide background.

## Scene Pacing

- Manim scenes intended for Slidev integration should be at least 25 seconds long unless a shorter micro-loop or bumper is explicitly documented.
- Give each scene 2 to 3 seconds of breathing room after the initial meaningful composition appears.
- Hold the resolved final state for 5 to 7 seconds so the slide has time to land.
- Do not spend the opening breath on a blank transparent frame; show the initial structure first, then let it breathe.

## Video Iteration Review

- After each meaningful video iteration, render or reference the latest output and show it in the chat with a Markdown media embed.
- Use the absolute filesystem path in the Markdown media embed so the Codex desktop app can display the video inline.
- Include the key validation result next to the embed, such as duration, frame count, transparency, or review-frame checks when relevant.

## Skills Strategy

- Reuse and adapt relevant skills from the external `manim_skill` repository when they are useful for this workflow.
- Evolve those skills so they work well for the specific needs of Slidev + Manim authoring.
- Prioritize skills and workflows that improve authoring, rendering, composition, transparent-video integration, and slide-oriented animation patterns.

## Skill evolution
Ensure when you learned something new that can improve quiality of the output check .agents/skills/gjv1-manim, if the skill doesn't have what you have learned, include it as a new reference or an aumentation of an existing element.

## External References

- Manim skill repository: <https://github.com/adithya-s-k/manim_skill/tree/main/skills>
- Manim Community: <https://github.com/manimCommunity/manim>
- Slidev: <https://github.com/slidevjs/slidev>
