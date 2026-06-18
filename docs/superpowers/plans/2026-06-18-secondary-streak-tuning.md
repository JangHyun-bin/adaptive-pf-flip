# Secondary Streak Tuning

## Goal

Tune the S72 velocity streak pass for clearer spray motion while recording actual rendered streak counts.

## Scope

- Increase spray streak length, width, alpha, and emission conservatively.
- Preserve the existing mist billboard and radial shader soft pass.
- Add bridge/report metrics for actual per-frame streak counts.
- Keep foam in the soft-pass path when foam velocities are below the streak speed gate.
- Preserve camera stability and visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s72_secondary_velocity_streaks\converted\sequence.json build\s73_streak_tuning_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s73_secondary_streak_tuning --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s73.md --compare-review-manifest build\shots\s72_secondary_velocity_streaks\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S73 generated:

- `build/shots/s73_secondary_streak_tuning/shot.gif`
- `build/shots/s73_secondary_streak_tuning/review/contact_sheet.png`
- `build/shots/s73_secondary_streak_tuning/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s73.md`

The tuned pass renders `115-119` spray streaks per frame and preserves QA. Foam is still represented by the soft mist pass because its current velocity stays below the streak speed gate.

## Next

S74 should focus on impact framing and timing so the active collision/spray region stays in frame for more of the shot before further particle-only tuning.
