# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chrome extension (MV3) that displays an animated Clippy-parody mascot ("Tuply") on DatoCMS admin pages. April Fools 2026 joke. No build step — load unpacked in Chrome. No package.json, no npm commands.

## Architecture

- All extension logic lives in `content-script.js` (single file). The dialogue tree is a config object (`DIALOGUE`) at the top — add new states there.
- UI renders inside a Shadow DOM for style isolation. CSS is inline in the `styles` template literal.
- Animations are raster Lottie files (embedded base64 PNGs), played with bundled lottie-web 5.12.2.
- `manifest.json` must list every animation JSON in `web_accessible_resources`.

## Animation Pipeline

When adding a new animation, always run the full pipeline in order:

```bash
# 1. Interpolate: two passes (12fps → 24fps → 48fps)
python3 scripts/interpolate_lottie.py assets/mascot-NAME.json --alpha-low 80 --alpha-high 175 --no-loop
python3 scripts/interpolate_lottie.py assets/mascot-NAME.json --alpha-low 80 --alpha-high 175 --no-loop

# 2. Recolor shoes from blue to purple
python3 scripts/recolor_lottie.py assets/mascot-NAME.json --from-color 0081DC --to-color 6200C4

# 3. Optimize (downscale 512→256px + pngquant compression)
python3 scripts/optimize_lottie.py assets/mascot-NAME.json --size 256 --quality 60-80
```

Python dependencies: `Pillow`, `numpy`. CLI tool: `pngquant` (brew install). RIFE binary at `scripts/rife-ncnn-vulkan/` (download per README).

## Key Gotchas

- **Ping-pong loops must be baked into frames** — lottie's runtime `setDirection`/`playSegments` loop causes visible jitter. Duplicate reversed frames directly in the Lottie JSON (see mascot-sad.json, mascot-write.json for examples).
- **Alpha channel handling** — RIFE destroys transparency. The interpolation script splits RGB+alpha, interpolates separately, recombines with sharpening (`--alpha-low 80 --alpha-high 175`).
- **Recoloring from backups** — Always `cp assets/backups/*.json assets/` before recoloring to a new color. The recolor script is a hue-shift, not idempotent — running it twice shifts hue twice.
- **Animation segments** — For animations that need intro + loop (like writing, sad), use `animSegments` in the dialogue config and `fadeToSegmentAnim()` in JS.
