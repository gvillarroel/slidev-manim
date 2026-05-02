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

# Default Visual System

Use a restrained default look: white background, black text, gray structure, and primary red for the single active accent or warning. Borders should be straight and square by default, with no rounded corners unless a spike explicitly tests rounded geometry.

- Use `Open Sans` for Manim text when available; fall back to Arial or the system sans-serif if Open Sans is unavailable.
- Start with `WHITE`, `BLACK`, `GRAY`, `GRAY_*`, `PAGE_BACKGROUND`, and `PRIMARY_RED`.
- Use the rest of the palette only when the user asks for more color, when a spike explicitly tests color roles, or when extra categories cannot be understood with red plus grayscale.
- Prefer rectangular panels, square-corner cards, straight bars, rules, and crisp grid alignment.

# Self-Containment Contract

This skill must remain self-contained. `SKILL.md`, `references/`, `examples/`, `scripts/`, and `assets/` must not depend on project-management notes, repository-root documentation, absolute local paths, web URLs, external skill repositories, or any other source outside `.agents/skills/gjv1-manim`.

- Link only to files that live inside this skill directory.
- If external material informs an addition, copy or summarize the durable guidance into a skill-local file first, then link to that local file.
- Treat project files such as `spikes/...` and `videos/...` as workflow inputs or outputs, not as canonical skill references.
- Every future addition must pass the self-containment audit before the skill is considered updated:

```bash
uv run --script .agents/skills/gjv1-manim/scripts/self-containment-audit.py
```

# Sequence Diagram Scenes

Use `sequence handoff` for protocol or Mermaid sequence-diagram animations.

- Keep the `.mmd` source as the inspectable protocol definition even when the final video is rebuilt with native Manim geometry.
- Preserve Mermaid participant order unless the spike explicitly documents a semantic reorder.
- Use native Manim participant cards, lifelines, activation bars, and message routes when connector quality, timing, or labels need careful control.
- Treat every message as a receiver-caused handoff: show a target slot or receiver cue before the pulse arrives, then remove or soften that cue after it has explained the landing.
- For opening breaths with participants in a top band, add faint destination slots or route scaffolds below the cards. Otherwise pixel audits and human review can both read the opening as top-heavy unused space.
- Use compact route-label chips for long cross-lane messages. Bare labels on long arrows tend to disappear into lifelines or compete with the route.
- Make return paths visibly different from requests, usually red and dashed, while normal request routes stay black or gray. Use additional route colors only when the user asks for a colored protocol view.
- Give the resolved frame one terminal artifact, such as a token badge, so the final hold has a center of interest after the protocol mechanics finish.

# Comparison Panel Scenes

Use `side-by-side comparison asset` when a Slidev comparison page embeds two related Manim clips.

- Treat each side as a complete slide-integration scene, not as a short decorative loop. Budget a visible opening breath, a mechanism proof beat, cleanup, and a 5 to 7 second final hold.
- Make the difference between the two sides visible through mechanism grammar. For example, one side can use a direct transfer while the other uses a prepared receiver, guide path, halo, or other causal scaffold.
- Keep the title band outside the motion lane. If the actor crosses under the title, lower the stage or add a quiet divider so sampled frames do not read as text collision.
- Use restrained square stage geometry and gray structure by default; let the actor, active route, receiver cue, or terminal halo carry the comparison.
- Remove route scaffolds and empty source slots before the resolved hold, then recenter the final actor or cluster so the clip does not end stranded in an old transfer layout.
- Resting audits may report route-to-actor or route-to-slot notices for the guided side. Inspect the full-size frame and treat the notice as acceptable only when the route is visibly the track being followed and does not obscure the actor or receiver.

# Time Rail Scenes

Use `time rail` when a left-side timeline or spine should act as the narrator instead of a traveling red dot.

- Treat the rail as elapsed time: show the full pending spine, ticks, slots, or branches in the first frame, then let the active red segment grow through it.
- Avoid adding a separate guide dot when the rail itself can carry progression. The active segment, tick state, and destination slot should explain causality.
- Keep the left rail visually stable while content resolves to the right; the viewer should read the rail as an organizing timeline, not as a decorative divider.
- Branches should emit from the rail only after the active segment reaches the tick. Soften branch guides after their card lands so the final frame does not look mid-transition.
- Use a terminal rule or final rail state as the resolved artifact. Do not leave disconnected pulses at former tick or branch positions.
- To continue from agenda into content, keep the rail fixed, activate one tick, soften or remove future agenda items, and let the active card open into a detail panel. The first detailed beat should feel like the selected point now owns the stage, while the rail preserves orientation.
- Avoid secondary red connector lines, row-outline boxes, or terminal rules inside the detail panel. If the rail is the narrator, extra red lines away from it read as annotation artifacts; use quiet gray local cues for detail rows.

# Gantt Timeline Scenes

Use `native gantt timeline` when a generated Mermaid Gantt SVG becomes too dense, text-heavy, or visually static as fragment batches.

- Keep the `.mmd`, Mermaid SVG, and generated fragments as inspectable artifacts, but rebuild the video with native Manim day ticks, task slots, and square task bars when the chart itself is the mechanism.
- Show the full pending timeline scaffold during the opening breath: date ticks, lane label, and faint task slots should be visible before any bar grows.
- Use one primary-red cursor or dependency marker to prove the timeline handoff. Let bars grow from their real start date instead of fading in as detached rectangles.
- Avoid Mermaid's dense daily labels when they crowd the bottom axis. Use a few readable anchor dates and let grid columns carry intermediate days.
- Replace enclosing terminal rectangles with separated corner brackets or a clean hold. A full-width outline around a wide chart can read as a frame artifact and trigger false edge/crowding failures.
- For strict crowding audits, full-size review expected contacts between axis/grid lines and between labels and their own filled task bars. Treat them as blocking only if they obscure the mechanism or look accidental in the rendered frame.

# Packet Diagram Scenes

Use `native packet fields` when a compact Mermaid packet SVG becomes a thin strip, a title-heavy generic unfold, or a fragment fade that does not explain the byte layout.

- Keep the `.mmd`, generated SVG, and fragments as inspectable artifacts, but rebuild the promoted video with native Manim field rectangles when the packet itself is the mechanism.
- Show the full two-row or multi-field packet scaffold during the opening breath before any field fills.
- Grow each field body from its bit-range start while one primary-red cursor, scan line, or active outline proves progression.
- Keep range labels inset from field edges and add tiny gutters between adjacent colored field bodies so strict crowding review does not read packet boundaries as accidental contact.
- Remove title bands, visible stage plates, and closed terminal outlines unless they carry meaning. A clean page background with separated terminal brackets usually leaves the final hold calmer.

# Data and Formula Scenes

Use `side formula handoff` for table transformations where two or more source cells create a derived value.

- Treat a table-to-counter handoff as a promising transformation grammar: source values cue first, the side mechanism produces one result token, and the live counter changes only while that token is visibly in flight.
- Establish source values with cell pulses, row cursors, or color-coded table roles before showing the formula.
- Do not put abstract markers directly on top of source numbers when the lesson depends on those exact values.
- Avoid enlarged moving copies over original cell text; they create double text, baseline mismatch, and unreadable overlaps.
- Give the formula its own side zone when the active table row is dense. Badges over headers or cells tend to occlude the data they are meant to explain.
- Keep formulas as composed, aligned text when every still frame must be readable. Reserve transforms for the computed result leaving the formula and landing in the destination cell.
- Use a high-contrast local background for floating formulas, usually white with a restrained gray or primary-red border.
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
- When an opening beat reserves a destination zone before motion reaches it, add faint target slots or scaffolds so the breath does not read as unused blank space.
- Keep only the experiments whose still frames remain intentional without narration.
- Respect the project pacing floor: at least 25 seconds for slide-integration scenes, with 2 to 3 seconds of visible opening breath and 5 to 7 seconds of final hold unless a shorter micro-loop is explicitly documented.

# Pre-Finish Review Protocol

Do not say the video is finished just because the render succeeded or one audit passed. Treat finish as a review decision based on rendered evidence.

## Required review order

1. Watch or scrub the rendered video once for overall rhythm, continuity, and whether the main mechanism reads without explanation.
2. Inspect the chosen proof frame for each act or mechanism beat at full size, not only in a thumbnail contact sheet.
3. Inspect the resolved final hold at full size and confirm that guides, slots, rails, masks, shutters, scaffolds, and travel residue are gone or clearly subordinate.
4. Inspect the opening breath and confirm the first meaningful composition is already visible and balanced.
5. Inspect the highest-risk transition family at 0.5 second intervals. This is mandatory for remaps, imported SVGs, dense cleanups, and any beat a human flagged as abrupt or suspicious.
6. Run the relevant automated audits for the scene type before declaring there are no framing or overlap problems.
7. If the spike is browser-native or responsive, inspect at least one mobile proof frame or mobile screenshot before declaring the composition finished.

## What must be true before “done”

- The mechanism reads in motion and in still frames.
- The proof frames answer the causal question of the scene, not just that something moved.
- The final hold is calmer and simpler than the mechanism beat.
- No obvious residue, clipped fragments, off-center drift, or support-device leftovers remain in the reviewed frames.
- The rendered output matches the current source. If there was a patch, rerender and re-review the video itself.
- Automated audits and human review agree, or any disagreement has been checked at full size and explained.

## What is not enough

- A successful render by itself.
- One clean contact sheet without full-size frame review.
- One passing composition audit without checking the frames it sampled.
- A source-only code review of the animation logic.
- Saying a suspicious frame is “probably fine” without opening that exact frame full size.

# Skill-Local Sources

- Treat this file and the bundled resources below as the canonical source for the skill.
- Use [references/video-quality-lessons.md](references/video-quality-lessons.md) for durable lessons that should survive future experiments.
- Store reusable additions inside this skill directory, either in `SKILL.md`, `references/`, `examples/`, `scripts/`, or `assets/`.
- Do not leave required skill guidance only in project notes, repository docs, web pages, or another skill.

# Bundled Resources

Load only the resource needed for the current task:

- For preferred color styles and exact Manim token names, read [references/preferred-color-styles.md](references/preferred-color-styles.md).
- For programming-code snippets, Manim `Code` options, syntax-highlighting styles, and performance-safe code galleries, read [references/code-options-and-highlighting.md](references/code-options-and-highlighting.md).
- For timing beats, `Succession`, `LaggedStart`, `ChangeSpeed`, scene sections, and audio-free voiceover cue patterns, read [references/narration-timing-and-cues.md](references/narration-timing-and-cues.md).
- For semantic transforms, matching-parts handoffs, identity preservation, and avoiding morph soup, read [references/semantic-transform-narration.md](references/semantic-transform-narration.md).
- For callout, reveal, indication, broadcast, and text-attention patterns, read [references/callout-reveal-narration.md](references/callout-reveal-narration.md).
- For palette, local stage, and transparency decisions, read [references/palette-stage-and-transparency.md](references/palette-stage-and-transparency.md).
- For choosing proof frames and patching a specific motion family, read [references/proof-frame-selection.md](references/proof-frame-selection.md).
- For minimal five-act narratives driven by one lead actor, act-specific proof frames, and conflict-to-resolution cleanup, read [references/minimal-act-proof-frames.md](references/minimal-act-proof-frames.md).
- For nested camera tours where a red guide marker becomes a pinned pointer for a solid detail panel, read [references/red-guide-detail-tour.md](references/red-guide-detail-tour.md).
- For camera-led narration, destination scaffolds, zoom discipline, and final recentering, read [references/camera-focus-narration.md](references/camera-focus-narration.md).
- For table-derived values, counters, row cues, formula side zones, and chart synchronization, read [references/data-counter-narration.md](references/data-counter-narration.md).
- For graph route selection, path pulses, traces, subordinate alternatives, and flow cleanup, read [references/graph-flow-narration.md](references/graph-flow-narration.md).
- For `ThreeDScene`, depth reveals, surface/column evidence, and disciplined 3D camera motion, read [references/3d-depth-narration.md](references/3d-depth-narration.md).
- For choosing Manim `Table` options, helper methods, and table-scene patterns, read [references/table-options-and-usage.md](references/table-options-and-usage.md).
- For data handoffs that transform source values into a live counter, read [references/data-handoff-live-counter.md](references/data-handoff-live-counter.md).
- For Manim arrow scenes, `GrowArrow`, start/end anchors, curved routes, and connector label clarity, read [references/arrow-growth-and-connectors.md](references/arrow-growth-and-connectors.md).
- For continuing a resolved composition into two generated project blocks, read [references/continuation-project-breakdowns.md](references/continuation-project-breakdowns.md).
- For red-hub radial fan-out scenes where focus moves between branches, read [references/radial-fanout-focus.md](references/radial-fanout-focus.md).
- For repeatable non-standard connector styles such as `cellular sprout line`, `organic fractal line`, and `scale spine line`, read [references/motion-line-styles.md](references/motion-line-styles.md).
- For repo-wide video review, promoted-output counting, and contact sheets, read [references/repo-wide-video-audit.md](references/repo-wide-video-audit.md).
- For a copyable new spike shape, start from [examples/quality-spike-template.py](examples/quality-spike-template.py).
- For a copyable overlap-free treemap pattern, start from [examples/overlap-free-treemap-unfold.py](examples/overlap-free-treemap-unfold.py).
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
- `sequence handoff`
- `side formula handoff`
- `time rail`
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
- `axis drop`

### Procedural line styles

- `cellular sprout line`
- `organic fractal line`
- `scale spine line`

### Camera-led narrative families

- `red guide tour`

If the experiment fits more than one family, choose the one whose mechanism must survive in a still frame.

## 3. Build the first pass

Follow these baseline rules:

- define colors with the preferred project tokens in [references/preferred-color-styles.md](references/preferred-color-styles.md), not default Manim color constants,
- use the default red, black, and grayscale palette first:
  - black and dark gray for primary structure, labels, and stable actors,
  - middle grays for panels, scaffolds, inactive paths, guides, and shadows,
  - primary red for the active accent, selected path, warning, return route, or final pulse.
- use orange, yellow, green, blue, and purple only when more color is explicitly requested or a scene needs categorical color separation that cannot be solved with red plus grayscale,
- prefer square-corner rectangular geometry,
- use only subtle gray framing or shadows,
- keep one main moving element per beat,
- make the landing state simpler than the source state,
- keep support elements subordinate to the mechanism being tested.
- budget time before coding: opening breath, mechanism beats, and final hold should add up to at least 25 seconds for normal slide-integration scenes.
- for a `red guide tour`, use one primary-red companion marker as the viewer's guide through a large diagram. The marker should travel between distant zones, pause as the camera frames each stop, and sometimes trigger or participate in the local mechanism before moving on. If the tour needs a nested explanation, use [references/red-guide-detail-tour.md](references/red-guide-detail-tour.md) so the marker can become a pinned upper-left pointer before a solid detail panel opens.

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

video = Path('videos/<spike-name>/<video-name>.webm')
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
- `sequence handoff`:
  sample the opening with pending receiver slots, a long cross-lane request mid-transfer, a database query or return frame, and the final terminal artifact after transient slots disappear.
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
- when local backing panels animate, set their layer order below actors and pulses before rendering. Panel opacity or scale changes can otherwise wash over the final colored mobjects.
- for negative-space scenes, remove abandoned source containers before the resolved hold. A faded empty panel often reads as residue, while plain quiet space reads as intentional.
- remove any device that remains after it has already explained the motion.
- if a guide is not still causing the motion, remove it instead of lowering opacity and letting it linger.
- for sequential negative-space transfers, retire each completed route scaffold as soon as its handoff lands. Keeping all route lines visible until the global cleanup can make later proof frames look like residue instead of intentional quiet space.
- after fading individual route guides, remove the parent scaffold group instead of fading that parent later. A late parent `FadeOut` can visually reintroduce already-retired child routes during cleanup.
- after a source container disappears, recenter or rebalance the resolved destination cluster. Negative space should feel intentionally quiet, not like the active zone is stranded in the old transfer lane.
- remove phase scaffolds in the same cleanup beat as the mechanism they support. Dashed rails, setup guides, and source-zone hints can read as accidental residue if they survive into the next proof frame.
- for imported SVG remaps, do not assume `ReplacementTransform` is safe across incompatible geometry.

## Mechanism-specific fixes

### Path and transfer

- keep the path visible through the transfer, not only before it,
- separate leader and supports more decisively,
- preserve a readable entrance, bridge, slot, or crossing,
- split one path into explicit legs when the handoff must be staged.
- for relay handoffs, show receiver pads or faint route legs during the opening breath, hold the support-to-support proof before the dominant form moves, then remove relay scaffolds and recenter the final cluster after the source zone disappears.
- for relay handoffs, prefer separated bracket pads with real clearance around settled actors. Closed receiver rectangles can read as actor-to-outline crowding in strict proof-frame review.
- if a relay leg would cross under an arriving actor, shorten it into a freestanding gate or entrance cue between stages rather than drawing the route into the actor.
- fade the traveling baton before cleanup morphs, then use a perimeter pulse or halo for the terminal artifact so the final hold does not inherit a stray accent dot.
- for slot-docking scenes, hold one proof frame where the dominant form is visibly compressed inside an open receiver while support forms sit outside the entrance. Remove the slot before the resolved landing, and recenter the final stage if the source zone disappears.
- for bridge-span scenes, keep rails visible above and below the dominant form in the proof frame. Stop open rails before the receiver slot, keep the active guide separate from both the actor and rails, and avoid connected bridge ends that create one closed outline around the actor in strict crowding review. After removing the source zone, recenter the target stage and resolved cluster so the final hold does not stay in the old transfer layout.
- for arc handoffs, let the dominant form visibly ride the curve before support forms move. Use faint destination slots during the opening breath, then retire the source zone and recenter the resolved cluster after cleanup.
- for sequence diagrams, let the target receiver cue exist before the pulse arrives and fade that cue in the cleanup beat once the route or activation bar records the message.
- for long sequence arrows, keep route labels in compact chips and place them on a consistent side of the route so lifelines remain subordinate.
- for quadrant or axis-drop diagrams, keep the causal drop cue vertical when the concept is lower cost, risk, or effort; put any later horizontal repositioning in a separate rail or staged move.
- hold the drop cue, remove it, then move the point. If the arrow and point move together, the cue reads like a drag handle instead of a prior decision signal.

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
- for clamp-close scenes, hold the side-pressure proof before release, then remove abandoned source panels and clamp bars before the landing morph so the release frame does not inherit support residue,
- for throat-gate scenes that recenter after a source-to-target transfer, keep the broad balancing frame or scaffold through the recentering transition, then remove it at the final-hold boundary. Removing it before the cluster moves can make sampled cleanup frames read off-center, while fading it through the final cluster can create stray-frame fragments.
- full-size review any crowding finding in the constrained proof frame; actor-to-actor contact can be acceptable only when it reads as pressure, while actor-to-guide or actor-to-outline contact remains blocking,
- keep support forms away from the squeeze zone.

### Reveal and conceal

- keep the reveal device visible during the proof frame,
- for layered reveals, give each lane a visible aperture or slot and compress the active layer into that aperture before releasing it. A passive divider beside a direct transform reads as a route marker, not as the cause of the reveal.
- narrow the leader mid-state so it feels contained,
- delay supports so the reveal or capture owns the beat,
- remove the device before the resolved landing.
- if the source zone disappears after an aperture or reveal, recenter the destination stage during cleanup so the final hold does not feel stranded in leftover negative space.
- move or retire the active accent in the same beat as the landing. A small pulse left at the old aperture edge reads as residue once the guide disappears.
- for mask-transfer scenes, retire the source row, route lines, destination slots, mask band, and traveling accent before the compact landing morph. Faded source actors or an accent left inside the destination cluster can pass broad composition review but fail strict actor-to-actor clearance.
- Use faint matching-color receiver slots during the opening breath when the destination is otherwise only gray structure. The color should stay subordinate, but it keeps the pending target readable in still frames and avoids top-heavy saturated-composition audits.
- If an exit gate balances the opening, remove it before the traveling mask reaches that side; mask-on-gate contact reads as a guide collision in strict crowding review.
- Retire source actors and route lines together before the mask exit sweep. Route lines left after their source row disappears read as unsupported stems even when the final landing is clean.

### Magnet capture

- Show the receiver, target slots, and magnet core during the opening breath so the destination reads as a prepared capture pocket, not a late decorative prop.
- Let the leader compress inside the open receiver before support forms move. Supports arriving too early turn the capture into a generic regroup.
- Retire target slots and field rails as soon as the leader proves the capture. If those guides remain under the support handoff, strict crowding audits and human review both read them as residue.
- If source cleanup removes the left panel, shift or recenter the receiver stage before the delayed supports arrive so the proof hold does not stay off-center.
- For bracket-style receivers, use separated strokes or visible corner gaps when running strict crowding audits. A connected U-shaped guide can produce one broad bounding box that falsely overlaps the captured actor.
- Fade the receiver and magnet core before the final landing morph unless they still cause the motion. Leaving the core in place while the leader expands can create actor-to-actor cleanup contact.

### Support and force

- delay support motion until the leader reaches the mechanism,
- make beams tilt enough to read as load transfer,
- stretch the dominant form more when tension is the point,
- keep anchors, pivots, or bumpers visibly separate from the leader.
- for counterlift balance scenes, keep rise and drop lanes visibly separate before the beam tilts. Curve setup handoffs around the beam, hold one proof frame where the leader is above one end while the opposing support drops on the other, and keep any counter actor in its own pocket near the pivot.
- remove or demote broad pale stage panels if the beam, pivot, receiver marks, and actors already explain the mechanism. Large panels behind actors can create strict crowding support-envelope findings without improving the still frame.
- for bumper deflect scenes, let the leader own a held compression frame before supports arrive, then move supports into their separate release lanes before the final morph so they do not cross through each other.
- retire passive destination slots or scaffolds before the deflected landing. Once the bumper has explained the turn, lingering outlines can read as actor-to-outline crowding instead of useful structure.
- for cradle catch scenes, hold one frame where the dominant form visibly rests above lower support pads, then separate the final support dots downward and outward. Retire hollow slots before colored supports occupy the same lane, and remove guide arcs, accents, and backing panels before the settle morph or final hold so the catch does not become actor-to-guide or actor-to-actor crowding.

### Landing and arrangement

- make size contrast more obvious,
- increase angular spacing in fan layouts,
- for snap recoil scenes, show the destination slot or pressure surface before the snap, hold one stretched overshoot proof frame, then retire slots before support forms settle so outlines do not become crowding.
- keep the pressure wall close enough to explain the snap but far enough from support forms to clear targeted crowding checks after the recoil.
- after source cleanup in a snap recoil scene, recenter the resolved target stage so the final hold does not remain stranded in the old transfer lane.
- for anchored orbit scenes, reserve target slots during the opening breath and keep each satellite on a distinct lane. If the second orbit crosses the first satellite's proof position, the still frame reads as collision even when the final layout is clean.
- for orbit-guided motion, treat crowding audit findings as blocking only after full-size review confirms actor-to-actor, actor-to-outline, or guide-over-actor interference. Actor-on-path contact can be intentional when the guide is the track being followed.
- when tightening a fan-out camera for hierarchy, audit the whole fan transition cadence and recenter for the earliest proof frames, not only the resolved hold,
- push edge landings closer to the boundary if tension is the point,
- for edge-tension scenes, show a faint target slot or temporary pressure wall during the opening breath, hold the overshoot against it in a proof frame, then remove abandoned source panels and the wall before the resolved hold.
- let the lead form arrive first when the scene depends on delayed settle,
- remove orbital or staging scaffolding before the final frame.

### Continuation and project breakdowns

- preserve the prior resolved composition as a compact input when it is the source for the next beat,
- put compact input labels in a small header band when a footer would crowd the shrunken source cluster,
- reveal output block scaffolds before detailed content so the setup frame is balanced,
- make scaffolds visible enough to survive review: pale panels are fine, but borders and header hints must not vanish,
- give real blocks a low-contrast body anchor or footer rail if they cover placeholder scaffolds before rows appear. A blank block body can make one sampled activation frame top-heavy even when the full block is eventually balanced.
- when a resolved source cluster must become a compact input, use a short centered bridge beat before the shrink if immediate scaffolds would collide with the full-size source. Reveal strong destination scaffolds as the source scales into the input column, not under the full-size cluster.
- activate each large block before revealing its list rows,
- keep a balancing scaffold visible until the replacement block is visibly established; fading both through the same first sampled frame can create a one-frame off-center composition,
- do not `ReplacementTransform` placeholder scaffolds into text-bearing blocks. Fade or remove the scaffold, then fade in the real block so title text does not become unreadable mid-frame.
- reveal keypoints progressively with one row per beat,
- for short task-list rows, inspect full-size frames for collapsed word spacing. If `Text` or `MarkupText` makes spaces ambiguous, compose the label from per-word mobjects arranged with a fixed gap.
- keep the fork or branch geometry visible while each block becomes populated,
- after the output pulse, soften fork or branch guides below mechanism strength unless they are still causing motion. The final hold should preserve the source-to-block relationship without looking mid-transition.
- for fan-out guide sets, shorten or curve any hub-to-target stroke that is nearly vertical. A full radial line to a target above the hub often reads as stray residue in sampled frames.
- if a tighter camera makes the final fan hold stronger but the audit flags early fan proof frames as off-center, nudge the camera center for the transition before widening the shot again.
- update the poster composition to the new terminal state when the final hold changes.

### Imported SVG and component remaps

- keep transformable SVG roles in stable top-level groups such as `body`, `slot`, or `accent`,
- delete roles with no target separately before transforming surviving roles,
- use direct transforms only for roles with compatible geometry,
- treat closed filled shapes to open stroked paths as semantic handoffs, not geometric morphs,
- establish the new primary body before moving smaller child roles so they do not appear to float,
- use `FadeOut` plus `Create` for incompatible primary-body handoffs,
- for chart-like Mermaid SVG outputs such as treemaps, prefer rebuilding the visible chart as native Manim geometry when imported text and values land on edges or become tiny fragments. Keep the generated SVG as an inspectable artifact, but let native rectangles, slots, labels, and values carry the video.
- for staged chart unfolds, show parent frames and faint child slots in the opening breath, activate each next slot with a temporary red outline, then remove that outline as the filled cell lands. Use a perimeter terminal accent instead of a filled pulse over text-bearing chart cells.
- for overlap-free treemaps, let leaf cells be the only filled area. Express parent groups with thin header rules, labels, or separate bands outside the child cell bodies; large parent backing rectangles, stage plates, and enclosing final outlines can read as actor-to-outline collisions even when they look like harmless structure.
- in treemaps, preserve real gutters between every leaf cell and remove active slot outlines as soon as the cell lands. If a terminal perimeter accent touches the chart in strict crowding review, prefer a clean final hold or an accent with visible clearance over a decorative enclosing outline.
- when a treemap polish cycle succeeds, copy the reusable structure into a skill-local example and link it from this file. Do not leave the only good pattern inside a spike directory.
- scale native Manim labels to the current imported SVG body when they are attached to an icon. A fixed label minimum can overpower compact document or badge icons after the icon becomes part of a source cluster.
- for Mermaid-generated diagram SVGs, keep the `.mmd` source as the inspectable diagram definition, render it with Mermaid CLI's `mmdc -i input.mmd -o output.svg` command. When avoiding a global install, use `npx -y -p @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.svg -b transparent`. Normalize only the node groups that need to become video actors into stable top-level ids before extracting fragments.
- for generated diagram SVGs, write whole source/target SVGs for inspection but animate per-role fragments extracted from stable top-level ids. Attach native Manim labels to imported node bodies instead of relying on SVG text import.
- if imported SVG arrows look bulky after render, replace video connectors with native Manim `Arrow` or `CurvedArrow` objects anchored to the SVG role positions. Keep the generated SVG for inspection, but do not force low-quality SVG arrowheads into the final video.
- when rebuilding generated Mermaid labels natively, preserve SVG `text-anchor` semantics and keep spaces between tspan chunks. Centering every label on its source coordinate can silently push left-aligned labels outside their node bodies.
- for generated SVG unfold scenes, reveal contiguous source-order batches rather than round-robin batches. Round-robin reveals can leave sparse lines or detached labels alone for several proof frames even when the final diagram is coherent.
- for small Mermaid block or pipeline diagrams, keep the `.mmd` and generated SVG as inspectable artifacts but rebuild the video as native Manim cards, receiver slots, connectors, and one active pulse when fragment extraction separates labels from bodies. Use faint labeled slots in the opening breath, fade each slot as its card lands, and avoid title/subtitle bands or extra terminal badge text when the cards already carry the semantics. If the final output card needs a terminal mark, use separated corner brackets with enough clearance to survive full-size crowding review.
- for Mermaid Venn or other intentional-overlap diagrams, keep the `.mmd` and generated SVG for inspection but rebuild the video with native circles, overlap regions, and prepared slots when generic fragment fades make the scene static. Attach the active cue to the current set or shared region, not to a separate rectangle or route line, and do not treat strict no-crowding findings on the intentional overlap as blocking without full-size review.
- selection handles or proof dots for imported SVG nodes should sit near node corners; centered dots over labels read as text defects. Route handles can sit on route centers when they do not obscure arrow direction.
- when an SVG cluster becomes a compact input for a continuation scene, tighten the terminal fan or stack before shrinking it. Loose source clusters become harder to read once framed inside a small panel.
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
- the rendered video has been reviewed with the pre-finish protocol above, not only by successful render or audit output,
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
- if the scene uses sequence-diagram handoffs, receiver slots should be visible in the opening or just before arrival, activation bars should record ownership, and the final hold should remove transient receiver scaffolds.
- if the scene uses a fork or split, the trunk remains visible long enough and the branches separate enough to avoid reading as a loose regroup.
- if the scene uses a funnel merge, multiple inputs are visibly compressed inside a narrowing neck before the dominant landing.
- if the scene uses a formula handoff, the formula is readable in its composed state and the result visibly replaces the destination value.
- if the scene uses an axis-drop cue, the vertical cue survives in at least one proof frame, the target slot is visible before motion, and the cue is gone before the point starts traveling.

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
6. run the pre-finish review protocol and do not declare the result done until the rendered evidence passes it,
7. record reusable lessons in this skill, preferably [references/video-quality-lessons.md](references/video-quality-lessons.md) or the most relevant skill-local reference,
8. fold recurring lessons back into this skill instead of letting them accumulate outside the skill.
