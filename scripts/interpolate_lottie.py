#!/usr/bin/env python3
"""
Lottie Frame Interpolation Pipeline
====================================
Takes a Lottie JSON file with embedded PNG frames, runs AI frame interpolation
via rife-ncnn-vulkan, and outputs a new Lottie JSON with doubled frame rate.

Usage:
    python3 scripts/interpolate_lottie.py assets/mascot-idle.json
    python3 scripts/interpolate_lottie.py assets/mascot-idle.json --multiplier 4
    python3 scripts/interpolate_lottie.py assets/mascot-idle.json --output assets/mascot-idle-smooth.json
    python3 scripts/interpolate_lottie.py assets/mascot-idle.json --model rife-v4.6

The script will:
  1. Extract all base64-encoded PNG frames from the Lottie assets
  2. Split each frame into RGB (on white background) and alpha channel
  3. Run rife-ncnn-vulkan separately on RGB and alpha sequences
  4. Recombine interpolated RGB + alpha to preserve transparency
  5. Rebuild the Lottie JSON with the new frames and updated frame rate
"""

import argparse
import base64
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
RIFE_BINARY = SCRIPT_DIR / "rife-ncnn-vulkan" / "rife-ncnn-vulkan"


def find_rife_binary():
    if RIFE_BINARY.exists():
        return RIFE_BINARY

    # Fall back to PATH
    found = shutil.which("rife-ncnn-vulkan")
    if found:
        return Path(found)

    print("Error: rife-ncnn-vulkan binary not found.", file=sys.stderr)
    print(f"Expected at: {RIFE_BINARY}", file=sys.stderr)
    print("Download from: https://github.com/nihui/rife-ncnn-vulkan/releases", file=sys.stderr)
    sys.exit(1)


def extract_frames(lottie_data, rgb_dir, alpha_dir, loop=True):
    """Extract Lottie image assets into separate RGB and alpha PNG sequences.

    RIFE doesn't handle alpha channels — transparent pixels bleed to black.
    We split each frame into:
      - RGB on a white background (for color interpolation)
      - Alpha channel as a grayscale image (for mask interpolation)
    After RIFE runs on both, we recombine them in `recombine_frames`.

    When loop=True, the first frame is appended at the end so RIFE generates
    a smooth transition from the last frame back to the first.
    """
    assets = lottie_data.get("assets", [])
    image_assets = [a for a in assets if a.get("t") == 2 and a.get("p", "").startswith("data:image/")]

    if not image_assets:
        print("Error: No embedded image assets found in Lottie file.", file=sys.stderr)
        sys.exit(1)

    image_assets.sort(key=lambda a: a["id"])

    if loop:
        image_assets.append(image_assets[0])

    for i, asset in enumerate(image_assets):
        data_uri = asset["p"]
        base64_data = data_uri.split(",", 1)[1]
        png_bytes = base64.b64decode(base64_data)

        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

        # Extract alpha as grayscale
        alpha = img.getchannel("A")
        alpha_rgb = Image.merge("RGB", (alpha, alpha, alpha))
        alpha_rgb.save(alpha_dir / f"{i:08d}.png")

        # Composite RGB onto white background so RIFE doesn't see black edges
        white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        composited = Image.alpha_composite(white_bg, img)
        composited.convert("RGB").save(rgb_dir / f"{i:08d}.png")

    real_count = len(image_assets) - (1 if loop else 0)
    extra = " (+1 loop-closer)" if loop else ""
    print(f"  Extracted {real_count} frames{extra} (RGB + alpha split)")
    return real_count

    print(f"  Extracted {len(image_assets)} frames (RGB + alpha split)")
    return len(image_assets)


def run_rife(input_dir, output_dir, model_name, rife_binary, label=""):
    """Run rife-ncnn-vulkan to interpolate a sequence of frames."""
    model_path = SCRIPT_DIR / "rife-ncnn-vulkan" / model_name

    if not model_path.exists():
        available = [
            d.name for d in (SCRIPT_DIR / "rife-ncnn-vulkan").iterdir()
            if d.is_dir() and d.name.startswith("rife")
        ]
        print(f"Error: Model '{model_name}' not found at {model_path}", file=sys.stderr)
        print(f"Available models: {', '.join(sorted(available))}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        str(rife_binary),
        "-i", str(input_dir),
        "-o", str(output_dir),
        "-m", str(model_path),
        "-f", "%08d.png",
        "-v",
    ]

    prefix = f"  [{label}] " if label else "  "
    print(f"{prefix}Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: rife-ncnn-vulkan failed (exit code {result.returncode})", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    interpolated_frames = sorted(output_dir.glob("*.png"))
    print(f"{prefix}Generated {len(interpolated_frames)} interpolated frames")
    return len(interpolated_frames)


def sharpen_alpha(alpha_img, cutoff_low=30, cutoff_high=225):
    """Apply a levels adjustment to the alpha channel to crisp up soft edges.

    Pixels below cutoff_low become fully transparent (0).
    Pixels above cutoff_high become fully opaque (255).
    Everything in between is remapped linearly across 0-255.
    """
    spread = cutoff_high - cutoff_low
    table = []
    for v in range(256):
        if v <= cutoff_low:
            table.append(0)
        elif v >= cutoff_high:
            table.append(255)
        else:
            table.append(int(255 * (v - cutoff_low) / spread))
    return alpha_img.point(table)


def recombine_frames(rgb_dir, alpha_dir, output_dir, alpha_cutoff_low=30, alpha_cutoff_high=225, loop=True):
    """Recombine interpolated RGB and alpha sequences into RGBA PNGs.

    When loop=True, drops the final frame (duplicate of frame 0) so the
    animation loops seamlessly without a repeated frame.
    """
    rgb_files = sorted(rgb_dir.glob("*.png"))
    alpha_files = sorted(alpha_dir.glob("*.png"))

    if len(rgb_files) != len(alpha_files):
        print(
            f"Error: RGB ({len(rgb_files)}) and alpha ({len(alpha_files)}) frame counts don't match",
            file=sys.stderr,
        )
        sys.exit(1)

    # Drop the last frame — it's a duplicate of frame 0 used only to
    # give RIFE a pair for the loop-closing interpolation
    if loop:
        rgb_files = rgb_files[:-1]
        alpha_files = alpha_files[:-1]

    for i, (rgb_path, alpha_path) in enumerate(zip(rgb_files, alpha_files)):
        rgb_img = Image.open(rgb_path).convert("RGB")
        alpha_img = Image.open(alpha_path).convert("L")
        alpha_img = sharpen_alpha(alpha_img, alpha_cutoff_low, alpha_cutoff_high)

        rgba = rgb_img.copy()
        rgba.putalpha(alpha_img)
        rgba.save(output_dir / f"{i:08d}.png")

    print(f"  Recombined {len(rgb_files)} RGBA frames (alpha sharpened: {alpha_cutoff_low}-{alpha_cutoff_high})")
    return len(rgb_files)


def rebuild_lottie(original_data, interpolated_dir, total_frames):
    """Rebuild the Lottie JSON with interpolated frames and doubled frame rate."""
    original_fr = original_data["fr"]
    new_fr = original_fr * 2
    width = original_data["w"]
    height = original_data["h"]
    half_w = width / 2.0
    half_h = height / 2.0

    new_assets = []
    new_layers = []

    frame_files = sorted(interpolated_dir.glob("*.png"))

    for i, frame_path in enumerate(frame_files):
        png_bytes = frame_path.read_bytes()
        b64_data = base64.b64encode(png_bytes).decode("ascii")
        data_uri = f"data:image/png;base64,{b64_data}"

        asset_id = f"frame_{i:04d}"

        new_assets.append({
            "id": asset_id,
            "nm": f"Frame {i}",
            "t": 2,
            "w": width,
            "h": height,
            "u": "",
            "p": data_uri,
            "e": 1,
        })

        new_layers.append({
            "ddd": 0,
            "ind": i,
            "ty": 2,
            "nm": f"Frame {i}",
            "refId": asset_id,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [half_w, half_h, 0]},
                "a": {"a": 0, "k": [half_w, half_h, 0]},
                "s": {"a": 0, "k": [100, 100, 100]},
            },
            "ao": 0,
            "ip": i,
            "op": i + 1,
            "st": 0,
            "bm": 0,
        })

    new_data = {
        "v": original_data["v"],
        "fr": new_fr,
        "ip": 0,
        "op": len(frame_files),
        "w": width,
        "h": height,
        "nm": original_data.get("nm", "Interpolated Animation"),
        "ddd": original_data.get("ddd", 0),
        "assets": new_assets,
        "layers": new_layers,
        "markers": original_data.get("markers", []),
    }

    return new_data


def main():
    parser = argparse.ArgumentParser(
        description="Interpolate frames in a Lottie JSON animation using AI (rife-ncnn-vulkan)"
    )
    parser.add_argument(
        "input",
        help="Path to the input Lottie JSON file",
    )
    parser.add_argument(
        "--output", "-o",
        help="Path for the output Lottie JSON (default: replaces the input file)",
    )
    parser.add_argument(
        "--model", "-m",
        default="rife-v4.6",
        help="RIFE model to use (default: rife-v4.6). Use 'rife-anime' for anime-style content.",
    )
    parser.add_argument(
        "--alpha-low",
        type=int,
        default=30,
        help="Alpha sharpening: values at or below this become fully transparent (default: 30)",
    )
    parser.add_argument(
        "--alpha-high",
        type=int,
        default=225,
        help="Alpha sharpening: values at or above this become fully opaque (default: 225)",
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="Skip appending the first frame as a loop-closer (use for ping-pong playback)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary frame directories for debugging",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rife_binary = find_rife_binary()

    print(f"Loading {input_path}...")
    with open(input_path) as f:
        lottie_data = json.load(f)

    original_fr = lottie_data["fr"]
    original_frames = lottie_data["op"] - lottie_data["ip"]
    print(f"  Original: {original_frames} frames @ {original_fr}fps")
    print(f"  Target:   ~{original_frames * 2 - 1} frames @ {original_fr * 2}fps")

    tmp_root = Path(tempfile.mkdtemp(prefix="lottie_interp_"))
    rgb_extracted_dir = tmp_root / "rgb_extracted"
    alpha_extracted_dir = tmp_root / "alpha_extracted"
    rgb_interpolated_dir = tmp_root / "rgb_interpolated"
    alpha_interpolated_dir = tmp_root / "alpha_interpolated"
    final_dir = tmp_root / "final"
    for d in [rgb_extracted_dir, alpha_extracted_dir, rgb_interpolated_dir, alpha_interpolated_dir, final_dir]:
        d.mkdir()

    try:
        use_loop = not args.no_loop

        print("\nStep 1: Extracting frames (RGB + alpha split)...")
        extract_frames(lottie_data, rgb_extracted_dir, alpha_extracted_dir, loop=use_loop)

        print("\nStep 2: Running AI frame interpolation...")
        run_rife(rgb_extracted_dir, rgb_interpolated_dir, args.model, rife_binary, label="RGB")
        run_rife(alpha_extracted_dir, alpha_interpolated_dir, args.model, rife_binary, label="Alpha")

        print("\nStep 3: Recombining RGB + alpha...")
        total_interpolated = recombine_frames(
            rgb_interpolated_dir, alpha_interpolated_dir, final_dir,
            alpha_cutoff_low=args.alpha_low, alpha_cutoff_high=args.alpha_high,
            loop=use_loop,
        )

        print("\nStep 4: Rebuilding Lottie JSON...")
        new_lottie = rebuild_lottie(lottie_data, final_dir, total_interpolated)

        new_fr = new_lottie["fr"]
        new_frames = new_lottie["op"]
        print(f"  Result: {new_frames} frames @ {new_fr}fps")

        print(f"\nWriting output to {output_path}...")
        with open(output_path, "w") as f:
            json.dump(new_lottie, f)

        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Output size: {output_size_mb:.1f} MB")
        print("\nDone!")

    finally:
        if args.keep_temp:
            print(f"\nTemp files kept at: {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
