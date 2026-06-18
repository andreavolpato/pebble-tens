"""Generate resource-side artifacts.

Only emit files here when the watch must consume them at runtime (packed
scene data, lookup tables, quantized bitmaps). Generated previews are *not*
runtime resources and belong under ``previews/`` instead.

This module is a stub: it defines the seam for resource generation and a
``package.json`` resource-entry helper so additions stay declarative.
"""

from __future__ import annotations

import json
from pathlib import Path

from .scene import Bitmap, FramebufferPatch, Pdc, Scene


def collect_resource_ids(scene: Scene) -> list[str]:
    """Resource ids referenced by a scene's resource-backed ops."""
    ids: list[str] = []
    for op in scene.ops:
        if isinstance(op, (Bitmap, Pdc)):
            ids.append(op.resource)
        elif isinstance(op, FramebufferPatch):
            ids.append(op.data_resource)
    # Preserve order, drop duplicates.
    seen: set[str] = set()
    return [i for i in ids if not (i in seen or seen.add(i))]


def resource_entries(scene: Scene) -> list[dict]:
    """Build draft ``resources.media`` entries for package.json."""
    entries = []
    for op in scene.ops:
        if isinstance(op, Bitmap):
            entries.append({"type": "bitmap", "name": op.resource, "file": f"images/{op.resource}.png"})
        elif isinstance(op, Pdc):
            entries.append({"type": "raw", "name": op.resource, "file": f"pdc/{op.resource}.pdc"})
        elif isinstance(op, FramebufferPatch):
            entries.append({"type": "raw", "name": op.data_resource, "file": f"data/{op.data_resource}.bin"})
    return entries


def write_resource_manifest(scene: Scene, path: str | Path) -> Path:
    """Write a draft media manifest (for review before merging into package.json)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"media": resource_entries(scene)}, indent=2), encoding="utf-8"
    )
    return path
