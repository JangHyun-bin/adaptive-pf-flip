# Secondary Volume Depth Material Tuning

## Goal

Use the S96 secondary depth diagnostic to tune spray and foam material readability so the contact volume reads as softer depth, not as a bright overlay of separate particles.

## Scope

- Add `dam_break_secondary_volume_depth_tuned` as an inherited S96 preset.
- Keep `secondary_depth_review` enabled and unchanged.
- Lower spray/foam material emission and alpha.
- Reduce streak emission/width and contact foam emission.
- Keep simulation, cache schema, renderer driver logic, and default `ctest` behavior unchanged.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s96_secondary_depth_review_metric\converted\sequence.json build\s97_secondary_volume_depth_material_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_secondary_volume_depth_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_secondary_volume_depth_tuned --out build\shots\s97_secondary_volume_depth_material_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s97.md --compare-review-manifest build\shots\s96_secondary_depth_review_metric\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S97 generated:

- `build/shots/s97_secondary_volume_depth_material_tuning/shot.gif`
- `build/shots/s97_secondary_volume_depth_material_tuning/review/contact_sheet.png`
- `build/shots/s97_secondary_volume_depth_material_tuning/review/secondary_depth_sheet.png`
- `docs/reports/cinematic_gate_s97.md`

The final gate preserves visual QA, temporal highlight QA, secondary framing QA, focus review QA, ripple readability QA, and secondary depth review QA. Visual bright ratio mean is `0.00456`, down from S96's `0.00774`, while the secondary depth review still reports mean crop particles `172.75`, mean depth span `10.24169`, and mean normalized depth span `0.39490`.

## Next

S98 should add a secondary depth comparison sheet so S96/S97/S98 contact-volume diagnostic changes can be inspected side by side.
