---
id: KNOW-0004
title: GJV1 Manim video quality learnings
status: active
date: 2026-04-15
---

# Summary

Higher-quality Manim videos in this repository come from hypothesis-driven iteration, sparse compositions, and frame review. The strongest results rely on shape relationships, timing, and color hierarchy more than on text.

# Experiments

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
- **Result**: Confirmed.
- **What worked**:
  - three large source capsules with clear spacing,
  - one warm pulse to cue movement,
  - a vertical destination stack that stayed simple,
  - almost no text.
- **What failed first**:
  - the destination stack was too far to the right,
  - the mid-transition overlap looked muddy until the landing positions were adjusted.

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
- **Result**: Confirmed after one revision.
- **What worked**:
  - a soft background strip behind the active panel,
  - faint ghost history instead of strong duplicated shapes,
  - diagonal source cards transforming into smaller orbit-like targets,
  - orange guide lines kept long enough to read direction but short enough to avoid clutter.
- **What failed first**:
  - the first version was too top-left heavy,
  - ghost shapes were too visible,
  - the target cluster was not balanced.

## Quality Negative Space Focus

- **Hypothesis**: Premium-looking motion can come from controlling where nothing happens, not only where motion happens.
- **Result**: Confirmed after enlarging the landing zone.
- **What worked**:
  - one soft active window on the left for the source state,
  - a delayed transfer to a second active window on the right,
  - a landing cluster that stayed compact but not timid,
  - large negative space that remained intentional instead of empty.
- **What failed first**:
  - the first landing cluster was too small,
  - the active zone was too weak to justify the empty space around it.

## Quality Mask Transfer

- **Hypothesis**: A traveling mask band can make a reveal feel more authored than plain fade-ins.
- **Result**: Confirmed after simplifying the final cluster.
- **What worked**:
  - a neutral vertical band that acts as a reveal device,
  - top-row chips as a source state and circles as a distilled target state,
  - top-row ghosts kept very faint in the final frame,
  - diagonal compact landing with clear size hierarchy.
- **What failed first**:
  - the band was too wide,
  - the first compact cluster felt muddy,
  - ghost chips were too visible and competed with the landing state.

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
  - orbit arcs used only during motion and removed afterward,
  - satellites landing in positions that still respect the anchor,
  - a final frame with anchor plus orbit residue implied by placement rather than by visible guides.
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
  - minimal supporting shapes that still keep the cluster legible.
- **What failed first**:
  - the first version ended on the right side without real tension,
  - the destination cluster was too timid,
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
- **Result**: Confirmed after tightening the shutter spacing and restoring a cleaner circular landing.
- **What worked**:
  - neutral shutters that create a clear before-and-after reveal state,
  - a compact reveal stage inside the aperture before the final transform,
  - full shutter removal before the resolved frame,
  - a final landing that stays cleaner than the reveal mechanics.
- **What failed first**:
  - the first reveal still looked like a normal transition with extra props,
  - the reveal shapes stayed too close to the final state,
  - the aperture needed stronger opening separation to feel intentional.

## Quality Snap Recoil

- **Hypothesis**: A decisive arrival followed by a short recoil can feel sharper and more intentional than a perfectly smooth settle.
- **Result**: Confirmed after increasing the overshoot distance of the dominant form.
- **What worked**:
  - the dominant green form arriving first with a visible overshoot,
  - a quick recoil into the final landing position,
  - support forms resolving afterward so the snap remains the main beat,
  - a final frame that still feels stable despite the sharper motion.
- **What failed first**:
  - the first overshoot was too small,
  - the snap risked reading like a normal arrival,
  - the recoil needed more contrast against the final settled position.

## Quality Bumper Deflect

- **Hypothesis**: A visible bumper should make a redirection feel more authored if the leader clearly compresses against it before the landing.
- **Result**: Confirmed after forcing the leader to arrive first and delaying the supports.
- **What worked**:
  - the green leader reaching the bumper before the blue and purple supports move,
  - a long enough orange bumper that the deflection surface remains legible in still frames,
  - a compressed, slightly tilted contact shape for the leader,
  - support forms arriving later so the contact frame stays uncluttered.
- **What failed first**:
  - the first version spread the support forms too early,
  - the contact frame did not show enough compression,
  - the bumper existed but did not yet feel like the cause of the turn.

## Quality Counterlift Balance

- **Hypothesis**: A counterlift should feel more deliberate if a visible beam tilts while one side rises and the other drops.
- **Result**: Confirmed after turning the balance line into an actual tilted mechanism.
- **What worked**:
  - the orange beam tilting enough to read as load transfer instead of decoration,
  - the green leader rising on one end while the blue support drops on the other,
  - a yellow pivot that stays visible through the proof frame,
  - a simpler final cluster after the mechanism disappears.
- **What failed first**:
  - the first version kept the beam too static,
  - the opposing motions looked like regrouping instead of weighted exchange,
  - the support roles were too close together to read as separate ends of a mechanism.

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
- **Result**: Confirmed after rebuilding the receiver as a right-side pocket and delaying the support forms.
- **What worked**:
  - a receiver pocket that clearly opens toward the arriving form,
  - a stretched green leader that is partly inside the pocket before the landing,
  - a yellow core that stays near the entrance during the capture frame,
  - support forms arriving after the main pull so the mechanism stays readable.
- **What failed first**:
  - the first receiver looked decorative instead of causal,
  - the leader crossed the receiver too completely and lost the sense of being pulled inward,
  - support forms arrived too early and diluted the capture beat.

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
- **Result**: Confirmed after tightening the lane and making the staging phase more compact.
- **What worked**:
  - a visible narrow lane that all forms pass through,
  - strong contrast between the staged lane and the circular landing,
  - enough compression in the lane to make the second release feel earned,
  - guide removal before the final convergence so the staging geometry owns the intermediate beat.
- **What failed first**:
  - the first lane was too loose,
  - the convergence looked too close to a direct transfer,
  - the intermediate stage needed stronger compression to justify its existence.

## Quality Arc Handoff

- **Hypothesis**: A dominant form can feel more authored if it transfers along a visible curve before the rest of the composition catches up.
- **Result**: Confirmed after keeping the arc visible through the handoff moment.
- **What worked**:
  - one strong orange arc that survives long enough to be legible,
  - the dominant green form arriving along that curve before the support forms resolve,
  - a final cluster that contrasts with the earlier curved path,
  - minimal supporting motion so the handoff remains the main beat.
- **What failed first**:
  - the first arc disappeared too soon,
  - the motion looked like a normal transfer with curved decoration,
  - the intermediate handoff position needed to be more distinct from the final landing.

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
- **Result**: Confirmed after changing the slot from a closed shell into open rails and pushing the green form deeper into the receiver.
- **What worked**:
  - an open receiving slot that reads as a real target instead of a decorative frame,
  - a hold frame where the green form is visibly docked while the blue form remains outside the entrance,
  - a short guide that leads into the receiver without overpowering the scene,
  - full removal of the docking rails before the resolved landing.
- **What failed first**:
  - the original slot looked too closed and generic,
  - the first dock state did not separate the receiver from the support forms strongly enough,
  - the mechanism needed a more obvious entrance to read in still frames.

## Quality Bridge Span

- **Hypothesis**: A temporary bridge can make a transfer feel more intentional if the dominant form clearly crosses a supported passage instead of drifting through empty space.
- **Result**: Confirmed after turning the bridge into a visible passage and shrinking the green form so the span remains readable around it.
- **What worked**:
  - a horizontal bridge that stays visible on both sides of the crossing form,
  - a hold frame where the green form is clearly on the bridge rather than merely near it,
  - blue and purple supports kept lower so they do not compete with the crossing beat,
  - bridge removal before the final cluster so the ending stays clean.
- **What failed first**:
  - the first bridge read like an orange bar instead of a supported crossing,
  - the green form was too large and swallowed the mechanism,
  - the passage needed visible separation above and below the crossing form.

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
- **Result**: Confirmed after widening the gate bars, shrinking the green form further, and moving the support forms away from the throat.
- **What worked**:
  - two longer orange bars that create a clear gated throat,
  - a compressed green form that is visibly thinner while passing between them,
  - support forms positioned away from the squeeze so the gate owns the frame,
  - gate removal before the resolved landing.
- **What failed first**:
  - the first gate bars looked too isolated and the squeeze was not tight enough,
  - the support forms were too close to the mechanism,
  - the green form needed stronger compression to read in still frames.

## Quality Relay Handoff

- **Hypothesis**: A support-to-support relay can make the final regroup feel more designed if the accent clearly passes from one support role to another before the dominant form arrives.
- **Result**: Confirmed after separating the accent move into two beats and sampling the mid-relay frame before the green form settles.
- **What worked**:
  - a two-segment relay path that gives the handoff a visible first and second leg,
  - a proof frame where the blue support, purple support, and accent define the relay before the green form fully joins,
  - a delayed green arrival so the support handoff has its own beat,
  - a final cluster that removes the relay device after the transfer has been established.
- **What failed first**:
  - the original relay read too much like a normal guide line,
  - the green form arrived too early and hid the handoff,
  - the useful proof frame was earlier than the first convenient landing sample.

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
- **Result**: Confirmed after lowering the blue and purple supports, shrinking the green form, and keeping a sampled frame where the green shape visibly rests above the cradle.
- **What worked**:
  - a blue left support and purple right support that read as the base of a shallow cradle,
  - a smaller green form that sits above those supports instead of flattening the whole group,
  - one guide that suggests descent into the cradle without turning into the main subject,
  - a resolved landing that removes the cradle logic after the catch has been established.
- **What failed first**:
  - the first cradle arrangement looked too much like a generic three-part stack,
  - the green form was too large and visually collapsed the support relationship,
  - the supports needed to sit lower to read as a catch from below.

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
- **Result**: Confirmed after sampling an earlier proof frame where the side bars are close enough to read as pressure around the leader.
- **What worked**:
  - two vertical support bars that clearly move inward toward the center,
  - a compressed green form that sits between them during the clamp beat,
  - an earlier hold frame where the closing action is cleaner than the later release frame,
  - clamp removal before the final landing so the composition resolves into a simpler cluster.
- **What failed first**:
  - the later sampled frame mixed mechanism and release too much,
  - the proof depended on choosing the right still instead of the first convenient one,
  - the clamp bars only read once they were close enough to create visible side pressure.

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
  - when continuing from the resolved SVG cluster into a two-column project breakdown, faint but visible destination block scaffolds kept the setup frame balanced before the progressive lists appeared,
  - fading placeholder scaffolds out while fading the real text-bearing project blocks in kept the activation readable at 0.3-second sampling,
  - moving the compact source label into a small filled header made the left input read as a deliberate source card and removed bottom-label crowding,
  - keeping the lower placeholder scaffold visible until the real lower block had enough opacity prevented one-frame vertical off-center regressions during the handoff,
  - lowering the final fan-out cluster slightly cleared a vertical off-center audit finding without changing the continuation layout.
- **What failed first**:
  - some plausible SVG Repo ids returned a Vercel challenge even through `show` URLs, so the downloader needs payload validation and a fallback,
  - treating every imported SVG as a direct morph target is risky because topology varies wildly between downloaded icons,
  - the composition becomes busy quickly when five external icons move at once, so the edit pipeline needs zones and one visible active device per beat,
  - fading in the initial raw icons left the first sampled frame structurally blank,
  - `ReplacementTransform` from placeholder scaffolds into blocks with title text created unreadable mid-frame glyph noise,
  - a fan-out can be technically unclipped but still fail composition because the active bbox sits too high,
  - very faint placeholder panels can look acceptable to a human but be ignored by the composition audit, leaving the source column flagged as off-center until the scaffold has enough stroke or header contrast.

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
59. If the dominant form in a cradle is too large, the catch stops reading as support and collapses into a generic stacked cluster.
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

# Reusable Process

1. State the missing hypothesis.
2. Budget the pacing before coding: opening breath, mechanism beats, and final hold should normally total at least 25 seconds.
3. Build a first composition with minimal text and strict palette discipline.
4. Render the video and export representative frames.
5. Critique spacing, hierarchy, dead space, pacing, and color emphasis from the frames.
6. Patch the composition and rerender.
7. Only keep experiments whose final frames look intentional without narration.
