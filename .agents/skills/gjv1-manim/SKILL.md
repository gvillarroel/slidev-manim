---
name: gjv1-manim
description: |
  Use when creating or refining Manim videos in this repository where the goal is higher visual quality, minimal text, and narration-ready motion language.

  This skill turns a vague video idea into a hypothesis-driven quality pass: define the missing experiment, render, extract frames, critique composition, iterate, and keep only the versions that still look intentional without explanatory text.
---

# Purpose

Use this skill when the goal is not merely to make a Manim video that works, but to make one that looks deliberate, sparse, and ready for narration later.

# Core Rule

The video should explain itself through shape, color, timing, compression, and reveal logic first. Text is a last resort.

# Data and Formula Scenes

Use `side formula handoff` for table transformations where two or more source cells create a derived value.

- Establish source values with cell pulses, row cursors, or color-coded table roles before showing the formula.
- Do not put abstract markers directly on top of source numbers when the lesson depends on those exact values.
- Avoid enlarged moving copies over original cell text; they create double text, baseline mismatch, and unreadable overlaps.
- Give the formula its own side zone when the active table row is dense. Badges over headers or cells tend to occlude the data they are meant to explain.
- Keep formulas as composed, aligned text when every still frame must be readable. Reserve transforms for the computed result leaving the formula and landing in the destination cell.
- Use a high-contrast local background for floating formulas, usually white with a restrained primary-color border.
- Make the result-to-cell moment a handoff, not a duplicate overlay. `ReplacementTransform` from transient result text into final table text is usually clearer than adding both.
- Keep row indicators subordinate: a left marker plus a thin bottom rule usually reads better than a filled highlight band.
- For text-derived classifications, preserve the full source string with inline markup when highlighting matched text. Splitting a transaction description into separate text chunks can remove visible spaces, and direct character slicing can drift when rendered glyph submobjects do not map to the source string.
- If a side badge, formula panel, or temporary guide balances the table during the mechanism, also sample the final frame after that support disappears. Recenter or rebalance the resolved table if the no-support hold becomes left- or right-heavy.
- For title bands that include both title and subtitle, build the backing panel from the measured title/subtitle group height plus padding. Fixed-height title panels can leave the subtitle outside the local background after font or spacing changes.
- For side badges, build the backing box from the measured terms plus generous horizontal padding. If the result must travel back into the table, fade or remove the source-side terms first so the traveling result does not cross over still-visible text.

## Grid Discipline For Side Mechanisms

- Treat side badges as a separate aligned column, not as objects positioned from each active cell.
- Give every badge the same centerline and width as the top rule badge so row-level mechanisms keep a grid-like rhythm.
- Reserve a visible gutter between the table and the side column. Long labels should shrink inside the side column before they drift onto a destination column.
- When a user reports that a badge or callout feels misplaced, compare it against the nearest row, column, and sibling badge. The fix is usually alignment to an explicit grid, not another local offset.

# Working Style

- Work from one explicit hypothesis at a time.
- Keep text near zero.
- Prefer native Manim geometry over imported SVG fragments when visual quality matters.
- Review real sampled frames before declaring the result good.
- For transforms with disappearing, remapped, or imported components, review at 0.5 second intervals before accepting the motion.
- Inspect suspicious contact-sheet frames at full size before deciding they are artifacts.
- If a human calls out a bad timestamp, extract that exact frame at full size and treat it as stronger evidence than the surrounding contact sheet.
- If a callout is about an existing rendered video, patch and rerender the video itself; skill updates are not a substitute for fixing the artifact.
- For camera moves, dense SVG imports, large panels, or overlapping clusters, run the automated frame composition audit before saying there are no crop or overlap problems.
- For continuation scenes that introduce a second column later, reveal visible destination scaffolds early enough that the setup frame still balances before the lists or detailed content appear.
- Keep only the experiments whose still frames remain intentional without narration.
- Respect the project pacing floor: at least 25 seconds for slide-integration scenes, with 2 to 3 seconds of visible opening breath and 5 to 7 seconds of final hold unless a shorter micro-loop is explicitly documented.

# Canonical Sources

- Reuse the accumulated patterns in [C:\Users\villa\dev\slidev-manim\.specs\knowledge\gjv1-manim-video-quality.md](C:/Users/villa/dev/slidev-manim/.specs/knowledge/gjv1-manim-video-quality.md).
- Update that knowledge note after each useful experiment. Do not let the skill drift away from the note.

# Bundled Resources

Load only the resource needed for the current task:

- For preferred color styles and exact Manim token names, read [references/preferred-color-styles.md](references/preferred-color-styles.md).
- For palette, local stage, and transparency decisions, read [references/palette-stage-and-transparency.md](references/palette-stage-and-transparency.md).
- For choosing proof frames and patching a specific motion family, read [references/proof-frame-selection.md](references/proof-frame-selection.md).
- For continuing a resolved composition into two generated project blocks, read [references/continuation-project-breakdowns.md](references/continuation-project-breakdowns.md).
- For repo-wide video review, promoted-output counting, and contact sheets, read [references/repo-wide-video-audit.md](references/repo-wide-video-audit.md).
- For a copyable new spike shape, start from [examples/quality-spike-template.py](examples/quality-spike-template.py).
- For a reusable all-video contact sheet command, run or adapt [examples/contact-sheet-review.py](examples/contact-sheet-review.py).
- For a prioritized edge, center, and near-clipping candidate pass, run or adapt [examples/frame-safety-audit.py](examples/frame-safety-audit.py).
- For exact timestamp margin, side-fragment, and broad overlap/crowding checks, run [scripts/frame-composition-audit.py](scripts/frame-composition-audit.py).
- For strict actor-to-guide, actor-to-outline, or actor-to-actor clearance checks, run [scripts/frame-crowding-audit.py](scripts/frame-crowding-audit.py).
- For rest-state mobject edge clearance before a full render, run [scripts/resting-mobject-audit.py](scripts/resting-mobject-audit.py).
- For the transparent-loop versus local-stage decision, compare [examples/transparent-loop-vs-backed-clip.py](examples/transparent-loop-vs-backed-clip.py).
- For reusable output resources, copy from [assets/canonical-palette.json](assets/canonical-palette.json), [assets/review-frame-policy.json](assets/review-frame-policy.json), [assets/frame-safety-policy.json](assets/frame-safety-policy.json), or [assets/manim_scene_helpers.py](assets/manim_scene_helpers.py).

# Workflow

## 1. Choose the missing hypothesis

Do not start with “make it nicer.” Start with one concrete test.

Good examples:

- one leader should visibly compress before release,
- a receiver should visibly cause the landing,
- a split should read as one branching event,
- a reveal should depend on a sleeve, aperture, or mask,
- a support mechanism should still be readable in one still frame.

If the request is vague, rewrite it internally as:

`If <mechanism> is made more visible, the motion should feel more authored than <generic alternative>.`

## 2. Pick the motion family

Classify the experiment before coding. This determines what proof frame to sample and what failure mode to expect.

### Transfer and path families

- `arc handoff`
- `bridge span`
- `weave crossing`
- `relay handoff`
- `side formula handoff`
- `parallax transfer`
- `slot docking`

### Compression and release families

- `compression release`
- `corridor squeeze`
- `throat gate`
- `clamp close`
- `merge funnel`
- `ramp lift`

### Reveal and conceal families

- `mask transfer`
- `aperture open`
- `occlusion peel`
- `magnet capture`
- `sleeve reveal`

### Pivot and force families

- `hinge pivot`
- `counterlift balance`
- `bumper deflect`
- `sling release`
- `cradle catch`

### Arrangement and landing families

- `fan splay`
- `scale hierarchy`
- `negative space focus`
- `edge tension`
- `anchored orbit`
- `echo settle`
- `snap recoil`
- `staged convergence`
- `fork diverge`

If the experiment fits more than one family, choose the one whose mechanism must survive in a still frame.

## 3. Build the first pass

Follow these baseline rules:

- define colors with the preferred project tokens in [references/preferred-color-styles.md](references/preferred-color-styles.md), not default Manim color constants,
- use the project primary palette for structural roles:
  - green, blue, purple, red for actors or stages,
  - orange for paths, guides, funnels, sleeves, gates, or support geometry,
  - yellow for transient pulses, pivots, or attractor cores.
- prefer rounded geometry,
- use only subtle gray framing or shadows,
- keep one main moving element per beat,
- make the landing state simpler than the source state,
- keep support elements subordinate to the mechanism being tested.
- budget time before coding: opening breath, mechanism beats, and final hold should add up to at least 25 seconds for normal slide-integration scenes.

## 4. Render and extract proof frames

Always render the real video:

```bash
uv run --script spikes/<spike-name>/main.py
```

Then extract frames with `PyAV`:

```bash
@'
import av
from pathlib import Path

video = Path(r'C:\path\to\video.webm')
out_dir = video.parent / 'review-frames'
out_dir.mkdir(parents=True, exist_ok=True)

container = av.open(str(video))
stream = container.streams.video[0]
indices = [25, 90, 150]
current = 0
wanted = set(indices)

for frame in container.decode(stream):
    if current in wanted:
        frame.to_image().save(out_dir / f'frame-{current:03d}.png')
    current += 1
    if current > max(indices):
        break

container.close()
'@ | uv run --with av --with pillow -
```

Prefer a white background during review if you are debugging composition quality.

For many videos at once, use the bundled contact sheet example instead of rewriting the PyAV loop:

```bash
uv run --with av --with pillow .agents/skills/gjv1-manim/examples/contact-sheet-review.py --root .
```

For component remaps, imported SVGs, deletion beats, or any scene where something appears to flicker in the background, also extract a half-second review set. Keep the images on a white background and build contact sheets, but open suspicious frames full size before patching. One-second sampling can miss unsupported child roles, lingering guides, and ambiguous SVG morph states.

For camera framing, panel crops, dense SVG clusters, or possible overlaps, also run the automated composition audit:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --cadence 0.5 --write-overlays
```

For rest holds, run the scene-geometry audit before rerendering a long video. It skips animations, captures every `wait()`, and reports named mobjects whose bounds are outside the active camera frame or inside the safety margin:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/resting-mobject-audit.py --scene-file spikes/<spike-name>/main.py --scene-class <SceneClass> --out-dir videos/<spike-name>/resting-mobject-audit
```

Use `--check-pairs` only when sibling mobject collisions are the suspected failure; the default is edge clearance because panel children and imported SVG leaves often overlap by design.

Use exact timestamps when a review points to a specific second:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
```

If the exact timestamp looks visually cramped but the composition audit only reports `possible_overlap_or_crowding`, run the stricter crowding audit on that timestamp and its surrounding half-second range:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --start 12 --end 16 --cadence 0.5 --write-overlays
```

Treat `low_visual_margin` and `off_center_content` as blocking composition findings. Treat `stray_vertical_fragment` as a full-size review prompt by default because intentional panel edges and route guides can trigger it; rerun with `--strict-stray` when the overlay shows unsupported vertical residue. Treat `possible_overlap_or_crowding` as a full-size review prompt unless `--strict-notices` is appropriate for the scene. Treat `low_component_clearance` from the crowding audit as blocking when the pair is actor-to-guide, actor-to-outline, or actor-to-actor.

## 5. Sample the right proof moment

Do not default to the final frame. Sample the frame that proves the mechanism.

Use these defaults:

- `compression / squeeze / funnel / clamp / throat / ramp`:
  sample the constrained mid-state, not the released landing.
- `capture / docking / sleeve / aperture / mask / occlusion`:
  sample the frame where the mechanism is still visible around the leader.
- `fork / split / relay / handoff / bridge / weave / arc`:
  sample the transfer frame, not only the start or finish.
- `continuation / project breakdown`:
  sample the setup with destination scaffolds, first populated block, fork-with-second-block, and final hold. The final completed list alone does not prove that the blocks were generated from the prior state.
- `table / formula handoff`:
  sample the formula-composed frame and the result-handoff frame; the final completed table alone does not prove the calculation mechanism.
- `snap / recoil / edge tension / echo settle`:
  sample the stressed or overshoot frame first, then the resolved landing.
- `counterlift / hinge / bumper / sling / cradle`:
  sample the frame where the support mechanism is visibly causing the motion.

If the first still does not prove the mechanism, resample earlier or later. The wrong proof frame can invalidate a good experiment.

If a one-second proof sheet looks clean but the scene includes removal, remapping, or topological SVG changes, resample every 0.5 seconds around the transition. The useful failure frame is often between the obvious beats.

## 6. Critique aggressively

Check these first:

- too much dead space on one side,
- shapes colliding into unreadable clusters,
- rest-state mobject audit findings for `outside_frame`, `low_edge_clearance`, or `off_center_rest_content`,
- automated audit findings for low margins, residual side fragments, or overlap/crowding near the active timestamp,
- accent motion too small to matter,
- guide geometry overpowering the actors,
- target state busier than source state,
- mechanism present in code but not legible in a still,
- colors failing to establish hierarchy.

If the frame still feels like a static exported diagram, the composition is unfinished.

# Patch Guide

Patch in this order:

1. spacing
2. hierarchy
3. mechanism visibility
4. motion path
5. cleanup

Do not add text before exhausting those fixes.

## General fixes

- move the landing composition toward the center of interest,
- simplify the final frame,
- enlarge the accent pulse,
- reduce ghost opacity,
- shorten or lengthen guides,
- strengthen the active zone if the frame uses negative space,
- remove any device that remains after it has already explained the motion.
- if a guide is not still causing the motion, remove it instead of lowering opacity and letting it linger.
- remove phase scaffolds in the same cleanup beat as the mechanism they support. Dashed rails, setup guides, and source-zone hints can read as accidental residue if they survive into the next proof frame.
- for imported SVG remaps, do not assume `ReplacementTransform` is safe across incompatible geometry.

## Mechanism-specific fixes

### Path and transfer

- keep the path visible through the transfer, not only before it,
- separate leader and supports more decisively,
- preserve a readable entrance, bridge, slot, or crossing,
- split one path into explicit legs when the handoff must be staged.

### Table and formula handoff

- pulse source cells before composing the formula so the viewer knows what values are being used,
- keep the formula in a stable side zone when table density makes in-row animation hard to read,
- compose formula text into its final aligned layout instead of moving individual terms if intermediate frames must stay readable,
- avoid formula badges, row highlights, or transient values that sit on top of headers, source cells, or destination cells,
- transform the computed result into the destination cell instead of leaving temporary result text over final table text,
- use subtle row focus geometry instead of a filled highlight band when the table already has strong color roles,
- sample both the formula-ready frame and the result-landing frame before accepting the scene.

### Compression and pressure

- tighten the constrained phase more than feels necessary,
- narrow the neck, lane, throat, corridor, or clamp gap,
- sample an earlier proof frame if the release weakens the pressure,
- keep support forms away from the squeeze zone.

### Reveal and conceal

- keep the reveal device visible during the proof frame,
- narrow the leader mid-state so it feels contained,
- delay supports so the reveal or capture owns the beat,
- remove the device before the resolved landing.

### Support and force

- delay support motion until the leader reaches the mechanism,
- make beams tilt enough to read as load transfer,
- stretch the dominant form more when tension is the point,
- keep anchors, pivots, or bumpers visibly separate from the leader.

### Landing and arrangement

- make size contrast more obvious,
- increase angular spacing in fan layouts,
- push edge landings closer to the boundary if tension is the point,
- let the lead form arrive first when the scene depends on delayed settle,
- remove orbital or staging scaffolding before the final frame.

### Continuation and project breakdowns

- preserve the prior resolved composition as a compact input when it is the source for the next beat,
- put compact input labels in a small header band when a footer would crowd the shrunken source cluster,
- reveal output block scaffolds before detailed content so the setup frame is balanced,
- make scaffolds visible enough to survive review: pale panels are fine, but borders and header hints must not vanish,
- activate each large block before revealing its list rows,
- keep a balancing scaffold visible until the replacement block is visibly established; fading both through the same first sampled frame can create a one-frame off-center composition,
- do not `ReplacementTransform` placeholder scaffolds into text-bearing blocks. Fade or remove the scaffold, then fade in the real block so title text does not become unreadable mid-frame.
- reveal keypoints progressively with one row per beat,
- for short task-list rows, inspect full-size frames for collapsed word spacing. If `Text` or `MarkupText` makes spaces ambiguous, compose the label from per-word mobjects arranged with a fixed gap.
- keep the fork or branch geometry visible while each block becomes populated,
- update the poster composition to the new terminal state when the final hold changes.

### Imported SVG and component remaps

- keep transformable SVG roles in stable top-level groups such as `body`, `slot`, or `accent`,
- delete roles with no target separately before transforming surviving roles,
- use direct transforms only for roles with compatible geometry,
- treat closed filled shapes to open stroked paths as semantic handoffs, not geometric morphs,
- establish the new primary body before moving smaller child roles so they do not appear to float,
- use `FadeOut` plus `Create` for incompatible primary-body handoffs,
- inspect half-second transition frames full size before changing the code; thumbnails can make intentional child roles look like residue.

# Quality Checklist

Ship the video only if most of these are true:

- the video is at least 25 seconds long, or a shorter micro-loop exception is documented,
- the first meaningful composition gets a visible opening breath,
- the final resolved state holds long enough to read,
- the structure reads without labels,
- the palette is disciplined,
- one accent motion clearly carries the beat,
- the final frame feels resolved,
- sampled frames look intentional on their own,
- table or formula scenes keep terms aligned, high contrast, and clear of source and destination cells,
- the video would still make sense once narration is added later.

## Mechanism checklist

- if the scene uses negative space, the active zone is strong enough to justify it.
- if the scene uses a mask, aperture, sleeve, or capture pocket, the device is visible during the proof frame and absent in the final landing.
- if the scene uses rhythm markers, they pace the scene without becoming the main subject.
- if the scene uses counter-motion, each side keeps a distinct role.
- if the scene uses scale hierarchy, the size contrast is obvious at first glance.
- if the scene uses orbit motion, the anchor stays stable and the orbital scaffold disappears before the landing.
- if the scene uses compression or squeeze, the constrained phase is visibly tighter than both source and destination.
- if the scene uses edge tension, the dominant form creates pressure near the frame boundary without accidental clipping.
- if the scene uses occlusion, one layer clearly reveals another rather than simply covering it.
- if the scene uses hinge, latch, anchor, pivot, bumper, or sling logic, the mechanism is visible in at least one proof frame and gone by the landing.
- if the scene uses delayed settle, the lead form lands first and the echo is visible in still frames.
- if the scene uses a fan-out landing, the forms keep enough spacing and angle to read as one designed sweep.
- if the scene uses snap or recoil, the overshoot is large enough to survive a still frame.
- if the scene uses a bridge, slot, or receiver, the entrance or passage remains visible around the leader.
- if the scene uses a fork or split, the trunk remains visible long enough and the branches separate enough to avoid reading as a loose regroup.
- if the scene uses a funnel merge, multiple inputs are visibly compressed inside a narrowing neck before the dominant landing.
- if the scene uses a formula handoff, the formula is readable in its composed state and the result visibly replaces the destination value.

# Common Failure Patterns

When the first pass looks weak, it is usually because of one of these:

- the mechanism exists but is too subtle to survive a still frame,
- support forms move too early and steal the beat,
- the guide or device remains too long and contaminates the landing,
- the mid-state is not compressed, tilted, stretched, or separated enough,
- the final frame is busier than the mechanism frame,
- the chosen proof frame is wrong even though the motion itself is good.
- a guide was faded down but not removed, so it reads as accidental background residue.
- a direct SVG morph crosses incompatible topology and creates translucent plates, persistent strokes, or ambiguous in-between geometry.
- child roles move before the new body exists, making them appear unsupported even if the final frame is clean.
- contact-sheet thumbnails make small intentional child-role geometry look like source residue; inspect the frame at full size before patching.
- title groups, badges, chips, or callouts touch a panel boundary; reserve a clean header band or move the mechanism away from that label zone.
- camera-focus passes leave cropped neighboring panel fragments visible at the frame edge instead of hiding or fully contextualizing them.
- formula terms are animated separately and become unreadable in intermediate frames.
- calculation badges sit on top of table values, headers, or active row cues.
- transient result text overlaps the final destination text instead of transforming into it.

# Output Expectation

For each experiment:

1. create or update a spike,
2. render the video,
3. extract proof frames,
4. extract half-second frames for component remaps or any transition that might hide artifacts between one-second samples,
5. iterate at least once if the first pass is not clearly decent,
6. record what worked and what failed in `.specs/knowledge/`,
7. fold recurring lessons back into this skill instead of letting them accumulate only in the note.
