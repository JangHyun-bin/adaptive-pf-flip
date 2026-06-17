# SPEC-4 Render Cache Validator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fast QA validator for SPEC-4 render cache manifests and JSONL frames so broken cache data fails before preview or rendering.

**Architecture:** A standalone Python validator reads either a S32 manifest JSON or loose JSONL frame inputs, validates manifest ordering and each frame's required sections, finite numeric fields, dimension consistency, particle positions, non-negative volumes, and water-volume drift. It uses only the Python standard library so it can run in CI or local smoke checks without numpy/Pillow.

**Tech Stack:** Python 3 standard library, existing C++ `export_render_cache3d`, CMake/ctest for regression coverage.

---

## File Structure

- Create `tools/validate_render_cache.py`
  - Accept `<manifest.json|cache.jsonl|cache-dir|glob>`.
  - Options: `--max-volume-drift`, `--allow-empty-secondary`, `--verbose`.
  - Exit `0` on valid cache, `1` on validation failure, `2` on bad CLI.
  - Print compact summary lines with frame count, particle count, phase cell count, and maximum volume drift.
- Modify `README.md`
  - Add S33 status line.
  - Add Quickstart command after render cache export.
- Modify `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`
  - Mark S33 as the next completed continuation item in the roadmap note.

## Task 1: Validator Core

**Files:**
- Create: `tools/validate_render_cache.py`

- [ ] **Step 1: Implement input discovery**

Support the same input shapes as `tools/render_cache_preview.py`:

```powershell
python tools\validate_render_cache.py build\manifest_smoke_sparse_manifest.json
python tools\validate_render_cache.py build\manifest_smoke_sparse_000.jsonl
python tools\validate_render_cache.py "build\manifest_smoke_sparse_*.jsonl"
```

Expected: manifest input resolves frame paths relative to the manifest directory.

- [ ] **Step 2: Implement manifest checks**

Validate:
- `lsfs_cache3d_manifest_version == 1`
- `sim_kind` is `sparse3d_tp` or `multires3d_tp`
- `dims` is three positive integers
- `dx` is finite and positive
- `frame_count == len(frames)`
- each frame has monotonic `frame`, positive `step`, finite nondecreasing `time`, non-empty `path`, and non-negative `bytes`
- referenced frame files exist

- [ ] **Step 3: Implement JSONL frame checks**

Validate each frame contains exactly one header, at least one camera, water-volume summary, phase-field declaration, and primary particle declaration. Validate header dims/dx against manifest when present. Validate all `phase_cell` and `particle` numeric fields are finite, positions are inside `[0,nx*dx] x [0,ny*dx] x [0,nz*dx]` with a small tolerance, and particle/phase volumes are non-negative.

- [ ] **Step 4: Implement water-volume drift gate**

For multi-frame input, compare total water-like volume per frame:

```text
phase_field_liquid_volume + primary_liquid_volume + secondary_droplet_volume + secondary_bubble_volume
```

Fail if the relative drift from frame 0 exceeds `--max-volume-drift`, default `0.25`.

## Task 2: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`

- [ ] **Step 1: Add README status and command**

Add S33 and show:

```powershell
python tools/validate_render_cache.py render_cache_sparse_manifest.json
python tools/render_cache_preview.py render_cache_sparse_manifest.json build/render_cache_preview 6
```

- [ ] **Step 2: Update continuation note**

Change the sequence plan's roadmap note so S33 is no longer only future work.

## Task 3: Verification

**Files:**
- Generated outputs stay under `build/`.

- [ ] **Step 1: Compile validator**

Run:

```powershell
python -m py_compile tools\validate_render_cache.py
```

Expected: exit `0`.

- [ ] **Step 2: Build exporter**

Run:

```powershell
cmake --build build --config Release --target export_render_cache3d
```

Expected: exit `0`.

- [ ] **Step 3: Valid sparse and MR smoke**

Run:

```powershell
.\build\Release\export_render_cache3d.exe --kind sparse --steps 2 --every 2 --out-prefix build\validator_sparse
python tools\validate_render_cache.py build\validator_sparse_manifest.json
.\build\Release\export_render_cache3d.exe --kind mr --steps 2 --every 2 --out-prefix build\validator_mr
python tools\validate_render_cache.py build\validator_mr_manifest.json
```

Expected: both validator runs print `status=ok`.

- [ ] **Step 4: Invalid drift smoke**

Run:

```powershell
python tools\validate_render_cache.py build\validator_sparse_manifest.json --max-volume-drift 0
```

Expected: exit `1` with a volume drift validation error.

- [ ] **Step 5: Full repo checks**

Run:

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

Expected: tests pass; only existing CRLF warnings are acceptable.

## Task 4: Commit

**Files:**
- Stage `tools/validate_render_cache.py`, `README.md`, and both plan docs.

- [ ] **Step 1: Commit and push**

Run:

```powershell
git add README.md tools\validate_render_cache.py docs\superpowers\plans\2026-06-17-spec4-render-cache-sequence.md docs\superpowers\plans\2026-06-17-spec4-render-cache-validator.md
git commit -m "test: add render cache validator"
git push origin main
```
