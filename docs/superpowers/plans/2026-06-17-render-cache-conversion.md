# Render Cache Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Keep S38 as one commit and push after verification.

**Goal:** Convert validated LSFS 3D render cache manifests into renderer-neutral assets without binding the simulator to a renderer.

**Architecture:** Keep the source cache as the canonical simulation artifact. The converter reads a manifest and its JSONL frames, writes a movable output bundle with relative paths, and leaves validation to `tools/validate_render_cache.py`. The first output format is deliberately simple: JSON camera/metadata, CSV particles, CSV phase cells, and a sequence index.

**Tech Stack:** Python 3 standard library, JSON/JSONL, CSV.

## Scope

- Create `tools/convert_render_cache.py`
  - Accept `<manifest.json> <out_dir>`.
  - Reject missing or malformed manifests/frames with non-zero exit.
  - Write `sequence.json`.
  - Write `frames/frame_000_camera.json`.
  - Write `frames/frame_000_particles.csv`.
  - Write `frames/frame_000_phase_cells.csv`.
  - Store only relative paths in `sequence.json`.
- Modify `README.md`
  - Add S38 status row and a quickstart conversion command.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S38 done after validation and set S39 as the next immediate action.

## Output Schema

`sequence.json`:

- `converter`
- `version`
- `source_manifest`
- `manifest_schema_version`
- `sim_kind`
- `dims`
- `dx`
- `frame_count`
- `frames`

Each frame entry uses relative paths:

- `camera`
- `particles`
- `phase_cells`

Camera JSON includes:

- source header fields
- camera fields
- optional cinematic metadata
- source manifest frame metadata

Particle CSV columns:

- `kind,index,phase,x,y,z,vx,vy,vz,volume,age`

Phase-cell CSV columns:

- `i,j,k,level,marker,phi,liquid_volume`

## Verification

```powershell
python -m py_compile tools\convert_render_cache.py
python tools\convert_render_cache.py build\s37_sparse_manifest.json build\s38_convert_smoke
python tools\validate_render_cache.py build\s37_sparse_manifest.json --require-cinematic
powershell -NoProfile -Command "Test-Path build\s38_convert_smoke\sequence.json; Test-Path build\s38_convert_smoke\frames\frame_000_camera.json; Test-Path build\s38_convert_smoke\frames\frame_000_particles.csv; Test-Path build\s38_convert_smoke\frames\frame_000_phase_cells.csv"
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Commit

```powershell
git add README.md tools\convert_render_cache.py docs\superpowers\plans\2026-06-17-render-cache-conversion.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add render cache conversion tool"
git push origin main
```
