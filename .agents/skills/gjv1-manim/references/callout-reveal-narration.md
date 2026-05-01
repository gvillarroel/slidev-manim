# Callout And Reveal Narration

Use this reference when a scene needs Manim indication animations or text reveal effects to guide narration.

## Best Use

- Treat a callout as a receiver-caused event. Show a faint target slot, pending state, or local frame before the callout animation lands.
- Use `Circumscribe` for a selected object that must stay readable in a still frame.
- Use `Indicate` for a short confirmation pulse after the selected object is already known.
- Use `Flash` for an arrival or decision instant, not for a sustained explanation.
- Use `FocusOn` only when dimming the context helps a voiceover phrase isolate one point. Do not leave the dimming residue in the final hold.
- Use `Broadcast` for status propagation from a focal point. Keep the focal object visible and remove residual rings before the resolved state.
- Use `Write` for a small final label or token after the visual mechanism has already explained the change.

## Pattern

1. Establish the full structure without motion and hold it for the opening breath.
2. Add a faint receiver cue around the target before the route pulse or callout begins.
3. Move the active accent into the receiver, then run the callout on that receiver only.
4. Convert the callout into a durable state mark, such as a small token, rule, or filled slot.
5. Remove temporary flashes, dimming overlays, receiver slots, and route guides before the final hold.

## Avoid

- Running several indication animations in parallel just to show available effects.
- Flashing every object when the narration needs one active object.
- Using `Wiggle` or `ApplyWave` on text-heavy objects; the intermediate frames often become less readable than a still callout.
- Leaving `Broadcast` rings, focus overlays, or circumscribe outlines after they stop causing the motion.
- Revealing explanatory text before the shape, route, or receiver cue has done the narrative work.

## Proof Frames

Sample at least these moments:

- opening breath with the receiver cue visible,
- arrival frame where the accent reaches the receiver,
- callout frame with the target still readable,
- final hold after all temporary attention scaffolds are removed.
