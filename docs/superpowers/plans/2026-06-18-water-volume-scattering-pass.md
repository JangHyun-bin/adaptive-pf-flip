# Water Volume Scattering Pass

## Goal

Add an opt-in water volume scattering/attenuation render pass so the main water body reads less like a flat transparent slab while preserving the S100 diagnostic gates.

## Scope

- Add `renderer.water_volume_scattering_pass` to the Blender bridge scene spec and bridge summary.
- Add a frame-local water volume scattering mesh pass made from thin translucent attenuation sheets inside the water region.
- Add `materials.water_volume_scatter` for the pass material.
- Add `dam_break_water_volume_scattering` as an inherited S100 preset.
- Keep simulation, cache schema, water mesh reconstruction, camera, and existing water material settings unchanged.
- Preserve visual QA, temporal highlight QA, focus review QA, ripple readability QA, secondary depth review QA, and comparison artifacts.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s100_water_depth_focus_comparison\converted\sequence.json build\shots\s102_water_volume_scattering_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_volume_scattering --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_volume_scattering --out build\shots\s102_water_volume_scattering --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s102.md --compare-review-manifest build\shots\s100_water_depth_focus_comparison\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S102 generated:

- `build/shots/s102_water_volume_scattering/shot.gif`
- `build/shots/s102_water_volume_scattering/review/contact_sheet.png`
- `build/shots/s102_water_volume_scattering/review/focus_comparison_sheet.png`
- `build/shots/s102_water_volume_scattering/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s102.md`

The full gate passed with `water_volume_scattering_pass` enabled:

- layers: `5`
- region min/max: `[0.8, 4.45, 3.2] / [27.2, 7.65, 19.0]`
- alpha/emission scale: `0.24 / 0.22`
- visual QA mean luminance: `101.3397`
- visual QA min contrast: `127.0`
- focus crop mean luminance: `92.4696`
- focus crop min contrast: `72.0`
- temporal max mean delta: `10.0695`

The probe and full contact sheets show a subtle internal attenuation cue without turning the water body into a fog layer.

## Next

S103 should add a secondary render integration review that checks spray/foam/bubble layers against the S102 water volume scattering baseline without weakening visual, focus, temporal, ripple, secondary depth, and comparison gates.
