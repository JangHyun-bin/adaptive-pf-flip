# Secondary Depth Comparison Sheet

## Goal

Add a side-by-side secondary depth comparison sheet so contact-volume diagnostic changes can be inspected across nearby cinematic gates.

## Scope

- Add `secondary_depth_comparison_sheet.png` and `secondary_depth_comparison_manifest.json` generation to `tools/run_cinematic_shot.py`.
- Load `secondary_depth_sheet` and `secondary_depth_manifest` from prior `review_manifest.json` files.
- Keep the S97 preset `dam_break_secondary_volume_depth_tuned` unchanged.
- Preserve all existing visual, temporal, secondary framing, focus, ripple, and secondary depth gates.
- Do not change simulation, cache schema, renderer driver logic, or default `ctest` behavior.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_secondary_volume_depth_tuned --out build\shots\s98_secondary_depth_comparison_sheet --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s98.md --compare-review-manifest build\shots\s97_secondary_volume_depth_material_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S98 generated:

- `build/shots/s98_secondary_depth_comparison_sheet/shot.gif`
- `build/shots/s98_secondary_depth_comparison_sheet/review/secondary_depth_sheet.png`
- `build/shots/s98_secondary_depth_comparison_sheet/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s98.md`

The comparison source count is `2`, comparing S97 against S98. Visual QA, temporal highlight QA, secondary framing QA, focus review QA, ripple readability QA, and secondary depth review QA all pass.

## Next

S99 should tune stronger water-body volume/depth cues while preserving visual, temporal, ripple, and secondary depth comparison gates.
