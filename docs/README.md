# Component GIF Catalog

This catalog collects every component GIF generated so far for the shared Manim component library.
Every entry is generated from the component demo manifest in `spikes/component-library-demos/main.py`,
so each component has a matching GIF and visible component name.

Regenerate the current set with:

```powershell
uv run --script spikes/component-library-demos/main.py --quality low
```

Source demos live in `spikes/component-library-demos/`. Full render outputs live in
`videos/component-library-demos/components/`. Doc-ready GIFs live in
`.specs/assets/component-demos/`.

## Current Components

| Component | Demo | Notes |
| --- | --- | --- |
| `slab` | ![slab](../.specs/assets/component-demos/slab.gif) | Solid rectangular block used for bars, rails, cards, and resolved payloads. |
| `pulse` | ![pulse](../.specs/assets/component-demos/pulse.gif) | Primary-red active actor used to carry handoffs, routes, and proof beats. |
| `open_slot` | ![open_slot](../.specs/assets/component-demos/open-slot.gif) | Open receiver outline that reserves a destination without enclosing the actor. |
| `source_slot` | ![source_slot](../.specs/assets/component-demos/source-slot.gif) | Bracketed launch slot for a source-side active actor. |
| `target_slot` | ![target_slot](../.specs/assets/component-demos/target-slot.gif) | Mirrored bracketed landing slot for a receiver-side active actor. |
| `bridge_lane` | ![bridge_lane](../.specs/assets/component-demos/bridge-lane.gif) | Guided transfer lane between source and destination zones. |
| `gate_column` | ![gate_column](../.specs/assets/component-demos/gate-column.gif) | Prepared vertical gate that opens around the active actor. |
| `time_rail` | ![time_rail](../.specs/assets/component-demos/time-rail.gif) | Left-side timeline rail that narrates progressive card activation. |
| `mask_window` | ![mask_window](../.specs/assets/component-demos/mask-window.gif) | Moving mask window that reveals transferred outputs. |
| `terminal_brackets` | ![terminal_brackets](../.specs/assets/component-demos/terminal-brackets.gif) | Separated corner marks used as a terminal resolved-state cue. |
| `terminal_brackets_around` | ![terminal_brackets_around](../.specs/assets/component-demos/terminal-brackets-around.gif) | Convenience wrapper that sizes terminal brackets around a target cluster. |
| `neutral_cluster` | ![neutral_cluster](../.specs/assets/component-demos/neutral-cluster.gif) | Reusable quiet gray payload cluster for transfer and resolve demos. |
| `aperture_shutters` | ![aperture_shutters](../.specs/assets/component-demos/aperture-shutters.gif) | Reusable opening shutters extracted from aperture-style transition spikes. |
| `merge_funnel` | ![merge_funnel](../.specs/assets/component-demos/merge-funnel.gif) | Converging guide rails for combining two inputs into one output. |
| `orbit_guides` | ![orbit_guides](../.specs/assets/component-demos/orbit-guides.gif) | Circular guide marks for anchored orbit and return-motion explanations. |
| `fork_guides` | ![fork_guides](../.specs/assets/component-demos/fork-guides.gif) | Branching guide rails for diverging one active actor into parallel outcomes. |
| `pressure_wall` | ![pressure_wall](../.specs/assets/component-demos/pressure-wall.gif) | Compact resistance marker for pressure, constraint, and boundary-contact scenes. |
| `clamp_pair` | ![clamp_pair](../.specs/assets/component-demos/clamp-pair.gif) | Opposing vertical clamp bars extracted from compression and clamp-close spikes. |
| `sleeve_channel` | ![sleeve_channel](../.specs/assets/component-demos/sleeve-channel.gif) | Three-sided reveal sleeve for contained payload transitions. |
| `ramp_plane` | ![ramp_plane](../.specs/assets/component-demos/ramp-plane.gif) | Inclined support plane for lift, ramp, and assisted-transfer scenes. |
| `fan_guides` | ![fan_guides](../.specs/assets/component-demos/fan-guides.gif) | Radial guide set for fan-out, splay, and multi-target distribution scenes. |
| `hinge_pivot` | ![hinge_pivot](../.specs/assets/component-demos/hinge-pivot.gif) | Pivot, arm, and arc guide for hinge or swing-motion explanations. |
| `arc_handoff` | ![arc_handoff](../.specs/assets/component-demos/arc-handoff.gif) | Curved route with source and target points for arced handoff scenes. |
| `bumper_stop` | ![bumper_stop](../.specs/assets/component-demos/bumper-stop.gif) | Angled stop and wall for deflecting an active actor away from a boundary. |
| `compression_channel` | ![compression_channel](../.specs/assets/component-demos/compression-channel.gif) | Narrow parallel rails for squeezing or releasing a payload. |
| `corridor_rails` | ![corridor_rails](../.specs/assets/component-demos/corridor-rails.gif) | Long guide rails with a central squeeze point for corridor passages. |
| `cradle_catch` | ![cradle_catch](../.specs/assets/component-demos/cradle-catch.gif) | Lower catch basin and support pads for landing or settling scenes. |
| `balance_beam` | ![balance_beam](../.specs/assets/component-demos/balance-beam.gif) | Fulcrum and beam primitive for counterweight and counterlift balance scenes. |
| `deformation_wave` | ![deformation_wave](../.specs/assets/component-demos/deformation-wave.gif) | Elastic wave guide for deformation, flex, and shape-change proof beats. |
| `settle_echo` | ![settle_echo](../.specs/assets/component-demos/settle-echo.gif) | Concentric settling rings for echo, impact, and delayed-resolution scenes. |
| `edge_tension_marker` | ![edge_tension_marker](../.specs/assets/component-demos/edge-tension-marker.gif) | Boundary wall and tether marker for edge-pressure compositions. |
| `keystone_lock` | ![keystone_lock](../.specs/assets/component-demos/keystone-lock.gif) | Central locking block with side supports for keystone-style closures. |
| `latch_anchor` | ![latch_anchor](../.specs/assets/component-demos/latch-anchor.gif) | Anchor dot and hook path for latched handoff scenes. |
| `layered_stack` | ![layered_stack](../.specs/assets/component-demos/layered-stack.gif) | Offset layer stack for progressive reveal and peel-style compositions. |
| `magnet_capture` | ![magnet_capture](../.specs/assets/component-demos/magnet-capture.gif) | Opposing capture arcs and poles for magnetic attraction scenes. |
| `negative_space_frame` | ![negative_space_frame](../.specs/assets/component-demos/negative-space-frame.gif) | Four-part frame that leaves an intentional central opening. |
| `parallax_planes` | ![parallax_planes](../.specs/assets/component-demos/parallax-planes.gif) | Offset depth planes for parallax transfer and layered motion scenes. |
| `occlusion_peel` | ![occlusion_peel](../.specs/assets/component-demos/occlusion-peel.gif) | Cover panel and reveal lip for occlusion and peel-away scenes. |
| `relay_nodes` | ![relay_nodes](../.specs/assets/component-demos/relay-nodes.gif) | Evenly spaced handoff nodes for relay and ownership transfer scenes. |
| `rhythm_gate_marks` | ![rhythm_gate_marks](../.specs/assets/component-demos/rhythm-gate-marks.gif) | Cadence marks on a rail for rhythm and gated timing scenes. |
| `shear_rails` | ![shear_rails](../.specs/assets/component-demos/shear-rails.gif) | Offset rails and body marker for shear and lateral-resolve scenes. |
| `sling_arc` | ![sling_arc](../.specs/assets/component-demos/sling-arc.gif) | Anchored release arc for sling and launch-motion scenes. |
| `snap_recoil_stop` | ![snap_recoil_stop](../.specs/assets/component-demos/snap-recoil-stop.gif) | Spring-like recoil cue with a pressure stop for snap-back scenes. |
| `convergence_lane` | ![convergence_lane](../.specs/assets/component-demos/convergence-lane.gif) | Narrowing lane for staged convergence and compression proofs. |
| `weave_crossing` | ![weave_crossing](../.specs/assets/component-demos/weave-crossing.gif) | Separated crossing strokes for over-under weave explanations. |
| `receiver_slot` | ![receiver_slot](../.specs/assets/component-demos/receiver-slot.gif) | Composite receiver-slot pattern with pending outline, moving payload, and terminal mark. |
| `rhythm_gate` | ![rhythm_gate](../.specs/assets/component-demos/rhythm-gate.gif) | Composite cadence pattern using several gate columns along a rail. |

## `slab`

Solid rectangular block used for bars, rails, cards, and resolved payloads.

![slab](../.specs/assets/component-demos/slab.gif)

## `pulse`

Primary-red active actor used to carry handoffs, routes, and proof beats.

![pulse](../.specs/assets/component-demos/pulse.gif)

## `open_slot`

Open receiver outline that reserves a destination without enclosing the actor.

![open_slot](../.specs/assets/component-demos/open-slot.gif)

## `source_slot`

Bracketed launch slot for a source-side active actor.

![source_slot](../.specs/assets/component-demos/source-slot.gif)

## `target_slot`

Mirrored bracketed landing slot for a receiver-side active actor.

![target_slot](../.specs/assets/component-demos/target-slot.gif)

## `bridge_lane`

Guided transfer lane between source and destination zones.

![bridge_lane](../.specs/assets/component-demos/bridge-lane.gif)

## `gate_column`

Prepared vertical gate that opens around the active actor.

![gate_column](../.specs/assets/component-demos/gate-column.gif)

## `time_rail`

Left-side timeline rail that narrates progressive card activation.

![time_rail](../.specs/assets/component-demos/time-rail.gif)

## `mask_window`

Moving mask window that reveals transferred outputs.

![mask_window](../.specs/assets/component-demos/mask-window.gif)

## `terminal_brackets`

Separated corner marks used as a terminal resolved-state cue.

![terminal_brackets](../.specs/assets/component-demos/terminal-brackets.gif)

## `terminal_brackets_around`

Convenience wrapper that sizes terminal brackets around a target cluster.

![terminal_brackets_around](../.specs/assets/component-demos/terminal-brackets-around.gif)

## `neutral_cluster`

Reusable quiet gray payload cluster for transfer and resolve demos.

![neutral_cluster](../.specs/assets/component-demos/neutral-cluster.gif)

## `aperture_shutters`

Reusable opening shutters extracted from aperture-style transition spikes.

![aperture_shutters](../.specs/assets/component-demos/aperture-shutters.gif)

## `merge_funnel`

Converging guide rails for combining two inputs into one output.

![merge_funnel](../.specs/assets/component-demos/merge-funnel.gif)

## `orbit_guides`

Circular guide marks for anchored orbit and return-motion explanations.

![orbit_guides](../.specs/assets/component-demos/orbit-guides.gif)

## `fork_guides`

Branching guide rails for diverging one active actor into parallel outcomes.

![fork_guides](../.specs/assets/component-demos/fork-guides.gif)

## `pressure_wall`

Compact resistance marker for pressure, constraint, and boundary-contact scenes.

![pressure_wall](../.specs/assets/component-demos/pressure-wall.gif)

## `clamp_pair`

Opposing vertical clamp bars extracted from compression and clamp-close spikes.

![clamp_pair](../.specs/assets/component-demos/clamp-pair.gif)

## `sleeve_channel`

Three-sided reveal sleeve for contained payload transitions.

![sleeve_channel](../.specs/assets/component-demos/sleeve-channel.gif)

## `ramp_plane`

Inclined support plane for lift, ramp, and assisted-transfer scenes.

![ramp_plane](../.specs/assets/component-demos/ramp-plane.gif)

## `fan_guides`

Radial guide set for fan-out, splay, and multi-target distribution scenes.

![fan_guides](../.specs/assets/component-demos/fan-guides.gif)

## `hinge_pivot`

Pivot, arm, and arc guide for hinge or swing-motion explanations.

![hinge_pivot](../.specs/assets/component-demos/hinge-pivot.gif)

## `arc_handoff`

Curved route with source and target points for arced handoff scenes.

![arc_handoff](../.specs/assets/component-demos/arc-handoff.gif)

## `bumper_stop`

Angled stop and wall for deflecting an active actor away from a boundary.

![bumper_stop](../.specs/assets/component-demos/bumper-stop.gif)

## `compression_channel`

Narrow parallel rails for squeezing or releasing a payload.

![compression_channel](../.specs/assets/component-demos/compression-channel.gif)

## `corridor_rails`

Long guide rails with a central squeeze point for corridor passages.

![corridor_rails](../.specs/assets/component-demos/corridor-rails.gif)

## `cradle_catch`

Lower catch basin and support pads for landing or settling scenes.

![cradle_catch](../.specs/assets/component-demos/cradle-catch.gif)

## `balance_beam`

Fulcrum and beam primitive for counterweight and counterlift balance scenes.

![balance_beam](../.specs/assets/component-demos/balance-beam.gif)

## `deformation_wave`

Elastic wave guide for deformation, flex, and shape-change proof beats.

![deformation_wave](../.specs/assets/component-demos/deformation-wave.gif)

## `settle_echo`

Concentric settling rings for echo, impact, and delayed-resolution scenes.

![settle_echo](../.specs/assets/component-demos/settle-echo.gif)

## `edge_tension_marker`

Boundary wall and tether marker for edge-pressure compositions.

![edge_tension_marker](../.specs/assets/component-demos/edge-tension-marker.gif)

## `keystone_lock`

Central locking block with side supports for keystone-style closures.

![keystone_lock](../.specs/assets/component-demos/keystone-lock.gif)

## `latch_anchor`

Anchor dot and hook path for latched handoff scenes.

![latch_anchor](../.specs/assets/component-demos/latch-anchor.gif)

## `layered_stack`

Offset layer stack for progressive reveal and peel-style compositions.

![layered_stack](../.specs/assets/component-demos/layered-stack.gif)

## `magnet_capture`

Opposing capture arcs and poles for magnetic attraction scenes.

![magnet_capture](../.specs/assets/component-demos/magnet-capture.gif)

## `negative_space_frame`

Four-part frame that leaves an intentional central opening.

![negative_space_frame](../.specs/assets/component-demos/negative-space-frame.gif)

## `parallax_planes`

Offset depth planes for parallax transfer and layered motion scenes.

![parallax_planes](../.specs/assets/component-demos/parallax-planes.gif)

## `occlusion_peel`

Cover panel and reveal lip for occlusion and peel-away scenes.

![occlusion_peel](../.specs/assets/component-demos/occlusion-peel.gif)

## `relay_nodes`

Evenly spaced handoff nodes for relay and ownership transfer scenes.

![relay_nodes](../.specs/assets/component-demos/relay-nodes.gif)

## `rhythm_gate_marks`

Cadence marks on a rail for rhythm and gated timing scenes.

![rhythm_gate_marks](../.specs/assets/component-demos/rhythm-gate-marks.gif)

## `shear_rails`

Offset rails and body marker for shear and lateral-resolve scenes.

![shear_rails](../.specs/assets/component-demos/shear-rails.gif)

## `sling_arc`

Anchored release arc for sling and launch-motion scenes.

![sling_arc](../.specs/assets/component-demos/sling-arc.gif)

## `snap_recoil_stop`

Spring-like recoil cue with a pressure stop for snap-back scenes.

![snap_recoil_stop](../.specs/assets/component-demos/snap-recoil-stop.gif)

## `convergence_lane`

Narrowing lane for staged convergence and compression proofs.

![convergence_lane](../.specs/assets/component-demos/convergence-lane.gif)

## `weave_crossing`

Separated crossing strokes for over-under weave explanations.

![weave_crossing](../.specs/assets/component-demos/weave-crossing.gif)

## `receiver_slot`

Composite receiver-slot pattern with pending outline, moving payload, and terminal mark.

![receiver_slot](../.specs/assets/component-demos/receiver-slot.gif)

## `rhythm_gate`

Composite cadence pattern using several gate columns along a rail.

![rhythm_gate](../.specs/assets/component-demos/rhythm-gate.gif)
