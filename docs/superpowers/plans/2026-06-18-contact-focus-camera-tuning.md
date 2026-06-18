# Contact Focus Camera Tuning

## Goal

Use the S88 focus-comparison evidence to narrow the contact camera and focus crop while preserving full-frame readability, secondary framing, and temporal highlight stability.

## Scope

- Add `dam_break_contact_focus_camera_tuned` as an inherited S88 preset.
- Narrow the camera FOV path from `40-44` degrees to `38-42` degrees.
- Adjust camera targets to keep the contact/ripple band denser while leaving secondary spray/foam inside frame.
- Adjust focus crop to `[0.02, 0.3, 0.98, 0.88]`.
- Run a probe render before the full 36-frame gate.
- Compare the S89 focus sheet against S88.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s88_water_impact_ripple_focus_comparison\converted\sequence.json build\s89_contact_focus_camera_probe_render_v2 --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_contact_focus_camera_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_contact_focus_camera_tuned --out build\shots\s89_contact_focus_camera_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s89.md --compare-review-manifest build\shots\s88_water_impact_ripple_focus_comparison\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S89 generated:

- `build/shots/s89_contact_focus_camera_tuning/shot.gif`
- `build/shots/s89_contact_focus_camera_tuning/review/contact_sheet.png`
- `build/shots/s89_contact_focus_camera_tuning/review/focus_sheet.png`
- `build/shots/s89_contact_focus_camera_tuning/review/focus_comparison_sheet.png`
- `docs/reports/cinematic_gate_s89.md`

The final gate passes camera stability, secondary framing, focus review, visual QA, and temporal highlight QA. The focus comparison source count is `2`.

## Next

S90 should tune impact ripple placement or strength using focus-comparison evidence.
