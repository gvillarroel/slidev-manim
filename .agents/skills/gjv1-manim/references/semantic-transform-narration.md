# Semantic Transform Narration

Use this reference when a Manim scene uses `Transform`, `ReplacementTransform`, `TransformFromCopy`, `FadeTransform`, `TransformMatchingShapes`, `TransformMatchingTex`, or `MoveToTarget` as narration devices rather than as generic morphs.

## Narrative Roles

- Use `Transform` when the same actor should visibly keep identity while changing state. Keep the actor count low, and make the before/after silhouettes compatible enough that the in-between frame still reads as one object.
- Use `MoveToTarget` when a whole actor or group needs a planned relocation, compression, or restyle. Show destination scaffolding first so the move feels intentional.
- Use `TransformFromCopy` when the source must remain available while a derived copy travels to a new role. Hold a proof frame where both the original and the copy are visible.
- Use `ReplacementTransform` when a temporary proof, guide, or intermediate object should become the resolved object with no duplicate residue left behind.
- Use `TransformMatchingShapes` for rearrangements where identical shapes or repeated glyphs should preserve continuity. Keep unmatched parts few, or the transition becomes a noisy regroup.
- Use `TransformMatchingTex` for formulas when matching tokens carry mathematical meaning. Split the expression into explicit tokens and color or space them so the preserved symbols are readable in the middle frame.
- Prefer additive or near-in-place `TransformMatchingTex` changes for narration. If a formula must be severely reordered, split it into smaller beats or add visible landing slots; a single crossing reorder often turns the proof frame into token soup.
- Use `FadeTransform` when topology or meaning changes enough that direct morphing would imply false identity. Fade the incompatible source out while the target lands cleanly.

## Proof Frames

Sample more than the final frame. A semantic-transform scene needs at least these checks:

- opening breath with destination slots or scaffolds visible,
- source-plus-copy handoff frame for `TransformFromCopy`,
- matching-parts mid-frame for `TransformMatchingShapes` or `TransformMatchingTex`,
- topology-break frame for `FadeTransform`,
- final hold after all guides, source ghosts, and duplicate intermediates are gone.

For matching transforms, extract half-second frames. One-second samples can miss brief morph soup where unmatched pieces cross through each other.

## Composition Pattern

1. Establish a source actor and a quiet destination scaffold.
2. Preserve identity with `Transform` or `MoveToTarget` only while the concept still means the same thing.
3. Derive or hand off evidence with `TransformFromCopy`, and hold the copy beside the original long enough to prove the relationship.
4. Promote the transient proof with `ReplacementTransform`; do not leave a temporary value over final text.
5. Use matching transforms only for repeated shapes, repeated formula tokens, or rearrangements where the preserved identity is the point.
6. Break identity with `FadeTransform` when the source and target have incompatible topology.
7. Remove guide rails, source slots, and faded residues before the final hold.

## Failure Patterns

- A direct `Transform` across unrelated topology creates a false continuity and often produces translucent plates, crossing strokes, or unreadable mid-shapes.
- `TransformMatchingShapes` on dense words can look like letter soup unless the scene isolates a small number of repeated parts.
- `TransformMatchingTex` works best when the expression is deliberately tokenized. If a long formula is one undifferentiated string, the match is technically correct but narratively weak.
- `TransformFromCopy` loses its explanatory value if the original source fades before the copy lands.
- `MoveToTarget` looks like a generic slide if the target state is not visible or implied before motion starts.
- Lingering guides after a `ReplacementTransform` can make the final hold feel unfinished even when the replacement itself is correct.

## LaTeX-Free Lab Pattern

Use real `MathTex` for production formula scenes when a LaTeX toolchain is available. For a portable spike that must still exercise `TransformMatchingTex`, create small `Text` tokens and attach a `tex_string` attribute to the token and its glyph submobjects before calling `TransformMatchingTex`. This preserves the class's token-matching behavior without making the spike depend on external LaTeX binaries.
