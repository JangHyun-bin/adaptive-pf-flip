# Surface Foam Contact Pass

## Goal

Connect the visible secondary foam band back to the water body with a surface-level foam render pass.

## Scope

- Add `surface_contact_foam_pass` renderer preset controls.
- Estimate and report per-frame contact foam patch counts.
- Render flattened foam patches from foam secondary particles below the secondary band.
- Preserve the existing primary secondary particles, mist billboards, velocity streaks, and active-secondary framing QA.
- Run a full 36-frame Blender gate against S75.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s75_active_secondary_framing_qa\converted\sequence.json build\s76_surface_foam_contact_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_impact_framing --preset-config configs\cinematic_presets.json
python tools\render_bridge_blender.py build\shots\s76_surface_foam_contact\converted\sequence.json build\s76_surface_foam_contact_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_impact_framing --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_impact_framing --out build\shots\s76_surface_foam_contact --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s76.md --compare-review-manifest build\shots\s75_active_secondary_framing_qa\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S76 generated:

- `build/shots/s76_surface_foam_contact/shot.gif`
- `build/shots/s76_surface_foam_contact/review/contact_sheet.png`
- `build/shots/s76_surface_foam_contact/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s76.md`

The final gate renders `54-58` surface contact foam patches per frame. Visual QA and active-secondary framing QA both pass.

## Next

S77 should make contact foam read as moving with the impact flow rather than only static horizontal patches.
