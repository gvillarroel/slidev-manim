# Manim 3D Depth Lab

This spike tests a narration-ready use of Manim 3D features: a flat 2D projection appears simple at first, then a staged camera move reveals that the same screen path carries hidden z-depth.

## Hypothesis

3D adds narrative value when the camera reveals a relationship that is invisible from the opening view. The useful beat is not rotation itself; it is the moment when the viewer can compare the fixed 2D projection with the newly visible depth columns, surface ridge, and final stopped 3D view.

## Feature Coverage

- `ThreeDScene` with an intentional top-down opening and 3D resolved hold.
- `ThreeDAxes` as a stable depth frame.
- `Surface` as the hidden relationship being revealed.
- `Sphere` probes and samples for readable point locations.
- `Prism` columns that connect the flat projection to the elevated ridge.
- `set_camera_orientation`, `move_camera`, fixed-in-frame reference overlay, and a short ambient camera rotation used only during the inspection beat.

## Run

```powershell
uv run --script spikes/manim-3d-depth-lab/main.py
```

The command renders:

- `videos/manim-3d-depth-lab/manim-3d-depth-lab.webm`
- `videos/manim-3d-depth-lab/manim-3d-depth-lab.png`

Optional quality override:

```powershell
uv run --script spikes/manim-3d-depth-lab/main.py --quality high
```

## Review Plan

Review the opening, camera tilt, mid-depth proof frame, ambient inspection, and final hold. The frame should fail if the camera movement reads as ornamental rotation, if the depth columns do not explain the height relation, or if the final hold is not readable after the camera stops.
