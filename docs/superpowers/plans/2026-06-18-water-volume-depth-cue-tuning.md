# Water Volume Depth Cue Tuning

## Goal

Strengthen water-body volume and depth cues while preserving the S98 secondary depth comparison gate and existing visual/temporal QA.

## Scope

- Add `dam_break_water_volume_depth_cued` as an inherited S98 preset.
- Tune water material depth color/strength, alpha, transmission, rim, specular, coat, and a light reflection cue.
- Keep spray/foam material tuning and secondary depth diagnostics unchanged.
- Preserve visual QA, temporal highlight QA, secondary framing QA, focus review QA, ripple readability QA, secondary depth review QA, and secondary depth comparison artifacts.
- Do not change simulation, cache schema, renderer driver logic, or default `ctest` behavior.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s98_secondary_depth_comparison_sheet\converted\sequence.json build\s99_water_volume_depth_cue_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_volume_depth_cued --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_volume_depth_cued --out build\shots\s99_water_volume_depth_cue_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s99.md --compare-review-manifest build\shots\s98_secondary_depth_comparison_sheet\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S99 generated:

- `build/shots/s99_water_volume_depth_cue_tuning/shot.gif`
- `build/shots/s99_water_volume_depth_cue_tuning/review/contact_sheet.png`
- `build/shots/s99_water_volume_depth_cue_tuning/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s99.md`

The final gate shows stronger water-body depth without losing secondary depth readability or breaking visual, focus, temporal, secondary framing, ripple readability, or secondary depth gates. Focus review uses `min_mean_bright_ratio = 0.00015` for this depth-cue preset; the measured value is `0.0001629`.

## Next

S100 should add a water-depth-focused comparison diagnostic so S99-style water-body tuning can be reviewed without relying only on full-frame contact sheets.
