"""Bake dithered spectral-gradient bitmaps for the on-device rainbow render.

The watch can't run Floyd-Steinberg per frame (the per-pixel approach boot-looped
on device), so we precompute the dithered spectral ramp once per layout and
bundle it as a Pebble resource. At runtime the grid's rainbow mask and the life
bar both reveal slices of this image instead of computing colors live.

Each image is the size of the day-grid (the screen minus the centering
margins): the horizontal spectral ramp mapped across ``grid_w`` and dithered to
the Pebble 64-color gamut, ``grid_h`` tall so every box row gets a faithful
dithered slice. The ramp is horizontal, so the life bar can sample any band of
rows from the same image.

There are exactly two layouts and thus two baked images:
  - "4x6" (3x2 cells) -> spectral_4x6.png
  - "6x4" (2x3 cells) -> spectral_6x4.png
because the two layouts have different grid widths.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from . import layout
from .palette import gradient_stops
from .preview import dither_gradient

# layout key -> Pebble resource name (RESOURCE_ID_<NAME> in C).
LAYOUT_RESOURCES = {
    "4x6": "SPECTRAL_4X6",
    "6x4": "SPECTRAL_6X4",
}


def bake_layout(layout_key: str, gradient: str = "spectral") -> Image.Image:
    """Render the whole-grid dithered gradient for one layout."""
    grid = layout.day_rect(layout_key)
    return dither_gradient(grid.w, grid.h, gradient_stops(gradient), axis="h")


def bake_all(out_dir: str | Path, gradient: str = "spectral") -> list[Path]:
    """Bake every layout's gradient image into ``out_dir`` (one PNG each)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for layout_key in LAYOUT_RESOURCES:
        img = bake_layout(layout_key, gradient)
        path = out_dir / f"spectral_{layout_key}.png"
        img.save(path, "PNG")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Bake dithered spectral gradient resource bitmaps."
    )
    parser.add_argument(
        "-o", "--out", default="../resources/images", help="output directory"
    )
    args = parser.parse_args(argv)
    for path in bake_all(args.out):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
