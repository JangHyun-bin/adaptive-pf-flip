# Contact Splash Secondary Visibility

## Goal

Make the large water-event gate show earlier pool contact and more visible physically conditioned spray.

## Approach

- Lower the large falling sheet and increase downward/outward initial velocity.
- Add opt-in downward-impact candidate selection to sim-side secondary spray emission.
- Record `secondary_spray_impact_candidates_last` in sim stats and exporter stdout.
- Parse impact candidate metrics in the shot runner and fail physical-secondary gates if impact candidates are zero.
- Increase `dam_break_cinematic` physical secondary count from 96 to 192 and secondary radius scale from 2.4 to 3.0.

## Validation

```powershell
cmake --build build --config Debug --target unit_tests
build\Debug\unit_tests.exe --test-case="sparse 3D secondary spray emission includes impact candidates"
build\Debug\unit_tests.exe --test-case="sparse 3D large water event*"
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py
cmake --build build --config Release --target export_render_cache3d
build\Release\export_render_cache3d.exe --kind sparse --scene large-water-event --nx 16 --ny 22 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s60_contact_splash_probe\render_cache --manifest build\s60_contact_splash_probe\manifest.json --secondary-physical-particles 64
python tools\validate_render_cache.py build\s60_contact_splash_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s60_contact_splash --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s60.md --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S60 generated `build/shots/s60_contact_splash/shot.gif` and `review/contact_sheet.png`. The report records `secondary_physical_particles=192`, `spray=173 bubble=19 total=192`, `impact_candidates=17646`, and `secondary_radius_scale=3.0`.

## Next

S61 should add contact foam/spray channel emphasis and more surface detail to reduce the smooth slab look.
