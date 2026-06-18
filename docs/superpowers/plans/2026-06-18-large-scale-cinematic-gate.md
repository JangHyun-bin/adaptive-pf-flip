# Large-Scale Cinematic Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the first larger end-to-end cinematic gate with a 48-frame shot, durable summary JSON, GIF artifact, and checked-in report.

**Architecture:** Keep the gate opt-in. Extend the S43 runner with a report writer, run the existing cache/validation/conversion/reconstruction/render pipeline at a larger frame count, and check in only the report and code/docs, not heavy generated build artifacts.

**Tech Stack:** Python 3 standard library, existing S43 shot runner, S44 cinematic presets, Blender bridge or preview fallback, CMake/ctest for regression.

---

### Task 1: Runner Report Output

**Files:**
- Modify: `tools/run_cinematic_shot.py`

- [ ] **Step 1: Add report CLI**

Add:

```powershell
--report docs/reports/cinematic_gate_s45.md
```

The report must include:

- shot status
- preset and renderer
- frame count and resolution
- artifact paths
- per-stage elapsed time
- cache/mesh/GIF metrics
- known limitations
- next recommended milestone

### Task 2: Gate Execution

**Files:**
- Generated under `build/shots/s45_bubble`
- Create: `docs/reports/cinematic_gate_s45.md`

- [ ] **Step 1: Run the gate**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s45_bubble --frames 48 --width 1280 --height 720 --samples 12 --report docs\reports\cinematic_gate_s45.md --no-build
```

- [ ] **Step 2: Verify summary**

Confirm:

- `shot_summary.json` has `status=ok`
- selected renderer is recorded
- `config.frames >= 48`
- `metrics.water_mesh_frame_count >= 48`
- `shot.gif` exists and has non-zero bytes
- report exists under `docs/reports/`

### Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: README**

Add S45 status and the large gate command.

- [ ] **Step 2: Roadmap**

Mark S45 done and set the next immediate action to the post-S45 visual-quality roadmap.

### Task 4: Validation

**Files:**
- Test generated outputs under `build/`

- [ ] **Step 1: Compile**

```powershell
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
```

- [ ] **Step 2: Regression**

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

### Task 5: Commit

**Files:**
- `README.md`
- `tools/run_cinematic_shot.py`
- `docs/reports/cinematic_gate_s45.md`
- `docs/superpowers/plans/2026-06-18-large-scale-cinematic-gate.md`
- `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: Commit and push**

```powershell
git add README.md tools\run_cinematic_shot.py docs\reports\cinematic_gate_s45.md docs\superpowers\plans\2026-06-18-large-scale-cinematic-gate.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "test: add large scale cinematic gate"
git push origin main
```
