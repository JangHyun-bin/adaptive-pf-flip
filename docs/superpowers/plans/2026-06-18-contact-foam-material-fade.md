# Contact Foam Material Fade

## Goal

Soften flow-aligned contact foam so it fades into the water surface instead of reading as separate bright marks.

## Scope

- Add UV coordinates to surface contact foam meshes.
- Add `material_falloff` support to `surface_contact_foam_pass`.
- Add `dam_break_contact_foam_fade` as an inherited render preset.
- Use the existing radial shader alpha falloff path for contact foam.
- Run a probe render and full 36-frame Blender gate against S77.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s77_contact_foam_flow_lines\converted\sequence.json build\s78_contact_foam_fade_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_contact_foam_fade --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_contact_foam_fade --out build\shots\s78_contact_foam_material_fade --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s78.md --compare-review-manifest build\shots\s77_contact_foam_flow_lines\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S78 generated:

- `build/shots/s78_contact_foam_material_fade/shot.gif`
- `build/shots/s78_contact_foam_material_fade/review/contact_sheet.png`
- `build/shots/s78_contact_foam_material_fade/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s78.md`

The final gate renders `54-58` radial-faded, flow-aligned contact foam strokes per frame. Visual QA and active-secondary framing QA both pass.

## Next

S79 should add water-surface glint or flow cues so the main water body carries more of the cinematic motion.
