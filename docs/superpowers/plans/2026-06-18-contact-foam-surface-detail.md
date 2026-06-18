# Contact Foam Surface Detail

## Goal

Make the S60 contact/splash gate split impact secondary particles into visible spray and foam channels, and reduce the smooth slab look with a small render-side surface detail pass.

## Approach

- Track impact secondary candidates through `SecondarySprayCandidate3D`.
- Convert a configurable fraction of impact droplets into foam-ready particles by assigning low surface velocity and older age.
- Export `secondary_spray_foam_ready_droplets_last` for acceptance gates and reports.
- Require nonzero foam channel counts in physical-secondary cinematic shots.
- Add preset-driven Blender water surface detail displacement and report it through `bridge_summary.json`.

## Validation

```powershell
cmake --build build --config Debug --target unit_tests
build\Debug\unit_tests.exe --test-case="sparse 3D secondary spray emission includes impact candidates"
build\Debug\unit_tests.exe --test-case="sparse 3D render cache writes schema sections"
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python -m json.tool configs\cinematic_presets.json > $null
cmake --build build --config Release --target export_render_cache3d
build\Release\export_render_cache3d.exe --kind sparse --scene large-water-event --nx 16 --ny 22 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s61_foam_surface_probe\render_cache --manifest build\s61_foam_surface_probe\manifest.json --secondary-physical-particles 64
python tools\validate_render_cache.py build\s61_foam_surface_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s61_contact_foam_surface --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s61.md --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S61 generated `build/shots/s61_contact_foam_surface/shot.gif` and `review/contact_sheet.png`. The report records `foam=58` on the first frame, `foam=54` on the last frame, `foam_ready=54`, and water surface detail enabled with `strength=0.045`, `scale=2.8`, `depth=4`.

## Next

S62 should make foam/spray visually stronger on screen, likely with larger channel-specific render sizing or a closer contact camera pass.
