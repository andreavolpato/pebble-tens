"""Raster preview generation.

Renders a ``Scene`` to a Pebble-sized PNG for desktop iteration. The PNG is a
development/test artifact only — the scene (display list) remains the source of
truth, not the image.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from PIL import Image, ImageDraw

from .derived import derive
from .palette import gradient_stops
from .scene import (
    Bitmap,
    FillRect,
    FramebufferPatch,
    Gradient,
    Line,
    Pdc,
    Scene,
    StrokeRect,
    Text,
    build_scene,
)
from .state import RuntimeState, UserConfig

_ALIGN = {"left": "la", "center": "ma", "right": "ra"}

# Pebble Time 2 renders 2 bits per channel: 4 levels per channel, 64 colors.
_PEBBLE_LEVELS = (0, 85, 170, 255)


def _pebble_palette_image() -> Image.Image:
    """A 'P'-mode image whose palette is the full Pebble 64-color gamut."""
    pal: list[int] = []
    for r in _PEBBLE_LEVELS:
        for g in _PEBBLE_LEVELS:
            for b in _PEBBLE_LEVELS:
                pal += [r, g, b]
    pim = Image.new("P", (1, 1))
    pim.putpalette(pal + [0] * (768 - len(pal)))
    return pim


_PEBBLE_PALETTE = _pebble_palette_image()


def _lerp_stops(stops: list[tuple[int, int, int]], t: float) -> tuple[int, int, int]:
    """Interpolate a multi-stop gradient at position ``t`` in [0, 1]."""
    if len(stops) == 1 or t <= 0:
        return stops[0] if t <= 0 else stops[-1]
    if t >= 1:
        return stops[-1]
    span = t * (len(stops) - 1)
    i = int(span)
    f = span - i
    a, b = stops[i], stops[i + 1]
    return tuple(round(a[c] + (b[c] - a[c]) * f) for c in range(3))


def _render_gradient(op: Gradient) -> Image.Image:
    """Build a smooth gradient then dither it to the Pebble gamut.

    The ramp is mapped over ``op.span`` pixels (default ``op.w``); only the
    first ``op.w`` are drawn, so a partially-filled bar shows the left slice of
    the full-span ramp rather than a compressed copy of it.
    """
    stops = gradient_stops(op.gradient)
    grad = Image.new("RGB", (op.w, op.h))
    gd = ImageDraw.Draw(grad)
    if op.axis == "v":
        n = max(1, (op.span or op.h) - 1)
        for j in range(op.h):
            gd.line([(0, j), (op.w - 1, j)], fill=_lerp_stops(stops, (op.offset + j) / n))
    else:
        n = max(1, (op.span or op.w) - 1)
        for i in range(op.w):
            gd.line([(i, 0), (i, op.h - 1)], fill=_lerp_stops(stops, (op.offset + i) / n))
    dithered = grad.quantize(palette=_PEBBLE_PALETTE, dither=Image.Dither.FLOYDSTEINBERG)
    return dithered.convert("RGB")


def render_image(scene: Scene) -> Image.Image:
    """Render a scene to a Pillow ``Image`` in RGB."""
    pal = scene.palette()
    img = Image.new("RGB", (scene.width, scene.height), pal.rgb(scene.background))
    draw = ImageDraw.Draw(img)

    for op in scene.ops:
        if isinstance(op, FillRect):
            draw.rectangle(
                [op.x, op.y, op.x + op.w - 1, op.y + op.h - 1],
                fill=pal.rgb(op.color),
            )
        elif isinstance(op, StrokeRect):
            draw.rectangle(
                [op.x, op.y, op.x + op.w - 1, op.y + op.h - 1],
                outline=pal.rgb(op.color),
            )
        elif isinstance(op, Line):
            draw.line([op.x1, op.y1, op.x2, op.y2], fill=pal.rgb(op.color), width=op.width)
        elif isinstance(op, Text):
            anchor = _ALIGN.get(op.align, "la")
            tx = op.x if op.align == "left" else (
                op.x + op.w // 2 if op.align == "center" else op.x + op.w
            )
            draw.text((tx, op.y), op.text, fill=pal.rgb(op.color), anchor=anchor)
        elif isinstance(op, Gradient):
            if op.w > 0 and op.h > 0:
                img.paste(_render_gradient(op), (op.x, op.y))
        elif isinstance(op, (Bitmap, Pdc, FramebufferPatch)):
            # Resource-backed ops are placeholders in the preview; draw a marker
            # box so layout is still visible without the bundled asset.
            x, y = op.x, op.y
            draw.rectangle([x, y, x + 8, y + 8], outline=pal.rgb("ink"))
        else:  # pragma: no cover - defensive
            raise TypeError(f"cannot preview op {op!r}")

    return img


def render_png(scene: Scene, path: str | Path) -> Path:
    """Render a scene and write it to ``path`` as PNG."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    render_image(scene).save(path, "PNG")
    return path


def _default_scene() -> Scene:
    """A sample scene for ``main`` (uses today's date, a placeholder birthday)."""
    now = _dt.datetime(2026, 8, 12, 15, 37)  # deterministic sample
    rt = RuntimeState.from_datetime(now)
    cfg = UserConfig(birth_year=1990, birth_month=4, birth_day=12)
    return build_scene(rt, cfg, derive(rt, cfg))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Render a Tens scene to PNG.")
    parser.add_argument(
        "-o", "--out", default="../previews/current.png", help="output PNG path"
    )
    args = parser.parse_args(argv)
    out = render_png(_default_scene(), args.out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
