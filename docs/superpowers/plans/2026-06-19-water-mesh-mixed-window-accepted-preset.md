# S214 Water Mesh Mixed-Window Accepted Preset

## Goal

Validate the S213 `normal_rough` smoothing fold inside the main accepted
`dam_break_water_mesh_smoothing` preset on a mixed source window that contains
both `normal_rough` and `stable` mesh-quality labels.

## Scope

- Use source indices `8..55` from the S205 annotated sequence.
- Dry-run the accepted preset and validate label routing.
- Render the accepted mixed window at 8 frames, 640x360, 16 samples.
- Render the same mixed window with only `water_mesh_quality_smoothing_pass`
  disabled through a temporary build-local preset config.
- Compare the two rendered frame sets.
- Package the accepted render into a gallery with the comparison sheet.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s214_mixed_window_accepted_preset\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s214_mixed_window_accepted_preset\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s214_mixed_window_accepted_preset\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s214_mixed_window_accepted_preset\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s214_mixed_window_accepted_preset\no_quality_smoothing --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config build\shots\s214_mixed_window_accepted_preset\no_quality_smoothing_config.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\no_quality_smoothing\frames --right build\shots\s214_mixed_window_accepted_preset\blender\frames --left-label S214-no-quality-smoothing --right-label S214-accepted --summary-left build\shots\s214_mixed_window_accepted_preset\no_quality_smoothing\bridge_summary.json --summary-right build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --out-dir build\shots\s214_mixed_window_accepted_preset\comparison --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_mesh_mixed_window_accepted_preset_s214.md --title "S214 Mixed-Window Accepted Preset Review" --finding "S214 compares the accepted water mesh smoothing preset against the same preset with the normal_rough quality smoothing pass disabled." --next "Keep the S213 preset fold only if the mixed sequence preserves coverage and does not visibly regress stable frames."
python tools\assemble_frames.py build\shots\s214_mixed_window_accepted_preset\blender\frames build\shots\s214_mixed_window_accepted_preset\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s214_mixed_window_accepted_preset --out build\shots\s214_mixed_window_accepted_preset\gallery --comparison-sheet build\shots\s214_mixed_window_accepted_preset\comparison\comparison_sheet.png --comparison-summary build\shots\s214_mixed_window_accepted_preset\comparison\comparison_summary.json --comparison-label "No Quality Smoothing vs Accepted" --title "S214 Mixed-Window Accepted Preset" --keyframes 8 --report docs\reports\cinematic_water_mesh_mixed_window_gallery_s214.md
```

## Results

- Mixed dry-run labels: `normal_rough: 1`, `stable: 7`
- Mixed gate: `passed`
- Accepted render: `build/shots/s214_mixed_window_accepted_preset/blender`
- No-quality-smoothing baseline render:
  `build/shots/s214_mixed_window_accepted_preset/no_quality_smoothing`
- Comparison:
  `build/shots/s214_mixed_window_accepted_preset/comparison/comparison_sheet.png`
- Gallery:
  `build/shots/s214_mixed_window_accepted_preset/gallery/index.html`

Metric deltas accepted minus no-quality-smoothing:

- Mean luminance: `0.00014919704861426908`
- Minimum contrast: `0.0`
- Mean bright ratio: `5.425347222222257e-07`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Keep the S213 accepted-preset fold. The mixed review proves the label-gated
`normal_rough` smoothing remains bounded when stable frames share the sequence.

## Next

Move back to broader cinematic quality work on top of the accepted mixed-window
preset: either publish the S214 gallery externally or start the next water
depth/reflection treatment.
