# Spray/Foam Depth Layering

## Goal

Tune the S94 contact-region render so spray and foam sit more naturally inside the contact volume instead of reading as a bright separated overlay layer.

## Scope

- Add `dam_break_spray_foam_depth_layered` as an inherited S94 preset.
- Reduce spray/foam particle radius scales and soft-pass alpha/emission.
- Reduce foam streak intensity and soften spray streak length/width.
- Lower and widen the surface contact foam pass so foam reconnects with the water surface.
- Preserve existing visual QA, temporal highlight QA, secondary framing QA, focus review QA, and ripple readability QA.
- Do not change simulation, cache schema, renderer driver logic, or default `ctest` behavior.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s94_water_surface_breakup_noise_tuning\converted\sequence.json build\s95_spray_foam_depth_layering_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_spray_foam_depth_layered --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_spray_foam_depth_layered --out build\shots\s95_spray_foam_depth_layering --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s95.md --compare-review-manifest build\shots\s94_water_surface_breakup_noise_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S95 generated:

- `build/shots/s95_spray_foam_depth_layering/shot.gif`
- `build/shots/s95_spray_foam_depth_layering/review/contact_sheet.png`
- `build/shots/s95_spray_foam_depth_layering/review/focus_comparison_sheet.png`
- `build/shots/s95_spray_foam_depth_layering/review/ripple_readability_comparison_sheet.png`
- `docs/reports/cinematic_gate_s95.md`

The final gate preserves visual QA, temporal highlight QA, camera stability, secondary framing QA, focus review QA, and ripple readability QA. Compared with S94, mean luminance stays within gate at `98.6785`, bright ratio drops to `0.00774`, and ripple readability comparison source count remains `2`.

## Next

S96 should add a dedicated contact-volume depth/layering diagnostic so future spray/foam tuning is gated by more than full-frame brightness and framing checks.
