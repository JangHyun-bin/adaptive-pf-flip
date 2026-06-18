# Water Highlight Motion Tuning

## Goal

Use the S82 temporal diff sheet and S81 scalar gate to tune water glint/reflection motion so the surface reads more active without introducing highlight flicker.

## Scope

- Add `dam_break_water_highlight_motion_tuned` as an inherited S82 preset.
- Increase short glint count, length, drift, alpha, and emission slightly.
- Increase reflection ribbon length and drift while slightly reducing width/alpha to avoid over-bright banding.
- Keep temporal highlight QA and temporal diff review enabled.
- Run a probe render and full 36-frame Blender gate against S82.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s82_water_highlight_temporal_diff_sheet\converted\sequence.json build\s83_water_highlight_motion_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_highlight_motion_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_highlight_motion_tuned --out build\shots\s83_water_highlight_motion_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s83.md --compare-review-manifest build\shots\s82_water_highlight_temporal_diff_sheet\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S83 generated:

- `build/shots/s83_water_highlight_motion_tuning/shot.gif`
- `build/shots/s83_water_highlight_motion_tuning/review/contact_sheet.png`
- `build/shots/s83_water_highlight_motion_tuning/review/temporal_diff_sheet.png`
- `docs/reports/cinematic_gate_s83.md`

The final gate renders `52` short glints plus `24` reflection ribbons with stronger drift. Temporal highlight QA still passes with max mean delta `11.0277` and max highlight-mask change ratio `0.002274`.

## Next

S84 should add localized impact-region ripple or surface-breakup cues tied to the active splash/foam band.
