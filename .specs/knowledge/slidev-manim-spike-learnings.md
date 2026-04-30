---
id: KNOW-0002
title: Slidev plus Manim spike learnings
status: active
date: 2026-04-14
---

# Summary

This repository should treat Slidev delivery assets and review assets as separate concerns when working with Manim.

# Learned Patterns

1. Transparent Manim output is appropriate for real Slidev integration, especially when the slide background should show through.
2. A spike may need multiple video variants with different framing or aspect-ratio assumptions, such as a full-slide version and a content-area version.
3. Review screenshots from Playwright are not always reliable for video rendering, even when the browser successfully fetches the asset.
4. White-background poster images are a practical review surrogate for transparent video during iteration.
5. Keeping Slidev decks inside each spike prevents the repository root from becoming a mix of unrelated experiments.
6. Local media in Slidev should be imported through Vite instead of referenced as raw `/videos/...` paths, otherwise the dev server can return HTML instead of the actual asset.
7. Slide-local `script setup` scope matters. If a later slide needs its own assets or state, define them in that slide instead of assuming an earlier block will cover it.
8. A fallback image should be hidden once the video emits `loadeddata`, otherwise both poster and video may render at the same time.
9. Small corner overlays, split-screen panels, and multi-slide narrative sequences are all viable integration patterns, but each one benefits from its own render framing instead of forcing one universal asset.
10. Reusing one Manim asset across multiple slide compositions is practical for layout testing; reusing a related family of assets is better for narrative sequence testing.
11. For review and debugging, verify media in three layers:
   standalone browser playback,
   Slidev asset resolution,
   visible slide composition.
12. Multi-video layouts are viable, but each tile or panel should keep its own local asset import and readiness state.
13. Wide and tall variants of the same concept are worth rendering separately when the surrounding slide composition changes significantly.
14. Timeline-style or stacked narrative layouts work better when the Manim asset is designed as a dedicated lane, not treated as a generic embedded rectangle.
15. Ambient background loops are viable when the motion stays low-contrast and the readable content sits on a solid or translucent foreground layer.
16. Inset annotation layouts work better when the inset asset is clearly subordinate in size and uses a framing designed specifically for that zoomed role.
17. A hero-plus-support pattern works when the hero owns the composition and the secondary loop behaves as reinforcement instead of a second focal point.
18. When authoring Slidev spike decks, simpler HTML structures are more robust than overly intricate nested layouts; if the Vue parser becomes unstable, reduce the slide markup first and then rebuild complexity incrementally.
19. Step-based narration across consecutive slides can reuse the same Manim asset successfully when each slide changes emphasis, framing, or annotation rather than replacing the motion language.
20. Device or browser frame embeds work better when the frame chrome is authored in Slidev and the Manim asset remains a reusable transparent payload inside that shell.
21. Side-by-side comparison slides benefit from separate assets for each approach and from keeping each panel visually balanced rather than forcing symmetric visual density.
22. In larger Slidev decks that mix Mermaid with custom HTML, Mermaid code fences are more robust when they stay outside complex nested wrappers; wrap the video panels, not the Mermaid block.
23. A background-loop layout can safely use an absolute transparent video layer behind regular slide content as long as the readable layer remains on a light, solid surface.
24. For static validation of built Slidev decks, serving the spike-local `dist/` directory works, but route-specific screenshots are more reliable when Playwright opens the root deck and navigates with arrow keys instead of requesting numbered paths directly.
25. Headless Chromium can still leave transparent `.webm` panels visually blank in screenshots even when the deck, diagram, and panel composition are correct, so screenshot validation should focus on layout, palette, and asset resolution rather than assuming visible decoded motion.
26. Slide-integration Manim videos need pacing room: use the ADR-0003 duration floor, hold an initial visible state before the main motion, and keep the final state on screen long enough for the slide to land.

# Practical Rule

- For spike review, prefer this asset set:
  - transparent `.webm` for the actual deck,
  - white `.png` poster for visual review and fallback,
  - optional alternate framing outputs when different slide compositions need different source videos.
- Prefer creating a dedicated spike whenever a new Slidev composition pattern changes the video framing, narrative role, or fallback behavior.
- If a slide needs multiple concurrent videos, give each one isolated imports, poster fallbacks, and explicit layout ownership instead of sharing a single global media state.
- When validating a spike, check video duration and pacing against ADR-0003 unless the README documents a shorter micro-loop or bumper exception.
