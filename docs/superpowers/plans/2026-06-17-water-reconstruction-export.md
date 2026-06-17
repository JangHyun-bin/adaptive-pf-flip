# Water Reconstruction Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export a renderer-friendly water body asset sequence from LSFS phase-cell render caches.

**Architecture:** Choose mesh-first reconstruction for S41. The new tool reads either canonical JSONL manifests or S38 converted `sequence.json` bundles, thresholds phase cells into occupied voxels, emits one OBJ surface mesh per output frame, and writes a movable `water_reconstruction.json` index. The cinematic preview can optionally consume that reconstruction index to overlay the mesh footprint and record mesh stats in `render_summary.json`.

**Tech Stack:** Python 3 standard library, OBJ mesh export, existing JSONL/CSV cache formats, Pillow preview path.

---

## Decision

Use OBJ mesh output first, not volume slices.

Reasons:

- The current cache has sparse phase-cell samples, not a full signed-distance volume.
- OBJ is renderer-neutral and directly importable by Blender for S42.
- It keeps S41 dependency-free and easy to validate in CI-style smoke runs.
- Volume/OpenVDB can still be introduced after the renderer bridge decision if mesh flicker or density detail becomes the bottleneck.

## Files

- Create `tools/reconstruct_water.py`
  - Accept manifest JSON, converted `sequence.json`, or JSONL frame.
  - Export `meshes/frame_0000_water.obj` assets.
  - Export `water_reconstruction.json` with relative mesh paths, frame count, and per-frame mesh stats.
- Modify `tools/convert_render_cache.py`
  - Add optional `--water-reconstruction PATH` to attach mesh paths to converted `sequence.json`.
- Modify `tools/cinematic_render_stub.py`
  - Add optional `--water-reconstruction PATH` overlay/summary support.
- Create `docs/render_bridge_decision.md`
  - Record mesh-first choice and commands.
- Modify `README.md`
  - Add S41 status and quickstart commands.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S41 done and set S42 as next immediate action.

## Tasks

### Task 1: Reconstruction Tool

- [ ] Implement manifest/sequence/JSONL loading.
- [ ] Convert phase cells with `phi >= threshold` or positive liquid volume into occupied cells.
- [ ] Emit exposed voxel faces as OBJ quads.
- [ ] Write `water_reconstruction.json` with relative paths and mesh stats.

### Task 2: Converter and Preview Integration

- [ ] Let `convert_render_cache.py --water-reconstruction PATH` attach water mesh paths to matching frame entries.
- [ ] Let `cinematic_render_stub.py --water-reconstruction PATH` overlay projected mesh vertices and write `mesh_vertex_count` / `mesh_face_count` in frame summaries.

### Task 3: Verification

```powershell
python -m py_compile tools\reconstruct_water.py tools\convert_render_cache.py tools\cinematic_render_stub.py
python tools\reconstruct_water.py build\s40_sparse_manifest.json build\s41_water_mesh --frames 8 --threshold 0.02
python tools\reconstruct_water.py build\s40_convert\sequence.json build\s41_water_mesh_from_sequence --frames 8 --threshold 0.02
python tools\convert_render_cache.py build\s40_sparse_manifest.json build\s41_convert_with_mesh --require-cinematic --water-reconstruction build\s41_water_mesh\water_reconstruction.json
python tools\cinematic_render_stub.py build\s40_sparse_manifest.json build\s41_cinematic_mesh --frames 8 --width 640 --height 360 --water-reconstruction build\s41_water_mesh\water_reconstruction.json
python -c "import json, os; s=json.load(open('build/s41_water_mesh/water_reconstruction.json')); assert s['frame_count'] >= 8; assert all(os.path.isfile(os.path.join('build/s41_water_mesh', f['mesh'])) for f in s['frames']); assert min(f['face_count'] for f in s['frames']) > 0; print(s['frame_count'])"
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Commit

```powershell
git add README.md tools\reconstruct_water.py tools\convert_render_cache.py tools\cinematic_render_stub.py docs\render_bridge_decision.md docs\superpowers\plans\2026-06-17-water-reconstruction-export.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add water reconstruction export"
git push origin main
```
