# Water Impact Ripple Tuning

## Goal

Tune S84 impact ripple density and material strength so the splash contact region reads as disturbed water without overpowering foam, spray, and water highlights.

## Scope

- Add `dam_break_water_impact_ripple_tuned` as an inherited S84 preset.
- Reduce ripple candidate density from `96` to `72` per frame.
- Lower spray weighting, arc size, arc width, alpha, and emission strength.
- Keep temporal highlight QA and temporal diff review enabled.
- Run a probe render and full 36-frame Blender gate against S84.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s84_water_surface_impact_ripple_cues\converted\sequence.json build\s85_water_impact_ripple_tuning_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_impact_ripple_tuned --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_impact_ripple_tuned --out build\shots\s85_water_impact_ripple_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s85.md --compare-review-manifest build\shots\s84_water_surface_impact_ripple_cues\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S85 generated:

- `build/shots/s85_water_impact_ripple_tuning/shot.gif`
- `build/shots/s85_water_impact_ripple_tuning/review/contact_sheet.png`
- `build/shots/s85_water_impact_ripple_tuning/review/comparison_sheet.png`
- `build/shots/s85_water_impact_ripple_tuning/review/temporal_diff_sheet.png`
- `docs/reports/cinematic_gate_s85.md`

The final gate renders `72` foam/spray-driven ripple candidates per frame. Visual QA, temporal highlight QA, camera stability, and active-secondary framing QA pass.

## Next

S86 should add soft material falloff to impact ripple arcs so the breakup blends into the water surface.
