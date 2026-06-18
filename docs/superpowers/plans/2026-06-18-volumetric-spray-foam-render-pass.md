# Volumetric Spray/Foam Render Pass

## Goal

Make physically seeded spray and foam read more like mist and foam instead of isolated hard spheres.

## Scope

- Add a preset-driven `secondary_soft_pass` renderer option.
- Keep particle/cache/physics data unchanged.
- Add a larger, translucent soft halo pass for spray and foam channels in the Blender driver.
- Record the active soft-pass settings in `bridge_summary.json` and shot reports.
- Preserve S65 visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s65_visual_qa_metrics\converted\sequence.json build\s66_soft_pass_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s66_volumetric_spray_foam --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s66.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S66 generated:

- `build/shots/s66_volumetric_spray_foam/shot.gif`
- `build/shots/s66_volumetric_spray_foam/review/contact_sheet.png`
- `build/shots/s66_volumetric_spray_foam/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s66.md`

The soft pass makes spray/foam clusters larger and more diffuse while keeping camera and visual QA gates green.

## Next

S67 should reduce the render cost of the soft pass. The visual direction is useful, but the current implementation adds many extra mesh spheres and makes Blender rendering much slower.
