# Impact Framing Gate

## Goal

Add an impact-focused cinematic preset that keeps the active spray band in view for more of the shot.

## Scope

- Add preset inheritance via `extends` for cinematic presets.
- Add `dam_break_impact_framing` as a small override of `dam_break_contact_closeup`.
- Raise target y and widen early FOV so secondary spray remains visible longer.
- Preserve inherited renderer, reconstruction, secondary streak, soft-pass, material, and lighting settings.
- Run a full 36-frame Blender visual gate against S73.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s73_secondary_streak_tuning\converted\sequence.json build\s74_impact_framing_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_impact_framing --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_impact_framing --out build\shots\s74_impact_framing --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s74.md --compare-review-manifest build\shots\s73_secondary_streak_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S74 generated:

- `build/shots/s74_impact_framing/shot.gif`
- `build/shots/s74_impact_framing/review/contact_sheet.png`
- `build/shots/s74_impact_framing/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s74.md`

The impact-framing preset improves visible spray-band coverage and passes camera stability plus visual QA. Bright-pixel coverage increased relative to S73.

## Next

S75 should add a numeric active-secondary framing QA metric so future camera and material changes cannot pass while losing the visible spray band.
