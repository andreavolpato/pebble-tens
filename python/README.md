# tens — Python authoring toolchain

Python is the design and code-generation layer for the **tens** Pebble Time 2
watchface. Raw state goes in; a deterministic `Scene` (an ordered display list
of small drawing operations), a PNG preview, and generated C artifacts come out.

The Pebble runtime (under `../src/c`) stays thin: it reads time and stored
settings, then redraws from the same scene model.

## Pipeline

```
RuntimeState + UserConfig  ->  DerivedState  ->  build_scene()  ->  Scene
                                                                     |
                                          +--------------------------+--------------------------+
                                          v                                                     v
                                  preview.render_png()                                   export_c.scene_to_c()
                                  (desktop PNG artifact)                                 (Pebble C drawing logic)
```

## Layout

- `src/tens/state.py` — `RuntimeState`, `UserConfig` (raw facts).
- `src/tens/derived.py` — season, age, progress, birthday distance.
- `src/tens/layout.py` — exact integer geometry on the 200×228 canvas.
- `src/tens/scene.py` — `Scene` and operation dataclasses.
- `src/tens/palette.py` — semantic palette + Pebble color mapping.
- `src/tens/preview.py` — raster preview rendering.
- `src/tens/export_c.py` — export scene to C headers / drawing tables.
- `src/tens/export_resources.py` — generate resource-side artifacts.
- `scripts/` — thin CLI entry points.
- `../tests/python/` — unit tests.

## Setup

```bash
cd python
python -m venv .venv
. .venv/Scripts/activate     # Windows; use bin/activate on POSIX
pip install -e ".[dev]"
```

## Common tasks

```bash
python scripts/make_preview.py            # write ../previews/current.png
python scripts/export_headers.py          # write generated C headers
pytest                                    # run the test suite
```
