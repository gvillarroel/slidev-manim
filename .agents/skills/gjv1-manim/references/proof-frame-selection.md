# Proof Frame Selection

Read this when the composition is built but the right review frames are unclear.

## Family Table

| Motion family | Proof frame to sample | Common failure | First patch |
| --- | --- | --- | --- |
| Arc handoff | Leader midway on visible arc | Arc disappears before it explains motion | Keep route visible through transfer |
| Bridge span | Leader crossing while bridge remains visible around it | Leader hides the bridge | Shrink leader or widen bridge |
| Weave crossing | Foreground crossing frame | Parallel movement reads as a normal transfer | Separate support forms and keep path visible |
| Relay handoff | Support-to-support transfer before dominant form resolves | One continuous path hides the relay | Split path into distinct legs |
| Parallax transfer | Lead form advanced farther than supports | Offsets are too subtle | Increase lead distance and delay supports |
| Slot docking | Leader visibly inside open receiver | Receiver reads as closed decoration | Use open rails and a clear entrance |
| Compression release | Tightest compressed frame | Squeeze is too polite | Narrow the constrained state |
| Corridor squeeze | Stack inside corridor | Corridor is wider than source state | Tighten corridor and reduce stack height |
| Throat gate | Leader inside the throat | Gate bars look decorative | Lengthen bars and clear support forms away |
| Clamp close | Bars close around leader | Sampled release frame hides pressure | Sample earlier hold frame |
| Merge funnel | Inputs compressed at narrow neck | Neck is too wide | Tighten funnel neck and mid-stack |
| Ramp lift | Leader aligned with ramp mid-lift | Ramp looks like a generic arrow | Lengthen ramp and align leader to surface |
| Mask transfer | Mask still covering source-to-target transition | Mask competes with actors | Keep mask neutral and narrow |
| Aperture open | Shutters separated but still visible | Reveal looks like normal fade | Increase opening distance |
| Occlusion peel | Front layer visibly peels away | Overlap reads as clutter | Exaggerate peel and remove guide residue |
| Magnet capture | Leader partly inside receiver pocket | Pocket looks decorative | Open the receiver toward leader |
| Sleeve reveal | Leader visibly contained in sleeve | Sleeve sits away from leader | Move sleeve deeper over the leader |
| Hinge pivot | Main form rotating around visible anchor | Anchor hidden by the leader | Separate anchor and increase rotation |
| Counterlift balance | Beam tilted while sides exchange height | Beam looks static | Tilt beam more and separate ends |
| Bumper deflect | Leader compressing against bumper | Deflection cause is unclear | Delay supports and show contact |
| Sling release | Taut tether plus stretched leader | Tether looks loose | Increase pullback and anchor separation |
| Cradle catch | Support forms below leader | Stack reads generic | Lower supports and shrink leader |
| Fan splay | Final angled fan | Landing reads as tilted pile | Increase angle and spacing |
| Scale hierarchy | Dominant form owns final frame | Size difference is subtle | Make main form obviously larger |
| Edge tension | Overshoot or landing near boundary | Edge pressure is timid | Push closer without clipping |
| Echo settle | Primary lands before supports | Timing difference is invisible | Increase support overshoot |
| Snap recoil | Overshoot before recoil | Snap reads as normal arrival | Increase overshoot distance |
| Staged convergence | Forms compressed in lane | Lane is too loose or enclosed by a box that becomes a support envelope | Make lane narrower than source and target, use open rails, and retire route cues before the held proof |
| Fork diverge | Branches separated around fork | Split reads as regrouping | Keep trunk visible and increase branch angle |
| Project breakdown continuation | Resolved input plus visible output scaffolds, then populated blocks | Continuation reads as a separate pasted slide | Keep compact source input, reveal scaffolds early, and populate blocks progressively |

## Critique Order

Patch in this order:

1. Spacing.
2. Hierarchy.
3. Mechanism visibility.
4. Motion path.
5. Cleanup.

Do not add text until the mechanism fails after those passes.

## Still-Frame Test

A proof frame should answer one question without narration:

`What physical or visual mechanism is causing this transition?`

If the answer is "it moved because the animation says so," the frame is unfinished.

## Timestamp Callouts

When a reviewer names a specific second, inspect that timestamp at full size before defending the contact sheet. Contact sheets can hide panel crops, over-tight margins, and thin residual fragments.

For the exact timestamp and its surrounding motion, run:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --start 12 --end 16 --cadence 0.5 --write-overlays
```

Patch any `low_visual_margin` or `off_center_content` finding before claiming the framing is clean. `stray_vertical_fragment` means the overlay should be opened full size; it is blocking only when the vertical slice is unsupported residue or an accidental crop, not when it is a deliberate panel edge, scaffold, or guide. Rerun with `--strict-stray` when a reviewer calls out side fragments. `possible_overlap_or_crowding` is also a full-size review prompt; it is not automatically wrong, but it is not dismissible from a thumbnail.

When the timestamp looks visually cramped or actors appear to touch a guide, outline, clamp, panel edge, or another actor, run the stricter crowding audit too:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --start 12 --end 16 --cadence 0.5 --write-overlays
```

Treat `low_component_clearance` as blocking when the pair is actor-to-guide, actor-to-outline, or actor-to-actor. Do not treat actor-to-support overlap as automatically wrong; labels and icon internals often sit inside their support body by design.

## Continuation Blocks

For a continuation that turns a resolved diagram into generated project blocks, do not sample only the final completed list. The useful proof set is:

1. setup with the prior resolved composition and visible output scaffolds,
2. first block populated,
3. fork or branch still visible while the second block activates,
4. both blocks populated,
5. final hold after guide softening.

If the setup frame is flagged as off-center, make the destination scaffolds more visible before moving the camera again. Very faint placeholder panels can look acceptable in motion but disappear from pixel-based audits.
