# Active Secondary Framing QA

## Goal

Make secondary spray/foam visibility measurable so camera and material changes cannot silently lose the active spray band.

## Scope

- Project spray and foam secondary particles into the active camera.
- Report inside-frame ratio and screen-y band placement.
- Add preset thresholds for mean/min inside ratio and vertical placement.
- Fail the shot runner when enabled framing QA does not pass.
- Preserve the S74 impact-framing preset and visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s74_impact_framing\converted\sequence.json build\s75_active_secondary_framing_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_impact_framing --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_impact_framing --out build\shots\s75_active_secondary_framing_qa --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s75.md --compare-review-manifest build\shots\s74_impact_framing\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S75 generated:

- `build/shots/s75_active_secondary_framing_qa/shot.gif`
- `build/shots/s75_active_secondary_framing_qa/review/contact_sheet.png`
- `build/shots/s75_active_secondary_framing_qa/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s75.md`

The active secondary framing gate passed with all spray/foam particles projected inside the frame and a stable vertical band.

## Next

S76 should add a surface/contact foam pass so the visible secondary band connects back to the water body.
