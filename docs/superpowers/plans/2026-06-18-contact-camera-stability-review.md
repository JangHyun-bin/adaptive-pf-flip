# Contact Camera Stability Review

## Goal

Make close-up cinematic gates more reviewable by measuring camera path stability and emitting a side-by-side wide/close comparison sheet.

## Scope

- Add Blender bridge camera path metrics to `bridge_summary.json`.
- Gate close-up presets with minimum camera height, minimum camera-to-target distance, and maximum FOV.
- Add `--compare-review-manifest` to `run_cinematic_shot.py`.
- Generate `review/comparison_sheet.png` and `review/comparison_manifest.json` from a previous wide gate plus the current close gate.
- Stabilize `dam_break_contact_closeup` by moving the path slightly farther from the water body.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s63_contact_closeup\converted\sequence.json build\s64_contact_camera_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s64_contact_camera_stability --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s64.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S64 generated:

- `build/shots/s64_contact_camera_stability/shot.gif`
- `build/shots/s64_contact_camera_stability/review/contact_sheet.png`
- `build/shots/s64_contact_camera_stability/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s64.md`

The camera stability gate passed and the comparison sheet shows the S62 wide gate beside the stabilized S64 contact close-up.

## Next

S65 should add screen-space visual QA metrics. The renderer already checks nonblank frames, but the shot summary should also expose coverage, contrast ranges, and visual-readability proxy gates for water and secondary particles.
