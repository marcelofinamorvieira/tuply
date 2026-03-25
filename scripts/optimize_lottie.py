#!/usr/bin/env python3
"""
Lottie Optimization Script
============================
Downscales embedded PNG frames and applies lossy compression (pngquant)
to dramatically reduce Lottie JSON file sizes.

Usage:
    python3 scripts/optimize_lottie.py assets/mascot-idle.json
    python3 scripts/optimize_lottie.py assets/mascot-*.json --size 256
    python3 scripts/optimize_lottie.py assets/mascot-*.json --size 256 --quality 60-80
"""

import argparse
import base64
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


def optimize_frame(png_bytes, target_size, quality):
    """Downscale a PNG frame and compress with pngquant."""
    img = Image.open(io.BytesIO(png_bytes))

    # Downscale if larger than target
    if img.width > target_size or img.height > target_size:
        img = img.resize((target_size, target_size), Image.LANCZOS)

    # Save as PNG to a buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_png = buf.getvalue()

    # Run pngquant for lossy compression
    try:
        result = subprocess.run(
            ["pngquant", "--quality", quality, "--speed", "1", "-"],
            input=raw_png,
            capture_output=True,
        )
        if result.returncode == 0 and len(result.stdout) > 0:
            return result.stdout
    except FileNotFoundError:
        print("Warning: pngquant not found, skipping compression", file=sys.stderr)

    return raw_png


def process_lottie(input_path, target_size, quality):
    print(f"Processing {input_path}...")

    with open(input_path) as f:
        data = json.load(f)

    original_size = input_path.stat().st_size

    # Update canvas dimensions
    data["w"] = target_size
    data["h"] = target_size

    assets = data.get("assets", [])
    image_assets = [a for a in assets if a.get("t") == 2 and a.get("p", "").startswith("data:image/")]

    if not image_assets:
        print(f"  No image assets found, skipping.")
        return

    for asset in image_assets:
        data_uri = asset["p"]
        base64_data = data_uri.split(",", 1)[1]
        png_bytes = base64.b64decode(base64_data)

        optimized = optimize_frame(png_bytes, target_size, quality)

        b64 = base64.b64encode(optimized).decode("ascii")
        asset["p"] = f"data:image/png;base64,{b64}"
        asset["w"] = target_size
        asset["h"] = target_size

    # Update layer anchor/position points for new dimensions
    half = target_size / 2.0
    for layer in data.get("layers", []):
        ks = layer.get("ks", {})
        p = ks.get("p", {})
        a = ks.get("a", {})
        if isinstance(p.get("k"), list) and len(p["k"]) >= 2:
            p["k"] = [half, half, 0]
        if isinstance(a.get("k"), list) and len(a["k"]) >= 2:
            a["k"] = [half, half, 0]

    with open(input_path, "w") as f:
        json.dump(data, f)

    new_size = input_path.stat().st_size
    reduction = (1 - new_size / original_size) * 100
    print(f"  {original_size / 1024 / 1024:.1f} MB → {new_size / 1024 / 1024:.1f} MB ({reduction:.0f}% reduction)")


def main():
    parser = argparse.ArgumentParser(description="Optimize Lottie JSON file sizes")
    parser.add_argument("inputs", nargs="+", help="Lottie JSON files to optimize")
    parser.add_argument("--size", type=int, default=256, help="Target frame size in pixels (default: 256)")
    parser.add_argument("--quality", default="60-80", help="pngquant quality range (default: 60-80)")
    args = parser.parse_args()

    for path_str in args.inputs:
        process_lottie(Path(path_str), args.size, args.quality)

    print("\nDone!")


if __name__ == "__main__":
    main()
