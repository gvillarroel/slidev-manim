---
title: Spike Component Review
updated: 2026-05-30
---

# Spike Component Review

This matrix tracks the current review pass for every spike directory and whether it should feed the reusable component catalog.
The review uses each spike directory name plus available README, `main.py`, browser, and slide artifacts as current-state evidence.

Decision meanings:

- `componentized`: the spike is already represented by an exported common component or composite catalog demo.
- `candidate`: the spike contains a reusable visual or motion surface that should be extracted or refined.
- `shared-runner`: the spike already uses shared infrastructure, and the reusable unit is not a GIF catalog component yet.
- `no-component`: the spike is primarily a workflow, API, layout, or reference experiment with no clear visual component to extract.

Summary:

- componentized: 129
- no-component: 32
- shared-runner: 26

## Review Matrix

| Spike | Family | Decision | Reusable surface | Evidence checked |
| --- | --- | --- | --- | --- |
| `aspect-ratio-variants` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `background-loop-layer` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `broadcast-limits-lab` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `circle-left-to-right` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `compare-two-approaches` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `device-frame-embed` | presentation/spike | componentized | device_frame | README, main.py, slides |
| `diagram-svg-video-manipulation` | presentation/spike | componentized | svg_role_slots | README, main.py |
| `grow-arrow-lab` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `hero-plus-supporting-loop` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `indication-animation-gallery` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `inset-annotation-panel` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `large-camera-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-3d-depth-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-callout-reveal-lab` | manim lab | componentized | callout_panel | README, main.py |
| `manim-camera-focus-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-code-highlighting-options` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-complex-color-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-data-counter-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-graph-flow-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-narration-timing-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-semantic-transform-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-table-options` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `mermaid-all-diagram-types` | mermaid | componentized | svg_role_slots | README, main.py |
| `mermaid-architecture-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-auth-sequence` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `mermaid-block-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-c4-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-class-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-diagram-side-by-side` | mermaid | componentized | svg_role_slots | README, main.py, slides |
| `mermaid-entity-relationship-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-flowchart-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-gantt-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-gitgraph-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-ishikawa-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-kanban-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-layout-gallery` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `mermaid-mindmap-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-packet-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-pie-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-quadrant-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-radar-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-requirement-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-sankey-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-sequence-boundary` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `mermaid-sequence-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-state-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-svg-component-remap` | mermaid | componentized | svg_role_slots | README, main.py |
| `mermaid-svg-direct-insert` | mermaid | componentized | svg_role_slots | README, main.py |
| `mermaid-timeline-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-treemap-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-treeview-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-user-journey-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-venn-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-xy-chart-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-zenuml-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mind-map-branching` | mind-map | componentized | mind_map_branch_guides | README, main.py |
| `mind-map-organic-fractal-lines` | mind-map | componentized | mind_map_branch_guides | README, main.py |
| `mind-map-scale-spine-lines` | mind-map | componentized | mind_map_branch_guides | README, main.py |
| `mind-map-shape-token-lines` | mind-map | componentized | mind_map_branch_guides | README, main.py |
| `multi-video-grid` | presentation/spike | componentized | multi_video_grid | README, main.py, slides |
| `overlay-corner-callout` | presentation/spike | componentized | callout_panel | README, main.py, slides |
| `polars-derived-column` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `quadrant-arrow-drop` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `quality-anchored-orbit` | quality mechanism | componentized | latch_anchor | README, main.py |
| `quality-aperture-open` | quality mechanism | componentized | aperture_shutters | README, main.py |
| `quality-arc-handoff` | quality mechanism | componentized | arc_handoff | README, main.py |
| `quality-bridge-span` | quality mechanism | componentized | bridge_lane | README, main.py |
| `quality-bumper-deflect` | quality mechanism | componentized | bumper_stop | README, main.py |
| `quality-clamp-close` | quality mechanism | componentized | clamp_pair | README, main.py |
| `quality-compression-release` | quality mechanism | componentized | compression_channel | README, main.py |
| `quality-corridor-squeeze` | quality mechanism | componentized | corridor_rails | README, main.py |
| `quality-counterlift-balance` | quality mechanism | componentized | balance_beam | README, main.py |
| `quality-counterweight-balance` | quality mechanism | componentized | balance_beam | README, main.py |
| `quality-cradle-catch` | quality mechanism | componentized | cradle_catch | README, main.py |
| `quality-deformation-flow` | quality mechanism | componentized | deformation_wave | README, main.py |
| `quality-echo-settle` | quality mechanism | componentized | settle_echo | README, main.py |
| `quality-edge-tension` | quality mechanism | componentized | edge_tension_marker | README, main.py |
| `quality-fan-splay` | quality mechanism | componentized | fan_guides | README, main.py |
| `quality-fork-diverge` | quality mechanism | componentized | fork_guides | README, main.py |
| `quality-hinge-pivot` | quality mechanism | componentized | hinge_pivot | README, main.py |
| `quality-keystone-lock` | quality mechanism | componentized | keystone_lock | README, main.py |
| `quality-latched-anchor` | quality mechanism | componentized | latch_anchor | README, main.py |
| `quality-layered-reveal` | quality mechanism | componentized | layered_stack | README, main.py |
| `quality-magnet-capture` | quality mechanism | componentized | magnet_capture | README, main.py |
| `quality-mask-transfer` | quality mechanism | componentized | mask_window | README, main.py |
| `quality-merge-funnel` | quality mechanism | componentized | merge_funnel | README, main.py |
| `quality-negative-space-focus` | quality mechanism | componentized | negative_space_frame | README, main.py |
| `quality-occlusion-peel` | quality mechanism | componentized | occlusion_peel | README, main.py |
| `quality-parallax-transfer` | quality mechanism | componentized | parallax_planes | README, main.py |
| `quality-pulse-routing` | quality mechanism | componentized | pulse | README, main.py |
| `quality-ramp-lift` | quality mechanism | componentized | ramp_plane | README, main.py |
| `quality-relay-handoff` | quality mechanism | componentized | relay_nodes | README, main.py |
| `quality-rhythm-gating` | quality mechanism | componentized | rhythm_gate_marks | README, main.py |
| `quality-scale-hierarchy` | quality mechanism | componentized | arc_handoff | README, main.py |
| `quality-shear-resolve` | quality mechanism | componentized | shear_rails | README, main.py |
| `quality-sleeve-reveal` | quality mechanism | componentized | sleeve_channel | README, main.py |
| `quality-sling-release` | quality mechanism | componentized | sling_arc | README, main.py |
| `quality-slot-docking` | quality mechanism | componentized | open_slot | README, main.py |
| `quality-snap-recoil` | quality mechanism | componentized | coil_guide | README, main.py |
| `quality-staged-convergence` | quality mechanism | componentized | convergence_lane | README, main.py |
| `quality-throat-gate` | quality mechanism | componentized | gate_column | README, main.py |
| `quality-weave-crossing` | quality mechanism | componentized | weave_crossing | README, main.py |
| `red-dot-alignment-spa` | browser-native red-dot | componentized | open_slot | README, main.py, browser files |
| `red-dot-anchor-spa` | browser-native red-dot | componentized | latch_anchor | README, main.py, browser files |
| `red-dot-arch-spa` | browser-native red-dot | componentized | arc_handoff | README, main.py, browser files |
| `red-dot-balance-spa` | browser-native red-dot | componentized | balance_beam | README, main.py, browser files |
| `red-dot-beacon-spa` | browser-native red-dot | componentized | pulse | README, main.py, browser files |
| `red-dot-bloom-spa` | browser-native red-dot | componentized | settle_echo | README, main.py, browser files |
| `red-dot-bridge-spa` | browser-native red-dot | componentized | bridge_lane | README, main.py, browser files |
| `red-dot-bumper-spa` | browser-native red-dot | componentized | bumper_stop | README, main.py, browser files |
| `red-dot-caliper-spa` | browser-native red-dot | componentized | caliper_gauge | README, main.py, browser files |
| `red-dot-circuit-spa` | browser-native red-dot | componentized | circuit_route | README, main.py, browser files |
| `red-dot-clamp-spa` | browser-native red-dot | componentized | clamp_pair | README, main.py, browser files |
| `red-dot-coil-spa` | browser-native red-dot | componentized | coil_guide | README, main.py, browser files |
| `red-dot-compass-spa` | browser-native red-dot | componentized | arc_handoff | README, main.py, browser files |
| `red-dot-constellation-spa` | browser-native red-dot | componentized | relay_nodes | README, main.py, browser files |
| `red-dot-cradle-spa` | browser-native red-dot | componentized | cradle_catch | README, main.py, browser files |
| `red-dot-crank-spa` | browser-native red-dot | componentized | hinge_pivot | README, main.py, browser files |
| `red-dot-crown-spa` | browser-native red-dot | componentized | terminal_brackets | README, main.py, browser files |
| `red-dot-domino-spa` | browser-native red-dot | componentized | rhythm_gate_marks | README, main.py, browser files |
| `red-dot-dovetail-spa` | browser-native red-dot | componentized | keystone_lock | README, main.py, browser files |
| `red-dot-eclipse-spa` | browser-native red-dot | componentized | negative_space_frame | README, main.py, browser files |
| `red-dot-fold-spa` | browser-native red-dot | componentized | hinge_pivot | README, main.py, browser files |
| `red-dot-fork-spa` | browser-native red-dot | componentized | fork_guides | README, main.py, browser files |
| `red-dot-funnel-spa` | browser-native red-dot | componentized | merge_funnel | README, main.py, browser files |
| `red-dot-glyph-spa` | browser-native red-dot | componentized | terminal_brackets | README, main.py, browser files |
| `red-dot-harbor-spa` | browser-native red-dot | componentized | open_slot | README, main.py, browser files |
| `red-dot-hinge-spa` | browser-native red-dot | componentized | hinge_pivot | README, main.py, browser files |
| `red-dot-hourglass-spa` | browser-native red-dot | componentized | convergence_lane | README, main.py, browser files |
| `red-dot-iris-spa` | browser-native red-dot | componentized | aperture_shutters | README, main.py, browser files |
| `red-dot-keyhole-spa` | browser-native red-dot | componentized | negative_space_frame | README, main.py, browser files |
| `red-dot-keystone-spa` | browser-native red-dot | componentized | keystone_lock | README, main.py, browser files |
| `red-dot-kite-spa` | browser-native red-dot | componentized | fork_guides | README, main.py, browser files |
| `red-dot-knot-spa` | browser-native red-dot | componentized | weave_crossing | README, main.py, browser files |
| `red-dot-labyrinth-spa` | browser-native red-dot | componentized | relay_nodes | README, main.py, browser files |
| `red-dot-lantern-spa` | browser-native red-dot | componentized | layered_stack | README, main.py, browser files |
| `red-dot-latch-spa` | browser-native red-dot | componentized | latch_anchor | README, main.py, browser files |
| `red-dot-lattice-spa` | browser-native red-dot | componentized | lattice_grid | README, main.py, browser files |
| `red-dot-lens-spa` | browser-native red-dot | componentized | negative_space_frame | README, main.py, browser files |
| `red-dot-loom-spa` | browser-native red-dot | componentized | weave_crossing | README, main.py, browser files |
| `red-dot-magnet-spa` | browser-native red-dot | componentized | magnet_capture | README, main.py, browser files |
| `red-dot-membrane-spa` | browser-native red-dot | componentized | deformation_wave | README, main.py, browser files |
| `red-dot-mirror-spa` | browser-native red-dot | componentized | parallax_planes | README, main.py, browser files |
| `red-dot-moire-spa` | browser-native red-dot | componentized | parallax_planes | README, main.py, browser files |
| `red-dot-narrative-spa` | browser-native red-dot | componentized | narrative_stage | README, main.py, browser files |
| `red-dot-orbit-spa` | browser-native red-dot | componentized | orbit_guides | README, main.py, browser files |
| `red-dot-peel-spa` | browser-native red-dot | componentized | occlusion_peel | README, main.py, browser files |
| `red-dot-pendulum-spa` | browser-native red-dot | componentized | arc_handoff | README, main.py, browser files |
| `red-dot-piston-spa` | browser-native red-dot | componentized | compression_channel | README, main.py, browser files |
| `red-dot-prism-spa` | browser-native red-dot | componentized | fork_guides | README, main.py, browser files |
| `red-dot-pulley-spa` | browser-native red-dot | componentized | arc_handoff | README, main.py, browser files |
| `red-dot-radial-focus-spa` | browser-native red-dot | componentized | fan_guides | README, main.py, browser files |
| `red-dot-ramp-spa` | browser-native red-dot | componentized | ramp_plane | README, main.py, browser files |
| `red-dot-ratchet-spa` | browser-native red-dot | componentized | rhythm_gate_marks | README, main.py, browser files |
| `red-dot-relay-spa` | browser-native red-dot | componentized | relay_nodes | README, main.py, browser files |
| `red-dot-resonance-spa` | browser-native red-dot | componentized | settle_echo | README, main.py, browser files |
| `red-dot-rhythm-gate-spa` | browser-native red-dot | componentized | gate_column | README, main.py, browser files |
| `red-dot-rivet-spa` | browser-native red-dot | componentized | latch_anchor | README, main.py, browser files |
| `red-dot-rosette-spa` | browser-native red-dot | componentized | orbit_guides | README, main.py, browser files |
| `red-dot-semaphore-spa` | browser-native red-dot | componentized | fork_guides | README, main.py, browser files |
| `red-dot-shear-spa` | browser-native red-dot | componentized | shear_rails | README, main.py, browser files |
| `red-dot-sling-spa` | browser-native red-dot | componentized | sling_arc | README, main.py, browser files |
| `red-dot-splice-spa` | browser-native red-dot | componentized | convergence_lane | README, main.py, browser files |
| `red-dot-spring-spa` | browser-native red-dot | componentized | snap_recoil_stop | README, main.py, browser files |
| `red-dot-switchback-spa` | browser-native red-dot | componentized | relay_nodes | README, main.py, browser files |
| `red-dot-thread-spa` | browser-native red-dot | componentized | sling_arc | README, main.py, browser files |
| `red-dot-threshold-spa` | browser-native red-dot | componentized | gate_column | README, main.py, browser files |
| `red-dot-tuning-spa` | browser-native red-dot | componentized | balance_beam | README, main.py, browser files |
| `red-dot-turbine-spa` | browser-native red-dot | componentized | orbit_guides | README, main.py, browser files |
| `red-dot-vault-spa` | browser-native red-dot | componentized | aperture_shutters | README, main.py, browser files |
| `red-dot-weave-spa` | browser-native red-dot | componentized | weave_crossing | README, main.py, browser files |
| `red-dot-zipper-spa` | browser-native red-dot | componentized | rhythm_gate_marks | README, main.py, browser files |
| `red-guide-detail-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `red-point-narrative-spa` | browser-native red-dot | componentized | narrative_stage | README, main.py, browser files |
| `slide-step-handshake` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `slidev-transition-showcase` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `split-screen-sync` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `step-reveal-sequence` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `svg-repo-video-lab` | presentation/spike | componentized | svg_role_slots | README, main.py |
| `svg-subelement-transform` | presentation/spike | componentized | svg_role_slots | README, main.py |
| `time-rail-branching` | time rail | componentized | time_rail | README, main.py |
| `time-rail-point-one` | time rail | componentized | time_rail | README, main.py |
| `time-rail-sequence` | time rail | componentized | time_rail | README, main.py |
| `timeline-stack` | time rail | componentized | time_rail | README, main.py, slides |
| `transaction-category-table` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `transaction-project-breakdown` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `zoomedscene-image-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
