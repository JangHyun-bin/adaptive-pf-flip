# S49 Cinematic Camera Motion

**Goal:** Add preset-driven camera motion so cinematic shots can move from static framing toward shot grammar and continuity checks.

## Scope

- Keep cache camera metadata unchanged.
- Precompute final render cameras in the Blender bridge scene spec.
- Preserve compatibility with older scene specs by letting the Blender driver apply static presets only when cameras are not precomputed.
- Add a moving camera path to `dam_break_cinematic`.
- Report camera-motion status in dry-run summaries and generated shot reports.

## Implementation

- `tools/render_bridge_blender.py`
  - Add camera keyframe interpolation in scene-spec generation.
  - Support `camera.motion.enabled`, `camera.motion.easing`, and keyed `path` entries.
  - Write `camera_motion` summary to `bridge_summary.json`.
  - Avoid reapplying static preset camera values over precomputed frame cameras in the Blender driver.

- `configs/cinematic_presets.json`
  - Add a 3-key smoothstep camera path to `dam_break_cinematic`.

- `tools/run_cinematic_shot.py`
  - Copy camera-motion status from `bridge_summary.json` into `shot_summary.json`.
  - Include camera-motion status in generated markdown reports.

## Validation

```powershell
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json
python tools\render_bridge_blender.py build\s48_secondary_convert_mesh\sequence.json build\s49_camera_dry --frames 4 --width 320 --height 180 --dry-run --max-secondary-particles 128 --secondary-radius-scale 2.4 --preset-config configs\cinematic_presets.json --render-preset dam_break_cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s49_camera_motion --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --report docs\reports\cinematic_gate_s49.md --no-build
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S50 should improve water material response with depth tint, rim highlights, and preset sweeps.
