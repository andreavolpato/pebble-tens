#!/usr/bin/env python3
"""Export the current scene to a generated Pebble C header.

Usage:
    python scripts/export_headers.py [-o OUT]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tens.export_c import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
