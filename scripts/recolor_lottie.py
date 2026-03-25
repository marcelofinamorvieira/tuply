#!/usr/bin/env python3
"""
Lottie Hue-Shift Recoloring Script
====================================
Shifts a range of hues in all embedded PNG frames of a Lottie JSON file.
Useful for recoloring specific elements (e.g., shoes, accessories) without
affecting the rest of the character.

Usage:
    python3 scripts/recolor_lottie.py assets/mascot-idle.json --from-color 0081DC --to-color 7E00FC
    python3 scripts/recolor_lottie.py assets/mascot-idle.json --from-color 0081DC --to-color 7E00FC --hue-range 40
    python3 scripts/recolor_lottie.py assets/*.json --from-color 0081DC --to-color 7E00FC

Restore from backups:
    cp assets/backups/*.json assets/
"""

import argparse
import base64
import colorsys
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s, v


def recolor_image(img, from_hue, to_hue, hue_range, sat_min):
    """Shift hues in the from_hue range to the to_hue range, preserving saturation and value."""
    rgba = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = rgba[:, :, :3] / 255.0
    alpha = rgba[:, :, 3]

    # Convert RGB to HSV
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    diff = max_c - min_c

    # Hue calculation
    hue = np.zeros_like(max_c)
    mask_r = (max_c == r) & (diff > 0)
    mask_g = (max_c == g) & (diff > 0)
    mask_b = (max_c == b) & (diff > 0)
    hue[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r]) + 360) % 360
    hue[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120) % 360
    hue[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240) % 360

    # Saturation
    sat = np.zeros_like(max_c)
    sat[max_c > 0] = diff[max_c > 0] / max_c[max_c > 0]

    # Find pixels in the target hue range with sufficient saturation
    hue_diff = np.abs(hue - from_hue)
    hue_diff = np.minimum(hue_diff, 360 - hue_diff)
    hue_mask = (hue_diff <= hue_range) & (sat >= sat_min) & (alpha > 0)

    if not np.any(hue_mask):
        return img

    # Shift hue
    hue_shift = to_hue - from_hue
    new_hue = (hue + hue_shift) % 360

    # Convert back to RGB only for affected pixels
    h_norm = new_hue / 360.0
    val = max_c

    result = rgba.copy()

    ys, xs = np.where(hue_mask)
    for y, x in zip(ys, xs):
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_norm[y, x], sat[y, x], val[y, x])
        result[y, x, 0] = r_new * 255
        result[y, x, 1] = g_new * 255
        result[y, x, 2] = b_new * 255

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def recolor_image_fast(img, from_hue, to_hue, hue_range, sat_min):
    """Vectorized version of recolor_image for performance."""
    rgba = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = rgba[:, :, :3] / 255.0
    alpha = rgba[:, :, 3]

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    diff = max_c - min_c

    # Hue
    hue = np.zeros_like(max_c)
    nonzero = diff > 0
    mask_r = (max_c == r) & nonzero
    mask_g = (max_c == g) & nonzero & ~mask_r
    mask_b = nonzero & ~mask_r & ~mask_g
    hue[mask_r] = (60 * ((g[mask_r] - b[mask_r]) / diff[mask_r])) % 360
    hue[mask_g] = (60 * ((b[mask_g] - r[mask_g]) / diff[mask_g]) + 120) % 360
    hue[mask_b] = (60 * ((r[mask_b] - g[mask_b]) / diff[mask_b]) + 240) % 360

    # Saturation
    sat = np.where(max_c > 0, diff / max_c, 0)

    # Mask: pixels in hue range with enough saturation
    hue_diff = np.abs(hue - from_hue)
    hue_diff = np.minimum(hue_diff, 360 - hue_diff)
    mask = (hue_diff <= hue_range) & (sat >= sat_min) & (alpha > 0)

    if not np.any(mask):
        return img

    # Shift hue for masked pixels
    hue_shift = to_hue - from_hue
    new_hue = np.where(mask, (hue + hue_shift) % 360, hue)

    # HSV to RGB (vectorized for masked pixels only)
    h_sector = (new_hue / 60.0) % 6
    h_i = h_sector.astype(int)
    f = h_sector - h_i
    p = max_c * (1 - sat)
    q = max_c * (1 - sat * f)
    t = max_c * (1 - sat * (1 - f))

    new_r = np.where(mask, np.choose(h_i % 6, [max_c, q, p, p, t, max_c]), r)
    new_g = np.where(mask, np.choose(h_i % 6, [t, max_c, max_c, q, p, p]), g)
    new_b = np.where(mask, np.choose(h_i % 6, [p, p, t, max_c, max_c, q]), b)

    result = rgba.copy()
    result[:, :, 0] = new_r * 255
    result[:, :, 1] = new_g * 255
    result[:, :, 2] = new_b * 255

    return Image.fromarray(result.astype(np.uint8), "RGBA")


def process_lottie(input_path, from_hue, to_hue, hue_range, sat_min):
    print(f"Processing {input_path}...")

    with open(input_path) as f:
        data = json.load(f)

    assets = data.get("assets", [])
    image_assets = [a for a in assets if a.get("t") == 2 and a.get("p", "").startswith("data:image/")]

    if not image_assets:
        print(f"  No image assets found, skipping.")
        return

    recolored = 0

    for asset in image_assets:
        data_uri = asset["p"]
        base64_data = data_uri.split(",", 1)[1]
        png_bytes = base64.b64decode(base64_data)

        img = Image.open(io.BytesIO(png_bytes))
        new_img = recolor_image_fast(img, from_hue, to_hue, hue_range, sat_min)

        buf = io.BytesIO()
        new_img.save(buf, format="PNG")
        new_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        asset["p"] = f"data:image/png;base64,{new_b64}"
        recolored += 1

    with open(input_path, "w") as f:
        json.dump(data, f)

    size_mb = input_path.stat().st_size / (1024 * 1024)
    print(f"  Recolored {recolored} frames ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Hue-shift a color range in Lottie PNG frames")
    parser.add_argument("inputs", nargs="+", help="Lottie JSON files to process")
    parser.add_argument("--from-color", required=True, help="Source hex color (e.g., 0081DC)")
    parser.add_argument("--to-color", required=True, help="Target hex color (e.g., 7E00FC)")
    parser.add_argument("--hue-range", type=float, default=35, help="Hue tolerance in degrees (default: 35)")
    parser.add_argument("--sat-min", type=float, default=0.25, help="Minimum saturation to affect (0-1, default: 0.25)")
    args = parser.parse_args()

    from_hue, _, _ = hex_to_hsv(args.from_color)
    to_hue, _, _ = hex_to_hsv(args.to_color)

    print(f"Hue shift: {from_hue:.0f}° → {to_hue:.0f}° (range: ±{args.hue_range}°, min sat: {args.sat_min})")

    for path_str in args.inputs:
        process_lottie(Path(path_str), from_hue, to_hue, args.hue_range, args.sat_min)

    print("\nDone! To revert: cp assets/backups/*.json assets/")


if __name__ == "__main__":
    main()
