# Video Quality Lessons

This is the skill-local accumulation point for durable GJV1 Manim quality lessons. If an experiment produces guidance that should affect future videos, fold it into this file or into `SKILL.md` so the skill remains usable without outside notes.

## Stable Process

1. State the missing visual hypothesis before coding.
2. Budget the opening breath, mechanism beats, and final hold before rendering.
3. Build with minimal text, strict palette roles, and one dominant motion idea per beat.
4. Render the real video, then inspect proof frames that show the mechanism.
5. Run composition, crowding, or resting-mobject audits when framing or overlap is a risk.
6. Patch spacing, hierarchy, mechanism visibility, motion path, and cleanup in that order.
7. Keep only versions whose still frames look intentional without narration.

## Durable Lessons

- A mechanism must survive in a still frame. If the sampled proof frame does not show the cause of the motion, resample or strengthen the mechanism.
- The opening breath should show the initial structure first; do not spend it on a blank transparent frame.
- Final holds are part of the composition. Remove guides, slots, sleeves, shutters, or scaffolds once they stop causing the motion.
- Use the primary palette semantically: green, blue, purple, and red for actors or states; orange for causal routes and mechanisms; yellow for transient attention.
- Transparent clips with labels, diagram text, timeline cards, or captioned arrows need a local `page-background` stage so they remain inspectable outside a slide.
- Decorative transparent loops can stay transparent when the slide surface supplies contrast and the clip has no labels or diagram text.
- Contact sheets are useful for broad passes, but suspicious thumbnails must be opened full size before patching.
- Camera-focus passes should hide or fully contextualize neighboring panels. Cropped fragments at the frame edge read as accidental unless they clearly remain context.
- Low edge clearance, off-center rest content, and low visual margins are composition problems even when no object is technically clipped.
- For imported SVGs, transform only compatible roles directly. Remove deleted roles first, establish the new primary body, then attach native Manim labels when text must stay readable.
- For generated diagram SVGs, keep inspectable source artifacts in the spike output, but animate stable role fragments and prefer native Manim connectors when imported arrowheads render too heavy.
- Sequence handoffs need receiver cues before arrival, activation bars or route evidence during ownership, and a terminal artifact so the final hold has a center of interest.
- Long sequence routes need compact route-label chips; return paths should use a visibly different grammar from request paths.
- Table and formula scenes should identify source cells in place, compose the formula in a stable side zone, and transform the computed result into the destination cell.
- Continuation scenes should preserve the previous resolved state as a compact input, reveal destination scaffolds early enough to balance the frame, and populate output blocks progressively.
- Placeholder scaffolds should be removed or faded before text-bearing blocks appear. Do not morph placeholder panels directly into titles or list rows.
- Compression, squeeze, clamp, and throat-gate scenes need a visibly tighter constrained phase than both source and landing states.
- Orbit, fan-out, and fork scenes need enough spacing in proof frames to avoid reading as collisions or loose regrouping.
- Axis-drop cues should keep the causal drop vertical, hold it, remove it, and only then move the point along any later rail.
- When a reviewer names a timestamp, validate that exact timestamp and the surrounding transition frames in the promoted video.
- Poster images must be updated when the terminal video state changes.

## Maintenance Rule

Before any future addition is considered complete, run:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/self-containment-audit.py
```

Fix every finding. If useful guidance came from outside this skill, copy or summarize the durable part here first and link only to skill-local files.
