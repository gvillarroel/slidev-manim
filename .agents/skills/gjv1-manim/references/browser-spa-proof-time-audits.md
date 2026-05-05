# Browser SPA Proof-Time Audits

Use this note for browser-native five-act SPAs that are reviewed with fixed proof screenshots.

## Rule

Run composition audits on the same timestamps used for proof screenshots instead of only on coarse evenly spaced samples.

## Why

Generic samples can pass or fail a different motion beat than the frame you are actually using to judge the narrative. Matching audit times to proof-frame times keeps the automated check attached to the same causal moment the human review is evaluating.

## Minimal practice

- Store the proof-frame timestamps once in the spike runner.
- Reuse those timestamps for Playwright screenshots and composition audits.
- Record the timestamps in the output summary so later review can reproduce the same checks.
- Generate 0.3-second cadence frames and contact sheets as normal runner outputs, not as an ad hoc review step. The named proof frames establish act milestones; dense cadence frames catch transition residue, off-center openings, and final-hold drift between those milestones.
- For sparse five-act openings, make the lead actor reach the next handoff entrance by the opening proof screenshot and show the pending target scaffolds at audit-visible opacity. A faint destination scaffold can balance empty space, but a tiny actor still far from that scaffold usually reads as off-center dead space.
- If the opening or search act is still left-heavy after that, reserve a faint version of the future conflict device on the far side of the stage. A pale throat, gate, or receiver wing can widen the content box enough for proof-frame audits while still reading as a prepared destination rather than a second subject.
- If a late search proof frame is meant to show the point arriving at the next mechanism, fade historical ingress trails below audit strength before that screenshot. A lingering red history rail can become the dominant left-side mass and make the audit center on where the point was instead of where the mechanism is now taking over.
- For portrait mobile proof shots, scaling the scene group alone may still leave a tiny letterboxed composition inside a tall browser viewport. Decide the SVG review crop explicitly with `preserveAspectRatio` or a portrait-specific viewBox, then confirm the terminal artifact still keeps its full silhouette after the mobile crop.
