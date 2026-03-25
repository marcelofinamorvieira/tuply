# DatoCMS Clippy - April Fools 2026

**It looks like you're trying to use a headless CMS. Would you like help with that?**

A Chrome extension that brings back the beloved office assistant experience — this time as DatoCMS's very own animated mascot. A friendly, D-shaped, coral-orange companion that greets you on every DatoCMS admin page, offers "helpful" documentation links, performs groundbreaking "AI Analysis" of your project, and eagerly collects your feedback.

Built as DatoCMS's April Fools 2026 joke. A parody of Microsoft's Clippy, reimagined for the modern headless CMS era.

## What It Does

When you visit any `*.admin.datocms.com` page, the mascot:

1. **Slides in** with a wave and a cheerful "Welcome to DatoCMS!"
2. **Asks** what you want to learn about today
3. Offers three options:
   - **Documentation** — links to actual DatoCMS docs (Content modeling, Media & assets, GraphQL API)
   - **AI Analysis** — "analyzes" your project for 15 seconds with a thinking animation and loading bar, then triumphantly announces: *"This is definitely a DatoCMS project."*
   - **Send feedback** — a fake feedback form with a writing animation (the mascot takes notes!)
4. **Idles** with a gentle breathing animation between interactions

## The Mascot

Seven animation states, all AI-interpolated from 12fps to 48fps for buttery smooth playback:

| Animation | Description |
|---|---|
| Wave | Entrance greeting |
| Talk | Explaining things with enthusiasm |
| Idle | Breathing quietly, waiting to help |
| Think | Deep in thought during "AI Analysis" |
| Eureka | The big reveal moment |
| Write | Taking notes on your feedback |
| Celebrate | Thanking you for feedback |

Animations are generated with [Motchi](https://motchi.art/) as Lottie JSON files with embedded PNG frames, then processed through our custom pipeline.

## Project Structure

```
.
├── manifest.json                 # Chrome Extension manifest (MV3)
├── content-script.js             # All logic: dialogue tree, animation state machine, UI
├── assets/
│   ├── lottie.min.js             # Bundled lottie-web player (v5.12.2)
│   ├── mascot-idle.json          # Idle breathing animation (48fps)
│   ├── mascot-wave.json          # Waving hello animation (48fps)
│   ├── mascot-talk.json          # Talking animation (48fps)
│   ├── mascot-think.json         # Thinking animation (48fps)
│   ├── mascot-eureka.json        # Eureka/discovery animation (48fps)
│   ├── mascot-write.json         # Writing/note-taking animation (48fps, baked ping-pong)
│   ├── mascot-celebrate.json     # Celebration animation (48fps)
│   └── backups/                  # Original animations before recoloring
├── scripts/
│   ├── interpolate_lottie.py     # AI frame interpolation pipeline (RIFE)
│   ├── recolor_lottie.py         # Hue-shift recoloring script
│   ├── rife-ncnn-vulkan/         # RIFE binary + models (not committed)
│   └── build_animated_mascot.py  # Legacy SVG mascot builder
```

## Installing

1. Clone this repo
2. Open `chrome://extensions/` in Chrome
3. Enable **Developer mode**
4. Click **Load unpacked** and select the project folder
5. Navigate to any DatoCMS admin page

## How It Works

### Architecture

The extension is a single content script injected on DatoCMS admin pages. Everything runs inside a **Shadow DOM** to isolate styles from the host page.

The dialogue system is a **state machine** defined as a plain config object. Each state has:
- A message to display
- An animation to play (with optional looping, segments, or auto-advance)
- Options (buttons/links) or custom content (feedback form, loading bar)

### Animation Pipeline

Source animations from Motchi come as raster Lottie files (embedded PNG frames) at 12fps. Our pipeline makes them production-ready:

1. **Frame interpolation** — `scripts/interpolate_lottie.py` uses [RIFE](https://github.com/nihui/rife-ncnn-vulkan) (AI video frame interpolation) to go from 12fps to 48fps
2. **Alpha preservation** — Frames are split into RGB + alpha channels, interpolated separately, then recombined (RIFE doesn't handle transparency natively)
3. **Alpha sharpening** — A levels adjustment crisps up soft edges from the interpolation
4. **Recoloring** — `scripts/recolor_lottie.py` hue-shifts the shoe color from blue (#0081DC) to purple (#6200C4) across all frames
5. **Segment baking** — The writing animation has its ping-pong loop baked directly into the frame sequence for jitter-free looping

### Dialogue Tree

```
greeting ("Welcome to DatoCMS!")
  └─ wave animation
      └─ menu ("What do you want to learn about today?")
          ├─ Documentation → docs submenu → links to real docs
          ├─ AI Analysis → 15s loading bar → "This is definitely a DatoCMS project."
          └─ Send feedback → textarea + writing animation → "Thank you!"
```

### Special Animation Behaviors

- **Ping-pong idle**: The idle animation plays forward then backward seamlessly since the source animation doesn't loop
- **Segment-based writing**: Intro (getting notepad) plays once, then only the middle writing portion loops, avoiding the repetitive notepad grab
- **Timed AI analysis**: The thinking animation loops for exactly 15 seconds while a loading bar fills up, then auto-advances to the result
- **Cross-fade transitions**: All animation swaps use a 250ms fade to avoid jarring cuts

## Build Scripts

### Frame Interpolation

```bash
# One-time setup: download RIFE
cd scripts
curl -sL "https://github.com/nihui/rife-ncnn-vulkan/releases/download/20221029/rife-ncnn-vulkan-20221029-macos.zip" -o rife.zip
unzip -q rife.zip && mv rife-ncnn-vulkan-20221029-macos rife-ncnn-vulkan && rm rife.zip
chmod +x rife-ncnn-vulkan/rife-ncnn-vulkan

# Interpolate an animation (12fps → 24fps per pass, run twice for 48fps)
python3 scripts/interpolate_lottie.py assets/mascot-idle.json --alpha-low 80 --alpha-high 175 --no-loop
python3 scripts/interpolate_lottie.py assets/mascot-idle.json --alpha-low 80 --alpha-high 175 --no-loop
```

### Recoloring

```bash
# Shift shoe color from blue to purple across all animations
python3 scripts/recolor_lottie.py assets/mascot-*.json --from-color 0081DC --to-color 6200C4

# Revert to originals
cp assets/backups/*.json assets/
```

## Dependencies

| Dependency | Purpose | Bundled? |
|---|---|---|
| [lottie-web](https://github.com/airbnb/lottie-web) 5.12.2 | Renders Lottie animations in the browser | Yes |
| [rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan) | AI frame interpolation (build-time) | No |
| [Pillow](https://python-pillow.org/) | Image processing for interpolation pipeline | No |
| [NumPy](https://numpy.org/) | Fast pixel manipulation for recoloring | No |
| Python 3.8+ | Runs build scripts | No |

## Credits

- Mascot animations generated with [Motchi](https://motchi.art/)
- Frame interpolation powered by [RIFE](https://github.com/hzwer/ECCV2022-RIFE) via [rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan)
- UI styled to match [DatoCMS brand guidelines](https://www.datocms.com/company/brand-assets)
- Spiritual successor to [Clippy](https://en.wikipedia.org/wiki/Office_Assistant) (1997-2007), gone but never forgotten
