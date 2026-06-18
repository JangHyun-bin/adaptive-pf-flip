# Water Highlight Temporal Diff Sheet

## Goal

Add an inspectable temporal difference artifact so water highlight motion can be reviewed visually, not only through scalar S81 temporal metrics.

## Scope

- Add preset-driven `temporal_diff_review` support to `tools/run_cinematic_shot.py`.
- Select evenly spaced adjacent frame pairs from the rendered PNG sequence.
- Emit amplified grayscale frame-difference images and a `temporal_diff_sheet.png`.
- Emit a `temporal_diff_manifest.json` with selected frame pairs.
- Add `dam_break_water_highlight_temporal_diff_sheet` as an inherited S81 preset.
- Report temporal diff artifacts and pair counts in the cinematic shot report.
- Run a full 36-frame Blender gate against S81.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_water_highlight_temporal_diff_sheet --out build\shots\s82_water_highlight_temporal_diff_sheet --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s82.md --compare-review-manifest build\shots\s81_water_highlight_temporal_review\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S82 generated:

- `build/shots/s82_water_highlight_temporal_diff_sheet/shot.gif`
- `build/shots/s82_water_highlight_temporal_diff_sheet/review/contact_sheet.png`
- `build/shots/s82_water_highlight_temporal_diff_sheet/review/temporal_diff_sheet.png`
- `build/shots/s82_water_highlight_temporal_diff_sheet/review/temporal_diff_manifest.json`
- `docs/reports/cinematic_gate_s82.md`

The final gate emits `8` amplified temporal diff pairs while preserving the S81 temporal highlight QA gate.

## Next

S83 should tune or animate water highlight/reflection motion using the temporal diff sheet as visual evidence, keeping highlight-mask change ratios below the S81 gate.
