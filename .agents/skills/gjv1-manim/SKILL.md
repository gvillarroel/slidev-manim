---
name: gjv1-manim
description: |
  Use when creating or refining Manim videos in this repository where the goal is higher visual quality, minimal text, and narration-ready motion language.

  This skill turns a vague video idea into a hypothesis-driven quality pass: define the missing experiment, render, extract frames, critique composition, iterate, and keep only the versions that still look intentional without explanatory text.
---

# Purpose

Use this skill when the goal is not merely to make a Manim video that works, but to make one that looks deliberate, sparse, and ready for narration later.

# Core Rule

The video should explain itself through shape, color, timing, compression, and reveal logic first. Text is a last resort.

# Working Style

- Work from one explicit hypothesis at a time.
- Keep text near zero.
- Prefer native Manim geometry over imported SVG fragments when visual quality matters.
- Review real sampled frames before declaring the result good.
- Keep only the experiments whose still frames remain intentional without narration.

# Canonical Sources

- Reuse the accumulated patterns in [C:\Users\villa\dev\slidev-manim\.specs\knowledge\gjv1-manim-video-quality.md](C:/Users/villa/dev/slidev-manim/.specs/knowledge/gjv1-manim-video-quality.md).
- Update that knowledge note after each useful experiment. Do not let the skill drift away from the note.

# Workflow

## 1. Choose the missing hypothesis

Do not start with “make it nicer.” Start with one concrete test.

Good examples:

- one leader should visibly compress before release,
- a receiver should visibly cause the landing,
- a split should read as one branching event,
- a reveal should depend on a sleeve, aperture, or mask,
- a support mechanism should still be readable in one still frame.

If the request is vague, rewrite it internally as:

`If <mechanism> is made more visible, the motion should feel more authored than <generic alternative>.`

## 2. Pick the motion family

Classify the experiment before coding. This determines what proof frame to sample and what failure mode to expect.

### Transfer and path families

- `arc handoff`
- `bridge span`
- `weave crossing`
- `relay handoff`
- `parallax transfer`
- `slot docking`

### Compression and release families

- `compression release`
- `corridor squeeze`
- `throat gate`
- `clamp close`
- `merge funnel`
- `ramp lift`

### Reveal and conceal families

- `mask transfer`
- `aperture open`
- `occlusion peel`
- `magnet capture`
- `sleeve reveal`

### Pivot and force families

- `hinge pivot`
- `counterlift balance`
- `bumper deflect`
- `sling release`
- `cradle catch`

### Arrangement and landing families

- `fan splay`
- `scale hierarchy`
- `negative space focus`
- `edge tension`
- `anchored orbit`
- `echo settle`
- `snap recoil`
- `staged convergence`
- `fork diverge`

If the experiment fits more than one family, choose the one whose mechanism must survive in a still frame.

## 3. Build the first pass

Follow these baseline rules:

- use the project primary palette for structural roles:
  - green, blue, purple, red for actors or stages,
  - orange for paths, guides, funnels, sleeves, gates, or support geometry,
  - yellow for transient pulses, pivots, or attractor cores.
- prefer rounded geometry,
- use only subtle gray framing or shadows,
- keep one main moving element per beat,
- make the landing state simpler than the source state,
- keep support elements subordinate to the mechanism being tested.

## 4. Render and extract proof frames

Always render the real video:

```bash
uv run --script spikes/<spike-name>/main.py
```

Then extract frames with `PyAV`:

```bash
@'
import av
from pathlib import Path

video = Path(r'C:\path\to\video.webm')
out_dir = video.parent / 'review-frames'
out_dir.mkdir(parents=True, exist_ok=True)

container = av.open(str(video))
stream = container.streams.video[0]
indices = [25, 90, 150]
current = 0
wanted = set(indices)

for frame in container.decode(stream):
    if current in wanted:
        frame.to_image().save(out_dir / f'frame-{current:03d}.png')
    current += 1
    if current > max(indices):
        break

container.close()
'@ | uv run --with av --with pillow -
```

Prefer a white background during review if you are debugging composition quality.

## 5. Sample the right proof moment

Do not default to the final frame. Sample the frame that proves the mechanism.

Use these defaults:

- `compression / squeeze / funnel / clamp / throat / ramp`:
  sample the constrained mid-state, not the released landing.
- `capture / docking / sleeve / aperture / mask / occlusion`:
  sample the frame where the mechanism is still visible around the leader.
- `fork / split / relay / handoff / bridge / weave / arc`:
  sample the transfer frame, not only the start or finish.
- `snap / recoil / edge tension / echo settle`:
  sample the stressed or overshoot frame first, then the resolved landing.
- `counterlift / hinge / bumper / sling / cradle`:
  sample the frame where the support mechanism is visibly causing the motion.

If the first still does not prove the mechanism, resample earlier or later. The wrong proof frame can invalidate a good experiment.

## 6. Critique aggressively

Check these first:

- too much dead space on one side,
- shapes colliding into unreadable clusters,
- accent motion too small to matter,
- guide geometry overpowering the actors,
- target state busier than source state,
- mechanism present in code but not legible in a still,
- colors failing to establish hierarchy.

If the frame still feels like a static exported diagram, the composition is unfinished.

# Patch Guide

Patch in this order:

1. spacing
2. hierarchy
3. mechanism visibility
4. motion path
5. cleanup

Do not add text before exhausting those fixes.

## General fixes

- move the landing composition toward the center of interest,
- simplify the final frame,
- enlarge the accent pulse,
- reduce ghost opacity,
- shorten or lengthen guides,
- strengthen the active zone if the frame uses negative space,
- remove any device that remains after it has already explained the motion.

## Mechanism-specific fixes

### Path and transfer

- keep the path visible through the transfer, not only before it,
- separate leader and supports more decisively,
- preserve a readable entrance, bridge, slot, or crossing,
- split one path into explicit legs when the handoff must be staged.

### Compression and pressure

- tighten the constrained phase more than feels necessary,
- narrow the neck, lane, throat, corridor, or clamp gap,
- sample an earlier proof frame if the release weakens the pressure,
- keep support forms away from the squeeze zone.

### Reveal and conceal

- keep the reveal device visible during the proof frame,
- narrow the leader mid-state so it feels contained,
- delay supports so the reveal or capture owns the beat,
- remove the device before the resolved landing.

### Support and force

- delay support motion until the leader reaches the mechanism,
- make beams tilt enough to read as load transfer,
- stretch the dominant form more when tension is the point,
- keep anchors, pivots, or bumpers visibly separate from the leader.

### Landing and arrangement

- make size contrast more obvious,
- increase angular spacing in fan layouts,
- push edge landings closer to the boundary if tension is the point,
- let the lead form arrive first when the scene depends on delayed settle,
- remove orbital or staging scaffolding before the final frame.

# Quality Checklist

Ship the video only if most of these are true:

- the structure reads without labels,
- the palette is disciplined,
- one accent motion clearly carries the beat,
- the final frame feels resolved,
- sampled frames look intentional on their own,
- the video would still make sense once narration is added later.

## Mechanism checklist

- if the scene uses negative space, the active zone is strong enough to justify it.
- if the scene uses a mask, aperture, sleeve, or capture pocket, the device is visible during the proof frame and absent in the final landing.
- if the scene uses rhythm markers, they pace the scene without becoming the main subject.
- if the scene uses counter-motion, each side keeps a distinct role.
- if the scene uses scale hierarchy, the size contrast is obvious at first glance.
- if the scene uses orbit motion, the anchor stays stable and the orbital scaffold disappears before the landing.
- if the scene uses compression or squeeze, the constrained phase is visibly tighter than both source and destination.
- if the scene uses edge tension, the dominant form creates pressure near the frame boundary without accidental clipping.
- if the scene uses occlusion, one layer clearly reveals another rather than simply covering it.
- if the scene uses hinge, latch, anchor, pivot, bumper, or sling logic, the mechanism is visible in at least one proof frame and gone by the landing.
- if the scene uses delayed settle, the lead form lands first and the echo is visible in still frames.
- if the scene uses a fan-out landing, the forms keep enough spacing and angle to read as one designed sweep.
- if the scene uses snap or recoil, the overshoot is large enough to survive a still frame.
- if the scene uses a bridge, slot, or receiver, the entrance or passage remains visible around the leader.
- if the scene uses a fork or split, the trunk remains visible long enough and the branches separate enough to avoid reading as a loose regroup.
- if the scene uses a funnel merge, multiple inputs are visibly compressed inside a narrowing neck before the dominant landing.

# Common Failure Patterns

When the first pass looks weak, it is usually because of one of these:

- the mechanism exists but is too subtle to survive a still frame,
- support forms move too early and steal the beat,
- the guide or device remains too long and contaminates the landing,
- the mid-state is not compressed, tilted, stretched, or separated enough,
- the final frame is busier than the mechanism frame,
- the chosen proof frame is wrong even though the motion itself is good.

# Output Expectation

For each experiment:

1. create or update a spike,
2. render the video,
3. extract proof frames,
4. iterate at least once if the first pass is not clearly decent,
5. record what worked and what failed in `.specs/knowledge/`,
6. fold recurring lessons back into this skill instead of letting them accumulate only in the note.
