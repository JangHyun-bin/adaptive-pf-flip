# Smooth Cinematic Water Meshes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the cinematic water body visibly less blocky by adding opt-in OBJ mesh smoothing and normals to the water reconstruction path.

**Architecture:** Keep the original voxel OBJ export as the default for compatibility. Add Laplacian smoothing and vertex-normal emission behind explicit CLI flags, then let cinematic presets and the shot runner opt into those flags.

**Tech Stack:** Python 3 standard library, existing render-cache JSONL/CSV inputs, OBJ mesh output, Blender bridge.

---

### Task 1: Reconstruction Smoothing

**Files:**
- Modify: `tools/reconstruct_water.py`

- [ ] **Step 1: Add CLI**

Add:

```powershell
--smooth-iterations N
--smooth-alpha A
--write-normals
```

Defaults preserve current behavior: zero smoothing and no normals unless requested.

- [ ] **Step 2: Smooth mesh vertices**

After generating exposed voxel faces, build vertex adjacency from faces and run bounded Laplacian smoothing:

```text
next = vertex * (1 - alpha) + average(neighbors) * alpha
```

- [ ] **Step 3: Write vertex normals**

When `--write-normals` is set, write one `vn` per vertex and faces as `f v//vn`.

### Task 2: Runner and Preset Wiring

**Files:**
- Modify: `tools/run_cinematic_shot.py`
- Modify: `configs/cinematic_presets.json`

- [ ] **Step 1: Add reconstruction preset section**

Add `reconstruction` to presets:

```json
{
  "smooth_iterations": 2,
  "smooth_alpha": 0.18,
  "write_normals": true
}
```

- [ ] **Step 2: Pass options to reconstruction**

The runner must pass smoothing and normal options into `reconstruct_water.py`.

### Task 3: Validation

**Files:**
- Generated under `build/`

- [ ] **Step 1: Compile**

```powershell
python -m py_compile tools\reconstruct_water.py tools\run_cinematic_shot.py
```

- [ ] **Step 2: Direct reconstruction smoke**

```powershell
python tools\reconstruct_water.py build\shots\s45_bubble\cache\manifest.json build\s46_smooth_mesh --frames 4 --smooth-iterations 2 --smooth-alpha 0.18 --write-normals
```

Expected: `water_reconstruction.json` records smoothing settings and OBJ files contain `vn` lines.

- [ ] **Step 3: Runner smoke**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s46_smooth --frames 4 --sim-steps 2 --width 640 --height 360 --renderer blender --samples 8 --no-build
```

Expected: summary reports smoothing settings and rendered frames exist.

### Task 4: Documentation and Commit

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: Mark S46 done**

Update README and roadmap.

- [ ] **Step 2: Commit and push**

```powershell
git add README.md configs\cinematic_presets.json tools\reconstruct_water.py tools\run_cinematic_shot.py docs\superpowers\plans\2026-06-18-smooth-cinematic-water-meshes.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: smooth cinematic water meshes"
git push origin main
```
