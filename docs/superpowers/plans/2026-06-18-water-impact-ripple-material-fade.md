# Water Impact Ripple Material Fade

## Goal

Add a softer material edge to the S85 impact ripple arcs so contact-region breakup blends into the water surface instead of reading as hard overlay lines.

## Scope

- Add `dam_break_water_impact_ripple_fade` as an inherited S85 preset.
- Carry `material_falloff` through the impact ripple pass summary and render values.
- Add UV coordinates to generated impact ripple arc meshes.
- Add an edge-falloff material that fades arc alpha across ripple width.
- Preserve existing public cinematic runner behavior and temporal review artifacts.
- Run a probe render and full 36-frame Blender gate against S85.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s85_water_impact_ripple_tuning\converted\sequence.json build\s86_water_impact_ripple_fade_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_impact_ripple_fade --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_impact_ripple_fade --out build\shots\s86_water_impact_ripple_material_fade --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s86.md --compare-review-manifest build\shots\s85_water_impact_ripple_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S86 generated:

- `build/shots/s86_water_impact_ripple_material_fade/shot.gif`
- `build/shots/s86_water_impact_ripple_material_fade/review/contact_sheet.png`
- `build/shots/s86_water_impact_ripple_material_fade/review/comparison_sheet.png`
- `build/shots/s86_water_impact_ripple_material_fade/review/temporal_diff_sheet.png`
- `docs/reports/cinematic_gate_s86.md`

The final gate renders `72` ripple candidates per frame with `material_falloff='edge_shader'`. Visual QA, temporal highlight QA, camera stability, and active-secondary framing QA pass.

## Next

S87 should add a focused contact-region review gate so impact ripple readability can be judged without hiding secondary spray/foam or breaking temporal highlight QA.
