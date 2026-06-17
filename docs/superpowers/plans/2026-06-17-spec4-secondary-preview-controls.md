# SPEC-4 Secondary Preview Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make secondary droplet/bubble render-cache data inspectable in preview output by adding type, age, and speed visualization controls.

**Architecture:** Keep the existing `tools/render_cache_preview.py` input contract and positional CLI compatibility, but add argparse options for secondary visualization mode, gain, radius, and primary-water visibility. Secondary particles are already present in the cache schema, so the change is a preview-layer upgrade only; the export schema and validator remain unchanged.

**Tech Stack:** Python 3, numpy, Pillow, existing `export_render_cache3d`, existing `validate_render_cache.py`, CMake/ctest.

---

## File Structure

- Modify `tools/render_cache_preview.py`
  - Add argparse while preserving `src out_dir scale` positional usage.
  - Add `--secondary-mode type|age|speed`.
  - Add `--secondary-gain FLOAT`.
  - Add `--secondary-radius FLOAT`.
  - Add `--hide-primary-water`.
  - Render droplet and bubble overlays with type colors, age ramp, or speed ramp.
- Modify `README.md`
  - Add S34 status line.
  - Add example preview commands for `--secondary-mode age` and `--secondary-mode speed`.
- Modify `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`
  - Mark S34 as completed and leave S35/S36 as next steps.

## Task 1: Preview CLI

**Files:**
- Modify: `tools/render_cache_preview.py`

- [ ] **Step 1: Add argparse wrapper**

Preserve:

```powershell
python tools\render_cache_preview.py render_cache_sparse_manifest.json build\render_cache_preview 6
```

Add:

```powershell
python tools\render_cache_preview.py render_cache_sparse_manifest.json build\render_cache_preview_age 6 --secondary-mode age
python tools\render_cache_preview.py render_cache_sparse_manifest.json build\render_cache_preview_speed 6 --secondary-mode speed --hide-primary-water
```

- [ ] **Step 2: Validate CLI values**

`scale > 0`, `secondary_gain >= 0`, and `secondary_radius > 0` must be enforced by argparse or explicit checks.

## Task 2: Secondary Layers

**Files:**
- Modify: `tools/render_cache_preview.py`

- [ ] **Step 1: Track weighted secondary splats**

For each `secondary_droplet` or `secondary_bubble`, accumulate:
- type density
- age weighted density if `age` exists, otherwise `0`
- speed weighted density from velocity magnitude

- [ ] **Step 2: Add color modes**

Mode behavior:
- `type`: droplets use cyan-white, bubbles use warm amber.
- `age`: young secondaries use cyan-white, older secondaries ramp to orange/red.
- `speed`: slow secondaries use blue, faster secondaries ramp to yellow/white.

- [ ] **Step 3: Preserve baseline output**

Default invocation should produce visually similar output to S31/S32 when no secondary particles are present.

## Task 3: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`

- [ ] **Step 1: Add S34 docs**

Add S34 to README and add preview examples after cache validation.

- [ ] **Step 2: Smoke real sparse/MR cache**

Run:

```powershell
cmake --build build --config Release --target export_render_cache3d
.\build\Release\export_render_cache3d.exe --kind sparse --steps 2 --every 2 --out-prefix build\s34_sparse
python tools\validate_render_cache.py build\s34_sparse_manifest.json
python tools\render_cache_preview.py build\s34_sparse_manifest.json build\s34_preview_type 4 --secondary-mode type
python tools\render_cache_preview.py build\s34_sparse_manifest.json build\s34_preview_age 4 --secondary-mode age
python tools\render_cache_preview.py build\s34_sparse_manifest.json build\s34_preview_speed 4 --secondary-mode speed --hide-primary-water
```

Expected: all commands exit `0`, GIFs exist.

- [ ] **Step 3: Smoke synthetic secondary cache**

Patch a generated cache under `build/` to include one secondary droplet and one secondary bubble, update the manifest byte size, then validate and render all secondary modes.

- [ ] **Step 4: Full checks**

Run:

```powershell
python -m py_compile tools\render_cache_preview.py
python -m py_compile tools\validate_render_cache.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

Expected: all pass; CRLF warnings are acceptable.

## Task 4: Commit

**Files:**
- Stage `README.md`, `tools/render_cache_preview.py`, and the plan docs.

- [ ] **Step 1: Commit and push**

Run:

```powershell
git add README.md tools\render_cache_preview.py docs\superpowers\plans\2026-06-17-spec4-render-cache-sequence.md docs\superpowers\plans\2026-06-17-spec4-secondary-preview-controls.md
git commit -m "feat: add secondary render cache preview controls"
git push origin main
```
