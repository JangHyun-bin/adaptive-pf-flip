# Secondary Depth Review Metric

## Goal

Add a dedicated contact-volume depth/layering diagnostic so spray and foam tuning is gated by projected secondary particle depth, not only full-frame brightness and framing checks.

## Scope

- Add `secondary_depth_review` support to `tools/run_cinematic_shot.py`.
- Use the Blender scene spec, camera, and secondary particle CSVs to project spray/foam particles into the rendered contact crop.
- Generate `secondary_depth_sheet.png` and `secondary_depth_manifest.json`.
- Report crop particle counts, crop ratio, depth span, normalized depth span, and spray/foam channel depth delta.
- Add `dam_break_secondary_depth_reviewed` as an inherited S95 preset that enables the new diagnostic gate.
- Preserve existing S95 render tuning and default `ctest` behavior.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_secondary_depth_reviewed --out build\shots\s96_secondary_depth_review_metric --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s96.md --compare-review-manifest build\shots\s95_spray_foam_depth_layering\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S96 generated:

- `build/shots/s96_secondary_depth_review_metric/shot.gif`
- `build/shots/s96_secondary_depth_review_metric/review/secondary_depth_sheet.png`
- `build/shots/s96_secondary_depth_review_metric/review/secondary_depth_manifest.json`
- `docs/reports/cinematic_gate_s96.md`

The new gate passes alongside visual QA, temporal highlight QA, camera stability, secondary framing QA, focus review QA, and ripple readability QA. The depth review reports active frame count `8`, mean crop particles `172.75`, mean crop ratio `0.99855`, mean depth span `10.24169`, and mean normalized depth span `0.39490`.

## Next

S97 should use the secondary depth diagnostic to tune a stronger volume-depth material/readability pass without breaking visual, temporal, or depth-review gates.
