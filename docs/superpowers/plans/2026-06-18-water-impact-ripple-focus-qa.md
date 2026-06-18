# Water Impact Ripple Focus QA

## Goal

Add a focused contact-region review artifact and gate so the S86 impact ripple fade can be judged in the area where the water surface, contact foam, and spray overlap.

## Scope

- Add a `focus_review` renderer config section to the cinematic runner.
- Generate `review/focus_sheet.png` from cropped keyframes.
- Generate `review/focus_review_manifest.json` with crop stats.
- Evaluate focus frame count, nonblank ratio, contrast, mean luminance, and bright-pixel ratio.
- Add `dam_break_water_impact_ripple_focus_qa` as an inherited S86 preset.
- Preserve existing full-frame contact sheet, comparison sheet, temporal diff sheet, and QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_water_impact_ripple_focus_qa --out build\shots\s87_water_impact_ripple_focus_qa --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s87.md --compare-review-manifest build\shots\s86_water_impact_ripple_material_fade\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S87 generated:

- `build/shots/s87_water_impact_ripple_focus_qa/shot.gif`
- `build/shots/s87_water_impact_ripple_focus_qa/review/contact_sheet.png`
- `build/shots/s87_water_impact_ripple_focus_qa/review/focus_sheet.png`
- `build/shots/s87_water_impact_ripple_focus_qa/review/focus_review_manifest.json`
- `build/shots/s87_water_impact_ripple_focus_qa/review/temporal_diff_sheet.png`
- `docs/reports/cinematic_gate_s87.md`

The final gate samples `8` focus crops and passes the focus review gate with min contrast `79.0`, mean luminance `92.4947`, and mean bright ratio `0.000648889`.

## Next

S88 should add focus-comparison artifacts so contact-region crops can be compared across nearby milestones without replacing the full-frame contact sheet.
