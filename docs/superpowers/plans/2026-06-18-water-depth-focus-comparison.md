# Water Depth Focus Comparison

## Goal

Add a water-depth-focused review crop so S99 water-body depth cues can be compared without relying only on full-frame contact sheets.

## Scope

- Add `dam_break_water_depth_focus_comparison` as an inherited S99 preset.
- Keep simulation, cache schema, material settings, camera settings, and renderer logic unchanged.
- Move the focus review crop to the lower water-body region: `[0.02, 0.42, 0.98, 0.95]`.
- Gate the water-depth crop on frame count, nonblank ratio, contrast, and bounded mean luminance.
- Override the inherited bright-speckle threshold to `0.0`; this diagnostic is about water-body depth separation, not highlight density.
- Compare the S100 focus sheet against the S99 review manifest.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_water_depth_focus_comparison --out build\shots\s100_water_depth_focus_comparison --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s100.md --compare-review-manifest build\shots\s99_water_volume_depth_cue_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S100 generated:

- `build/shots/s100_water_depth_focus_comparison/shot.gif`
- `build/shots/s100_water_depth_focus_comparison/review/contact_sheet.png`
- `build/shots/s100_water_depth_focus_comparison/review/focus_sheet.png`
- `build/shots/s100_water_depth_focus_comparison/review/focus_comparison_sheet.png`
- `build/shots/s100_water_depth_focus_comparison/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s100.md`

The full gate passed. The water-depth focus crop produced:

- frame count: `8`
- nonblank ratio min/mean/max: `1.0 / 1.0 / 1.0`
- contrast min/mean/max: `75.0 / 149.125 / 196.0`
- mean luminance min/mean/max: `74.5558 / 92.4267 / 116.9138`
- bright ratio mean: `0.0001196`

The focus comparison sheet now contrasts the S99 contact-region crop with the S100 lower water-body crop, making the water depth and rim cues easier to inspect directly.

## Next

S101 should tune the water-depth comparison crop or lighting only if the S100 focus comparison shows weak water-body separation. Otherwise, keep the S100 crop as the water-depth diagnostic and move on to the next cinematic/rendering gap.
