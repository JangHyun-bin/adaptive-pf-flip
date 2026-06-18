# Contact Camera Close-up Gate

## Goal

Make the large water-event contact region easier to inspect than the wide S62 shot by adding a close camera preset and recording a full visual gate.

## Scope

- Add a `dam_break_contact_closeup` cinematic preset.
- Reuse the S62 physical secondary, foam, surface detail, and channel radius settings.
- Keep the simulation scene as `large-water-event`.
- Use a tighter camera path aimed at the contact region.
- Record a 36-frame 1280x720 Blender gate and checked-in report.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python tools\render_bridge_blender.py build\s61_foam_surface_probe\converted\sequence.json build\s63_contact_closeup_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s63_contact_closeup --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s63.md --no-build --timeout-seconds 1500
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S63 added `dam_break_contact_closeup` and generated:

- `build/shots/s63_contact_closeup/shot.gif`
- `build/shots/s63_contact_closeup/review/contact_sheet.png`
- `docs/reports/cinematic_gate_s63.md`

The gate passed with 36 cache/render frames, 192 physical secondary particles, foam count above the acceptance threshold, surface detail enabled, and a much larger close-up GIF than S62.

## Next

S64 should add camera stability checks and a wide/close review comparison. S63 proves the close-up inspection value, but late frames can get too close to the water body for a presentation-grade shot.
