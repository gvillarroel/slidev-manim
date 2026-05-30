# Component GIF Catalog

This catalog collects every component GIF generated so far for the shared
Manim component library. Regenerate the current set with:

```powershell
uv run --script spikes/component-library-demos/main.py --quality low
```

Source demos live in `spikes/component-library-demos/`. Full render outputs
live in `videos/component-library-demos/components/`. Doc-ready GIFs live in
`.specs/assets/component-demos/`.

## Current Components

| Component | Demo | Notes |
| --- | --- | --- |
| Receiver Slot | ![Receiver slot](../.specs/assets/component-demos/receiver-slot.gif) | Reusable receiver slot with a pending outline, moving payload, and resolved terminal mark. |
| Terminal Brackets | ![Terminal brackets](../.specs/assets/component-demos/terminal-brackets.gif) | Separated corner marks used as a terminal resolved-state cue. |
| Bridge Lane | ![Bridge lane](../.specs/assets/component-demos/bridge-lane.gif) | Guided transfer lane between source and destination zones. |
| Rhythm Gate | ![Rhythm gate](../.specs/assets/component-demos/rhythm-gate.gif) | Prepared gates that open in sequence to make cadence visible. |
| Time Rail | ![Time rail](../.specs/assets/component-demos/time-rail.gif) | Left-side timeline rail that narrates progressive card activation. |
| Mask Window | ![Mask window](../.specs/assets/component-demos/mask-window.gif) | Moving mask window that reveals transferred outputs. |

## Receiver Slot

Reusable receiver slot with a pending outline, moving payload, and resolved
terminal mark.

![Receiver slot](../.specs/assets/component-demos/receiver-slot.gif)

## Terminal Brackets

Separated corner marks used as a terminal resolved-state cue.

![Terminal brackets](../.specs/assets/component-demos/terminal-brackets.gif)

## Bridge Lane

Guided transfer lane between source and destination zones.

![Bridge lane](../.specs/assets/component-demos/bridge-lane.gif)

## Rhythm Gate

Prepared gates that open in sequence to make cadence visible.

![Rhythm gate](../.specs/assets/component-demos/rhythm-gate.gif)

## Time Rail

Left-side timeline rail that narrates progressive card activation.

![Time rail](../.specs/assets/component-demos/time-rail.gif)

## Mask Window

Moving mask window that reveals transferred outputs.

![Mask window](../.specs/assets/component-demos/mask-window.gif)
