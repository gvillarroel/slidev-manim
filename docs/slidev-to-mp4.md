# Slidev deck to MP4

This repository includes a small wrapper that exports a Slidev deck as PNG frames and then assembles those frames into an MP4 with `ffmpeg`.

```bash
scripts/slidev-to-mp4.sh spikes/circle-left-to-right/slides.md videos/circle-left-to-right.mp4
```

Useful options are environment variables:

```bash
WITH_CLICKS=1 SLIDE_SECONDS=3 FPS=30 SIZE=1920x1080 \
  scripts/slidev-to-mp4.sh slides.md videos/deck.mp4
```

Requirements:

- Node dependencies installed (`npm install` or `pnpm install`)
- `ffmpeg` in `PATH`

The script keeps temporary PNG exports out of the repository and writes the final video wherever the second argument points.
