# Slidev Video Workflow

## Transition Coverage

For a complete built-in transition showcase, validate the direction in the rendered video. In the current local recording workflow, the visible transition to a target slide is controlled by the source slide's frontmatter:

| Target slide | Transition |
| --- | --- |
| 2 | source slide 1 uses `fade` |
| 3 | source slide 2 uses `fade-out` |
| 4 | source slide 3 uses `slide-left` |
| 5 | source slide 4 uses `slide-right` |
| 6 | source slide 5 uses `slide-up` |
| 7 | source slide 6 uses `slide-down` |
| 8 | source slide 7 uses `view-transition` |
| 9 | source slide 8 uses a custom transition |

Use an additional target slide for a custom transition when broad Slidev coverage matters.
For larger showcase videos, append new slides and assign custom transition names to the source slides. Keep the original coverage path intact, then add examples such as `zoom-route`, `rotate-route`, `curtain-route`, `blur-route`, `diagonal-route`, and `stack-route` with matching Vue Transition CSS classes.

For `fade` and `fade-out`, do not rely on small code-highlight changes as the only visible evidence. The local Slidev client defines these as opacity-only route transitions, with `fade-out` delaying the incoming slide after the outgoing slide fades. In showcase videos, set an explicit deck duration and place high-contrast proof blocks on both sides of the navigation:

```css
:root {
  --slidev-transition-duration: 1.5s;
}

.fade-proof {
  position: absolute;
  right: 44px;
  bottom: 36px;
  width: 430px;
  min-height: 92px;
  color: white;
}
```

Record with a route wait long enough for the delayed `fade-out` enter phase, such as `--transition-ms 2800`, then sample frames during the transition.

## Recording Versus Static Export

`slidev export` is appropriate for PDF, PNG, PPTX, and Markdown outputs. Those static exports do not show slide transitions as a viewer experiences them.

Use browser recording when the output must show transitions, moving CSS, or timed navigation. The bundled recorder launches Slidev, opens Chromium through Playwright, waits on each slide, advances with `ArrowRight`, and writes the browser video.

Playwright recording starts while the page is still loading, so polished spike entrypoints should trim the leading `Loading slide...` frames after recording. A robust local pattern is to compare decoded video frames with `screenshots/slide-01.png`, find the first close match, and rewrite the WebM from that timestamp before extracting review frames.

## View Transition Pattern

The source and target slides should both include an element with the same `view-transition-name`:

```html
<div style="view-transition-name: shared-token">Pipeline</div>
```

The target slide should use:

```md
---
transition: view-transition
---
```

Chromium-based browsers are the practical validation target for this transition.

For review videos, make the transition obvious. Put the source and target in visibly different slide positions, avoid a tiny same-place morph, and slow the named transition:

```css
::view-transition-group(shared-token),
::view-transition-old(shared-token),
::view-transition-new(shared-token) {
  animation-duration: 2.2s;
}
```

Validate the result by sampling frames during the transition, not only by checking the target slide screenshot.

## Code Highlighting Recording

Slidev dynamic line highlighting advances on clicks:

````md
```ts {none|1-3|5|all}
const value = compute()
```
````

A video recorder that only sends one `ArrowRight` per slide will skip or collapse those highlight stages. Use a click plan and a per-click hold, for example:

```bash
node .agents/skills/gjv1-slidev/scripts/record-slidev-video.mjs \
  --entry spikes/demo/slides.md \
  --output videos/demo/demo.webm \
  --click-plan '{"2":4,"5":3}' \
  --seconds-per-click 1.6
```

Save screenshots for each click stage, such as `slide-02-click-01.png`, so the dynamic highlighting can be reviewed without scrubbing the full video.

## In-Slide Animation Coverage

Slidev's animation surface is broader than route transitions. A comprehensive browser-recorded deck should include:

- `v-click` reveal stages
- `v-after` content that appears with the previous click
- `v-click-hide` or `v-click.hide` disappearing content
- `[start, end]` click ranges
- `<v-clicks>` for list/table child animation
- `<v-switch>` for click-driven state replacement
- `v-motion` enter and click variants
- Shiki `magic-move` code morphing
- `v-mark` rough annotations

These features all consume click stages. When several are on the same slide, their click registrations can share or extend the same counter. Measure the real number of same-slide `ArrowRight` presses in the browser or run the strict recorder and adjust `--click-plan` until the next `ArrowRight` leaves the slide.

Do not accept a recording that falls back to direct navigation after an undercounted click plan. Direct navigation skips the route transition and proves at least one in-slide animation stage was missed.

## Intention Versus Frame Review

For feedback-driven iterations, build a small intention table for every interactive slide:

- expected visible elements at each click
- expected highlighted code lines at each click
- expected current state for components such as `<v-switch>`
- actual visible elements and highlighted lines from the active slide DOM or saved click screenshots

This catches cases where the deck technically records all clicks but the visual story is wrong. Common failure modes:

- `<v-clicks fade>` shows all future list items at 50% opacity; use plain `<v-clicks>` for hidden-until-click reveal.
- Dynamic fenced code highlighting registers click stages and can delay relative `v-click`, `v-after`, or `<v-switch>` animations that appear later in the DOM.
- Code ranges can silently point to non-existent lines, producing empty stages or a final all-highlight state at the wrong time.

When explanatory code must highlight in lockstep with a different animation, prefer a manual code panel driven by `$clicks`:

```html
<pre class="manual-code"><code>
<span :class="{ 'manual-highlight': $clicks === 1 }">&lt;div v-click&gt;Item&lt;/div&gt;</span>
</code></pre>
```

Manual `$clicks` highlights do not register additional click stages, so they are useful for explaining `v-click`, `v-after`, `<v-clicks>`, and `<v-switch>` behavior without changing the behavior being demonstrated.

## Custom Transition Pattern

Define custom Vue Transition classes in the spike's `style.css` when the transition is part of the deck system:

```css
.pulse-route-enter-active,
.pulse-route-leave-active {
  transition:
    transform 1.6s cubic-bezier(.16, .82, .18, 1),
    clip-path 1.6s cubic-bezier(.16, .82, .18, 1),
    filter 1.6s ease,
    opacity 1.6s ease;
}

.pulse-route-enter-from {
  opacity: 0;
  transform: translateX(34vw) scale(.76) rotate(5deg);
  filter: blur(14px);
  clip-path: polygon(100% 0, 100% 0, 100% 100%, 100% 100%);
}

.pulse-route-leave-to {
  opacity: 0;
  transform: translateX(-28vw) scale(1.12) rotate(-4deg);
  filter: blur(10px);
  clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
}
```

Then use the transition name in slide frontmatter:

```md
---
transition: pulse-route
---
```

For a demo video, do not rely on a small fade or tiny scale change across mostly white slides. Sample frames during the navigation and make the route transition carry visible evidence, such as a diagonal wipe, a large lateral move, blur, rotation, or high-contrast target content.

## Deck-Wide Styling

Prefer a `style.css` file beside `slides.md` for palette tokens, panel styling, code sizing, Mermaid limits, and custom transition classes. It keeps Markdown content focused on the slide material and avoids surprises from large inline `<style>` blocks being scoped or ordered differently than expected.

## Practical Timing

Use `--seconds-per-slide 3` as the minimum for a quick showcase. Increase to 4 or 5 seconds when a slide includes dense Mermaid diagrams, long code blocks, or a presenter-style read.

Use 1280x720 for fast draft loops and 1920x1080 for polished review videos. If the entrypoint trims the loader by re-encoding the WebM, raise the trim bitrate for 1080p outputs, typically to 12 to 16 Mbps, so code and Mermaid diagrams survive the final encode.
