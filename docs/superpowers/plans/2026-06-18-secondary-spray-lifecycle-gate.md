# Secondary Spray Lifecycle Gate

## Goal

Promote physical cinematic secondary emission from a render-facing cache seed into the sparse 3D two-phase simulation step.

## Approach

- Add sim-side secondary spray emission controls to `SparseSim3DTP`.
- Select deterministic liquid-particle candidates from the current primary particle state.
- Emit droplets and bubbles into the existing secondary particle containers.
- Reuse the existing secondary lifecycle, age arrays, and volume accounting.
- Record emission counts, candidate counts, emitted volumes, and current secondary volumes.
- Keep the older exporter-local physical seed path only as a multires fallback for this milestone.

## Acceptance Gate

- Unit coverage proves one sparse sim step emits deterministic droplet/bubble counts.
- Emitted secondary volume equals current plus removed lifecycle volume.
- Cache export with `--secondary-physical-particles` reports sim-side totals.
- The cinematic shot report records secondary channel counts, secondary volume, and an acceptance minimum.

## Validation

```powershell
cmake --build build --config Release --target export_render_cache3d
cmake --build build --config Debug --target unit_tests
python -m py_compile tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json > $null
build\Debug\unit_tests.exe --test-case="sparse 3D secondary spray emission*"
build\Debug\unit_tests.exe --test-case="3D secondary*"
build\Release\export_render_cache3d.exe --kind sparse --scene falling-water --nx 16 --ny 20 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s57_sim_side_secondary_probe\render_cache --manifest build\s57_sim_side_secondary_probe\manifest.json --secondary-physical-particles 32
python tools\validate_render_cache.py build\s57_sim_side_secondary_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s57_secondary_lifecycle_gate --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs\reports\cinematic_gate_s57.md --no-build --timeout-seconds 900
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S57 keeps demo secondary particles disabled and records `secondary_physical_particles=96` in the cinematic preset. The Blender gate reports `spray=86 bubble=10 total=96` on the first and last frames, with stable secondary cache volume `droplet=47.3 bubble=4.5 total=51.8`.

## Next

S58 should couple physical spray emission thresholds to interface/curvature diagnostics and run a larger visual acceptance gate.
