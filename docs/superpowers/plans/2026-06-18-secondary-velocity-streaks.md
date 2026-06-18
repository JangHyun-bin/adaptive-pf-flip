# Secondary Velocity Streaks

## Goal

Render secondary spray and foam with velocity-aligned streak geometry so contact particles read as moving spray instead of only circular sprites.

## Scope

- Add `secondary_streak_pass` preset controls for spray and foam.
- Read secondary particle `vx/vy/vz` columns from converted frame CSV files.
- Build one camera-plane-projected quad per eligible spray/foam particle.
- Scale streak length from particle speed while capping maximum length.
- Preserve the existing secondary particle and mist billboard passes.
- Record streak settings in Blender bridge summaries and cinematic reports.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s71_secondary_mist_texture_falloff\converted\sequence.json build\s72_velocity_streak_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s72_secondary_velocity_streaks --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s72.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S72 generated:

- `build/shots/s72_secondary_velocity_streaks/shot.gif`
- `build/shots/s72_secondary_velocity_streaks/review/contact_sheet.png`
- `build/shots/s72_secondary_velocity_streaks/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s72.md`

The velocity streak pass is implemented and recorded in render summaries. Visual QA passed, and the contact-sheet review shows visible thin streaks in later impact frames.

## Next

S73 should tune streak length, width, alpha, and emission against the S72 sheet so motion streaks are clearer without creating noisy white scratch artifacts.
