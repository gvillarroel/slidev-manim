---
id: KNOW-0004
title: GJV1 Manim video quality learnings
status: active
date: 2026-04-15
---

# Summary

Higher-quality Manim videos in this repository come from hypothesis-driven iteration, sparse compositions, and frame review. The strongest results rely on shape relationships, timing, and color hierarchy more than on text.

# Experiments

## Manim Code Highlighting Options

- **Hypothesis**: A dense code-gallery scene reads better when the first frame already shows the full scaffold, the title has a reserved header band, and the final hold keeps only one persistent code-emphasis device.
- **Result**: Confirmed on `spikes/manim-code-highlighting-options/` after removing the blank opening frame, lowering the code grid and option panel below the title/subtitle band, and simplifying the final hold to one token box plus a concise summary tag.
- **What worked**:
  - adding the header, language grid, and option panel before the opening wait so frame-zero review shows a meaningful structure instead of an empty local stage,
  - reserving vertical space for the title and subtitle before placing dense code cards or option panels, because small subtitle collisions are obvious in full-size frames but easy to miss in thumbnails,
  - cleaning the final hold by fading the broad line wash and keeping only the token box as the durable active geometry,
  - moving the terminal summary above the lower stage edge and shortening its copy so it reads as a resolved badge rather than a footer artifact.
- **Validation note**:
  - the final render was reviewed with 0.3-second alpha-on-white contact sheets and full-size proof frames at the opening, summary entrance, and final hold; composition audit sampled 91 frames with zero blocking frames, resting-mobject audit reported zero blocking snapshots, and WebM metadata reported `alpha_mode=1`.

## Manim Semantic Transform Lab

- **Hypothesis**: A transform-gallery scene reads better when every later example has a prepared proof bay visible in the opening breath, instead of appearing as disconnected lower-row mini-scenes.
- **Result**: Confirmed on `spikes/manim-semantic-transform-lab/` after replacing the near-blank opening and high, tiny flow with a two-tier scaffold: top handoff path plus three lower proof bays for shape, formula, and topology examples.
- **What worked**:
  - adding all proof bays at frame zero so the opening still frame explains where future transform examples will land,
  - lifting the lower proof row until the dark transform examples no longer dominated composition-center audits during the topology proof beat,
  - scaling the additive `TransformMatchingTex` target to the formula bay before accepting the render, because the first full-size review caught the expression crossing its panel,
  - keeping red identity markers outside card outlines with enough endpoint margin, then pulling the top-flow endpoints inward so the final-card handoff cleared edge review.
- **Validation note**:
  - the final render was reviewed with 0.3-second alpha-on-white contact sheets and full-size proof frames for the opening, shape reorder, formula expansion, topology fade, final handoff, and final hold. Composition audit cleared 132 sampled frames with zero blocking frames, resting-mobject audit had zero blocking snapshots, and WebM alpha validation reported `alpha_mode=1` with alpha range `0..255`. The strict crowding audit still reported text-inside-card and actor-near-support prompts, which were inspected full size and treated as expected for card/formula internals rather than visible collisions.

## Inset Annotation Panel

- **Hypothesis**: A small inset asset reads better when the opening frame already shows the source panel, target inset slot, and route scaffolds, then uses one red actor to prove the handoff into the magnified view.
- **Result**: Confirmed on `spikes/inset-annotation-panel/` after replacing 4-second label-heavy loops with 27.6-second and 26.9-second slide-integration renders.
- **What worked**:
  - using square panels, gray structure, and one primary-red actor instead of blue/orange/green decoration,
  - setting the square variant's Manim frame shape before scene construction, because `-r 1200,1200` alone changes pixels without making the composition square,
  - showing receiver brackets, a route, and an aperture during the opening breath so both videos explain the pending magnification before anything moves,
  - removing duplicate terminal dots after full-size proof-frame review caught a shadowed double-core that the contact sheet made easy to miss,
  - shrinking local `page-background` stages to margin-safe dimensions so resting-mobject audits do not fail on neutral backing geometry.
- **Validation note**:
  - final 0.3-second contact sheets, full-size proof frames, composition audits, rest-state audits, duration checks, and WebM metadata checks all passed; both promoted WebMs report `alpha_mode=1`.

## Side-by-Side Comparison Assets

- **Hypothesis**: A comparison-slide asset reads better when each side is a complete slide-integration clip with its own opening structure, mechanism proof, and final hold, instead of a short generic loop.
- **Result**: Confirmed on `spikes/compare-two-approaches/` after replacing 3.13-second direct loops with 26.1-second and 28.6-second paced clips.
- **What worked**:
  - keeping the title band clear by moving the motion stage below a quiet divider,
  - using square stage geometry and subdued gray structure so the actor and handoff path own the hierarchy,
  - making Approach A a plain direct transfer while Approach B uses a prepared receiver, guide path, and halo, so the comparison is visible in still frames,
  - removing route scaffolds before the resolved hold and recentering the final actor so neither clip ends stranded in a transfer layout,
  - promoting Manim outputs by latest modified time so rerenders do not copy stale files from reused staging folders.
- **Validation note**:
  - broad 0.3-second composition audits can clear while resting-mobject audits report expected path-to-actor or path-to-slot notices. For guided handoffs, inspect whether those notices are the route being followed before treating them as defects.

## Time Rail Narrative Family

- **Decision**: Name the timeline-like alternative to the red guide dot `time rail`.
- **Rationale**: The left-side vertical line reads as a line of time, so it can become the narrator instead of a separate moving point. Progress should be shown by the rail itself filling, reaching ticks, and causing cards or branches to resolve.
- **Reusable rule**:
  - show the full pending rail, ticks, slots, or branches in the first frame,
  - grow the active primary-red rail segment through time,
  - let each destination resolve only after the rail reaches its tick,
  - avoid adding a separate red dot unless it has a different semantic job,
  - soften branch or slot scaffolds after their causal beat so the final hold reads as resolved.
- **New exploration spikes**:
  - `spikes/time-rail-sequence/` tests time as a vertical progress narrator for sequential cards,
  - `spikes/time-rail-branching/` tests time as a spine that emits consequence branches,
  - `spikes/time-rail-point-one/` tests the continuation from agenda into the first detailed point.
- **Continuation rule**:
  - treat the first pass as the agenda,
  - let the rail reach point 1 before any detail appears,
  - soften future agenda items so the viewer understands the presentation is now inside point 1,
  - open the active card into a detail panel while keeping the rail fixed as orientation.
- **Detail-panel correction**:
  - avoid diagonal red connectors, red row-outline boxes, and extra terminal red rules after point 1 opens,
  - keep red reserved for the rail, active tick, and active card accent,
  - use quiet gray row cues when the detail panel needs progressive focus.

## Split Screen Sync

- **Hypothesis**: A split-screen embed test reads more like a real synchronization mechanism when both panes are visible from the first frame, each receiver slot is prepared before the pulse arrives, and the route pulse stops at the slot entrance instead of sitting inside a hollow outline.
- **Result**: Confirmed after replacing a 3.2-second single-circle slide with a 25.4-second staged three-row sync render.
- **What worked**:
  - showing the source cards, faint routes, and empty receiver slots before the opening breath, so the first sampled frames explain the pending split-screen relationship,
  - moving one red pulse at a time along shortened connector segments with visible clearance from both source and target cards,
  - fading each receiver slot out as the target card lands, which avoids actor-to-outline crowding while keeping the receiver causal,
  - using a complete fading terminal outline instead of drawing the outline stroke around the final hold, because partially drawn edge fragments looked like residue in 0.3-second frames,
  - promoting rendered files by newest modification time so reused Manim staging folders cannot copy stale renders.
- **Validation note**:
  - strict crowding audit findings on cue rectangles were useful, not noise. Wrapping red cue boxes around actors created zero-clearance actor-to-outline contacts; replacing those cues with separated route segments cleared composition, rest, and crowding audits.
- **Terminal-hold refinement**:
  - a closed terminal rectangle can work as a brief fading completion cue, but it becomes actor-to-outline crowding when it holds around the resolved cards,
  - for a held terminal state, prefer separated corner brackets or other broken perimeter marks with real clearance; they keep the completion signal without enclosing the actors in one audit bounding box.

## Mermaid Treemap SVG Unfold

- **Hypothesis**: A chart-like Mermaid SVG unfold reads better when the final chart is rebuilt as native Manim geometry with visible slots in the opening breath, rather than imported as tiny SVG fragments that fade into place.
- **Result**: Confirmed after replacing the generic fragment fade-in with a 25.9-second staged treemap reveal.
- **What worked**:
  - showing both parent section frames and faint child slots in the first frame, so the opening breath reads as a pending treemap instead of an empty stage,
  - centering native labels and values inside each treemap cell, which removed imported SVG edge labels and tiny numeric fragments,
  - using a red active outline around the next slot, then removing it as each cell lands, so the mechanism survives 0.3-second still-frame review without contaminating the resolved hold,
  - reserving the terminal red accent for a perimeter outline around the complete chart, avoiding a filled pulse over text-bearing cells,
  - keeping the local stage and title band separated enough that the header no longer competes with the chart frame.
- **Overlap-free refinement**:
  - when the target is a zero-overlap treemap, let only leaf cells own filled area and keep parent categories as thin header rules, labels, or separate bands outside the child cell bodies,
  - avoid large parent backing rectangles, local stage plates, and enclosing final outlines if strict crowding review reads them as actor-to-outline contact with the chart,
  - use real gutters between every leaf cell, faint slot previews during the opening breath, and a temporary active outline that disappears as soon as the filled cell lands,
  - if a terminal accent creates chart-outline contact, prefer a clean final hold or a perimeter accent with visible clearance over an outline that touches the treemap.
- **Reusable artifact**: The self-contained skill example `examples/overlap-free-treemap-unfold.py` preserves this pattern for future treemap videos.
- **Validation note**:
  - broad composition and resting-mobject audits can pass even when the render is too short for slide integration; duration remains a separate blocking check.

## Mermaid Requirement SVG Unfold

- **Hypothesis**: A generated Mermaid SVG unfold reads better when the first frame shows a faint complete scaffold, text anchors from the SVG are preserved, and source-order fragments reveal in contiguous chunks instead of round-robin batches.
- **Result**: Confirmed after the requirement diagram render moved from a mostly empty opening and cropped labels to a 25.5-second render with readable anchored labels, visible opening structure, and a non-occluding terminal outline.
- **What worked**:
  - preserving SVG `text-anchor` semantics when rebuilding labels as native Manim text, so left-aligned Mermaid labels no longer drift half a label width outside their boxes,
  - joining individual SVG/tspan text parts with explicit spaces, which prevents labels such as `Text: Decompose...` from collapsing into one run,
  - keeping a faint full-diagram scaffold during the opening breath, then fading it as the first real batch appears, so the first sampled frames show the intended target structure,
  - revealing fragments in contiguous source-order chunks, because round-robin batching can isolate sparse lines or labels for too long,
  - using a perimeter terminal outline instead of a filled red pulse, which gives the hold a center of interest without covering text.
- **Validation note**:
  - broad composition audit and resting-mobject audit cleared the final render with zero blocking frames/snapshots; the contact sheet still mattered because the initial audit did not catch text-anchor drift as a blocking issue.

## Mermaid Block Diagram SVG Unfold

- **Hypothesis**: A small generated Mermaid block diagram reads better when the Mermaid SVG remains an inspectable source artifact, but the video itself is rebuilt as native Manim blocks, receiver slots, connectors, and one active handoff pulse.
- **Result**: Confirmed on `spikes/mermaid-block-svg-unfold/` after replacing generic SVG fragment batches with a 25.9-second native pipeline unfold, then tightening the clip into a title-free slide asset.
- **What worked**:
  - using faint labeled receiver slots during the opening breath so the first frame shows the whole pending pipeline without exposing blank boxes,
  - fading each slot label with its slot as the real colored block lands, which avoids the label/body split caused by generic SVG fragment extraction,
  - giving each next block a red receiver cue before the pulse arrives, then leaving only simple gray arrows and colored cards in the resolved hold,
  - removing the redundant title/subtitle band once the card labels carried the semantics, which reduced top-heavy dead space and cleared the default composition audit,
  - moving the red handoff cue to the card corner instead of the card center, so proof frames no longer put the active dot over text,
  - replacing an enclosing terminal rectangle, long terminal rules, and extra badge text with separated corner brackets around the output card, with enough clearance to avoid actor-to-outline crowding in full-size review.
- **Validation note**:
  - the final 0.3-second composition audit cleared with zero blocking frames, the resting-mobject audit cleared with zero blocking snapshots, and strict crowding overlays still reported repeated outline/actor proximity around the card row; full-size review showed no visible collision after increasing bracket clearance.

## Mermaid Venn SVG Unfold

- **Hypothesis**: A Venn diagram reads better when the generated SVG remains an inspectable artifact, but the video is rebuilt as native Manim circles, prepared slots, and an explicit overlap lens instead of fading generic SVG fragments.
- **Result**: Confirmed on `spikes/mermaid-venn-svg-unfold/` after replacing a mostly static fragment reveal and late rectangle accent with a 26.46-second native Venn composition.
- **What worked**:
  - showing both pending circle slots and the center overlap slot in the first frame, so the opening breath starts with the actual Venn mechanism,
  - activating the left set, right set, and shared lens in sequence with the cue attached to the current slot rather than to a separate route line,
  - removing temporary slot scaffolds before the terminal hold and using separated corner brackets instead of a closed rectangle around the diagram,
  - keeping the raw Mermaid SVG and fragment output generation path intact while making the promoted video use simpler native geometry.
- **Validation note**:
  - strict frame-crowding audits are a poor blocking signal for Venn and overlap diagrams because zero-clearance overlap is the subject. Use them only as full-size review prompts; rely on contact sheets, exact proof-frame inspection, composition audit, and resting-mobject audit for actual acceptance.

## Mermaid Gantt SVG Unfold

- **Hypothesis**: A Mermaid Gantt chart reads better when the generated SVG remains an inspectable source artifact, but the promoted video is rebuilt as a native timeline with visible task slots, a red time cursor, and bars that grow from their actual start dates.
- **Result**: Confirmed on `spikes/mermaid-gantt-svg-unfold/` after replacing generic SVG fragment batches with a 25.53-second native Gantt unfold.
- **What worked**:
  - showing the full pending timeline scaffold during the opening breath, so the first frame is not a blank or sparse fragment state,
  - using a primary-red cursor and dependency markers to explain the day-3 handoff from `Source mmd` into the overlapping downstream work,
  - reducing dense date labels to readable anchor dates while leaving grid columns to carry the intervening days,
  - replacing the full-width terminal outline with separated corner brackets so the resolved hold no longer looks like a frame artifact,
  - nudging the chart system down after the first audit pass so the title plus chart bbox cleared the default center tolerance.
- **Validation note**:
  - the 0.3-second frame composition audit cleared with zero blocking frames after the layout nudge,
  - the strict crowding audit still flags expected scaffold internals and text-inside-bar contacts, so it is useful only as a full-size review prompt for this chart family.

## Mermaid Packet SVG Unfold

- **Hypothesis**: A compact Mermaid packet diagram reads better when the `.mmd`, generated SVG, and fragments remain as inspectable artifacts, but the promoted video is rebuilt as native packet fields instead of generic fragment fades.
- **Result**: Confirmed on `spikes/mermaid-packet-svg-unfold/` after replacing the thin title-heavy SVG unfold with a 25.76-second native packet reveal.
- **What worked**:
  - showing the full two-row packet scaffold during the opening breath so the first frame already explains the byte layout,
  - growing each field body from the left while a single primary-red cursor and active outline prove the bit-range progression,
  - removing the title band and visible backing plate so the packet itself owns the hierarchy,
  - using small gutters between adjacent field bodies and left-inset range labels so full-size review and strict crowding audits do not read packet boundaries or labels as accidental contacts,
  - keeping only separated terminal corner brackets for the final hold instead of enclosing the whole packet in a closed outline.
- **Validation note**:
  - final 0.3-second white-background review frames, full-size proof frames, frame composition audit, frame crowding audit, and resting-mobject audit all cleared with zero blocking findings; WebM metadata reported 25.758 seconds at 1600x900.

## Mermaid Kanban SVG Unfold

- **Hypothesis**: A Mermaid Kanban board reads better when the generated SVG remains inspectable, but the promoted video is rebuilt as a native board with prepared receiver cards and explicit handoff pulses.
- **Result**: Confirmed on `spikes/mermaid-kanban-svg-unfold/` after replacing the generic fragment reveal with a 28.928-second native Kanban board render.
- **What worked**:
  - showing all columns, headers, faint receiver cards, source card, and connector stubs during the opening breath,
  - removing the title/subtitle band so the board itself owns the hierarchy,
  - using one red pulse per handoff and stopping it at the receiver entrance before fading in the destination cards,
  - fading receiver slots out before real cards fade in, because cross-faded slot text and card text made the 4.8-second proof frame unreadable,
  - shortening the lanes and adding restrained bottom lane rails to balance strong-color headers and clear off-center composition audits,
  - using separated terminal brackets around the `Manim video` card instead of a closed outline around the whole board,
  - adding the Manim `--transparent` render flag for the WebM path, because scene opacity alone did not produce alpha metadata.
- **Validation note**:
  - final 0.3-second white-background review frames covered 97 samples; full-size proof frames at the opening, both handoffs, and final hold were reviewed; composition audit reported 0 blocking frames with 3 notice-only handoff frames; resting-mobject audit reported 0 blocking snapshots; WebM metadata reported `alpha_mode=1`, 28.928 seconds, and 1600x900.

## Red Dot Narrative SPA

- **Hypothesis**: A browser-native visual narrative that loops interactively records better when capture mode disables looping, starts with a meaningful first frame, and holds the resolved state after the authored timeline completes.
- **Result**: Confirmed on `spikes/red-dot-narrative-spa/` after adding a recording-only `?capture=1` mode, extending the browser recording to 36 seconds, and clamping playback on the final resolution frame.
- **What worked**:
  - making the first frame show the dot, candidate slots, and route scaffold instead of fading up from near-empty chrome,
  - strengthening the persistent review frame evenly so composition audits center on the intended stage rather than a bottom-heavy shadow,
  - retiring clamp residue before the transformation cards take over, which lets the ring/card system own the proof frames,
  - keeping search target activation on card perimeters, moving echo dots outside closed outlines, and demoting placeholder text lines so strict crowding review does not read candidate internals as active collisions,
  - separating interactive loop behavior from recording behavior so the exported WebM holds the terminal composition instead of sampling the restart.
- **Validation note**:
  - final render was reviewed with 120 frames sampled every 0.3 seconds, full-size proof screenshots including mobile resolution, browser console/page-error validation, composition audit at 0.3-second cadence with 0 blocking frames, and targeted crowding audit at 3.0, 8.2, 14.0, 20.3, 28.6, and 34.0 seconds with 0 blocking frames.

## Timeline Stack

- **Hypothesis**: A timeline stack reads as a staged progression when the initial frame already shows the spine, pending markers, and empty destination slots before any card content arrives.
- **Result**: Confirmed after replacing a 2.1-second quick reveal with a 26.2-second slide-integration render for both wide and portrait variants.
- **What worked**:
  - showing the full timeline scaffold on frame zero and using the opening breath for reading, not for fading in structure,
  - giving each card a prepared slot, then using a single primary-red progress rail, marker, and card accent to make the handoff causal in still frames,
  - switching timeline text to an explicit sans-serif font and square-corner cards so the visual language matches the project default,
  - giving portrait and wide variants separate stage/card sizing while sharing the same timing grammar,
  - adding spike-local audit setup functions so rest-state geometry checks use the same frame aspect ratio as the render command.
- **Validation note**:
  - resting-mobject audits for non-default aspect-ratio renders need matching `config.pixel_width`, `config.pixel_height`, and derived `config.frame_height`; otherwise portrait scenes can falsely report outside-frame objects even when the promoted render is visually safe.

## Step Reveal Sequence

- **Hypothesis**: A slide-sequence loop reads as a mechanism instead of a moving dot when the opening frame already shows source states, receiver slots, and quiet route scaffolds.
- **Result**: Confirmed after replacing 2.9-3.6 second single-dot loops with 28.3-32.9 second staged reveal videos.
- **What worked**:
  - showing all source cards, empty receiver slots, and faint route guides during the opening breath, so the viewer can read the pending handoffs before motion starts,
  - using one primary-red pulse to activate each route while the settled states use green, blue, and purple as quiet categorical actors,
  - moving the completed receiver stack to the resolved center before the final hold, which keeps the ending from feeling stranded in the old transfer layout,
  - fading the traveling pulse during cleanup before drawing the final outline or terminal arrow, so the cleanup proof frames do not contain a disconnected red dot,
  - choosing an installed fallback font when Open Sans is unavailable, so local renders stay clean without repeated font warnings,
  - clearing the spike-local Manim staging directory per variant and promoting by newest modified time so stale cached renders do not contaminate review.
- **Validation note**:
  - broad composition audits can pass while a small pulse still reads as residue in full-size transition frames; inspect cleanup frames at full size before accepting final-outline or terminal-arrow beats.

## Mermaid Layout Gallery Device Frame Loop

- **Hypothesis**: A device-frame embed reads more clearly when the transparent Manim asset animates only the app content and does not duplicate the surrounding Slidev/browser frame.
- **Result**: Confirmed after replacing the static nested frame and short checkout loop with 27.0-second wide and portrait content-only handoff videos.
- **What worked**:
  - removing the internal device shell because the Slidev layout already supplies the browser/device frame,
  - showing source cards, processor and receipt slots, faint routes, and the active pulse during the opening breath so transparent whitespace reads as pending UI structure,
  - using a visible red route pulse across staged square UI states so the mechanism survives 0.3-second still frames,
  - keeping the receipt slot blank until the pulse reaches it, then replacing the slot with the resolved confirmation card to avoid ghost text during the handoff,
  - removing routes and the pulse before the final hold, then using separated corner brackets around the receipt instead of a closed terminal rectangle,
  - adding spike-local audit setup functions for the wide and portrait Manim frame shapes so rest-state checks match the actual render geometry,
  - clearing the fixed Manim staging directory before the promoted render and promoting by newest modified time so stale cached outputs do not enter review.
- **Validation note**:
  - for transparent loop embeds, extract alpha-on-white frames with a VP9/libvpx decode path; PyAV-only review can show black backgrounds and hide the real slide embed behavior,
  - poster images need a rerender whenever the terminal state changes, because Slidev uses them as the first inspectable still inside the browser/device frame.

## Diagram SVG Video Manipulation Polish

- **Hypothesis**: A generated diagram remap reads more like an authored video when semantic SVG actors are larger, target scaffolds explain only the remap, and the route pulse owns a clean stage afterward.
- **Result**: Confirmed after enlarging the actors, replacing the broad destination hint with three target slots, moving slot cleanup before the route pulse, and adding a terminal outline around the resolved video node.
- **What worked**:
  - using specific destination slots instead of one large faint box, so the remap has visible receivers without creating a dead central panel,
  - fading destination slots before the route pulse, so the pulse proof frames do not read as actor-to-outline crowding,
  - keeping native Manim connectors but ending them just outside node bodies, which preserves graph direction while reducing connector overlap,
  - using a red pulse and terminal outline as the active accent against categorical green, blue, and purple nodes.
- **Validation note**:
  - strict crowding audits can still flag graph connector-to-node proximity or pulse-on-route contact; inspect the overlays full size and reserve blocking status for contacts that obscure actors or leave scaffolds after their causal beat.

## Quadrant Arrow Drop

- **Hypothesis**: A selected point in a quadrant diagram reads as intentionally repositioned when the cost-drop cue is vertical, held before motion, and separated from the later horizontal target slot.
- **Result**: Confirmed after replacing a short diagonal arrow pass with a 27.7-second staged drop-and-slide.
- **What worked**:
  - starting with a visible quadrant board instead of a blank opening frame,
  - making the red cue a true vertical drop arrow and holding it long enough to survive 0.3-second review frames,
  - reserving the future destination with a yellow target slot and a low-opacity orange rail,
  - removing the arrow before the point moves, so the cue reads as cause rather than as a simultaneous drag handle,
  - shrinking the outer review frame until the resting mobject audit cleared edge safety margins.
- **What failed first**:
  - a 2.86-second render was too short for slide integration,
  - the diagonal arrow read as a generic route instead of a cost-drop mechanism,
  - the first outer frame was technically visible but still too close to the camera edge for the resting audit.

## Repo-wide Generated Video Color-System Pass

- **Hypothesis**: Older utility spikes would read more clearly if every generated video used the ADR-0002 palette as semantic roles instead of generic Manim color constants.
- **Result**: Confirmed after a repo-wide render and contact-sheet review.
- **What worked**:
  - replacing one-note blue and default black/gray usage with green, blue, and purple structural actors,
  - reserving orange for paths, bridges, arrows, and other causal guide geometry,
  - reserving yellow for transient pulses, cores, halos, and focus marks,
  - adding a local `page-background` stage behind text-heavy transparent clips so they remain readable over dark review backgrounds,
  - reviewing all 86 promoted WebM outputs plus 3 legacy MP4 compatibility outputs as contact sheets, which exposed cramped top titles and stale exports that were not obvious from source code,
  - separating decorative transparent loops from explanatory clips, so only videos with labels or diagram text gained local backing panels.
- **What failed first**:
  - poster-only background colors did not help transparent WebM frames during video review,
  - some older scripts had readable motion but weak semantic color separation,
  - widening or adding local stage panels changed the perceived margins, so title placement needed another pass.

## Quality Deformation Flow

- **Hypothesis**: Shape deformation with stable colors will read better than text-heavy explanation cards.
- **Result**: Confirmed again after expanding the draft into a 25.4-second slide-integration scene with a visible opening breath, red squeeze gate, staged receiver handoffs, cleanup, and centered final hold.
- **What worked**:
  - showing source capsules, open receiver marks, and the red gate in the first frame, so the opening breath starts with meaningful structure,
  - making each capsule compress inside the gate before it becomes a node, so the deformation survives in 0.3-second still frames,
  - using open bracket receiver marks instead of full circular outlines, which avoids actor-to-outline crowding after a node lands,
  - retiring each completed receiver mark immediately and removing the gate before the final hold,
  - recentering the resolved stack after source cleanup and leaving only the colored nodes plus short orange connectors.
- **What failed first**:
  - the legacy version was only about 6.0 seconds and had no real slide-integration pacing,
  - the opening started almost blank because structure faded in after the first frame,
  - a tiny detached pulse read as residue rather than mechanism,
  - closed slot outlines and behind-node guide spines created strict actor-to-outline crowding,
  - the staged layout needed several center adjustments because source rails, gate, and target receivers changed the active balance at different beats.

## Quality Pulse Routing

- **Hypothesis**: One moving accent through mostly calm structure feels more premium than having all elements animate at once.
- **Result**: Confirmed.
- **What worked**:
  - one yellow pulse moving through gray infrastructure,
  - station colors from the primary palette,
  - rings and light shadows for depth without visual noise,
  - a final highlight on the destination node.
- **What to keep**:
  - keep the path calm and let the accent motion do the storytelling.

## Quality Layered Reveal

- **Hypothesis**: Asymmetry and layered depth make the result feel more intentional than a centered generic diagram.
- **Result**: Confirmed again after expanding the short draft into a 25.5-second slide-integration scene with visible opening structure, hollow destination slots, lane-sized red gate apertures, staged layer handoffs, cleanup, and a centered final hold.
- **What worked**:
  - showing source cards, faint destination slots, guide lanes, and the reveal gate before the opening breath, so the first sampled frame is already meaningful,
  - compressing each active layer into a lane-sized aperture before releasing it to the target, which makes the reveal device visible in still frames instead of looking like a passive divider,
  - using one active route per layer and then transforming only that active layer, which keeps the mechanism readable in still frames,
  - widening the resolved cluster and recentering the final panel after support cleanup, so the hold reads as a resolved composition rather than a small knot in leftover transfer space,
  - removing slots, guides, gate, ghost history, and source field before the final hold, so the resolved cluster owns the last frame,
  - shrinking neutral backing strips until the resting mobject audit cleared edge margins.
- **What failed first**:
  - the legacy version was only about 5.8 seconds and had no real final hold,
  - fading the initial cards in made the earliest review frames feel too blank for a slide-integration scene,
  - applying opacity to a stroke-only target-slot group filled the slots and made them read as unfinished actors,
  - the full-width decorative strip was visually subtle but still failed rest-state edge clearance.

## Quality Negative Space Focus

- **Hypothesis**: Premium-looking motion can come from controlling where nothing happens, not only where motion happens.
- **Result**: Confirmed after enlarging the landing zone.
- **What worked**:
  - one soft active window on the left for the source state,
  - faint destination slots during the opening breath, so the right-side negative space read as reserved instead of empty,
  - staged one-route-at-a-time pulse travel, with each source tile transforming only after its path was activated,
  - removing each completed route scaffold once and avoiding a later parent-group `FadeOut`, because fading the parent group after child cleanup reintroduced faint route lines as residue,
  - explicit layer ordering for animated backing panels, which kept the destination panel from washing over the final colored actors,
  - removing the abandoned source panel before the resolved hold, leaving negative space instead of a ghost container,
  - recentering the resolved destination cluster after source cleanup, so the final hold kept intentional quiet space without stranding the active zone on the old right-side lane,
  - using a brief perimeter focus cue instead of a lingering accent dot, then removing it before the final hold,
  - a delayed transfer to a second active window on the right,
  - a landing cluster that stayed compact but not timid,
  - large negative space that remained intentional instead of empty.
- **What failed first**:
  - the first landing cluster was too small,
  - the active zone was too weak to justify the empty space around it,
  - the first render was only 6.3 seconds and opened before the source actors were visible,
  - animating the destination backing panel without explicit z-order let it overlay and desaturate the final actors,
  - leaving a faded source panel in the final hold read as residue rather than deliberate quiet space,
  - fading the route scaffold parent after fading individual child guides made the routes briefly reappear during cleanup.

## Quality Mask Transfer

- **Hypothesis**: A traveling mask band can make a reveal feel more authored than plain fade-ins.
- **Result**: Confirmed again after expanding the draft into a 31.8-second slide-integration scene with visible opening structure, staged mask passes, scaffold cleanup before compaction, and a clean final hold.
- **What worked**:
  - a neutral vertical band that acts as a reveal device,
  - top-row chips as a source state and circles as a distilled target state,
  - faint matching-color stroke-only destination slots during the opening breath, so the lower row reads as pending structure and stays part of the saturated composition audit,
  - a faint exit gate that balances the opening breath, then disappears before the band reaches it so strict crowding review does not see two guides colliding,
  - stopping the mask at multiple proof beats so each revealed circle has a readable cause,
  - removing the source row and route lines before the exit sweep, then removing the target slots, band, and active accent before the compact landing morph, so cleanup frames do not inherit source stems, guide collisions, or accent residue,
  - diagonal compact landing with clear size hierarchy and enough actor spacing for the final hold.
- **What failed first**:
  - the legacy draft was only 5.496 seconds and opened on a mostly empty frame,
  - the band was too wide,
  - the first compact cluster felt muddy,
  - ghost chips were too visible and competed with the landing state,
  - leaving the source row and yellow accent during the compacting morph created strict actor-to-actor clearance failures even after the broad composition audit passed.

## Quality Rhythm Gating

- **Hypothesis**: Timed gates can make a simple transform feel choreographed instead of merely sequential.
- **Result**: Confirmed after reducing gate dominance.
- **What worked**:
  - three beat markers that stage the motion,
  - one accent pulse moving through each gate,
  - a final landing that is cleaner than the gated buildup,
  - gate opacity low enough that structure wins over decoration.
- **What failed first**:
  - the gates were too visually heavy,
  - the final cluster needed to be stronger so the beat structure felt justified.

## Quality Counterweight Balance

- **Hypothesis**: Opposing transforms can add tension and control without increasing scene complexity.
- **Result**: Confirmed.
- **What worked**:
  - left shapes and right shapes changing category in opposite directions,
  - two soft fields to hold each side of the composition,
  - one accent moving between the fields to connect the exchange,
  - a final frame where both sides still feel distinct.
- **What to keep**:
  - counter-motion is useful when both sides keep different visual roles instead of converging into one cluster.

## Quality Scale Hierarchy

- **Hypothesis**: A premium frame can become clearer when one element owns the composition by size and the rest become supporting marks.
- **Result**: Confirmed.
- **What worked**:
  - one dominant green circle that immediately establishes the focal point,
  - secondary blue and purple shapes that stay clearly subordinate,
  - a large soft zone that reinforces the destination hierarchy,
  - a final frame that reads in one glance.
- **What to keep**:
  - make the main shape clearly larger, not just slightly larger, when testing hierarchy.

## Quality Anchored Orbit

- **Hypothesis**: Orbit-like paths around a stable anchor feel more designed than direct linear rearrangement.
- **Result**: Confirmed.
- **What worked**:
  - one stable green anchor,
  - a visible source stage and faint target slots during the opening breath, so the destination zone reads as reserved structure instead of dead space,
  - orbit arcs used only during motion and removed afterward,
  - separating upper and lower orbit paths enough that the second satellite does not crowd the first at the proof frame,
  - satellites landing in positions that still respect the anchor,
  - a final frame with anchor plus orbit residue implied by placement rather than by visible guides.
- **Validation note**:
  - targeted crowding audits can flag intentional actor-on-path contact in orbit scenes; inspect those frames full size and reserve blocking status for actor-to-actor crowding, actor-to-outline collisions, or guides that hide the actor.
- **What to keep**:
  - orbital scaffolding should disappear before the ending frame so the destination state stays clean.

## Quality Compression Release

- **Hypothesis**: A scene that visibly compresses before it resolves will feel more intentional than a direct source-to-target transform.
- **Result**: Confirmed after tightening the compression cluster and simplifying the landing.
- **What worked**:
  - a short compression beat before the release,
  - a final cluster with clear size hierarchy inside one soft destination zone,
  - one yellow accent that arrives before the structural release instead of competing with it,
  - a long orange guide that is still simple enough to read as directional pressure.
- **What failed first**:
  - the compression phase was too loose,
  - the release cluster was not decisive enough,
  - the early guide path felt more like a leftover line than a staging device.

## Quality Edge Tension

- **Hypothesis**: A landing composition pushed near the boundary can feel more dynamic than a comfortable centered landing, as long as clipping never becomes accidental.
- **Result**: Confirmed after moving the target mass closer to the boundary and adding a brief overshoot.
- **What worked**:
  - a dominant green landing shape very near the right edge,
  - a small overshoot before the settle so the edge pressure feels earned,
  - a narrower destination zone that makes the right boundary matter,
  - adding faint destination slots and a temporary red pressure wall during the opening breath, so the edge reads as a pending surface before the actors arrive,
  - holding the overshoot against the wall long enough to survive 0.3-second proof frames,
  - removing the abandoned source panel during cleanup, leaving quiet negative space instead of an empty container,
  - minimal supporting shapes that still keep the cluster legible.
- **What failed first**:
  - the draft was only 3.43 seconds and had no real slide-integration pacing,
  - the first version ended on the right side without real tension,
  - the destination cluster was too timid,
  - the first long rerender left an empty source panel in the resolved hold,
  - the wide soft zone weakened the sense of pressure.

## Quality Occlusion Peel

- **Hypothesis**: Temporary overlap can make a transform feel richer if one layer clearly peels away and the landing frame removes that overlap completely.
- **Result**: Confirmed after making the peel phase more pronounced and removing guide residue from the landing.
- **What worked**:
  - a front layer that briefly dominates and then exposes the rear layer,
  - overlap that is readable because the color roles remain distinct,
  - an early guide that disappears before the resolved frame,
  - a final cluster that is compact and fully separated.
- **What failed first**:
  - the peel was too subtle,
  - the first landing still carried too much guide residue,
  - the occlusion read as generic stacking instead of deliberate reveal.

## Quality Hinge Pivot

- **Hypothesis**: Rotation around a believable anchor can feel more designed than direct translation when the anchored motion is visible long enough to register.
- **Result**: Confirmed after shortening the guide and removing the anchor before the final landing.
- **What worked**:
  - one dominant green arm that rotates through the center of the stage,
  - a visible hinge point during motion and no hinge residue afterward,
  - supporting blue and purple elements that follow the pivot rather than competing with it,
  - a resolved final cluster that still hints at the earlier rotation.
- **What failed first**:
  - the first guide was too long,
  - the hinge marker stayed visible too late,
  - the motion risked reading as normal repositioning instead of pivot-driven choreography.

## Quality Echo Settle

- **Hypothesis**: A scene can feel more authored if the dominant form lands first and the secondary forms settle a beat later instead of stopping all at once.
- **Result**: Confirmed after increasing the secondary overshoot and simplifying the guide usage.
- **What worked**:
  - the green dominant form landing first,
  - blue and purple supports overshooting and then settling back,
  - guide removal before the delayed settle so the timing difference becomes the main idea,
  - a final cluster that still looks resolved instead of staggered.
- **What failed first**:
  - the initial landing looked too much like a normal cluster,
  - the delayed settle was too subtle,
  - the guide lingered long enough to compete with the timing idea.

## Quality Fan Splay

- **Hypothesis**: A landing that opens into a controlled angled fan can feel more premium than a compact circular cluster.
- **Result**: Confirmed after increasing the separation and angle clarity of the final forms.
- **What worked**:
  - a narrow approach before the opening move,
  - three final forms that keep clear directional differences,
  - enough spacing that the fan shape reads immediately,
  - a landing that stays structured even with minimal text and no extra labels.
- **What failed first**:
  - the first fan arrangement was too close to a generic tilted stack,
  - the final spacing was too timid,
  - the ending needed a clearer top-to-bottom sweep.

## Quality Shear Resolve

- **Hypothesis**: A brief sheared intermediate state can make a transform feel more designed than a clean direct handoff.
- **Result**: Confirmed after increasing the diagonal angle and compressing the final landing.
- **What worked**:
  - one clear shared diagonal across all forms during the stressed intermediate frame,
  - stronger angle contrast between the source and the sheared state,
  - guide removal before the final resolve so the diagonal beat becomes the main idea,
  - a simpler circular landing that contrasts clearly with the sheared geometry.
- **What failed first**:
  - the first shear was too polite,
  - the diagonal relationship between forms was not strong enough,
  - the motion risked reading as a normal transform with minor tilt.

## Quality Aperture Open

- **Hypothesis**: A neutral aperture opening can make a reveal feel authored if the shutters disappear before the resolved frame.
- **Result**: Confirmed again after turning a 4.1-second draft into a 26.0-second slide-integration scene with a visible opening breath, sustained aperture proof frames, and a clean final hold.
- **What worked**:
  - neutral shutters that create a clear before-and-after reveal state,
  - showing source shapes and faint destination slots during the opening breath instead of starting on an empty frame,
  - a compact reveal stage inside the aperture before the final transform,
  - carrying the active accent into the landing instead of leaving it at the old guide edge,
  - recentering the destination stage after the source zone disappears, so the resolved hold owns the frame,
  - full shutter removal before the resolved frame,
  - a final landing that stays cleaner than the reveal mechanics.
- **What failed first**:
  - the draft was far below the 25-second pacing floor and had no real final hold,
  - the first reveal still looked like a normal transition with extra props,
  - the reveal shapes stayed too close to the final state,
  - the target cluster initially stayed too far right after source cleanup,
  - the accent dot briefly read as residue when it did not travel with the landing,
  - the aperture needed stronger opening separation to feel intentional.

## Quality Snap Recoil

- **Hypothesis**: A decisive arrival followed by a short recoil can feel sharper and more intentional than a perfectly smooth settle.
- **Result**: Confirmed again after expanding the draft into a 25.9-second slide-integration scene with visible opening structure, a held overshoot proof beat, separated support settle, and a recentered final hold.
- **What worked**:
  - the dominant green form arriving first with a visible overshoot,
  - showing faint target slots and a pressure wall during the opening breath, so the destination zone reads as pending structure instead of empty space,
  - holding a stretched overshoot near the wall long enough to survive 0.3-second proof-frame review,
  - a quick recoil into the final landing position,
  - retiring target slots before the support settle so slot outlines do not become actor-to-outline crowding,
  - support forms resolving afterward so the snap remains the main beat,
  - keeping clear space between the support forms and the pressure wall in the settle frame,
  - recentering the target stage after source cleanup,
  - a final frame that still feels stable despite the sharper motion.
- **What failed first**:
  - the draft was far below the 25-second pacing floor and had no visible opening breath,
  - the first overshoot was too small,
  - the snap risked reading like a normal arrival,
  - the recoil needed more contrast against the final settled position,
  - passive target slots and a too-near pressure wall triggered strict crowding findings after the main mechanism had already landed.

## Quality Bumper Deflect

- **Hypothesis**: A visible bumper should make a redirection feel more authored if the leader clearly compresses against it before the landing.
- **Result**: Confirmed again after expanding the draft into a 26.9-second slide-integration scene with visible opening structure, a held bumper-contact proof beat, and a clean final hold.
- **What worked**:
  - the green leader reaching the bumper before the blue and purple supports move,
  - a long enough orange bumper that the deflection surface remains legible in still frames,
  - a compressed, slightly tilted contact shape for the leader,
  - support forms arriving later so the contact frame stays uncluttered,
  - retiring passive destination slots before the release so they do not crowd the landing,
  - moving support forms into separated lanes before the final morph so they do not cross through each other in 0.3-second proof frames.
- **What failed first**:
  - the first version spread the support forms too early,
  - the contact frame did not show enough compression,
  - the bumper existed but did not yet feel like the cause of the turn,
  - leaving destination scaffolds visible during release triggered actor-to-outline crowding and made the landing look unfinished,
  - letting a support form travel through another actor during the release looked acceptable in motion but failed the targeted crowding audit.

## Quality Counterlift Balance

- **Hypothesis**: A counterlift should feel more deliberate if a visible beam tilts while one side rises and the other drops.
- **Result**: Confirmed again after expanding the draft into a 25.17-second slide-integration scene with a visible setup, curved setup paths, held counterlift proof, cleanup, and final hold.
- **What worked**:
  - the orange beam tilting enough to read as load transfer instead of decoration,
  - the green leader rising on one end while the blue support drops on the other,
  - a yellow pivot that stays visible through the proof frame,
  - using faint receiver marks in the opening breath so the rise/drop lanes are prepared before motion,
  - curving setup handoffs around the beam so actors do not cross the support surface in sampled frames,
  - keeping the purple counter actor in a separate pocket near the pivot instead of letting the beam cut through it,
  - removing broad pale staging panels and retiring the beam before the final cluster, so the hold has no support residue.
- **What failed first**:
  - the original render was only 2.47 seconds and had no opening breath or final hold,
  - the first version kept the beam too static,
  - the opposing motions looked like regrouping instead of weighted exchange,
  - the support roles were too close together to read as separate ends of a mechanism,
  - broad pale target panels created noisy strict-crowding findings because the audit treated them as one support envelope behind the actors.

## Quality Fork Diverge

- **Hypothesis**: A split should feel authored if the leader reaches a visible fork before the branches separate.
- **Result**: Confirmed after increasing branch separation and keeping the trunk stable through the proof frame.
- **What worked**:
  - one clear trunk feeding two visibly different branch angles,
  - a shorter green leader that stays attached to the fork while the children separate,
  - upper and lower branch forms far enough apart to read as divergence rather than staggering,
  - a proof frame where the fork geometry is still visible around all three forms.
- **What failed first**:
  - the first branch spacing was too timid,
  - the split looked too much like a regroup around one central shape,
  - the fork geometry needed to remain visible longer during the separation.

## Quality Magnet Capture

- **Hypothesis**: A receiver should feel like it captures if the pocket stays visible while the leader stretches into it.
- **Result**: Confirmed again after turning the draft into a 29.9-second slide-integration scene with a visible opening breath, held capture proof frames, and a clean centered final hold.
- **What worked**:
  - showing the source state, receiver pocket, target slots, and magnet core during the opening breath instead of starting with a late receiver reveal,
  - a stretched green leader that becomes visibly compressed inside the open pocket before support forms move,
  - fading target slots and field rails as soon as the leader has proved the capture, so support-hand-off frames do not inherit guide residue,
  - shifting the receiver stage toward center before the delayed supports arrive, which avoids a long off-center hold after the source panel disappears,
  - using a broken receiver bracket with enough stroke gaps for strict crowding audits to measure real clearances instead of one large U-shaped bounding box,
  - fading the receiver and magnet core before the final landing morph, so the resolved hold has no actor-to-guide or actor-to-actor cleanup contact.
- **What failed first**:
  - the original render was only 2.864 seconds and had no slide-integration pacing,
  - the first receiver looked decorative instead of causal,
  - the leader crossed the receiver too completely and lost the sense of being pulled inward,
  - support forms arrived too early and diluted the capture beat,
  - leaving target slots, field rails, or the red core into later beats created strict crowding failures even when the broad composition audit passed.

## Quality Merge Funnel

- **Hypothesis**: A merge should feel authored if multiple inputs visibly compress through a narrowing funnel before resolving into one dominant output.
- **Result**: Confirmed after tightening the funnel neck and compressing the intermediate stack.
- **What worked**:
  - a visibly narrowing orange funnel with a small outlet,
  - three compressed mid-state forms stacked tightly enough to read as forced convergence,
  - a proof frame where the funnel still surrounds the stacked inputs,
  - a dominant green landing that feels like the outlet result rather than a new unrelated shape.
- **What failed first**:
  - the first neck was too wide,
  - the intermediate stack was too relaxed to feel squeezed,
  - the outlet pressure was not obvious enough in still frames.

## Quality Sleeve Reveal

- **Hypothesis**: A reveal should feel controlled if the dominant form slides through a visible sleeve and emerges cleaner on the far side.
- **Result**: Confirmed after moving the sleeve deeper over the leader and tightening the mid-state form.
- **What worked**:
  - a sleeve shape that remains visible around the leader during the proof frame,
  - a narrower green mid-state that feels contained instead of simply translated,
  - a yellow core that stays inside the sleeve while the reveal happens,
  - support forms arriving later so the covered-pass-through remains the main beat.
- **What failed first**:
  - the first sleeve sat too far from the leader,
  - the leader was too wide and made the sleeve feel decorative,
  - the reveal beat was too close to a normal slide-in.

## Quality Staged Convergence

- **Hypothesis**: Converging through a narrow shared lane can feel more choreographed than collapsing directly into the final cluster.
- **Result**: Confirmed again after expanding the short draft into a 25.6-second transparent slide-integration scene with a visible opening scaffold, a held compressed-lane proof, cleanup of route and slot guides, and a centered 8.1-second final hold.
- **What worked**:
  - a visible narrow lane that all forms pass through,
  - strong contrast between the staged lane and the circular landing,
  - enough compression in the lane to make the second release feel earned,
  - guide removal before the final convergence so the staging geometry owns the intermediate beat,
  - using open lane rails instead of a closed outline, because a closed box reads as a support envelope around every compressed actor in strict crowding review,
  - retiring the red cue before the lane proof and letting the final release be carried by the actors, so the proof frame does not inherit route residue.
- **What failed first**:
  - the first lane was too loose,
  - the convergence looked too close to a direct transfer,
  - the intermediate stage needed stronger compression to justify its existence,
  - keeping the active cue on the lane rail made the held proof read as actor-to-guide contact,
  - a closed lane outline and late red release cue generated strict crowding prompts that were visible enough to simplify.
- **Validation note**:
  - final review used 86 extracted 0.3-second white-background frames, full-size opening/lane/release/final proof-frame inspection, frame composition audit with zero blocking frames across 86 samples, resting-mobject audit with zero blocking snapshots across 3 rest states, VP9 `alpha_mode=1`, and decoded alpha range `0..255`. The strict crowding audit still reported 11 transition prompts during actor remaps; full-size overlays showed expected transform contact rather than persistent final-frame crowding.

## Quality Arc Handoff

- **Hypothesis**: A dominant form can feel more authored if it transfers along a visible curve before the rest of the composition catches up.
- **Result**: Confirmed again after expanding the draft into a 27.6-second slide-integration scene with a visible opening breath, sustained arc proof frames, delayed support travel, and a centered final hold.
- **What worked**:
  - one strong orange arc that survives long enough to be legible,
  - the dominant green form arriving along that curve before the support forms resolve,
  - faint destination slots during the opening breath so the target zone reads as pending structure,
  - delayed gray support arcs that appear only after the dominant handoff is established,
  - removing the outer frame and source zone during cleanup, then recentering the final cluster with its target field,
  - a final cluster that contrasts with the earlier curved path,
  - minimal supporting motion so the handoff remains the main beat.
- **What failed first**:
  - the 2.9-second draft was far below the slide-integration pacing floor,
  - the first sampled frame had no meaningful mechanism breath,
  - the first arc disappeared too soon,
  - the motion looked like a normal transfer with curved decoration,
  - the intermediate handoff position needed to be more distinct from the final landing,
  - after source cleanup, the final cluster initially remained too far right and failed off-center audits until it was shifted toward the middle.

## Quality Corridor Squeeze

- **Hypothesis**: Passing through a constrained corridor can create a stronger sense of authored compression than a normal free-space approach.
- **Result**: Confirmed after narrowing the squeeze phase and keeping the compressed state more explicit.
- **What worked**:
  - a visibly compressed three-form stack inside one narrow corridor,
  - enough contrast between the squeezed phase and the later circular landing,
  - neutral corridor geometry that supports the compression without competing for attention,
  - a final release that feels earned because the squeeze stage is real.
- **What failed first**:
  - the first corridor was too loose,
  - the squeeze looked too close to an ordinary intermediate cluster,
  - the constrained phase needed stronger reduction in height to register in still frames.

## Quality Weave Crossing

- **Hypothesis**: A controlled foreground crossing can feel more authored than parallel lateral movement if one form clearly owns the weave moment.
- **Result**: Confirmed after keeping the curved path visible through the transfer and separating the support forms more clearly.
- **What worked**:
  - one orange path that remains visible during the actual crossing beat,
  - a dominant green form landing above the blue support so the hierarchy stays readable,
  - a smaller purple support kept low enough to avoid muddy overlap,
  - a final circular cluster that is calmer than the weave moment.
- **What failed first**:
  - the first crossing read too much like a normal transfer with decoration,
  - the support forms were too close together,
  - the path was not present long enough to justify the weave idea in still frames.

## Quality Latched Anchor

- **Hypothesis**: A visible latch point can make a transfer feel more intentional if the dominant form briefly locks to it before the rest of the cluster resolves.
- **Result**: Confirmed after moving the latch out of the overlap zone and sampling the hold frame where the anchor is still visible.
- **What worked**:
  - a distinct orange latch marker separated from the dominant form instead of hidden under it,
  - one short guide that points into the latch without becoming the main subject,
  - a hold state where the green form sits visibly latched before the final circular landing,
  - full removal of the latch before the resolved frame so the ending remains clean.
- **What failed first**:
  - the latch was swallowed by the green and blue forms,
  - the anchor was present in motion but not legible in the sampled stills,
  - the composition needed a clearer point of contact instead of just proximity.

## Quality Parallax Transfer

- **Hypothesis**: Shallow parallax can make a transfer feel more premium if the dominant form advances earlier and farther than the supporting forms.
- **Result**: Confirmed after increasing the lead distance of the green form and holding the support forms farther back.
- **What worked**:
  - a dominant green form that claims the forward position first,
  - blue and purple supports kept clearly behind that lead move instead of traveling in lockstep,
  - one curved orange route that stays visible through the depth beat,
  - a final landing that simplifies the earlier stagger into one coherent cluster.
- **What failed first**:
  - the first parallax pass was too polite and read like a normal regroup,
  - the support forms traveled too neatly with the leader,
  - the depth beat needed more separation to survive still review.

## Quality Slot Docking

- **Hypothesis**: A visible receiving slot can make a landing feel authored if the dominant form briefly compresses into it before the final resolve.
- **Result**: Confirmed again after expanding the draft into a 28.8-second slide-integration scene with visible opening structure, a held constrained slot proof, and a centered final hold.
- **What worked**:
  - an open receiving slot that reads as a real target instead of a decorative frame,
  - a hold frame where the green form is visibly docked while the blue and purple supports remain below or outside the entrance,
  - a short guide that leads into the receiver without overpowering the scene,
  - red pressure ticks at the slot mouth, which make the constrained phase read before the resolve,
  - full removal of the docking rails before the resolved landing,
  - recentering the resolved local stage after the source zone disappears, which prevents the final hold from feeling stranded in the old right-side target zone.
- **What failed first**:
  - the draft was only 3.096 seconds and opened on a blank sampled frame,
  - the original slot looked too closed and generic,
  - the first dock state did not separate the receiver from the support forms strongly enough,
  - the mechanism needed a more obvious entrance to read in still frames,
  - strict crowding audits treat a hollow receiver as one bounding box around the docked actor, so the overlay must be inspected full size before counting the slot as actor-to-outline collision.

## Quality Bridge Span

- **Hypothesis**: A temporary bridge can make a transfer feel more intentional if the dominant form clearly crosses a supported passage instead of drifting through empty space.
- **Result**: Confirmed again after expanding the draft into a 29.7-second slide-integration scene with visible opening structure, a held bridge-crossing proof frame, and a centered resolved hold.
- **What worked**:
  - using square-corner geometry and canonical palette tokens so the bridge reads as structure rather than decoration,
  - showing faint destination slots during the opening breath so the right side reads as pending structure,
  - a horizontal bridge that stays visible on both sides of the crossing form,
  - open bridge rails that stop at the receiver entrance instead of touching the target slot, which keeps strict crowding review from reading one closed outline around the actor,
  - a small red guide that travels above the bridge with clear air from both the rails and the green actor,
  - a hold frame where the green form is clearly on the bridge rather than merely near it,
  - blue and purple supports kept lower and released in separate beats so they do not compete with the crossing beat or collide with each other,
  - fading the used green receiver slot with the bridge, before the support release,
  - bridge removal before the final cluster so the ending stays clean,
  - recentering the resolved local stage after the source zone disappears so the final hold does not stay stranded in the old transfer layout.
- **What failed first**:
  - the draft was only 3.096 seconds and had no useful final hold,
  - the first bridge read like an orange bar instead of a supported crossing,
  - the green form was too large and swallowed the mechanism,
  - the passage needed visible separation above and below the crossing form,
  - connected bridge ends and target slots became one structural component in strict crowding review,
  - a red guide riding on top of the green actor looked like a stain instead of an active guide,
  - simultaneous support release made blue and purple cross too tightly in still-frame review,
  - leaving the final cluster in the old right-side target zone created dead space after source cleanup.

## Quality Keystone Lock

- **Hypothesis**: A support-built pocket can make a landing feel more designed if the dominant form visibly enters that notch before the final resolve.
- **Result**: Confirmed after turning the purple support into a vertical side wall and sampling the later hold frame where the green form is visibly nested into the pocket.
- **What worked**:
  - a blue base plus purple side wall that clearly assemble the receiving pocket,
  - a smaller green form that can visibly enter the notch without hiding it,
  - a guide that points into the pocket without becoming the main subject,
  - a final landing that removes the assembly logic after the lock has been established.
- **What failed first**:
  - the first pocket arrangement looked like a loose regroup,
  - the green form stayed too far from the support-built receiver,
  - the correct proof frame was later than the first sampled hold frame.

## Quality Throat Gate

- **Hypothesis**: A narrow throat can make a passage feel more authored if the dominant form visibly compresses through it before the final resolve.
- **Result**: Confirmed after widening the gate bars, shrinking the green form further, and moving the support forms away from the throat. Reconfirmed in the 2026-05-02 polish pass after expanding the clip into a 25.9-second red-and-gray slide-integration scene with a visible opening breath, a held throat proof, cleanup, recentering, and a 6.2-second final hold.
- **What worked**:
  - two longer orange bars that create a clear gated throat,
  - a compressed green form that is visibly thinner while passing between them,
  - support forms positioned away from the squeeze so the gate owns the frame,
  - gate removal before the resolved landing,
  - using one primary-red actor and grayscale supports so the throat mechanism owns the hierarchy,
  - keeping the broad stage frame through the recentering transition, then removing it at the final-hold boundary instead of fading it through the cluster.
- **What failed first**:
  - the first gate bars looked too isolated and the squeeze was not tight enough,
  - the support forms were too close to the mechanism,
  - the green form needed stronger compression to read in still frames,
  - removing the broad frame before recentering caused off-center cleanup audit failures, while fading it through the cluster caused stray edge-fragment notices.
- **Validation note**:
  - the final 2026-05-02 render was reviewed with 87 alpha-on-white frames sampled every 0.3 seconds, full-size opening/squeeze/final proof frames, a 0.3-second composition audit with zero findings, and a resting-mobject audit with zero blocking snapshots.

## Quality Relay Handoff

- **Hypothesis**: A support-to-support relay can make the final regroup feel more designed if the accent clearly passes from one support role to another before the dominant form arrives.
- **Result**: Confirmed again after expanding the draft into a 25.5-second slide-integration scene with visible opening pads, held support-to-support proof frames, delayed green arrival, cleanup, and a recentered final hold.
- **What worked**:
  - a two-segment relay path that gives the handoff a visible first and second leg,
  - a proof frame where the blue support, purple support, and accent define the relay before the green form fully joins,
  - a delayed green arrival so the support handoff has its own beat,
  - showing the receiver pads and faint guide legs during the opening breath, so the empty target side reads as prepared structure instead of dead space,
  - using separated corner-bracket receiver pads with real clearance around settled actors, so strict crowding review reads them as prepared pockets instead of actor-to-outline collisions,
  - shortening the final relay leg into a freestanding gate between support stages when a full line would pass under the arriving green actor,
  - fading the traveling baton before the rectangle-to-circle cleanup and using a perimeter terminal pulse, which keeps the final regroup free of stray accent residue,
  - removing the source frame, pads, and relay lines before the final morph, then recentering the resolved cluster so the long hold does not inherit the old left-to-right layout.
- **What failed first**:
  - the original relay read too much like a normal guide line,
  - the green form arrived too early and hid the handoff,
  - the useful proof frame was earlier than the first convenient landing sample,
  - closed receiver outlines around support actors created strict actor-to-outline clearance failures,
  - the third relay route crossed too close to the arriving green actor until it became a short gate cue,
  - the first long render cleared the mechanism but failed off-center audits after the source scaffold disappeared.

## Quality Sling Release

- **Hypothesis**: A pullback and release can make a transfer feel more authored if the dominant form is visibly stretched against a support tether before launch.
- **Result**: Confirmed after moving the blue anchor farther right, tightening the tether, and stretching the green form more aggressively in the pull frame.
- **What worked**:
  - one taut orange tether that clearly connects the stretched green form to the blue anchor,
  - a longer, flatter green form in the pull frame so stored tension reads in a still,
  - the blue anchor isolated enough to act as a real counterforce,
  - tether removal after the release so the final cluster is cleaner than the setup.
- **What failed first**:
  - the first tether looked too loose,
  - the green form was not stretched enough to read as stored tension,
  - the blue anchor needed more separation from the pull state.

## Quality Cradle Catch

- **Hypothesis**: A support-assisted catch can make a landing feel more designed if the support forms clearly sit underneath the dominant form before the final resolve.
- **Result**: Confirmed again after rebuilding the draft into a 30.1-second slide-integration scene with visible opening structure, a held cradle proof frame, explicit scaffold cleanup, and a clean final hold.
- **What worked**:
  - faint cradle slots and a shallow arc in the opening breath, so the target zone read as a pending catch instead of empty space,
  - a blue left support and purple right support that read as the base of a shallow cradle,
  - a smaller green form that sits above those supports instead of flattening the whole group,
  - one guide and accent that suggest descent into the cradle without turning into the main subject,
  - removing hollow receiver slots before the colored support pads move into them, which prevents one-frame slot/actor contacts during the mechanism proof,
  - removing the guide, arc, and accent before the circle settle instead of fading them through the settle, which cleared strict 0.3-second crowding checks,
  - a resolved landing that removes the cradle logic and backing panels after the catch has been established,
  - separating the final support dots downward and outward enough that the stricter crowding audit no longer reads the resolved hold as actor contact.
- **What failed first**:
  - the draft was only 3.13 seconds and had no slide-integration pacing,
  - the first cradle arrangement looked too much like a generic three-part stack,
  - the green form was too large and visually collapsed the support relationship,
  - the supports needed to sit lower to read as a catch from below,
  - keeping a pale target panel behind the final cluster made crowding checks ambiguous even when the frame looked intentional,
  - fading cradle slots, arcs, guides, or accents through the settle can pass broad composition review while failing strict actor-to-guide clearance.

## Quality Ramp Lift

- **Hypothesis**: A visible ramp can make upward motion feel more authored if the dominant form clearly rides the support surface before the final resolve.
- **Result**: Confirmed on the first pass.
- **What worked**:
  - one angled orange ramp with enough length to read as a lifting surface,
  - a hold frame where the green form is clearly above the lower support and aligned with the ramp direction,
  - support forms separated so the ramp remains legible as the main mechanism,
  - ramp removal before the final cluster so the ending stays simpler than the setup.
- **What failed first**:
  - no major structural failure in the first pass, but the proof depends on sampling the mid-lift frame rather than the resolved landing.

## Quality Clamp Close

- **Hypothesis**: Side clamps can make a squeeze feel more intentional if they visibly close around the dominant form before release.
- **Result**: Confirmed again after expanding the draft into a 27.4-second slide-integration scene with a visible opening breath, held pressure proof, clamp cleanup, and clean final hold.
- **What worked**:
  - two vertical support bars that clearly move inward toward the center,
  - a compressed green form that sits between them during the clamp beat,
  - an earlier hold frame where the closing action is cleaner than the later release frame,
  - fading the abandoned source panel during the pressure proof so the left side does not become empty residue,
  - clamp removal before the release morph so the final landing is not contaminated by support bars,
  - recentering the target stage after source cleanup so the resolved hold does not feel stranded.
- **What failed first**:
  - the draft was far below the 25-second pacing floor and began with too little visible structure,
  - the later sampled frame mixed mechanism and release too much,
  - the proof depended on choosing the right still instead of the first convenient one,
  - the clamp bars only read once they were close enough to create visible side pressure,
  - keeping the source panel and clamp bars into the release made 0.3-second samples read as residue even though the mechanism itself was clear.

## Polars Derived Column

- **Hypothesis**: A table transformation should feel calculated if two source cells converge through an operator before the derived value lands in the new column.
- **Result**: Confirmed after cleanup, color-system, pacing, and formula-layout passes.
- **What worked**:
  - the real Polars dataframe is computed in the script, so the animated values match the expression,
  - green and blue source columns plus a purple destination column keep the data roles clear,
  - a subtle row cursor plus source-cell pulses establish the active row without covering source values,
  - a white calculation badge with an orange border keeps the floating formula readable over colored cells and active-row highlights,
  - slowing each row with formula and result holds makes the calculation readable without changing the visual structure,
  - placing the initial pause after the table appears avoids a blank transparent opening while still giving the viewer setup time,
  - exact canonical `primary-*`, `highlight-*`, `gray-*`, `white`, and `page-background` tokens keep the spike aligned with ADR-0002,
  - a white title band, table panel, and code panel keep the transparent WebM usable over darker Slidev backgrounds,
  - transforming the computed result into the destination cell is clearer than placing abstract marker shapes over the numbers,
  - moving the calculation into a side formula badge keeps formula terms aligned and prevents source-cell text from visually colliding with duplicated animated text,
  - when formula text itself must stay readable, let the full formula appear already composed and reserve transforms for the computed result handoff.
- **What failed first**:
  - `Indicate` brought the highlighted header boxes above their labels until text and boxes were given explicit z-ordering,
  - `Open Sans` was not installed on the local renderer, so the script needed the ADR-approved `Arial` fallback,
  - the first color pass used semitransparent cell fills and a white poster background instead of exact highlight tokens and canonical `page-background`,
  - the first floating formula was gray text without a local background, so it lost contrast against the active row and table cells,
  - the first row indicator was a translucent yellow band that covered too much of the row and felt heavier than the calculation itself,
  - circular source tokens looked like pointers sitting on top of the values instead of making the values themselves feel used,
  - enlarged moving value copies created a double-text effect when they sat directly over the original cell values,
  - placing the formula badge over the active row fixed the copy issue but introduced table/header occlusion, so the calculation needed its own side zone,
  - animating formula terms individually made intermediate frames look misaligned and less readable than a composed formula,
  - transparent WebM review frames decoded through PyAV appeared against black, which made unbacked dark title text look too low-contrast.

## SVG Subelement Transform

- **Hypothesis**: A chained SVG transformation should read more clearly if a delete-only group is removed before the surviving semantic groups remap into the next SVG.
- **Result**: Confirmed after one scale pass.
- **What worked**:
  - top-level SVG group ids (`body`, `slot`, `accent`, `delete_badge`) made the animation code explicit about which subelement was deleted and which roles survived,
  - deleting `delete_badge` before the morph kept the transformation from feeling like a whole-icon dissolve,
  - the orange squeeze gate created a useful proof frame for the intermediate SVG stage,
  - one-second frame review exposed which support marks were causal and which were just residue,
  - replacing the final `body` morph with `FadeOut` plus `Create` made the final hold clean while preserving semantic role mapping,
  - half-second review showed that the target body should be established before moving compatible child roles.
- **What failed first**:
  - the first pass was compositionally small inside the 16:9 frame,
  - enlarging the SVG roles and widening the compression gate made the sampled frames more legible without adding text,
  - leaving an orange path as faint residue made the guide read like accidental background motion,
  - direct SVG morphs between filled closed geometry and open stroked geometry created ambiguous in-between shapes,
  - path-normalizing the middle body helped one frame but left a persistent source stroke in the final state,
  - a one-second review missed that the final body handoff briefly made child roles look unsupported,
  - thumbnail sheets can misclassify small role geometry, so inspect suspect half-second frames full size before patching.

## SVG Repo Video Lab

- **Hypothesis**: Downloaded SVG Repo icons become more useful for Slidev-integrated video when they are cached, palette-normalized, and then animated as editable vector components instead of used as opaque clip art.
- **Result**: Confirmed for source download, XML-level recolor, Manim-level deformation, and text replacement attached to a downloaded document SVG.
- **What worked**:
  - using SVG Repo `show/<id>/<slug>.svg` URLs was more reliable from command-line rendering than the direct `download` URLs, which can return a security challenge,
  - caching raw SVGs under the spike and writing edited variants under `videos/<spike>/.generated/svg/` kept the source assets auditable while keeping generated mutations out of source control,
  - XML-level fill replacement worked well for monochrome icons and simple multi-path chart icons before they entered Manim,
  - keeping Manim text as an overlay locked to the downloaded text-document SVG was more predictable than relying on renderer-dependent SVG `<text>` support,
  - a local `page-background` stage made the detailed icons readable while preserving transparent margins in the WebM,
  - starting the scene with the raw SVG structure already present gave the opening breath a real composition instead of a blank first frame,
  - adding faint target slots inside the initially empty edit zone made the opening breath read as a pending destination instead of unused space,
  - when continuing from the resolved SVG cluster into a two-column project breakdown, faint but visible destination block scaffolds kept the setup frame balanced before the progressive lists appeared,
  - fading placeholder scaffolds out while fading the real text-bearing project blocks in kept the activation readable at 0.3-second sampling,
  - moving the compact source label into a small filled header made the left input read as a deliberate source card and removed bottom-label crowding,
  - keeping the lower placeholder scaffold visible until the real lower block had enough opacity prevented one-frame vertical off-center regressions during the handoff,
  - lowering the final fan-out cluster slightly cleared a vertical off-center audit finding without changing the continuation layout,
  - replacing full radial fan guides with shortened segmented guide strokes removed a near-vertical orange residue line while preserving the sense of a fan-out,
  - adding a subtle body anchor rail to real project blocks kept partially populated block activations vertically balanced after the placeholder scaffold was covered,
  - scaling the native Manim document badge to the compact SVG body kept `RAW`/`VIDEO` readable without letting the label overpower the imported document icon,
  - tightening the final fan-out positions before the continuation made the compact input source read as one resolved object instead of a tall stack of loose icons,
  - tightening the fan-hold camera made the resolved SVG cluster feel more deliberate, but only after a small camera recenter kept the early fan proof frames inside the composition audit threshold,
  - softening continuation fork guides after the output pulse kept the final hold cleaner while preserving the source-to-block relationship.
- **What failed first**:
  - some plausible SVG Repo ids returned a Vercel challenge even through `show` URLs, so the downloader needs payload validation and a fallback,
  - treating every imported SVG as a direct morph target is risky because topology varies wildly between downloaded icons,
  - the composition becomes busy quickly when five external icons move at once, so the edit pipeline needs zones and one visible active device per beat,
  - fading in the initial raw icons left the first sampled frame structurally blank,
  - `ReplacementTransform` from placeholder scaffolds into blocks with title text created unreadable mid-frame glyph noise,
  - a fan-out can be technically unclipped but still fail composition because the active bbox sits too high,
  - a full center-to-target fan guide can read as a stray vertical fragment when the target sits almost directly above the hub,
  - a real text-bearing block can cover the placeholder scaffold before its rows appear, leaving a one-frame active bbox that is too top-heavy unless the block has its own body anchor,
  - an empty destination panel during the opening breath reads as dead space unless there is subtle target scaffolding already visible,
  - very faint placeholder panels can look acceptable to a human but be ignored by the composition audit, leaving the source column flagged as off-center until the scaffold has enough stroke or header contrast,
  - a fixed minimum width for text attached to a small imported SVG can make the label become the focal object instead of the SVG body,
  - tightening a fan-out camera against the final hold can introduce off-center failures earlier in the fan formation; audit the whole transition cadence, then nudge the camera to satisfy the proof frames instead of judging only the final cluster,
  - broad crowding audits can flag the intended actor-to-actor contact inside a compression frame; inspect the full-size proof frame and only accept it when the overlap visibly reads as squeeze pressure instead of accidental collision,
  - terminal fork guides that remain at mechanism strength after the pulse can make the final hold feel like it is still mid-transition.

## SVG Repo Continuation Blocks

- **Hypothesis**: A resolved SVG composition can become the input to a second-column project breakdown if the continuation preserves the final cluster as a compact source and reveals destination blocks progressively.
- **Result**: Confirmed after widening the final camera frame, adding visible block scaffolds, and validating the proof frames around the continuation rather than only the old source-to-SVG mechanism.
- **What worked**:
  - keeping the resolved SVG fan as a compact left input made the continuation feel like a real second beat instead of a new unrelated diagram,
  - two large right-side blocks with strong primary-color header bands gave the lists enough hierarchy to read from a slide distance,
  - revealing list rows one at a time made the subproject keypoints feel generated from the prior explanation instead of pasted onto the final frame,
  - drawing the trunk first and each branch as its corresponding block activates kept the fork mechanism visible in still frames,
  - output placeholders with visible gray borders and header hints balanced the setup frame before the detailed lists appeared,
  - updating the poster composition to the new terminal state kept the promoted PNG aligned with the promoted WebM.
- **What failed first**:
  - a narrow continuation camera caused the left input panel to read as a cropped side fragment even though nothing was technically cut off,
  - placeholders that were too faint looked fine to a human but were ignored by the audit, leaving the setup frame flagged as off-center,
  - fading a balancing scaffold in the same beat as the replacement block can create a single bad sampled frame where neither object visually owns the space,
  - auditing only the whole video made earlier intentional focus passes obscure the quality of the new continuation; exact proof timestamps were more useful.
- **Validation pattern**:
  - sample setup, first block populated, fork-with-second-block, both blocks populated, and final hold frames,
  - run `frame-composition-audit.py --times "<proof times>" --write-overlays` on those proof frames,
  - confirm VP9 alpha with a decoder that preserves alpha; on Windows, `imageio-ffmpeg` plus `-c:v libvpx-vp9 -vf format=yuva420p,alphaextract` worked when `ffmpeg` was not on `PATH`.

## Transaction Category Table

- **Hypothesis**: A two-column transaction table should read as text-derived classification if the matched keyword is visible inside the original description before the category lands in the destination cell.
- **Result**: Confirmed after replacing segmented text with inline markup and reviewing medium-render frames.
- **What worked**:
  - keeping the table to two columns made the transformation match the user-facing model directly,
  - using `MarkupText` preserved the original transaction description while coloring only the matched keyword,
  - a full source-cell outline plus a row cursor gave enough active-row focus without placing badges over table values,
  - the side `keyword -> category` badge made the extraction rule readable while leaving the actual table uncluttered,
  - replacing the transient category result into the destination cell kept the handoff clear,
  - sampling the no-badge final frame exposed that the table was balanced only while the side badge was present,
  - a short resolved-state recenter after the badge disappears keeps the final hold framed without weakening the row-level mechanism frames,
  - sizing the title backing panel from the measured title/subtitle group kept both lines inside the local background,
  - sizing side badges from measured terms plus horizontal padding kept `keyword -> category` readable,
  - placing every side badge on one fixed side-column centerline kept the Uber and Pharmacy badges aligned with the top rule badge instead of drifting toward the purple destination column,
  - fading the source-side `keyword ->` terms before the category handoff prevented the result text from crossing over still-visible badge text,
  - setting the camera background to `page-background` avoided black frame margins in standalone WebM review.
- **What failed first**:
  - splitting descriptions into separate text chunks removed visible spaces around the highlighted keyword,
  - direct `Text` character slicing misaligned with spaces because rendered glyph submobjects do not map cleanly to the source string,
  - the table was staged left to make room for the side badge, which made the final no-badge hold feel off-center,
  - a fixed-height title panel covered the main title but let the subtitle fall outside the backing shape,
  - the fixed-width `keyword -> category` badge had cramped left and right padding,
  - positioning row badges from the active category cell made long badges feel attached to the purple column instead of arranged in their own ordered column,
  - keeping `keyword ->` visible while the category traveled back to the table created mid-frame overlap around the 19-second proof frame,
  - a smaller local stage left black margins when the WebM was decoded without alpha in PyAV.

## Transaction Project Breakdown

- **Hypothesis**: A resolved transaction-category table can become two workstream backlogs if the table remains visible as a compact input while two destination blocks appear progressively.
- **Result**: Confirmed after preserving the previous final state as the opening frame, adding visible output scaffolds, and reviewing the generated project-list frames at medium quality.
- **What worked**:
  - starting from the resolved table avoided re-explaining the row classification mechanism,
  - compacting the table into a left input panel made the continuation read as a second beat of the previous result,
  - two right-side project blocks with blue and purple headers established clear workstream roles,
  - visible placeholder panels balanced the setup before tasks appeared,
  - orange trunk and branch guides made the two-block split readable in still frames,
  - revealing one task row per beat made the lists feel generated from the classified table,
  - composing task labels from per-word mobjects with fixed gaps preserved spaces that looked collapsed in direct `Text` and `MarkupText` rows.
- **What failed first**:
  - rendering task rows as a single `Text`/`MarkupText` object made phrases such as `export category dataset` and `convert gaps to tasks` visually lose the first space,
  - relying on the final frame alone would not prove the continuation; setup, first-block, fork, both-blocks, and final-hold frames were all needed,
  - the automated audit flagged expected title-band centering and panel/guide fragments, so full-size review was needed to distinguish warnings from real overlap.

# Practical Rules

1. Start each quality experiment with a single explicit visual hypothesis.
2. Keep text near zero. If narration will be added later, the video should communicate through shape, rhythm, and color first.
3. Use the primary palette as the main semantic signal:
   - green, blue, purple, red for structural actors,
   - orange for route or connection emphasis,
   - yellow for transient accent pulses.
4. Review with a white background first. White review renders make spacing, contrast, and overdraw defects obvious.
5. Extract real video frames before declaring a composition good. Poster images alone are not enough.
6. Watch for three common failure modes in review frames:
   - too much empty space on one side,
   - overlapping shapes that read as mud,
   - accent motion that is too small relative to the stage.
7. Prefer one primary moving element per beat. If multiple things animate at once, clarity and quality perception drop quickly.
8. Use faint gray shadows and thin neutral frames to add depth without fighting the palette.
9. Keep target states visually simpler than source states. The landing frame should feel resolved.
10. If a frame still feels like a static exported diagram, add either:
   - stronger deformation,
   - clearer asymmetry,
   - or a more deliberate accent path.
11. Negative space only feels premium if the active zone is strong enough to earn the empty area around it.
12. Mask-driven reveals work better when the mask is narrow and neutral, so it reads as a device instead of as another actor.
13. In final frames, source ghosts should be barely present. If they compete with the landing cluster, reduce them again.
14. Rhythm markers can improve quality perception, but only when they are visually subordinate to the shapes they are pacing.
15. Counter-motion works best when the two opposing groups keep distinct roles and do not collapse into one ambiguous mass.
16. Strong scale hierarchy improves clarity when the size differences are obvious, not subtle.
17. Orbit-like motion feels premium when one anchor remains stable and the orbital guides disappear before the landing frame.
17a. Anchored-orbit scenes need distinct lanes for each satellite; a second orbit that crosses the first satellite's proof position reads as collision even if the final layout is clean.
17b. In orbit scenes, a low-clearance crowding audit can be a false positive when the actor is intentionally riding its path guide. Confirm full-size frames and fix only if the guide hides the actor, collides with an outline, or causes actor-to-actor crowding.
18. Compression beats work best when the squeeze is visibly tighter than the source layout and the release lands into a simpler, stronger cluster.
19. Edge tension only reads when the dominant form is pushed close enough to the boundary to create pressure, but still far enough to avoid accidental clipping.
20. A short overshoot can make a boundary landing feel authored, but the final settle still has to look clean and stable.
21. Occlusion only helps when one layer clearly peels away; if the overlap is static or ambiguous, it just looks crowded.
22. Any guide used to explain an occlusion move should disappear before the final frame, or it weakens the resolved landing.
23. Hinge-like motion needs a visible anchor during the pivot and no anchor residue after the landing.
24. Pivot experiments work better when the main rotating form is obviously dominant and the supporting forms remain subordinate.
25. Delayed settle only reads when the primary form lands decisively first and the secondary forms overshoot enough for the echo to register.
26. If guide geometry remains on screen during a delayed settle, it can hide the timing idea instead of supporting it.
27. Fan-out landings need enough angular separation and spacing to read as one designed sweep rather than as a tilted pile.
28. A narrow approach can make a fan-out landing feel more intentional by giving the opening move a clear before-and-after state.
29. Shear-based motion only reads when the intermediate diagonal is strong enough to register in still frames, not just in motion.
30. A sheared intermediate state works better when the final landing becomes more stable and simple than the stressed frame.
31. Aperture-style reveals need neutral mechanics and a clear opening distance, or they feel like decoration instead of reveal logic.
32. Any aperture or shutter device should disappear before the final frame so the landing state owns the composition.
33. Snap-recoil motion only reads when the overshoot is large enough to register in still frames, not just as a tiny wobble in motion.
34. In snap-recoil compositions, support forms should resolve after the dominant snap so the primary beat stays legible.
35. Staged convergence needs a lane that is visibly narrower than both the source layout and the final landing.
36. If the intermediate lane is too loose, the choreography reads like a normal transfer instead of a deliberate two-stage convergence.
37. Arc-based handoff only works when the path remains visible through the transfer moment; otherwise it reads like decoration.
38. In an arc handoff, the dominant form should own the curved motion while support forms stay calmer and resolve later.
39. Corridor squeeze needs a compressed phase that is visibly shorter in height than the source and destination states.
40. Neutral corridor geometry should support the squeeze and then disappear before the resolved landing owns the frame.
41. Crossing paths only improve quality when one form clearly owns the foreground crossing and the support forms stay calm enough to preserve hierarchy.
42. If a composition depends on a latch or anchor, that device must be visibly distinct in at least one review frame; being technically present in motion is not enough.
43. Anchor and latch devices work better when they sit just outside the overlap zone, so the mechanism reads before the final landing removes it.
44. Parallax only reads as depth when the dominant form advances noticeably earlier or farther than the supports; small offsets collapse back into ordinary regrouping.
45. In a parallax transfer, support forms should lag enough to preserve foreground and background roles through the mid-frame.
46. Docking works better with an open receiver than with a closed outline, because the entrance itself explains the motion.
47. A docking mechanism should disappear before the final landing, but the hold frame still needs one moment where the dominant form is visibly inside the receiver.
48. A bridge transfer only reads when the passage remains visible around the dominant form; if the crossing form hides the span, the mechanism collapses into a normal move.
49. In a bridge composition, secondary forms should sit away from the span so the crossing beat owns the frame.
50. A support-built receiver works better when the supporting forms create different walls of the pocket instead of stacking in parallel.
51. When a mechanism depends on a specific hold frame, sample later or earlier beats until the proof is visually undeniable instead of documenting the first convenient still.
52. A throat gate only reads when the dominant form is visibly more compressed inside the throat than in the source or landing states.
53. Gate bars should be long enough to define the passage and the support forms should stay away from that squeeze zone.
54. A relay handoff works better when the accent path is split into distinct legs instead of one continuous stroke.
55. If the point of the experiment is support-to-support transfer, delay the dominant form so the relay has one frame where it owns the scene.
56. Sling-style motion only reads when the tether looks taut and the dominant form is visibly stretched in the pullback frame.
57. The support anchor in a sling composition should sit far enough from the pulled form to create visible stored tension before release.
58. A cradle catch works better when the support forms stay lower than the dominant form and clearly define the underside of the catch.
59. If the dominant form in a cradle is too large, the catch stops reading as support and collapses into a generic stacked cluster. After the catch proof frame, move support dots lower and outward and remove backing panels so the resolved hold keeps clear actor-to-actor spacing.
60. Ramp-based motion works better when the support line is long enough to read as a surface, not just a directional cue.
61. In a ramp lift, the useful proof frame is the mid-lift beat where the leader visibly aligns with the ramp rather than the final landing.
62. A clamp close only reads when the side bars are near enough to create visible pressure around the leader.
63. For clamp-style experiments, an earlier hold frame can communicate the mechanism better than a later release frame.
64. Transparent clips that include labels or dark text need a local `page-background` panel or stage, not only a poster background.
65. Repo-wide color-system passes should assign palette roles semantically: green, blue, and purple for actors; orange for routes and causal structure; yellow for momentary attention.
66. Contact sheets are useful after mechanical palette migrations because they reveal margin and clipping regressions across many scripts at once.
67. Avoid default Manim color constants in spike scripts unless the spike is intentionally testing a different visual direction; canonical hex tokens make color drift easier to detect.
68. Do not treat every black PyAV review background as a defect. If the clip is a decorative loop meant to overlay a Slidev surface, preserve transparency and judge the colored motion itself.
69. If a clip contains labels, arrows with captions, timeline cards, or explanatory text, add a local `page-background` stage so the video is inspectable outside its slide container.
70. Slide-integration scenes should normally be at least 25 seconds long, with 2 to 3 seconds of visible opening breath and 5 to 7 seconds of final hold.
71. The opening breath should not be a blank transparent frame. Reveal the initial structure first, then let the viewer read it before motion begins.
72. Final holds are part of the composition. The resolved frame should stay clean, stable, and readable instead of feeling like the clip ends the moment the mechanism completes.
73. SVG remapping reads better when delete-only groups are removed before shared groups transform; otherwise the viewer reads the move as one opaque icon morph.
74. For SVG fragment experiments, sampled proof frames should include the deleted state, the constrained intermediate stage, and the clean landing state.
75. Direct SVG morphs are only trustworthy when source and target roles have compatible geometry; closed filled shapes to open stroked paths should be treated as semantic handoffs instead.
76. If a guide is not still causing the motion, remove it instead of lowering opacity and letting it linger as residue.
77. For SVG semantic handoffs, establish the new primary body before moving child roles; otherwise subelements can appear to float even if the final frame is clean.
78. Review suspicious contact-sheet frames full size before deciding they are artifacts; tiny thumbnails can make intentional child-role geometry look like body residue.
79. Repo-wide video audits must include promoted non-WebM files too. Legacy MP4 compatibility exports can silently drift from the current script unless the script regenerates them.
80. Table-formula scenes read best when source cells are identified in place, while the formula itself lives in a stable side zone.
81. Enlarged value copies over original cell text create double-text artifacts; prefer source-cell pulses and reserve transforms for the computed result handoff.
82. Formula proof frames should include the composed formula and the result-to-cell handoff, not only the final completed table.
82a. After a table-derived value returns from a counter or formula side zone, make the cleanup a bridge into the final table: retire side mechanisms, move or scale the table into the resolved center, and inspect sampled transition frames for faded side-panel residue. Active-red centering audits can overreact while both the table value and side counter are visible, so confirm those warnings at full size and use a slightly wider center tolerance only when the human frame is clearly balanced.
83. For SVG Repo assets, prefer `show/<id>/<slug>.svg` for automated retrieval and validate that the payload is actually SVG before caching it.
84. Keep raw downloaded SVGs separate from generated palette/text variants so later review can distinguish source behavior from pipeline edits.
85. When an imported SVG needs editable text, lock native Manim text to the SVG body unless the render pipeline has proven that SVG `<text>` imports consistently across environments.
86. When a `MovingCameraScene` crops into one stage zone, dim neighboring panel strokes and fills during that focus so edge fragments read as context instead of accidental framing.
87. If a final panel border stops explaining the motion after fan-out, fade it before the hold; the resolved cluster should own the last frame.
88. Promote rendered outputs by latest modified time when Manim writes into reused media folders, because lexicographic path order can copy stale low-quality variants after rerenders.
89. Repo-wide audits need a full-size follow-up for any thumbnail where title text, badges, chips, or callouts sit near the edge; thumbnails made the `aspect-ratio-variants` title clipping easy to miss until candidate frames were extracted.
90. For layout-variant videos, shorten copy and adapt scale per aspect ratio instead of reusing wide-scene coordinates in a portrait render. Portrait variants should get their own stage size, font sizes, and motion lane.
91. Semantic remap scenes need a reserved header band for global badges. Badges that touch a panel border read as accidental overlap even when they do not hide the transformed nodes.
92. A frame-safety audit is useful before patching a whole repo: use it to prioritize edge, center, and large-near-edge candidates, then confirm each suspected issue at full size before changing scripts.
93. In `MovingCameraScene` focus passes, hide neighboring panels or guides completely when they would only appear as cropped edge fragments. Faint context is useful only when the visible shape still reads as context, not as an accidental slice.
94. If a reviewer names a timestamp, fix and validate that exact timestamp in the promoted video, not only the workflow or skill notes.
95. Over-tight camera focus can make a valid mechanism look misframed even when no object is technically cut off; widen the camera or shrink the device until the active colored bbox clears the margin threshold.
96. For SVG clusters, treat `possible_overlap_or_crowding` as a full-size inspection prompt. Do not count it as a crop failure when the overlap is internal to a single imported SVG and the active margins pass.
97. In continuation scenes that move from one resolved input column to a second output column, reveal visible output scaffolds early enough to balance the frame, then replace each scaffold with the real block as its list appears.
98. Rest holds need a geometry audit as well as rendered-frame review. A skipped-animation mobject pass can identify which held object is inside the edge safety margin before spending time on another full render.
99. If a held panel or zone is almost as tall as the camera frame, widen the camera instead of trusting that the panel is technically visible. Low edge clearance reads as bad framing even without literal clipping.
100. For project-breakdown continuations, keep the prior resolved composition visible as a compact input instead of fading it away. The viewer needs the source state to understand that the blocks were generated from it.
101. In list-based project blocks, use strong header bands and small progressive row reveals. The row text may be necessary, but the animation should still be carried by the fork, block activation, and timing.
102. Do not let placeholder panels be merely decorative haze. If a scaffold balances the composition before content appears, give it enough stroke or header contrast to survive proof-frame review and automated audits.
103. For continuation scenes, validate the exact proof frames for the new mechanism. A full-video audit is still useful, but older intentional focus passes can produce unrelated findings.
104. For transparent VP9 WebM validation, metadata such as `alpha_mode=1` is useful but not enough. Extract an alpha frame with a VP9 decoder; if `alphaextract` reports missing planes, force `-c:v libvpx-vp9` and `format=yuva420p`.
105. When a spike's terminal state changes, update the poster path as part of the same iteration so the promoted PNG remains a truthful still of the latest video.
106. For half-second review, do not stop at the first called-out timestamp. Sample the surrounding transition and any later camera handoff, because a fixed timestamp can hide adjacent frames with worse composition.
107. Pixel audits should center on the full intentional scaffold when neutral panels balance the scene. Strong-color-only centering can falsely flag a valid source-to-destination setup as off-center.
108. Treat thin vertical-fragment findings as review prompts unless `--strict-stray` is enabled. Intentional panel edges, scaffolds, and branch guides can look like stray lines to connected-component audits; unsupported residue still needs a full-size overlay check.
109. Use a dedicated crowding audit after a timestamp callout about cramped SVG clusters. Margins and centering can pass while an actor still touches a guide, outline, clamp, or sibling actor.
110. In SVG and label compositions, actor-to-support overlap is not automatically a failure. Text inside an icon body, labels inside a document card, and imported SVG internals can be intentional; reserve blocking crowding findings for actor-to-guide, actor-to-outline, and actor-to-actor clearance failures.
111. Thin neutral rails and panel edges should not redefine the active center unless they genuinely expand the layout. Centering audits should use full content boxes only when the scaffold is large enough to balance the composition, not when it is just a top or bottom rail.
112. If the first review frame is blank because the opening structure fades in, add the initial structure before the first wait and spend the breath on a visible composition.
113. Do not morph placeholder scaffolds into text-bearing blocks. Fade or remove the placeholder, then reveal the real block so mid-frame titles stay readable.
114. A technically visible fan-out can still need vertical recentering; treat off-center audit findings during mechanism proof frames as composition problems, not just crop checks.
115. Compact source panels in continuation scenes read cleaner when their label is a small header band instead of a footer that competes with the compressed source cluster.
116. When a placeholder scaffold is carrying balance, keep it visible until the replacement block is visibly established; otherwise a single transition sample can become vertically off-center.
117. Phase scaffolds such as dashed rails, setup guides, or source-zone hints should fade in the same cleanup beat as the mechanism they support. If they linger into the next mechanism, 0.3-second contact sheets can make them read as accidental residue even when audits do not block.
118. Native Manim labels attached to imported SVGs should scale to the current SVG body, not to a fixed label minimum. Compact icons need subordinate labels so the imported shape remains the actor.
119. In continuation scenes, soften fork or branch guides after the output pulse unless the guide is still causing motion. The final hold should preserve the relationship without looking mid-transition.
120. If an opening composition reserves a destination zone before anything moves there, add faint target slots or scaffolds during the visible breath so the empty zone reads as intentional pending structure.
121. For fan-out guides, shorten or curve any nearly vertical hub-to-target stroke. A full radial line to a target above the hub can look like residue even when it is geometrically correct.
122. Real project blocks need their own low-contrast body anchor if they cover placeholder scaffolds before rows appear. Otherwise a partial block activation can become vertically top-heavy for one sampled frame.
123. When tightening the camera for a fan-out hold, rerun the 0.3-second composition audit across the whole fan transition. The final frame can look stronger while early fan proof frames drift off-center, and a small camera recenter is usually better than giving up the tighter hierarchy.
124. For compression, squeeze, and clamp proof frames, one actor-to-actor contact can be acceptable when the still frame clearly communicates pressure. Validate it full size and keep actor-to-guide or actor-to-outline collisions as blocking.
125. When a continuation starts from a resolved source cluster, a short centered bridge beat can be cleaner than revealing destination scaffolds immediately. If scaffolds appear while the source is still full-size, 0.3-second samples can become off-center or crowded; let the resolved source hold/move as one readable object, then reveal strong scaffold panels as it scales into the input column.
126. For quadrant or axis-drop scenes, keep the causal drop cue vertical when the concept is lower cost or lower risk. A diagonal arrow usually reads as a generic route instead of the intended axis change.
127. When a point must move after an axis cue, separate the mechanism into a held cue, cue removal, and then staged movement. Simultaneous arrow-and-point motion can look like a drag handle instead of a prior decision signal.
128. Large decorative or review frames need the same edge-clearance discipline as actors. If a resting audit flags the outer frame, shrink the frame or widen the camera before accepting the hold.
129. Generated diagram SVGs are most useful when the script writes whole source/target SVGs and then extracts one fragment per stable top-level role id. This keeps the diagram inspectable while still making each node and edge independently animatable in Manim.
130. For generated SVG diagrams, attach native Manim labels to imported SVG bodies instead of relying on SVG text import. It preserves geometry as the actor while keeping labels readable across render environments.
131. Selection handles for SVG diagram roles should sit at node corners or route centers, not on top of label centers. Centered handles can read as text defects in still-frame review.
132. Fade source-layout lanes when a target scaffold takes over. A lane that survives into the final hold looks like leftover diagram residue even when no audit blocks it.
133. Imported SVG arrowheads can look much heavier in Manim than in the raw SVG because stroke conversion turns them into thick filled outlines. For diagram videos, prefer native Manim `Arrow` or `CurvedArrow` connectors anchored to SVG-derived role positions when connector quality matters.
134. For Mermaid-generated diagram videos, keep the `.mmd` file and raw Mermaid SVG as review artifacts. Generate the SVG with Mermaid CLI's `mmdc -i input.mmd -o output.svg` command, or `npx -y -p @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.svg -b transparent` when avoiding a global install. Then normalize only the node groups that need animation into stable top-level ids, strip Mermaid labels from imported fragments, and attach native Manim text for predictable video rendering.
135. Sequence-diagram animations read better when each message has a receiver cue before arrival. A moving arrow alone looks like a static diagram export; a target slot plus activation bar makes the destination feel causal.
136. Opening breaths for participant/lifeline diagrams can become top-heavy because the only saturated objects are the participant cards. Add faint receiver slots or route scaffolds during the breath so the pending protocol occupies the full intended stage.
137. Long cross-lane sequence messages need compact route-label chips. Bare labels are too small or too close to lifelines once multiple horizontal routes accumulate.
138. Return messages should have a different route grammar from requests, such as red dashed paths, while request routes stay orange. This preserves protocol direction without adding explanatory text.
139. Receiver slots should disappear after their causal beat. Leaving all slots visible into the final hold makes the resolved frame look mid-transition even if the animation itself was clear.
140. A terminal artifact, such as a token badge, gives sequence-diagram scenes a resolved center of interest after the last message completes.
141. Animated local backing panels should get explicit z-order below actors and pulses. Otherwise a panel opacity or scale animation can end up visually washing over the final colored mobjects.
142. Negative-space final holds should remove abandoned source containers. Empty panels read as residue, while plain quiet space lets the resolved active zone own the frame.
143. In sequential negative-space transfers, retire each completed route scaffold as soon as its handoff lands. Keeping all route lines until the final cleanup can make later proof frames read as guide residue rather than intentional quiet space.
144. In aperture reveals, move or fade the active accent with the landing cleanup. A pulse left at the former shutter edge reads as residue once the guide disappears.
145. When a reveal removes the source zone, recenter or rebalance the destination stage before the final hold. Otherwise the final cluster can feel stranded in leftover source-to-target layout space.
146. Arc handoff scenes need a proof frame where the dominant form is visibly riding the curve while supports remain calmer. After the source zone disappears, recenter the resolved cluster instead of leaving it stranded in the old target lane.
147. Bridge-span scenes should hold a proof frame where the dominant form is inside the passage while bridge rails remain visible above and below it. Keep bridge ends and receiver slots separated so strict crowding review does not see one closed outline around the actor. If the source zone is removed during cleanup, recenter the target stage and resolved cluster before the final hold.
148. For hollow target slots, set stroke opacity directly instead of applying group opacity. Group opacity can fill stroke-only shapes and make scaffolds look like active actors.
149. Decorative neutral strips and review frames still need rest-state edge clearance. If the audit flags them, shrink the strip or widen the camera even when the colored actors are comfortably inside the frame.
150. Once a support scaffold or backing strip disappears, do not animate it back for a late transition beat. A one-second return reads like a continuity error even when the object is subtle.
151. Do not reuse one transient pulse across separated handoffs if it disappears between them. Draw the active route or use persistent markers instead, because a vanishing dot that returns later reads like a continuity error.
152. Text-bearing terminal cores should use perimeter halos or behind-core rings for pulses. A filled accent crossing the glyph can make the proof frame unreadable even when the pulse is visually centered and intentional.
153. For split-screen or source-to-target sync handoffs, stop the traveling pulse at the receiver entrance when a hollow slot is the cue. Let the target actor appear after the pulse arrives, then fade the slot immediately so strict crowding checks do not see the actor as touching its outline.
154. Red cue rectangles wrapped around active cards can create actor-to-outline crowding even when they look harmless in thumbnails. Prefer separated route segments, corner marks, or a terminal perimeter artifact with real clearance.
155. If a terminal artifact must remain visible through the final hold around a resolved stack, use separated corner brackets instead of a closed rectangle. A closed outline encloses the actors and can fail strict crowding review even when the frame looks visually balanced.
156. In cradle-catch scenes, retire hollow slots before colored support pads occupy that lane, then remove guide arcs and accents before the settle morph. Fading scaffolds through the settle can leave strict 0.3-second crowding failures even when the contact sheet looks acceptable.
157. Slot-docking scenes should remove the abandoned source zone before the dock proof, not after the landing. A faint empty source panel can make 0.3-second proof frames look like dead space even when the receiver action is clear.
158. When a slot proof uses a hollow receiver, keep the active pulse at the receiver entrance or fade it with the guide. A red dot sitting inside the docked actor reads as residue instead of cause.
159. After a slot-docking proof, fade the receiver panel and recenter the resolved actors before the final hold. If separated corner brackets remain as the terminal artifact, give them enough clearance from every resolved actor to pass full-size crowding review.
160. Compact packet diagrams should usually be rebuilt with native field rectangles when generic SVG fragment reveals make the diagram a thin strip. Show the whole packet scaffold first, grow each field body from its bit-range start, use one red cursor or active outline for progression, add tiny gutters between adjacent colored field bodies, and keep range labels inset from field edges.
161. Do not keep a visible local stage plate around simple native packet or bar diagrams unless it carries semantic contrast. Strict crowding audits can treat the plate as an actor touching every field, while a clean page background plus separated terminal brackets keeps the final hold calmer.
162. Browser-native recordings that loop interactively need a capture-only non-looping mode. Clamp the recorded timeline to the resolved final state and keep recording for the final-hold budget so the promoted video does not end by restarting the opening.
163. Persistent review frames or stage plates should be visible as a complete balanced scaffold, not only through shadows or bottom edges. If only the bottom chrome is detected, 0.3-second composition audits can read otherwise centered motion as vertically off-center.
164. In browser-native search beats with candidate cards, use one active cue per target. A red border plus red internal rule or center echo dot can create strict crowding failures and visual ambiguity; keep placeholder internals faint and put visited echoes outside closed outlines.
165. For 3D depth reveals, do not show the full elevated surface and ridge during the flat opening if discovery is the point. Let the opening show only the projection and samples, then reveal surface, columns, and ridge during the camera tilt.
166. Tighten 3D camera zoom enough that the final hold reads as a slide asset, while validating the full tilt path for crop safety. A technically correct 3D model can still fail visually if it sits too small in a wide white field.

## Manim 3D Depth Lab

- **Hypothesis**: The 3D depth reveal reads better when the first view is a true flat projection and the surface ridge appears as a consequence of the camera tilt, not as pre-shown decoration.
- **Result**: Confirmed on `spikes/manim-3d-depth-lab/` after tightening the camera, removing the surface and elevated ridge from the opening breath, and revealing the surface, ridge path, and depth columns during the tilt.
- **What worked**:
  - starting with only the ground projection, sample points, and active probe so the opening still has structure without giving away height,
  - using the camera tilt as the causal beat that introduces the neutral surface, red ridge, and vertical columns,
  - increasing camera zoom and depth-marker weight so the final stopped hold has less dead white field and stronger height evidence,
  - keeping the surface neutral while the primary-red probe and ridge carry the active hierarchy.
- **Validation note**:
  - the final render was reviewed with 83 extracted 0.3-second white-background frames and full-size proof frames at the opening, tilt proof, moving-probe beat, and final hold; composition audit sampled 84 frames with zero findings, crowding audit sampled 84 frames with zero blocking frames, resting-mobject audit reported zero blocking snapshots, and VP9 alpha decoded to a 0 to 255 range.

# Reusable Process

1. State the missing hypothesis.
2. Budget the pacing before coding: opening breath, mechanism beats, and final hold should normally total at least 25 seconds.
3. Build a first composition with minimal text and strict palette discipline.
4. Render the video and export representative frames.
5. Critique spacing, hierarchy, dead space, pacing, and color emphasis from the frames.
6. Patch the composition and rerender.
7. Only keep experiments whose final frames look intentional without narration.
