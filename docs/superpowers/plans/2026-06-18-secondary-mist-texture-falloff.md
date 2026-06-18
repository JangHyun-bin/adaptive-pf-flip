# Secondary Mist Texture Falloff

## Goal

Move beyond ring-only mist falloff by using UV-driven radial shader alpha for billboard disks.

## Scope

- Add repeated per-disk UVs to billboard mist meshes.
- Add `material_falloff=radial_shader` preset support.
- Build a radial shader material from UV distance to disk center.
- Preserve the existing ring-material fallback.
- Preserve camera stability, visual QA, and render-cost gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s70_secondary_mist_falloff_tuned\converted\sequence.json build\s71_mist_texture_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s71_secondary_mist_texture_falloff --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s71.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S71 generated:

- `build/shots/s71_secondary_mist_texture_falloff/shot.gif`
- `build/shots/s71_secondary_mist_texture_falloff/review/contact_sheet.png`
- `build/shots/s71_secondary_mist_texture_falloff/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s71.md`

The radial shader path is now implemented and validated. The visual change is subtle, so the next larger visual improvement should use motion-aware streak geometry.

## Next

S72 should use velocity-aligned or camera-facing streak geometry for spray/foam secondaries so they read as moving spray rather than stationary circular sprites.
