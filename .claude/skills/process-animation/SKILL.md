---
name: process-animation
description: Run the full animation pipeline on a new Lottie file — interpolate to 48fps, recolor shoes to purple, optimize file size. Use when adding a new mascot animation from Motchi/Anirive.
disable-model-invocation: true
---

Process a new Lottie animation through the full pipeline. The user provides a source file path or URL as `$ARGUMENTS`.

## Steps

1. **Copy/download** the source Lottie to `assets/mascot-NAME.json` (ask the user for the animation name if not obvious from context)

2. **Inspect** the source:
   ```bash
   python3 -c "import json; d=json.load(open('assets/mascot-NAME.json')); print(f'{d[\"fr\"]}fps, {d[\"op\"]} frames, {d[\"w\"]}x{d[\"h\"]}')"
   ```

3. **Interpolate** (two passes, 12fps → 24fps → 48fps):
   ```bash
   python3 scripts/interpolate_lottie.py assets/mascot-NAME.json --alpha-low 80 --alpha-high 175 --no-loop
   python3 scripts/interpolate_lottie.py assets/mascot-NAME.json --alpha-low 80 --alpha-high 175 --no-loop
   ```

4. **Recolor** shoes from blue to purple:
   ```bash
   python3 scripts/recolor_lottie.py assets/mascot-NAME.json --from-color 0081DC --to-color 6200C4
   ```

5. **Optimize** (downscale + compress):
   ```bash
   python3 scripts/optimize_lottie.py assets/mascot-NAME.json --size 256 --quality 60-80
   ```

6. **Register** in `manifest.json` under `web_accessible_resources`

7. **Add** the animation key to the `ANIMS` object in `content-script.js`

8. **Report** final frame count, fps, duration, and file size
