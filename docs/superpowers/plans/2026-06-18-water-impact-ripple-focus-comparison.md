# Water Impact Ripple Focus Comparison

## Goal

Add a side-by-side focus comparison artifact so contact-region crop sheets from nearby cinematic gates can be compared without replacing the full-frame contact sheet.

## Scope

- Load `focus_sheet` and `focus_review_manifest` from `lsfs_cinematic_review_pack` manifests when present.
- Generate `review/focus_comparison_sheet.png` from prior and current focus sheets.
- Generate `review/focus_comparison_manifest.json` with source manifests and focus artifacts.
- Preserve the existing full-frame comparison sheet path.
- Run a full 36-frame gate against S87 to prove comparison artifacts are written.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_water_impact_ripple_focus_qa --out build\shots\s88_water_impact_ripple_focus_comparison --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s88.md --compare-review-manifest build\shots\s87_water_impact_ripple_focus_qa\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S88 generated:

- `build/shots/s88_water_impact_ripple_focus_comparison/shot.gif`
- `build/shots/s88_water_impact_ripple_focus_comparison/review/contact_sheet.png`
- `build/shots/s88_water_impact_ripple_focus_comparison/review/comparison_sheet.png`
- `build/shots/s88_water_impact_ripple_focus_comparison/review/focus_sheet.png`
- `build/shots/s88_water_impact_ripple_focus_comparison/review/focus_comparison_sheet.png`
- `build/shots/s88_water_impact_ripple_focus_comparison/review/focus_comparison_manifest.json`
- `docs/reports/cinematic_gate_s88.md`

The final gate compares `2` focus sources. Focus review QA, full-frame visual QA, temporal highlight QA, camera stability, and secondary framing QA pass.

## Next

S89 should use the focus-comparison evidence to tune contact camera framing or impact ripple placement.
