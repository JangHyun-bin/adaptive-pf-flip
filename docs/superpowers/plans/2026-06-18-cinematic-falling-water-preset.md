# S47 Cinematic Falling-Water / Dam-Break Preset

**Goal:** Make the cinematic pipeline produce a visibly dynamic sparse 3D two-phase water-motion shot instead of always exporting the bubble-tank scene.

## Scope

- Add explicit scene selection to `export_render_cache3d`.
- Keep the existing bubble-tank default for compatibility.
- Route `dam_break_cinematic` through a dynamic sparse falling-water scene while keeping `--scene dam-break` available for the existing dam-break initializer.
- Pass scene selection through `tools/run_cinematic_shot.py` and `configs/cinematic_presets.json`.
- Leave MR dam-break export out of this slice because `MRSim3DTP` currently exposes only the bubble-tank interface-band initializer.

## Implementation

- `apps/export_render_cache3d.cpp`
  - Add `--scene bubble|dam-break|falling-water`.
  - For sparse runs, call `initBubbleTank()`, `initTwoPhaseDamBreak()`, or `initFallingWaterColumn()`.
  - For MR runs, reject non-bubble scenes with a clear error.
  - Print the canonical selected scene in stdout metrics.

- `src/driver/sparse_sim3d_tp.cpp`
  - Add `initFallingWaterColumn()` with a suspended liquid block and small initial downward velocity for readable motion.

- `tools/run_cinematic_shot.py`
  - Add `--scene`.
  - Include `scene` in effective config and `shot_summary.json`.
  - Pass `--scene` to the exporter.
  - Make generated reports mention the selected scene.

- `configs/cinematic_presets.json`
  - Mark `bubble_cinematic` as `scene: bubble`.
  - Mark `dam_break_cinematic` as `scene: falling-water`.

## Validation

```powershell
cmake --build build --config Release --target export_render_cache3d
.\build\Release\export_render_cache3d.exe --kind sparse --scene falling-water --steps 2 --every 1 --out-prefix build\s47_falling_cache --manifest build\s47_falling_manifest.json
python tools\validate_render_cache.py build\s47_falling_manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s47_dam_break --frames 8 --sim-steps 4 --width 640 --height 360 --renderer blender --samples 8 --report docs\reports\cinematic_gate_s47.md --no-build
python -m py_compile tools\run_cinematic_shot.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S48 should make secondary droplet, spray, foam, and bubble channels visible enough to read in cinematic frames.
