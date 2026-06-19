# S224 Wide Accepted Preset Review

## Goal

Validate the accepted `dam_break_water_mesh_smoothing` preset over a wider render window after the S223 secondary readability promotion.

## Scope

- Use the S205 annotated converted sequence.
- Render source indices `8..55` as `16` review frames.
- Keep the current accepted S223 preset unchanged.
- Compare against a build-local S220-style baseline with only the S223 secondary soft/streak overrides removed.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s224_wide_accepted_review\dry --frames 16 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s224_wide_accepted_review\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s224_wide_accepted_review\mixed_gate --min-stable-ratio 0.85
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s224_wide_accepted_review\blender --frames 16 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 900
python tools\compare_cinematic_frames.py --left build\shots\s224_wide_accepted_review\s220_baseline\frames --right build\shots\s224_wide_accepted_review\blender\frames --left-label S220-wide-baseline --right-label S224-accepted-wide --summary-left build\shots\s224_wide_accepted_review\s220_baseline\bridge_summary.json --summary-right build\shots\s224_wide_accepted_review\blender\bridge_summary.json --out-dir build\shots\s224_wide_accepted_review\comparison_s220 --frames 16 --thumb-width 320 --report docs\reports\cinematic_wide_accepted_review_s224.md
python tools\build_bridge_cinematic_gallery.py build\shots\s224_wide_accepted_review --out build\shots\s224_wide_accepted_review\gallery --comparison-sheet build\shots\s224_wide_accepted_review\comparison_s220\comparison_sheet.png --comparison-summary build\shots\s224_wide_accepted_review\comparison_s220\comparison_summary.json --comparison-label "S220 Wide Baseline vs S224 Accepted" --title "S224 Wide Accepted Preset Review" --keyframes 8 --report docs\reports\cinematic_wide_accepted_review_gallery_s224.md
```

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match the S220-wide baseline on all `16` frames.
- Mean luminance delta versus S220-wide baseline: `+0.19168701171875568`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.

## Decision

Keep S223 as the accepted cinematic baseline. The wider review window preserves the bounded metrics and direct secondary thinning while retaining the readability gain.

## Next

Use S224 as the accepted wide-window proof before publishing a gallery or starting the next visual tuning pass.
