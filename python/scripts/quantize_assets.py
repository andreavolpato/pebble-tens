#!/usr/bin/env python3
"""Quantize source images to the Pebble 64-color palette.

Pebble Time 2 renders 64 colors (2 bits per channel). This script reduces an
RGB image to that gamut so bundled bitmaps look on-device as they do in
preview. Stub: wire up real per-channel quantization as assets are added.

Usage:
    python scripts/quantize_assets.py SRC DST
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

# Pebble channel levels: 0, 85, 170, 255 (2 bits per channel).
_LEVELS = (0, 85, 170, 255)


def _nearest(value: int) -> int:
    return min(_LEVELS, key=lambda lvl: abs(lvl - value))


def quantize_to_pebble(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    return Image.eval(rgb, _nearest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Quantize an image to Pebble 64 colors.")
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    args = parser.parse_args(argv)

    out = quantize_to_pebble(Image.open(args.src))
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.dst)
    print(f"wrote {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
