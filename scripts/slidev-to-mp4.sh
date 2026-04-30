#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/slidev-to-mp4.sh <deck.md> [output.mp4]

Environment variables:
  SLIDE_SECONDS   Seconds per exported slide/click frame. Default: 5
  FPS             Output video frames per second. Default: 30
  SIZE            Output canvas size. Default: 1920x1080
  WITH_CLICKS     Export every Slidev click step when set to 1. Default: 0
  SLIDEV_WAIT     Milliseconds to wait before export. Default: 1000

Examples:
  scripts/slidev-to-mp4.sh spikes/circle-left-to-right/slides.md videos/circle.mp4
  WITH_CLICKS=1 SLIDE_SECONDS=3 scripts/slidev-to-mp4.sh slides.md deck.mp4
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

DECK="$1"
OUT="${2:-deck.mp4}"
SLIDE_SECONDS="${SLIDE_SECONDS:-5}"
FPS="${FPS:-30}"
SIZE="${SIZE:-1920x1080}"
WITH_CLICKS="${WITH_CLICKS:-0}"
SLIDEV_WAIT="${SLIDEV_WAIT:-1000}"

if [[ ! -f "$DECK" ]]; then
  echo "Deck not found: $DECK" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required but was not found in PATH" >&2
  exit 1
fi

if [[ "$SIZE" != *x* ]]; then
  echo "SIZE must look like 1920x1080" >&2
  exit 1
fi
WIDTH="${SIZE%x*}"
HEIGHT="${SIZE#*x}"

TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

if [[ -x "node_modules/.bin/slidev" ]]; then
  slidev_cmd=(node_modules/.bin/slidev)
elif command -v pnpm >/dev/null 2>&1; then
  slidev_cmd=(pnpm exec slidev)
else
  slidev_cmd=(npx slidev)
fi

export_args=(export "$DECK" --format png --output "$TMPDIR/png" --wait "$SLIDEV_WAIT")
if [[ "$WITH_CLICKS" == "1" || "$WITH_CLICKS" == "true" ]]; then
  export_args+=(--with-clicks)
fi

"${slidev_cmd[@]}" "${export_args[@]}"

mapfile -t frames < <(find "$TMPDIR/png" -type f -name '*.png' | sort -V)
if [[ "${#frames[@]}" -eq 0 ]]; then
  echo "Slidev did not export any PNG frames" >&2
  exit 1
fi

mkdir -p "$TMPDIR/frames"
idx=0
for frame in "${frames[@]}"; do
  printf -v numbered "%s/frames/frame-%06d.png" "$TMPDIR" "$idx"
  ln -s "$(realpath "$frame")" "$numbered"
  idx=$((idx + 1))
done
INPUT_RATE="$(LC_ALL=C awk -v d="$SLIDE_SECONDS" 'BEGIN { printf "%.8f", 1 / d }')"

mkdir -p "$(dirname "$OUT")"
ffmpeg -y \
  -framerate "$INPUT_RATE" \
  -i "$TMPDIR/frames/frame-%06d.png" \
  -vf "scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -r "$FPS" \
  -movflags +faststart \
  "$OUT"

echo "Wrote $OUT from ${#frames[@]} exported frame(s)."
