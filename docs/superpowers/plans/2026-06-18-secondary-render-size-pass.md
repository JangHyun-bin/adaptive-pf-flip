# Secondary Render Size Pass

## Goal

Make foam and spray more legible in the large water-event shot without changing the physical secondary counts.

## Approach

- Add channel-specific secondary radius scales to the Blender bridge.
- Keep global `secondary_radius_scale` as the base, then multiply by per-channel values.
- Add optional material emission controls for spray/foam particles.
- Record channel radius scales in `bridge_summary.json` and the shot report.
- Keep S61 foam acceptance checks active.

## Validation

```powershell
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json > $null
python tools\render_bridge_blender.py build\s61_foam_surface_probe\converted\sequence.json build\s62_secondary_size_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_cinematic --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s62_secondary_size_pass --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s62.md --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S62 generated `build/shots/s62_secondary_size_pass/shot.gif` and `review/contact_sheet.png`. The report records channel radius scales `spray=1.35`, `foam=1.85`, `bubble=1.15`, with foam counts still above gate thresholds.

## Next

S63 should add a closer contact-camera preset or crop gate so the foam/spray and surface breakup are easier to inspect.
