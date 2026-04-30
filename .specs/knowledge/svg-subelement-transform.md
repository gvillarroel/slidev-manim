---
id: KNOW-0005
title: SVG subelement transform in Manim
status: active
date: 2026-04-29
---

# Summary

Hand-authored SVGs with stable group ids can be transformed in Manim as semantic components instead of being imported as one opaque shape.

# Learned Points

1. Keep each transformable SVG role in a top-level `<g id="...">` container.
2. Extract each role into a fragment SVG before loading it with `SVGMobject`; this preserves a clear mapping from source role to target role.
3. Delete-only roles should have no matching target role. Animate them out separately before transforming the surviving roles.
4. Chained stages work best when each stage keeps the same ids for surviving roles, even if the geometry changes completely.
5. A proof frame should show the removed role absent, the compressed intermediate state, and the clean final symbol.
6. Increasing the scale of the SVG roles after the first review helped the still frames read better on a 16:9 slide canvas.
7. Direct `ReplacementTransform` from a filled rounded SVG body to an open stroked SVG path produced ambiguous background geometry around the handoff frame.
8. `FadeTransform` avoided one artifact but created a large translucent plate, so it was not a good default for this case.
9. A path-normalized intermediate body looked promising but left a persistent horizontal source stroke in the final frame.
10. For topologically incompatible SVG roles, use an explicit semantic handoff: remove the old role and create the new role, while reserving direct morphs for compatible roles.
11. One-second review missed a half-second ambiguity where the scene briefly lost or overlapped its main body during the final handoff.
12. The clearer staging is body-first: replace the incompatible body role first, then move compatible child roles after the target body exists.
13. Full-size frame inspection matters after contact sheets. A shape that looked like body residue in thumbnails was actually the intended `slot` role still in its rectangular source form.

# Practical Rule

For `SVG -> fragment SVGs -> Manim`, prefer this pipeline:

- author or export SVG stages with stable top-level role ids,
- extract one fragment per role using the same source `viewBox`,
- use `ReplacementTransform` for shared roles,
- use `FadeOut` for delete-only roles,
- use `FadeOut` plus `Create` when a shared role changes from filled closed geometry to open stroked geometry,
- stage incompatible body replacement before moving smaller shared roles so they do not appear to float without a container,
- review extracted frames on a white background before accepting the render.
