# Contact Foam Ripple Integration

## Goal

Tune contact foam and impact ripple styling so the contact-region surface breakup reads less like separate overlay layers.

## Scope

- Add `dam_break_contact_foam_ripple_integrated` as an inherited S92 preset.
- Keep ripple diagnostics and diagnostic comparison artifacts enabled.
- Reduce surface contact foam width and brightness.
- Keep impact ripple strength close to S90.
- Run an 8-frame probe before the full 36-frame gate.
- Compare S93 against S92 via full-frame, focus, and ripple diagnostic sheets.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s92_ripple_diagnostic_comparison\converted\sequence.json build\s93_contact_foam_ripple_integration_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_contact_foam_ripple_integrated --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_contact_foam_ripple_integrated --out build\shots\s93_contact_foam_ripple_integration --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s93.md --compare-review-manifest build\shots\s92_ripple_diagnostic_comparison\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S93 generated:

- `build/shots/s93_contact_foam_ripple_integration/shot.gif`
- `build/shots/s93_contact_foam_ripple_integration/review/contact_sheet.png`
- `build/shots/s93_contact_foam_ripple_integration/review/focus_sheet.png`
- `build/shots/s93_contact_foam_ripple_integration/review/ripple_readability_sheet.png`
- `build/shots/s93_contact_foam_ripple_integration/review/ripple_readability_comparison_sheet.png`
- `docs/reports/cinematic_gate_s93.md`

The final gate passes ripple readability QA, focus review QA, full-frame visual QA, temporal highlight QA, camera stability, and secondary framing QA.

## Next

S94 should tune water surface breakup/detail in the contact region while preserving diagnostic and temporal gates.
