# Mermaid Auth Sequence

## Purpose

This spike animates a Mermaid sequence diagram for a public API authenticating through an auth service and user database.

The Manim scene keeps the Mermaid source in `diagram.mmd`, then rebuilds the sequence with native Manim geometry so the message routes, receiver slots, activation bars, and final token handoff can be tuned frame by frame.

## Run The Render

From the repository root:

```bash
uv run --script spikes/mermaid-auth-sequence/main.py
```

This writes the final assets to:

```text
videos/mermaid-auth-sequence/mermaid-auth-sequence.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence.png
```

To render the critique variants:

```bash
uv run --script spikes/mermaid-auth-sequence/main.py --all-iterations --quality low
```

Iteration outputs are written as:

```text
videos/mermaid-auth-sequence/mermaid-auth-sequence-v1.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v2.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v3.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v4.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v5.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v6.webm
videos/mermaid-auth-sequence/mermaid-auth-sequence-v7.webm
```

## Critique Log

1. `v1` checked the raw sequence layout. It preserved the Mermaid participant order, but the route crossings looked like ordinary diagram export and the receiver side did not cause the motion.
2. `v2` strengthened the actor hierarchy with canonical primary-color cards and clearer vertical spacing. The frame read better, but the message endpoints still felt like arrows landing on empty lifelines.
3. `v3` added receiver slots and activation bars. The proof frames started to show why each message lands, but the slots lingered too long into the resolved state.
4. `v4` introduced a yellow pulse that moves before each route settles. This made the handoff readable in still frames, but the long API-to-service pass needed a cleaner label treatment.
5. `v5` converted route labels into compact chips and faded the mechanism scaffolds after their causal beat. The final hold became cleaner, but the terminal token still needed a stronger landing.
6. `v6` added the final token badge, tightened label placement, softened completed routes, and kept only the participant cards, lifelines, activation history, route labels, and token for the final hold.
7. `v7` removes the local rounded stage plate, replaces the multicolor participant system with white/gray cards, uses gray request routes plus primary-red receiver cues/returns, clears Manim staging before promoted renders, and writes dense 0.3-second review frames/contact sheets after the normal render.

## Learnings

- Sequence-diagram animations work best when each message has a visible receiver device, not just a moving arrow.
- Long cross-lane sequence messages need route labels in compact chips so the text does not compete with lifelines.
- Receiver slots should be visible during the proof frame and removed or softened before the final hold.
- A final token or terminal artifact gives the resolved frame a center of interest after the protocol mechanics finish.
- For content-first transparent sequence assets, neutral participant cards and gray request routes keep hierarchy calmer than per-participant saturated colors.
- Faint primary-red receiver slots in the opening breath make the pending handoff visible in still frames and give active-color audits a meaningful vertical span.
- Clear the spike-local Manim staging directory before promoted renders when changing visual style, because cached partial movies can preserve stale proof frames.

## Validation

- Final render: `videos/mermaid-auth-sequence/mermaid-auth-sequence.webm`
- Duration: 25.791 seconds at 1600x900 and 30 fps.
- Review extraction: 87 alpha-on-white frames at 0.3-second cadence plus 5 contact sheets under `videos/mermaid-auth-sequence/review/`.
- Composition audit: 87 sampled frames at 0.3-second cadence; blocking prompts remain on early active-color centering and were inspected full-size.
- Frame crowding audit: 87 sampled frames at 0.3-second cadence; blocking prompts remain on intentional route/slot/label contacts and were inspected full-size.
- Resting mobject audit: 6 rest snapshots, 0 blocking snapshots, notice-only expected internal sequence-diagram overlaps.
- Transparency: VP9 `alpha_mode=1`; `alphaextract` confirmed alpha range 0-255.
