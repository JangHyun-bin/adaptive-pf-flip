# High-Detail Cinematic Surface Gate

## Goal

Exercise the S53 implicit tetra reconstruction path with a denser falling-water cache and a larger rendered frame.

## Gate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s54_high_detail_surface --nx 20 --ny 24 --nz 17 --frames 24 --sim-steps 24 --width 960 --height 540 --renderer blender --samples 10 --review-frames 6 --report docs\reports\cinematic_gate_s54.md --no-build --timeout-seconds 900
```

## Evidence

- `shot_summary.json` status is `ok`.
- `water_reconstruction.json` reports `surface_mode: tetra`.
- First S54 mesh: 1798 vertices, 3592 faces, 1798 normals.
- `review/contact_sheet.png` shows a closer high-detail surface gate.
- The report records the remaining framing limitation from using fixed camera presets on larger grid overrides.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S55 should add grid-aware camera framing for high-detail gates, then begin replacing demo secondary seeding with physical spray generation.
