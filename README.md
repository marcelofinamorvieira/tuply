# Tuply - April Fools 2026

**It looks like you're trying to use a headless CMS. Would you like help with that?**

A Chrome extension that adds **Tuply**, DatoCMS's very own animated AI assistant, to every DatoCMS admin page. A friendly, D-shaped, coral-orange companion that offers "advanced AI operations" and delivers results that are technically correct.

Built as a DatoCMS April Fools 2026 joke. Spiritual successor to [Clippy](https://en.wikipedia.org/wiki/Office_Assistant) (1997-2007), gone but never forgotten.

## What It Does

When you visit any `*.admin.datocms.com` page, Tuply:

1. **Pops in** with a wave and a cheerful "Welcome to DatoCMS!"
2. **Introduces himself**: "I'm **Tuply**, your advanced AI assistant"
3. **Asks** what AI operation you want to use
4. Offers three options:
   - **AI Analysis**: "analyzes" your project for 15 seconds with a thinking animation, loading bar, and rotating status messages, then triumphantly announces: *"This is **definitely** a DatoCMS project."*
   - **Write my content**: furiously writes with a thought bubble, then proudly presents: *"Lorem ipsum dolor sit amet"* with a copy-to-clipboard button
   - **Review my schema**: thinks hard, gets progressively sadder, then delivers: *"Oh my... You should start over."*
5. **Idles** with a gentle breathing animation between interactions

## Install

**Option A: Download from releases**
1. Download `tuply-ext.zip` from the [latest release](https://github.com/marcelofinamorvieira/tuply/releases/latest)
2. Unzip it
3. Open `chrome://extensions/` in Chrome
4. Enable **Developer mode** (top-right toggle)
5. Click **Load unpacked** and select the unzipped `tuply-ext` folder
6. Visit any DatoCMS admin page

**Option B: Clone the repo**
1. `git clone https://github.com/marcelofinamorvieira/tuply.git`
2. Open `chrome://extensions/` in Chrome
3. Enable **Developer mode**
4. Click **Load unpacked** and select the cloned folder
5. Visit any DatoCMS admin page

## The Mascot

Eleven animation states, all AI-interpolated from 12fps to 48fps for buttery smooth playback:

| Animation | Description |
|---|---|
| Wave | Entrance greeting |
| Intro | Self-introduction pose |
| Talk | Explaining things with enthusiasm |
| Idle | Breathing quietly, waiting to help |
| Think | Deep in thought during "AI Analysis" |
| Eureka | The big reveal moment |
| Proud | Smug pride after "discovering" your project is DatoCMS |
| Write | Furiously writing content (segment-based: notepad grab → writing loop) |
| Celebrate | Jumping celebration when presenting content |
| Sad | Progressively sadder after reviewing your schema (baked squint loop) |
| Toss | Throwing away paper after copying content |

Animations are generated with [Motchi](https://motchi.art/) as Lottie JSON files with embedded PNG frames, then processed through our custom pipeline.

## Project Structure

```
.
├── manifest.json                 # Chrome Extension manifest (MV3)
├── content-script.js             # All logic: dialogue tree, animation state machine, UI
├── assets/
│   ├── lottie.min.js             # Bundled lottie-web player (v5.12.2)
│   ├── mascot-idle.json          # Idle breathing (48fps)
│   ├── mascot-wave.json          # Waving hello (48fps)
│   ├── mascot-intro.json         # Self-introduction (48fps)
│   ├── mascot-talk.json          # Talking (48fps)
│   ├── mascot-think.json         # Thinking (48fps)
│   ├── mascot-eureka.json        # Eureka moment (48fps)
│   ├── mascot-proud.json         # Proud/smug pose (48fps)
│   ├── mascot-write.json         # Writing (48fps, baked ping-pong segments)
│   ├── mascot-celebrate.json     # Jumping celebration (48fps)
│   ├── mascot-sad.json           # Thinking → sad (48fps, baked squint loop)
│   ├── mascot-toss.json          # Throwing paper away (48fps)
│   └── backups/                  # Original animations before recoloring (gitignored)
├── scripts/
│   ├── interpolate_lottie.py     # AI frame interpolation pipeline (RIFE)
│   ├── recolor_lottie.py         # Hue-shift recoloring script
│   ├── optimize_lottie.py        # Downscale + pngquant compression
│   ├── rife-ncnn-vulkan/         # RIFE binary + models (gitignored)
│   └── build_animated_mascot.py  # Legacy SVG mascot builder
```

## How It Works

### Architecture

The extension is a single content script injected on DatoCMS admin pages. Everything runs inside a **Shadow DOM** to isolate styles from the host page.

The dialogue system is a **state machine** defined as a plain config object. Each state has:
- A message to display
- An animation to play (with optional looping, segments, or auto-advance)
- Options (buttons/links) or custom content (feedback form, loading bar)

### Animation Pipeline

Source animations from Motchi come as raster Lottie files (embedded PNG frames) at 12fps. Our pipeline makes them production-ready:

1. **Frame interpolation**: `scripts/interpolate_lottie.py` uses [RIFE](https://github.com/nihui/rife-ncnn-vulkan) (AI video frame interpolation) to go from 12fps to 48fps
2. **Alpha preservation**: Frames are split into RGB + alpha channels, interpolated separately, then recombined (RIFE doesn't handle transparency natively)
3. **Alpha sharpening**: A levels adjustment crisps up soft edges from the interpolation
4. **Recoloring**: `scripts/recolor_lottie.py` hue-shifts the shoe color from blue (#0081DC) to purple (#6200C4) across all frames
5. **Segment baking**: Animations with intro + loop portions (writing, sad) have their ping-pong loops baked directly into the frame sequence for jitter-free looping
6. **Optimization**: `scripts/optimize_lottie.py` downscales frames from 512px to 256px and runs pngquant lossy compression (~89% size reduction)

### Dialogue Tree

```
greeting ("Welcome to DatoCMS!")
  └─ wave animation
      └─ introduction ("I'm Tuply, your advanced AI assistant")
          └─ intro animation
              └─ menu ("What AI operation do you want to use?")
                  ├─ AI Analysis → think (15s loading bar + status text)
                  │   └─ "This is definitely a DatoCMS project" → eureka → proud loop
                  ├─ Write my content → write (thought bubble, 8s)
                  │   └─ "Lorem ipsum dolor sit amet" [copy] → celebrate → toss on copy
                  └─ Review my schema → sad (thinking → squint loop)
                      └─ "Oh my..." → "You should start over." → ← Back
```

### Special Animation Behaviors

- **Ping-pong idle**: The idle animation plays forward then backward seamlessly since the source animation doesn't loop
- **Segment-based writing**: Intro (getting notepad) plays once, then only the middle writing portion loops, avoiding the repetitive notepad grab
- **Baked sad squint**: The sad animation's squint loop is baked with 0.5s holds at each end for expressive, deliberate squinting
- **Timed AI analysis**: The thinking animation loops for 15 seconds with a loading bar and rotating status text (scanning records, analyzing models, etc.)
- **Thought bubble**: The content writing state uses a comic-book thought cloud with animated trailing circles
- **Pop-in bubbles**: Every speech bubble transition replays a bouncy pop-in animation with a 300ms delay
- **Cross-fade transitions**: All animation swaps use a 250ms fade to avoid jarring cuts
- **Per-state idle overrides**: AI result uses the proud animation instead of the default idle

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

### Optimization

```bash
# Downscale 512→256px + lossy PNG compression (pngquant)
python3 scripts/optimize_lottie.py assets/mascot-*.json --size 256 --quality 60-80
```

Reduces file sizes by ~89% (254MB → 32MB total) with no visible quality loss at the 300px display size.

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
| [pngquant](https://pngquant.org/) | Lossy PNG compression for optimization | No (`brew install pngquant`) |
| Python 3.8+ | Runs build scripts | No |

## Credits

- Mascot animations generated with [Motchi](https://motchi.art/)
- Frame interpolation powered by [RIFE](https://github.com/hzwer/ECCV2022-RIFE) via [rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan)
- UI styled to match [DatoCMS brand guidelines](https://www.datocms.com/company/brand-assets)
- Spiritual successor to [Clippy](https://en.wikipedia.org/wiki/Office_Assistant) (1997-2007), gone but never forgotten
