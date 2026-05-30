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

- candidate: 99
- componentized: 26
- no-component: 36
- shared-runner: 26

## Review Matrix

| Spike | Family | Decision | Reusable surface | Evidence checked |
| --- | --- | --- | --- | --- |
| `aspect-ratio-variants` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `background-loop-layer` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `broadcast-limits-lab` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `circle-left-to-right` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `compare-two-approaches` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `device-frame-embed` | presentation/spike | candidate | device content frame | README, main.py, slides |
| `diagram-svg-video-manipulation` | presentation/spike | candidate | svg role remap helpers | README, main.py |
| `grow-arrow-lab` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `hero-plus-supporting-loop` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `indication-animation-gallery` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `inset-annotation-panel` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `large-camera-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-3d-depth-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-callout-reveal-lab` | manim lab | candidate | callout panel | README, main.py |
| `manim-camera-focus-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-code-highlighting-options` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-complex-color-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-data-counter-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-graph-flow-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-narration-timing-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-semantic-transform-lab` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `manim-table-options` | manim lab | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `mermaid-all-diagram-types` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `mermaid-architecture-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-auth-sequence` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `mermaid-block-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-c4-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-class-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-diagram-side-by-side` | mermaid | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
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
| `mermaid-svg-component-remap` | mermaid | candidate | svg role remap helpers | README, main.py |
| `mermaid-svg-direct-insert` | mermaid | candidate | svg role remap helpers | README, main.py |
| `mermaid-timeline-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-treemap-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-treeview-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-user-journey-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-venn-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-xy-chart-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mermaid-zenuml-svg-unfold` | mermaid | shared-runner | mermaid_svg_unfold_engine | README, main.py |
| `mind-map-branching` | mind-map | candidate | mind-map branch guides | README, main.py |
| `mind-map-organic-fractal-lines` | mind-map | candidate | mind-map branch guides | README, main.py |
| `mind-map-scale-spine-lines` | mind-map | candidate | mind-map branch guides | README, main.py |
| `mind-map-shape-token-lines` | mind-map | candidate | mind-map branch guides | README, main.py |
| `multi-video-grid` | presentation/spike | candidate | multi-video grid | README, main.py, slides |
| `overlay-corner-callout` | presentation/spike | candidate | callout panel | README, main.py, slides |
| `polars-derived-column` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `quadrant-arrow-drop` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `quality-anchored-orbit` | quality mechanism | componentized | orbit_guides | README, main.py |
| `quality-aperture-open` | quality mechanism | componentized | aperture_shutters | README, main.py |
| `quality-arc-handoff` | quality mechanism | candidate | arc handoff guide | README, main.py |
| `quality-bridge-span` | quality mechanism | componentized | bridge_lane | README, main.py |
| `quality-bumper-deflect` | quality mechanism | candidate | bumper deflection stop | README, main.py |
| `quality-clamp-close` | quality mechanism | componentized | clamp_pair | README, main.py |
| `quality-compression-release` | quality mechanism | candidate | compression channel | README, main.py |
| `quality-corridor-squeeze` | quality mechanism | candidate | corridor rails | README, main.py |
| `quality-counterlift-balance` | quality mechanism | candidate | counterlift balance | README, main.py |
| `quality-counterweight-balance` | quality mechanism | candidate | counterweight balance | README, main.py |
| `quality-cradle-catch` | quality mechanism | candidate | cradle catch | README, main.py |
| `quality-deformation-flow` | quality mechanism | candidate | deformation flow | README, main.py |
| `quality-echo-settle` | quality mechanism | candidate | settle echo | README, main.py |
| `quality-edge-tension` | quality mechanism | candidate | edge tension marker | README, main.py |
| `quality-fan-splay` | quality mechanism | componentized | fan_guides | README, main.py |
| `quality-fork-diverge` | quality mechanism | componentized | fork_guides | README, main.py |
| `quality-hinge-pivot` | quality mechanism | componentized | hinge_pivot | README, main.py |
| `quality-keystone-lock` | quality mechanism | candidate | keystone lock | README, main.py |
| `quality-latched-anchor` | quality mechanism | candidate | latch anchor | README, main.py |
| `quality-layered-reveal` | quality mechanism | candidate | layered reveal stack | README, main.py |
| `quality-magnet-capture` | quality mechanism | candidate | magnet capture | README, main.py |
| `quality-mask-transfer` | quality mechanism | componentized | mask_window | README, main.py |
| `quality-merge-funnel` | quality mechanism | componentized | merge_funnel | README, main.py |
| `quality-negative-space-focus` | quality mechanism | candidate | negative-space focus frame | README, main.py |
| `quality-occlusion-peel` | quality mechanism | candidate | occlusion peel | README, main.py |
| `quality-parallax-transfer` | quality mechanism | candidate | parallax planes | README, main.py |
| `quality-pulse-routing` | quality mechanism | componentized | pulse | README, main.py |
| `quality-ramp-lift` | quality mechanism | componentized | ramp_plane | README, main.py |
| `quality-relay-handoff` | quality mechanism | candidate | relay handoff nodes | README, main.py |
| `quality-rhythm-gating` | quality mechanism | candidate | rhythm gating | README, main.py |
| `quality-scale-hierarchy` | quality mechanism | candidate | scale hierarchy slots | README, main.py |
| `quality-shear-resolve` | quality mechanism | candidate | shear resolve rails | README, main.py |
| `quality-sleeve-reveal` | quality mechanism | componentized | sleeve_channel | README, main.py |
| `quality-sling-release` | quality mechanism | candidate | sling release | README, main.py |
| `quality-slot-docking` | quality mechanism | componentized | open_slot | README, main.py |
| `quality-snap-recoil` | quality mechanism | candidate | snap recoil stop | README, main.py |
| `quality-staged-convergence` | quality mechanism | candidate | staged convergence lane | README, main.py |
| `quality-throat-gate` | quality mechanism | componentized | gate_column | README, main.py |
| `quality-weave-crossing` | quality mechanism | candidate | weave crossing | README, main.py |
| `red-dot-alignment-spa` | browser-native red-dot | candidate | alignment guides | README, main.py, browser files |
| `red-dot-anchor-spa` | browser-native red-dot | candidate | anchor marker | README, main.py, browser files |
| `red-dot-arch-spa` | browser-native red-dot | candidate | arch guide | README, main.py, browser files |
| `red-dot-balance-spa` | browser-native red-dot | candidate | balance beam | README, main.py, browser files |
| `red-dot-beacon-spa` | browser-native red-dot | candidate | beacon pulse | README, main.py, browser files |
| `red-dot-bloom-spa` | browser-native red-dot | candidate | bloom field | README, main.py, browser files |
| `red-dot-bridge-spa` | browser-native red-dot | componentized | bridge_lane | README, main.py, browser files |
| `red-dot-bumper-spa` | browser-native red-dot | candidate | bumper stop | README, main.py, browser files |
| `red-dot-caliper-spa` | browser-native red-dot | candidate | caliper gauge | README, main.py, browser files |
| `red-dot-circuit-spa` | browser-native red-dot | candidate | circuit route | README, main.py, browser files |
| `red-dot-clamp-spa` | browser-native red-dot | componentized | clamp_pair | README, main.py, browser files |
| `red-dot-coil-spa` | browser-native red-dot | candidate | coil guide | README, main.py, browser files |
| `red-dot-compass-spa` | browser-native red-dot | candidate | compass sweep | README, main.py, browser files |
| `red-dot-constellation-spa` | browser-native red-dot | candidate | constellation nodes | README, main.py, browser files |
| `red-dot-cradle-spa` | browser-native red-dot | candidate | cradle catch | README, main.py, browser files |
| `red-dot-crank-spa` | browser-native red-dot | candidate | crank pivot | README, main.py, browser files |
| `red-dot-crown-spa` | browser-native red-dot | candidate | crown terminal | README, main.py, browser files |
| `red-dot-domino-spa` | browser-native red-dot | candidate | domino row | README, main.py, browser files |
| `red-dot-dovetail-spa` | browser-native red-dot | candidate | dovetail socket | README, main.py, browser files |
| `red-dot-eclipse-spa` | browser-native red-dot | candidate | eclipse mask | README, main.py, browser files |
| `red-dot-fold-spa` | browser-native red-dot | candidate | fold hinge | README, main.py, browser files |
| `red-dot-fork-spa` | browser-native red-dot | componentized | fork_guides | README, main.py, browser files |
| `red-dot-funnel-spa` | browser-native red-dot | componentized | merge_funnel | README, main.py, browser files |
| `red-dot-glyph-spa` | browser-native red-dot | candidate | glyph marker | README, main.py, browser files |
| `red-dot-harbor-spa` | browser-native red-dot | candidate | harbor slot | README, main.py, browser files |
| `red-dot-hinge-spa` | browser-native red-dot | componentized | hinge_pivot | README, main.py, browser files |
| `red-dot-hourglass-spa` | browser-native red-dot | candidate | hourglass choke | README, main.py, browser files |
| `red-dot-iris-spa` | browser-native red-dot | candidate | iris aperture | README, main.py, browser files |
| `red-dot-keyhole-spa` | browser-native red-dot | candidate | keyhole mask | README, main.py, browser files |
| `red-dot-keystone-spa` | browser-native red-dot | candidate | keystone | README, main.py, browser files |
| `red-dot-kite-spa` | browser-native red-dot | candidate | kite guide | README, main.py, browser files |
| `red-dot-knot-spa` | browser-native red-dot | candidate | knot path | README, main.py, browser files |
| `red-dot-labyrinth-spa` | browser-native red-dot | candidate | labyrinth route | README, main.py, browser files |
| `red-dot-lantern-spa` | browser-native red-dot | candidate | lantern reveal | README, main.py, browser files |
| `red-dot-latch-spa` | browser-native red-dot | candidate | latch hook | README, main.py, browser files |
| `red-dot-lattice-spa` | browser-native red-dot | candidate | lattice grid | README, main.py, browser files |
| `red-dot-lens-spa` | browser-native red-dot | candidate | lens focus | README, main.py, browser files |
| `red-dot-loom-spa` | browser-native red-dot | candidate | loom weave | README, main.py, browser files |
| `red-dot-magnet-spa` | browser-native red-dot | candidate | magnet | README, main.py, browser files |
| `red-dot-membrane-spa` | browser-native red-dot | candidate | membrane flex | README, main.py, browser files |
| `red-dot-mirror-spa` | browser-native red-dot | candidate | mirror plane | README, main.py, browser files |
| `red-dot-moire-spa` | browser-native red-dot | candidate | moire overlay | README, main.py, browser files |
| `red-dot-narrative-spa` | browser-native red-dot | candidate | narrative stage | README, main.py, browser files |
| `red-dot-orbit-spa` | browser-native red-dot | componentized | orbit_guides | README, main.py, browser files |
| `red-dot-peel-spa` | browser-native red-dot | candidate | peel layer | README, main.py, browser files |
| `red-dot-pendulum-spa` | browser-native red-dot | candidate | pendulum arc | README, main.py, browser files |
| `red-dot-piston-spa` | browser-native red-dot | candidate | piston channel | README, main.py, browser files |
| `red-dot-prism-spa` | browser-native red-dot | candidate | prism split | README, main.py, browser files |
| `red-dot-pulley-spa` | browser-native red-dot | candidate | pulley route | README, main.py, browser files |
| `red-dot-radial-focus-spa` | browser-native red-dot | candidate | radial focus | README, main.py, browser files |
| `red-dot-ramp-spa` | browser-native red-dot | componentized | ramp_plane | README, main.py, browser files |
| `red-dot-ratchet-spa` | browser-native red-dot | candidate | ratchet steps | README, main.py, browser files |
| `red-dot-relay-spa` | browser-native red-dot | candidate | relay nodes | README, main.py, browser files |
| `red-dot-resonance-spa` | browser-native red-dot | candidate | resonance rings | README, main.py, browser files |
| `red-dot-rhythm-gate-spa` | browser-native red-dot | componentized | gate_column | README, main.py, browser files |
| `red-dot-rivet-spa` | browser-native red-dot | candidate | rivet pin | README, main.py, browser files |
| `red-dot-rosette-spa` | browser-native red-dot | candidate | rosette guide | README, main.py, browser files |
| `red-dot-semaphore-spa` | browser-native red-dot | candidate | semaphore arms | README, main.py, browser files |
| `red-dot-shear-spa` | browser-native red-dot | candidate | shear rails | README, main.py, browser files |
| `red-dot-sling-spa` | browser-native red-dot | candidate | sling release | README, main.py, browser files |
| `red-dot-splice-spa` | browser-native red-dot | candidate | splice join | README, main.py, browser files |
| `red-dot-spring-spa` | browser-native red-dot | candidate | spring recoil | README, main.py, browser files |
| `red-dot-switchback-spa` | browser-native red-dot | candidate | switchback route | README, main.py, browser files |
| `red-dot-thread-spa` | browser-native red-dot | candidate | thread path | README, main.py, browser files |
| `red-dot-threshold-spa` | browser-native red-dot | candidate | threshold gate | README, main.py, browser files |
| `red-dot-tuning-spa` | browser-native red-dot | candidate | tuning fork | README, main.py, browser files |
| `red-dot-turbine-spa` | browser-native red-dot | candidate | turbine rotor | README, main.py, browser files |
| `red-dot-vault-spa` | browser-native red-dot | candidate | vault door | README, main.py, browser files |
| `red-dot-weave-spa` | browser-native red-dot | candidate | weave crossing | README, main.py, browser files |
| `red-dot-zipper-spa` | browser-native red-dot | candidate | zipper track | README, main.py, browser files |
| `red-guide-detail-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `red-point-narrative-spa` | browser-native red-dot | no-component | workflow, API, layout, or reference experiment | README, main.py, browser files |
| `slide-step-handshake` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `slidev-transition-showcase` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `split-screen-sync` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `step-reveal-sequence` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py, slides |
| `svg-repo-video-lab` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `svg-subelement-transform` | presentation/spike | candidate | svg role remap helpers | README, main.py |
| `time-rail-branching` | time rail | componentized | time_rail | README, main.py |
| `time-rail-point-one` | time rail | componentized | time_rail | README, main.py |
| `time-rail-sequence` | time rail | componentized | time_rail | README, main.py |
| `timeline-stack` | time rail | componentized | time_rail | README, main.py, slides |
| `transaction-category-table` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `transaction-project-breakdown` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
| `zoomedscene-image-tour` | presentation/spike | no-component | workflow, API, layout, or reference experiment | README, main.py |
