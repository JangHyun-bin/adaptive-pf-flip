# Water Surface Glint Flow

## Goal

Add subtle directional highlights to the main water surface so the cinematic shot is not carried only by spray, foam, and contact patches.

## Scope

- Add a preset-driven `water_surface_glint_pass` to the Blender bridge scene spec.
- Render deterministic thin glint quads over a configured water-surface region.
- Add a `water_glint` material and inherited `dam_break_water_glint_flow` preset.
- Report the glint pass in the bridge summary and cinematic shot report.
- Run a probe render and full 36-frame Blender gate against S78.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s78_contact_foam_material_fade\converted\sequence.json build\s79_water_glint_flow_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_glint_flow --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_glint_flow --out build\shots\s79_water_surface_glint_flow --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s79.md --compare-review-manifest build\shots\s78_contact_foam_material_fade\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S79 generated:

- `build/shots/s79_water_surface_glint_flow/shot.gif`
- `build/shots/s79_water_surface_glint_flow/review/contact_sheet.png`
- `build/shots/s79_water_surface_glint_flow/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s79.md`

The final gate renders `44` deterministic water-surface glint strokes per frame. Visual QA, camera stability, and active-secondary framing QA pass.

## Next

S80 should add reflection-continuity cues so the water body reads less like a flat slab as the camera moves.
