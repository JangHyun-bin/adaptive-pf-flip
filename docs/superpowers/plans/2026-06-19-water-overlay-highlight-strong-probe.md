# S219 Strong Water Overlay Highlight Probe

## Goal

Compare one stronger overlay-only highlight candidate against S218 before
folding anything into the accepted preset.

## Scope

- Add `dam_break_water_mesh_overlay_highlight_strong_probe`.
- Leave accepted water material, volume scattering, water surface detail, mesh
  smoothing, and `normal_rough` quality smoothing unchanged.
- Tune only `water_surface_glint_pass` and `water_reflection_pass`.
- Render the same mixed window (`8..55`) and compare against S214 and S218.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s219_overlay_highlight_strong_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_overlay_highlight_strong_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s219_overlay_highlight_strong_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s219_overlay_highlight_strong_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s219_overlay_highlight_strong_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_overlay_highlight_strong_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\blender\frames --right build\shots\s219_overlay_highlight_strong_probe\blender\frames --left-label S214-accepted --right-label S219-strong-overlay --summary-left build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --summary-right build\shots\s219_overlay_highlight_strong_probe\blender\bridge_summary.json --out-dir build\shots\s219_overlay_highlight_strong_probe\comparison_s214 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_overlay_highlight_strong_probe_s219.md --title "S219 Strong Water Overlay Highlight Probe" --finding "S219 compares a stronger overlay-only glint/reflection tune against the accepted S214 mixed-window preset." --next "Prefer S219 only if it gives a visible highlight/readability gain without reducing S214 coverage or contrast."
python tools\compare_cinematic_frames.py --left build\shots\s218_overlay_highlight_probe\blender\frames --right build\shots\s219_overlay_highlight_strong_probe\blender\frames --left-label S218-overlay --right-label S219-strong-overlay --summary-left build\shots\s218_overlay_highlight_probe\blender\bridge_summary.json --summary-right build\shots\s219_overlay_highlight_strong_probe\blender\bridge_summary.json --out-dir build\shots\s219_overlay_highlight_strong_probe\comparison_s218 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_overlay_highlight_s218_s219_comparison.md --title "S218 vs S219 Overlay Highlight A/B" --finding "S219 is compared against S218 to decide which overlay-only candidate should feed the accepted preset." --next "Promote the stronger candidate only if the visual gain over S218 is clear and metrics stay bounded."
python tools\assemble_frames.py build\shots\s219_overlay_highlight_strong_probe\blender\frames build\shots\s219_overlay_highlight_strong_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s219_overlay_highlight_strong_probe --out build\shots\s219_overlay_highlight_strong_probe\gallery --comparison-sheet build\shots\s219_overlay_highlight_strong_probe\comparison_s214\comparison_sheet.png --comparison-summary build\shots\s219_overlay_highlight_strong_probe\comparison_s214\comparison_summary.json --comparison-label "S214 Accepted vs S219 Strong Overlay" --title "S219 Strong Water Overlay Highlight Probe" --keyframes 8 --report docs\reports\cinematic_water_overlay_highlight_strong_gallery_s219.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Render: `build/shots/s219_overlay_highlight_strong_probe/blender`
- S214 comparison: `build/shots/s219_overlay_highlight_strong_probe/comparison_s214/comparison_sheet.png`
- S218 comparison: `build/shots/s219_overlay_highlight_strong_probe/comparison_s218/comparison_sheet.png`
- Gallery: `build/shots/s219_overlay_highlight_strong_probe/gallery/index.html`

S219 minus S214:

- Mean luminance: `0.43489746093749204`
- Minimum contrast: `0.0`
- Mean bright ratio: `5.425347222222257e-07`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

S219 minus S218:

- Mean luminance: `0.32243109809027715`
- Minimum contrast: `0.0`
- Mean bright ratio: `5.425347222222257e-07`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Prefer S219 over S218 as the overlay-only promotion candidate. It gives a clearer
surface streak/readability gain while preserving the S214 contrast and coverage
metrics.

## Next

S220 should fold S219 into `dam_break_water_mesh_smoothing` and rerun the mixed
accepted-preset validation.
