# Repo-Wide Video Audit

Read this when asked to review all generated videos or verify that scripts and rendered outputs match the current visual system.

## Count Promoted Deliverables

Promoted outputs are direct video files under `videos/<spike-name>/`. Ignore Manim internals under `.manim`, `partial_movie_files`, and nested render cache folders.

PowerShell audit:

```powershell
$patterns = @('*.webm','*.mp4','*.mov','*.mkv')
$all = Get-ChildItem -Path videos -Recurse -File -Include $patterns | Sort-Object FullName
$promoted = $all | Where-Object {
  $_.FullName -notmatch '\\.manim\\' -and
  $_.FullName -notmatch '\\partial_movie_files\\' -and
  $_.Directory.Parent.FullName -eq (Resolve-Path videos).Path
}
"promoted_deliverables=$($promoted.Count)"
$promoted | Group-Object Extension | ForEach-Object { "$($_.Name) $($_.Count)" }
```

Always include promoted non-WebM files. Legacy MP4 compatibility exports can silently drift from the current script.

## Generate Contact Sheets

Use the bundled example:

```powershell
uv run --with av --with pillow .agents/skills/gjv1-manim/examples/contact-sheet-review.py --root .
```

Useful smoke test:

```powershell
uv run --with av --with pillow .agents/skills/gjv1-manim/examples/contact-sheet-review.py --root . --limit 4 --output videos/review-sheets/gjv1-audit-smoke.png
```

## Prioritize Edge and Center Risks

Run the frame-safety audit before deciding which contact-sheet thumbnails need full-size inspection:

```powershell
uv run --with av --with pillow .agents/skills/gjv1-manim/examples/frame-safety-audit.py --root .
```

This writes:

```text
videos/review-sheets/frame-safety-audit/frame-safety-audit.json
videos/review-sheets/frame-safety-audit/frame-safety-audit.png
```

Treat these as candidates, not verdicts. The audit intentionally flags near-edge text, panel borders, chips, and off-center compositions so the next step is a full-size frame review.

## Automated Composition Audit

For a specific rendered video with camera work, large panels, SVG clusters, or tight transforms, run the denser pixel audit:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --cadence 0.5 --write-overlays
```

Use exact timestamps when a reviewer points to a failure:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-composition-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
```

Read `composition-audit/report.md` first, then open overlay PNGs for blocking findings. Blocking defaults are low visual margin and off-center content. Stray vertical fragments are notices by default because stage panels, scaffolds, and route guides can be intentional; use `--strict-stray` when the suspected issue is unsupported side residue. Possible overlap or crowding is also a notice by default; use `--strict-notices` when dense overlap is unacceptable for the scene.

## Automated Crowding Audit

Use the stricter crowding audit when SVG clusters, clamps, guides, or panel outlines may be visually touching actors even if the whole frame has adequate margins:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --cadence 0.5 --write-overlays
```

For a reviewer-called timestamp, inspect the exact second and the surrounding transition:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --times 14 --write-overlays
uv run --script .agents/skills/gjv1-manim/scripts/frame-crowding-audit.py --video videos/<spike-name>/<video-name>.webm --start 12 --end 16 --cadence 0.5 --write-overlays
```

Treat `low_component_clearance` findings as blocking for actor-to-guide, actor-to-outline, and actor-to-actor pairs. Actor-to-support overlap is often intentional in imported SVGs or labels inside a body, so confirm that case visually before patching.

## Confirm VP9 Alpha

For transparent WebM deliverables, check both stream metadata and a decoded alpha frame. Metadata such as `alpha_mode=1` confirms intent, but an extracted alpha image confirms the promoted file still contains transparent pixels.

If system `ffmpeg` is not on `PATH`, use `imageio-ffmpeg`. If `alphaextract` reports missing planes, force the VP9 decoder:

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

A useful transparent clip should show an extrema range with both transparent and opaque values, for example `(0, 255)`.

## Audit Rest-State Geometry

When a video looks cut off at a held state, use the mobject geometry audit before guessing at camera numbers. It runs the scene with skipped animations, captures each `wait()`, and compares visible mobject bounds against the active camera frame:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/resting-mobject-audit.py --scene-file spikes/<spike-name>/main.py --scene-class <SceneClass> --out-dir videos/<spike-name>/resting-mobject-audit
```

For scenes that download or generate local assets during `main()`, pass setup hooks:

```powershell
uv run --script .agents/skills/gjv1-manim/scripts/resting-mobject-audit.py --scene-file spikes/svg-repo-video-lab/main.py --scene-class SvgRepoVideoLabScene --setup-call ensure_raw_assets --setup-call ensure_generated_variants --out-dir videos/svg-repo-video-lab/resting-mobject-audit
```

Treat `outside_frame`, `low_edge_clearance`, and `off_center_rest_content` as blocking for rest holds. Add `--check-pairs` only when sibling mobject collisions are the suspected issue; parent panels, labels, and imported SVG internals frequently overlap by design.

## Review Criteria

Check these for every sheet:

- Are there stale exports with old colors?
- Do text-heavy clips have a local `page-background` stage?
- Are decorative loops intentionally transparent?
- Are title margins visible in thumbnails?
- Do titles, badges, chips, or callouts have their own safe header band instead of touching the frame or diagram panels?
- Are primary colors serving semantic roles instead of arbitrary decoration?
- Does at least one sampled frame prove the intended mechanism?
- Do automated composition audit overlays show adequate active margins and no residual side fragments?

## Final Report

Include:

- promoted deliverable count by extension,
- contact sheet paths,
- rest-state mobject audit report paths when held frames, camera focus, or final holds were involved,
- composition audit report paths when camera framing, panels, SVG clusters, or overlaps were involved,
- crowding audit report paths when actors, guides, outlines, clamps, or dense SVG clusters were involved,
- VP9 alpha metadata and alpha-extraction result for transparent WebM deliverables,
- scripts patched,
- render commands run,
- syntax and token checks,
- any intentionally transparent clips left unchanged.
