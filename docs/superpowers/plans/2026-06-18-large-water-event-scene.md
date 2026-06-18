# Large Water-Event Scene

## Goal

Replace the compact falling-water block with a larger visual setup that reads as a water event: a wide falling sheet descending toward a shallow impact pool.

## Approach

- Add `SparseSim3DTP::initLargeWaterEvent()`.
- Seed the scene as gas everywhere except:
  - a wide elevated liquid sheet with downward and mild outward velocity
  - a shallow lower liquid pool for early contact/readability
- Add exporter scene aliases: `large-water-event`, `water-event`, and `wide-falling-water`.
- Switch `dam_break_cinematic` to `large-water-event`.
- Increase camera auto-frame max scale so the 28x34x22 gate stays framed.

## Validation

```powershell
cmake --build build --config Debug --target unit_tests
build\Debug\unit_tests.exe --test-case="sparse 3D large water event*"
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py
cmake --build build --config Release --target export_render_cache3d
build\Release\export_render_cache3d.exe --kind sparse --scene large-water-event --nx 16 --ny 22 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s59_large_water_event_probe\render_cache --manifest build\s59_large_water_event_probe\manifest.json --secondary-physical-particles 32
python tools\validate_render_cache.py build\s59_large_water_event_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s59_large_water_event --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s59.md --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S59 generated `build/shots/s59_large_water_event/shot.gif` and `review/contact_sheet.png`. The report records `scene=large-water-event`, `particles=133120`, primary liquid particles `24720`, interface cells `3312`, and camera frame scale `1.75`.

## Next

S60 should increase contact-driven splash breakup and spray visibility for the large water-event scene.
