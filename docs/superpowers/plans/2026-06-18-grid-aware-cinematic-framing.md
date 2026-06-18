# Grid-Aware Cinematic Framing

## Goal

Keep high-detail cinematic gates framed when the simulation grid is overridden above the preset's reference dimensions.

## Approach

- Add `camera.auto_frame` to cinematic render presets.
- Apply framing in `tools/render_bridge_blender.py` after static/motion camera preset evaluation.
- Use reference dims and reference center to scale:
  - camera target from the reference grid center to the current grid center
  - camera distance vector from target to position
  - optional vertical FOV padding
- Preserve existing motion keys; auto framing runs after interpolation.
- Record `camera_framing` in Blender bridge summaries and generated shot reports.

## Validation

```powershell
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json > $null
python tools\render_bridge_blender.py build\shots\s54_high_detail_surface\converted\sequence.json build\s55_camera_frame_dry --frames 2 --width 320 --height 180 --dry-run --max-secondary-particles 128 --secondary-radius-scale 2.4 --preset-config configs\cinematic_presets.json --render-preset dam_break_cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s55_grid_aware_camera --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs\reports\cinematic_gate_s55.md --no-build --timeout-seconds 900
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

The S55 contact sheet keeps the same high-detail tetra surface density as S54 but removes the top crop by applying a 1.25 camera framing scale.

## Next

S56 should begin replacing demo secondary seeding with physical spray generation and keep the review-pack gate as the visual acceptance loop.
