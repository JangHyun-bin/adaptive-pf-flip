# Water Surface Impact Ripple Cues

## Goal

Add localized impact-region ripple and surface-breakup cues tied to active foam/spray particles so the splash contact area reads as disturbed water, not only as floating secondary particles.

## Scope

- Add preset-driven `water_impact_ripple_pass` support to the Blender bridge.
- Count foam/spray ripple candidates in the scene spec and bridge summary.
- Render thin partial ring arcs near selected foam/spray secondary particles.
- Add `water_ripple` material controls with alpha and emission scaling.
- Add `dam_break_water_impact_ripple_cues` as an inherited S83 preset.
- Report ripple pass settings and counts in the cinematic shot report.
- Run a probe render and full 36-frame Blender gate against S83.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s83_water_highlight_motion_tuning\converted\sequence.json build\s84_water_impact_ripple_probe_render --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_impact_ripple_cues --preset-config configs\cinematic_presets.json --timeout-seconds 600
python tools\run_cinematic_shot.py --preset dam_break_water_impact_ripple_cues --out build\shots\s84_water_surface_impact_ripple_cues --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s84.md --compare-review-manifest build\shots\s83_water_highlight_motion_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S84 generated:

- `build/shots/s84_water_surface_impact_ripple_cues/shot.gif`
- `build/shots/s84_water_surface_impact_ripple_cues/review/contact_sheet.png`
- `build/shots/s84_water_surface_impact_ripple_cues/review/temporal_diff_sheet.png`
- `docs/reports/cinematic_gate_s84.md`

The final gate renders `96` foam/spray-driven ripple candidates per frame. Visual QA, temporal highlight QA, camera stability, and active-secondary framing QA pass.

## Next

S85 should tune ripple density and material strength against contact-area readability, foam/spray visibility, and temporal highlight QA.
