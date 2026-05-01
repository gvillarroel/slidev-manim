# Narration Timing And Cues

Use this reference when a Manim scene must feel ready for a spoken slide narration, especially when real microphone or TTS audio is not available yet.

## Core Pattern

Treat timing primitives as narration structure:

- `Scene.next_section()` names the edit and slide-integration boundary.
- A lightweight scripted cue object supplies the intended narration duration.
- `Succession` owns strict sentence order.
- `LaggedStart` owns progressive grouped reveals.
- `AnimationGroup` owns simultaneous supporting motion inside one beat.
- `ChangeSpeed` owns one deliberate slow-down, not general polish.
- A final `wait()` holds the resolved frame for the presenter.

The goal is not to show every timing feature in isolation. The goal is to make a viewer feel where the speaker would breathe, build, slow down, and land.

## Scripted Voiceover Durations Without Audio

Use a local tracker-style helper when audio is not ready:

```python
@dataclass(frozen=True)
class ScriptedCue:
    section_name: str
    duration: float
    caption: str

@contextmanager
def scripted_voiceover(self, cue: ScriptedCue):
    start = float(self.time)
    yield cue
    end = float(self.time)
    self.narration_cues.append({
        "section_name": cue.section_name,
        "planned_duration_seconds": cue.duration,
        "actual_duration_seconds": round(end - start, 3),
        "caption": cue.caption,
        "requires_audio_service": False,
    })
```

Then use it like a future voiceover tracker:

```python
self.next_section(name=cue.section_name)
with self.scripted_voiceover(cue) as tracker:
    self.play(Succession(...), run_time=tracker.duration)
```

This keeps the spike deterministic and makes it easy to replace the helper with a real voiceover tracker later.

## Opening Breath

Never spend the opening breath on an empty frame. Add the meaningful structure first, then hold it for 2 to 3 seconds:

```python
self.add(stage, rail, slots, marker)
self.next_section(name="01 opening breath")
with self.scripted_voiceover(opening_cue) as tracker:
    self.wait(tracker.duration)
```

The opening frame should already answer what the viewer is looking at. Use faint slots, a rail, or destination scaffolds so the pause reads as intentional.

## Progressive Beat Groups

Use `Succession` for the sentence-level order and `LaggedStart` for the internal grouped reveal:

```python
self.play(
    Succession(
        AnimationGroup(marker.animate.move_to(first_target), run_time=1.0),
        LaggedStart(*[FadeIn(group) for group in beat_groups], lag_ratio=0.25, run_time=3.0),
        AnimationGroup(final_pulse.animate.scale(1.08), run_time=0.8),
    ),
    run_time=tracker.duration,
)
```

Keep each group visually sparse. The grouped reveal should make narration beats legible, not become a data dashboard.

## Deliberate Slow-Down

Reserve `ChangeSpeed` for the one moment the speaker would slow down. Make the slowdown visible in still frames with a bracket, pause bars, or a strengthened active zone.

When the total duration matters, calculate the inner animation duration from the speed profile:

```python
speedinfo = {0.0: 1.0, 0.4: 1.0, 0.5: 0.15, 0.75: 0.15, 1.0: 1.0}
scale = ChangeSpeed(Wait(run_time=1), speedinfo=speedinfo, rate_func=linear).get_scaled_total_time()
inner_run_time = target_duration / scale

self.play(
    ChangeSpeed(
        AnimationGroup(marker.animate.move_to(target), run_time=inner_run_time),
        speedinfo=speedinfo,
        rate_func=linear,
    )
)
```

Do not use many slowdowns in one slide clip. Multiple slowdowns remove the narrative signal.

## Section Metadata

Use `next_section()` before every narration beat and render with section saving enabled. The resulting section metadata is useful to slide systems, editors, and future audio alignment.

Each section should contain at least one wait or animation. A section that only adds static mobjects can become empty, so add the static composition first and then hold it inside the section.

## Final Hold

After the last meaningful cleanup, hold the resolved frame for 5 to 7 seconds:

```python
self.play(cleanup_and_final_badge, run_time=1.0)
self.wait(6.0)
```

Remove transient timing devices unless they still explain the final state. The final frame should look like a slide can safely sit there while the presenter finishes a sentence.

## Review Checklist

- Total duration is at least 25 seconds for slide integration.
- The first meaningful composition is visible before the opening wait.
- Proof frames include the opening breath, grouped reveal, slowdown proof, section metadata, and final hold.
- Section metadata contains named sections with usable durations.
- Scripted cue durations and actual section durations are close enough to support later audio alignment.
- The local stage is opaque when text, labels, or metadata are present.
- A single primary-red marker or accent carries the timing story.
