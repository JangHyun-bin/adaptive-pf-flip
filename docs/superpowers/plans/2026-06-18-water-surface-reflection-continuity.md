# Water Surface Reflection Continuity

## Goal

Add a broader, camera-stable reflection layer over S79 glints so the main water body reads less like a flat slab during the moving-camera shot.

## Scope

- Add a preset-driven `water_reflection_pass` to the Blender bridge scene spec.
- Reuse the water-surface strip mesh path for longer reflection ribbons.
- Add `water_reflection` material controls with alpha and emission scaling.
- Add `dam_break_water_reflection_continuity` as an inherited S79 preset.
- Report the reflection pass in the bridge summary and cinematic shot report.
- Run a probe render and full 36-frame Blender gate against S79.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s79_water_surface_glint_flow\converted\sequence.json build\s80_water_reflection_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_reflection_continuity --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_reflection_continuity --out build\shots\s80_water_reflection_continuity --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s80.md --compare-review-manifest build\shots\s79_water_surface_glint_flow\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S80 generated:

- `build/shots/s80_water_reflection_continuity/shot.gif`
- `build/shots/s80_water_reflection_continuity/review/contact_sheet.png`
- `build/shots/s80_water_reflection_continuity/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s80.md`

The final gate renders `24` longer water reflection ribbons over the S79 glint layer. Visual QA, camera stability, and active-secondary framing QA pass.

## Next

S81 should add a temporal highlight review or shimmer gate so water highlights can be checked for flicker and static banding across the camera move.
