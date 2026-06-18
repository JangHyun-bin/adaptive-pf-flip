# Cinematic Visual Gate V2

## Goal

Run a larger dynamic cinematic gate through the current sparse 3D two-phase, water reconstruction, Blender bridge, camera-motion, water-material, and review-pack stack.

## Scope

- Use the `dam_break_cinematic` falling-water preset.
- Increase beyond the S51 smoke shot while keeping the run practical on the local machine.
- Produce durable evidence under `build/shots/s52_visual_gate_v2`.
- Check in the generated markdown report, not the heavy PNG/GIF artifacts.

## Gate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s52_visual_gate_v2 --frames 36 --sim-steps 36 --width 960 --height 540 --renderer blender --samples 10 --review-frames 8 --report docs\reports\cinematic_gate_s52.md --no-build --timeout-seconds 600
```

## Expected Evidence

- `shot_summary.json` status is `ok`.
- `shot.gif` exists.
- `review/contact_sheet.png` exists.
- `review/review_manifest.json` reports 8 keyframes.
- `docs/reports/cinematic_gate_s52.md` records timings, artifact paths, material response, and known limitations.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S53 should replace coarse voxel-derived water surfaces with a smoother reconstruction path before the next material or lighting pass.
