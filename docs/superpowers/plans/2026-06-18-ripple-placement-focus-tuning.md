# Ripple Placement Focus Tuning

## Goal

Use the S89 contact-focused camera to make impact ripple arcs slightly wider and stronger while keeping the cinematic gates stable.

## Scope

- Add `dam_break_ripple_placement_focus_tuned` as an inherited S89 preset.
- Keep the S89 camera and focus crop.
- Increase ripple spray weighting from `0.18` to `0.22`.
- Increase ripple arc fraction, radius, radius step, width, alpha, and emission strength.
- Keep the ripple candidate count bounded at `72` per frame.
- Run an 8-frame probe before the full 36-frame gate.
- Compare the S90 focus sheet against S89.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s89_contact_focus_camera_tuning\converted\sequence.json build\s90_ripple_placement_focus_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_ripple_placement_focus_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_ripple_placement_focus_tuned --out build\shots\s90_ripple_placement_focus_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s90.md --compare-review-manifest build\shots\s89_contact_focus_camera_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S90 generated:

- `build/shots/s90_ripple_placement_focus_tuning/shot.gif`
- `build/shots/s90_ripple_placement_focus_tuning/review/contact_sheet.png`
- `build/shots/s90_ripple_placement_focus_tuning/review/focus_sheet.png`
- `build/shots/s90_ripple_placement_focus_tuning/review/focus_comparison_sheet.png`
- `docs/reports/cinematic_gate_s90.md`

The final gate keeps `72` ripple candidates per frame. Focus review QA, full-frame visual QA, temporal highlight QA, camera stability, and secondary framing QA pass.

## Next

S91 should add ripple/contact readability diagnostics so subtle focus-region changes are easier to inspect.
