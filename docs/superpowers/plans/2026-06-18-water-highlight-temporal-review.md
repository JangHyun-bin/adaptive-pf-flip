# Water Highlight Temporal Review

## Goal

Add a scalar temporal QA gate for water glint/reflection layers so excessive flicker, frozen frames, or unstable highlight masks are caught before adding more cinematic material passes.

## Scope

- Add temporal highlight summary metrics to `tools/run_cinematic_shot.py`.
- Measure frame-to-frame grayscale deltas and highlight-mask change ratios from rendered PNG frames.
- Add a preset-driven `temporal_highlight_qa` gate.
- Add `dam_break_water_highlight_temporal_review` as an inherited S80 preset.
- Report temporal highlight summary and gate results in the cinematic shot report and review manifest metrics.
- Run a full 36-frame Blender gate against S80.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_water_highlight_temporal_review --out build\shots\s81_water_highlight_temporal_review --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s81.md --compare-review-manifest build\shots\s80_water_reflection_continuity\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S81 generated:

- `build/shots/s81_water_highlight_temporal_review/shot.gif`
- `build/shots/s81_water_highlight_temporal_review/review/contact_sheet.png`
- `build/shots/s81_water_highlight_temporal_review/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s81.md`

The final gate passes with `35` temporal frame pairs, mean frame delta `3.6414`, max frame delta `11.0089`, and max highlight-mask change ratio `0.002274`.

## Next

S82 should add a temporal difference review sheet so highlight motion can be inspected visually, not only through scalar metrics.
