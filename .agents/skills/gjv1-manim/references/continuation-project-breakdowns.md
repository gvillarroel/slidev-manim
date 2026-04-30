# Continuation Project Breakdowns

Use this when a Manim scene continues from a resolved diagram into a second-column breakdown, roadmap, or generated subproject list.

## Visual Hypothesis

If the prior resolved state stays visible as a compact input and the destination blocks appear progressively, the continuation reads as generated from the previous explanation rather than as a separate slide pasted onto the end.

## Composition Pattern

1. Keep the resolved source composition visible on the left as a compact input panel.
2. Add visible destination scaffolds in the output column before any detailed list text appears.
3. Draw the trunk or branch guide from the source toward the output column.
4. Activate the first large block, then reveal its keypoints one row at a time.
5. Activate the second large block, then reveal its keypoints one row at a time.
6. Fade or soften guide geometry only after both blocks are populated.
7. Hold the final state for 5 to 7 seconds.

## Styling

- Use a neutral local stage for any text-heavy continuation.
- Use black, gray, or primary-red header bands for the large output blocks by default.
- Use small primary-red or grayscale keypoint marks. Use the wider palette only when the user asks for color or the breakdown needs categorical separation.
- Keep the prior composition smaller than the output blocks so the new result owns the final frame.
- Keep text concise enough that each row fits without scaling with viewport width.
- Keep block edges straight and square.

## Scaffolds

Scaffolds should balance the frame before content appears. They must be visible enough to survive full-size frame review and automated composition audits.

Useful defaults:

- panel stroke: `GRAY_300` or stronger,
- panel fill: white at moderate opacity,
- header hint: a short straight gray bar,
- z-index below real block content,
- remove or replace each scaffold as its real block appears.

Avoid purely atmospheric haze. If the audit ignores the scaffold, the setup frame can still be flagged as off-center even when the composition looks acceptable in motion.

## Proof Frames

Sample these exact moments:

- setup with resolved input plus output scaffolds,
- first block populated,
- fork visible while second block activates,
- both blocks populated,
- final hold after guide softening.

Run:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike>/<video>.webm --times "<setup>,<first>,<fork>,<both>,<hold>" --write-overlays
```

`possible_overlap_or_crowding` is expected for compact imported SVG inputs and should be inspected full size. Treat `low_visual_margin`, `stray_vertical_fragment`, and unresolved `off_center_content` as blocking.

## Poster

When the continuation changes the terminal state, update the poster composition in the same patch. The promoted PNG should show the new final hold, not the previous video endpoint.

## Alpha Validation

For transparent VP9 WebM, check both metadata and an extracted alpha frame. On Windows, `ffmpeg` may not be on `PATH`; use `imageio-ffmpeg` if needed. If `alphaextract` fails with missing planes, force the VP9 decoder and alpha format:

```powershell
@'
import subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
video = Path(r'videos/<spike>/<video>.webm')
out = video.parent / 'review-frames' / 'alpha-check-frame.png'
out.parent.mkdir(parents=True, exist_ok=True)

subprocess.run(
    [
        ffmpeg,
        '-hide_banner',
        '-loglevel',
        'error',
        '-c:v',
        'libvpx-vp9',
        '-i',
        str(video),
        '-frames:v',
        '1',
        '-vf',
        'format=yuva420p,alphaextract',
        str(out),
    ],
    check=True,
)

print(Image.open(out).convert('L').getextrema())
'@ | uv run --with imageio-ffmpeg --with pillow -
```

Expected useful output for a transparent clip is an alpha extrema range with both transparent and opaque values, such as `(0, 255)`.
