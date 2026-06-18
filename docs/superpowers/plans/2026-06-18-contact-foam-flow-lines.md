# Contact Foam Flow Lines

## Goal

Make surface contact foam read as moving with the impact flow instead of only static horizontal patches.

## Scope

- Preserve the S76 surface contact foam pass as the default behavior.
- Add optional `flow_aligned` orientation to surface contact foam geometry.
- Add `dam_break_contact_foam_flow` as an inherited render preset.
- Use velocity direction when available and radial fallback from a scene flow center.
- Run a full 36-frame Blender gate against S76.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s76_surface_foam_contact\converted\sequence.json build\s77_contact_foam_flow_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_contact_foam_flow --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_contact_foam_flow --out build\shots\s77_contact_foam_flow_lines --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s77.md --compare-review-manifest build\shots\s76_surface_foam_contact\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S77 generated:

- `build/shots/s77_contact_foam_flow_lines/shot.gif`
- `build/shots/s77_contact_foam_flow_lines/review/contact_sheet.png`
- `build/shots/s77_contact_foam_flow_lines/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s77.md`

The final gate renders `54-58` flow-aligned surface foam strokes per frame. Visual QA and active-secondary framing QA both pass.

## Next

S78 should soften contact foam integration so flow strokes fade into the water surface instead of reading as separate bright marks.
