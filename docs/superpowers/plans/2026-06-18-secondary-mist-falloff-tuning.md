# Secondary Mist Falloff Tuning

## Goal

Tune the S69 radial falloff settings to reduce visible circular sprite edges while preserving the visual QA gate and render-cost range.

## Scope

- Keep the S69 concentric falloff geometry.
- Lower outer alpha to zero.
- Slightly reduce max mist radius.
- Raise inner emission enough to keep spray/foam readable.
- Preserve physical secondary counts and visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python tools\render_bridge_blender.py build\shots\s69_secondary_mist_falloff\converted\sequence.json build\s70_mist_falloff_tuned_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s70_secondary_mist_falloff_tuned --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s70.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S70 generated:

- `build/shots/s70_secondary_mist_falloff_tuned/shot.gif`
- `build/shots/s70_secondary_mist_falloff_tuned/review/contact_sheet.png`
- `build/shots/s70_secondary_mist_falloff_tuned/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s70.md`

The tuned falloff preserved QA and render cost. It improved the outer edge slightly, but a smoother material or texture falloff is the next higher-leverage visual step.

## Next

S71 should move from ring-only falloff to a material/texture-style radial falloff for smoother mist sprite edges.
