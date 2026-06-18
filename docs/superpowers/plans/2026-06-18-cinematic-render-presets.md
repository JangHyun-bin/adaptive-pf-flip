# Cinematic Render Presets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add named cinematic render presets for camera, materials, lighting, tone mapping, renderer choice, and shot dimensions, then make the S43 runner and Blender bridge consume them.

**Architecture:** Keep presets as data in `configs/cinematic_presets.json`. `tools/run_cinematic_shot.py` loads simulation and render defaults from the chosen preset, while `tools/render_bridge_blender.py` loads the same preset and writes it into `blender_scene_spec.json` for the generated Blender driver.

**Tech Stack:** Python 3 standard library, JSON preset schema, existing S43 shot runner, existing S42 Blender bridge, Blender background rendering.

---

### Task 1: Preset Schema

**Files:**
- Create: `configs/cinematic_presets.json`

- [ ] **Step 1: Add two presets**

Create `bubble_cinematic` and `dam_break_cinematic`. Each preset must include:

- `simulation`
- `shot`
- `renderer`
- `camera`
- `lighting`
- `materials`
- `tone_mapping`

`bubble_cinematic` preserves the current small sparse bubble smoke defaults. `dam_break_cinematic` is a look/shot preset for the next scene class; it can still run through the current bubble exporter until a dam-break render-cache exporter exists.

### Task 2: Runner Integration

**Files:**
- Modify: `tools/run_cinematic_shot.py`

- [ ] **Step 1: Add preset config CLI**

Add:

```powershell
--preset-config configs/cinematic_presets.json
--render-preset NAME
```

`--preset` selects simulation/shot defaults. `--render-preset` defaults to `--preset`.

- [ ] **Step 2: Load preset values**

Use the selected preset to fill defaults for:

- `kind`
- `nx`, `ny`, `nz`
- `dt`
- `cg_iters`
- `physics_preset`
- `frames`
- `sim_steps`
- `cache_every`
- `width`, `height`
- `renderer`
- `samples`
- `max_secondary_particles`
- `fps`

CLI values still override preset values.

- [ ] **Step 3: Pass preset to Blender bridge**

When calling `render_bridge_blender.py`, pass:

```powershell
--preset-config configs\cinematic_presets.json --render-preset bubble_cinematic
```

Record the loaded preset path and names in `shot_summary.json`.

### Task 3: Blender Bridge Integration

**Files:**
- Modify: `tools/render_bridge_blender.py`

- [ ] **Step 1: Add preset config CLI**

Add:

```powershell
--preset-config configs/cinematic_presets.json
--render-preset bubble_cinematic
```

- [ ] **Step 2: Write preset into scene spec**

`blender_scene_spec.json` must include:

```json
{
  "render_preset_name": "bubble_cinematic",
  "render_preset": { "...": "..." }
}
```

- [ ] **Step 3: Apply preset in Blender driver**

Use preset values for:

- tone mapping view transform, look, exposure, gamma
- world color
- key area light and sun light
- water/floor/droplet/spray/foam/bubble material colors, roughness, alpha, transmission
- optional camera position, target, FOV/lens override

### Task 4: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: README**

Add S44 status and quickstart examples:

```powershell
python tools/run_cinematic_shot.py --preset bubble_cinematic --out build/shots/bubble_cinematic --frames 24 --width 1280 --height 720
python tools/run_cinematic_shot.py --preset dam_break_cinematic --out build/shots/dam_break_cinematic --frames 24 --width 1280 --height 720
```

- [ ] **Step 2: Roadmap**

Mark S44 done and set next immediate action to S45 large-scale cinematic gate.

### Task 5: Validation

**Files:**
- Generated outputs under `build/`

- [ ] **Step 1: Compile Python**

```powershell
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
```

- [ ] **Step 2: Preset dry-run**

```powershell
python tools\render_bridge_blender.py build\s42_convert_with_mesh\sequence.json build\s44_preset_dry --frames 2 --width 240 --height 135 --dry-run --preset-config configs\cinematic_presets.json --render-preset bubble_cinematic
```

- [ ] **Step 3: Runner smoke**

```powershell
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\shots\s44_bubble --frames 4 --sim-steps 2 --width 320 --height 180 --renderer blender --samples 8 --no-build
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s44_dam --frames 2 --sim-steps 2 --width 240 --height 135 --renderer preview --no-build
```

- [ ] **Step 4: Regression**

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

### Task 6: Commit

**Files:**
- `README.md`
- `configs/cinematic_presets.json`
- `tools/run_cinematic_shot.py`
- `tools/render_bridge_blender.py`
- `docs/superpowers/plans/2026-06-18-cinematic-render-presets.md`
- `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

- [ ] **Step 1: Commit and push**

```powershell
git add README.md configs\cinematic_presets.json tools\run_cinematic_shot.py tools\render_bridge_blender.py docs\superpowers\plans\2026-06-18-cinematic-render-presets.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add cinematic render presets"
git push origin main
```
