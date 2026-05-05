---
title: Device Frame Embed
summary: Slidev spike for embedding transparent Manim videos inside browser and device frames.
---

# Device Frame Embed

This spike tests whether a transparent Manim animation still reads well when Slidev wraps it in a browser-like frame or a device mockup.

## Run the render

From the repository root:

```bash
uv run --script spikes/device-frame-embed/main.py
```

This writes the rendered assets to:

```text
videos/device-frame-embed/
```

Expected outputs:

```text
videos/device-frame-embed/device-frame-embed-browser.webm
videos/device-frame-embed/device-frame-embed-browser.png
videos/device-frame-embed/device-frame-embed-device.webm
videos/device-frame-embed/device-frame-embed-device.png
videos/device-frame-embed/review-frames-0.3s/browser/sheets/
videos/device-frame-embed/review-frames-0.3s/device/sheets/
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/device-frame-embed/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/device-frame-embed/slides.md
```

## Learnings

- Keep the browser or device chrome in Slidev, not inside the Manim asset, so the animation stays reusable.
- Separate wide and tall renders when the frame shape changes; the framing is easier to control than relying on one crop.
- Transparent WebM plus a white PNG poster remains the most practical delivery pair for review and playback.
- Local Vite imports and per-slide readiness state make embedded media more reliable in Slidev.
- Keep the Slidev template simple when combining raw HTML with embedded media; fewer wrappers means fewer parser issues.
- Build the wide and tall Manim compositions independently. The tall device version needs larger vertical spacing and stronger card scale than the browser version, or the asset turns into a tiny center icon inside the phone chrome.
- Use one primary-red pulse for the handoff and neutral gray content cards. Extra source, processor, and receipt colors compete with the Slidev frame and weaken the transparent asset.
- Generate 0.3-second alpha-on-white review frames for each promoted aspect ratio so the embed can be judged without opening the Slidev deck.
