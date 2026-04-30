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

## Review Criteria

Check these for every sheet:

- Are there stale exports with old colors?
- Do text-heavy clips have a local `page-background` stage?
- Are decorative loops intentionally transparent?
- Are title margins visible in thumbnails?
- Do titles, badges, chips, or callouts have their own safe header band instead of touching the frame or diagram panels?
- Are primary colors serving semantic roles instead of arbitrary decoration?
- Does at least one sampled frame prove the intended mechanism?

## Final Report

Include:

- promoted deliverable count by extension,
- contact sheet paths,
- scripts patched,
- render commands run,
- syntax and token checks,
- any intentionally transparent clips left unchanged.
