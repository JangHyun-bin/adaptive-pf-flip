# S218 Water Overlay Highlight Probe

## Goal

Recover the useful highlight/readability direction from S216/S217 without their
water-material darkening and contrast loss.

## Scope

- Add `dam_break_water_mesh_overlay_highlight_probe`.
- Leave accepted water material, volume scattering, water surface detail, mesh
  smoothing, and label-gated `normal_rough` smoothing unchanged.
- Tune only `water_surface_glint_pass` and `water_reflection_pass`.
- Render the same S214 mixed window (`8..55`) and compare against S214 accepted.
- Package a gallery for review.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s218_overlay_highlight_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_overlay_highlight_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s218_overlay_highlight_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s218_overlay_highlight_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s218_overlay_highlight_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_overlay_highlight_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\blender\frames --right build\shots\s218_overlay_highlight_probe\blender\frames --left-label S214-accepted --right-label S218-overlay-highlight --summary-left build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --summary-right build\shots\s218_overlay_highlight_probe\blender\bridge_summary.json --out-dir build\shots\s218_overlay_highlight_probe\comparison_s214 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_overlay_highlight_probe_s218.md --title "S218 Water Overlay Highlight Probe" --finding "S218 isolates reflection and glint overlay tuning while leaving the accepted water material and scatter unchanged." --next "Promote S218 only if it increases useful highlight readability without reducing S214 coverage or contrast."
python tools\assemble_frames.py build\shots\s218_overlay_highlight_probe\blender\frames build\shots\s218_overlay_highlight_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s218_overlay_highlight_probe --out build\shots\s218_overlay_highlight_probe\gallery --comparison-sheet build\shots\s218_overlay_highlight_probe\comparison_s214\comparison_sheet.png --comparison-summary build\shots\s218_overlay_highlight_probe\comparison_s214\comparison_summary.json --comparison-label "S214 Accepted vs S218 Overlay Highlight" --title "S218 Water Overlay Highlight Probe" --keyframes 8 --report docs\reports\cinematic_water_overlay_highlight_gallery_s218.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Render: `build/shots/s218_overlay_highlight_probe/blender`
- Comparison: `build/shots/s218_overlay_highlight_probe/comparison_s214/comparison_sheet.png`
- Gallery: `build/shots/s218_overlay_highlight_probe/gallery/index.html`

S218 minus S214:

- Mean luminance: `0.1124663628472149`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Keep S218 as the current safe overlay-highlight candidate. It is subtle, but it
adds surface streak readability without the darkening or contrast loss that
blocked S216/S217.

## Next

S219 should decide whether to fold S218 into the accepted preset or test one
slightly stronger overlay-only candidate before promotion.
