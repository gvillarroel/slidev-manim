---
id: component-library-demos
title: Component library demos
status: active
---

# Component Library Demos

This spike renders short demos for reusable components from `spikes/_common`.
The GIFs are copied to `.specs/assets/component-demos/` so documentation can
embed stable previews, while the full render outputs stay under
`videos/component-library-demos/`.

Run:

```powershell
uv run --script spikes/component-library-demos/main.py --quality low
```

Render one component:

```powershell
uv run --script spikes/component-library-demos/main.py --component bridge-lane
```

