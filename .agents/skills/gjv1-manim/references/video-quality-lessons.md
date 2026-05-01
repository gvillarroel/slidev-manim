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
- In sequential negative-space transfers, retire each completed route scaffold as soon as its handoff lands. Keeping all route lines until the global cleanup can turn later proof frames into a residue field instead of quiet space.
- Use the default visual system first: white background, black text, gray structure, and primary red as the active accent. Reach for orange, yellow, green, blue, or purple only when the user asks for color or when extra categories need explicit separation.
- Square corners and straight rectangular edges are the default. Rounded forms should be an explicit style choice, not the baseline.
- Text should try `Open Sans` first, with Arial or the system sans-serif as fallback.
- Transparent clips with labels, diagram text, timeline cards, or captioned arrows need a local `page-background` stage so they remain inspectable outside a slide.
- Decorative transparent loops can stay transparent when the slide surface supplies contrast and the clip has no labels or diagram text.
- Contact sheets are useful for broad passes, but suspicious thumbnails must be opened full size before patching.
- Camera-focus passes should hide or fully contextualize neighboring panels. Cropped fragments at the frame edge read as accidental unless they clearly remain context.
- Low edge clearance, off-center rest content, and low visual margins are composition problems even when no object is technically clipped.
- For imported SVGs, transform only compatible roles directly. Remove deleted roles first, establish the new primary body, then attach native Manim labels when text must stay readable.
- For generated diagram SVGs, keep inspectable source artifacts in the spike output, but animate stable role fragments and prefer native Manim connectors when imported arrowheads render too heavy.
- For generated diagram remaps, use specific receiver slots instead of one broad destination box, then remove those slots before any route pulse or resolved hold. Slot outlines that remain around docked nodes read as actor-to-outline crowding.
- In graph-style diagram videos, strict crowding audits can flag intentional connector-to-node proximity or pulse-on-route contact. Inspect overlays full size and treat the finding as blocking only when the contact hides an actor, collides with an outline after the causal beat, or muddies the mechanism.
- Slot-docking scenes need a held constrained proof frame with the dominant form inside an open receiver and the support forms outside the entrance. Hollow receivers can trigger strict crowding false positives because their bounding box surrounds the actor, so inspect overlays full size before deciding whether the slot is a real collision.
- Sequence handoffs need receiver cues before arrival, activation bars or route evidence during ownership, and a terminal artifact so the final hold has a center of interest.
- Long sequence routes need compact route-label chips; return paths should use a visibly different grammar from request paths.
- Bridge-span scenes should hold a proof frame where the dominant form is inside the passage while bridge rails remain visible above and below it. If source cleanup removes the left zone, recenter the target stage and resolved cluster before the final hold.
- Arc handoffs need one proof frame where the dominant form is visibly riding the curved path while supports stay calmer. If cleanup removes the source zone, recenter the resolved cluster so the final hold does not remain stranded in the old target lane.
- Table and formula scenes should identify source cells in place, compose the formula in a stable side zone, and transform the computed result into the destination cell.
- Continuation scenes should preserve the previous resolved state as a compact input, reveal destination scaffolds early enough to balance the frame, and populate output blocks progressively.
- Placeholder scaffolds should be removed or faded before text-bearing blocks appear. Do not morph placeholder panels directly into titles or list rows.
- Compression, squeeze, clamp, and throat-gate scenes need a visibly tighter constrained phase than both source and landing states.
- Clamp-close scenes should hold the pressure proof before the release, then remove abandoned source panels and clamp bars before morphing into the landing. If the clamp remains during the release, 0.3-second samples can read as support residue instead of resolved motion.
- Aperture and reveal scenes should not leave the destination stranded after the source zone disappears. Recenter or rebalance the destination stage during cleanup, and carry the active accent into the landing or remove it with the guide.
- Mask-transfer scenes should retire the source row, route lines, destination slots, mask band, and traveling accent before the compact landing morph. Faded source actors or an accent left inside the destination cluster can pass broad composition checks while failing strict actor-to-actor clearance.
- Orbit, fan-out, and fork scenes need enough spacing in proof frames to avoid reading as collisions or loose regrouping.
- Snap recoil scenes need the destination slot or pressure surface visible before the snap, a held stretched overshoot proof frame, and early removal of target slots before support forms settle. Keep the wall far enough from supports to clear targeted crowding checks, then recenter the resolved stage after source cleanup.
- Edge-tension scenes read best when the destination edge exists as a temporary pressure surface before arrival, the overshoot is held against it in a proof frame, and abandoned source panels disappear before the final hold.
- Axis-drop cues should keep the causal drop vertical, hold it, remove it, and only then move the point along any later rail.
- Bumper deflect scenes read cleaner when the leader owns a held compression frame, supports move into separate release lanes before the final morph, and passive destination slots disappear before the landing.
- Cradle catch scenes need a held proof frame where lower support pads visibly receive the dominant form. After that proof, separate support dots downward and outward and remove cradle/backing scaffolds so the resolved hold keeps clear actor-to-actor spacing.
- Magnet capture scenes should show a prepared receiver during the opening breath, hold the leader compressed inside the pocket before supports move, retire target slots and field rails immediately after their causal beat, and fade the receiver/core before the landing morph. If a bracket receiver is audited strictly, separated strokes or clear corner gaps prevent one U-shaped guide from becoming a false overlap box.
- When a reviewer names a timestamp, validate that exact timestamp and the surrounding transition frames in the promoted video.
- Poster images must be updated when the terminal video state changes.
- When target slots or receiver outlines must stay hollow, set stroke opacity directly instead of applying group opacity. Group opacity can turn stroke-only placeholders into filled disks and make the opening breath look like unresolved actors.
- Decorative backing strips and review frames still count as rest-state composition objects. If a resting audit flags low edge clearance on neutral structure, shrink the structure or widen the camera before accepting the hold.

## Maintenance Rule

Before any future addition is considered complete, run:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/self-containment-audit.py
```

Fix every finding. If useful guidance came from outside this skill, copy or summarize the durable part here first and link only to skill-local files.
