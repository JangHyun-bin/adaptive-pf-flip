# SPEC-4 Render Cache Sequence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first sequence-management layer for SPEC-4 render caches so exported 3D frames can be consumed as a validated multi-frame asset instead of loose JSONL files.

**Architecture:** `export_render_cache3d` keeps writing one JSONL cache per frame, then writes a small JSON manifest next to the frames. The Python preview tool accepts either loose frame inputs or the manifest and renders the frame list in manifest order. Unit tests pin the manifest schema without adding slow simulation work to default tests.

**Tech Stack:** C++17/MSVC, CMake, doctest, Python 3, numpy, Pillow.

---

## File Structure

- Modify `src/driver/render_cache3d.h`
  - Add `RenderCacheManifestFrame3D`.
  - Add `writeRenderCacheManifest3D(path, simKind, dims, dx, frames)`.
  - Keep frame JSONL writer APIs unchanged.
- Modify `apps/export_render_cache3d.cpp`
  - Add `--manifest PATH` optional CLI.
  - Default manifest path is `<out-prefix>_manifest.json`.
  - Record frame path, index, simulation step, time, and file size.
- Modify `tools/render_cache_preview.py`
  - Accept `*.json` manifest input in addition to JSONL file, directory, and glob input.
  - Resolve manifest frame paths relative to the manifest file directory.
- Modify `tests/test_render_cache3d.cpp`
  - Add a fast manifest schema test.
- Modify `README.md`
  - Add S32 status line and Quickstart manifest usage.

## Continuation Roadmap

1. S32 render cache manifest + sequence tooling.
2. S33 render cache QA validator for missing sections, non-finite values, volume drift, and frame ordering.
3. S34 secondary render layer preview controls for droplet/bubble age, velocity, and type inspection.
4. S35 secondary particle physics upgrade for drag, buoyancy, reabsorption, and mass/volume coupling.
5. S36 large-scale benchmark v2 with cache/export/preview timing and peak memory diagnostics.

## Task 1: Manifest Writer

**Files:**
- Modify: `src/driver/render_cache3d.h`
- Test: `tests/test_render_cache3d.cpp`

- [ ] **Step 1: Add a failing doctest for manifest sections**

Add a test that writes two manifest frames and checks for:
- `"lsfs_cache3d_manifest_version":1`
- `"sim_kind":"sparse3d_tp"`
- `"dims":[8,12,8]`
- `"path":"cache_000.jsonl"`
- `"step":3`

- [ ] **Step 2: Run the Debug cache test**

Run: `.\build\Debug\unit_tests.exe --test-case="*render cache*"`

Expected before implementation: compile failure or missing symbol for `writeRenderCacheManifest3D`.

- [ ] **Step 3: Implement manifest schema writer**

Add a small manifest frame struct and a JSON writer in `render_cache3d.h`. Validate positive dims/dx, finite times, non-empty paths, and non-negative indices/steps/sizes.

- [ ] **Step 4: Run the Debug cache test**

Run: `cmake --build build --config Debug --target unit_tests; .\build\Debug\unit_tests.exe --test-case="*render cache*"`

Expected: PASS.

## Task 2: Export Runner Manifest

**Files:**
- Modify: `apps/export_render_cache3d.cpp`

- [ ] **Step 1: Add CLI path handling**

Add `--manifest PATH`, defaulting to `<out-prefix>_manifest.json`.

- [ ] **Step 2: Record frame metadata**

After each frame write, store frame index, simulation step, time, path, and byte size.

- [ ] **Step 3: Write manifest at the end**

Call `writeRenderCacheManifest3D` after sparse or MR export completes.

- [ ] **Step 4: Smoke sparse export**

Run: `.\build\Release\export_render_cache3d.exe --kind sparse --steps 2 --every 2 --out-prefix build\manifest_smoke_sparse`

Expected: `build\manifest_smoke_sparse_manifest.json` exists and `status=ok` remains printed.

## Task 3: Preview Manifest Input

**Files:**
- Modify: `tools/render_cache_preview.py`

- [ ] **Step 1: Add manifest detection**

When the source is a JSON file, parse it as a manifest if it contains `lsfs_cache3d_manifest_version`.

- [ ] **Step 2: Resolve frame paths**

Resolve relative frame paths against the manifest file directory.

- [ ] **Step 3: Smoke manifest preview**

Run: `python tools\render_cache_preview.py build\manifest_smoke_sparse_manifest.json build\manifest_preview_sparse 4`

Expected: `build\manifest_preview_sparse\cache_preview.gif` exists.

## Task 4: Docs, Verification, Commit

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add README status and Quickstart command**

Add S32 and show preview from the manifest path.

- [ ] **Step 2: Run verification**

Run:

```powershell
python -m py_compile tools\render_cache_preview.py
cmake --build build --config Debug --target unit_tests
cmake --build build --config Release --target export_render_cache3d
.\build\Debug\unit_tests.exe --test-case="*render cache*"
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

- [ ] **Step 3: Commit and push**

Run:

```powershell
git add README.md src\driver\render_cache3d.h apps\export_render_cache3d.cpp tests\test_render_cache3d.cpp tools\render_cache_preview.py docs\superpowers\plans\2026-06-17-spec4-render-cache-sequence.md
git commit -m "feat: add render cache manifest"
git push origin main
```
