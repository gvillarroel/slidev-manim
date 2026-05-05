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
- For content-first transparent sequence assets, prefer neutral white/gray participant cards and gray request routes over saturated per-participant colors. Let primary red carry receiver cues, returns, and the terminal artifact.
- Faint red receiver slots in the opening breath can make the pending handoff survive still-frame review and keep active-color composition audits from centering only on a top row.
- Strict crowding audits on native sequence diagrams often flag expected route-to-label, route-to-slot, activation-bar, and card-internal contacts. Inspect those timestamps full size, then patch only contacts that obscure labels or make the receiver mechanism ambiguous.

# Comparison Panel Scenes

Use `side-by-side comparison asset` when a Slidev comparison page embeds two related Manim clips.

- Treat each side as a complete slide-integration scene, not as a short decorative loop. Budget a visible opening breath, a mechanism proof beat, cleanup, and a 5 to 7 second final hold.
- Make the difference between the two sides visible through mechanism grammar. For example, one side can use a direct transfer while the other uses a prepared receiver, guide path, halo, or other causal scaffold.
- Keep the title band outside the motion lane. If the actor crosses under the title, lower the stage or add a quiet divider so sampled frames do not read as text collision.
- Use restrained square stage geometry and gray structure by default; let the actor, active route, receiver cue, or terminal halo carry the comparison.
- Remove route scaffolds and empty source slots before the resolved hold, then recenter the final actor or cluster so the clip does not end stranded in an old transfer layout.
- Resting audits may report route-to-actor or route-to-slot notices for the guided side. Inspect the full-size frame and treat the notice as acceptable only when the route is visibly the track being followed and does not obscure the actor or receiver.

# Hero Plus Support Assets

Use `hero plus support asset` when one dominant transparent clip and one smaller looping clip are meant to appear together on a Slidev page.

- Pace the hero as the explanatory slide-integration scene: visible opening structure, one strong proof path, cleanup, and a 5 to 7 second final hold.
- Keep the support clip as a documented micro-loop only when it is clearly subordinate to the hero.
- Use the same red/gray grammar in both assets so the support loop reinforces the hero rather than introducing a second palette.
- Put the support actor on a nearby motion lane instead of directly on the static guide. Actor-on-guide contact can read as crowding in sampled stills, while a small lane offset still communicates the loop.
- Remove terminal halos, old center dots, and guide scaffolds from the hero final hold unless they still cause the resolved state. A clean hero hold should be calmer than the proof path.
- Size the support loop for its eventual downscaled embed, not only for the full square render. A tiny support loop can pass audits while disappearing in the actual slide hierarchy.
- When enlarging a hero orbit or route, budget the full transient footprint of the red actor, halo, and proof pulse. The base track may have enough margin while the active halo still trips top/bottom frame pressure.

# Multi-Asset Grid Scenes

Use `multi-asset grid` when a Slidev page embeds three or more independent Manim clips in one grid or repeated panel layout.

- Let the Slidev layout own labels, titles, cards, shadows, and rounded chrome. The Manim assets should usually be content-first transparent clips with only the mechanism and quiet support geometry.
- Use one shared visual grammar across the asset family, normally primary red for the active actor and grayscale for support. Four independent saturated palettes make a dense grid read as unrelated samples instead of one coherent system.
- Give every promoted grid asset slide-integration pacing unless a shorter micro-loop is explicitly documented. Looping playback in the deck is not a substitute for a meaningful opening breath, proof beat, cleanup, and final hold in the exported clip.
- Keep frame-zero scaffolds visible for each asset so posters and fallback stills are useful before video playback starts.
- Generate dense review frames and contact sheets per asset, not only for the combined Slidev screenshot. A grid can look aligned while one member still has a weak mechanism, stale title chrome, or an under-held final state.
- Resting audits may report notice-level contacts when an actor intentionally sits on an orbit, track, ring, or receiver during the proof. Treat those as acceptable only after full-size frame review confirms the guide is the mechanism and not stale residue.

# Frame Wrapper Embed Assets

Use `frame wrapper embed asset` when a transparent Manim clip will be placed inside Slidev browser chrome, phone frames, device mockups, or other external UI wrappers.

- Let the Slidev frame own the browser shell, phone bezel, title bar, notch, shadows, and surrounding chrome. The Manim video should usually contain only the content-region mechanism.
- Build separate compositions for wide and tall embeds instead of cropping one scene into both ratios. Tall device renders often need larger cards, longer vertical routes, and stronger spacing to avoid shrinking into a small center icon.
- Use one primary-red actor for the handoff and keep source, processor, and output cards in neutral gray. Multiple saturated role colors compete with the external frame and make the transparent asset feel like a second UI system.
- Keep route segments outside the card interiors and fade receiver slots as the real cards land. A route or slot that survives into the final hold reads as local chrome residue inside the device frame.
- Generate 0.3-second alpha-on-white review frames per aspect ratio, then inspect at least one proof frame and the final hold full size before judging the embed from the Slidev deck.

# Mermaid Companion Assets

Use `mermaid companion asset` when a Slidev page already has a static Mermaid diagram and the Manim video should reinforce only one mechanism beside it.

- Let Mermaid own the explicit diagram syntax and labels. The Manim asset should usually be a native red/gray motion companion, not a second multicolor diagram.
- Show the full pending native flow during the opening breath: source card, destination slots, short route segments, and receiver cues should all be visible before the pulse moves.
- Keep route segments slightly detached from card borders. A red pulse parked on a card edge reads as a still-frame defect even when the route is semantically correct.
- Use one terminal artifact with margin, such as separated output brackets. Avoid leaving the active dot at the frame edge during the final hold.
- Keep durable companion-asset refinements in [references/video-quality-lessons.md](references/video-quality-lessons.md).

# Browser-Native SVG Narratives

Use `browser-native SVG narrative` when a spike records an HTML/SVG visual system through Playwright but still follows this repository's red/gray motion-language standards.

- Generate dense 0.3-second review frames and a contact sheet from the promoted recording, not only named proof screenshots.
- Make the first frame audit-visible: show the destination hub, slots, route hints, or receiver scaffold before any side-entering actor starts moving.
- If Playwright recording starts with a blank browser frame, trim the promoted recording after capture and preserve explicit output frame timestamps. A frame-count-valid WebM with broken duration metadata will make cadence audits miss the real scene.
- Fade old ingress trails once the hub, fan-out, or selected card owns the mechanism; long red history rails can pull sampled frames off center after the story has moved on.
- Keep associated chips and callouts in a side pocket outside the selected card's rotation or swing lane. If they sit below the card, they can read as a crowded second body.
- Use a clean white stage and subtle gray grid by default. Decorative glows, broad plates, and soft browser backgrounds often weaken sparse red/gray hierarchy.
- Treat strict crowding findings on card internals, selected-card brackets, or intentional hub rings as full-size review prompts. Patch them only when the frame actually reads as collision or obscures the mechanism.
- Keep durable browser-native refinements in [references/video-quality-lessons.md](references/video-quality-lessons.md).

# Time Rail Scenes

Use `time rail` when a left-side timeline or spine should act as the narrator instead of a traveling red dot.

- Treat the rail as elapsed time: show the full pending spine, ticks, slots, or branches in the first frame, then let the active red segment grow through it.
- Avoid adding a separate guide dot when the rail itself can carry progression. The active segment, tick state, and destination slot should explain causality.
- Keep the left rail visually stable while content resolves to the right; the viewer should read the rail as an organizing timeline, not as a decorative divider.
- Branches should emit from the rail only after the active segment reaches the tick. Soften branch guides after their card lands so the final frame does not look mid-transition.
- Use a terminal rule or final rail state as the resolved artifact. Do not leave disconnected pulses at former tick or branch positions.
- For transparent time-rail sequences, prefer outline-only pending card slots over filled placeholder bars. Filled slots can look like a static wireframe before the rail proves causality.
- Keep terminal artifacts attached to the rail itself, such as a completed rail with a bottom cap. Detached red rules away from the spine compete with the rail's narrator role.
- To continue from agenda into content, keep the rail fixed, activate one tick, soften or remove future agenda items, and let the active card open into a detail panel. The first detailed beat should feel like the selected point now owns the stage, while the rail preserves orientation.
- Avoid secondary red connector lines, row-outline boxes, or terminal rules inside the detail panel. If the rail is the narrator, extra red lines away from it read as annotation artifacts; use quiet gray local cues for detail rows.

# Rhythm Gate Scenes

Use `rhythm gate` when timing cadence is the mechanism and the viewer should read progress as a sequence of prepared openings.

- Show the rail, source, destination, and every pending gate in the opening breath so the first frame reads as a timed path, not a moving-dot demo.
- Open each gate before the actor reaches the center of the slot, then hold a proof frame where the actor is visibly inside the opened channel.
- Give the opened channel real clearance around the active actor. If the actor scales during the proof, widen the gate rules or reduce the scale pulse before accepting strict crowding findings.
- Keep beat marks off the gate-rule endpoints. A tiny mark that touches the lower end of a gate line can look harmless in thumbnails but still reads as zero-clearance residue in full-size audit overlays.
- During cleanup, remove receiver slots, gate rules, and old source scaffolds before the actor scales into a terminal artifact. Faint leftovers can pull composition audits off-center even when the resolved cluster is visually centered.
- Prefer separated terminal echo strokes, ticks, or corner marks over full rings that enclose the actor. Enclosing rings often become actor-to-outline crowding unless the containment is the explicit subject.

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
- Prefer one active red role and grayscale data fields unless distinct semantic categories truly need multiple colors. In packet scenes, bit position usually matters more than category hue.
- Put scan cues outside the field body when labels must remain readable. Short top/bottom boundary notches can prove progression without crossing text.
- Retire the slot label just before the real field grows. Growing a body over ghost text creates double labels and strict crowding failures in sampled proof frames.
- Remove title bands, visible stage plates, and closed terminal outlines unless they carry meaning. A clean page background with separated terminal brackets usually leaves the final hold calmer.
- For transparent packet assets, set Manim transparency in config and on the scene camera, then validate decoded alpha extrema. WebM output alone does not prove transparency.

# Kanban Board Scenes

Use `native kanban board` when a Mermaid Kanban SVG unfold becomes a tiny static fragment reveal, or when labels and card bodies arrive separately.

- Keep the `.mmd`, generated SVG, and fragments as inspectable artifacts, but promote a native Manim board when the board flow is the mechanism.
- Show the full lane scaffold in the opening breath: columns, headers, faint receiver cards, quiet connector stubs, and any source card should be visible before motion starts.
- Use one active pulse per handoff and stop it at the receiver entrance. Highlight only receiver outlines, not the slot text, so the target reads as prepared without becoming a second active label.
- Remove receiver slots before fading in the real cards. If slot text and card text cross-fade, sampled frames can become unreadable even though the final card is clean.
- If the board has empty lower lanes, use restrained bottom lane rails or a shorter lane height to balance strong-color headers. Otherwise strong-color centering audits and human review can read the board as top-heavy.
- Use separated corner brackets around the terminal card instead of enclosing the full board. The final hold should identify the output without turning the whole board into a red frame artifact.
- For transparent Slidev assets, make both the scene and render command transparent; scene opacity alone is not enough if the Manim CLI render omits `--transparent`.

# State Diagram Scenes

Use `native state flow` when a Mermaid state diagram SVG unfold becomes a thin static strip, renders too slowly through `SVGMobject`, or leaves labels and state bodies without a clear handoff mechanism.

- Keep the `.mmd`, generated SVG, PNG, and fragments as inspectable artifacts, but promote native Manim state cards, arrows, receiver cues, and one active pulse when the state transition is the subject.
- Use a two-row or otherwise expanded layout for small state diagrams instead of accepting a thin horizontal strip with large dead space.
- Show faint labeled receiver slots in the opening breath so frame zero explains the pending states before the first pulse moves.
- Stop the active pulse at the receiver entrance and fade or reset it before the next handoff. A pulse parked over the state label reads as a text defect.
- Make receiver cues outline-only. Animating whole cue opacity can fill the card and obscure the label even when the final card is clean.
- Remove decorative guide rails or review frames before the final hold unless they still cause the state relationship. The resolved hold should usually keep only state cards, arrows, the terminal state, and a small separated accent.
- Keep review extraction dependencies lazy inside helper functions so rest-state audits can import the scene with their lean dependency set.

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
- For simple direct-transfer clips that are meant to be promoted Slidev assets, do not accept a three-second decorative move. Give the clip a prepared source and destination, one active proof route, cleanup, and a 5 to 7 second resolved hold.
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
8. For browser-native narratives that loop interactively, use a recording-only non-looping mode and hold the resolved frame through the exported final hold.
9. For browser-native SVG search beats, keep active target cues on perimeters and move visited echoes outside closed outlines after the beat. Faint placeholder internals are safer than stacked red marks inside a card or slot.
10. For browser-native five-act narratives, inspect the tension-to-transformation cleanup at dense cadence. Retire old search scaffolds and side-entry trails before a centered hub, ring, or system becomes the proof frame, or the still frame will keep reading the previous route.
11. For browser-native prism or facet narratives, make frame-zero destination scaffolds strong enough for dense composition audits, then demote internal red facet accents and compact the terminal cluster for portrait proof frames.
12. For browser-native threshold narratives using `preserveAspectRatio="slice"`, make portrait viewBox ratios match the handset ratio closely or the terminal bracket grammar can crop into disconnected edge fragments.

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
- for camera-led focus stops, prefer one red guide dot and open receiver brackets. Decorative halos and closed slots can create zero-clearance still frames around the very marker meant to explain the stop.
- for long camera travel holds, validate both the rendered frame audit and the resting-mobject audit. Widen the travel frame enough that origin and destination panels are visible with real margin before the guide starts crossing.

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
- for arc handoffs, let one primary-red dominant form visibly ride the curve before gray support forms move. Use open source and destination brackets during the opening breath, keep support guide arcs visibly below the support actors, then keep balancing scaffolds through the recentering move and remove them only after the resolved cluster has settled.
- keep review-frame helper dependencies lazy-imported inside runner utilities. Resting-mobject audits import the scene file directly, so top-level capture dependencies can break validation even when rendering works.
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
- for mask-transfer scenes, retire the source row and route lines before the mask exit sweep, then remove destination slots, the mask band, exit gate, and traveling accent before the compact landing morph. Faded source actors, lingering slots, or an accent left inside the destination cluster can pass broad composition review but fail strict actor-to-actor clearance.
- for mask-transfer cleanup, split source-row retirement from the mask exit when 0.3-second samples show the band brushing fading source chips. A very short source-retire beat can clear strict crowding without reintroducing a dead empty crossing.
- Use faint matching-color receiver slots during the opening breath when the destination is otherwise only gray structure. The color should stay subordinate, but it keeps the pending target readable in still frames and avoids top-heavy saturated-composition audits.
- Tune opening receiver slots against both human review and audits. If they are too strong, they can become extra active actors in crowding review; if they are gray-only, they can vanish from composition centering.
- For wide-row-to-compact-cluster mask transfers, preview faint compact receiver targets before the morph, then enlarge and recenter the final cluster so the landing reads as prepared in sampled still frames.
- If an exit gate balances the opening, remove it before the traveling mask reaches that side; mask-on-gate contact reads as a guide collision in strict crowding review.
- Retire source actors and route lines together before the mask exit sweep. Route lines left after their source row disappears read as unsupported stems even when the final landing is clean.
- for inset or magnification panel scenes, retire the source panel, receiver slot, and stale guides before the final centered hold. If animated recentering creates sampled off-center cleanup frames, snap the resolved cluster to its final layout after the source disappears instead of drifting it across the hold.
- split crosshair or reticle guide lines around the terminal dot or core. Continuous guide strokes running under the actor create actor-to-guide contact in still frames and make strict crowding reports harder to triage.
- for transparent square assets with a local review stage plate, keep the opaque plate slightly inside the Manim frame. A full-frame plate can preserve `alpha_mode=1` while the decoded alpha plane is all opaque; validate transparency with decoded alpha extrema, not metadata alone.

### Magnet capture

- Show the receiver, target slots, and magnet core during the opening breath so the destination reads as a prepared capture pocket, not a late decorative prop.
- Let the leader compress inside the open receiver before support forms move. Supports arriving too early turn the capture into a generic regroup.
- Retire target slots and field rails as soon as the leader proves the capture. If those guides remain under the support handoff, strict crowding audits and human review both read them as residue.
- If source cleanup removes the left panel, shift or recenter the receiver stage before the delayed supports arrive so the proof hold does not stay off-center.
- For bracket-style receivers, use separated strokes or visible corner gaps when running strict crowding audits. A connected U-shaped guide can produce one broad bounding box that falsely overlaps the captured actor.
- Keep the leader's stretch lane clear of waiting supports. If the source supports must remain visible, park them above or below the lane before the leader elongates.
- Do not let a broad target panel outline surround the leader during the capture proof. Use a stroke-free pale plate or let the open receiver strokes define the pocket, then remove the plate before the support handoff.
- Fade the receiver and magnet core before the final landing morph unless they still cause the motion. Leaving the core in place while the leader expands can create actor-to-actor cleanup contact.

### Keystone lock

- Let the support forms assemble the receiving pocket before the leader arrives; otherwise the lock reads as a generic regroup.
- Use the opening breath to show the source form, route hint, and faint destination pocket slots so the transfer has a visible purpose before motion starts.
- Keep broad but quiet balancing scaffolds visible while the constrained cluster recenters. If the source or target plate disappears while the locked pocket is still right-weighted, 0.3-second composition audits can catch a one-frame off-center cleanup beat.
- Avoid broad closed receiver outlines around the pocket when the leader has not arrived yet. Open slots and support jaws usually reserve the destination with fewer actor-to-outline or actor-to-support audit prompts.
- If the proof requires the leader to enter a support pocket, treat one strict insertion-frame crowding prompt as a full-size review cue before patching. Patch it only when the red actor visibly obscures the support geometry or the pocket stops reading as the mechanism.
- Once the cluster is centered, fade the source/target plates and route before the terminal hold. The final support should sit clear of the leader tip unless the contact itself is the pressure proof.

### Support and force

- delay support motion until the leader reaches the mechanism,
- make beams tilt enough to read as load transfer,
- stretch the dominant form more when tension is the point,
- keep anchors, pivots, or bumpers visibly separate from the leader.
- for counterlift balance scenes, keep rise and drop lanes visibly separate before the beam tilts. Curve setup handoffs around the beam, hold one proof frame where the leader is above one end while the opposing support drops on the other, and keep any counter actor in its own pocket near the pivot.
- for counterweight balance scenes, keep the beam and counterweight actors visibly separate in every sampled proof frame. Use open bracket slots during setup instead of closed boxes around actors, remove side rails or broad panels when the beam already explains the stage, and nudge lifted or dropped supports clear of tilted beam endpoints before accepting the hold.
- remove or demote broad pale stage panels if the beam, pivot, receiver marks, and actors already explain the mechanism. Large panels behind actors can create strict crowding support-envelope findings without improving the still frame.
- for ramp-lift scenes, keep quiet support actors near the ramp after the source lane disappears so the held lift proof does not become a sparse off-center ramp-only frame. Retire broad source and destination panels before the support proof; strict actor-on-ramp crowding findings are review prompts, but actor-to-panel, actor-to-support, and final-hold contacts should still be patched.
- for bumper deflect scenes, let the leader own a held compression frame before supports arrive, then move supports into their separate release lanes before the final morph so they do not cross through each other.
- retire passive destination slots or scaffolds before the deflected landing. Once the bumper has explained the turn, lingering outlines can read as actor-to-outline crowding instead of useful structure.
- for cradle catch scenes, hold one frame where the dominant form visibly rests above lower support pads, then separate the final support dots downward and outward. Retire hollow slots before colored supports occupy the same lane, and remove guide arcs, accents, and backing panels before the settle morph or final hold so the catch does not become actor-to-guide or actor-to-actor crowding.

### Landing and arrangement

- make size contrast more obvious,
- increase angular spacing in fan layouts,
- for scale-hierarchy scenes, show the target size slots during the opening breath, then recenter the resolved dominant/support cluster after source cleanup. If the final hierarchy already reads without help, remove soft plates, route guides, and terminal brackets before the final hold.
- for snap recoil scenes, show the destination slot or pressure surface before the snap, hold one stretched overshoot proof frame, then retire slots before support forms settle so outlines do not become crowding.
- keep the pressure wall close enough to explain the snap but far enough from support forms to clear targeted crowding checks after the recoil.
- after source cleanup in a snap recoil scene, recenter the resolved target stage so the final hold does not remain stranded in the old transfer lane.
- for snap recoil scenes, prefer one primary-red leader with gray support forms. Use open target rails or receiver slots rather than a broad filled destination plate under the leader; filled plates can create actor-to-panel crowding during the stretched proof even when the motion reads correctly.
- for staged convergence scenes, use open rails or separated brackets for the narrow lane rather than a closed box around the compressed actors. Retire any red cue before the held lane proof, then remove slot and rail scaffolds before the centered final hold.
- for staged convergence openings, a temporary destination edge can balance a left-heavy source scaffold, but fade that edge during the compression transform rather than in a separate static cleanup beat. The final morph should land directly on the centered resolved cluster instead of relying on a later recenter shift.
- for terminal corner brackets, give the horizontal and vertical strokes a real gap at each corner. Connected L-shaped brackets can create zero-clearance strict-crowding failures even when the actors themselves have enough air.
- for anchored orbit scenes, reserve target slots during the opening breath and keep each satellite on a distinct lane. If the second orbit crosses the first satellite's proof position, the still frame reads as collision even when the final layout is clean.
- for orbit-guided motion, treat crowding audit findings as blocking only after full-size review confirms actor-to-actor, actor-to-outline, or guide-over-actor interference. Actor-on-path contact can be intentional when the guide is the track being followed.
- when tightening a fan-out camera for hierarchy, audit the whole fan transition cadence and recenter for the earliest proof frames, not only the resolved hold,
- push edge landings closer to the boundary if tension is the point,
- for edge-tension scenes, show a faint target slot or temporary pressure wall during the opening breath, hold the overshoot against it in a proof frame, then remove abandoned source panels before the resolved hold.
- if the resolved edge-tension hold intentionally stays right-weighted, keep a quiet left anchor or shortened tension tether as causal balance. Use thin filled bars for passive rails and walls when rest-state audits need to see them; zero-area `Line` mobjects may be visually present but ignored by bounds audits.
- for hollow target slots, set stroke opacity directly rather than applying group opacity. Group opacity can make stroke-only circles look filled, which turns pending destinations into ghost actors.
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
- for small Mermaid block or pipeline diagrams, keep the `.mmd` and generated SVG as inspectable artifacts but rebuild the video as native Manim cards, receiver slots, connectors, and one active pulse when fragment extraction separates labels from bodies. Use faint labeled slots in the opening breath, fade each slot as its card lands, and avoid title/subtitle bands or extra terminal badge text when the cards already carry the semantics. Keep route pulses on connector lanes and fade them at receiver entrances instead of letting them sit on card labels. Use open guide rails instead of a closed stage plate when the plate is only a review frame. If the final output card needs a terminal mark, use separated corner brackets with literal gaps and enough clearance to survive full-size crowding review.
- for generated diagram remaps, show faint destination slots from frame zero when the opening source row would otherwise sit inside a mostly empty frame. Prefer open top/bottom rails over closed review frames, fade those rails before the resolved hold, and avoid placing a terminal bracket on the same corner where an incoming arrow lands. A three-corner terminal accent can be clearer than a symmetric bracket set that collides with the route.
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
- stale Manim partial movies or promoted outputs survived a style change because the spike-local staging directory was reused.
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
