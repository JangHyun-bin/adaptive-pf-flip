# Physical Secondary Spray Seed

## Goal

Begin replacing cinematic demo secondary particles with physically conditioned secondary emission.

## Approach

- Add `--secondary-physical-particles` to `export_render_cache3d`.
- Select candidate liquid particles from the actual simulated particle state:
  - near the upper liquid region
  - high upward or lateral motion
  - deterministic frame-index sampling for reproducible cache output
- Emit secondary droplets/bubbles into the existing render-cache secondary particle sections.
- Switch `dam_break_cinematic` from `secondary_demo_particles: 96` to `secondary_physical_particles: 96`.
- Record first/last secondary channel counts in generated shot reports.

## Validation

```powershell
cmake --build build --config Release --target export_render_cache3d
python -m py_compile tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json > $null
build\Release\export_render_cache3d.exe --kind sparse --scene falling-water --nx 16 --ny 20 --nz 14 --steps 4 --every 1 --dt 0.02 --out-prefix build\s56_physical_seed_probe\render_cache --manifest build\s56_physical_seed_probe\manifest.json --secondary-physical-particles 32
python tools\validate_render_cache.py build\s56_physical_seed_probe\manifest.json --require-cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s56_physical_secondary --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs\reports\cinematic_gate_s56.md --no-build --timeout-seconds 900
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S56 reports demo secondary particles at 0 and physical secondary particles at 96. The cache records `spray=86 bubble=10 total=96` on first and last frames.

## Next

S57 should promote secondary spray emission from a render-facing seed into a sim-side lifecycle gate with volume accounting and acceptance thresholds.
