# S220 Water Overlay Highlight Acceptance

## Goal

Fold the S219 overlay-only glint/reflection controls into the accepted
`dam_break_water_mesh_smoothing` preset and verify that the accepted preset
reproduces the S219 visual gain.

## Scope

- Add S219 `water_surface_glint_pass` and `water_reflection_pass` overrides to
  `dam_break_water_mesh_smoothing`.
- Keep accepted water material, volume scattering, water surface detail, mesh
  smoothing, and `normal_rough` quality smoothing unchanged.
- Render the S214 mixed source window (`8..55`) through the accepted preset.
- Compare against S214 accepted and S219 probe renders.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s220_accepted_overlay_highlight\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s220_accepted_overlay_highlight\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s220_accepted_overlay_highlight\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s220_accepted_overlay_highlight\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\blender\frames --right build\shots\s220_accepted_overlay_highlight\blender\frames --left-label S214-accepted --right-label S220-accepted-overlay --summary-left build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --summary-right build\shots\s220_accepted_overlay_highlight\blender\bridge_summary.json --out-dir build\shots\s220_accepted_overlay_highlight\comparison_s214 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_overlay_highlight_acceptance_s220.md --title "S220 Accepted Overlay Highlight Promotion" --finding "S220 folds the S219 overlay-only glint/reflection controls into the accepted water mesh smoothing preset." --next "Keep S220 only if accepted-preset rendering preserves coverage and contrast while matching the S219 visual gain."
python tools\compare_cinematic_frames.py --left build\shots\s219_overlay_highlight_strong_probe\blender\frames --right build\shots\s220_accepted_overlay_highlight\blender\frames --left-label S219-strong-overlay --right-label S220-accepted-overlay --summary-left build\shots\s219_overlay_highlight_strong_probe\blender\bridge_summary.json --summary-right build\shots\s220_accepted_overlay_highlight\blender\bridge_summary.json --out-dir build\shots\s220_accepted_overlay_highlight\comparison_s219 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_overlay_highlight_s219_s220_parity.md --title "S219 vs S220 Overlay Highlight Parity" --finding "S220 accepted-preset render is compared against the S219 probe to verify the fold." --next "Treat S220 as accepted only if parity holds within render noise."
python tools\assemble_frames.py build\shots\s220_accepted_overlay_highlight\blender\frames build\shots\s220_accepted_overlay_highlight\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s220_accepted_overlay_highlight --out build\shots\s220_accepted_overlay_highlight\gallery --comparison-sheet build\shots\s220_accepted_overlay_highlight\comparison_s214\comparison_sheet.png --comparison-summary build\shots\s220_accepted_overlay_highlight\comparison_s214\comparison_summary.json --comparison-label "S214 Accepted vs S220 Accepted Overlay" --title "S220 Accepted Overlay Highlight" --keyframes 8 --report docs\reports\cinematic_water_overlay_highlight_acceptance_gallery_s220.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Accepted render: `build/shots/s220_accepted_overlay_highlight/blender`
- S214 comparison: `build/shots/s220_accepted_overlay_highlight/comparison_s214/comparison_sheet.png`
- S219 parity comparison: `build/shots/s220_accepted_overlay_highlight/comparison_s219/comparison_sheet.png`
- Gallery: `build/shots/s220_accepted_overlay_highlight/gallery/index.html`

S220 minus S214:

- Mean luminance: `0.43489312065972285`
- Minimum contrast: `0.0`
- Mean bright ratio: `5.425347222222257e-07`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

S220 minus S219:

- Mean luminance: `-4.340277769188106e-06`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Accept S220. The S219 overlay-only controls are now part of
`dam_break_water_mesh_smoothing`.

## Next

Start the next visual pass from S220. Secondary particle readability is the
nearest useful target: improve spray/foam/bubble read without increasing direct
particle clutter.
