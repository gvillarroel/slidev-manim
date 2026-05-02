# Data Counter Narration

Use this reference when a scene explains a table-derived value, a live counter, a small chart, or a row-by-row data handoff.

## Narrative Shape

Use a `source row -> side aggregation -> live counter -> destination cell` structure when the viewer needs to understand where a number came from.

1. Establish the table and the counter area before motion begins.
2. Cue the source row with a left marker and a thin bottom rule.
3. Pulse source cells with stroke-only outlines, not filled highlights.
4. Send small tokens from source cells to fixed formula slots.
5. Count only while a result handoff is visibly in flight.
6. Remove or soften side mechanisms before the final hold unless they still explain the result.

## Tables

Use `MobjectTable` when entries need native `Text` styling, non-LaTeX reliability, or per-entry control. It still inherits the useful `Table` row, column, line, and cell helpers.

After constructing a `MobjectTable`, repaint text through the mobject family. Some table assembly paths can leave text with stroke-like or pale fills if the original entry color is trusted without a post-layout pass.

```python
def paint_text(mob, color):
    mob.set_color(color, family=True)
    mob.set_fill(color=color, opacity=1, family=True)
    mob.set_stroke(color=color, width=0, opacity=0, family=True)
```

Prefer a left row marker plus a bottom rule over a row-wide fill band. Filled bands or filled cell highlights compete with the values the narration depends on.

## Source And Formula Handoff

Keep source values readable in place. Do not move enlarged copies over table cells.

Use small red tokens or short route lines to show that values are being handed from source cells into the formula zone. Fade in the formula terms in stable side slots as the tokens arrive. The formula panel should be close enough to read as related, but separated enough that no term covers the source row.

For dense rows, keep the formula in a side panel with:

- fixed slots for each source term,
- stable operator text,
- a restrained result slot,
- enough gutter between the table and the formula route.

## Counters

Use `DecimalNumber` with native `Text` digits when local LaTeX availability is uncertain:

```python
counter = DecimalNumber(
    0,
    num_decimal_places=0,
    group_with_commas=False,
    mob_class=Text,
    font_size=58,
)
```

Use `ChangeDecimalToValue(counter, target)` when the counter should visibly interpolate to a known result. Pair it with `ValueTracker` for progress rails, fills, or secondary indicators, and add the tracker to the scene before relying on updater-driven visuals.

The clearest counter beat usually animates these together:

- a small result token moving from formula result slot to counter,
- `ChangeDecimalToValue`,
- `ValueTracker.animate.set_value(1)`,
- optional chart update.

## Bar Charts

Use `BarChart` only as context, not as the main explanation, unless the chart itself is the lesson. For data-table narration, a small chart can show the active value becoming comparable to prior rows.

`BarChart` creates y-axis numbers internally. If the scene should avoid LaTeX, pass a native label constructor:

```python
chart = BarChart(
    values=[210, 325, 0],
    y_range=[0, 500, 100],
    axis_config={"label_constructor": Text, "font_size": 12},
    tips=False,
)
```

Animate `chart.animate.change_bar_values([...])` in the same play as the counter update when the chart should read as a secondary synchronized witness.

## Cell Cues And Final Landing

Do not use `set_opacity(1)` to reveal `SurroundingRectangle` cell cues if the cue should stay outline-only. `set_opacity` can restore fill opacity and turn a ring into a filled block. Use stroke opacity instead:

```python
ring.set_fill(opacity=0)
ring.set_stroke(opacity=0)
self.play(ring.animate.set_stroke(opacity=1))
```

Before landing a computed value in a destination cell:

- show a destination outline,
- fade or remove placeholder text,
- move the final value through a clear gutter,
- introduce the final value above the outline,
- keep the final value and destination outline both visible in the resolved hold.

Do not `FadeIn` a text mobject whose stored opacity is zero; it will fade to its own invisible target. Either introduce a normally styled copy at landing time or animate opacity on a mobject already in the scene.

After the value has returned from the counter or formula side zone, make the cleanup a deliberate bridge into the final table. Retire side mechanisms, move or scale the table into the resolved center, and sample the transition frames where faded side panels and the growing table overlap. If the default active-color centering audit flags a frame where both the side counter and final table value are visible, inspect it full size before patching; use a slightly wider center tolerance only when the human composition is still balanced.

## Review And Audit Notes

Sample at least these frames:

- opening table and side-zone setup,
- source-row cue,
- formula-ready frame,
- counter handoff mid-count,
- result landing,
- resolved hold after side mechanisms leave.

Run the composition audit at half-second cadence. For table scenes, broad `possible_overlap_or_crowding` notices are common because grid rules and text are intentionally adjacent. Full-size review is required before treating them as defects.

Run targeted crowding audit on source-cue and final-landing frames when outlines or badges surround values. Expect low-clearance notices for intentional text-inside-outline pairs; patch only when the outline touches, covers, or visually competes with the value.
