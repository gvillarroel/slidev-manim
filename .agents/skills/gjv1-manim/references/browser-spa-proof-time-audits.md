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
