# S48 Visible Secondary Cinematic Render

**Goal:** Make droplet, spray, foam, and bubble secondary channels visibly present in cinematic Blender frames.

## Scope

- Keep physical escaped-particle branching unchanged.
- Add an opt-in exporter hook for deterministic render-demo secondary particles.
- Keep the hook disabled by default for normal simulation, validation, and benchmark runs.
- Add Blender radius scaling so secondary particles remain readable at shot scale.
- Update the cinematic preset and checked-in report with an explicit note that this is a render-demo seed, not the final physical spray model.

## Implementation

- `apps/export_render_cache3d.cpp`
  - Add `--secondary-demo-particles N`.
  - If `N > 0`, seed deterministic secondary droplet/bubble containers just before each cache frame write.
  - Populate droplet ages and velocities so existing render-channel classification emits spray, droplet, foam, and bubble channels.

- `tools/run_cinematic_shot.py`
  - Add `--secondary-demo-particles` and `--secondary-radius-scale`.
  - Pass both through to exporter/Blender bridge.
  - Record both in `shot_summary.json` and generated reports.

- `tools/render_bridge_blender.py`
  - Add `--secondary-radius-scale`.
  - Store it in `blender_scene_spec.json`.
  - Scale secondary sphere radii while preserving the existing cap.

- `configs/cinematic_presets.json`
  - Keep `bubble_cinematic` secondary demo disabled.
  - Enable `dam_break_cinematic` with 96 demo secondary particles and a readable radius scale.

## Validation

```powershell
cmake --build build --config Release --target export_render_cache3d
.\build\Release\export_render_cache3d.exe --kind sparse --scene falling-water --steps 4 --every 1 --secondary-demo-particles 96 --out-prefix build\s48_secondary_cache --manifest build\s48_secondary_manifest.json
python tools\validate_render_cache.py build\s48_secondary_manifest.json --require-cinematic
python tools\convert_render_cache.py build\s48_secondary_manifest.json build\s48_secondary_convert --require-cinematic
python tools\render_bridge_blender.py build\s48_secondary_convert\sequence.json build\s48_secondary_blender --frames 2 --width 320 --height 180 --dry-run --max-secondary-particles 128 --secondary-radius-scale 2.4 --preset-config configs\cinematic_presets.json --render-preset dam_break_cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s48_secondary --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --report docs\reports\cinematic_gate_s48.md --no-build
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S49 should add camera motion and shot continuity checks. Physical spray generation remains a later physics task.
