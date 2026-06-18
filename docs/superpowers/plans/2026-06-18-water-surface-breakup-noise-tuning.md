# Water Surface Breakup Noise Tuning

## Goal

Tune the S93 contact foam/ripple integration so the main water surface has stronger breakup detail in the contact region without over-brightening the shot or breaking diagnostic gates.

## Scope

- Add `dam_break_water_surface_breakup_noise_tuned` as an inherited S93 preset.
- Increase water surface detail from strength `0.045`, scale `2.8`, depth `4` to strength `0.058`, scale `2.25`, depth `5`.
- Keep ripple readability review enabled with slightly stricter thresholds.
- Run an 8-frame Blender probe and a full 36-frame Blender gate against S93.
- Do not change simulation, cache schema, or default `ctest` behavior.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s93_contact_foam_ripple_integration\converted\sequence.json build\s94_water_surface_breakup_noise_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_surface_breakup_noise_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_surface_breakup_noise_tuned --out build\shots\s94_water_surface_breakup_noise_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s94.md --compare-review-manifest build\shots\s93_contact_foam_ripple_integration\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S94 generated:

- `build/shots/s94_water_surface_breakup_noise_tuning/shot.gif`
- `build/shots/s94_water_surface_breakup_noise_tuning/review/contact_sheet.png`
- `build/shots/s94_water_surface_breakup_noise_tuning/review/focus_comparison_sheet.png`
- `build/shots/s94_water_surface_breakup_noise_tuning/review/ripple_readability_comparison_sheet.png`
- `docs/reports/cinematic_gate_s94.md`

The final gate keeps visual QA, temporal highlight QA, camera stability, secondary framing QA, focus review QA, and ripple readability QA passing. Ripple readability comparison source count is `2`, comparing S93 against S94.

## Next

S95 should tune spray/foam depth layering so secondaries sit more naturally in the contact volume while preserving diagnostic, temporal, and secondary framing gates.
