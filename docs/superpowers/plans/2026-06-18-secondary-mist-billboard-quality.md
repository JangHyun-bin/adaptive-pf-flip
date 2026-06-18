# Secondary Mist Billboard Quality

## Goal

Improve spray/foam naturalness beyond soft spheres without reintroducing the S66 render cost.

## Scope

- Keep the S67 batched mesh strategy.
- Add a `billboard_disks` soft-pass geometry mode.
- Orient mist disks toward the active camera per frame.
- Preserve physical secondary counts, camera stability gates, and visual QA gates.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\render_bridge_blender.py build\shots\s67_secondary_soft_perf\converted\sequence.json build\s68_mist_billboard_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s68_secondary_mist_quality --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s68.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S68 generated:

- `build/shots/s68_secondary_mist_quality/shot.gif`
- `build/shots/s68_secondary_mist_quality/review/contact_sheet.png`
- `build/shots/s68_secondary_mist_quality/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s68.md`

The billboard disk mode kept render cost near S67 and increased the bright-pixel visual QA proxy, but the disk edges are still visible.

## Next

S69 should add radial alpha/falloff or texture-driven sprite shading so spray and foam read less like circular overlays.
