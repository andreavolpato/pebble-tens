#!/usr/bin/env python3
"""Bake the dithered spectral gradient resource bitmaps.

Usage:
    python scripts/bake_gradients.py [-o OUTDIR]   (default: ../resources/images)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tens.bake import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
