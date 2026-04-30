---
id: ADR-0003
title: Scene duration and pacing
status: accepted
date: 2026-04-29
---

# Context

Slide-oriented Manim videos need enough time for a presenter and viewer to register the composition. Short clips can look technically correct but feel rushed when embedded in a deck, especially when narration or live explanation is expected.

# Decision

Manim scenes intended for Slidev integration should use a deliberate pacing floor:

- A scene should be at least 25 seconds long unless it is explicitly documented as a micro-loop, bumper, or timing-constrained exception.
- Start with 2 to 3 seconds of visual breathing room after the first meaningful composition is visible.
- End with 5 to 7 seconds of resolved hold so the slide does not move away immediately after the final state appears.
- Avoid blank openings for transparent assets. If the scene starts from an empty transparent frame, reveal the initial structure first, then hold for the opening breath.
- Treat pauses and holds as part of the authored scene, not as filler. They should preserve the composition, hierarchy, and palette discipline.

# Consequences

- New spike videos should feel calmer and more narration-ready by default.
- Render review should check total duration, opening breath, and ending hold in addition to visual frame quality.
- Scene scripts should budget time intentionally instead of compressing all motion into a short sequence.
- Exceptions are allowed, but the spike README or source comments should explain why a shorter duration is appropriate.
