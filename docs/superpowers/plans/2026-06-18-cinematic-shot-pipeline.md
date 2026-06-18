# Cinematic Shot Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one command that exports a 3D render cache, validates it, converts it, reconstructs water meshes, renders preview or Blender frames, assembles a GIF, and writes a durable shot summary.

**Architecture:** Keep S43 as orchestration only. `tools/run_cinematic_shot.py` calls the existing C++ exporter and Python tools as subprocesses, records elapsed times and logs, and chooses Blender or preview rendering without changing simulation, cache schema, reconstruction, or renderer internals.

**Tech Stack:** Python 3 standard library, existing CMake Release `export_render_cache3d`, existing render-cache validation/conversion/reconstruction tools, Pillow-based preview/GIF tooling, optional Blender bridge.

---

### Task 1: Shot Runner

**Files:**
- Create: `tools/run_cinematic_shot.py`

- [ ] **Step 1: Add CLI and preset mapping**

Create a Python CLI with:

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\bubble_cinematic --frames 24 --width 1280 --height 720
```

Required options:

- `--preset bubble_cinematic`
- `--out PATH`
- `--frames N`
- `--width N`
- `--height N`
- `--renderer auto|preview|blender`
- `--sim-steps N`
- `--cache-every N`
- `--kind sparse|mr`
- `--build-dir build`
- `--config Release`
- `--no-build`

- [ ] **Step 2: Build or locate exporter**

Find `build/<config>/export_render_cache3d.exe`. If it is missing and `--no-build` is not set, run:

```powershell
cmake --build build --config Release --target export_render_cache3d
```

Fail with a clear error if the executable is still missing.

- [ ] **Step 3: Run pipeline commands**

Run these commands in order and stop on the first failure:

```powershell
.\build\Release\export_render_cache3d.exe --kind sparse --nx 12 --ny 18 --nz 12 --steps 24 --every 1 --out-prefix build\shots\bubble_cinematic\cache\render_cache --manifest build\shots\bubble_cinematic\cache\manifest.json
python tools\validate_render_cache.py build\shots\bubble_cinematic\cache\manifest.json --require-cinematic
python tools\reconstruct_water.py build\shots\bubble_cinematic\cache\manifest.json build\shots\bubble_cinematic\water_mesh --frames 24 --threshold 0.02
python tools\convert_render_cache.py build\shots\bubble_cinematic\cache\manifest.json build\shots\bubble_cinematic\converted --require-cinematic --water-reconstruction build\shots\bubble_cinematic\water_mesh\water_reconstruction.json
python tools\render_bridge_blender.py build\shots\bubble_cinematic\converted\sequence.json build\shots\bubble_cinematic\blender --frames 24 --width 1280 --height 720
python tools\assemble_frames.py build\shots\bubble_cinematic\blender\frames build\shots\bubble_cinematic\shot.gif --fps 12
```

For `--renderer preview`, replace the Blender command with:

```powershell
python tools\cinematic_render_stub.py build\shots\bubble_cinematic\cache\manifest.json build\shots\bubble_cinematic\preview --frames 24 --width 1280 --height 720 --water-reconstruction build\shots\bubble_cinematic\water_mesh\water_reconstruction.json
python tools\assemble_frames.py build\shots\bubble_cinematic\preview build\shots\bubble_cinematic\shot.gif --fps 12
```

- [ ] **Step 4: Write summary**

Write `shot_summary.json` with:

- runner name and version
- preset, kind, dimensions, sim steps, render frames, resolution
- selected renderer
- paths for manifest, sequence, water reconstruction, render directory, GIF
- every subprocess command, return code, elapsed milliseconds, stdout log, stderr log
- final `status=ok`

### Task 2: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: README status and quickstart**

Add S43 as done and document:

```powershell
python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
```

- [ ] **Step 2: Roadmap handoff**

Mark S43 done and set next immediate action to S44:

```text
docs/superpowers/plans/2026-06-18-cinematic-render-presets.md
```

The next success condition is a named preset file for camera, material, lighting, tone mapping, renderer choice, and shot dimensions.

### Task 3: Validation

**Files:**
- Test generated outputs under `build/`

- [ ] **Step 1: Python compile**

```powershell
python -m py_compile tools\run_cinematic_shot.py
```

- [ ] **Step 2: Preview smoke**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s43_preview --frames 4 --sim-steps 2 --width 320 --height 180 --renderer preview --no-build
```

Expected: `build\shots\s43_preview\shot_summary.json` reports `status=ok`, and `shot.gif` exists.

- [ ] **Step 3: Blender smoke**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s43_blender --frames 8 --sim-steps 2 --width 320 --height 180 --renderer blender --samples 8 --no-build
```

Expected: `build\shots\s43_blender\shot_summary.json` reports `status=ok`, and `blender\frames\frame_0000.png` exists.

- [ ] **Step 4: Regression**

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

### Task 4: Commit

**Files:**
- `README.md`
- `tools/run_cinematic_shot.py`
- `docs/superpowers/plans/2026-06-18-cinematic-shot-pipeline.md`
- `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: Commit and push**

```powershell
git add README.md tools\run_cinematic_shot.py docs\superpowers\plans\2026-06-18-cinematic-shot-pipeline.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add cinematic shot pipeline"
git push origin main
```
