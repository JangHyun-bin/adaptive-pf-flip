# Secondary Soft-pass Performance

## Goal

Keep the S66 spray/foam soft-pass look while reducing Blender render cost.

## Scope

- Keep core secondary particle rendering unchanged.
- Replace per-particle soft halo `bpy.ops` sphere creation with batched channel meshes.
- Preserve the same `secondary_soft_pass` preset controls.
- Record `geometry=batched_spheres` in the soft-pass summary.
- Preserve camera stability and visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s66_volumetric_spray_foam\converted\sequence.json build\s67_soft_pass_perf_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s67_secondary_soft_perf --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s67.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S67 generated:

- `build/shots/s67_secondary_soft_perf/shot.gif`
- `build/shots/s67_secondary_soft_perf/review/contact_sheet.png`
- `build/shots/s67_secondary_soft_perf/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s67.md`

The S67 Blender render stage took `105.16s`, down from S66's `236.36s`, while visual QA remained green.

## Next

S68 should improve the visual character of spray and foam beyond soft spheres. The likely next path is camera-facing billboard or flattened mist geometry with the same metrics and comparison gate.
