# Interface-Conditioned Secondary Spray

## Goal

Make physical sparse secondary emission depend on measured interface diagnostics instead of only particle height and velocity heuristics.

## Approach

- Add an opt-in interface gate to `SecondarySprayEmissionConfig3D`.
- Feed `SparseSim3DTP::interface_diagnostics_last` into the sim-side secondary spray emission step.
- Require minimum interface cells, gradient, and curvature diagnostics before emission is accepted.
- Record gate pass/fail, effective requested particles, interface cells, gradient max, and curvature max.
- Parse exporter metrics in `tools/run_cinematic_shot.py` and fail physical-secondary shots if the interface gate fails.
- Keep the render-cache channel and volume acceptance checks from S57.

## Validation

```powershell
cmake --build build --config Debug --target unit_tests
build\Debug\unit_tests.exe --test-case="sparse 3D secondary spray emission*"
build\Debug\unit_tests.exe --test-case="sparse 3D two-phase interface diagnostics*"
python -m py_compile tools\run_cinematic_shot.py
cmake --build build --config Release --target export_render_cache3d
build\Release\export_render_cache3d.exe --kind sparse --scene falling-water --nx 16 --ny 20 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s58_interface_secondary_probe\render_cache --manifest build\s58_interface_secondary_probe\manifest.json --secondary-physical-particles 32
python tools\validate_render_cache.py build\s58_interface_secondary_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s58_interface_secondary_gate --nx 24 --ny 30 --nz 20 --frames 30 --sim-steps 30 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s58.md --no-build --timeout-seconds 1200
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S58 generated a 30-frame 1280x720 Blender gate at `build/shots/s58_interface_secondary_gate`. The report records `secondary_spray_interface_gate=True`, `secondary_spray_interface_gate_passed_last=True`, `effective_requested=96`, `interface_cells=784`, `grad_max=0.5095651925135785`, and `curvature_abs_max=1.2725215746745409`.

## Next

S59 should improve the falling-water scene complexity and surface detail so the shot reads as a larger water event instead of a compact falling block.
