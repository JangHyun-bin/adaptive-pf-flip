# S227 Accepted Motion Window Review

## Goal

Validate the accepted S223/S224 cinematic preset over a longer 32-frame motion window before adding another visual tuning pass.

## Scope

- Use the S205 annotated converted sequence.
- Render source indices `8..55` as `32` review frames.
- Compare the accepted preset against a S220-style baseline with S223 secondary soft/streak overrides removed.
- Keep the S225 public tunnel running; do not publish a new tunnel by default.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s227_accepted_motion_window\dry --frames 32 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s227_accepted_motion_window\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s227_accepted_motion_window\mixed_gate --min-stable-ratio 0.85
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s227_accepted_motion_window\blender --frames 32 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 1200
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s227_accepted_motion_window\s220_baseline --frames 32 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config build\shots\s224_wide_accepted_review\s220_baseline_config.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 1200
python tools\compare_cinematic_frames.py --left build\shots\s227_accepted_motion_window\s220_baseline\frames --right build\shots\s227_accepted_motion_window\blender\frames --left-label S220-motion-baseline --right-label S227-accepted-motion --summary-left build\shots\s227_accepted_motion_window\s220_baseline\bridge_summary.json --summary-right build\shots\s227_accepted_motion_window\blender\bridge_summary.json --out-dir build\shots\s227_accepted_motion_window\comparison_s220 --frames 32 --thumb-width 260 --report docs\reports\cinematic_accepted_motion_window_s227.md
python tools\build_bridge_cinematic_gallery.py build\shots\s227_accepted_motion_window --out build\shots\s227_accepted_motion_window\gallery --comparison-sheet build\shots\s227_accepted_motion_window\comparison_s220\comparison_sheet.png --comparison-summary build\shots\s227_accepted_motion_window\comparison_s220\comparison_summary.json --comparison-label "S220 Motion Baseline vs S227 Accepted" --title "S227 Accepted Motion Window Review" --keyframes 10 --report docs\reports\cinematic_accepted_motion_window_gallery_s227.md
```

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match the S220-motion baseline on all `32` frames.
- Mean luminance delta versus S220-motion baseline: `+0.20133558485242986`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.

## Decision

Keep the accepted S223/S224 preset. The longer motion window preserves the bounded metrics and direct secondary thinning while retaining the readability gain.

## Next

Use S227 as the baseline proof for the next actual visual improvement pass.
