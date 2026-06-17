# First Cinematic Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce local cinematic PNG/GIF previews from LSFS render cache manifests or converted S38 `sequence.json` bundles.

**Architecture:** Keep this as a renderer stub, not the final renderer. It loads either canonical JSONL cache frames or S38 converted CSV/JSON assets into one internal frame model, projects the water/secondary data through a fixed camera, writes `frame_####.png`, then uses a separate assembler for `preview.gif`. It also writes `render_summary.json` with pixel occupancy so nonblank visual output is machine-checkable.

**Tech Stack:** Python 3, Pillow, JSON/JSONL, CSV.

---

## File Structure

- Create `tools/cinematic_render_stub.py`
  - Load manifest JSON or converted `sequence.json`.
  - Parse camera metadata, phase cells, and particle channels.
  - Render cinematic preview PNG frames.
  - Write `render_summary.json` with per-frame occupancy.
- Create `tools/assemble_frames.py`
  - Assemble a directory of `frame_####.png` images into a GIF.
  - Fail gracefully when Pillow is unavailable.
- Modify `README.md`
  - Add S39 status row and quickstart commands.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S39 done and set S40 as the next immediate action.

## Tasks

### Task 1: Add Cinematic Renderer Stub

**Files:**
- Create: `tools/cinematic_render_stub.py`

- [ ] **Step 1: Implement input loading**

Support:

```powershell
python tools\cinematic_render_stub.py build\s37_sparse_manifest.json build\cinematic_preview --frames 12 --width 1280 --height 720
python tools\cinematic_render_stub.py build\s38_convert_smoke\sequence.json build\cinematic_preview_from_sequence --frames 12 --width 1280 --height 720
```

- [ ] **Step 2: Implement rendering**

Draw:

- background gradient
- projected phase-cell water mass
- liquid primary particles as subtle water reinforcement
- secondary droplets/bubbles as visible particle channels
- time/frame overlay-free output, no UI text inside images

- [ ] **Step 3: Implement occupancy summary**

Write `render_summary.json` with:

- `frame_count`
- `min_occupancy`
- per-frame `occupancy`, `water_pixels`, `secondary_pixels`
- output image paths relative to preview directory

### Task 2: Add Frame Assembler

**Files:**
- Create: `tools/assemble_frames.py`

- [ ] **Step 1: Implement GIF assembly**

Command:

```powershell
python tools\assemble_frames.py build\cinematic_preview build\cinematic_preview.gif --fps 12
```

- [ ] **Step 2: Fail gracefully**

If Pillow is missing, print a clear message and return non-zero without deleting PNG frames.

### Task 3: Update Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: Add S39 README row and quickstart**

Include the render and assemble commands after cache conversion.

- [ ] **Step 2: Mark roadmap S39 done**

Set next action to S40 secondary spray/foam visual channels.

### Task 4: Verify and Commit

**Files:**
- All S39 files

- [ ] **Step 1: Syntax check**

```powershell
python -m py_compile tools\cinematic_render_stub.py tools\assemble_frames.py
```

- [ ] **Step 2: Render from manifest**

```powershell
python tools\cinematic_render_stub.py build\s37_sparse_manifest.json build\s39_preview_manifest --frames 12 --width 640 --height 360
python tools\assemble_frames.py build\s39_preview_manifest build\s39_preview_manifest.gif --fps 12
```

- [ ] **Step 3: Render from converted sequence**

```powershell
python tools\cinematic_render_stub.py build\s38_convert_smoke\sequence.json build\s39_preview_sequence --frames 12 --width 640 --height 360
```

- [ ] **Step 4: Check occupancy**

```powershell
python -c "import json; s=json.load(open('build/s39_preview_manifest/render_summary.json')); assert s['frame_count'] >= 12; assert s['min_occupancy'] > 0.01; print(s['frame_count'], s['min_occupancy'])"
```

- [ ] **Step 5: Run repo gates**

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

- [ ] **Step 6: Commit and push**

```powershell
git add README.md tools\cinematic_render_stub.py tools\assemble_frames.py docs\superpowers\plans\2026-06-17-first-cinematic-preview.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add cinematic cache preview renderer"
git push origin main
```
